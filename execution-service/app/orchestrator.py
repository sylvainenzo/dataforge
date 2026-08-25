"""Sandbox orchestrator interface (Phase 1 §7) and the one implementation
this environment can actually run.

============================================================================
SECURITY WARNING — READ BEFORE DEPLOYING ANYTHING BUILT ON THIS FILE
============================================================================
LocalSubprocessOrchestrator is NOT the production sandbox described in the
Phase 1 architecture. It runs submitted code as a plain OS subprocess on
the SAME host, filesystem, and network namespace as this service. There is
no gVisor container, no filesystem isolation, no network isolation, and no
strong memory isolation (macOS does not reliably enforce RLIMIT_AS the way
Linux does). A determined user could read files this process can read,
reach the network, or otherwise escape the limited protections applied
here.

This class exists only so the execution-service's API contract, WebSocket
streaming protocol, timeout handling, and quota logic can be built and
exercised end-to-end in an environment with no Docker/gVisor available
(verified: `docker` is not installed on this machine). It must never be
used to run code from users you do not already fully trust.

GVisorOrchestrator below is the required production implementation per
Phase 1 §7 — it is a stub that raises NotImplementedError, documenting the
interface a real implementation must satisfy (spin up a `runsc`-runtime
container per run, apply the same resource limits, stream output back, and
tear the container down unconditionally). Swapping it in is the only
change needed elsewhere in this service — orchestrator selection is a
single line in main.py.
============================================================================
"""

import asyncio
import base64
import functools
import os
import resource
import subprocess
import tempfile
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.config import settings


@dataclass
class ExecutionChunk:
    stream: str  # "stdout" | "stderr" | "exit" | "image" (data is base64-encoded PNG bytes)
    data: str


class Orchestrator(Protocol):
    async def run(self, *, code: str, language: str) -> AsyncIterator[ExecutionChunk]: ...


def _current_process_count() -> int:
    """Number of processes the current UID already owns, via `ps` (portable
    across Linux and macOS, unlike /proc). Called in the parent, before
    forking — never inside preexec_fn, where spawning another process would
    be unsafe (fork() only carries over the calling thread)."""

    try:
        result = subprocess.run(
            ["ps", "-U", str(os.getuid())], capture_output=True, text=True, timeout=2
        )
        return max(0, len(result.stdout.splitlines()) - 1)  # minus the header row
    except (OSError, subprocess.SubprocessError):
        return 200  # unknown — assume a busy machine rather than a quiet one


def _limit_resources(nproc_limit: int) -> None:
    """Runs inside the child process via subprocess's preexec_fn, right
    after fork() and before exec(). Best-effort only — see the module
    docstring for what this does and does not actually guarantee."""

    cpu_seconds = settings.execution_timeout_seconds + 2  # small grace margin over the wall-clock timeout below
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
    try:
        mem_bytes = settings.execution_memory_limit_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    except (ValueError, OSError):
        # RLIMIT_AS is not reliably enforced on macOS/Darwin — this is a
        # known platform gap, not a bug here. Documented, not hidden.
        pass

    # RLIMIT_NPROC caps the *total* process count for this UID system-wide,
    # not just this subprocess's own descendants — a hardcoded low absolute
    # value (e.g. 16) breaks on any real dev machine that already runs more
    # than that for the user, which is every machine, always. It surfaced
    # here because Rscript forks an internal R process on startup and
    # Python's single-process script execution happens not to; the limit
    # was silently too tight for both languages the whole time. Fixed by
    # budgeting headroom (computed by the caller, in the parent process)
    # above whatever the UID was already using right before this run
    # started, so a fork-bomb inside the sandboxed script is still capped,
    # without breaking on a machine that's simply busy.
    resource.setrlimit(resource.RLIMIT_NPROC, (nproc_limit, nproc_limit))


_LANGUAGE_COMMANDS: dict[str, tuple[str, str]] = {
    # language -> (interpreter setting name, script filename)
    "python": ("sandbox_python_path", "submission.py"),
    "r": ("sandbox_r_path", "submission.R"),
}

_MAX_IMAGES_PER_RUN = 5
_MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB — a normal matplotlib PNG is a few hundred KB


def _collect_image_chunks(tmpdir: str) -> Iterator[ExecutionChunk]:
    """Picks up any PNGs the script saved to its own tmpdir (e.g. via
    `plt.savefig(...)`) and yields each as a base64-encoded chunk, in
    filename order (fig1.png before fig2.png) so multi-chart exercises
    render in the order the student created them."""

    png_paths = sorted(Path(tmpdir).glob("*.png"))
    for path in png_paths[:_MAX_IMAGES_PER_RUN]:
        data = path.read_bytes()
        if len(data) > _MAX_IMAGE_BYTES:
            yield ExecutionChunk("stderr", f"\n[{path.name} skipped — exceeds {_MAX_IMAGE_BYTES // 1024 // 1024}MB output limit]\n")
            continue
        yield ExecutionChunk("image", base64.b64encode(data).decode("ascii"))
    if len(png_paths) > _MAX_IMAGES_PER_RUN:
        yield ExecutionChunk("stderr", f"\n[only the first {_MAX_IMAGES_PER_RUN} images are shown]\n")


class LocalSubprocessOrchestrator:
    """Dev/demo-only — see module docstring."""

    async def run(self, *, code: str, language: str) -> AsyncIterator[ExecutionChunk]:
        if language not in _LANGUAGE_COMMANDS:
            yield ExecutionChunk("stderr", f"Language '{language}' is not supported by the local dev executor.")
            yield ExecutionChunk("exit", "1")
            return

        setting_name, script_name = _LANGUAGE_COMMANDS[language]
        interpreter_path = getattr(settings, setting_name)
        nproc_limit = await asyncio.to_thread(_current_process_count) + 32

        with tempfile.TemporaryDirectory(prefix="dataforge-exec-") as tmpdir:
            script_path = Path(tmpdir) / script_name
            script_path.write_text(code)

            interpreter_args = [interpreter_path]
            if language == "python":
                interpreter_args.append("-I")  # isolated mode: ignores PYTHONPATH/user site-packages
            interpreter_args.append(str(script_path))

            process = await asyncio.create_subprocess_exec(
                *interpreter_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=tmpdir,
                # Strips everything this process itself could pass on — no
                # secrets, no app config — for both languages (verified
                # Rscript runs cleanly under this same stripped PATH, same
                # as the Python sandbox). Verified independently that
                # macOS's own /usr/bin/python3 shim still injects a handful
                # of harmless build-toolchain paths (SDKROOT, CPATH, etc.)
                # no matter what env is passed; that's an OS-level launcher
                # behavior this process cannot suppress, not a leak from
                # this service, and it exposes no credentials.
                env={"PATH": "/usr/bin:/bin:/usr/local/bin", "MPLBACKEND": "Agg"},
                preexec_fn=functools.partial(_limit_resources, nproc_limit),
            )

            output_bytes = 0
            truncated = False

            async def _drain(stream: asyncio.StreamReader, label: str) -> AsyncIterator[ExecutionChunk]:
                nonlocal output_bytes, truncated
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    output_bytes += len(line)
                    if output_bytes > settings.execution_max_output_bytes:
                        if not truncated:
                            truncated = True
                            yield ExecutionChunk(label, "\n[output truncated — exceeded limit]\n")
                        continue
                    yield ExecutionChunk(label, line.decode(errors="replace"))

            try:
                async with asyncio.timeout(settings.execution_timeout_seconds):
                    stdout_task = _drain(process.stdout, "stdout")
                    stderr_task = _drain(process.stderr, "stderr")
                    async for chunk in _merge(stdout_task, stderr_task):
                        yield chunk
                    exit_code = await process.wait()

                    # Data viz exercises (matplotlib/seaborn) save a real
                    # PNG to the sandboxed tmpdir rather than trying to open
                    # a display (there isn't one — MPLBACKEND=Agg above).
                    # Picking those files up and streaming them back is what
                    # makes "run a chart" a real feature instead of text-only
                    # output pretending charts work.
                    for chunk in _collect_image_chunks(tmpdir):
                        yield chunk

                    yield ExecutionChunk("exit", str(exit_code))
            except TimeoutError:
                process.kill()
                await process.wait()
                yield ExecutionChunk("stderr", f"\n[killed — exceeded {settings.execution_timeout_seconds}s timeout]\n")
                yield ExecutionChunk("exit", "124")


async def _merge(*iterators: AsyncIterator[ExecutionChunk]) -> AsyncIterator[ExecutionChunk]:
    """Interleaves stdout/stderr as they arrive rather than waiting for
    stdout to fully drain before starting stderr."""

    queue: asyncio.Queue[ExecutionChunk | None] = asyncio.Queue()

    async def _pump(it: AsyncIterator[ExecutionChunk]) -> None:
        async for item in it:
            await queue.put(item)
        await queue.put(None)

    pumps = [asyncio.create_task(_pump(it)) for it in iterators]
    finished = 0
    while finished < len(pumps):
        item = await queue.get()
        if item is None:
            finished += 1
            continue
        yield item


class GVisorOrchestrator:
    """Required production implementation per Phase 1 §7 — not implemented
    in this environment (no Docker/gVisor available to build and test
    against). A real implementation spins up a fresh, network-default-deny,
    resource-quota'd container per run using the `runsc` runtime, streams
    its stdout/stderr back exactly like LocalSubprocessOrchestrator does,
    and unconditionally destroys the container afterward — no reuse across
    runs, ever."""

    async def run(self, *, code: str, language: str) -> AsyncIterator[ExecutionChunk]:
        raise NotImplementedError(
            "GVisorOrchestrator requires a gVisor-capable container host. "
            "Use LocalSubprocessOrchestrator for local development only."
        )
        yield  # pragma: no cover — makes this an async generator for Protocol compliance

# DataForge Execution Gateway — Phase 7

A separate deployable from the Core API (`../backend`), by design — this is
the one component that runs untrusted user code, isolated as its own
security boundary per Phase 1 §3/§7.

## Read this first

`app/orchestrator.py`'s module docstring explains exactly what
`LocalSubprocessOrchestrator` does and does not protect against. Short
version: **it is a dev/demo-only executor**, not the gVisor-isolated
production sandbox the architecture requires. It runs code as a plain OS
subprocess with CPU/memory/process-count limits and a stripped environment
— no container, no filesystem isolation, no network isolation. Do not point
this at real untrusted users.

## Setup

```bash
cd execution-service
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env   # JWT_SECRET must match ../backend/.env exactly

# The interpreter submitted code actually runs under — deliberately separate
# from this service's own venv so submissions can't reach FastAPI/SQLAlchemy/
# secrets even in principle:
python3 -m venv sandbox-env
sandbox-env/bin/pip install pandas numpy
```

## Run

```bash
uvicorn app.main:app --reload --port 8100
```

Requires the Core API (for login/cookies) and Redis (rate limiting) running.

## What's real

WebSocket streaming (`/ws/execution`), 10s timeout with hard process kill,
CPU/process-count limits enforced via `resource.setrlimit` (memory limiting
is best-effort — macOS does not reliably enforce `RLIMIT_AS`), output
truncation at 64KB, per-user rate limiting via Redis, and every run logged
to the shared `audit_logs` table.

## Verified, not just written

Ran a real script against a real running instance covering: normal stdout,
stderr + an uncaught exception's traceback, an infinite loop actually
getting killed at the 10s mark (confirmed via wall-clock timing in the
test output), and confirmed the environment strip works except for a
handful of harmless macOS-injected toolchain paths that the OS's own
Python launcher adds regardless of what environment is passed (documented
in the code, not hidden). Then verified from the actual browser UI
(`/labs/python`) that a pandas DataFrame filter runs correctly end-to-end,
and that all of the above appears in `audit_logs`.

## Known gaps

- `GVisorOrchestrator` in `orchestrator.py` is a documented stub, not an
  implementation — this machine has no Docker/gVisor to build against.
- SQL and R languages are not implemented here — SQL needs a different
  execution path entirely (per-session isolated Postgres schema, not a
  subprocess), planned for Phase 8.

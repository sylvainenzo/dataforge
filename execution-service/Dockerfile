# Written for Phase 15 but NOT built or run — no Docker in this environment.
#
# SECURITY: packaging this service into a container is necessary but NOT
# sufficient for the production sandbox Phase 1 §7 requires. This Dockerfile
# alone gives you the default `runc` container runtime, which is not a
# strong enough boundary for untrusted code. In production this container
# MUST be run with the gVisor runtime (`docker run --runtime=runsc ...`, or
# a Kubernetes RuntimeClass set to gvisor) — see app/orchestrator.py's
# module docstring for the full explanation of what LocalSubprocessOrchestrator
# does and does not protect against.

FROM python:3.12-slim AS builder

WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip

COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir --prefix=/install .

# The interpreter submitted code actually runs under — deliberately
# separate from the service's own dependencies (see orchestrator.py).
RUN python -m venv /sandbox-env \
    && /sandbox-env/bin/pip install --no-cache-dir pandas numpy

FROM python:3.12-slim

RUN groupadd --system app && useradd --system --gid app --home /app app
WORKDIR /app

COPY --from=builder /install /usr/local
COPY --from=builder /sandbox-env /app/sandbox-env
COPY app ./app

RUN chown -R app:app /app
USER app

EXPOSE 8100
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]

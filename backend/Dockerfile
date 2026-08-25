# Written for Phase 15 but NOT built or run — this machine has no Docker
# (confirmed absent in Phase 1/7 investigation). Follows standard, current
# best practice (multi-stage, non-root, slim base) but verify a real build
# before relying on it: `docker build -t dataforge-backend .`

FROM python:3.12-slim AS builder

WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip

COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.12-slim

RUN groupadd --system app && useradd --system --gid app --home /app app
WORKDIR /app

COPY --from=builder /install /usr/local
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY scripts ./scripts

RUN chown -R app:app /app
USER app

EXPOSE 8000
# Shell form (not exec-form CMD ["..."]) so $PORT actually expands — most
# PaaS hosts (Railway, Render, etc.) assign a dynamic port at runtime and
# expect the container to bind to it; ${PORT:-8000} falls back to 8000 for
# `docker run` / docker-compose where nothing sets it. Runs migrations on
# every boot — fine for a single-instance deploy, but if this ever scales
# to multiple replicas, move `alembic upgrade head` to a separate release
# step so concurrent boots can't race on the same migration.
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

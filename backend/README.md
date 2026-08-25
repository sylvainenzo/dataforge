# DataForge Backend — Phases 2-13

Database layer, auth, curriculum, Mac Setup Wizard, AI Tutor, datasets,
projects, progress/gamification, admin, and a real test suite. See
`docs/PHASE-1-ARCHITECTURE.md` for the full roadmap; SQL execution lives in
this service, Python code execution is a separate service
(`../execution-service`).

## Setup

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
python3 -c "import secrets; print(secrets.token_urlsafe(48))"   # run twice,
# paste the two outputs into .env as JWT_SECRET and SESSION_SECRET
```

Needs Postgres (with pgvector) and Redis running — see
`../infra/docker-compose.yml`, or `brew services start postgresql redis`.
The SQL Lab additionally needs its own database and a low-privilege role
(`sql_lab_readonly`) — see `docs/PHASE-1-ARCHITECTURE.md` §19/§7 for why it's
a separate database, not a schema in this one.

## Run migrations

```bash
alembic upgrade head
```

Then optionally seed real example content:

```bash
python3 scripts/seed_curriculum.py
python3 scripts/seed_tools.py
python3 scripts/seed_projects.py
python3 scripts/seed_gamification.py
python3 scripts/grant_admin.py you@example.com   # first admin — see the script's docstring
```

## Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

Interactive API docs: http://localhost:8000/docs

## Run tests

```bash
createdb dataforge_test   # once
pytest tests/ -v
```

`tests/conftest.py` points the test process at `dataforge_test` and a
separate Redis DB index automatically — it will not touch your dev
database. Migrations run for real against it (not a hand-maintained test
schema), and roll back at the end of the session.

## What's real

Auth (cookie-based, rate-limited, refresh rotation), OAuth (honest 503 when
unconfigured), curriculum + server-graded quizzes, Mac Setup Wizard with
Homebrew commands verified against the live index, SQL Lab with a real
low-privilege Postgres role, AI Tutor (honest 503 without an API key),
dataset upload with real pandas profiling, gamification computed live from
activity tables (never a mutable counter), SM-2 spaced repetition, and an
admin dashboard with real RBAC enforcement.

## Verified, not just written

Every phase in this backend was exercised with real requests against a
real local Postgres + Redis, not just written and assumed — see each
phase's chat summary for specifics. The Phase 13 test suite (28 backend
tests) turns the highest-value manual checks into automated regression
tests, including a regression test for a real bug found in Phase 11
(re-visiting a completed lesson silently downgraded it back to
in-progress). `ruff check` is clean; CI runs both on every push
(`.github/workflows/ci.yml`) — written to mirror the exact commands
verified locally, but not yet observed running on GitHub itself.

## Known gaps

- Email verification and password reset are deliberately deferred — need
  the Celery/email worker that doesn't exist yet.
- OAuth and AI Tutor code paths are real but untested against the actual
  Google/GitHub/Anthropic APIs — no credentials available in this
  environment. Both degrade honestly (503) rather than faking success.
- CI workflow hasn't been observed running on GitHub Actions itself.

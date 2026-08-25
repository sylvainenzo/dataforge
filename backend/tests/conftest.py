"""Sets DATABASE_URL to the dedicated dataforge_test database BEFORE any
app module is imported anywhere, since Settings() is instantiated once at
import time. This must stay the first thing that happens in the test
process — conftest.py is guaranteed to load before test modules."""

import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://user@localhost:5432/dataforge_test")
os.environ.setdefault("JWT_SECRET", "test-secret-not-for-production-use-only-in-ci")
os.environ.setdefault("SQL_LAB_DATABASE_URL", os.environ["DATABASE_URL"])  # unused by these tests, just needs to parse
# A different Redis DB index than dev (0) — otherwise rate-limit counters
# accumulated from manual dev-session testing bleed into test runs and
# cause spurious 429s.
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/2")

import subprocess  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

BACKEND_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """Runs the real Alembic migration chain against dataforge_test once
    per test session — the same migrations that create the real database,
    not a hand-maintained test schema that could drift from it."""

    subprocess.run(
        ["alembic", "upgrade", "head"], cwd=BACKEND_ROOT, check=True, env={**os.environ}
    )
    yield
    subprocess.run(
        ["alembic", "downgrade", "base"], cwd=BACKEND_ROOT, check=True, env={**os.environ}
    )


@pytest_asyncio.fixture(autouse=True)
async def flush_test_redis(apply_migrations):
    """Per-test, not per-session: rate-limit counters are keyed by
    request.client.host, which is the same fake value for every request
    under ASGITransport — without this, tests that each call
    register/login several times exhaust the real 5/min and 10/min limits
    partway through the suite and start silently failing with 429s."""

    from app.core.redis import redis_client

    await redis_client.flushdb()
    yield


@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    """Truncates all app tables between tests so each test starts from a
    known-empty state, without re-running migrations per test (slow).
    Excludes `roles`: it's reference/lookup data seeded once by the
    migration itself (op.bulk_insert in the initial migration), not
    per-test fixture data — truncating and re-seeding it every test just
    fights the migration's own seed and risks duplicate-key errors."""

    from app.core.db import async_engine

    yield

    async with async_engine.begin() as conn:
        result = await conn.execute(
            text(
                "SELECT tablename FROM pg_tables WHERE schemaname='public' "
                "AND tablename NOT IN ('alembic_version', 'roles')"
            )
        )
        tables = [row[0] for row in result.fetchall()]
        if tables:
            await conn.execute(text(f"TRUNCATE TABLE {', '.join(tables)} RESTART IDENTITY CASCADE"))


@pytest_asyncio.fixture
async def client():
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

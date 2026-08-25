from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_SANDBOX_PYTHON = str(Path(__file__).resolve().parent.parent / "sandbox-env" / "bin" / "python3")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Deliberately the same secret/algorithm as the Core API (app/core/security.py)
    # so this service can independently verify a user's access token without a
    # network round-trip back to the Core API on every WebSocket message.
    jwt_secret: str
    jwt_algorithm: str = "HS256"

    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql+psycopg://user@localhost:5432/dataforge_dev"

    cors_origins: list[str] = ["http://localhost:5180"]

    execution_timeout_seconds: int = 10
    execution_memory_limit_mb: int = 256
    execution_max_output_bytes: int = 64_000
    execution_rate_limit_per_minute: int = 20

    # A dedicated venv (execution-service/sandbox-env, built by
    # `python3 -m venv sandbox-env && sandbox-env/bin/pip install pandas numpy`)
    # standing in for what a real container base image would provide —
    # deliberately NOT this service's own interpreter, so submitted code
    # can't reach this service's own dependencies (FastAPI, SQLAlchemy, the
    # JWT secret's import path, etc.) even in principle.
    sandbox_python_path: str = _DEFAULT_SANDBOX_PYTHON

    # System Rscript — there is no per-language sandbox venv equivalent for
    # R the way there is for Python; the same resource-limit / stripped-env
    # subprocess protections apply regardless.
    sandbox_r_path: str = "/usr/local/bin/Rscript"


settings = Settings()

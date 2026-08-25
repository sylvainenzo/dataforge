from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_postgres_scheme(url: str) -> str:
    """Managed Postgres add-ons (Railway, Render, Heroku-style) hand you a
    plain postgres:// or postgresql:// URL — this app's async engine needs
    the +psycopg driver scheme. Accept either so pasting a platform's
    connection string verbatim doesn't silently break the app at startup."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://user@localhost:5432/dataforge_dev"
    redis_url: str = "redis://localhost:6379/0"

    @field_validator("database_url", "sql_lab_database_url", mode="after")
    @classmethod
    def _fix_postgres_scheme(cls, v: str) -> str:
        return _normalize_postgres_scheme(v)

    # No default: a missing secret must fail loudly, never fall back to a
    # value baked into source control.
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    cors_origins: list[str] = ["http://localhost:5180"]
    # Cookies must be Secure over HTTPS in any real deployment; only relaxed
    # for plain-HTTP local development.
    cookie_secure: bool = False
    # "lax" works when frontend and backend share a site (or are both on
    # localhost). Once they're on different domains (e.g. a Netlify
    # frontend calling a Railway/Render backend), the browser won't attach
    # a Lax cookie to that cross-site fetch at all — auth silently breaks.
    # Set COOKIE_SAMESITE=none (requires cookie_secure=true, which browsers
    # enforce) for a split-domain deployment.
    cookie_samesite: str = "lax"

    session_secret: str = "dev-only-session-secret-change-me"
    google_client_id: str | None = None
    google_client_secret: str | None = None
    github_client_id: str | None = None
    github_client_secret: str | None = None
    oauth_redirect_base_url: str = "http://localhost:8000"

    rate_limit_login_per_minute: int = 10
    rate_limit_register_per_minute: int = 5

    # A separate database, connected as a dedicated low-privilege role
    # (SELECT-only, scoped to the sample_data schema — see
    # execution-service/README-adjacent Phase 1 §19) — never the app's own
    # transactional database or a privileged role.
    sql_lab_database_url: str = "postgresql+psycopg://user@localhost:5432/dataforge_sql_lab"
    sql_lab_rate_limit_per_minute: int = 30

    # None means the AI Tutor is disabled — endpoints return a clear 503
    # rather than pretending to work (same pattern as unconfigured OAuth).
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-5"
    ai_tutor_rate_limit_per_minute: int = 15

    # Local filesystem, gitignored — standing in for the S3/MinIO storage
    # architecture from Phase 1 §22 (no MinIO/S3 available in this
    # environment, same category of gap as Docker for Phase 7's sandbox).
    dataset_storage_path: str = "storage/datasets"
    dataset_max_upload_mb: int = 50
    certificate_storage_path: str = "storage/certificates"

    # None means password-reset emails can't actually be sent — the
    # forgot-password endpoint returns a clear 503 rather than silently
    # doing nothing (same pattern as the unconfigured AI Tutor/OAuth).
    resend_api_key: str | None = None
    email_from: str = "DataForge <onboarding@resend.dev>"
    # Used to build the link inside the reset email (e.g. the Netlify URL
    # in production) — this backend has no other way to know its own
    # frontend's address.
    frontend_url: str = "http://localhost:5180"
    reset_password_token_expire_minutes: int = 30
    rate_limit_forgot_password_per_minute: int = 3


settings = Settings()

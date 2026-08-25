import json
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings

# Raw SQL against the shared audit_logs table rather than importing the Core
# API's ORM models — keeps this service genuinely independent/deployable on
# its own, per Phase 1 §3's "separate deployable" requirement.
_engine = create_async_engine(settings.database_url, future=True)


async def log_execution(*, user_id: uuid.UUID, language: str, exit_code: str, duration_ms: int) -> None:
    metadata = json.dumps({"language": language, "exit_code": exit_code, "duration_ms": duration_ms})
    async with _engine.begin() as conn:
        await conn.execute(
            text(
                """
                INSERT INTO audit_logs (user_id, action, resource_type, event_metadata, created_at)
                VALUES (:user_id, 'code_execution', 'execution_run', CAST(:metadata AS jsonb), now())
                """
            ),
            {"user_id": str(user_id), "metadata": metadata},
        )

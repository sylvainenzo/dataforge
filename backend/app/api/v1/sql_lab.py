from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.core.config import settings
from app.core.db import get_db
from app.core.sql_lab_db import SqlLabSessionLocal
from app.core.token_store import check_rate_limit
from app.models.platform import AuditLog
from app.schemas.sql_lab import SqlRunRequest, SqlRunResult
from app.services.sql_lab_exercises import EXERCISES, SqlExercise
from app.services.sql_lab_service import QueryRejectedError, run_query

router = APIRouter(prefix="/sql-lab", tags=["sql-lab"])


@router.get("/exercises", response_model=list[SqlExercise])
async def list_exercises(current_user: CurrentUser = Depends(get_current_user)):
    return EXERCISES


@router.post("/execute", response_model=SqlRunResult)
async def execute_query(
    body: SqlRunRequest,
    request: Request,
    app_db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    client_ip = request.client.host if request.client else "unknown"
    if not await check_rate_limit("sql-lab", client_ip, settings.sql_lab_rate_limit_per_minute):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many queries, slow down")

    async with SqlLabSessionLocal() as db:
        try:
            columns, rows, truncated = await run_query(db, body.sql)
        except QueryRejectedError as exc:
            # Logged even on rejection — a rejected query is still a real
            # attempt and legitimate activity/audit signal.
            app_db.add(AuditLog(user_id=current_user.id, action="sql_query", resource_type="sql_lab_run"))
            await app_db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    app_db.add(AuditLog(user_id=current_user.id, action="sql_query", resource_type="sql_lab_run"))
    await app_db.commit()

    return SqlRunResult(columns=columns, rows=rows, truncated=truncated, row_count=len(rows))

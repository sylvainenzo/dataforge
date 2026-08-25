import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.platform import AuditLog


async def log_event(
    db: AsyncSession,
    *,
    action: str,
    resource_type: str,
    user_id: uuid.UUID | None = None,
    ip_address: str | None = None,
    metadata: dict | None = None,
) -> None:
    """Fire-and-forget audit trail — Phase 1 §13/§52. Auth events
    specifically (login success/failure) are what let an operator notice a
    credential-stuffing attempt; execution/SQL events were already logged
    from Phases 7-8, this fills the auth gap."""

    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            event_metadata=metadata,
            ip_address=ip_address,
        )
    )
    await db.commit()

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.identity import OAuthAccount, OAuthProvider, Profile, Role, User, UserRole
from app.services.auth_service import DEFAULT_ROLE, get_user_by_email


async def get_or_create_oauth_user(
    db: AsyncSession,
    *,
    provider: OAuthProvider,
    provider_account_id: str,
    email: str,
    display_name: str,
) -> User:
    """Three cases, in order: (1) this exact provider account has signed in
    before -> return its linked user; (2) no OAuthAccount yet, but a user
    with this email already exists (e.g. registered by password) -> link the
    OAuth account to it; (3) brand new -> create user + profile + role +
    OAuthAccount together."""

    existing_link = await db.execute(
        select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_account_id == provider_account_id,
        )
    )
    link = existing_link.scalar_one_or_none()
    if link is not None:
        result = await db.execute(select(User).where(User.id == link.user_id))
        return result.scalar_one()

    normalized_email = email.lower()
    user = await get_user_by_email(db, normalized_email)
    if user is None:
        user = User(email=normalized_email, password_hash=None, is_active=True)
        db.add(user)
        await db.flush()

        db.add(Profile(user_id=user.id, display_name=display_name))

        role_result = await db.execute(select(Role).where(Role.name == DEFAULT_ROLE))
        role = role_result.scalar_one()
        db.add(UserRole(user_id=user.id, role_id=role.id))

    db.add(OAuthAccount(user_id=user.id, provider=provider, provider_account_id=provider_account_id))
    await db.commit()
    await db.refresh(user)
    return user

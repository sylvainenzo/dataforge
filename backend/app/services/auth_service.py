import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.identity import Profile, Role, User, UserRole

DEFAULT_ROLE = "student"


class EmailAlreadyRegisteredError(Exception):
    pass


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_roles(db: AsyncSession, user_id: uuid.UUID) -> list[str]:
    result = await db.execute(
        select(Role.name).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user_id)
    )
    return list(result.scalars().all())


async def get_display_name(db: AsyncSession, user_id: uuid.UUID) -> str | None:
    result = await db.execute(select(Profile.display_name).where(Profile.user_id == user_id))
    return result.scalar_one_or_none()


async def register_user(db: AsyncSession, *, email: str, password: str, display_name: str) -> User:
    normalized_email = email.lower()
    if await get_user_by_email(db, normalized_email) is not None:
        raise EmailAlreadyRegisteredError(normalized_email)

    user = User(email=normalized_email, password_hash=hash_password(password), is_active=True)
    db.add(user)
    await db.flush()  # assigns user.id before we reference it below

    db.add(Profile(user_id=user.id, display_name=display_name))

    default_role = await db.execute(select(Role).where(Role.name == DEFAULT_ROLE))
    role = default_role.scalar_one()
    db.add(UserRole(user_id=user.id, role_id=role.id))

    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, *, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if user is None or user.password_hash is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def update_display_name(db: AsyncSession, user_id: uuid.UUID, display_name: str) -> None:
    result = await db.execute(select(Profile).where(Profile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        db.add(Profile(user_id=user_id, display_name=display_name))
    else:
        profile.display_name = display_name
    await db.commit()


class IncorrectPasswordError(Exception):
    pass


class NoPasswordSetError(Exception):
    """The account only has an OAuth login (Google/GitHub) and has never
    set a password, so there is nothing to verify a 'current password'
    against."""


async def change_password(db: AsyncSession, user_id: uuid.UUID, *, current_password: str, new_password: str) -> None:
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise ValueError(f"User {user_id} not found")
    if user.password_hash is None:
        raise NoPasswordSetError()
    if not verify_password(current_password, user.password_hash):
        raise IncorrectPasswordError()

    user.password_hash = hash_password(new_password)
    await db.commit()

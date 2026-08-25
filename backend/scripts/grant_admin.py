"""Bootstrap script — grants the admin role to a user by email. There is no
UI path to create the first admin (chicken-and-egg problem: admin UI is
itself admin-gated), so this is the documented way to promote the first
admin. Run: python3 scripts/grant_admin.py user@example.com
"""

import asyncio
import sys

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.identity import Role, User, UserRole


async def grant_admin(email: str) -> None:
    async with AsyncSessionLocal() as db:
        user_result = await db.execute(select(User).where(User.email == email.lower()))
        user = user_result.scalar_one_or_none()
        if user is None:
            print(f"No user found with email {email}")
            return

        role_result = await db.execute(select(Role).where(Role.name == "admin"))
        admin_role = role_result.scalar_one()

        existing = await db.execute(
            select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == admin_role.id)
        )
        if existing.scalar_one_or_none() is not None:
            print(f"{email} is already an admin.")
            return

        db.add(UserRole(user_id=user.id, role_id=admin_role.id))
        await db.commit()
        print(f"Granted admin to {email}.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/grant_admin.py user@example.com")
        sys.exit(1)
    asyncio.run(grant_admin(sys.argv[1]))

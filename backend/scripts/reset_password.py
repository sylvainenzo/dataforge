"""Admin stopgap — sets a user's password directly by email. There is no
self-service "forgot password" flow yet (that needs a transactional email
provider wired in to actually deliver a reset link, which isn't set up).
Until then, this is how a forgotten password gets reset: the admin runs
this against the live backend, then tells the user their temporary
password so they can sign in and change it themselves from Settings.

Run: python3 scripts/reset_password.py user@example.com NewTemporaryPass123
"""

import asyncio
import sys

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.core.security import hash_password
from app.models.identity import User


async def reset_password(email: str, new_password: str) -> None:
    if len(new_password) < 8:
        print("Password must be at least 8 characters.")
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email.lower()))
        user = result.scalar_one_or_none()
        if user is None:
            print(f"No user found with email {email}")
            return

        user.password_hash = hash_password(new_password)
        await db.commit()
        print(f"Password reset for {email}. Tell them to sign in and change it from Settings.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/reset_password.py user@example.com NewTemporaryPass123")
        sys.exit(1)
    asyncio.run(reset_password(sys.argv[1], sys.argv[2]))

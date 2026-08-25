import httpx

from app.core.config import settings

RESEND_API_URL = "https://api.resend.com/emails"


class EmailNotConfiguredError(Exception):
    pass


class EmailDeliveryError(Exception):
    pass


async def send_password_reset_email(to_email: str, reset_url: str, *, expires_in_minutes: int) -> None:
    if not settings.resend_api_key:
        raise EmailNotConfiguredError("RESEND_API_KEY is not set")

    body = (
        "Someone (hopefully you) asked to reset the password on your DataForge account.\n\n"
        f"Reset it here: {reset_url}\n\n"
        f"This link expires in {expires_in_minutes} minutes and only works once.\n\n"
        "If you didn't ask for this, you can safely ignore this email — your password hasn't been changed."
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            RESEND_API_URL,
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json={
                "from": settings.email_from,
                "to": [to_email],
                "subject": "Reset your DataForge password",
                "text": body,
            },
        )

    if response.status_code >= 400:
        raise EmailDeliveryError(f"Resend API returned {response.status_code}: {response.text}")

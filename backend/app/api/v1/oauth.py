from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from app.core.config import settings
from app.core.cookies import set_auth_cookies
from app.core.db import get_db
from app.core.security import create_access_token, create_refresh_token
from app.models.identity import OAuthProvider
from app.services.oauth_service import get_or_create_oauth_user

router = APIRouter(prefix="/auth", tags=["oauth"])

oauth = OAuth()

if settings.google_client_id and settings.google_client_secret:
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

if settings.github_client_id and settings.github_client_secret:
    oauth.register(
        name="github",
        client_id=settings.github_client_id,
        client_secret=settings.github_client_secret,
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "read:user user:email"},
    )


def _require_provider_client(provider_name: str):
    client = oauth.create_client(provider_name)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{provider_name.capitalize()} sign-in is not configured on this server",
        )
    return client


@router.get("/google/login")
async def google_login(request: Request):
    client = _require_provider_client("google")
    redirect_uri = f"{settings.oauth_redirect_base_url}/api/v1/auth/google/callback"
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    client = _require_provider_client("google")
    token = await client.authorize_access_token(request)
    userinfo = token.get("userinfo") or await client.userinfo(token=token)

    user = await get_or_create_oauth_user(
        db,
        provider=OAuthProvider.GOOGLE,
        provider_account_id=userinfo["sub"],
        email=userinfo["email"],
        display_name=userinfo.get("name", userinfo["email"]),
    )
    return _login_response(user)


@router.get("/github/login")
async def github_login(request: Request):
    client = _require_provider_client("github")
    redirect_uri = f"{settings.oauth_redirect_base_url}/api/v1/auth/github/callback"
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/github/callback")
async def github_callback(request: Request, db: AsyncSession = Depends(get_db)):
    client = _require_provider_client("github")
    token = await client.authorize_access_token(request)

    profile_resp = await client.get("user", token=token)
    profile = profile_resp.json()

    email = profile.get("email")
    if not email:
        # GitHub only returns a public email if the user opted in; fall back
        # to the dedicated emails endpoint for the primary verified address.
        emails_resp = await client.get("user/emails", token=token)
        primary = next((e for e in emails_resp.json() if e.get("primary")), None)
        email = primary["email"] if primary else None
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your GitHub account has no accessible email address",
        )

    user = await get_or_create_oauth_user(
        db,
        provider=OAuthProvider.GITHUB,
        provider_account_id=str(profile["id"]),
        email=email,
        display_name=profile.get("name") or profile.get("login", email),
    )
    return _login_response(user)


def _login_response(user) -> Response:
    access_token = create_access_token(user.id)
    refresh_token, _, _ = create_refresh_token(user.id)
    # Redirect back into the SPA — it re-fetches /auth/me to pick up the
    # session from the cookies set below rather than receiving tokens in
    # the URL, which would leak them into browser history/referrer headers.
    response = RedirectResponse(url=f"{settings.cors_origins[0]}/auth/callback")
    set_auth_cookies(response, access_token, refresh_token, settings.refresh_token_expire_days * 86400)
    return response

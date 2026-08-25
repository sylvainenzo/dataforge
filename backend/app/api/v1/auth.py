import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user, get_refresh_payload
from app.core.config import settings
from app.core.cookies import clear_auth_cookies, set_auth_cookies
from app.core.db import get_db
from app.core.security import (
    InvalidTokenError,
    TokenType,
    create_access_token,
    create_refresh_token,
    create_reset_password_token,
    decode_token,
)
from app.core.token_store import check_rate_limit, is_jti_revoked, revoke_jti
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    UpdateProfileRequest,
    UserRead,
)
from app.services.audit_service import log_event
from app.services.auth_service import (
    EmailAlreadyRegisteredError,
    IncorrectPasswordError,
    NoPasswordSetError,
    authenticate_user,
    change_password,
    get_display_name,
    get_user_by_email,
    get_user_by_id,
    get_user_roles,
    register_user,
    set_password,
    update_display_name,
)
from app.services.email_service import EmailDeliveryError, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])


async def _enforce_rate_limit(request: Request, scope: str, limit: int) -> None:
    client_ip = request.client.host if request.client else "unknown"
    if not await check_rate_limit(scope, client_ip, limit):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests, slow down")


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    await _enforce_rate_limit(request, "register", settings.rate_limit_register_per_minute)

    try:
        user = await register_user(db, email=body.email, password=body.password, display_name=body.display_name)
    except EmailAlreadyRegisteredError as exc:
        # Deliberately vague — confirming an email is *not* registered would
        # let an attacker enumerate accounts.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Could not register this account"
        ) from exc

    access_token = create_access_token(user.id)
    refresh_token, _, _ = create_refresh_token(user.id)
    set_auth_cookies(response, access_token, refresh_token, settings.refresh_token_expire_days * 86400)

    client_ip = request.client.host if request.client else None
    await log_event(db, action="register", resource_type="user", user_id=user.id, ip_address=client_ip)

    roles = await get_user_roles(db, user.id)
    display_name = await get_display_name(db, user.id)
    return UserRead(id=user.id, email=user.email, display_name=display_name, is_active=user.is_active, roles=roles)


@router.post("/login", response_model=UserRead)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    await _enforce_rate_limit(request, "login", settings.rate_limit_login_per_minute)
    client_ip = request.client.host if request.client else None

    user = await authenticate_user(db, email=body.email, password=body.password)
    if user is None:
        # No user_id on a failed attempt — logging the attempted email
        # would let anyone harvest which addresses are registered, so this
        # only records that a failure happened from this IP, which is
        # exactly what brute-force detection needs.
        await log_event(db, action="login_failed", resource_type="user", ip_address=client_ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = create_access_token(user.id)
    refresh_token, _, _ = create_refresh_token(user.id)
    set_auth_cookies(response, access_token, refresh_token, settings.refresh_token_expire_days * 86400)

    await log_event(db, action="login", resource_type="user", user_id=user.id, ip_address=client_ip)

    roles = await get_user_roles(db, user.id)
    display_name = await get_display_name(db, user.id)
    return UserRead(id=user.id, email=user.email, display_name=display_name, is_active=user.is_active, roles=roles)


@router.post("/refresh", response_model=UserRead)
async def refresh(
    response: Response,
    db: AsyncSession = Depends(get_db),
    refresh_payload: dict = Depends(get_refresh_payload),
):
    """Rotates the refresh token on every use: the old jti is revoked and a
    new refresh token issued, so a leaked-but-unused-yet token has a single
    use window rather than remaining valid for its full 30-day life."""

    user_id = uuid.UUID(refresh_payload["sub"])
    user = await get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    old_expires_at = datetime.fromtimestamp(refresh_payload["exp"], tz=UTC)
    await revoke_jti(refresh_payload["jti"], old_expires_at)

    access_token = create_access_token(user.id)
    new_refresh_token, _, new_expires_at = create_refresh_token(user.id)
    set_auth_cookies(response, access_token, new_refresh_token, settings.refresh_token_expire_days * 86400)

    roles = await get_user_roles(db, user.id)
    display_name = await get_display_name(db, user.id)
    return UserRead(id=user.id, email=user.email, display_name=display_name, is_active=user.is_active, roles=roles)


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response, refresh_payload: dict = Depends(get_refresh_payload)):
    expires_at = datetime.fromtimestamp(refresh_payload["exp"], tz=UTC)
    await revoke_jti(refresh_payload["jti"], expires_at)

    clear_auth_cookies(response)
    return MessageResponse(message="Logged out")


@router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUser = Depends(get_current_user)):
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        is_active=True,
        roles=current_user.roles,
    )


@router.patch("/me", response_model=UserRead)
async def update_me(
    body: UpdateProfileRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await update_display_name(db, current_user.id, body.display_name)
    roles = await get_user_roles(db, current_user.id)
    return UserRead(
        id=current_user.id, email=current_user.email, display_name=body.display_name, is_active=True, roles=roles
    )


@router.post("/change-password", response_model=MessageResponse)
async def change_my_password(
    body: ChangePasswordRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await change_password(
            db, current_user.id, current_password=body.current_password, new_password=body.new_password
        )
    except IncorrectPasswordError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
        ) from exc
    except NoPasswordSetError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account signs in via OAuth and has no password to change",
        ) from exc

    client_ip = request.client.host if request.client else None
    await log_event(db, action="password_changed", resource_type="user", user_id=current_user.id, ip_address=client_ip)

    return MessageResponse(message="Password changed")


_FORGOT_PASSWORD_GENERIC_MESSAGE = MessageResponse(
    message="If that email is registered, a reset link has been sent."
)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    body: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await _enforce_rate_limit(request, "forgot-password", settings.rate_limit_forgot_password_per_minute)

    # Checked before the user lookup, and unconditionally — an existing vs.
    # non-existing email must produce the exact same response, or the 503
    # itself becomes a way to enumerate registered accounts.
    if not settings.resend_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Password reset emails aren't configured on this server yet.",
        )

    user = await get_user_by_email(db, body.email)
    if user is not None and user.is_active:
        token, _, _ = create_reset_password_token(user.id)
        reset_url = f"{settings.frontend_url}/reset-password?token={token}"
        try:
            await send_password_reset_email(
                user.email, reset_url, expires_in_minutes=settings.reset_password_token_expire_minutes
            )
        except EmailDeliveryError:
            # Still returns the generic message below — surfacing a delivery
            # failure here would also leak whether the email was registered.
            pass

    return _FORGOT_PASSWORD_GENERIC_MESSAGE


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(body: ResetPasswordRequest, request: Request, db: AsyncSession = Depends(get_db)):
    invalid_link_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="This reset link is invalid or has expired."
    )

    try:
        payload = decode_token(body.token, TokenType.RESET_PASSWORD)
    except InvalidTokenError as exc:
        raise invalid_link_error from exc

    if await is_jti_revoked(payload["jti"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This reset link has already been used.")

    user_id = uuid.UUID(payload["sub"])
    user = await get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise invalid_link_error

    await set_password(db, user_id, new_password=body.new_password)

    expires_at = datetime.fromtimestamp(payload["exp"], tz=UTC)
    await revoke_jti(payload["jti"], expires_at)

    client_ip = request.client.host if request.client else None
    await log_event(db, action="password_reset", resource_type="user", user_id=user_id, ip_address=client_ip)

    return MessageResponse(message="Password reset — you can now sign in with your new password.")

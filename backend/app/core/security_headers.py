from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Baseline defensive headers — Phase 1 §52. Not a substitute for the
    real controls (parameterized queries, RBAC, rate limiting) already in
    place elsewhere, but cheap and standard on any production API."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # /docs and /redoc are FastAPI's own Swagger/ReDoc UI, which load
        # their JS/CSS from a CDN — a strict default-src would silently
        # break the interactive docs page. Every real API path stays
        # locked down; only these two dev-tool pages get a relaxed policy.
        if request.url.path in ("/docs", "/redoc"):
            # Swagger/ReDoc's own HTML embeds an inline bootstrap <script>,
            # so 'unsafe-inline' is unavoidable here specifically — scoped
            # to these two dev-tool paths only, never the API itself.
            response.headers["Content-Security-Policy"] = (
                "default-src 'self' cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
                "img-src 'self' fastapi.tiangolo.com data:; "
                "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net"
            )
        else:
            response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"

        if settings.cookie_secure:
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response

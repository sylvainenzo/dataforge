from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.admin import router as admin_router
from app.api.v1.ai_tutor import router as ai_tutor_router
from app.api.v1.auth import router as auth_router
from app.api.v1.career import router as career_router
from app.api.v1.certificates import router as certificates_router
from app.api.v1.curriculum import router as curriculum_router
from app.api.v1.datasets import router as datasets_router
from app.api.v1.knowledge_base import router as knowledge_base_router
from app.api.v1.oauth import router as oauth_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.progress import router as progress_router
from app.api.v1.projects import router as projects_router
from app.api.v1.search import router as search_router
from app.api.v1.sql_lab import router as sql_lab_router
from app.api.v1.tools import router as tools_router
from app.core.config import settings
from app.core.security_headers import SecurityHeadersMiddleware

app = FastAPI(title="DataForge API", version="0.1.0")

app.add_middleware(SecurityHeadersMiddleware)

# Required by Authlib's Starlette OAuth client to stash the CSRF state
# between /login and /callback (Phase 1 §13 OAuth2 flow).
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(oauth_router, prefix="/api/v1")
app.include_router(curriculum_router, prefix="/api/v1")
app.include_router(tools_router, prefix="/api/v1")
app.include_router(sql_lab_router, prefix="/api/v1")
app.include_router(ai_tutor_router, prefix="/api/v1")
app.include_router(datasets_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")
app.include_router(progress_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(knowledge_base_router, prefix="/api/v1")
app.include_router(career_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(certificates_router, prefix="/api/v1")
app.include_router(portfolio_router, prefix="/api/v1")


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """A constraint violation (duplicate slug, duplicate order within a
    course, etc.) is a client input problem, not a server fault — surface it
    as 409 with the DB's own reason instead of a bare 500."""

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": f"Conflicts with existing data: {exc.orig}"},
    )


@app.get("/api/v1/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

import uuid
from datetime import datetime

from pydantic import BaseModel


class PortfolioSettings(BaseModel):
    bio: str | None
    portfolio_public: bool


class PortfolioSettingsUpdate(BaseModel):
    bio: str | None = None
    portfolio_public: bool | None = None


class PortfolioProject(BaseModel):
    project_title: str
    project_slug: str
    submission_url: str | None
    reviewed_at: datetime | None


class PortfolioCertificate(BaseModel):
    course_title: str
    certificate_number: str
    issued_at: datetime


class PublicPortfolio(BaseModel):
    user_id: uuid.UUID
    display_name: str
    bio: str | None
    projects: list[PortfolioProject]
    certificates: list[PortfolioCertificate]

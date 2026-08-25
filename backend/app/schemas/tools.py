import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class ToolSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    slug: str
    description: str
    category: str
    mac_supported: bool
    apple_silicon_supported: bool
    intel_supported: bool
    last_verified_at: date


class ToolDetail(ToolSummary):
    official_url: str
    docs_url: str | None
    install_method: str
    homebrew_command: str | None
    verification_command: str | None
    common_errors: dict | None
    alternatives: list[str] | None


class InstallGuideRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    content: dict
    last_verified_at: date


class WizardChecklistItem(BaseModel):
    tool: ToolSummary
    essential: bool
    reason: str

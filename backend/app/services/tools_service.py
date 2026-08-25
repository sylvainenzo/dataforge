import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_base import InstallGuide, Tool

# Which tools are "essential" vs "optional" depends on career + experience.
# This is server-side logic, not a fabricated database relationship — every
# tool listed genuinely applies to every track; only Docker's priority
# shifts, since a beginner doesn't need containers on day one but a Data
# Engineer or ML Engineer track hits Docker quickly.
DOCKER_PRIORITY_CAREERS = {"data-engineer", "ml-engineer", "analytics-engineer"}


async def list_tools(db: AsyncSession) -> list[Tool]:
    result = await db.execute(select(Tool).order_by(Tool.name))
    return list(result.scalars().all())


async def get_tool_detail(db: AsyncSession, slug: str) -> Tool | None:
    result = await db.execute(select(Tool).where(Tool.slug == slug))
    return result.scalar_one_or_none()


async def get_install_guide_for_tool(db: AsyncSession, tool_id: uuid.UUID) -> InstallGuide | None:
    result = await db.execute(select(InstallGuide).where(InstallGuide.tool_id == tool_id))
    return result.scalar_one_or_none()


async def build_checklist(
    db: AsyncSession, *, architecture: str, career: str, experience: str
) -> list[tuple[Tool, bool, str]]:
    tools = await list_tools(db)
    checklist: list[tuple[Tool, bool, str]] = []

    for tool in tools:
        if architecture == "apple_silicon" and not tool.apple_silicon_supported:
            continue
        if architecture == "intel" and not tool.intel_supported:
            continue

        if tool.slug == "docker-desktop":
            if career in DOCKER_PRIORITY_CAREERS:
                essential, reason = True, f"Core to the {career.replace('-', ' ')} track from early on."
            elif experience == "beginner":
                essential, reason = False, "Useful later — not needed for your first lessons."
            else:
                essential, reason = True, "You'll want this once labs start using containers."
        else:
            essential, reason = True, "Foundational for every DataForge track."

        checklist.append((tool, essential, reason))

    checklist.sort(key=lambda t: (not t[1], t[0].name))
    return checklist

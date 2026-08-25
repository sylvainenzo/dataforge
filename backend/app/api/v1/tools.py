from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.tools import InstallGuideRead, ToolDetail, ToolSummary, WizardChecklistItem
from app.services import tools_service

router = APIRouter(tags=["tools"])


@router.get("/tools", response_model=list[ToolSummary])
async def list_tools(db: AsyncSession = Depends(get_db)):
    return await tools_service.list_tools(db)


@router.get("/tools/{slug}", response_model=ToolDetail)
async def get_tool(slug: str, db: AsyncSession = Depends(get_db)):
    tool = await tools_service.get_tool_detail(db, slug)
    if tool is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    return tool


@router.get("/tools/{slug}/install-guide", response_model=InstallGuideRead)
async def get_install_guide(slug: str, db: AsyncSession = Depends(get_db)):
    tool = await tools_service.get_tool_detail(db, slug)
    if tool is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    guide = await tools_service.get_install_guide_for_tool(db, tool.id)
    if guide is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No install guide for this tool yet")
    return guide


class ChecklistRequest(BaseModel):
    architecture: Literal["apple_silicon", "intel"]
    career: str
    experience: Literal["beginner", "intermediate", "advanced"]


@router.post("/mac-setup/checklist", response_model=list[WizardChecklistItem])
async def generate_checklist(body: ChecklistRequest, db: AsyncSession = Depends(get_db)):
    checklist = await tools_service.build_checklist(
        db, architecture=body.architecture, career=body.career, experience=body.experience
    )
    return [WizardChecklistItem(tool=tool, essential=essential, reason=reason) for tool, essential, reason in checklist]

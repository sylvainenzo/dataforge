import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.core.db import get_db
from app.schemas.certificates import CertificateRead, CertificateVerification
from app.services import certificate_service

router = APIRouter(tags=["certificates"])


@router.get("/certificates", response_model=list[CertificateRead])
async def list_my_certificates(
    db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    return await certificate_service.list_user_certificates(db, current_user.id)


@router.post("/courses/{slug}/certificate", response_model=CertificateRead, status_code=status.HTTP_201_CREATED)
async def issue_course_certificate(
    slug: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    try:
        return await certificate_service.get_or_issue_certificate(db, current_user.id, slug)
    except certificate_service.CourseNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found") from exc
    except certificate_service.CourseNotCompleteError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complete every lesson in this course before requesting a certificate",
        ) from exc


@router.get("/certificates/{certificate_id}/download")
async def download_certificate(
    certificate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    path = await certificate_service.get_certificate_pdf_path(db, current_user.id, certificate_id)
    if path is None or not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")
    return FileResponse(path, media_type="application/pdf", filename=path.name)


@router.get("/certificates/verify/{certificate_number}", response_model=CertificateVerification)
async def verify_certificate(certificate_number: str, db: AsyncSession = Depends(get_db)):
    result = await certificate_service.verify_certificate(db, certificate_number)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No certificate found with that number")
    return result

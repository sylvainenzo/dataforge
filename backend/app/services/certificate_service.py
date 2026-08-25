import secrets
import uuid
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.curriculum import Course, Lesson, Module
from app.models.gamification import Certificate
from app.models.identity import Profile
from app.models.learning_science import ProgressStatus, UserProgress


class CourseNotCompleteError(Exception):
    pass


class CourseNotFoundError(Exception):
    pass


async def is_course_complete(db: AsyncSession, user_id: uuid.UUID, course_id: uuid.UUID) -> bool:
    total_result = await db.execute(
        select(func.count())
        .select_from(Lesson)
        .join(Module, Module.id == Lesson.module_id)
        .where(Module.course_id == course_id, Lesson.published == True)  # noqa: E712
    )
    total = total_result.scalar_one()
    if total == 0:
        return False

    completed_result = await db.execute(
        select(func.count())
        .select_from(Lesson)
        .join(Module, Module.id == Lesson.module_id)
        .join(
            UserProgress,
            (UserProgress.lesson_id == Lesson.id)
            & (UserProgress.user_id == user_id)
            & (UserProgress.status == ProgressStatus.COMPLETED),
        )
        .where(Module.course_id == course_id, Lesson.published == True)  # noqa: E712
    )
    completed = completed_result.scalar_one()
    return completed >= total


def _generate_certificate_number() -> str:
    # DF-XXXXXXXX — short, unique, and visibly not a sequential/guessable ID.
    return f"DF-{secrets.token_hex(4).upper()}"


def _render_pdf(*, recipient_name: str, course_title: str, certificate_number: str, issued_at) -> bytes:
    """A real, generated PDF — not a template image. Explicitly labeled as
    a platform-completion certificate, never claiming accreditation, per
    the Certificate model's own docstring."""

    from io import BytesIO

    buffer = BytesIO()
    page_size = landscape(letter)
    c = canvas.Canvas(buffer, pagesize=page_size)
    width, height = page_size

    ink = HexColor("#1a1830")
    accent = HexColor("#5850ec")
    muted = HexColor("#5b6472")

    c.setStrokeColor(accent)
    c.setLineWidth(3)
    c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 1.3 * inch, "DATAFORGE")

    c.setFillColor(ink)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2, height - 2.1 * inch, "Certificate of Platform Completion")

    c.setFont("Helvetica", 14)
    c.setFillColor(muted)
    c.drawCentredString(width / 2, height - 2.7 * inch, "This certifies that")

    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(ink)
    c.drawCentredString(width / 2, height - 3.3 * inch, recipient_name)

    c.setFont("Helvetica", 14)
    c.setFillColor(muted)
    c.drawCentredString(width / 2, height - 3.8 * inch, "has completed the course")

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(accent)
    c.drawCentredString(width / 2, height - 4.3 * inch, course_title)

    c.setFont("Helvetica", 10)
    c.setFillColor(muted)
    c.drawCentredString(
        width / 2,
        1.3 * inch,
        "This certifies completion of self-paced course content on the DataForge platform.",
    )
    c.drawCentredString(
        width / 2,
        1.1 * inch,
        "DataForge is not an accredited educational institution and this is not a university credential.",
    )

    c.setFont("Helvetica", 9)
    c.drawString(0.75 * inch, 0.75 * inch, f"Issued: {issued_at.strftime('%Y-%m-%d')}")
    c.drawRightString(width - 0.75 * inch, 0.75 * inch, f"Certificate No. {certificate_number}")

    c.showPage()
    c.save()
    return buffer.getvalue()


async def get_or_issue_certificate(db: AsyncSession, user_id: uuid.UUID, course_slug: str) -> Certificate:
    course_result = await db.execute(select(Course).where(Course.slug == course_slug))
    course = course_result.scalar_one_or_none()
    if course is None:
        raise CourseNotFoundError(course_slug)

    existing_result = await db.execute(
        select(Certificate).where(Certificate.user_id == user_id, Certificate.course_id == course.id)
    )
    existing = existing_result.scalar_one_or_none()
    if existing is not None:
        return existing

    if not await is_course_complete(db, user_id, course.id):
        raise CourseNotCompleteError(course_slug)

    profile_result = await db.execute(select(Profile.display_name).where(Profile.user_id == user_id))
    display_name = profile_result.scalar_one_or_none() or "DataForge Learner"

    certificate_number = _generate_certificate_number()
    certificate = Certificate(
        user_id=user_id,
        course_id=course.id,
        title=f"Certificate of Completion — {course.title}",
        certificate_number=certificate_number,
    )
    db.add(certificate)
    await db.flush()

    pdf_bytes = _render_pdf(
        recipient_name=display_name,
        course_title=course.title,
        certificate_number=certificate_number,
        issued_at=certificate.issued_at,
    )

    storage_dir = Path(settings.certificate_storage_path)
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_key = f"{certificate.id}.pdf"
    (storage_dir / storage_key).write_bytes(pdf_bytes)
    certificate.pdf_storage_key = storage_key

    await db.commit()
    await db.refresh(certificate)
    return certificate


async def list_user_certificates(db: AsyncSession, user_id: uuid.UUID) -> list[Certificate]:
    result = await db.execute(
        select(Certificate).where(Certificate.user_id == user_id).order_by(Certificate.issued_at.desc())
    )
    return list(result.scalars().all())


async def get_certificate_pdf_path(db: AsyncSession, user_id: uuid.UUID, certificate_id: uuid.UUID) -> Path | None:
    result = await db.execute(
        select(Certificate).where(Certificate.id == certificate_id, Certificate.user_id == user_id)
    )
    certificate = result.scalar_one_or_none()
    if certificate is None or certificate.pdf_storage_key is None:
        return None
    return Path(settings.certificate_storage_path) / certificate.pdf_storage_key


async def verify_certificate(db: AsyncSession, certificate_number: str) -> dict | None:
    """Public verification — no auth required, since the entire point of a
    certificate number is that anyone (an employer, etc.) can check it's
    real without needing an account."""

    result = await db.execute(
        select(Certificate, Course.title, Profile.display_name)
        .join(Course, Course.id == Certificate.course_id)
        .join(Profile, Profile.user_id == Certificate.user_id)
        .where(Certificate.certificate_number == certificate_number)
    )
    row = result.first()
    if row is None:
        return None
    certificate, course_title, display_name = row
    return {
        "certificate_number": certificate.certificate_number,
        "recipient_name": display_name,
        "course_title": course_title,
        "issued_at": certificate.issued_at,
    }

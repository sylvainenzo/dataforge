from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.core.config import settings
from app.core.db import get_db
from app.core.token_store import check_rate_limit
from app.schemas.datasets import DatasetDetail, DatasetSummary
from app.services import dataset_service
from app.services.dataset_service import UnsupportedFormatError

UPLOAD_RATE_LIMIT_PER_MINUTE = 5

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("", response_model=list[DatasetSummary])
async def list_datasets(db: AsyncSession = Depends(get_db)):
    return await dataset_service.list_datasets(db)


@router.get("/{slug}", response_model=DatasetDetail)
async def get_dataset(slug: str, db: AsyncSession = Depends(get_db)):
    dataset = await dataset_service.get_dataset(db, slug)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    latest_version = await dataset_service.get_latest_version(db, dataset.id)
    return DatasetDetail(
        id=dataset.id,
        name=dataset.name,
        slug=dataset.slug,
        description=dataset.description,
        source=dataset.source,
        license=dataset.license,
        difficulty=dataset.difficulty.value,
        format=dataset.format.value,
        latest_version=latest_version,
    )


@router.post("/upload", response_model=DatasetSummary, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(""),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    # Uploads are one of the few endpoints that write to disk and run real
    # parsing work — unlike most reads, unlimited requests here is a real
    # resource-exhaustion vector, not just noise.
    if not await check_rate_limit("dataset-upload", str(current_user.id), UPLOAD_RATE_LIMIT_PER_MINUTE):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many uploads, slow down")

    max_bytes = settings.dataset_max_upload_mb * 1024 * 1024
    file_bytes = await file.read()
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File exceeds the {settings.dataset_max_upload_mb}MB limit for synchronous processing.",
        )

    try:
        dataset = await dataset_service.ingest_upload(
            db,
            file_bytes=file_bytes,
            filename=file.filename or "upload.csv",
            name=name,
            description=description,
            uploaded_by=current_user.id,
        )
    except UnsupportedFormatError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not parse file: {exc}"
        ) from exc

    return dataset

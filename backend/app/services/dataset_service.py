import uuid
from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.base import DifficultyLevel
from app.models.datasets import Dataset, DatasetFormat, DatasetVersion, ProfilingStatus
from app.services.dataset_profiling import profile_dataframe

_READERS = {
    DatasetFormat.CSV: pd.read_csv,
    DatasetFormat.JSON: pd.read_json,
    DatasetFormat.PARQUET: pd.read_parquet,
    DatasetFormat.EXCEL: pd.read_excel,
}

_EXTENSION_TO_FORMAT = {
    ".csv": DatasetFormat.CSV,
    ".json": DatasetFormat.JSON,
    ".parquet": DatasetFormat.PARQUET,
    ".xlsx": DatasetFormat.EXCEL,
    ".xls": DatasetFormat.EXCEL,
}


class UnsupportedFormatError(Exception):
    pass


def detect_format(filename: str) -> DatasetFormat:
    ext = Path(filename).suffix.lower()
    if ext not in _EXTENSION_TO_FORMAT:
        raise UnsupportedFormatError(f"Unsupported file type '{ext}'. Use CSV, JSON, Parquet, or Excel.")
    return _EXTENSION_TO_FORMAT[ext]


async def list_datasets(db: AsyncSession) -> list[Dataset]:
    result = await db.execute(select(Dataset).order_by(Dataset.name))
    return list(result.scalars().all())


async def get_dataset(db: AsyncSession, slug: str) -> Dataset | None:
    result = await db.execute(select(Dataset).where(Dataset.slug == slug))
    return result.scalar_one_or_none()


async def get_latest_version(db: AsyncSession, dataset_id: uuid.UUID) -> DatasetVersion | None:
    result = await db.execute(
        select(DatasetVersion)
        .where(DatasetVersion.dataset_id == dataset_id)
        .order_by(DatasetVersion.version_number.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def ingest_upload(
    db: AsyncSession,
    *,
    file_bytes: bytes,
    filename: str,
    name: str,
    description: str,
    uploaded_by: uuid.UUID,
) -> Dataset:
    """Synchronous ingest for files within the configured size limit — the
    caller (the API route) is responsible for enforcing the size limit
    before calling this, so this function can assume it's safe to run
    inline within the request."""

    file_format = detect_format(filename)

    storage_dir = Path(settings.dataset_storage_path)
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_key = f"{uuid.uuid4()}_{filename}"
    file_path = storage_dir / storage_key
    file_path.write_bytes(file_bytes)

    df = _READERS[file_format](file_path)
    profiling_result = profile_dataframe(df)

    slug_base = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")
    slug = f"{slug_base}-{uuid.uuid4().hex[:6]}"

    dataset = Dataset(
        name=name,
        slug=slug,
        description=description,
        source="User upload",
        source_url="internal://user-upload",
        license="Uploaded by user — license not independently verified. Do not redistribute.",
        domain=None,
        difficulty=DifficultyLevel.BEGINNER,
        format=file_format,
    )
    db.add(dataset)
    await db.flush()

    version = DatasetVersion(
        dataset_id=dataset.id,
        version_number=1,
        storage_key=storage_key,
        row_count=profiling_result["row_count"],
        column_count=profiling_result["column_count"],
        file_size_bytes=len(file_bytes),
        profiling_status=ProfilingStatus.COMPLETE,
        profiling_result=profiling_result,
        uploaded_by=uploaded_by,
    )
    db.add(version)
    await db.commit()
    await db.refresh(dataset)
    return dataset

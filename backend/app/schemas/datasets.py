import uuid

from pydantic import BaseModel, ConfigDict


class DatasetSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    source: str
    license: str
    difficulty: str
    format: str


class DatasetVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    version_number: int
    row_count: int | None
    column_count: int | None
    file_size_bytes: int | None
    profiling_status: str
    profiling_result: dict | None


class DatasetDetail(DatasetSummary):
    latest_version: DatasetVersionRead | None = None

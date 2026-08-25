import enum
import uuid

from sqlalchemy import BigInteger, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, DifficultyLevel, TimestampMixin, UUIDPkMixin


class DatasetFormat(str, enum.Enum):
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    PARQUET = "parquet"


class ProfilingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class Dataset(Base, UUIDPkMixin, TimestampMixin):
    """source_url and license are required, not optional, at the model
    level — enforced again at the admin-upload API layer in a later phase —
    per Phase 1 §9/§27: never fabricate dataset ownership or licensing."""

    __tablename__ = "datasets"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    license: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str | None] = mapped_column(String(80), nullable=True)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, name="difficulty_level", native_enum=True), nullable=False
    )
    format: Mapped[DatasetFormat] = mapped_column(
        Enum(DatasetFormat, name="dataset_format", native_enum=True), nullable=False
    )

    versions: Mapped[list["DatasetVersion"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")


class DatasetVersion(Base, UUIDPkMixin):
    __tablename__ = "dataset_versions"
    __table_args__ = (UniqueConstraint("dataset_id", "version_number", name="uq_dataset_version"),)

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    column_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    profiling_status: Mapped[ProfilingStatus] = mapped_column(
        Enum(ProfilingStatus, name="profiling_status", native_enum=True),
        nullable=False,
        default=ProfilingStatus.PENDING,
    )
    # dtypes, missingness, summary stats, correlations, outlier flags — the
    # async EDA profiling job output from Phase 1 §9/§25.
    profiling_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    dataset: Mapped["Dataset"] = relationship(back_populates="versions")

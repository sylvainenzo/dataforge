import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPkMixin


class TaskType(str, enum.Enum):
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    DIMENSIONALITY_REDUCTION = "dimensionality_reduction"
    TIME_SERIES = "time_series"
    ANOMALY_DETECTION = "anomaly_detection"


class ModelRunStatus(str, enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Experiment(Base, UUIDPkMixin, TimestampMixin):
    """A learner's ML Lab session (Phase 1 §24): dataset + target + algorithm
    comparisons live as child ModelRun rows."""

    __tablename__ = "experiments"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True, index=True
    )
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    task_type: Mapped[TaskType] = mapped_column(Enum(TaskType, name="task_type", native_enum=True), nullable=False)

    runs: Mapped[list["ModelRun"]] = relationship(back_populates="experiment", cascade="all, delete-orphan")


class ModelRun(Base, UUIDPkMixin):
    __tablename__ = "model_runs"

    experiment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    algorithm: Mapped[str] = mapped_column(String(80), nullable=False)
    hyperparameters: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # accuracy/precision/recall/f1/roc_auc for classification, mae/rmse/r2
    # for regression, etc. — shape depends on task_type (Phase 1 §19).
    metrics: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    feature_importance: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[ModelRunStatus] = mapped_column(
        Enum(ModelRunStatus, name="model_run_status", native_enum=True), nullable=False, default=ModelRunStatus.RUNNING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    experiment: Mapped["Experiment"] = relationship(back_populates="runs")

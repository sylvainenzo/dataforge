# Import every model module so Base.metadata is fully populated before
# Alembic autogenerate (or Base.metadata.create_all) runs.
from app.models import (  # noqa: F401,E402
    ai,
    assessment,
    career,
    curriculum,
    datasets,
    experiments,
    gamification,
    identity,
    knowledge_base,
    learning_science,
    platform,
    projects,
)
from app.models.base import Base  # noqa: F401

__all__ = ["Base"]

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning_science import Flashcard, SpacedRepetitionLog
from app.services.spaced_repetition import ReviewState, sm2

DEFAULT_EASE_FACTOR = 2.5


async def get_due_flashcards(db: AsyncSession, user_id: uuid.UUID, limit: int = 20) -> list[Flashcard]:
    """Due = never reviewed, or due_at has passed. A learner's first-ever
    session sees everything, since nothing has a log row yet."""

    now = datetime.now(UTC)
    result = await db.execute(
        select(Flashcard)
        .outerjoin(
            SpacedRepetitionLog,
            (SpacedRepetitionLog.flashcard_id == Flashcard.id) & (SpacedRepetitionLog.user_id == user_id),
        )
        .where(or_(SpacedRepetitionLog.id.is_(None), SpacedRepetitionLog.due_at <= now))
        .limit(limit)
    )
    return list(result.scalars().all())


async def submit_review(
    db: AsyncSession, *, user_id: uuid.UUID, flashcard_id: uuid.UUID, grade: int
) -> SpacedRepetitionLog:
    result = await db.execute(
        select(SpacedRepetitionLog).where(
            SpacedRepetitionLog.user_id == user_id, SpacedRepetitionLog.flashcard_id == flashcard_id
        )
    )
    log = result.scalar_one_or_none()

    current_state = (
        ReviewState(repetitions=log.repetitions, ease_factor=float(log.ease_factor), interval_days=log.interval_days)
        if log is not None
        else ReviewState(repetitions=0, ease_factor=DEFAULT_EASE_FACTOR, interval_days=0)
    )
    new_state = sm2(grade, current_state)

    now = datetime.now(UTC)
    due_at = now + timedelta(days=new_state.interval_days)

    if log is None:
        log = SpacedRepetitionLog(
            user_id=user_id,
            flashcard_id=flashcard_id,
            ease_factor=new_state.ease_factor,
            interval_days=new_state.interval_days,
            repetitions=new_state.repetitions,
            due_at=due_at,
            last_reviewed_at=now,
            last_grade=grade,
        )
        db.add(log)
    else:
        log.ease_factor = new_state.ease_factor
        log.interval_days = new_state.interval_days
        log.repetitions = new_state.repetitions
        log.due_at = due_at
        log.last_reviewed_at = now
        log.last_grade = grade

    await db.commit()
    await db.refresh(log)
    return log

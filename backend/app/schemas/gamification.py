import uuid

from pydantic import BaseModel, ConfigDict


class AchievementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    key: str
    name: str
    description: str
    xp_reward: int
    icon: str | None


class ProgressSummary(BaseModel):
    xp: int
    streak_days: int
    badges: list[AchievementRead]
    newly_awarded: list[str]


class FlashcardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    front: str
    back: str


class FlashcardReviewRequest(BaseModel):
    grade: int  # 0-5, SM-2 scale


class FlashcardReviewResult(BaseModel):
    interval_days: int
    due_at: str
    repetitions: int

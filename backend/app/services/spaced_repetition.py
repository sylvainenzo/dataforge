"""SM-2 (SuperMemo-2) spaced repetition — Phase 1 §38. Textbook
implementation, grade 0-5 (0 = total blackout, 5 = perfect recall)."""

from dataclasses import dataclass


@dataclass
class ReviewState:
    repetitions: int
    ease_factor: float
    interval_days: int


def sm2(grade: int, state: ReviewState) -> ReviewState:
    if not 0 <= grade <= 5:
        raise ValueError("grade must be between 0 and 5")

    if grade >= 3:
        if state.repetitions == 0:
            interval = 1
        elif state.repetitions == 1:
            interval = 6
        else:
            interval = round(state.interval_days * state.ease_factor)
        repetitions = state.repetitions + 1
    else:
        repetitions = 0
        interval = 1

    ease_factor = state.ease_factor + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    ease_factor = max(1.3, ease_factor)

    return ReviewState(repetitions=repetitions, ease_factor=round(ease_factor, 4), interval_days=interval)

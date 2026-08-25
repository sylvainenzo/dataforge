import pytest

from app.services.spaced_repetition import ReviewState, sm2


def test_first_correct_review_sets_interval_to_one_day():
    state = ReviewState(repetitions=0, ease_factor=2.5, interval_days=0)
    result = sm2(5, state)
    assert result.interval_days == 1
    assert result.repetitions == 1


def test_second_correct_review_sets_interval_to_six_days():
    state = sm2(5, ReviewState(repetitions=0, ease_factor=2.5, interval_days=0))
    result = sm2(5, state)
    assert result.interval_days == 6
    assert result.repetitions == 2


def test_failing_grade_resets_repetitions_and_interval():
    state = ReviewState(repetitions=3, ease_factor=2.7, interval_days=16)
    result = sm2(1, state)
    assert result.repetitions == 0
    assert result.interval_days == 1


def test_ease_factor_never_drops_below_1_3():
    state = ReviewState(repetitions=0, ease_factor=1.3, interval_days=1)
    result = sm2(0, state)
    assert result.ease_factor >= 1.3


def test_perfect_recall_increases_ease_factor():
    state = ReviewState(repetitions=1, ease_factor=2.5, interval_days=6)
    result = sm2(5, state)
    assert result.ease_factor > 2.5


def test_invalid_grade_raises():
    with pytest.raises(ValueError):
        sm2(6, ReviewState(repetitions=0, ease_factor=2.5, interval_days=0))

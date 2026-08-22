import pytest

from trustlens.uncertainty import classification_intervals, wilson_interval


def test_wilson_interval_contains_observed_proportion() -> None:
    interval = wilson_interval(50, 60)

    assert interval.estimate == pytest.approx(5 / 6)
    assert interval.lower < interval.estimate < interval.upper
    assert 0 <= interval.lower <= interval.upper <= 1


def test_classification_intervals_match_locked_confusion_matrix() -> None:
    intervals = classification_intervals(
        true_negatives=67,
        false_positives=73,
        false_negatives=10,
        true_positives=50,
    )

    assert intervals["recall"].estimate == pytest.approx(50 / 60)
    assert intervals["precision"].estimate == pytest.approx(50 / 123)
    assert intervals["specificity"].estimate == pytest.approx(67 / 140)


@pytest.mark.parametrize("successes,trials", [(-1, 10), (11, 10), (0, 0)])
def test_wilson_interval_rejects_invalid_counts(successes: int, trials: int) -> None:
    with pytest.raises(ValueError):
        wilson_interval(successes, trials)

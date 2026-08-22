import numpy as np
import pandas as pd
import pytest

from trustlens.error_analysis import find_error_slices


def test_error_slices_rank_supported_groups() -> None:
    features = pd.DataFrame({"group": ["a"] * 8 + ["b"] * 8, "amount": list(range(16))})
    actual = np.array([1, 1, 1, 1, 0, 0, 0, 0] * 2)
    predicted = np.array([0, 0, 0, 1, 1, 1, 0, 0] + [1, 1, 1, 1, 0, 0, 0, 0])

    result = find_error_slices(
        features,
        actual,
        predicted,
        numeric_features=("amount",),
        minimum_class_support=2,
        limit=3,
    )

    assert result["highest_false_negative_rate"][0].feature == "group"
    assert result["highest_false_negative_rate"][0].group == "a"
    assert result["highest_false_negative_rate"][0].error_rate == pytest.approx(0.75)
    assert result["highest_false_positive_rate"][0].group == "a"


def test_error_slices_reject_mismatched_lengths() -> None:
    with pytest.raises(ValueError):
        find_error_slices(pd.DataFrame({"x": [1]}), np.array([0, 1]), np.array([0]))

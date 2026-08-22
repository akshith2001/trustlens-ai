import numpy as np

from trustlens.explainability import summarise_importances


def test_importances_are_ranked_by_mean_performance_drop() -> None:
    samples = np.array([[0.01, 0.02], [0.10, 0.08]])

    results = summarise_importances(["weak", "strong"], samples)

    assert [result.feature for result in results] == ["strong", "weak"]

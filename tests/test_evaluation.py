import numpy as np

from trustlens.evaluation import evaluate_predictions


def test_evaluation_counts_errors_and_weighted_cost() -> None:
    actual = np.array([0, 0, 1, 1])
    predicted = np.array([0, 1, 0, 1])

    metrics = evaluate_predictions(actual, predicted)

    assert metrics.true_negatives == 1
    assert metrics.false_positives == 1
    assert metrics.false_negatives == 1
    assert metrics.true_positives == 1
    assert metrics.weighted_error_cost == 6
    assert metrics.accuracy == 0.5

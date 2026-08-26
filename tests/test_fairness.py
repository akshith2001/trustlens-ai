import numpy as np
import pandas as pd

from trustlens.fairness import subgroup_metrics, wilson_interval


def test_subgroup_metrics_report_recall_and_false_positive_rate() -> None:
    actual = np.array([0, 1, 0, 1])
    predicted = np.array([1, 1, 0, 0])
    groups = pd.Series(["a", "a", "b", "b"])

    results = {
        result.group: result for result in subgroup_metrics(actual, predicted, groups)
    }

    assert results["a"].recall == 1.0
    assert results["a"].false_positive_rate == 1.0
    assert results["b"].recall == 0.0
    assert results["b"].false_positive_rate == 0.0


def test_wilson_interval_is_wider_for_smaller_samples() -> None:
    small = wilson_interval(5, 10)
    large = wilson_interval(50, 100)

    assert small is not None and large is not None
    assert (small[1] - small[0]) > (large[1] - large[0])

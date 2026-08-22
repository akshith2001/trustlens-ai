import numpy as np

from trustlens.review_policy import select_review_cases


def test_review_policy_selects_probabilities_closest_to_threshold() -> None:
    probabilities = np.array([0.05, 0.19, 0.21, 0.80])

    selected = select_review_cases(probabilities, threshold=0.20, review_budget=0.5)

    assert selected.tolist() == [False, True, True, False]

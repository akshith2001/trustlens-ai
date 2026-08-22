"""Human-review policies for borderline calibrated predictions."""

from dataclasses import dataclass

import numpy as np

from trustlens.calibration import (
    out_of_fold_probabilities,
    select_cost_sensitive_threshold,
)
from trustlens.data import CreditDataset
from trustlens.evaluation import evaluate_predictions
from trustlens.features import GOVERNED_EXCLUDED_FEATURES


@dataclass(frozen=True)
class ReviewPolicyResult:
    review_budget: float
    automated_coverage: float
    records_reviewed: int
    error_capture_rate: float
    remaining_weighted_error_cost: int
    potential_cost_reduction: float


def select_review_cases(
    probabilities: np.ndarray,
    threshold: float,
    review_budget: float,
) -> np.ndarray:
    """Select the requested share closest to the decision threshold."""

    if not 0.0 <= review_budget < 1.0:
        raise ValueError("review_budget must be at least 0 and below 1")
    count = int(round(len(probabilities) * review_budget))
    selected = np.zeros(len(probabilities), dtype=bool)
    if count:
        closest = np.argsort(np.abs(probabilities - threshold))[:count]
        selected[closest] = True
    return selected


def analyse_review_budgets(
    dataset: CreditDataset,
    budgets: tuple[float, ...] = (0.0, 0.1, 0.2, 0.3),
) -> list[ReviewPolicyResult]:
    """Measure potential impact if reviewed errors are corrected by humans."""

    actual, _, probabilities = out_of_fold_probabilities(
        dataset,
        excluded_features=GOVERNED_EXCLUDED_FEATURES,
    )
    threshold, _ = select_cost_sensitive_threshold(actual, probabilities)
    predictions = (probabilities >= threshold).astype(int)
    original = evaluate_predictions(actual, predictions)
    original_errors = predictions != actual
    total_errors = int(original_errors.sum())

    results = []
    for budget in budgets:
        reviewed = select_review_cases(probabilities, threshold, budget)
        retained = ~reviewed
        remaining = evaluate_predictions(actual[retained], predictions[retained])
        captured_errors = int((reviewed & original_errors).sum())
        potential_reduction = (
            (original.weighted_error_cost - remaining.weighted_error_cost)
            / original.weighted_error_cost
        )
        results.append(
            ReviewPolicyResult(
                review_budget=budget,
                automated_coverage=float(retained.mean()),
                records_reviewed=int(reviewed.sum()),
                error_capture_rate=(
                    captured_errors / total_errors if total_errors else 0.0
                ),
                remaining_weighted_error_cost=remaining.weighted_error_cost,
                potential_cost_reduction=float(potential_reduction),
            )
        )
    return results

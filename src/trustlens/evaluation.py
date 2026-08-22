"""Evaluation measures used consistently across TrustLens models."""

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


FALSE_NEGATIVE_COST = 5
FALSE_POSITIVE_COST = 1


@dataclass(frozen=True)
class ClassificationMetrics:
    accuracy: float
    balanced_accuracy: float
    precision: float
    recall: float
    f1: float
    true_negatives: int
    false_positives: int
    false_negatives: int
    true_positives: int
    weighted_error_cost: int


def evaluate_predictions(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> ClassificationMetrics:
    """Evaluate binary predictions with higher risk as the positive class."""

    tn, fp, fn, tp = confusion_matrix(actual, predicted, labels=[0, 1]).ravel()
    weighted_cost = (fn * FALSE_NEGATIVE_COST) + (fp * FALSE_POSITIVE_COST)

    return ClassificationMetrics(
        accuracy=float(accuracy_score(actual, predicted)),
        balanced_accuracy=float(balanced_accuracy_score(actual, predicted)),
        precision=float(precision_score(actual, predicted, zero_division=0)),
        recall=float(recall_score(actual, predicted, zero_division=0)),
        f1=float(f1_score(actual, predicted, zero_division=0)),
        true_negatives=int(tn),
        false_positives=int(fp),
        false_negatives=int(fn),
        true_positives=int(tp),
        weighted_error_cost=int(weighted_cost),
    )


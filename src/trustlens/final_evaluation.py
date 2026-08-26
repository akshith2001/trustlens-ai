"""One-time evaluation of the locked governed model on the held-out test set."""

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.model_selection import train_test_split

from trustlens.baseline import RANDOM_STATE, TEST_SIZE
from trustlens.calibration import expected_calibration_error
from trustlens.data import CreditDataset
from trustlens.evaluation import evaluate_predictions
from trustlens.experiments import build_random_forest
from trustlens.features import GOVERNED_EXCLUDED_FEATURES
from trustlens.governance import (
    GOVERNED_DECISION_THRESHOLD,
    GOVERNED_MODEL_NAME,
)


@dataclass(frozen=True)
class FinalTestResult:
    model_name: str
    test_records: int
    decision_threshold: float
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
    brier_score: float
    log_loss: float
    expected_calibration_error: float

    def to_dict(self) -> dict[str, str | int | float]:
        return asdict(self)


def evaluate_locked_model(dataset: CreditDataset) -> FinalTestResult:
    """Fit on development data and evaluate the untouched test partition."""

    _, test_target, probabilities, predictions = generate_locked_predictions(dataset)
    metrics = evaluate_predictions(test_target.to_numpy(), predictions)

    return FinalTestResult(
        model_name=GOVERNED_MODEL_NAME,
        test_records=len(test_target),
        decision_threshold=GOVERNED_DECISION_THRESHOLD,
        accuracy=metrics.accuracy,
        balanced_accuracy=metrics.balanced_accuracy,
        precision=metrics.precision,
        recall=metrics.recall,
        f1=metrics.f1,
        true_negatives=metrics.true_negatives,
        false_positives=metrics.false_positives,
        false_negatives=metrics.false_negatives,
        true_positives=metrics.true_positives,
        weighted_error_cost=metrics.weighted_error_cost,
        brier_score=float(brier_score_loss(test_target, probabilities)),
        log_loss=float(log_loss(test_target, probabilities)),
        expected_calibration_error=expected_calibration_error(
            test_target.to_numpy(), probabilities
        ),
    )


def generate_locked_predictions(
    dataset: CreditDataset,
) -> tuple[pd.DataFrame, pd.Series, np.ndarray, np.ndarray]:
    """Reproduce locked predictions for diagnostics without model tuning."""

    train_features, test_features, train_target, test_target = train_test_split(
        dataset.features,
        dataset.target,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=dataset.target,
    )
    model = CalibratedClassifierCV(
        estimator=build_random_forest(excluded_features=GOVERNED_EXCLUDED_FEATURES),
        method="sigmoid",
        cv=3,
    )
    model.fit(train_features, train_target)
    probabilities = model.predict_proba(test_features)[:, 1]
    predictions = (probabilities >= GOVERNED_DECISION_THRESHOLD).astype(int)
    return test_features, test_target, probabilities, predictions

"""Probability calibration and validation-only threshold selection."""

from dataclasses import dataclass

import numpy as np
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.model_selection import StratifiedKFold, train_test_split

from trustlens.baseline import RANDOM_STATE, TEST_SIZE
from trustlens.data import CreditDataset
from trustlens.evaluation import ClassificationMetrics, evaluate_predictions
from trustlens.experiments import build_random_forest
from trustlens.features import GOVERNED_EXCLUDED_FEATURES


@dataclass(frozen=True)
class CalibrationSummary:
    raw_brier_score: float
    calibrated_brier_score: float
    raw_log_loss: float
    calibrated_log_loss: float
    raw_expected_calibration_error: float
    calibrated_expected_calibration_error: float
    selected_threshold: float
    threshold_balanced_accuracy: float
    threshold_precision: float
    threshold_recall: float
    threshold_f1: float
    threshold_weighted_error_cost: int


def expected_calibration_error(
    actual: np.ndarray,
    probabilities: np.ndarray,
    bins: int = 10,
) -> float:
    """Calculate weighted absolute confidence error over equal-width bins."""

    boundaries = np.linspace(0.0, 1.0, bins + 1)
    total = len(actual)
    error = 0.0
    for index in range(bins):
        lower = boundaries[index]
        upper = boundaries[index + 1]
        if index == bins - 1:
            in_bin = (probabilities >= lower) & (probabilities <= upper)
        else:
            in_bin = (probabilities >= lower) & (probabilities < upper)
        count = int(in_bin.sum())
        if count == 0:
            continue
        observed_rate = float(actual[in_bin].mean())
        mean_confidence = float(probabilities[in_bin].mean())
        error += (count / total) * abs(observed_rate - mean_confidence)
    return error


def development_data(dataset: CreditDataset):
    features_development, _, target_development, _ = train_test_split(
        dataset.features,
        dataset.target,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=dataset.target,
    )
    return features_development, target_development


def out_of_fold_probabilities(
    dataset: CreditDataset,
    folds: int = 5,
    excluded_features: frozenset[str] = frozenset(),
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    features, target = development_data(dataset)
    splitter = StratifiedKFold(
        n_splits=folds,
        shuffle=True,
        random_state=RANDOM_STATE,
    )
    actual = target.to_numpy()
    raw_probabilities = np.empty(len(target), dtype=float)
    calibrated_probabilities = np.empty(len(target), dtype=float)

    for train_indices, validation_indices in splitter.split(features, target):
        train_features = features.iloc[train_indices]
        validation_features = features.iloc[validation_indices]
        train_target = target.iloc[train_indices]

        raw_model = build_random_forest(excluded_features=excluded_features)
        raw_model.fit(train_features, train_target)

        calibrated_model = CalibratedClassifierCV(
            estimator=clone(build_random_forest(excluded_features=excluded_features)),
            method="sigmoid",
            cv=3,
        )
        calibrated_model.fit(train_features, train_target)

        raw_probabilities[validation_indices] = raw_model.predict_proba(
            validation_features
        )[:, 1]
        calibrated_probabilities[validation_indices] = calibrated_model.predict_proba(
            validation_features
        )[:, 1]

    return actual, raw_probabilities, calibrated_probabilities


def select_cost_sensitive_threshold(
    actual: np.ndarray,
    probabilities: np.ndarray,
) -> tuple[float, ClassificationMetrics]:
    """Select the lowest-cost validation threshold with a stable tie-break."""

    candidates = []
    for threshold in np.arange(0.05, 0.951, 0.01):
        predicted = (probabilities >= threshold).astype(int)
        metrics = evaluate_predictions(actual, predicted)
        candidates.append(
            (
                metrics.weighted_error_cost,
                -metrics.balanced_accuracy,
                threshold,
                metrics,
            )
        )
    _, _, selected_threshold, selected_metrics = min(
        candidates, key=lambda item: item[:3]
    )
    return float(selected_threshold), selected_metrics


def analyse_random_forest_calibration(
    dataset: CreditDataset,
) -> CalibrationSummary:
    """Compare probabilities and select a cost-sensitive review threshold."""

    actual, raw_probabilities, calibrated_probabilities = out_of_fold_probabilities(
        dataset,
        excluded_features=GOVERNED_EXCLUDED_FEATURES,
    )

    selected_threshold, selected_metrics = select_cost_sensitive_threshold(
        actual, calibrated_probabilities
    )

    return CalibrationSummary(
        raw_brier_score=float(brier_score_loss(actual, raw_probabilities)),
        calibrated_brier_score=float(
            brier_score_loss(actual, calibrated_probabilities)
        ),
        raw_log_loss=float(log_loss(actual, raw_probabilities)),
        calibrated_log_loss=float(log_loss(actual, calibrated_probabilities)),
        raw_expected_calibration_error=expected_calibration_error(
            actual, raw_probabilities
        ),
        calibrated_expected_calibration_error=expected_calibration_error(
            actual, calibrated_probabilities
        ),
        selected_threshold=float(selected_threshold),
        threshold_balanced_accuracy=selected_metrics.balanced_accuracy,
        threshold_precision=selected_metrics.precision,
        threshold_recall=selected_metrics.recall,
        threshold_f1=selected_metrics.f1,
        threshold_weighted_error_cost=selected_metrics.weighted_error_cost,
    )

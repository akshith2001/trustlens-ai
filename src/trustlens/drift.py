"""Dataset-level covariate drift detection through adversarial validation."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline

from trustlens.baseline import RANDOM_STATE
from trustlens.features import build_preprocessor


DEFAULT_DRIFT_AUC_THRESHOLD = 0.70


@dataclass(frozen=True)
class DriftResult:
    adversarial_auc_mean: float
    adversarial_auc_std: float
    threshold: float
    drift_detected: bool
    action: str


def drift_action(auc: float, threshold: float = DEFAULT_DRIFT_AUC_THRESHOLD) -> str:
    """Return the governance action associated with a drift score."""

    return "pause_and_investigate" if auc >= threshold else "continue_monitoring"


def detect_covariate_drift(
    reference: pd.DataFrame,
    incoming: pd.DataFrame,
    threshold: float = DEFAULT_DRIFT_AUC_THRESHOLD,
) -> DriftResult:
    """Test whether a classifier can distinguish reference from incoming data."""

    if list(reference.columns) != list(incoming.columns):
        raise ValueError("Reference and incoming data must have identical columns")
    combined = pd.concat([reference, incoming], ignore_index=True)
    source = np.concatenate(
        [np.zeros(len(reference), dtype=int), np.ones(len(incoming), dtype=int)]
    )
    detector = Pipeline(
        steps=[
            ("preprocess", build_preprocessor()),
            (
                "model",
                LogisticRegression(max_iter=2_000, random_state=RANDOM_STATE),
            ),
        ]
    )
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scores = cross_val_score(detector, combined, source, cv=folds, scoring="roc_auc")
    mean_auc = float(scores.mean())
    action = drift_action(mean_auc, threshold)
    return DriftResult(
        adversarial_auc_mean=mean_auc,
        adversarial_auc_std=float(scores.std()),
        threshold=threshold,
        drift_detected=action == "pause_and_investigate",
        action=action,
    )


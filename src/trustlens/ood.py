"""Individual out-of-distribution screening for governed predictions."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler

from trustlens.baseline import RANDOM_STATE
from trustlens.data import CreditDataset
from trustlens.features import NUMERIC_FEATURES


@dataclass(frozen=True)
class OODResult:
    normal_holdout_flag_rate: float
    synthetic_extreme_flag_rate: float
    training_contamination: float
    action_for_flagged_record: str


def ood_action(flagged: bool) -> str:
    return "pause_for_human_review" if flagged else "continue_with_audit"


def fit_ood_detector(
    reference: pd.DataFrame,
    contamination: float = 0.05,
):
    scaler = RobustScaler()
    transformed = scaler.fit_transform(reference[NUMERIC_FEATURES])
    detector = IsolationForest(
        n_estimators=300,
        contamination=contamination,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    detector.fit(transformed)
    return scaler, detector


def flag_ood_records(scaler, detector, records: pd.DataFrame) -> np.ndarray:
    """Return True where an individual record is outside learned support."""

    transformed = scaler.transform(records[NUMERIC_FEATURES])
    return detector.predict(transformed) == -1


def evaluate_ood_detector(
    dataset: CreditDataset,
    contamination: float = 0.05,
) -> OODResult:
    """Compare normal holdout flags with controlled synthetic extremes."""

    reference, normal_holdout = train_test_split(
        dataset.features,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=dataset.target,
    )
    scaler, detector = fit_ood_detector(reference, contamination)
    normal_flags = flag_ood_records(scaler, detector, normal_holdout)

    synthetic_extremes = normal_holdout.copy()
    synthetic_extremes["duration_months"] += 36
    synthetic_extremes["credit_amount"] *= 4
    synthetic_flags = flag_ood_records(
        scaler, detector, synthetic_extremes
    )

    return OODResult(
        normal_holdout_flag_rate=float(normal_flags.mean()),
        synthetic_extreme_flag_rate=float(synthetic_flags.mean()),
        training_contamination=contamination,
        action_for_flagged_record=ood_action(True),
    )

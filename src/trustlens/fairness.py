"""Transparent subgroup diagnostics with explicit assessability limits."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from trustlens.calibration import (
    development_data,
    out_of_fold_probabilities,
    select_cost_sensitive_threshold,
)
from trustlens.data import CreditDataset
from trustlens.features import GOVERNED_EXCLUDED_FEATURES


@dataclass(frozen=True)
class GroupMetrics:
    group: str
    records: int
    observed_higher_risk_rate: float
    warning_rate: float
    recall: float | None
    recall_interval: tuple[float, float] | None
    false_positive_rate: float | None
    false_positive_interval: tuple[float, float] | None


@dataclass(frozen=True)
class FairnessAudit:
    gender_status: str
    gender_reason: str
    age_results: list[GroupMetrics]
    foreign_worker_code_results: list[GroupMetrics]


def _safe_rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def wilson_interval(
    successes: int,
    total: int,
    z: float = 1.96,
) -> tuple[float, float] | None:
    """Return a 95% Wilson interval for a binary proportion."""

    if total == 0:
        return None
    proportion = successes / total
    denominator = 1 + (z**2 / total)
    centre = (proportion + (z**2 / (2 * total))) / denominator
    margin = (
        z
        * np.sqrt((proportion * (1 - proportion) / total) + (z**2 / (4 * total**2)))
        / denominator
    )
    return max(0.0, centre - margin), min(1.0, centre + margin)


def subgroup_metrics(
    actual: np.ndarray,
    predicted: np.ndarray,
    groups: pd.Series,
) -> list[GroupMetrics]:
    """Report performance by group without declaring fairness from one metric."""

    results = []
    group_values = groups.astype("string").fillna("missing").to_numpy()
    for group in sorted(np.unique(group_values)):
        selected = group_values == group
        group_actual = actual[selected]
        group_predicted = predicted[selected]
        positives = int((group_actual == 1).sum())
        negatives = int((group_actual == 0).sum())
        true_positives = int(((group_actual == 1) & (group_predicted == 1)).sum())
        false_positives = int(((group_actual == 0) & (group_predicted == 1)).sum())
        results.append(
            GroupMetrics(
                group=str(group),
                records=int(selected.sum()),
                observed_higher_risk_rate=float(group_actual.mean()),
                warning_rate=float(group_predicted.mean()),
                recall=_safe_rate(true_positives, positives),
                recall_interval=wilson_interval(true_positives, positives),
                false_positive_rate=_safe_rate(false_positives, negatives),
                false_positive_interval=wilson_interval(false_positives, negatives),
            )
        )
    return results


def audit_credit_subgroups(dataset: CreditDataset) -> FairnessAudit:
    """Run exploratory subgroup diagnostics on development predictions only."""

    development_features, _ = development_data(dataset)
    actual, _, probabilities = out_of_fold_probabilities(
        dataset,
        excluded_features=GOVERNED_EXCLUDED_FEATURES,
    )
    threshold, _ = select_cost_sensitive_threshold(actual, probabilities)
    predicted = (probabilities >= threshold).astype(int)

    age_groups = pd.cut(
        development_features["age_years"],
        bins=[-np.inf, 24, 59, np.inf],
        labels=["under_25", "25_to_59", "60_and_over"],
    )
    worker_codes = development_features["foreign_worker"].map(
        lambda value: f"recorded_code_{value}"
    )
    return FairnessAudit(
        gender_status="not_assessable",
        gender_reason=(
            "The source combines sex and marital status, and UCI states that "
            "sex cannot be reliably recovered for every code."
        ),
        age_results=subgroup_metrics(actual, predicted, age_groups),
        foreign_worker_code_results=subgroup_metrics(actual, predicted, worker_codes),
    )

"""Post-hoc slice diagnostics for a locked binary classifier."""

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ErrorSlice:
    feature: str
    group: str
    class_support: int
    errors: int
    error_rate: float

    def to_dict(self) -> dict[str, str | int | float]:
        return asdict(self)


def find_error_slices(
    features: pd.DataFrame,
    actual: np.ndarray,
    predicted: np.ndarray,
    *,
    numeric_features: tuple[str, ...] = (),
    excluded_features: frozenset[str] = frozenset(),
    minimum_class_support: int = 10,
    limit: int = 10,
) -> dict[str, list[ErrorSlice]]:
    """Rank supported slices by false-negative and false-positive rate."""

    if len(features) != len(actual) or len(actual) != len(predicted):
        raise ValueError("features, actual and predicted must have equal length")
    if minimum_class_support <= 0 or limit <= 0:
        raise ValueError("minimum_class_support and limit must be positive")

    actual_array = np.asarray(actual)
    predicted_array = np.asarray(predicted)
    false_negative_slices: list[ErrorSlice] = []
    false_positive_slices: list[ErrorSlice] = []

    for feature in features.columns:
        if feature in excluded_features:
            continue
        groups = _groups_for_feature(
            features[feature], numeric=feature in numeric_features
        )
        for group_name in groups.dropna().unique():
            mask = (groups == group_name).to_numpy()
            positive_mask = mask & (actual_array == 1)
            negative_mask = mask & (actual_array == 0)
            positive_support = int(positive_mask.sum())
            negative_support = int(negative_mask.sum())

            if positive_support >= minimum_class_support:
                errors = int((positive_mask & (predicted_array == 0)).sum())
                false_negative_slices.append(
                    ErrorSlice(
                        feature,
                        str(group_name),
                        positive_support,
                        errors,
                        errors / positive_support,
                    )
                )
            if negative_support >= minimum_class_support:
                errors = int((negative_mask & (predicted_array == 1)).sum())
                false_positive_slices.append(
                    ErrorSlice(
                        feature,
                        str(group_name),
                        negative_support,
                        errors,
                        errors / negative_support,
                    )
                )

    def ranking(item: ErrorSlice) -> tuple[float, int, int]:
        return item.error_rate, item.class_support, item.errors

    return {
        "highest_false_negative_rate": sorted(
            false_negative_slices, key=ranking, reverse=True
        )[:limit],
        "highest_false_positive_rate": sorted(
            false_positive_slices, key=ranking, reverse=True
        )[:limit],
    }


def _groups_for_feature(series: pd.Series, *, numeric: bool) -> pd.Series:
    if numeric:
        try:
            return pd.qcut(series, q=4, duplicates="drop").astype(str)
        except ValueError:
            return series.astype(str)
    return series.astype(str)

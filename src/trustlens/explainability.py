"""Validation-based global explainability for TrustLens models."""

from dataclasses import dataclass

import numpy as np
from sklearn.inspection import permutation_importance
from sklearn.model_selection import StratifiedKFold

from trustlens.baseline import RANDOM_STATE
from trustlens.calibration import development_data
from trustlens.data import CreditDataset
from trustlens.experiments import build_random_forest


@dataclass(frozen=True)
class FeatureImportance:
    feature: str
    balanced_accuracy_drop_mean: float
    balanced_accuracy_drop_std: float


def summarise_importances(
    feature_names: list[str],
    importance_samples: np.ndarray,
) -> list[FeatureImportance]:
    """Summarise and rank repeated importance measurements."""

    results = [
        FeatureImportance(
            feature=name,
            balanced_accuracy_drop_mean=float(importance_samples[index].mean()),
            balanced_accuracy_drop_std=float(importance_samples[index].std()),
        )
        for index, name in enumerate(feature_names)
    ]
    return sorted(
        results,
        key=lambda result: result.balanced_accuracy_drop_mean,
        reverse=True,
    )


def cross_validated_permutation_importance(
    dataset: CreditDataset,
    folds: int = 5,
    repeats: int = 10,
) -> list[FeatureImportance]:
    """Estimate importance from performance loss on unseen validation rows."""

    features, target = development_data(dataset)
    splitter = StratifiedKFold(
        n_splits=folds,
        shuffle=True,
        random_state=RANDOM_STATE,
    )
    fold_samples = []
    for fold, (train_indices, validation_indices) in enumerate(
        splitter.split(features, target)
    ):
        model = build_random_forest()
        model.fit(features.iloc[train_indices], target.iloc[train_indices])
        importance = permutation_importance(
            model,
            features.iloc[validation_indices],
            target.iloc[validation_indices],
            scoring="balanced_accuracy",
            n_repeats=repeats,
            random_state=RANDOM_STATE + fold,
            n_jobs=-1,
        )
        fold_samples.append(importance.importances)

    samples = np.concatenate(fold_samples, axis=1)
    return summarise_importances(list(features.columns), samples)


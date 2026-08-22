"""Cross-validated model experiments that leave the final test set untouched."""

from dataclasses import dataclass

import numpy as np
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline

from trustlens.baseline import RANDOM_STATE, TEST_SIZE
from trustlens.data import CreditDataset
from trustlens.evaluation import evaluate_predictions
from trustlens.features import build_preprocessor


@dataclass(frozen=True)
class CrossValidationSummary:
    model_name: str
    folds: int
    balanced_accuracy_mean: float
    balanced_accuracy_std: float
    precision_mean: float
    precision_std: float
    recall_mean: float
    recall_std: float
    f1_mean: float
    f1_std: float
    weighted_error_cost_mean: float
    weighted_error_cost_std: float


def build_logistic_regression(cost_sensitive: bool = False) -> Pipeline:
    """Build an interpretable probability-producing classification pipeline."""

    return Pipeline(
        steps=[
            ("preprocess", build_preprocessor()),
            (
                "model",
                LogisticRegression(
                    max_iter=2_000,
                    random_state=RANDOM_STATE,
                    class_weight={0: 1, 1: 5} if cost_sensitive else None,
                ),
            ),
        ]
    )


def build_random_forest(
    excluded_features: frozenset[str] = frozenset(),
) -> Pipeline:
    """Build a cost-sensitive non-linear ensemble model."""

    return Pipeline(
        steps=[
            ("preprocess", build_preprocessor(excluded_features)),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=400,
                    min_samples_leaf=5,
                    class_weight={0: 1, 1: 5},
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def build_hist_gradient_boosting() -> Pipeline:
    """Build a regularised cost-sensitive boosting model."""

    return Pipeline(
        steps=[
            ("preprocess", build_preprocessor()),
            (
                "model",
                HistGradientBoostingClassifier(
                    learning_rate=0.05,
                    max_iter=200,
                    max_leaf_nodes=15,
                    min_samples_leaf=20,
                    l2_regularization=1.0,
                    class_weight={0: 1, 1: 5},
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def cross_validate_logistic_regression(
    dataset: CreditDataset,
    folds: int = 5,
    cost_sensitive: bool = False,
) -> CrossValidationSummary:
    """Evaluate logistic regression inside the development partition only."""

    model_name = (
        "cost_sensitive_logistic_regression"
        if cost_sensitive
        else "logistic_regression"
    )
    return _cross_validate_model(
        dataset=dataset,
        model_name=model_name,
        template=build_logistic_regression(cost_sensitive=cost_sensitive),
        folds=folds,
    )


def cross_validate_random_forest(
    dataset: CreditDataset,
    folds: int = 5,
) -> CrossValidationSummary:
    return _cross_validate_model(
        dataset=dataset,
        model_name="cost_sensitive_random_forest",
        template=build_random_forest(),
        folds=folds,
    )


def cross_validate_restricted_random_forest(
    dataset: CreditDataset,
    folds: int = 5,
) -> CrossValidationSummary:
    excluded = frozenset({"age_years", "personal_status_sex", "foreign_worker"})
    return cross_validate_random_forest_excluding(
        dataset=dataset,
        excluded_features=excluded,
        model_name="restricted_cost_sensitive_random_forest",
        folds=folds,
    )


def cross_validate_random_forest_excluding(
    dataset: CreditDataset,
    excluded_features: frozenset[str],
    model_name: str,
    folds: int = 5,
) -> CrossValidationSummary:
    return _cross_validate_model(
        dataset=dataset,
        model_name=model_name,
        template=build_random_forest(excluded_features=excluded_features),
        folds=folds,
    )


def cross_validate_hist_gradient_boosting(
    dataset: CreditDataset,
    folds: int = 5,
) -> CrossValidationSummary:
    return _cross_validate_model(
        dataset=dataset,
        model_name="cost_sensitive_hist_gradient_boosting",
        template=build_hist_gradient_boosting(),
        folds=folds,
    )


def _cross_validate_model(
    dataset: CreditDataset,
    model_name: str,
    template: Pipeline,
    folds: int,
) -> CrossValidationSummary:
    """Evaluate one candidate on fixed stratified development folds."""

    features_development, _, target_development, _ = train_test_split(
        dataset.features,
        dataset.target,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=dataset.target,
    )
    splitter = StratifiedKFold(
        n_splits=folds,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    balanced_accuracies: list[float] = []
    precisions: list[float] = []
    recalls: list[float] = []
    f1_scores: list[float] = []
    weighted_costs: list[float] = []

    for train_indices, validation_indices in splitter.split(
        features_development, target_development
    ):
        model = clone(template)
        train_features = features_development.iloc[train_indices]
        validation_features = features_development.iloc[validation_indices]
        train_target = target_development.iloc[train_indices]
        validation_target = target_development.iloc[validation_indices]

        model.fit(train_features, train_target)
        predictions = model.predict(validation_features)
        metrics = evaluate_predictions(validation_target.to_numpy(), predictions)
        balanced_accuracies.append(metrics.balanced_accuracy)
        precisions.append(metrics.precision)
        recalls.append(metrics.recall)
        f1_scores.append(metrics.f1)
        weighted_costs.append(metrics.weighted_error_cost)

    return CrossValidationSummary(
        model_name=model_name,
        folds=folds,
        balanced_accuracy_mean=float(np.mean(balanced_accuracies)),
        balanced_accuracy_std=float(np.std(balanced_accuracies)),
        precision_mean=float(np.mean(precisions)),
        precision_std=float(np.std(precisions)),
        recall_mean=float(np.mean(recalls)),
        recall_std=float(np.std(recalls)),
        f1_mean=float(np.mean(f1_scores)),
        f1_std=float(np.std(f1_scores)),
        weighted_error_cost_mean=float(np.mean(weighted_costs)),
        weighted_error_cost_std=float(np.std(weighted_costs)),
    )

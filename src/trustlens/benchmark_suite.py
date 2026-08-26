"""Controlled multi-dataset benchmark extensions for TrustLens."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from sklearn.base import clone
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from trustlens.baseline import RANDOM_STATE
from trustlens.evaluation import FALSE_NEGATIVE_COST, FALSE_POSITIVE_COST

SUITE_SCHEMA_VERSION = "1.0"
DEFAULT_SUITE_PATH = Path("results/controlled_benchmark_suite.json")
DEFAULT_REPORT_PATH = Path("reports/Controlled_Benchmark_Report.md")


@dataclass(frozen=True)
class Interval:
    estimate: float
    lower: float
    upper: float
    confidence_level: float = 0.95


@dataclass(frozen=True)
class ModelSuiteResult:
    model_name: str
    balanced_accuracy: Interval
    weighted_cost_per_record: Interval


@dataclass(frozen=True)
class DatasetSuiteResult:
    dataset_name: str
    records: int
    positive_rate: float
    models: tuple[ModelSuiteResult, ...]
    paired_cost_difference_random_forest_minus_logistic: Interval
    controlled_shift_balanced_accuracy_delta: dict[str, float]


def controlled_datasets() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Return deterministic synthetic cases with documented difficulty."""

    linear = make_classification(
        n_samples=1_000,
        n_features=12,
        n_informative=7,
        n_redundant=2,
        class_sep=1.2,
        flip_y=0.03,
        weights=[0.5, 0.5],
        random_state=RANDOM_STATE,
    )
    nonlinear_imbalanced = make_classification(
        n_samples=1_000,
        n_features=16,
        n_informative=8,
        n_redundant=3,
        n_clusters_per_class=3,
        class_sep=0.75,
        flip_y=0.05,
        weights=[0.7, 0.3],
        random_state=RANDOM_STATE + 1,
    )
    return {
        "synthetic_linear_balanced": linear,
        "synthetic_nonlinear_imbalanced": nonlinear_imbalanced,
    }


def _models() -> dict[str, object]:
    return {
        "cost_sensitive_logistic_regression": make_pipeline(
            StandardScaler(),
            LogisticRegression(
                max_iter=2_000,
                class_weight={0: 1, 1: FALSE_NEGATIVE_COST},
                random_state=RANDOM_STATE,
            ),
        ),
        "cost_sensitive_random_forest": RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=5,
            class_weight={0: 1, 1: FALSE_NEGATIVE_COST},
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }


def _per_record_cost(actual: np.ndarray, predicted: np.ndarray) -> np.ndarray:
    return np.where(
        (actual == 1) & (predicted == 0),
        FALSE_NEGATIVE_COST,
        np.where((actual == 0) & (predicted == 1), FALSE_POSITIVE_COST, 0),
    ).astype(float)


def bootstrap_interval(
    values: np.ndarray,
    statistic,
    *,
    resamples: int = 1_000,
    random_state: int = RANDOM_STATE,
) -> Interval:
    """Calculate a deterministic percentile bootstrap interval."""

    if len(values) == 0 or resamples < 100:
        raise ValueError("values must be non-empty and resamples must be at least 100")
    generator = np.random.default_rng(random_state)
    estimates = np.empty(resamples, dtype=float)
    for index in range(resamples):
        sample_indices = generator.integers(0, len(values), size=len(values))
        estimates[index] = statistic(values[sample_indices])
    estimate = float(statistic(values))
    lower, upper = np.quantile(estimates, [0.025, 0.975])
    return Interval(estimate=estimate, lower=float(lower), upper=float(upper))


def _balanced_accuracy_interval(
    actual: np.ndarray,
    predicted: np.ndarray,
    *,
    resamples: int,
) -> Interval:
    paired = np.column_stack([actual, predicted])
    return bootstrap_interval(
        paired,
        lambda rows: balanced_accuracy_score(rows[:, 0], rows[:, 1]),
        resamples=resamples,
    )


def evaluate_controlled_dataset(
    dataset_name: str,
    features: np.ndarray,
    target: np.ndarray,
    *,
    folds: int = 5,
    resamples: int = 1_000,
) -> DatasetSuiteResult:
    """Evaluate models with shared OOF folds and a controlled future shift."""

    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=RANDOM_STATE)
    predictions: dict[str, np.ndarray] = {}
    results: list[ModelSuiteResult] = []
    models = _models()
    for model_name, model in models.items():
        predicted = cross_val_predict(
            model, features, target, cv=splitter, method="predict"
        )
        predictions[model_name] = predicted
        costs = _per_record_cost(target, predicted)
        results.append(
            ModelSuiteResult(
                model_name=model_name,
                balanced_accuracy=_balanced_accuracy_interval(
                    target, predicted, resamples=resamples
                ),
                weighted_cost_per_record=bootstrap_interval(
                    costs, np.mean, resamples=resamples
                ),
            )
        )

    logistic_cost = _per_record_cost(
        target, predictions["cost_sensitive_logistic_regression"]
    )
    forest_cost = _per_record_cost(target, predictions["cost_sensitive_random_forest"])
    paired_difference = bootstrap_interval(
        forest_cost - logistic_cost, np.mean, resamples=resamples
    )

    train_features, test_features, train_target, test_target = train_test_split(
        features,
        target,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=target,
    )
    shifted_features = test_features.copy()
    shifted_features[:, : min(3, shifted_features.shape[1])] += 1.5 * train_features[
        :, : min(3, train_features.shape[1])
    ].std(axis=0)
    shift_deltas: dict[str, float] = {}
    for model_name, template in models.items():
        model = clone(template).fit(train_features, train_target)
        reference_score = balanced_accuracy_score(
            test_target, model.predict(test_features)
        )
        shifted_score = balanced_accuracy_score(
            test_target, model.predict(shifted_features)
        )
        shift_deltas[model_name] = float(shifted_score - reference_score)

    return DatasetSuiteResult(
        dataset_name=dataset_name,
        records=len(target),
        positive_rate=float(np.mean(target)),
        models=tuple(results),
        paired_cost_difference_random_forest_minus_logistic=paired_difference,
        controlled_shift_balanced_accuracy_delta=shift_deltas,
    )


def run_suite(*, folds: int = 5, resamples: int = 1_000) -> dict[str, object]:
    datasets = tuple(
        evaluate_controlled_dataset(
            name, features, target, folds=folds, resamples=resamples
        )
        for name, (features, target) in controlled_datasets().items()
    )
    return {
        "schema_version": SUITE_SCHEMA_VERSION,
        "scope": (
            "Controlled synthetic robustness benchmark; not external domain "
            "validation and not evidence for operational decisions."
        ),
        "random_state": RANDOM_STATE,
        "folds": folds,
        "bootstrap_resamples": resamples,
        "datasets": [asdict(dataset) for dataset in datasets],
    }


def write_suite(payload: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def write_markdown_report(payload: dict[str, object], report_path: Path) -> None:
    lines = [
        "# TrustLens Controlled Benchmark Report",
        "",
        str(payload["scope"]),
        "",
        "The historical credit final holdout was not opened or reevaluated.",
        "",
    ]
    for dataset in payload["datasets"]:
        lines.extend(
            [
                f"## {dataset['dataset_name']}",
                "",
                f"Records: {dataset['records']}; positive rate: "
                f"{dataset['positive_rate']:.3f}.",
                "",
                "| Model | Balanced accuracy (95% bootstrap CI) | "
                "Weighted cost/record (95% bootstrap CI) |",
                "|---|---:|---:|",
            ]
        )
        for model in dataset["models"]:
            balance = model["balanced_accuracy"]
            cost = model["weighted_cost_per_record"]
            lines.append(
                f"| {model['model_name']} | {balance['estimate']:.3f} "
                f"({balance['lower']:.3f}–{balance['upper']:.3f}) | "
                f"{cost['estimate']:.3f} ({cost['lower']:.3f}–"
                f"{cost['upper']:.3f}) |"
            )
        difference = dataset["paired_cost_difference_random_forest_minus_logistic"]
        lines.extend(
            [
                "",
                "Paired cost difference (random forest − logistic): "
                f"{difference['estimate']:.3f} "
                f"(95% CI {difference['lower']:.3f}–"
                f"{difference['upper']:.3f}). Negative favours the forest.",
                "",
                "Controlled-shift balanced-accuracy deltas: "
                + ", ".join(
                    f"{name} {delta:+.3f}"
                    for name, delta in dataset[
                        "controlled_shift_balanced_accuracy_delta"
                    ].items()
                ),
                "",
            ]
        )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run controlled TrustLens benchmarks")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--resamples", type=int, default=1_000)
    parser.add_argument("--output", type=Path, default=DEFAULT_SUITE_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()
    if args.folds < 2 or args.resamples < 100:
        raise SystemExit("folds must be >= 2 and resamples must be >= 100")
    payload = run_suite(folds=args.folds, resamples=args.resamples)
    write_suite(payload, args.output)
    write_markdown_report(payload, args.report)
    print(f"Wrote suite to {args.output} and report to {args.report}")


if __name__ == "__main__":
    main()

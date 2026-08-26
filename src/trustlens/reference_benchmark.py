"""Real-dataset reference benchmark for the TrustLens evaluation machinery."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.datasets import load_breast_cancer, load_wine
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from trustlens.baseline import RANDOM_STATE

SCHEMA_VERSION = "1.0"
DEFAULT_OUTPUT = Path("results/reference_benchmark.json")
DEFAULT_REPORT = Path("reports/Reference_Benchmark_Report.md")


@dataclass(frozen=True)
class ReferenceResult:
    dataset: str
    model: str
    records: int
    features: int
    balanced_accuracy: float
    roc_auc: float
    brier_score: float
    shifted_balanced_accuracy_delta: float
    proxy_group_recall_gap: float | None


def reference_datasets() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Load deterministic, packaged public reference datasets.

    These datasets exercise the evaluation pipeline across domains. They are not
    external validation for lending or evidence for operational use.
    """

    cancer = load_breast_cancer()
    wine = load_wine()
    return {
        "wisconsin_breast_cancer": (cancer.data, cancer.target),
        "wine_class_0_vs_rest": (wine.data, (wine.target == 0).astype(int)),
    }


def candidate_models() -> dict[str, object]:
    """Return diverse, deterministic baselines without optional dependencies."""

    logistic = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=2_000, random_state=RANDOM_STATE),
    )
    return {
        "logistic_regression": logistic,
        "calibrated_logistic_regression": CalibratedClassifierCV(
            estimator=clone(logistic), method="sigmoid", cv=3
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=250,
            min_samples_leaf=3,
            random_state=RANDOM_STATE,
            n_jobs=1,
        ),
        "histogram_gradient_boosting": HistGradientBoostingClassifier(
            max_iter=150,
            learning_rate=0.08,
            random_state=RANDOM_STATE,
        ),
    }


def _recall_gap(
    actual: np.ndarray, predicted: np.ndarray, proxy: np.ndarray
) -> float | None:
    """Return a diagnostic recall gap across low/high feature-value halves."""

    high = proxy >= np.median(proxy)
    recalls: list[float] = []
    for selected in (high, ~high):
        positives = (actual[selected] == 1).sum()
        if positives:
            recalls.append(
                float(
                    (predicted[selected] == actual[selected])[
                        actual[selected] == 1
                    ].mean()
                )
            )
    return abs(recalls[0] - recalls[1]) if len(recalls) == 2 else None


def evaluate_reference_dataset(
    name: str, features: np.ndarray, target: np.ndarray, *, folds: int = 5
) -> list[ReferenceResult]:
    """Evaluate candidates with shared folds and a deterministic noise shift."""

    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=RANDOM_STATE)
    train_x, test_x, train_y, test_y = train_test_split(
        features, target, test_size=0.3, stratify=target, random_state=RANDOM_STATE
    )
    scale = np.std(train_x, axis=0)
    scale[scale == 0] = 1
    generator = np.random.default_rng(RANDOM_STATE)
    shifted_x = test_x + generator.normal(0, 0.35, test_x.shape) * scale

    results = []
    for model_name, template in candidate_models().items():
        probabilities = cross_val_predict(
            template, features, target, cv=splitter, method="predict_proba"
        )[:, 1]
        predicted = (probabilities >= 0.5).astype(int)
        fitted = clone(template).fit(train_x, train_y)
        reference_score = balanced_accuracy_score(test_y, fitted.predict(test_x))
        shifted_score = balanced_accuracy_score(test_y, fitted.predict(shifted_x))
        results.append(
            ReferenceResult(
                dataset=name,
                model=model_name,
                records=len(target),
                features=features.shape[1],
                balanced_accuracy=round(
                    float(balanced_accuracy_score(target, predicted)), 10
                ),
                roc_auc=round(float(roc_auc_score(target, probabilities)), 10),
                brier_score=round(float(brier_score_loss(target, probabilities)), 10),
                shifted_balanced_accuracy_delta=round(
                    float(shifted_score - reference_score), 10
                ),
                proxy_group_recall_gap=(
                    None
                    if (gap := _recall_gap(target, predicted, features[:, 0])) is None
                    else round(gap, 10)
                ),
            )
        )
    return results


def run_reference_benchmark(*, folds: int = 5) -> dict[str, object]:
    """Run all public reference cases and return a stable JSON payload."""

    if folds < 2:
        raise ValueError("folds must be at least 2")
    results = [
        result
        for name, (features, target) in reference_datasets().items()
        for result in evaluate_reference_dataset(name, features, target, folds=folds)
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": (
            "Cross-domain public reference benchmark of evaluation machinery; "
            "not external credit validation or evidence for real-world decisions."
        ),
        "random_state": RANDOM_STATE,
        "folds": folds,
        "results": [asdict(result) for result in results],
    }


def write_outputs(payload: dict[str, object], output: Path, report: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# TrustLens Public Reference Benchmark",
        "",
        str(payload["scope"]),
        "",
        "| Dataset | Model | Balanced accuracy | ROC AUC | Brier | Shift Δ | Proxy recall gap |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for result in payload["results"]:
        gap = result["proxy_group_recall_gap"]
        lines.append(
            f"| {result['dataset']} | {result['model']} | "
            f"{result['balanced_accuracy']:.3f} | {result['roc_auc']:.3f} | "
            f"{result['brier_score']:.3f} | "
            f"{result['shifted_balanced_accuracy_delta']:+.3f} | "
            f"{gap:.3f} |"
        )
    lines.extend(
        [
            "",
            "The proxy split uses the first feature only as a pipeline diagnostic. It is not a protected-attribute fairness assessment.",
            "Lower Brier score is better; a negative shift delta indicates degradation under the controlled noise shift.",
        ]
    )
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run TrustLens public reference benchmark"
    )
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    payload = run_reference_benchmark(folds=args.folds)
    write_outputs(payload, args.output, args.report)
    print(f"Wrote reference benchmark to {args.output} and {args.report}")


if __name__ == "__main__":
    main()

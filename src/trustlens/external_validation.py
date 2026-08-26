"""Independent credit-domain reference validation on the FICO HELOC dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.datasets import fetch_openml
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from trustlens.baseline import RANDOM_STATE

OPENML_DATA_ID = 45554
DEFAULT_OUTPUT = Path("results/external_credit_validation.json")
DEFAULT_REPORT = Path("reports/External_Credit_Validation.md")


def load_heloc_reference(
    *, data_home: Path = Path(".audit-cache/openml")
) -> tuple[pd.DataFrame, np.ndarray]:
    """Load the CC0 OpenML HELOC reference without committing raw records."""

    dataset = fetch_openml(
        data_id=OPENML_DATA_ID,
        as_frame=True,
        parser="auto",
        data_home=data_home,
    )
    features = dataset.data.astype(float)
    target = (dataset.target.astype("string") == "Bad").astype(int).to_numpy()
    if features.empty or set(np.unique(target)) != {0, 1}:
        raise ValueError("unexpected HELOC dataset schema")
    return features, target


def validation_models() -> dict[str, object]:
    return {
        "logistic_regression": make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(max_iter=2_000, random_state=RANDOM_STATE),
        ),
        "random_forest": make_pipeline(
            SimpleImputer(strategy="median"),
            RandomForestClassifier(
                n_estimators=250,
                min_samples_leaf=5,
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=1,
            ),
        ),
    }


def evaluate_external_credit_reference(
    features: pd.DataFrame, target: np.ndarray, *, folds: int = 5
) -> dict[str, object]:
    if folds < 2:
        raise ValueError("folds must be at least 2")
    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=RANDOM_STATE)
    results = []
    for name, model in validation_models().items():
        probabilities = cross_val_predict(
            clone(model), features, target, cv=splitter, method="predict_proba"
        )[:, 1]
        predicted = (probabilities >= 0.5).astype(int)
        results.append(
            {
                "model": name,
                "balanced_accuracy": round(
                    float(balanced_accuracy_score(target, predicted)), 10
                ),
                "roc_auc": round(float(roc_auc_score(target, probabilities)), 10),
                "brier_score": round(
                    float(brier_score_loss(target, probabilities)), 10
                ),
            }
        )
    schema = "|".join(features.columns) + f"|{len(features)}"
    return {
        "schema_version": "1.0",
        "dataset": "FICO-HELOC-cleaned",
        "openml_data_id": OPENML_DATA_ID,
        "license": "CC0-1.0",
        "records": len(features),
        "features": features.shape[1],
        "positive_class": "Bad",
        "positive_rate": round(float(np.mean(target)), 10),
        "schema_fingerprint_sha256": hashlib.sha256(schema.encode()).hexdigest(),
        "folds": folds,
        "random_state": RANDOM_STATE,
        "collection_period_status": "not_documented_in_source_metadata",
        "scope": (
            "Independent credit-domain reference validation. It is not a temporal "
            "validation, a replication of the historical study, or evidence for "
            "operational credit decisions."
        ),
        "results": results,
    }


def write_validation(payload: dict[str, object], output: Path, report: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# External Credit-Domain Reference Validation",
        "",
        str(payload["scope"]),
        "",
        f"Dataset: FICO HELOC cleaned (OpenML {payload['openml_data_id']}, {payload['license']}).",
        f"Records: {payload['records']}; features: {payload['features']}; positive rate: {payload['positive_rate']:.3f}.",
        "The source metadata does not document a collection period, so this report does not call the dataset contemporary.",
        "",
        "| Model | Balanced accuracy | ROC AUC | Brier score |",
        "|---|---:|---:|---:|",
    ]
    for result in payload["results"]:
        lines.append(
            f"| {result['model']} | {result['balanced_accuracy']:.3f} | "
            f"{result['roc_auc']:.3f} | {result['brier_score']:.3f} |"
        )
    lines.extend(
        [
            "",
            "This dataset has no protected-attribute audit in TrustLens and must not be used to make claims about fairness.",
            "Raw HELOC records are downloaded into an ignored cache and are not committed to the repository.",
        ]
    )
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run external HELOC validation")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--data-home", type=Path, default=Path(".audit-cache/openml"))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    features, target = load_heloc_reference(data_home=args.data_home)
    payload = evaluate_external_credit_reference(features, target, folds=args.folds)
    write_validation(payload, args.output, args.report)
    print(f"Wrote external validation to {args.output} and {args.report}")


if __name__ == "__main__":
    main()

import json
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from trustlens import (
    benchmark,
    benchmark_suite,
    external_validation,
    reference_benchmark,
)
from trustlens.data import CreditDataset
from trustlens.drift import detect_covariate_drift
from trustlens.experiments import _cross_validate_model
from trustlens.review_policy import analyse_review_budgets


def test_benchmark_cli_writes_payload(tmp_path, monkeypatch) -> None:
    output = tmp_path / "benchmark.json"
    payload = {"candidate_ranking": []}
    result = SimpleNamespace(to_dict=lambda: payload)
    monkeypatch.setattr(benchmark, "run_development_benchmark", lambda *_, **__: result)
    monkeypatch.setattr(
        sys, "argv", ["benchmark", "--folds", "2", "--output", str(output)]
    )
    benchmark.main()
    assert json.loads(output.read_text()) == payload


def test_suite_cli_and_validation(tmp_path, monkeypatch) -> None:
    output, report = tmp_path / "suite.json", tmp_path / "suite.md"
    payload = {"scope": "test", "datasets": []}
    monkeypatch.setattr(benchmark_suite, "run_suite", lambda **_: payload)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "suite",
            "--folds",
            "2",
            "--resamples",
            "100",
            "--output",
            str(output),
            "--report",
            str(report),
        ],
    )
    benchmark_suite.main()
    assert output.exists() and report.exists()
    monkeypatch.setattr(sys, "argv", ["suite", "--folds", "1"])
    with pytest.raises(SystemExit):
        benchmark_suite.main()


def test_reference_and_external_clis(tmp_path, monkeypatch) -> None:
    reference_payload = {"scope": "reference", "results": []}
    monkeypatch.setattr(
        reference_benchmark, "run_reference_benchmark", lambda **_: reference_payload
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "reference",
            "--folds",
            "2",
            "--output",
            str(tmp_path / "r.json"),
            "--report",
            str(tmp_path / "r.md"),
        ],
    )
    reference_benchmark.main()
    assert (tmp_path / "r.json").exists()

    features = pd.DataFrame({"a": [0.0, 1.0, 2.0, 3.0], "b": [1.0, 0.0, 1.0, 0.0]})
    target = np.array([0, 0, 1, 1])
    payload = {
        "scope": "external",
        "results": [],
        "openml_data_id": 45554,
        "license": "CC0",
        "records": 4,
        "features": 2,
        "positive_rate": 0.5,
    }
    monkeypatch.setattr(
        external_validation, "load_heloc_reference", lambda **_: (features, target)
    )
    monkeypatch.setattr(
        external_validation,
        "evaluate_external_credit_reference",
        lambda *_, **__: payload,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "external",
            "--output",
            str(tmp_path / "e.json"),
            "--report",
            str(tmp_path / "e.md"),
        ],
    )
    external_validation.main()
    assert (tmp_path / "e.json").exists()


def test_cross_validation_core_on_numeric_fixture() -> None:
    features = pd.DataFrame({"x": np.linspace(-2, 2, 60), "y": np.tile([0.0, 1.0], 30)})
    target = pd.Series(([0, 1] * 30), name="higher_risk")
    dataset = CreditDataset(features, target)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500))
    result = _cross_validate_model(dataset, "fixture", model, folds=2)
    assert result.model_name == "fixture"
    assert result.folds == 2


def test_drift_and_review_workflows(monkeypatch) -> None:
    from trustlens.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES

    generator = np.random.default_rng(42)
    reference = pd.DataFrame(
        {
            **{name: generator.normal(size=30) for name in NUMERIC_FEATURES},
            **{
                name: generator.integers(1, 4, size=30) for name in CATEGORICAL_FEATURES
            },
        }
    )
    incoming = reference.copy()
    incoming[NUMERIC_FEATURES[0]] += 4
    result = detect_covariate_drift(reference, incoming)
    assert 0 <= result.adversarial_auc_mean <= 1
    with pytest.raises(ValueError):
        detect_covariate_drift(reference, incoming.drop(columns=[incoming.columns[0]]))

    actual = np.array([0, 0, 1, 1, 0, 1])
    probabilities = np.array([0.1, 0.4, 0.3, 0.9, 0.2, 0.8])
    monkeypatch.setattr(
        "trustlens.review_policy.out_of_fold_probabilities",
        lambda *_, **__: (actual, probabilities, probabilities),
    )
    policies = analyse_review_budgets(
        CreditDataset(reference.iloc[:6], pd.Series(actual)), budgets=(0.0, 0.5)
    )
    assert len(policies) == 2

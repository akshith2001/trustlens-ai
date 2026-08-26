import json

import numpy as np
import pytest

from trustlens.reference_benchmark import (
    _recall_gap,
    reference_datasets,
    run_reference_benchmark,
    write_outputs,
)


def test_reference_datasets_are_binary_and_nonempty() -> None:
    for features, target in reference_datasets().values():
        assert len(features) == len(target)
        assert features.shape[1] > 1
        assert set(np.unique(target)) == {0, 1}


def test_recall_gap_and_invalid_folds() -> None:
    actual = np.array([1, 1, 1, 1])
    predicted = np.array([1, 1, 0, 0])
    proxy = np.array([0, 0, 1, 1])
    assert _recall_gap(actual, predicted, proxy) == 1.0
    with pytest.raises(ValueError, match="at least 2"):
        run_reference_benchmark(folds=1)


def test_reference_benchmark_and_outputs(tmp_path) -> None:
    payload = run_reference_benchmark(folds=2)
    assert payload["schema_version"] == "1.0"
    assert len(payload["results"]) == 8
    assert {result["model"] for result in payload["results"]} == {
        "logistic_regression",
        "calibrated_logistic_regression",
        "random_forest",
        "histogram_gradient_boosting",
    }
    output = tmp_path / "result.json"
    report = tmp_path / "report.md"
    write_outputs(payload, output, report)
    assert json.loads(output.read_text())["folds"] == 2
    assert "not external credit validation" in report.read_text()

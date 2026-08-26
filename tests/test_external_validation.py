import json

import numpy as np
import pandas as pd
import pytest

from trustlens.external_validation import (
    evaluate_external_credit_reference,
    write_validation,
)


def test_external_validation_schema_and_outputs(tmp_path) -> None:
    generator = np.random.default_rng(42)
    features = pd.DataFrame(generator.normal(size=(80, 4)), columns=list("abcd"))
    target = (features["a"] + features["b"] > 0).astype(int).to_numpy()
    payload = evaluate_external_credit_reference(features, target, folds=2)
    assert payload["license"] == "CC0-1.0"
    assert len(payload["results"]) == 2
    output, report = tmp_path / "result.json", tmp_path / "report.md"
    write_validation(payload, output, report)
    assert json.loads(output.read_text())["records"] == 80
    assert "does not call the dataset contemporary" in report.read_text()


def test_external_validation_rejects_invalid_folds() -> None:
    with pytest.raises(ValueError):
        evaluate_external_credit_reference(
            pd.DataFrame({"x": [0, 1]}), np.array([0, 1]), folds=1
        )

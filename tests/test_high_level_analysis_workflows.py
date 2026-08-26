import numpy as np
import pandas as pd

from trustlens import calibration, explainability, local_explanation
from trustlens.data import CreditDataset


def _dataset() -> CreditDataset:
    features = pd.DataFrame({"feature_a": range(10), "feature_b": range(10, 20)})
    target = pd.Series([0, 1] * 5)
    return CreditDataset(features, target)


def test_cross_validated_permutation_importance(monkeypatch) -> None:
    class Model:
        def fit(self, *_):
            return self

    class Result:
        importances = np.array([[0.1, 0.2], [0.3, 0.4]])

    monkeypatch.setattr(
        explainability,
        "development_data",
        lambda _: (_dataset().features, _dataset().target),
    )
    monkeypatch.setattr(explainability, "build_random_forest", Model)
    monkeypatch.setattr(
        explainability, "permutation_importance", lambda *_, **__: Result()
    )
    result = explainability.cross_validated_permutation_importance(
        _dataset(), folds=2, repeats=2
    )
    assert [item.feature for item in result] == ["feature_b", "feature_a"]


def test_calibration_analysis_summary(monkeypatch) -> None:
    actual = np.array([0, 0, 1, 1])
    raw = np.array([0.1, 0.4, 0.6, 0.9])
    calibrated = np.array([0.05, 0.2, 0.8, 0.95])
    monkeypatch.setattr(
        calibration,
        "out_of_fold_probabilities",
        lambda *_, **__: (actual, raw, calibrated),
    )
    summary = calibration.analyse_random_forest_calibration(_dataset())
    assert summary.calibrated_brier_score < summary.raw_brier_score
    assert 0.05 <= summary.selected_threshold <= 0.95


def test_local_explanation_workflow(monkeypatch) -> None:
    features = pd.DataFrame({"duration": [1.0, 2.0, 3.0, 4.0], "purpose": [1, 1, 2, 2]})
    target = pd.Series([0, 1, 0, 1])

    class Model:
        def __init__(self, **_):
            pass

        def fit(self, *_):
            return self

        def predict_proba(self, frame):
            probabilities = np.linspace(0.4, 0.6, len(frame))
            return np.column_stack((1 - probabilities, probabilities))

    monkeypatch.setattr(
        local_explanation, "development_data", lambda _: (features, target)
    )
    monkeypatch.setattr(local_explanation, "NUMERIC_FEATURES", ("duration",))
    monkeypatch.setattr(local_explanation, "CATEGORICAL_FEATURES", ("purpose",))
    monkeypatch.setattr(local_explanation, "GOVERNED_EXCLUDED_FEATURES", frozenset())
    monkeypatch.setattr(
        local_explanation,
        "train_test_split",
        lambda x, y, **_: (x.iloc[:2], x.iloc[2:], y.iloc[:2], y.iloc[2:]),
    )
    monkeypatch.setattr(local_explanation, "CalibratedClassifierCV", Model)
    result = local_explanation.explain_validation_record(
        CreditDataset(features, target)
    )
    assert result.effects
    assert "not causal" in result.warning

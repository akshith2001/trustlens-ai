from trustlens.data import EXPECTED_FEATURES
from trustlens.features import (
    CATEGORICAL_FEATURES,
    GOVERNED_EXCLUDED_FEATURES,
    NUMERIC_FEATURES,
)
from trustlens.features import build_preprocessor
from trustlens.experiments import build_logistic_regression


def test_feature_roles_are_disjoint_and_complete() -> None:
    numeric = set(NUMERIC_FEATURES)
    categorical = set(CATEGORICAL_FEATURES)

    assert numeric.isdisjoint(categorical)
    assert len(numeric | categorical) == EXPECTED_FEATURES


def test_cost_sensitive_model_penalises_false_negatives_more() -> None:
    pipeline = build_logistic_regression(cost_sensitive=True)
    model = pipeline.named_steps["model"]

    assert model.class_weight == {0: 1, 1: 5}


def test_preprocessor_can_exclude_sensitive_features() -> None:
    preprocessor = build_preprocessor(
        frozenset({"age_years", "personal_status_sex", "foreign_worker"})
    )
    selected_columns = {
        column
        for _, _, columns in preprocessor.transformers
        for column in columns
    }

    assert "age_years" not in selected_columns
    assert "personal_status_sex" not in selected_columns
    assert "foreign_worker" not in selected_columns


def test_governed_model_excludes_invalid_and_sensitive_worker_fields() -> None:
    assert GOVERNED_EXCLUDED_FEATURES == {
        "personal_status_sex",
        "foreign_worker",
    }

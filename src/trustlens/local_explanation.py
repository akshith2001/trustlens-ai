"""Local model-sensitivity explanations without causal claims."""

from dataclasses import dataclass

import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split

from trustlens.baseline import RANDOM_STATE
from trustlens.calibration import development_data
from trustlens.data import CreditDataset
from trustlens.experiments import build_random_forest
from trustlens.features import (
    CATEGORICAL_FEATURES,
    GOVERNED_EXCLUDED_FEATURES,
    NUMERIC_FEATURES,
)
from trustlens.governance import GOVERNED_DECISION_THRESHOLD


@dataclass(frozen=True)
class SensitivityEffect:
    feature: str
    observed_value: str
    reference_value: str
    probability_change: float


@dataclass(frozen=True)
class LocalExplanation:
    original_probability: float
    threshold: float
    predicted_class: int
    effects: list[SensitivityEffect]
    warning: str


def _reference_values(training_features: pd.DataFrame) -> dict[str, object]:
    values: dict[str, object] = {}
    for feature in NUMERIC_FEATURES:
        if feature not in GOVERNED_EXCLUDED_FEATURES:
            values[feature] = training_features[feature].median()
    for feature in CATEGORICAL_FEATURES:
        if feature not in GOVERNED_EXCLUDED_FEATURES:
            values[feature] = training_features[feature].mode().iloc[0]
    return values


def explain_validation_record(dataset: CreditDataset) -> LocalExplanation:
    """Explain one borderline internal validation record by perturbation."""

    features, target = development_data(dataset)
    train_features, validation_features, train_target, _ = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=target,
    )
    model = CalibratedClassifierCV(
        estimator=build_random_forest(
            excluded_features=GOVERNED_EXCLUDED_FEATURES
        ),
        method="sigmoid",
        cv=3,
    )
    model.fit(train_features, train_target)
    probabilities = model.predict_proba(validation_features)[:, 1]
    position = int(abs(probabilities - GOVERNED_DECISION_THRESHOLD).argmin())
    record = validation_features.iloc[[position]].copy()
    original_probability = float(probabilities[position])

    effects = []
    for feature, reference_value in _reference_values(train_features).items():
        changed = record.copy()
        observed_value = changed.iloc[0][feature]
        changed.loc[:, feature] = reference_value
        changed_probability = float(model.predict_proba(changed)[0, 1])
        effects.append(
            SensitivityEffect(
                feature=feature,
                observed_value=str(observed_value),
                reference_value=str(reference_value),
                probability_change=changed_probability - original_probability,
            )
        )
    effects.sort(key=lambda effect: abs(effect.probability_change), reverse=True)
    return LocalExplanation(
        original_probability=original_probability,
        threshold=GOVERNED_DECISION_THRESHOLD,
        predicted_class=int(original_probability >= GOVERNED_DECISION_THRESHOLD),
        effects=effects,
        warning=(
            "One-at-a-time perturbations show model sensitivity only. They are "
            "not causal effects, feasible interventions, or financial advice."
        ),
    )


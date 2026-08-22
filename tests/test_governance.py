from trustlens.governance import (
    GOVERNED_DECISION_THRESHOLD,
    GOVERNED_REVIEW_BUDGET,
)


def test_governance_settings_are_valid_probabilities() -> None:
    assert 0 < GOVERNED_DECISION_THRESHOLD < 1
    assert 0 < GOVERNED_REVIEW_BUDGET < 1

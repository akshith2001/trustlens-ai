from trustlens.governance import (
    GOVERNED_DECISION_THRESHOLD,
    GOVERNED_REVIEW_BUDGET,
    determine_governance_action,
)


def test_governance_settings_are_valid_probabilities() -> None:
    assert 0 < GOVERNED_DECISION_THRESHOLD < 1
    assert 0 < GOVERNED_REVIEW_BUDGET < 1


def test_drift_overrides_record_probability() -> None:
    action, _ = determine_governance_action(
        0.01, drift_auc=0.75, is_out_of_distribution=False
    )
    assert action == "pause_and_investigate"


def test_out_of_distribution_record_requires_review() -> None:
    action, _ = determine_governance_action(
        0.01, drift_auc=0.50, is_out_of_distribution=True
    )
    assert action == "pause_for_human_review"


def test_probability_routes_to_monitoring_or_review() -> None:
    low_action, _ = determine_governance_action(
        0.05, drift_auc=0.50, is_out_of_distribution=False
    )
    warning_action, _ = determine_governance_action(
        0.45, drift_auc=0.50, is_out_of_distribution=False
    )
    assert low_action == "continue_with_monitoring"
    assert warning_action == "human_review_required"


def test_invalid_probability_is_rejected() -> None:
    try:
        determine_governance_action(1.01, drift_auc=0.50, is_out_of_distribution=False)
    except ValueError as error:
        assert "probability" in str(error)
    else:
        raise AssertionError("Expected invalid probability to be rejected")

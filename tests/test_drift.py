from trustlens.drift import drift_action


def test_drift_policy_pauses_at_threshold() -> None:
    assert drift_action(0.69) == "continue_monitoring"
    assert drift_action(0.70) == "pause_and_investigate"

from trustlens.ood import ood_action


def test_flagged_record_is_paused() -> None:
    assert ood_action(True) == "pause_for_human_review"
    assert ood_action(False) == "continue_with_audit"

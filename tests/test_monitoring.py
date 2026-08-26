import pytest

from trustlens.monitoring import GovernanceMonitor


def test_monitoring_is_bounded_and_alerts() -> None:
    monitor = GovernanceMonitor(window_size=2, ood_rate_alert_threshold=0.5)
    assert monitor.snapshot().records == 0
    monitor.record(probability=0.2, drift_auc=0.5, is_ood=False, action="continue")
    monitor.record(probability=0.8, drift_auc=0.8, is_ood=True, action="pause")
    snapshot = monitor.snapshot()
    assert snapshot.records == 2
    assert set(snapshot.alerts) == {
        "population_drift_threshold_breached",
        "ood_rate_threshold_breached",
    }
    assert snapshot.actions == {"continue": 1, "pause": 1}
    monitor.record(probability=0.4, drift_auc=0.4, is_ood=False, action="continue")
    assert monitor.snapshot().records == 2


def test_monitoring_validates_inputs() -> None:
    with pytest.raises(ValueError):
        GovernanceMonitor(window_size=0)
    monitor = GovernanceMonitor()
    with pytest.raises(ValueError):
        monitor.record(probability=2, drift_auc=0.5, is_ood=False, action="bad")

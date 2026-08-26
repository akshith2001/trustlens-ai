"""Runtime governance telemetry with privacy-preserving aggregates."""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import asdict, dataclass
from threading import Lock


@dataclass(frozen=True)
class MonitoringSnapshot:
    records: int
    mean_probability: float
    ood_rate: float
    maximum_drift_auc: float
    actions: dict[str, int]
    alerts: tuple[str, ...]


class GovernanceMonitor:
    """Maintain a bounded window of non-identifying governance signals."""

    def __init__(
        self,
        *,
        window_size: int = 500,
        drift_alert_threshold: float = 0.70,
        ood_rate_alert_threshold: float = 0.10,
    ):
        if window_size < 1:
            raise ValueError("window_size must be positive")
        self._events: deque[tuple[float, float, bool, str]] = deque(maxlen=window_size)
        self._drift_threshold = drift_alert_threshold
        self._ood_threshold = ood_rate_alert_threshold
        self._lock = Lock()

    def record(
        self, *, probability: float, drift_auc: float, is_ood: bool, action: str
    ) -> None:
        if not 0 <= probability <= 1 or not 0 <= drift_auc <= 1:
            raise ValueError("probability and drift_auc must be between 0 and 1")
        with self._lock:
            self._events.append((probability, drift_auc, is_ood, action))

    def snapshot(self) -> MonitoringSnapshot:
        with self._lock:
            events = tuple(self._events)
        if not events:
            return MonitoringSnapshot(0, 0.0, 0.0, 0.0, {}, ())
        ood_rate = sum(event[2] for event in events) / len(events)
        maximum_drift = max(event[1] for event in events)
        alerts = []
        if maximum_drift >= self._drift_threshold:
            alerts.append("population_drift_threshold_breached")
        if ood_rate >= self._ood_threshold:
            alerts.append("ood_rate_threshold_breached")
        return MonitoringSnapshot(
            records=len(events),
            mean_probability=sum(event[0] for event in events) / len(events),
            ood_rate=ood_rate,
            maximum_drift_auc=maximum_drift,
            actions=dict(Counter(event[3] for event in events)),
            alerts=tuple(alerts),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self.snapshot())

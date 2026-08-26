"""Uncertainty summaries for locked classification results."""

from dataclasses import asdict, dataclass
from math import sqrt


@dataclass(frozen=True)
class Interval:
    estimate: float
    lower: float
    upper: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def wilson_interval(
    successes: int, trials: int, z: float = 1.959963984540054
) -> Interval:
    """Return a two-sided Wilson score interval for a binomial proportion."""

    if trials <= 0:
        raise ValueError("trials must be positive")
    if successes < 0 or successes > trials:
        raise ValueError("successes must be between zero and trials")

    estimate = successes / trials
    z_squared = z * z
    denominator = 1 + (z_squared / trials)
    centre = (estimate + (z_squared / (2 * trials))) / denominator
    margin = (
        z
        * sqrt(
            (estimate * (1 - estimate) / trials) + (z_squared / (4 * trials * trials))
        )
        / denominator
    )
    return Interval(
        estimate=estimate,
        lower=max(0.0, centre - margin),
        upper=min(1.0, centre + margin),
    )


def classification_intervals(
    *,
    true_negatives: int,
    false_positives: int,
    false_negatives: int,
    true_positives: int,
) -> dict[str, Interval]:
    """Calculate 95% Wilson intervals from a locked confusion matrix."""

    return {
        "recall": wilson_interval(true_positives, true_positives + false_negatives),
        "precision": wilson_interval(true_positives, true_positives + false_positives),
        "specificity": wilson_interval(
            true_negatives, true_negatives + false_positives
        ),
    }

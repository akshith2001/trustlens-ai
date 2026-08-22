"""Create uncertainty intervals without retraining or retuning the locked model."""

import json
from pathlib import Path

from trustlens.uncertainty import classification_intervals


ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "results" / "final_test_metrics.json"
OUTPUT_PATH = ROOT / "results" / "final_test_uncertainty.json"


def main() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    intervals = classification_intervals(
        true_negatives=metrics["true_negatives"],
        false_positives=metrics["false_positives"],
        false_negatives=metrics["false_negatives"],
        true_positives=metrics["true_positives"],
    )
    payload = {
        "method": "two-sided 95% Wilson score interval",
        "purpose": "post-hoc uncertainty reporting; no model selection or retuning",
        "intervals": {name: value.to_dict() for name, value in intervals.items()},
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    for name, interval in intervals.items():
        print(
            f"{name}: {interval.estimate:.3f} "
            f"(95% CI {interval.lower:.3f}-{interval.upper:.3f})"
        )
    print(f"Written to {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

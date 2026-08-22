"""Run descriptive slice analysis on the locked test predictions."""

import json
from pathlib import Path

from trustlens.data import load_credit_dataset
from trustlens.error_analysis import find_error_slices
from trustlens.features import GOVERNED_EXCLUDED_FEATURES, NUMERIC_FEATURES
from trustlens.final_evaluation import generate_locked_predictions


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "results" / "error_analysis.json"


def main() -> None:
    dataset = load_credit_dataset()
    features, actual, _, predicted = generate_locked_predictions(dataset)
    rankings = find_error_slices(
        features,
        actual.to_numpy(),
        predicted,
        numeric_features=tuple(NUMERIC_FEATURES),
        excluded_features=GOVERNED_EXCLUDED_FEATURES,
        minimum_class_support=10,
        limit=10,
    )
    payload = {
        "analysis_type": "post-hoc descriptive slice diagnostics",
        "minimum_class_support": 10,
        "model_changed_or_retuned": False,
        "warning": "Many slices were inspected on a small historical test set. Patterns may be unstable and are not causal or deployment evidence.",
        "rankings": {name: [entry.to_dict() for entry in entries] for name, entries in rankings.items()},
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    for name, entries in rankings.items():
        print(name.replace("_", " ").title())
        for entry in entries[:5]:
            print(f"  {entry.feature}={entry.group}: {entry.error_rate:.3f} ({entry.errors}/{entry.class_support})")
    print(f"Written to {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

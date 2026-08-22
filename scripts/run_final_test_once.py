"""Create the immutable first final-test result for the governed model."""

import json
from pathlib import Path

from trustlens.data import load_credit_dataset
from trustlens.final_evaluation import evaluate_locked_model


RESULT_PATH = Path("results/final_test_metrics.json")


def main() -> None:
    if RESULT_PATH.exists():
        raise SystemExit(
            "Final test result already exists. Refusing to rerun or overwrite it."
        )
    result = evaluate_locked_model(load_credit_dataset())
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(
        json.dumps(result.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result.to_dict(), indent=2))
    print(f"Locked result written to {RESULT_PATH}")


if __name__ == "__main__":
    main()


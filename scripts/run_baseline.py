"""Run the transparent minimum benchmark for TrustLens models."""

from dataclasses import asdict

from trustlens.baseline import evaluate_majority_baseline
from trustlens.data import load_credit_dataset


def main() -> None:
    metrics = evaluate_majority_baseline(load_credit_dataset())

    print("Majority-class baseline")
    for name, value in asdict(metrics).items():
        if isinstance(value, float):
            print(f"{name}: {value:.3f}")
        else:
            print(f"{name}: {value}")


if __name__ == "__main__":
    main()


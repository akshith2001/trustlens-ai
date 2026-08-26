"""Evaluate individual-record out-of-distribution screening."""

from dataclasses import asdict

from trustlens.data import load_credit_dataset
from trustlens.ood import evaluate_ood_detector


def main() -> None:
    result = evaluate_ood_detector(load_credit_dataset())
    print("Individual out-of-distribution evaluation")
    for name, value in asdict(result).items():
        if isinstance(value, float):
            print(f"{name}: {value:.3f}")
        else:
            print(f"{name}: {value}")
    print("Synthetic extremes are test fixtures, not observed applicants.")


if __name__ == "__main__":
    main()

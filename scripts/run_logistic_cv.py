"""Evaluate logistic regression without accessing the final test results."""

from dataclasses import asdict

from trustlens.data import load_credit_dataset
from trustlens.experiments import cross_validate_logistic_regression


def main() -> None:
    summary = cross_validate_logistic_regression(load_credit_dataset())

    print("Development-set cross-validation")
    for name, value in asdict(summary).items():
        if isinstance(value, float):
            print(f"{name}: {value:.3f}")
        else:
            print(f"{name}: {value}")


if __name__ == "__main__":
    main()


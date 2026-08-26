"""Evaluate random-forest calibration and select a review threshold."""

from dataclasses import asdict

from trustlens.calibration import analyse_random_forest_calibration
from trustlens.data import load_credit_dataset


def main() -> None:
    summary = analyse_random_forest_calibration(load_credit_dataset())
    print("Random-forest probability calibration")
    for name, value in asdict(summary).items():
        if isinstance(value, float):
            print(f"{name}: {value:.3f}")
        else:
            print(f"{name}: {value}")


if __name__ == "__main__":
    main()

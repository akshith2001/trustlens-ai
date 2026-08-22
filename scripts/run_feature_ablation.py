"""Compare the full model with a sensitive-feature-restricted model."""

from trustlens.data import load_credit_dataset
from trustlens.experiments import (
    cross_validate_random_forest,
    cross_validate_restricted_random_forest,
)


def main() -> None:
    dataset = load_credit_dataset()
    results = [
        cross_validate_random_forest(dataset),
        cross_validate_restricted_random_forest(dataset),
    ]
    print("Excluded in restricted model: age_years, personal_status_sex, foreign_worker")
    print(
        f"{'model':42} {'bal_acc':>8} {'precision':>10} "
        f"{'recall':>8} {'f1':>8} {'cost':>8}"
    )
    for result in results:
        print(
            f"{result.model_name:42} "
            f"{result.balanced_accuracy_mean:8.3f} "
            f"{result.precision_mean:10.3f} "
            f"{result.recall_mean:8.3f} "
            f"{result.f1_mean:8.3f} "
            f"{result.weighted_error_cost_mean:8.1f}"
        )
    print("Feature removal does not by itself prove or guarantee fairness.")


if __name__ == "__main__":
    main()


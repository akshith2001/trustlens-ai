"""Compare ordinary and cost-sensitive logistic regression fairly."""

from trustlens.data import load_credit_dataset
from trustlens.experiments import cross_validate_logistic_regression


def main() -> None:
    dataset = load_credit_dataset()
    summaries = [
        cross_validate_logistic_regression(dataset, cost_sensitive=False),
        cross_validate_logistic_regression(dataset, cost_sensitive=True),
    ]

    header = (
        f"{'model':38} {'bal_acc':>8} {'precision':>10} "
        f"{'recall':>8} {'f1':>8} {'cost':>8}"
    )
    print(header)
    print("-" * len(header))
    for result in summaries:
        print(
            f"{result.model_name:38} "
            f"{result.balanced_accuracy_mean:8.3f} "
            f"{result.precision_mean:10.3f} "
            f"{result.recall_mean:8.3f} "
            f"{result.f1_mean:8.3f} "
            f"{result.weighted_error_cost_mean:8.1f}"
        )


if __name__ == "__main__":
    main()


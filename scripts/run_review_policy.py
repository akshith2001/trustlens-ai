"""Evaluate human-review budgets for borderline model predictions."""

from trustlens.data import load_credit_dataset
from trustlens.review_policy import analyse_review_budgets


def main() -> None:
    results = analyse_review_budgets(load_credit_dataset())
    header = (
        f"{'review':>8} {'coverage':>10} {'records':>8} "
        f"{'errors_captured':>16} {'remaining_cost':>15} {'cost_reduction':>15}"
    )
    print(header)
    print("-" * len(header))
    for result in results:
        print(
            f"{result.review_budget:8.0%} "
            f"{result.automated_coverage:10.0%} "
            f"{result.records_reviewed:8d} "
            f"{result.error_capture_rate:16.1%} "
            f"{result.remaining_weighted_error_cost:15d} "
            f"{result.potential_cost_reduction:15.1%}"
        )


if __name__ == "__main__":
    main()

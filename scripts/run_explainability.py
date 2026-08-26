"""Report validation-based global feature importance."""

from trustlens.data import load_credit_dataset
from trustlens.explainability import cross_validated_permutation_importance


def main() -> None:
    results = cross_validated_permutation_importance(load_credit_dataset())
    print("Cross-validated permutation importance")
    print(f"{'rank':>4} {'feature':30} {'mean_drop':>10} {'std':>10}")
    for rank, result in enumerate(results, start=1):
        print(
            f"{rank:4d} {result.feature:30} "
            f"{result.balanced_accuracy_drop_mean:10.4f} "
            f"{result.balanced_accuracy_drop_std:10.4f}"
        )


if __name__ == "__main__":
    main()

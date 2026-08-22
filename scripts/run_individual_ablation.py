"""Measure the individual contribution of sensitive or ambiguous inputs."""

from trustlens.data import load_credit_dataset
from trustlens.experiments import (
    cross_validate_random_forest,
    cross_validate_random_forest_excluding,
)


def main() -> None:
    dataset = load_credit_dataset()
    configurations = [
        ("full_model", frozenset()),
        ("without_personal_status_sex", frozenset({"personal_status_sex"})),
        ("without_age", frozenset({"age_years"})),
        ("without_foreign_worker", frozenset({"foreign_worker"})),
        (
            "without_status_sex_and_worker",
            frozenset({"personal_status_sex", "foreign_worker"}),
        ),
        (
            "without_all_three",
            frozenset({"age_years", "personal_status_sex", "foreign_worker"}),
        ),
    ]
    results = []
    for name, excluded in configurations:
        if not excluded:
            result = cross_validate_random_forest(dataset)
        else:
            result = cross_validate_random_forest_excluding(
                dataset=dataset,
                excluded_features=excluded,
                model_name=name,
            )
        results.append((name, result))

    print(
        f"{'configuration':30} {'bal_acc':>8} {'precision':>10} "
        f"{'recall':>8} {'f1':>8} {'cost':>8}"
    )
    for name, result in results:
        print(
            f"{name:30} {result.balanced_accuracy_mean:8.3f} "
            f"{result.precision_mean:10.3f} {result.recall_mean:8.3f} "
            f"{result.f1_mean:8.3f} {result.weighted_error_cost_mean:8.1f}"
        )


if __name__ == "__main__":
    main()

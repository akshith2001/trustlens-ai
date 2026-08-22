"""Run development-set subgroup diagnostics and assessability checks."""

from trustlens.data import load_credit_dataset
from trustlens.fairness import audit_credit_subgroups


def display_group(title: str, results) -> None:
    print(title)
    print(
        f"{'group':20} {'n':>5} {'observed':>10} {'warnings':>10} "
        f"{'recall (95% CI)':>23} {'fpr (95% CI)':>23}"
    )
    for result in results:
        recall = (
            "N/A"
            if result.recall is None
            else (
                f"{result.recall:.3f} "
                f"[{result.recall_interval[0]:.3f}, "
                f"{result.recall_interval[1]:.3f}]"
            )
        )
        fpr = (
            "N/A"
            if result.false_positive_rate is None
            else (
                f"{result.false_positive_rate:.3f} "
                f"[{result.false_positive_interval[0]:.3f}, "
                f"{result.false_positive_interval[1]:.3f}]"
            )
        )
        print(
            f"{result.group:20} {result.records:5d} "
            f"{result.observed_higher_risk_rate:10.3f} "
            f"{result.warning_rate:10.3f} {recall:>23} {fpr:>23}"
        )


def main() -> None:
    audit = audit_credit_subgroups(load_credit_dataset())
    print(f"Gender fairness: {audit.gender_status}")
    print(f"Reason: {audit.gender_reason}")
    display_group("Age-band diagnostics", audit.age_results)
    display_group(
        "Recorded foreign-worker-code diagnostics",
        audit.foreign_worker_code_results,
    )
    print("These are exploratory diagnostics, not proof of fairness or discrimination.")


if __name__ == "__main__":
    main()

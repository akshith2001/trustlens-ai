"""Display a local model-sensitivity explanation."""

from trustlens.data import load_credit_dataset
from trustlens.local_explanation import explain_validation_record


def main() -> None:
    explanation = explain_validation_record(load_credit_dataset())
    print(f"original_probability: {explanation.original_probability:.3f}")
    print(f"governed_threshold: {explanation.threshold:.3f}")
    print(f"predicted_class: {explanation.predicted_class}")
    print("Top local sensitivity effects")
    print(f"{'feature':30} {'observed':>12} {'reference':>12} {'prob_change':>12}")
    for effect in explanation.effects[:10]:
        print(
            f"{effect.feature:30} {effect.observed_value:>12} "
            f"{effect.reference_value:>12} {effect.probability_change:12.4f}"
        )
    print(explanation.warning)


if __name__ == "__main__":
    main()

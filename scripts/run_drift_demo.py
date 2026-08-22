"""Demonstrate normal monitoring and controlled synthetic drift."""

from sklearn.model_selection import train_test_split

from trustlens.baseline import RANDOM_STATE
from trustlens.data import load_credit_dataset
from trustlens.drift import detect_covariate_drift


def show(label: str, result) -> None:
    print(label)
    print(f"  adversarial_auc_mean: {result.adversarial_auc_mean:.3f}")
    print(f"  adversarial_auc_std: {result.adversarial_auc_std:.3f}")
    print(f"  drift_detected: {result.drift_detected}")
    print(f"  action: {result.action}")


def main() -> None:
    dataset = load_credit_dataset()
    reference, incoming = train_test_split(
        dataset.features,
        test_size=0.5,
        random_state=RANDOM_STATE,
        stratify=dataset.target,
    )
    no_shift = detect_covariate_drift(reference, incoming)

    shifted = incoming.copy()
    shifted["duration_months"] = shifted["duration_months"] + 12
    shifted["credit_amount"] = shifted["credit_amount"] * 1.5
    controlled_shift = detect_covariate_drift(reference, shifted)

    show("Random holdout", no_shift)
    show("Controlled synthetic shift", controlled_shift)
    print("Synthetic shifts are evaluation fixtures, not observed real-world data.")


if __name__ == "__main__":
    main()


"""Display the verified structure of the first TrustLens case study."""

from trustlens.data import load_credit_dataset


def main() -> None:
    dataset = load_credit_dataset()

    print("South German Credit dataset")
    print(f"Rows: {len(dataset.features)}")
    print(f"Features: {dataset.features.shape[1]}")
    print(f"Missing values: {dataset.features.isna().sum().sum()}")
    print("Target counts:")
    print(dataset.target.value_counts().sort_index().to_string())
    print("Target meaning: 0 = lower risk, 1 = higher risk")
    print("Feature names:")
    print(", ".join(dataset.features.columns))


if __name__ == "__main__":
    main()

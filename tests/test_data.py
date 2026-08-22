import pandas as pd

from trustlens.data import CreditDataset


def test_credit_dataset_holds_features_and_target() -> None:
    features = pd.DataFrame({"duration": [12, 24]})
    target = pd.Series([0, 1], name="credit_risk")

    dataset = CreditDataset(features=features, target=target)

    assert dataset.features.shape == (2, 1)
    assert dataset.target.tolist() == [0, 1]

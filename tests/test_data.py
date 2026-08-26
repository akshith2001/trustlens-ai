import pandas as pd
import pytest

from trustlens.data import CreditDataset, load_credit_dataset


def test_credit_dataset_holds_features_and_target() -> None:
    features = pd.DataFrame({"duration": [12, 24]})
    target = pd.Series([0, 1], name="credit_risk")

    dataset = CreditDataset(features=features, target=target)

    assert dataset.features.shape == (2, 1)
    assert dataset.target.tolist() == [0, 1]


def test_corrupted_cached_archive_is_rejected(tmp_path) -> None:
    archive_path = tmp_path / "south_german_credit.zip"
    archive_path.write_bytes(b"not the locked research dataset")

    with pytest.raises(ValueError, match="checksum mismatch"):
        load_credit_dataset(archive_path)

from hashlib import sha256
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
import pandas as pd
import pytest

from trustlens.baseline import evaluate_majority_baseline
from trustlens.calibration import development_data, select_cost_sensitive_threshold
from trustlens.data import (
    ARCHIVE_MEMBER,
    COLUMN_NAMES,
    CreditDataset,
    load_credit_dataset,
)
from trustlens.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES
from trustlens.local_explanation import _reference_values
from trustlens.ood import fit_ood_detector, flag_ood_records
from trustlens.review_policy import select_review_cases


def _small_dataset() -> CreditDataset:
    features = pd.DataFrame({"feature": np.arange(20)})
    target = pd.Series([0] * 14 + [1] * 6, name="higher_risk")
    return CreditDataset(features=features, target=target)


def test_majority_baseline_and_development_split() -> None:
    dataset = _small_dataset()

    baseline = evaluate_majority_baseline(dataset)
    development_features, development_target = development_data(dataset)

    assert baseline.false_negatives > 0
    assert baseline.true_positives == 0
    assert len(development_features) == len(development_target) == 16


def test_threshold_selection_prefers_lower_weighted_cost() -> None:
    actual = np.array([0, 0, 1, 1])
    probabilities = np.array([0.1, 0.4, 0.3, 0.9])

    threshold, metrics = select_cost_sensitive_threshold(actual, probabilities)

    assert 0.0 < threshold < 1.0
    assert metrics.weighted_error_cost == 1


def test_local_reference_values_exclude_governed_features() -> None:
    frame = pd.DataFrame(
        {
            **{name: [1, 2, 3] for name in NUMERIC_FEATURES},
            **{name: [1, 1, 2] for name in CATEGORICAL_FEATURES},
        }
    )

    references = _reference_values(frame)

    assert references["duration_months"] == 2
    assert references["checking_account_status"] == 1
    assert "personal_status_sex" not in references


def test_ood_detector_flags_records_with_expected_shape() -> None:
    reference = pd.DataFrame({name: np.linspace(0, 1, 40) for name in NUMERIC_FEATURES})
    scaler, detector = fit_ood_detector(reference, contamination=0.1)

    flags = flag_ood_records(scaler, detector, reference.iloc[:5])

    assert flags.dtype == bool
    assert flags.shape == (5,)


def test_review_budget_validation_and_zero_selection() -> None:
    probabilities = np.array([0.1, 0.2, 0.3])

    assert not select_review_cases(probabilities, 0.2, 0.0).any()
    with pytest.raises(ValueError, match="below 1"):
        select_review_cases(probabilities, 0.2, 1.0)


def test_valid_archive_is_parsed_after_checksum_verification(
    tmp_path, monkeypatch
) -> None:
    source_columns = list(COLUMN_NAMES)
    rows = []
    for index in range(1_000):
        values = [str((index + offset) % 4 + 1) for offset in range(20)]
        rows.append(" ".join(values + [str(index % 2)]))
    content = (" ".join(source_columns + ["kredit"]) + "\n" + "\n".join(rows)).encode()
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr(ARCHIVE_MEMBER, content)
    archive_bytes = buffer.getvalue()
    monkeypatch.setattr(
        "trustlens.data.ARCHIVE_SHA256", sha256(archive_bytes).hexdigest()
    )
    path = tmp_path / "dataset.zip"
    path.write_bytes(archive_bytes)

    dataset = load_credit_dataset(path)

    assert dataset.features.shape == (1_000, 20)
    assert dataset.target.value_counts().to_dict() == {1: 500, 0: 500}

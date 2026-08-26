"""Dataset loading and validation for the TrustLens case studies."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

import pandas as pd

SOUTH_GERMAN_CREDIT_DATASET_ID = 573
DATASET_ARCHIVE_URL = (
    "https://archive.ics.uci.edu/static/public/573/south%2Bgerman%2Bcredit%2Bupdate.zip"
)
ARCHIVE_MEMBER = "SouthGermanCredit.asc"
ARCHIVE_SHA256 = "0b40d40eb7321693d559e247a556f88a6cc8df8489c3cb2ae084db7592584551"
EXPECTED_ROWS = 1_000
EXPECTED_FEATURES = 20
COLUMN_NAMES = {
    "laufkont": "checking_account_status",
    "laufzeit": "duration_months",
    "moral": "credit_history",
    "verw": "purpose",
    "hoehe": "credit_amount",
    "sparkont": "savings",
    "beszeit": "employment_duration",
    "rate": "installment_rate",
    "famges": "personal_status_sex",
    "buerge": "other_debtors",
    "wohnzeit": "present_residence",
    "verm": "property",
    "alter": "age_years",
    "weitkred": "other_installment_plans",
    "wohn": "housing",
    "bishkred": "number_credits",
    "beruf": "job",
    "pers": "people_liable",
    "telef": "telephone",
    "gastarb": "foreign_worker",
}


@dataclass(frozen=True)
class CreditDataset:
    """Validated features and target from the credit-risk case study."""

    features: pd.DataFrame
    target: pd.Series


def _default_cache_path() -> Path:
    return (
        Path(__file__).resolve().parents[2] / "data" / "raw" / "south_german_credit.zip"
    )


def _download_archive(cache_path: Path) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(DATASET_ARCHIVE_URL, timeout=30) as response:  # noqa: S310
        archive_bytes = response.read()
    _validate_archive_bytes(archive_bytes)
    cache_path.write_bytes(archive_bytes)


def _validate_archive_bytes(archive_bytes: bytes) -> None:
    """Reject data that do not match the research artifact used by TrustLens."""

    digest = sha256(archive_bytes).hexdigest()
    if digest != ARCHIVE_SHA256:
        raise ValueError(
            "South German Credit archive checksum mismatch: "
            f"received {digest}, expected {ARCHIVE_SHA256}"
        )


def load_credit_dataset(cache_path: Path | None = None) -> CreditDataset:
    """Download once, load, and validate the South German Credit dataset.

    The loader intentionally fails when the received data do not match the
    documented shape. Silent schema changes would undermine reproducibility.
    """

    archive_path = cache_path or _default_cache_path()
    if not archive_path.exists():
        _download_archive(archive_path)

    _validate_archive_bytes(archive_path.read_bytes())

    with ZipFile(archive_path) as archive:
        with archive.open(ARCHIVE_MEMBER) as data_file:
            frame = pd.read_csv(data_file, sep=r"\s+")

    if "kredit" not in frame.columns:
        raise ValueError("Expected target column 'kredit' was not found")

    raw_target = frame["kredit"]
    if set(raw_target.unique()) != {0, 1}:
        raise ValueError("Expected source target values 0 and 1")

    features = frame.drop(columns="kredit").rename(columns=COLUMN_NAMES).copy()
    # UCI source: 0 = bad/higher risk and 1 = good/lower risk. TrustLens
    # treats the higher-risk outcome as the positive class for clear recall
    # and false-negative reporting.
    target = raw_target.map({0: 1, 1: 0}).rename("higher_risk")

    if features.shape != (EXPECTED_ROWS, EXPECTED_FEATURES):
        raise ValueError(
            "Unexpected feature shape: "
            f"received {features.shape}, expected "
            f"({EXPECTED_ROWS}, {EXPECTED_FEATURES})"
        )
    if len(target) != EXPECTED_ROWS:
        raise ValueError(
            f"Unexpected target length: received {len(target)}, "
            f"expected {EXPECTED_ROWS}"
        )
    if features.isna().any().any() or target.isna().any():
        raise ValueError("The dataset unexpectedly contains missing values")
    if target.nunique() != 2:
        raise ValueError("Credit risk must have exactly two target classes")

    return CreditDataset(features=features, target=target)

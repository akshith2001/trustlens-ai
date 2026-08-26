"""Privacy-aware, hash-chained governance audit records."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

AUDIT_SCHEMA_VERSION = "1.0"
GENESIS_HASH = "0" * 64


@dataclass(frozen=True)
class GovernanceAuditRecord:
    """One append-only governance event without raw personal features."""

    schema_version: str
    record_id: str
    timestamp_utc: str
    model_name: str
    model_version: str
    input_digest: str
    probability: float
    drift_auc: float
    is_out_of_distribution: bool
    action: str
    reason: str
    previous_record_hash: str
    record_hash: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def digest_input(features: dict[str, object], *, salt: str) -> str:
    """Digest canonical input data so the audit log does not store raw values."""

    if not salt:
        raise ValueError("A non-empty deployment-specific salt is required")
    canonical = json.dumps(features, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(f"{salt}:{canonical}".encode()).hexdigest()


def _record_hash(payload: dict[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def create_audit_record(
    *,
    record_id: str,
    timestamp_utc: str,
    model_name: str,
    model_version: str,
    input_digest: str,
    probability: float,
    drift_auc: float,
    is_out_of_distribution: bool,
    action: str,
    reason: str,
    previous_record_hash: str = GENESIS_HASH,
) -> GovernanceAuditRecord:
    """Create a validated record whose hash commits to all prior fields."""

    if not record_id or not model_name or not model_version or not reason:
        raise ValueError("record, model, version and reason fields must be non-empty")
    if len(input_digest) != 64 or len(previous_record_hash) != 64:
        raise ValueError(
            "input and previous-record digests must be SHA-256 hex strings"
        )
    try:
        int(input_digest, 16)
        int(previous_record_hash, 16)
        parsed_timestamp = datetime.fromisoformat(timestamp_utc.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("Invalid digest or ISO-8601 timestamp") from error
    if parsed_timestamp.utcoffset() is None:
        raise ValueError("timestamp_utc must include a UTC offset")
    if not 0.0 <= probability <= 1.0 or not 0.0 <= drift_auc <= 1.0:
        raise ValueError("probability and drift_auc must be between 0 and 1")

    payload: dict[str, object] = {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "record_id": record_id,
        "timestamp_utc": timestamp_utc,
        "model_name": model_name,
        "model_version": model_version,
        "input_digest": input_digest,
        "probability": probability,
        "drift_auc": drift_auc,
        "is_out_of_distribution": is_out_of_distribution,
        "action": action,
        "reason": reason,
        "previous_record_hash": previous_record_hash,
    }
    return GovernanceAuditRecord(**payload, record_hash=_record_hash(payload))


def verify_audit_chain(records: list[GovernanceAuditRecord]) -> bool:
    """Return whether record content and previous-hash links are intact."""

    expected_previous = GENESIS_HASH
    for record in records:
        payload = record.to_dict()
        observed_hash = str(payload.pop("record_hash"))
        if record.previous_record_hash != expected_previous:
            return False
        if _record_hash(payload) != observed_hash:
            return False
        expected_previous = observed_hash
    return True


def append_audit_record(path: Path, record: GovernanceAuditRecord) -> None:
    """Append one canonical JSON Lines record after validating the existing chain."""

    existing: list[GovernanceAuditRecord] = []
    if path.exists():
        existing = [
            GovernanceAuditRecord(**json.loads(line))
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    if not verify_audit_chain(existing):
        raise ValueError("Existing audit chain failed integrity verification")
    expected_previous = existing[-1].record_hash if existing else GENESIS_HASH
    if record.previous_record_hash != expected_previous:
        raise ValueError("New record does not extend the current audit chain")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")

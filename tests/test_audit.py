from dataclasses import replace

import pytest

from trustlens.audit import (
    GENESIS_HASH,
    append_audit_record,
    create_audit_record,
    digest_input,
    verify_audit_chain,
)


def _record(previous_hash: str = GENESIS_HASH):
    return create_audit_record(
        record_id="event-1",
        timestamp_utc="2026-08-26T12:00:00Z",
        model_name="governed_model",
        model_version="0.2.0",
        input_digest=digest_input({"feature": 1}, salt="test-salt"),
        probability=0.42,
        drift_auc=0.51,
        is_out_of_distribution=False,
        action="human_review_required",
        reason="Higher-risk warning requires review.",
        previous_record_hash=previous_hash,
    )


def test_input_digest_is_canonical_and_salted() -> None:
    assert digest_input({"b": 2, "a": 1}, salt="x") == digest_input(
        {"a": 1, "b": 2}, salt="x"
    )
    assert digest_input({"a": 1}, salt="x") != digest_input({"a": 1}, salt="y")


def test_audit_chain_detects_content_tampering() -> None:
    first = _record()
    valid_second = create_audit_record(
        record_id="event-2",
        timestamp_utc="2026-08-26T12:01:00Z",
        model_name="governed_model",
        model_version="0.2.0",
        input_digest=digest_input({"feature": 2}, salt="test-salt"),
        probability=0.10,
        drift_auc=0.51,
        is_out_of_distribution=False,
        action="continue_with_monitoring",
        reason="No locked trigger fired.",
        previous_record_hash=first.record_hash,
    )

    assert verify_audit_chain([first, valid_second])
    assert not verify_audit_chain([first, replace(valid_second, reason="tampered")])


def test_records_append_as_verified_json_lines(tmp_path) -> None:
    path = tmp_path / "audit.jsonl"
    first = _record()
    second = create_audit_record(
        record_id="event-2",
        timestamp_utc="2026-08-26T12:01:00Z",
        model_name="governed_model",
        model_version="0.2.0",
        input_digest=digest_input({"feature": 2}, salt="test-salt"),
        probability=0.10,
        drift_auc=0.51,
        is_out_of_distribution=False,
        action="continue_with_monitoring",
        reason="No locked trigger fired.",
        previous_record_hash=first.record_hash,
    )

    append_audit_record(path, first)
    append_audit_record(path, second)

    assert len(path.read_text(encoding="utf-8").splitlines()) == 2


def test_invalid_audit_values_are_rejected() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        create_audit_record(
            record_id="event",
            timestamp_utc="2026-08-26T12:00:00Z",
            model_name="model",
            model_version="1",
            input_digest="a" * 64,
            probability=1.1,
            drift_auc=0.5,
            is_out_of_distribution=False,
            action="review",
            reason="reason",
        )

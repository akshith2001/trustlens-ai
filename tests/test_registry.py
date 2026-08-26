import json

import pytest

from trustlens.registry import ExperimentLedger, FileRegistry


def test_registry_persists_and_rejects_duplicates(tmp_path) -> None:
    registry = FileRegistry(tmp_path / "registry.json")
    assert registry.list_models() == []
    entry = registry.register(name="risk", version="1", artifact=b"model")
    assert registry.list_models() == [entry]
    assert len(entry.artifact_sha256) == 64
    with pytest.raises(ValueError, match="already exists"):
        registry.register(name="risk", version="1", artifact=b"other")
    with pytest.raises(ValueError, match="invalid model stage"):
        registry.register(name="risk", version="2", artifact=b"x", stage="live")


def test_experiment_ledger_is_jsonl(tmp_path) -> None:
    ledger = ExperimentLedger(tmp_path / "runs.jsonl")
    record = ledger.log(
        run_name="benchmark", parameters={"folds": 5}, metrics={"auc": 0.8}
    )
    assert json.loads(ledger.path.read_text())["metrics"] == {"auc": 0.8}
    assert record["schema_version"] == "1.0"
    with pytest.raises(ValueError):
        ledger.log(run_name="", parameters={}, metrics={})
    with pytest.raises(ValueError):
        ledger.log(run_name="bad", parameters={}, metrics={"auc": "high"})

"""Small, auditable model registry and experiment ledger."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class ModelVersion:
    name: str
    version: str
    artifact_sha256: str
    stage: str
    created_at: str
    metadata: dict[str, object]


class FileRegistry:
    """Persist model metadata without storing model inputs or credentials."""

    def __init__(self, path: Path):
        self.path = path

    def list_models(self) -> list[ModelVersion]:
        if not self.path.exists():
            return []
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return [ModelVersion(**item) for item in payload]

    def register(
        self,
        *,
        name: str,
        version: str,
        artifact: bytes,
        stage: str = "candidate",
        metadata: dict[str, object] | None = None,
    ) -> ModelVersion:
        if not name.strip() or not version.strip():
            raise ValueError("name and version are required")
        if stage not in {"candidate", "validated", "archived"}:
            raise ValueError("invalid model stage")
        models = self.list_models()
        if any(item.name == name and item.version == version for item in models):
            raise ValueError("model version already exists")
        entry = ModelVersion(
            name=name,
            version=version,
            artifact_sha256=hashlib.sha256(artifact).hexdigest(),
            stage=stage,
            created_at=datetime.now(UTC).isoformat(),
            metadata=metadata or {},
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(
                [asdict(item) for item in (*models, entry)],
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return entry


class ExperimentLedger:
    """Append-only JSONL experiment records suitable for later MLflow import."""

    def __init__(self, path: Path):
        self.path = path

    def log(
        self,
        *,
        run_name: str,
        parameters: dict[str, object],
        metrics: dict[str, float],
        artifact_sha256: str | None = None,
    ) -> dict[str, object]:
        if not run_name.strip():
            raise ValueError("run_name is required")
        if not all(isinstance(value, (int, float)) for value in metrics.values()):
            raise ValueError("metrics must be numeric")
        record = {
            "schema_version": "1.0",
            "run_name": run_name,
            "recorded_at": datetime.now(UTC).isoformat(),
            "parameters": parameters,
            "metrics": metrics,
            "artifact_sha256": artifact_sha256,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")
        return record

"""Reproducible, synthetic materials for the unrun TrustLens usability pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from trustlens.governance import (
    GOVERNED_DECISION_THRESHOLD,
    determine_governance_action,
)

CATEGORIES = {
    "reliable_lower_risk",
    "reliable_higher_risk",
    "borderline_uncertainty",
    "drift_or_ood",
    "fairness_or_data_limitation",
}
ACTIONS = {
    "continue_with_monitoring",
    "human_review_required",
    "pause_and_investigate",
}
ARMS = {"score", "explain", "contract"}


@dataclass(frozen=True)
class Vignette:
    vignette_id: str
    category: str
    title: str
    probability: float
    drift_auc: float
    is_out_of_distribution: bool
    material_limitation: bool
    explanation: tuple[str, ...]
    evidence_contract: dict[str, str]
    expected_action: str


def _derived_action(vignette: Vignette) -> str:
    if vignette.material_limitation:
        return "pause_and_investigate"
    action, _ = determine_governance_action(
        vignette.probability,
        drift_auc=vignette.drift_auc,
        is_out_of_distribution=vignette.is_out_of_distribution,
    )
    if action == "pause_for_human_review":
        return "human_review_required"
    return action


def load_vignettes(path: Path) -> tuple[Vignette, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "synthetic_study_materials_not_yet_run":
        raise ValueError("pilot status must state that the study has not been run")
    records = tuple(
        Vignette(
            vignette_id=item["id"],
            category=item["category"],
            title=item["title"],
            probability=float(item["probability"]),
            drift_auc=float(item["drift_auc"]),
            is_out_of_distribution=bool(item["is_out_of_distribution"]),
            material_limitation=bool(item["material_limitation"]),
            explanation=tuple(item["explanation"]),
            evidence_contract=dict(item["evidence_contract"]),
            expected_action=item["expected_action"],
        )
        for item in payload["vignettes"]
    )
    if len(records) != 15:
        raise ValueError("the locked pilot bank must contain exactly 15 vignettes")
    if len({record.vignette_id for record in records}) != len(records):
        raise ValueError("vignette identifiers must be unique")
    counts = Counter(record.category for record in records)
    if set(counts) != CATEGORIES or set(counts.values()) != {3}:
        raise ValueError("the pilot bank must contain three cases in each category")
    for record in records:
        if not 0 <= record.probability <= 1 or not 0 <= record.drift_auc <= 1:
            raise ValueError(f"invalid probability in {record.vignette_id}")
        if record.expected_action not in ACTIONS:
            raise ValueError(f"invalid expected action in {record.vignette_id}")
        if _derived_action(record) != record.expected_action:
            raise ValueError(f"scoring key conflicts with governance policy in {record.vignette_id}")
        required = {
            "provenance",
            "uncertainty",
            "limitations",
            "permitted_interpretation",
            "required_action",
        }
        if set(record.evidence_contract) != required:
            raise ValueError(f"incomplete evidence contract in {record.vignette_id}")
    return records


def render_vignette(vignette: Vignette, arm: str) -> dict[str, Any]:
    """Return exactly the information visible to one experimental arm."""
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {sorted(ARMS)}")
    rendered: dict[str, Any] = {
        "id": vignette.vignette_id,
        "title": vignette.title,
        "probability": vignette.probability,
        "predicted_class": (
            "higher_risk_warning"
            if vignette.probability >= GOVERNED_DECISION_THRESHOLD
            else "lower_risk_signal"
        ),
    }
    if arm in {"explain", "contract"}:
        rendered["explanation"] = list(vignette.explanation)
    if arm == "contract":
        rendered["evidence_contract"] = vignette.evidence_contract
    return rendered


def score_action(vignette: Vignette, selected_action: str) -> dict[str, bool]:
    if selected_action not in ACTIONS:
        raise ValueError(f"selected_action must be one of {sorted(ACTIONS)}")
    correct = selected_action == vignette.expected_action
    critical_error = selected_action == "continue_with_monitoring" and vignette.expected_action == "pause_and_investigate"
    return {"correct": correct, "critical_error": critical_error}


def build_manifest(path: Path) -> dict[str, Any]:
    vignettes = load_vignettes(path)
    return {
        "status": "designed_not_run",
        "vignette_count": len(vignettes),
        "category_counts": dict(sorted(Counter(item.category for item in vignettes).items())),
        "arms": {
            arm: sorted(render_vignette(vignettes[0], arm))
            for arm in ("score", "explain", "contract")
        },
        "locked_threshold": GOVERNED_DECISION_THRESHOLD,
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "publication_boundary": "No participant data have been collected and no effectiveness claim is supported.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vignettes", type=Path, default=Path("data/pilot_vignettes.json"))
    parser.add_argument("--output", type=Path, default=Path("results/pilot_vignette_manifest.json"))
    args = parser.parse_args()
    manifest = build_manifest(args.vignettes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

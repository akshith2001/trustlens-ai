import json
from pathlib import Path

import pytest

from trustlens.human_factors import (
    build_manifest,
    load_vignettes,
    render_vignette,
    score_action,
)

DATA = Path("data/pilot_vignettes.json")


def test_locked_bank_has_three_cases_per_category() -> None:
    manifest = build_manifest(DATA)
    assert manifest["vignette_count"] == 15
    assert set(manifest["category_counts"].values()) == {3}
    assert manifest["status"] == "designed_not_run"


def test_arm_rendering_only_adds_declared_evidence() -> None:
    vignette = load_vignettes(DATA)[0]
    score = render_vignette(vignette, "score")
    explain = render_vignette(vignette, "explain")
    contract = render_vignette(vignette, "contract")
    assert "explanation" not in score
    assert "explanation" in explain
    assert "evidence_contract" not in explain
    assert "evidence_contract" in contract
    assert "expected_action" not in contract


def test_scoring_records_critical_continue_error() -> None:
    vignette = next(item for item in load_vignettes(DATA) if item.vignette_id == "D01")
    assert score_action(vignette, "continue_with_monitoring") == {
        "correct": False,
        "critical_error": True,
    }


def test_invalid_arm_is_rejected() -> None:
    with pytest.raises(ValueError, match="arm"):
        render_vignette(load_vignettes(DATA)[0], "unknown")


def test_status_cannot_imply_completed_study(tmp_path: Path) -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    payload["status"] = "completed"
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="not been run"):
        load_vignettes(path)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda payload: payload["vignettes"].pop(), "exactly 15"),
        (
            lambda payload: payload["vignettes"][1].update(
                {"id": payload["vignettes"][0]["id"]}
            ),
            "unique",
        ),
        (
            lambda payload: payload["vignettes"][0].update(
                {"category": "unknown"}
            ),
            "three cases",
        ),
        (
            lambda payload: payload["vignettes"][0].update({"probability": 2}),
            "invalid probability",
        ),
        (
            lambda payload: payload["vignettes"][0].update(
                {"expected_action": "approve"}
            ),
            "invalid expected action",
        ),
        (
            lambda payload: payload["vignettes"][0].update(
                {"expected_action": "human_review_required"}
            ),
            "conflicts",
        ),
        (
            lambda payload: payload["vignettes"][0]["evidence_contract"].pop(
                "limitations"
            ),
            "incomplete evidence contract",
        ),
    ],
)
def test_structural_errors_are_rejected(
    tmp_path: Path, mutation: object, message: str
) -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    mutation(payload)  # type: ignore[operator]
    path = tmp_path / "bad-structure.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        load_vignettes(path)


def test_invalid_selected_action_is_rejected() -> None:
    with pytest.raises(ValueError, match="selected_action"):
        score_action(load_vignettes(DATA)[0], "approve")

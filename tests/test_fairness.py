from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from scripts import run_fairness_audit
from trustlens.fairness import (
    GENDER_ASSESSABILITY_REASON,
    GENDER_ASSESSABILITY_STATUS,
    subgroup_metrics,
    wilson_interval,
)


def test_subgroup_metrics_report_recall_and_false_positive_rate() -> None:
    actual = np.array([0, 1, 0, 1])
    predicted = np.array([1, 1, 0, 0])
    groups = pd.Series(["a", "a", "b", "b"])

    results = {
        result.group: result for result in subgroup_metrics(actual, predicted, groups)
    }

    assert results["a"].recall == 1.0
    assert results["a"].false_positive_rate == 1.0
    assert results["b"].recall == 0.0
    assert results["b"].false_positive_rate == 0.0


def test_wilson_interval_is_wider_for_smaller_samples() -> None:
    small = wilson_interval(5, 10)
    large = wilson_interval(50, 100)

    assert small is not None and large is not None
    assert (small[1] - small[0]) > (large[1] - large[0])


def test_fairness_cli_does_not_log_unexpected_metadata(monkeypatch, capsys) -> None:
    monkeypatch.setattr(run_fairness_audit, "load_credit_dataset", lambda: object())
    monkeypatch.setattr(
        run_fairness_audit,
        "audit_credit_subgroups",
        lambda _: SimpleNamespace(
            gender_status="not_assessable",
            gender_reason="private applicant detail",
            age_results=[],
            foreign_worker_code_results=[],
        ),
    )

    with pytest.raises(ValueError, match="Unexpected gender assessability metadata"):
        run_fairness_audit.main()

    assert "private applicant detail" not in capsys.readouterr().out


def test_fairness_cli_reports_fixed_assessability_metadata(monkeypatch, capsys) -> None:
    monkeypatch.setattr(run_fairness_audit, "load_credit_dataset", lambda: object())
    monkeypatch.setattr(
        run_fairness_audit,
        "audit_credit_subgroups",
        lambda _: SimpleNamespace(
            gender_status=GENDER_ASSESSABILITY_STATUS,
            gender_reason=GENDER_ASSESSABILITY_REASON,
            age_results=[],
            foreign_worker_code_results=[],
        ),
    )

    run_fairness_audit.main()

    output = capsys.readouterr().out
    assert "Gender fairness: not_assessable" in output
    assert f"Reason: {GENDER_ASSESSABILITY_REASON}" in output

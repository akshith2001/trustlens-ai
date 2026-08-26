import json

from trustlens.benchmark import (
    DevelopmentBenchmark,
    RankedCandidate,
    rank_candidates,
    write_benchmark,
)
from trustlens.experiments import CrossValidationSummary


def _summary(
    model_name: str,
    *,
    cost: float,
    balanced_accuracy: float,
) -> CrossValidationSummary:
    return CrossValidationSummary(
        model_name=model_name,
        folds=5,
        balanced_accuracy_mean=balanced_accuracy,
        balanced_accuracy_std=0.01,
        precision_mean=0.4,
        precision_std=0.01,
        recall_mean=0.8,
        recall_std=0.01,
        f1_mean=0.53,
        f1_std=0.01,
        weighted_error_cost_mean=cost,
        weighted_error_cost_std=2.0,
    )


def test_candidates_are_ranked_by_declared_rule() -> None:
    ranked = rank_candidates(
        [
            _summary("higher_cost", cost=30, balanced_accuracy=0.9),
            _summary("lower_balance", cost=20, balanced_accuracy=0.6),
            _summary("winner", cost=20, balanced_accuracy=0.7),
        ]
    )

    assert [candidate.model_name for candidate in ranked] == [
        "winner",
        "lower_balance",
        "higher_cost",
    ]
    assert [candidate.rank for candidate in ranked] == [1, 2, 3]


def test_benchmark_json_is_stable_and_machine_readable(tmp_path) -> None:
    candidate = RankedCandidate(
        rank=1, **vars(_summary("model", cost=20, balanced_accuracy=0.7))
    )
    benchmark = DevelopmentBenchmark(
        schema_version="1.0",
        dataset_name="dataset",
        dataset_sha256="abc",
        random_state=42,
        final_holdout_fraction=0.2,
        ranking_rule="declared rule",
        false_negative_cost=5,
        false_positive_cost=1,
        python_version="3.13.0",
        dependency_versions={"numpy": "2.3.0"},
        candidates=(candidate,),
    )
    output = tmp_path / "benchmark.json"

    write_benchmark(benchmark, output)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert payload["candidates"][0]["model_name"] == "model"
    assert output.read_text(encoding="utf-8").endswith("\n")

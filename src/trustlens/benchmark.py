"""Reproducible development benchmark that never evaluates the final holdout."""

from __future__ import annotations

import argparse
import json
import platform
from collections.abc import Callable
from dataclasses import asdict, dataclass
from importlib.metadata import version
from pathlib import Path

from trustlens.baseline import RANDOM_STATE, TEST_SIZE
from trustlens.data import ARCHIVE_SHA256, CreditDataset, load_credit_dataset
from trustlens.evaluation import FALSE_NEGATIVE_COST, FALSE_POSITIVE_COST
from trustlens.experiments import (
    CrossValidationSummary,
    cross_validate_hist_gradient_boosting,
    cross_validate_logistic_regression,
    cross_validate_random_forest,
)

BENCHMARK_SCHEMA_VERSION = "1.0"
DEFAULT_BENCHMARK_PATH = Path("results/development_benchmark.json")


@dataclass(frozen=True)
class RankedCandidate:
    """One cross-validated candidate with its benchmark rank."""

    rank: int
    model_name: str
    folds: int
    balanced_accuracy_mean: float
    balanced_accuracy_std: float
    precision_mean: float
    precision_std: float
    recall_mean: float
    recall_std: float
    f1_mean: float
    f1_std: float
    weighted_error_cost_mean: float
    weighted_error_cost_std: float


@dataclass(frozen=True)
class DevelopmentBenchmark:
    """Versioned evidence artifact for development-only model comparison."""

    schema_version: str
    dataset_name: str
    dataset_sha256: str
    random_state: int
    final_holdout_fraction: float
    ranking_rule: str
    false_negative_cost: int
    false_positive_cost: int
    python_version: str
    dependency_versions: dict[str, str]
    candidates: tuple[RankedCandidate, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def rank_candidates(
    summaries: list[CrossValidationSummary],
) -> tuple[RankedCandidate, ...]:
    """Rank candidates by cost, then balanced accuracy, then model name."""

    ordered = sorted(
        summaries,
        key=lambda result: (
            result.weighted_error_cost_mean,
            -result.balanced_accuracy_mean,
            result.model_name,
        ),
    )
    return tuple(
        RankedCandidate(rank=index, **asdict(summary))
        for index, summary in enumerate(ordered, start=1)
    )


def run_development_benchmark(
    dataset: CreditDataset,
    *,
    folds: int = 5,
) -> DevelopmentBenchmark:
    """Compare declared candidates using development folds only."""

    benchmark_functions: tuple[
        Callable[[CreditDataset, int], CrossValidationSummary], ...
    ] = (
        lambda data, count: cross_validate_logistic_regression(
            data, folds=count, cost_sensitive=False
        ),
        lambda data, count: cross_validate_logistic_regression(
            data, folds=count, cost_sensitive=True
        ),
        lambda data, count: cross_validate_random_forest(data, folds=count),
        lambda data, count: cross_validate_hist_gradient_boosting(data, folds=count),
    )
    summaries = [function(dataset, folds) for function in benchmark_functions]
    dependencies = {
        package: version(package) for package in ("numpy", "pandas", "scikit-learn")
    }
    return DevelopmentBenchmark(
        schema_version=BENCHMARK_SCHEMA_VERSION,
        dataset_name="UCI South German Credit",
        dataset_sha256=ARCHIVE_SHA256,
        random_state=RANDOM_STATE,
        final_holdout_fraction=TEST_SIZE,
        ranking_rule=(
            "lowest mean weighted error cost; highest mean balanced accuracy; "
            "lexicographic model name"
        ),
        false_negative_cost=FALSE_NEGATIVE_COST,
        false_positive_cost=FALSE_POSITIVE_COST,
        python_version=platform.python_version(),
        dependency_versions=dependencies,
        candidates=rank_candidates(summaries),
    )


def write_benchmark(
    benchmark: DevelopmentBenchmark,
    output_path: Path = DEFAULT_BENCHMARK_PATH,
) -> None:
    """Write stable, reviewable JSON for CI and research comparisons."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(benchmark.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the TrustLens development benchmark without evaluating the "
            "locked final holdout."
        )
    )
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--output", type=Path, default=DEFAULT_BENCHMARK_PATH)
    return parser


def main() -> None:
    args = build_argument_parser().parse_args()
    if args.folds < 2:
        raise SystemExit("--folds must be at least 2")
    benchmark = run_development_benchmark(load_credit_dataset(), folds=args.folds)
    write_benchmark(benchmark, args.output)
    print(f"Wrote development benchmark to {args.output}")


if __name__ == "__main__":
    main()

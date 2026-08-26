import numpy as np

from trustlens.benchmark_suite import (
    bootstrap_interval,
    controlled_datasets,
    run_suite,
)


def test_controlled_datasets_are_deterministic() -> None:
    first = controlled_datasets()
    second = controlled_datasets()

    assert first.keys() == second.keys()
    for name in first:
        assert np.array_equal(first[name][0], second[name][0])
        assert np.array_equal(first[name][1], second[name][1])


def test_bootstrap_interval_contains_mean_estimate() -> None:
    interval = bootstrap_interval(np.arange(20), np.mean, resamples=200)

    assert interval.lower < interval.estimate < interval.upper
    assert interval.estimate == 9.5


def test_smoke_suite_has_shared_schema_and_two_datasets() -> None:
    payload = run_suite(folds=2, resamples=100)

    assert payload["schema_version"] == "1.0"
    assert len(payload["datasets"]) == 2
    assert all(len(dataset["models"]) == 2 for dataset in payload["datasets"])

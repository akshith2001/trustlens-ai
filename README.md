# TrustLens AI

[![Tests](https://github.com/akshith2001/trustlens-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/akshith2001/trustlens-ai/actions/workflows/tests.yml)

Version 0.2.0 · Python 3.11+

**Live research dashboard:**
[trustlens-governance-ai.streamlit.app](https://trustlens-governance-ai.streamlit.app/)

**Research report:**
[TrustLens AI: Human-Governed Machine Learning for Reliability-Aware Risk Classification](reports/TrustLens_AI_Research_Report.pdf)

**One-page research summary:**
[TrustLens AI supervisor brief](reports/TrustLens_AI_One_Page_Research_Summary.pdf)

TrustLens AI is a research prototype for evaluating whether machine-learning
predictions are accurate, calibrated, explainable, and suitable for human
review. The first case study uses historical credit-risk data; a later module
will evaluate computer-vision anomaly detection.

## Research question

Can a human-governed auditing layer combining cost-sensitive evaluation,
uncertainty estimation, drift detection, and explainability identify unreliable
machine-learning outputs more effectively than confidence scores alone?

## Current status

The governed tabular research engine is covered by an automated test suite.
Its locked model was evaluated once on a 200-record holdout. It achieved 0.833
higher-risk recall and reduced the predefined weighted error cost from the
majority baseline's 300 to 123, while also producing 73 false positives. See
[`docs/results.md`](docs/results.md) for the complete, limitation-aware report
and [`MODEL_CARD.md`](MODEL_CARD.md) for intended use, governance and risks.
The results report also includes confidence intervals so the small held-out
sample is not presented with false precision.
Post-hoc error-slice diagnostics also show where the locked model failed on its
historical holdout, without using those findings to retune the model.

## Architecture

The project separates model development, locked final evaluation and runtime
governance. See the rendered pipeline and full methodology in
[`docs/architecture.md`](docs/architecture.md).

## Reproducible development benchmark

TrustLens publishes a versioned, machine-readable comparison of declared model
candidates. The benchmark uses only the development partition; it never opens
or reevaluates the locked final holdout.

```bash
trustlens-benchmark --output results/development_benchmark.json
```

The artifact records the dataset checksum, split seed, error-cost definition,
ranking rule, dependency versions, fold count, metric means and standard
deviations. Candidates are ranked by lowest mean weighted error cost, then
highest mean balanced accuracy, with model name as a deterministic tie-breaker.

The controlled robustness suite adds two deterministic synthetic datasets,
paired model-cost comparisons, 95% bootstrap intervals and a documented
covariate-shift stress test:

```bash
trustlens-benchmark-suite
```

Its results are explicitly not external domain validation. They test the
benchmark machinery under controlled linear, nonlinear, balanced, imbalanced
and shifted conditions without making claims about real people or decisions.
The complete predeclared methodology and interpretation boundary are documented
in [`docs/benchmark_protocol.md`](docs/benchmark_protocol.md).

## Governance audit records

The `trustlens.audit` module creates privacy-aware JSON Lines records that store
a salted input digest rather than raw feature values. Each event commits to the
previous event hash, allowing later verification that the chain was not edited
or reordered. This demonstrates audit mechanics; it is not a production logging
or privacy compliance system.

## Development and citation

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for research-integrity and development
requirements, [`SECURITY.md`](SECURITY.md) for private vulnerability reporting,
and [`CITATION.cff`](CITATION.cff) for citation metadata. Release changes are
recorded in [`CHANGELOG.md`](CHANGELOG.md).

## Safety and scope

This project is an educational research prototype. It must not be used to make
real lending, employment, legal, medical, or security decisions.

## Planned modules

- Tabular credit-risk classification and evaluation
- Confidence calibration and uncertainty-based rejection
- Drift and out-of-distribution detection
- Fairness and explainability analysis
- Evidence-grounded local LLM summaries
- Human review and versioned audit records
- Computer-vision anomaly detection

## Dataset

The first case study uses the UCI South German Credit dataset:
https://doi.org/10.24432/C5QG88

The dataset contains 1,000 historical records from 1973--1975. Its age,
sampling design, and limited demographic encoding are material limitations and
will be treated as audit findings rather than hidden.

The loader verifies the downloaded archive against its locked SHA-256 digest
before parsing it. This prevents an upstream change or corrupted cache from
silently altering the published experiment.


# TrustLens AI

[![Tests](https://github.com/akshith2001/trustlens-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/akshith2001/trustlens-ai/actions/workflows/tests.yml)

**Live research dashboard:**
[trustlens-governance-ai.streamlit.app](https://trustlens-governance-ai.streamlit.app/)

**Research report:**
[TrustLens AI: Human-Governed Machine Learning for Reliability-Aware Risk Classification](reports/TrustLens_AI_Research_Report.pdf)

TrustLens AI is a research prototype for evaluating whether machine-learning
predictions are accurate, calibrated, explainable, and suitable for human
review. The first case study uses historical credit-risk data; a later module
will evaluate computer-vision anomaly detection.

## Research question

Can a human-governed auditing layer combining cost-sensitive evaluation,
uncertainty estimation, drift detection, and explainability identify unreliable
machine-learning outputs more effectively than confidence scores alone?

## Current status

The governed tabular research engine is implemented with 20 automated tests.
Its locked model was evaluated once on a 200-record holdout. It achieved 0.833
higher-risk recall and reduced the predefined weighted error cost from the
majority baseline's 300 to 123, while also producing 73 false positives. See
[`docs/results.md`](docs/results.md) for the complete, limitation-aware report
and [`MODEL_CARD.md`](MODEL_CARD.md) for intended use, governance and risks.
The results report also includes confidence intervals so the small held-out
sample is not presented with false precision.

## Architecture

The project separates model development, locked final evaluation and runtime
governance. See the rendered pipeline and full methodology in
[`docs/architecture.md`](docs/architecture.md).

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

The first case study will use the UCI South German Credit dataset:
https://doi.org/10.24432/C5QG88

The dataset contains 1,000 historical records from 1973--1975. Its age,
sampling design, and limited demographic encoding are material limitations and
will be treated as audit findings rather than hidden.


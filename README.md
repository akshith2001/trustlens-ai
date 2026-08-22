# TrustLens AI

TrustLens AI is a research prototype for evaluating whether machine-learning
predictions are accurate, calibrated, explainable, and suitable for human
review. The first case study uses historical credit-risk data; a later module
will evaluate computer-vision anomaly detection.

## Research question

Can a human-governed auditing layer combining cost-sensitive evaluation,
uncertainty estimation, drift detection, and explainability identify unreliable
machine-learning outputs more effectively than confidence scores alone?

## Current status

The governed tabular research engine is implemented with 16 automated tests.
Its locked model was evaluated once on a 200-record holdout. It achieved 0.833
higher-risk recall and reduced the predefined weighted error cost from the
majority baseline's 300 to 123, while also producing 73 false positives. See
[`docs/results.md`](docs/results.md) for the complete, limitation-aware report.

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

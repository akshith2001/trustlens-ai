# TrustLens AI model card

> Release 0.3.0 adds a cross-domain public reference benchmark. Those results
> validate evaluation mechanics only; they do not extend the credit model's
> intended use or establish clinical or lending validity.

## Model details

TrustLens AI's first case study is a human-governed binary classification
prototype built around a cost-sensitive random forest. Probabilities are
calibrated with sigmoid calibration using three internal folds. The governed
decision threshold is 0.20 because missing a genuinely higher-risk historical
record was assigned five times the cost of an unnecessary warning.

This is a research and education artifact, not a deployed decision system.

## Intended use

The model is intended to demonstrate an auditable ML workflow that combines:

- cost-sensitive model selection;
- probability calibration;
- a predeclared decision threshold;
- drift and out-of-distribution checks;
- subgroup diagnostics and uncertainty intervals;
- local sensitivity explanations; and
- explicit escalation to human review.

It may be used to reproduce the experiments, examine methodological trade-offs,
or discuss responsible AI system design.

## Prohibited use

Do not use this model to make or support real lending, employment, insurance,
legal, medical, immigration, security, or eligibility decisions. A prediction
must not be interpreted as a statement about a person's trustworthiness or
character.

## Training and evaluation data

The case study uses the UCI South German Credit dataset, containing 1,000
historical records collected in 1973--1975. The normalized target is
`0 = lower risk` and `1 = higher risk`. The data contain 700 lower-risk and 300
higher-risk records.

The dataset is old, higher-risk records were oversampled, and the credit-amount
transformation is not fully documented. It is unsuitable for claims about
modern lending populations. See the dataset DOI:
<https://doi.org/10.24432/C5QG88>.

## Governance choices

- `personal_status_sex` is excluded because its combined coding prevents a
  defensible gender analysis.
- `foreign_worker` is excluded from prediction.
- `age_years` is retained for the governed experiment, with age-band results
  reported as exploratory diagnostics rather than proof of fairness.
- Drift AUC of 0.70 or above triggers `pause_and_investigate`.
- An individually out-of-distribution record triggers
  `pause_for_human_review`.
- The locked final-test result is written once and cannot be silently replaced
  by the evaluation script.

Feature removal alone does not establish fairness, and human review is not
assumed to be perfect.

## Locked final-test performance

The final test partition contains 200 records and was evaluated once after
development choices were locked.

| Metric | Result |
|---|---:|
| Balanced accuracy | 0.656 |
| Precision (higher risk) | 0.407 |
| Recall (higher risk) | 0.833 |
| F1 (higher risk) | 0.546 |
| False positives | 73 |
| False negatives | 10 |
| Weighted error cost | 123 |
| Brier score | 0.173 |
| Expected calibration error | 0.070 |

The predefined weighted error cost is 59% below the majority-class baseline's
300. However, the low precision and 73 false positives prevent any claim that
the model is suitable for operational decisions.

## Robustness and monitoring evidence

- Random-holdout adversarial-validation AUC: 0.485.
- Controlled synthetic-shift AUC: 0.779, correctly triggering a pause.
- Normal holdout OOD flag rate: 7.5%.
- Controlled synthetic-extreme OOD flag rate: 74.0%.

Synthetic shifts and extremes are evaluation fixtures, not observed deployment
events. They test code paths and governance responses; they do not establish
real-world detection performance.

## Explainability limits

Permutation importance describes average predictive dependence on the
development data. Local perturbations describe model sensitivity near one
record. Neither method establishes causation, recourse, or financial advice.

## Known limitations

- Small, historical and non-representative dataset.
- Material class imbalance and sampling uncertainty.
- Generalisation gap between development and the locked test result.
- Gender fairness is not assessable from the available source field.
- Subgroup estimates can be unstable, especially for small groups.
- No external validation, prospective study or live monitoring evidence.
- No evidence that the chosen error-cost ratio reflects stakeholder values.

## Reproducibility

The repository includes the data loader, experiment scripts, locked JSON
results, figure-generation code, dashboard and automated tests. GitHub Actions
runs the test suite on supported Python versions after each push and pull
request.

For the complete quantitative report, see [`docs/results.md`](docs/results.md).


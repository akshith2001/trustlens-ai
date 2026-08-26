# TrustLens Controlled Benchmark Report

Controlled synthetic robustness benchmark; not external domain validation and not evidence for operational decisions.

The historical credit final holdout was not opened or reevaluated.

## synthetic_linear_balanced

Records: 1000; positive rate: 0.491.

| Model | Balanced accuracy (95% bootstrap CI) | Weighted cost/record (95% bootstrap CI) |
|---|---:|---:|
| cost_sensitive_logistic_regression | 0.758 (0.734–0.781) | 0.314 (0.270–0.365) |
| cost_sensitive_random_forest | 0.863 (0.843–0.883) | 0.191 (0.153–0.235) |

Paired cost difference (random forest − logistic): -0.123 (95% CI -0.173–-0.077). Negative favours the forest.

Controlled-shift balanced-accuracy deltas: cost_sensitive_logistic_regression -0.104, cost_sensitive_random_forest -0.173

## synthetic_nonlinear_imbalanced

Records: 1000; positive rate: 0.308.

| Model | Balanced accuracy (95% bootstrap CI) | Weighted cost/record (95% bootstrap CI) |
|---|---:|---:|
| cost_sensitive_logistic_regression | 0.589 (0.564–0.611) | 0.654 (0.601–0.712) |
| cost_sensitive_random_forest | 0.750 (0.724–0.778) | 0.450 (0.386–0.513) |

Paired cost difference (random forest − logistic): -0.204 (95% CI -0.267–-0.146). Negative favours the forest.

Controlled-shift balanced-accuracy deltas: cost_sensitive_logistic_regression +0.050, cost_sensitive_random_forest -0.055

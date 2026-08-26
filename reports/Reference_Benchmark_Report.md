# TrustLens Public Reference Benchmark

Cross-domain public reference benchmark of evaluation machinery; not external credit validation or evidence for real-world decisions.

| Dataset | Model | Balanced accuracy | ROC AUC | Brier | Shift Δ | Proxy recall gap |
|---|---|---:|---:|---:|---:|---:|
| wisconsin_breast_cancer | logistic_regression | 0.967 | 0.995 | 0.020 | -0.037 | 0.033 |
| wisconsin_breast_cancer | calibrated_logistic_regression | 0.968 | 0.995 | 0.024 | -0.020 | 0.011 |
| wisconsin_breast_cancer | random_forest | 0.949 | 0.989 | 0.035 | +0.011 | 0.107 |
| wisconsin_breast_cancer | histogram_gradient_boosting | 0.961 | 0.992 | 0.029 | -0.014 | 0.052 |
| wine_class_0_vs_rest | logistic_regression | 0.996 | 1.000 | 0.011 | +0.000 | 0.000 |
| wine_class_0_vs_rest | calibrated_logistic_regression | 0.966 | 0.999 | 0.024 | +0.028 | 0.070 |
| wine_class_0_vs_rest | random_forest | 0.970 | 0.999 | 0.023 | -0.083 | 0.465 |
| wine_class_0_vs_rest | histogram_gradient_boosting | 0.953 | 0.995 | 0.034 | -0.083 | 0.447 |

The proxy split uses the first feature only as a pipeline diagnostic. It is not a protected-attribute fairness assessment.
Lower Brier score is better; a negative shift delta indicates degradation under the controlled noise shift.

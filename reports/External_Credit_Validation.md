# External Credit-Domain Reference Validation

Independent credit-domain reference validation. It is not a temporal validation, a replication of the historical study, or evidence for operational credit decisions.

Dataset: FICO HELOC cleaned (OpenML 45554, CC0-1.0).
Records: 9871; features: 23; positive rate: 0.520.
The source metadata does not document a collection period, so this report does not call the dataset contemporary.

| Model | Balanced accuracy | ROC AUC | Brier score |
|---|---:|---:|---:|
| logistic_regression | 0.730 | 0.800 | 0.182 |
| random_forest | 0.731 | 0.801 | 0.182 |

This dataset has no protected-attribute audit in TrustLens and must not be used to make claims about fairness.
Raw HELOC records are downloaded into an ignored cache and are not committed to the repository.

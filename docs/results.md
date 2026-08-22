# Locked results

## Final test protocol

The final 20% stratified test partition was evaluated once after the model,
excluded features, probability calibration method, and decision threshold had
been selected using development data. The result was written to
`results/final_test_metrics.json`; the evaluation script refuses to overwrite
that file.

## Governed model

- Cost-sensitive random forest
- Sigmoid probability calibration with three internal folds
- Excluded model inputs: `personal_status_sex`, `foreign_worker`
- Locked higher-risk decision threshold: 0.20
- Final test records: 200 (140 lower risk, 60 higher risk)

## Final test result

| Metric | Result |
|---|---:|
| Accuracy | 0.585 |
| Balanced accuracy | 0.656 |
| Precision (higher risk) | 0.407 |
| Recall (higher risk) | 0.833 |
| F1 (higher risk) | 0.546 |
| True negatives | 67 |
| False positives | 73 |
| False negatives | 10 |
| True positives | 50 |
| Weighted error cost | 123 |
| Brier score | 0.173 |
| Log loss | 0.521 |
| Expected calibration error | 0.070 |

## Statistical uncertainty

Because the locked test partition contains only 200 records, point estimates
must not be treated as exact population performance. Two-sided 95% Wilson score
intervals calculated from the locked confusion matrix are:

| Metric | Estimate | 95% confidence interval |
|---|---:|---:|
| Recall (higher risk) | 0.833 | 0.720--0.907 |
| Precision (higher risk) | 0.407 | 0.324--0.495 |
| Specificity (lower risk) | 0.479 | 0.398--0.561 |

These are post-hoc uncertainty summaries. They were not used to select, tune or
change the locked model, and they do not address dataset shift or external
validity.

The majority-class test baseline produced 60 false negatives and a weighted
error cost of 300. The governed model reduced this predefined cost by 59%, but
its low precision and 73 false positives demonstrate why outputs require human
review and must not be used for real lending decisions.

## Generalisation gap

Performance on the locked test set was weaker than development estimates.
Higher-risk recall declined from 0.879 to 0.833, balanced accuracy declined from
0.698 to 0.656, and expected calibration error increased from 0.032 to 0.070.
This gap is reported as evidence of sampling uncertainty and limited data, not
used as a reason to retune against the test partition.

## Post-hoc error analysis

Descriptive slice analysis was performed after locking and evaluating the
model. To reduce extremely small comparisons, a slice was reported only when
it contained at least ten records from the class relevant to that error rate.
The highest observed false-negative rate was for
`checking_account_status=4` (8/11, 0.727). The highest observed false-positive
rate was for `checking_account_status=1` (30/32, 0.938). Other elevated error
rates appeared in several property, job, credit-history, housing, purpose, age
and duration slices.

These results indicate that the locked model's errors are not evenly distributed
and that its strongest feature can be associated with sharply different error
patterns across recorded codes. They do not establish causation, unfairness or
present-day behaviour. The data are historical, individual slices remain small,
and many slices were inspected. The findings therefore support human review and
external validation rather than model deployment or post-test retuning. Full
machine-readable results are stored in `results/error_analysis.json`.

## Other development findings

- Nested sigmoid calibration reduced development Brier score from 0.239 to
  0.163 and expected calibration error from 0.267 to 0.032.
- A 20% human-review budget captured 23.0% of observed development errors and
  produced a potential weighted-cost reduction of 25.8%, assuming reviewed
  errors are corrected.
- Adversarial drift AUC was 0.485 for a random holdout and 0.779 for a controlled
  synthetic shift.
- The revised numerical OOD detector flagged 7.5% of normal holdout records and
  74.0% of controlled synthetic extremes.
- Removing the ambiguous personal-status/sex field and the foreign-worker field
  retained nearly all cross-validated performance.

## Interpretation limits

- The source data are from 1973--1975 and are not representative of current
  lending populations.
- Higher-risk records were oversampled.
- Credit amount was transformed using an undocumented method.
- Gender fairness is not assessable from the combined personal-status/sex field.
- Subgroup diagnostics do not establish causation, fairness, or discrimination.
- Synthetic drift and anomaly fixtures are not observed real-world events.
- This research prototype must not make real financial decisions.

# Research design

## Case study 1: historical credit risk

### Task

Binary classification of lower-risk and higher-risk historical credit records.

### Evaluation protocol

1. Reserve a stratified 20% test set before model development.
2. Use stratified five-fold cross-validation within the remaining 80%.
3. Select models and settings using validation results only.
4. Evaluate the selected model once on the untouched test set.

### Baselines and candidates

- Majority-class baseline
- Logistic regression
- Random forest
- Gradient boosting

### Primary evaluation

- Confusion matrix
- Precision, recall, and F1 for each class
- Balanced accuracy
- ROC-AUC and precision-recall AUC
- Probability calibration
- Cost-sensitive error: false negative cost 5, false positive cost 1

### Known limitations

- Only 1,000 records
- Data collected in 1973--1975
- Higher-risk records were deliberately oversampled
- Credit amount was transformed by an undocumented method
- Sex cannot be reliably recovered from the combined personal-status variable
- Historical relationships must not be assumed valid for present-day lending

### Governance rule

The system may flag cases for human review, but it must not approve or reject a
real applicant.

## OOD experiment log

The first individual OOD prototype applied Isolation Forest after combined
numeric and one-hot categorical preprocessing. It flagged 5.0% of a normal
holdout but only 12.5% of controlled numerical extremes. This sensitivity was
judged inadequate. The next version separates numerical anomaly screening with
robust scaling from the planned categorical-rarity detector.

## Locked-model error analysis

After the one-time final evaluation, TrustLens may reproduce the deterministic
locked predictions for descriptive error analysis. It ranks false-negative and
false-positive rates across categorical groups and numeric quartiles only when
the relevant class has at least ten records in the slice. Excluded model inputs
are also excluded from this analysis.

This is diagnostic reporting, not another development stage. The slice results
must not be used to alter the model or threshold. Patterns found by searching
many slices in a small historical dataset may be unstable, non-causal and
unsuitable for present-day decisions.

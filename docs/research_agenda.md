# TrustLens AI research agenda

## Working title

**Evidence-Constrained Credit-Risk Decision Support Under Uncertainty**

## Research proposition

A defensible credit-risk system should not merely predict. It should attach
provenance, uncertainty, limitations, permitted interpretation and a clear
human action to every material output. TrustLens calls this structure an
**evidence contract**.

The software is an educational research prototype. It is not a lending system
and must not be used to approve, reject or price real applicants.

## Research motivation

Credit-risk decisions can affect people even when the basis for a prediction is
unclear to the person affected. A visible score alone does not reveal the
freshness or provenance of the underlying data, the model's uncertainty, the
possibility of proxy effects, or the route for meaningful challenge.

This motivates a general research question: how can a person assess a
consequential prediction when its data provenance, assumptions, uncertainty
and permitted use are not presented together?

## Primary research questions

1. Can an evidence-contract interface reduce overconfident interpretation of
   credit-risk predictions without hiding useful model information?
2. How does a locked 0.20 threshold change higher-risk recall, false-negative
   cost and review burden relative to default or unconstrained thresholds?
3. Can drift and out-of-distribution signals identify cases that should be
   deferred to a human rather than automatically interpreted?
4. How should fairness limitations be communicated when protected-group labels
   are excluded from modelling but audit evidence is incomplete?

## Working hypotheses

- Evidence-contract outputs improve a non-technical user's ability to identify
  when a prediction should not be trusted.
- The locked threshold reduces costly false negatives compared with a
  majority-class baseline, while increasing false positives and review work.
- Explicit uncertainty and OOD warnings reduce inappropriate automatic
  acceptance of borderline cases.

## Existing evidence

The current locked historical holdout contains 200 records: 140 lower-risk and
60 higher-risk. The calibrated random forest uses a locked 0.20 threshold. It
produced 50 true positives, 10 false negatives, 67 true negatives and 73 false
positives. Higher-risk recall was 0.833 and balanced accuracy was 0.656. These
results are evidence about one historical holdout, not present-day lending
performance.

Independent reference validation uses 9,871 records from the FICO HELOC
dataset and produced approximately 0.73 balanced accuracy and 0.80 ROC AUC.
The source metadata does not document a collection period, so the result is not
claimed as contemporary or temporal validation.

## Proposed study

1. Freeze the pipeline, feature schema, threshold, split and report template.
2. Reproduce the locked evaluation with confusion matrix, asymmetric cost,
   calibration and Wilson confidence intervals.
3. Add contemporary independent validation and document data provenance,
   population, label definition and temporal fit.
4. Run temporal, subgroup and OOD stress tests. If the needed group labels are
   unavailable, state that fairness cannot be established.
5. Compare score-only, score-plus-explanation and evidence-contract interfaces
   in a controlled user study.
6. Measure comprehension, calibrated trust, appropriate deferral, decision
   time and disagreement with the system.

## Publication boundary

The strongest claim available today is that TrustLens implements a reproducible
framework for studying reliability-aware, human-governed prediction. The
existing evidence does not establish fairness, legal compliance, production
readiness or safety for real credit decisions.

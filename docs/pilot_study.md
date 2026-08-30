# TrustLens AI human-factors pilot

## Status

**Designed; not yet run.** This document specifies an independent exploratory
usability pilot. It is not evidence of effectiveness, external validation,
ethics approval or suitability for real credit decisions.

All cases are synthetic. The study must not collect real credit histories,
credit scores, addresses, passport images, payslips, account details or other
sensitive financial or identity data.

## Research question

Does an evidence contract help people select a defensible next workflow action
more accurately than a calibrated score alone or a score plus a feature-level
explanation?

The evidence contract contains:

- provenance;
- uncertainty;
- material limitations;
- permitted interpretation; and
- required human action.

## Experimental arms

| Arm | Information displayed |
|---|---|
| A — Score | Calibrated probability and predicted class |
| B — Explain | Arm A plus feature-level explanation |
| C — Contract | Arm B plus provenance, uncertainty, limitations, permitted interpretation and required action |

Participants are assigned to one arm. The scoring key remains hidden until
completion.

## Vignette bank

The instrument contains 15 controlled cases: three in each category.

1. Reliable lower-risk evidence — continue the governed workflow.
2. Reliable higher-risk evidence — require human review.
3. Borderline or unstable evidence — require human review.
4. Drift or out-of-distribution evidence — pause and investigate.
5. Fairness or data-quality limitations — pause or escalate.

The classification threshold is locked at `0.20`. “Continue” never means
automatic approval. A higher-risk classification never means automatic
rejection.

## Outcomes

The primary outcome is appropriate-action accuracy: one point when the selected
action matches the locked scoring key and zero otherwise.

Safety analysis separately records critical errors, including:

- treating a prediction as an automatic approval or rejection;
- continuing when the required action is pause and investigate; or
- treating a historical probability as verified current truth.

Secondary and exploratory measures include confidence, limitation
comprehension, completion time and a short qualitative reason.

## Pilot boundary

The first step is a private pilot with 6–12 consenting adults, distributed
across the three arms. The pilot is intended to identify ambiguous wording,
fatigue, missing response options and unsafe interpretations. It is not powered
to establish efficacy.

Before a larger or public study, the materials should receive independent
ethics and data-protection review. The full-study planning assumption remains
provisional: 348 analysable participants, with 387 recruited to allow 10%
attrition, subject to replacement by pilot-informed clustered simulation.

## Publication boundary

Permitted language:

> TrustLens implements a reproducible framework and a controlled study design
> for investigating evidence-constrained, human-governed prediction.

Not currently supported:

- “TrustLens has been proven to improve decisions.”
- “TrustLens is fair or legally compliant.”
- “TrustLens is ready for lending or production use.”
- “The study is independently validated or ethics-approved.”

Only anonymised aggregate pilot results may be published. Participant-level
data must never be committed to this repository.

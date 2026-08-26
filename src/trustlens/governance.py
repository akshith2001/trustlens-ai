"""Locked governance settings selected from development evidence."""

GOVERNED_DECISION_THRESHOLD = 0.20
GOVERNED_REVIEW_BUDGET = 0.20
GOVERNED_MODEL_NAME = "restricted_cost_sensitive_random_forest"


def determine_governance_action(
    probability: float,
    *,
    drift_auc: float,
    is_out_of_distribution: bool,
    uncertainty_margin: float = 0.05,
) -> tuple[str, str]:
    """Return the governed action and a human-readable reason.

    The function is deliberately separate from model prediction: governance
    can override a confident-looking output when system-level or record-level
    reliability checks fail.
    """
    for name, value in {"probability": probability, "drift_auc": drift_auc}.items():
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be between 0 and 1")
    if uncertainty_margin < 0.0:
        raise ValueError("uncertainty_margin must be non-negative")

    if drift_auc >= 0.70:
        return (
            "pause_and_investigate",
            "Population shift reached the locked drift trigger (AUC ≥ 0.70).",
        )
    if is_out_of_distribution:
        return (
            "pause_for_human_review",
            "The record is outside the model's supported data region.",
        )
    if abs(probability - GOVERNED_DECISION_THRESHOLD) <= uncertainty_margin:
        return (
            "human_review_required",
            "The probability is inside the uncertainty band around the threshold.",
        )
    if probability >= GOVERNED_DECISION_THRESHOLD:
        return (
            "human_review_required",
            "The governed model produced a higher-risk warning.",
        )
    return (
        "continue_with_monitoring",
        "No locked reliability trigger fired; retain monitoring and audit logs.",
    )

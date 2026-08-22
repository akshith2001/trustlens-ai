"""TrustLens AI research dashboard."""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from trustlens.governance import determine_governance_action


ROOT = Path(__file__).resolve().parent
FINAL_RESULT = json.loads(
    (ROOT / "results" / "final_test_metrics.json").read_text(encoding="utf-8")
)
DEVELOPMENT = json.loads(
    (ROOT / "results" / "development_summary.json").read_text(encoding="utf-8")
)

st.set_page_config(page_title="TrustLens AI", page_icon="🔎", layout="wide")
st.title("TrustLens AI")
st.caption("Human-governed reliability and explainability for machine learning")
st.warning(
    "Research prototype using historical data from 1973–1975. "
    "Do not use it for real lending decisions."
)

overview, simulator, governance, evidence, limitations = st.tabs(
    ["Overview", "Governance simulator", "Human governance", "Evidence", "Limitations"]
)

with overview:
    st.subheader("Locked final-test result")
    columns = st.columns(4)
    columns[0].metric("Balanced accuracy", f"{FINAL_RESULT['balanced_accuracy']:.3f}")
    columns[1].metric("Higher-risk recall", f"{FINAL_RESULT['recall']:.3f}")
    columns[2].metric("Precision", f"{FINAL_RESULT['precision']:.3f}")
    columns[3].metric("Weighted error cost", FINAL_RESULT["weighted_error_cost"])
    st.image(
        str(ROOT / "figures" / "final_test_summary.png"),
        caption="Generated from the immutable final-test JSON result.",
        use_container_width=True,
    )
    st.markdown(
        "The governed model found **50 of 60** higher-risk records and missed "
        "10. It also produced **73 false alarms**, so outputs require human review."
    )

with simulator:
    st.subheader("Governance simulator")
    st.caption(
        "Explore locked system rules using hypothetical signals. This does not "
        "run a credit model or assess a person."
    )
    probability = st.slider(
        "Hypothetical calibrated higher-risk probability",
        min_value=0.0,
        max_value=1.0,
        value=0.20,
        step=0.01,
    )
    drift_auc = st.slider(
        "Population-shift AUC",
        min_value=0.0,
        max_value=1.0,
        value=0.50,
        step=0.01,
    )
    is_ood = st.checkbox("Record flagged as out of distribution")
    action, reason = determine_governance_action(
        probability,
        drift_auc=drift_auc,
        is_out_of_distribution=is_ood,
    )
    labels = {
        "continue_with_monitoring": "CONTINUE WITH MONITORING",
        "human_review_required": "HUMAN REVIEW REQUIRED",
        "pause_for_human_review": "PAUSE FOR HUMAN REVIEW",
        "pause_and_investigate": "PAUSE SYSTEM AND INVESTIGATE",
    }
    if action == "continue_with_monitoring":
        st.success(labels[action])
    elif action == "human_review_required":
        st.warning(labels[action])
    else:
        st.error(labels[action])
    st.write(reason)
    st.markdown(
        "**Rule precedence:** population drift → individual OOD → threshold "
        "uncertainty/higher-risk warning → monitored continuation."
    )

with governance:
    st.subheader("Review-capacity trade-off")
    budgets = {int(row["budget"] * 100): row for row in DEVELOPMENT["review_policy"]}
    selected_budget = st.select_slider(
        "Maximum share sent for human review",
        options=list(budgets),
        value=20,
        format_func=lambda value: f"{value}%",
    )
    policy = budgets[selected_budget]
    columns = st.columns(3)
    columns[0].metric("Automated coverage", f"{policy['coverage']:.0%}")
    columns[1].metric("Errors captured", f"{policy['errors_captured']:.1%}")
    columns[2].metric(
        "Potential cost reduction",
        f"{policy['potential_cost_reduction']:.1%}",
    )
    st.caption(
        "Potential reduction assumes reviewed errors are corrected. Human review "
        "is not assumed to be perfect."
    )
    st.subheader("Locked governance rules")
    st.markdown(
        "- Decision threshold selected on development data: **0.20**\n"
        "- Ambiguous `personal_status_sex` excluded from prediction\n"
        "- `foreign_worker` excluded from prediction\n"
        "- Drift AUC ≥ 0.70: **pause and investigate**\n"
        "- OOD record: **pause for human review**"
    )

with evidence:
    st.subheader("Calibration")
    calibration = pd.DataFrame(
        {
            "Measure": ["Brier score", "Expected calibration error"],
            "Raw": [
                DEVELOPMENT["calibration"]["raw_brier_score"],
                DEVELOPMENT["calibration"]["raw_expected_calibration_error"],
            ],
            "Calibrated": [
                DEVELOPMENT["calibration"]["calibrated_brier_score"],
                DEVELOPMENT["calibration"]["calibrated_expected_calibration_error"],
            ],
        }
    )
    st.dataframe(calibration, hide_index=True, use_container_width=True)
    st.subheader("Shift and anomaly checks")
    st.markdown(
        f"- Random-holdout drift AUC: **{DEVELOPMENT['drift']['random_holdout_auc']:.3f}**\n"
        f"- Controlled-shift drift AUC: **{DEVELOPMENT['drift']['controlled_shift_auc']:.3f}**\n"
        f"- Normal OOD flag rate: **{DEVELOPMENT['ood']['normal_holdout_flag_rate']:.1%}**\n"
        f"- Synthetic-extreme OOD flag rate: **{DEVELOPMENT['ood']['synthetic_extreme_flag_rate']:.1%}**"
    )
    st.caption("Controlled shifts and extremes are synthetic evaluation fixtures.")

with limitations:
    st.subheader("What this project cannot claim")
    st.markdown(
        "- It does not validate modern lending decisions.\n"
        "- It does not establish causation, fairness, or discrimination.\n"
        "- Gender fairness is not assessable from the source data.\n"
        "- Synthetic anomaly results do not establish real-world detection rates.\n"
        "- Local perturbations are model sensitivity, not financial advice.\n"
        "- Final-test performance is weaker than development performance and is "
        "reported without retuning."
    )
    st.subheader("Reproducibility")
    st.code(
        "python -m pytest\n"
        "python scripts/run_final_test_once.py  # refuses to overwrite existing result\n"
        "streamlit run app.py",
        language="powershell",
    )

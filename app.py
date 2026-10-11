"""
Streamlit dashboard for the AI Ticket Triage Agent.

Run with:
    streamlit run app.py
"""
import pandas as pd
import streamlit as st

from src.agent import LOG_PATH, run_batch

st.set_page_config(page_title="AI Ticket Triage Agent", page_icon="🎫", layout="wide")

st.title("🎫 AI Ticket Triage Agent")
st.caption(
    "Classifies support tickets, decides auto-respond vs. escalate, and "
    "drafts a suggested response — with every decision logged and reasoned."
)

with st.expander("ℹ️ About this project"):
    st.markdown(
        """
        This agent runs a simple but explicit loop for each ticket:
        **classify → decide routing → draft response → log**.

        The routing policy is intentionally simple and explainable:
        high-urgency or billing tickets are escalated to a human; everything
        else is auto-responded to. Every decision is logged with a reason.
        """
    )

col1, col2 = st.columns([1, 3])
with col1:
    run_clicked = st.button("▶️ Run batch on sample tickets", type="primary")

if run_clicked:
    with st.spinner("Running agent over ticket batch..."):
        try:
            results_df = run_batch()
            st.session_state["results"] = results_df
        except Exception as e:
            st.error("Batch run failed. Check that GOOGLE_API_KEY is set in your .env file.")
            st.exception(e)

if "results" not in st.session_state and LOG_PATH.exists():
    st.session_state["results"] = pd.read_csv(LOG_PATH)

if "results" in st.session_state:
    df = st.session_state["results"]

    m1, m2, m3 = st.columns(3)
    m1.metric("Total tickets", len(df))
    m2.metric("Escalated", int((df["decision"] == "escalate").sum()))
    m3.metric("Auto-responded", int((df["decision"] == "auto_respond").sum()))

    st.markdown("### Ticket decisions")
    st.dataframe(
        df[["ticket_id", "subject", "category", "urgency", "decision", "decision_reason"]],
        use_container_width=True,
    )

    st.markdown("### Drill into a ticket")
    selected_id = st.selectbox("Select a ticket", df["ticket_id"])
    row = df[df["ticket_id"] == selected_id].iloc[0]
    st.markdown(f"**Subject:** {row['subject']}")
    st.markdown(f"**Classification reasoning:** {row['classification_reasoning']}")
    st.markdown(f"**Decision:** `{row['decision']}` — {row['decision_reason']}")
    st.markdown("**Suggested response:**")
    st.info(row["suggested_response"])
else:
    st.info("Click 'Run batch on sample tickets' to process the sample ticket queue.")

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import streamlit as st
from app.services.api_client import BackendAPIClient

st.set_page_config(page_title="Analyze", page_icon="🔬", layout="wide")

client = BackendAPIClient()

st.title("🔬 Analyze a Stock")
st.markdown("Submit a ticker for multi-agent investment analysis.")

with st.form("analysis_form"):
    col1, col2 = st.columns([2, 1])

    with col1:
        ticker = st.text_input(
            "Stock Ticker",
            placeholder="e.g. AAPL, MSFT, TSLA",
            help="Enter any US-listed stock ticker symbol",
        ).upper().strip()

    with col2:
        period = st.selectbox(
            "Analysis Period",
            options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3,
            help="Historical period used for price and risk calculations",
        )

    submitted = st.form_submit_button("🚀 Start Analysis", type="primary", use_container_width=True)

if submitted:
    if not ticker:
        st.error("Please enter a ticker symbol.")
    else:
        with st.spinner(f"Submitting analysis for {ticker}..."):
            try:
                result = client.submit_analysis(ticker, period)
                run_id = result["run_id"]
                st.session_state["active_run_id"] = run_id
                st.session_state["active_ticker"] = ticker

                st.success(f"✅ Analysis submitted for **{ticker}**")
                st.info(f"Run ID: `{run_id}`")
                st.markdown("---")
                st.markdown("Navigate to the **Results** page to track progress.")
                st.page_link("pages/2_Results.py", label="→ Go to Results")

            except Exception as e:
                st.error(f"Failed to submit analysis: {e}")
                st.caption("Make sure the backend is running and the ticker is valid.")

if st.session_state.get("active_run_id"):
    st.divider()
    st.markdown(f"**Active run:** `{st.session_state['active_run_id']}` for **{st.session_state.get('active_ticker', '')}**")

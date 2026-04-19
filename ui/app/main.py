import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st

st.set_page_config(
    page_title="Investment Analyst",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.services.api_client import BackendAPIClient

client = BackendAPIClient()

st.title("📈 Investment MCP Multi-Agent System")
st.markdown(
    "AI-powered equity analysis using **5 specialized agents**: "
    "Research · Technical · Sector · Risk · Report Writer"
)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🔬 How It Works")
    st.markdown(
        "1. Enter a stock ticker\n"
        "2. Submit for analysis\n"
        "3. 5 AI agents run in sequence\n"
        "4. Get a full investment report"
    )

with col2:
    st.markdown("### 🤖 Agent Pipeline")
    st.markdown(
        "→ **Research Agent** — Fundamentals\n\n"
        "→ **Technical Analyst** — Price signals\n\n"
        "→ **Sector Analyst** — Market context\n\n"
        "→ **Risk Analyst** — Risk metrics\n\n"
        "→ **Report Writer** — Final synthesis"
    )

with col3:
    st.markdown("### ⚡ Quick Start")
    quick_ticker = st.text_input(
        "Ticker Symbol",
        placeholder="e.g. AAPL, MSFT, GOOGL",
        help="Enter a US-listed stock ticker symbol (not a company name)",
        key="home_ticker",
    )
    if st.button("Analyze Now", type="primary"):
        if quick_ticker:
            try:
                result = client.submit_analysis(quick_ticker.upper())
                st.session_state["active_run_id"] = result["run_id"]
                st.session_state["active_ticker"] = quick_ticker.upper()
                st.success(f"Analysis started! Run ID: `{result['run_id']}`")
                st.page_link("pages/2_Results.py", label="View Results →")
            except Exception as e:
                st.error(f"Failed to start analysis: {e}")

st.divider()

try:
    health = client.health()
    st.caption(f"🟢 Backend connected | Status: {health.get('status', 'unknown')}")
except Exception:
    st.caption("🔴 Backend not reachable — make sure the backend is running")

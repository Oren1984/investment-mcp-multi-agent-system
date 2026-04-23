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
    "Multi-source investment intelligence platform powered by **5 specialized AI agents**, "
    "an MCP tool gateway, and a pluggable data provider architecture."
)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🔬 How It Works")
    st.markdown(
        "1. Choose your execution mode\n"
        "2. Enter a stock ticker\n"
        "3. Submit for analysis\n"
        "4. Get a full investment report with source provenance"
    )
    st.markdown("**Execution Modes:**")
    st.markdown(
        "- ⚡ **Hybrid** — RAG pre-fetch + Agent analysis *(recommended)*\n"
        "- 🤖 **Agent Only** — Full 5-agent AI pipeline\n"
        "- 📊 **RAG Only** — Raw data snapshot, no LLM"
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
        help="Enter a US-listed stock ticker symbol",
        key="home_ticker",
    )
    quick_mode = st.selectbox(
        "Mode",
        options=["hybrid", "agent_only", "rag_only"],
        format_func=lambda m: {"hybrid": "⚡ Hybrid", "agent_only": "🤖 Agent Only", "rag_only": "📊 RAG Only"}[m],
        key="home_mode",
    )
    if st.button("Analyze Now", type="primary"):
        if quick_ticker:
            try:
                result = client.submit_analysis(quick_ticker.upper(), execution_mode=quick_mode)
                st.session_state["active_run_id"] = result["run_id"]
                st.session_state["active_ticker"] = quick_ticker.upper()
                st.session_state["active_mode"] = quick_mode
                st.success(f"Analysis started! Run ID: `{result['run_id']}`")
                st.page_link("pages/2_Results.py", label="View Results →")
            except Exception as e:
                st.error(f"Failed to start analysis: {e}")

st.divider()

# ---------------------------------------------------------------------------
# Backend health + source summary
# ---------------------------------------------------------------------------
try:
    health = client.health()
    backend_ok = health.get("status") == "ok"
    if backend_ok:
        st.caption(f"🟢 Backend connected | Status: {health.get('status', 'unknown')}")
    else:
        st.caption("🟡 Backend reachable but unhealthy")
except Exception:
    st.caption("🔴 Backend not reachable — make sure the backend is running")
    st.stop()

try:
    sources_summary = client.get_sources_status()
    by_status = sources_summary.get("by_status", {})
    total = sources_summary.get("total", 0)
    ok_count = by_status.get("OK", 0)
    warn_count = by_status.get("WARN", 0)
    err_count = by_status.get("ERROR", 0)

    parts = []
    if ok_count:
        parts.append(f"🟢 {ok_count} OK")
    if warn_count:
        parts.append(f"🟡 {warn_count} WARN")
    if err_count:
        parts.append(f"🔴 {err_count} ERROR")

    status_str = " · ".join(parts) if parts else "no active sources"
    st.caption(f"📡 Sources ({total} registered): {status_str}")
except Exception:
    pass

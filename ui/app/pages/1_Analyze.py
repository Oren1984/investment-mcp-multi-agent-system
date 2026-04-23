import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import streamlit as st
from app.services.api_client import BackendAPIClient

st.set_page_config(page_title="Analyze", page_icon="🔬", layout="wide")

client = BackendAPIClient()

st.title("🔬 Analyze a Stock")
st.markdown("Submit a ticker for investment analysis. Choose your execution mode below.")

# ---------------------------------------------------------------------------
# Execution Mode Selector
# ---------------------------------------------------------------------------
st.markdown("### Execution Mode")

MODE_INFO = {
    "hybrid": {
        "label": "Hybrid — RAG + Agent",
        "icon": "⚡",
        "description": (
            "**Recommended.** Pre-fetches raw market data first (RAG pass), "
            "then runs all 5 AI agents with that context already loaded. "
            "Produces the richest, most data-grounded analysis."
        ),
    },
    "agent_only": {
        "label": "Agent Only",
        "icon": "🤖",
        "description": (
            "Runs the full 5-agent AI pipeline (Research → Technical → Sector → Risk → Report Writer). "
            "Agents call data tools on-demand during analysis. Standard deep analysis mode."
        ),
    },
    "rag_only": {
        "label": "RAG Only",
        "icon": "📊",
        "description": (
            "Retrieves raw market data from all sources without LLM synthesis. "
            "Returns a structured Market Data Snapshot — fast, no Anthropic API key needed. "
            "Ideal for checking live data availability."
        ),
    },
}

mode_options = list(MODE_INFO.keys())
mode_labels = [f"{MODE_INFO[m]['icon']} {MODE_INFO[m]['label']}" for m in mode_options]

selected_idx = st.radio(
    "Select execution mode",
    options=range(len(mode_options)),
    format_func=lambda i: mode_labels[i],
    index=0,
    horizontal=True,
    label_visibility="collapsed",
)

selected_mode = mode_options[selected_idx]
info = MODE_INFO[selected_mode]
st.info(f"**{info['icon']} {info['label']}** — {info['description']}")

st.divider()

# ---------------------------------------------------------------------------
# Analysis Form
# ---------------------------------------------------------------------------
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

    submitted = st.form_submit_button(
        f"{info['icon']} Run Analysis ({info['label']})",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if not ticker:
        st.error("Please enter a ticker symbol.")
    else:
        with st.spinner(f"Submitting {selected_mode.replace('_', ' ')} analysis for {ticker}..."):
            try:
                result = client.submit_analysis(ticker, period, execution_mode=selected_mode)
                run_id = result["run_id"]
                st.session_state["active_run_id"] = run_id
                st.session_state["active_ticker"] = ticker
                st.session_state["active_mode"] = selected_mode

                st.success(f"✅ Analysis submitted for **{ticker}** in **{info['label']}** mode")
                st.info(f"Run ID: `{run_id}`")
                st.markdown("---")
                st.markdown("Navigate to the **Results** page to track progress.")
                st.page_link("pages/2_Results.py", label="→ Go to Results")

            except Exception as e:
                st.error(f"Failed to submit analysis: {e}")
                st.caption("Make sure the backend is running and the ticker is valid.")

if st.session_state.get("active_run_id"):
    st.divider()
    active_mode = st.session_state.get("active_mode", "")
    mode_icon = MODE_INFO.get(active_mode, {}).get("icon", "")
    st.markdown(
        f"**Active run:** `{st.session_state['active_run_id']}` for "
        f"**{st.session_state.get('active_ticker', '')}** "
        f"{mode_icon} `{active_mode}`"
    )

# ---------------------------------------------------------------------------
# Source Availability Panel (collapsed by default)
# ---------------------------------------------------------------------------
st.divider()
with st.expander("📡 Data Source Availability", expanded=False):
    try:
        sources_data = client.get_sources()
        sources = sources_data.get("sources", [])
        summary = sources_data.get("summary", {})

        by_status = summary.get("by_status", {})
        cols = st.columns(5)
        STATUS_COLOR = {"OK": "🟢", "WARN": "🟡", "ERROR": "🔴", "OFFLINE": "⚫", "FUTURE": "🔵"}
        for i, (status, count) in enumerate(by_status.items()):
            with cols[i % 5]:
                st.metric(f"{STATUS_COLOR.get(status, '⚪')} {status}", count)

        st.markdown("**Active & Available Sources:**")
        for src in sources:
            status = src["status"]
            icon = STATUS_COLOR.get(status, "⚪")
            last = src.get("last_fetch")
            last_str = last[:16].replace("T", " ") if last else "—"
            st.caption(
                f"{icon} **{src['name']}** ({status}) — {src['description']} | Last: {last_str}"
            )

        st.caption("→ [View full Source Monitor](4_Sources)")
    except Exception:
        st.caption("Source monitor unavailable — backend may not be running.")

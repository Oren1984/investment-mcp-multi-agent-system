import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import time
import streamlit as st
from app.services.api_client import BackendAPIClient
from app.components.status_badge import render_status_badge, render_progress_bar
from app.components.report_viewer import render_report
from app.utils.formatters import fmt_datetime

st.set_page_config(page_title="Results", page_icon="📊", layout="wide")

client = BackendAPIClient()

st.title("📊 Analysis Results")

run_id = st.text_input(
    "Run ID",
    value=st.session_state.get("active_run_id", ""),
    placeholder="Paste a run ID or submit from the Analyze page",
)

if not run_id:
    st.info("Enter a Run ID above, or go to the Analyze page to start a new analysis.")
    st.stop()

try:
    status_data = client.get_status(run_id)
except Exception as e:
    st.error(f"Could not fetch status for `{run_id}`: {e}")
    st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Ticker", status_data.get("ticker", "—"))
with col2:
    render_status_badge(status_data.get("status", ""))
with col3:
    st.metric("Started", fmt_datetime(status_data.get("started_at")))

render_progress_bar(status_data.get("status", ""))

status = status_data.get("status", "")

if status in ("PENDING", "RUNNING"):
    st.markdown("---")
    col_refresh, _ = st.columns([1, 4])
    with col_refresh:
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()

    if st.checkbox("Auto-refresh every 5 seconds", value=False):
        time.sleep(5)
        st.rerun()

elif status == "COMPLETED":
    st.markdown("---")
    try:
        report = client.get_report(run_id)
        if report:
            render_report(report)
        else:
            st.warning("Report not ready yet, please refresh.")
    except Exception as e:
        st.error(f"Error loading report: {e}")

elif status == "FAILED":
    st.markdown("---")
    st.error("Analysis failed.")
    if status_data.get("error_message"):
        with st.expander("Error Details"):
            st.code(status_data["error_message"])

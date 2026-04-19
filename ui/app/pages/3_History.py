import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import streamlit as st
import pandas as pd
from app.services.api_client import BackendAPIClient
from app.utils.formatters import fmt_datetime, fmt_status_emoji

st.set_page_config(page_title="History", page_icon="📋", layout="wide")

client = BackendAPIClient()

st.title("📋 Analysis History")
st.markdown("Previous investment analyses run on this system.")

limit = st.slider("Show last N runs", min_value=5, max_value=100, value=20, step=5)

try:
    history = client.get_history(limit=limit)
    items = history.get("items", [])
except Exception as e:
    st.error(f"Could not load history: {e}")
    st.stop()

if not items:
    st.info("No analyses run yet. Go to the Analyze page to get started.")
    st.stop()

rows = [
    {
        "Ticker": item["ticker"],
        "Status": fmt_status_emoji(item["status"]),
        "Created": fmt_datetime(item.get("created_at")),
        "Completed": fmt_datetime(item.get("completed_at")),
        "Has Report": "✅" if item.get("has_report") else "—",
        "Run ID": item["run_id"],
    }
    for item in items
]

df = pd.DataFrame(rows)
st.dataframe(df.drop(columns=["Run ID"]), use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("**Load a specific run:**")

selected_run = st.selectbox(
    "Select run ID",
    options=[item["run_id"] for item in items],
    format_func=lambda x: f"{next(i['ticker'] for i in items if i['run_id'] == x)} — {x[:8]}...",
)

if st.button("View Results", type="primary"):
    st.session_state["active_run_id"] = selected_run
    st.page_link("pages/2_Results.py", label="→ Go to Results")
    st.info(f"Active run set to `{selected_run}`. Navigate to Results.")

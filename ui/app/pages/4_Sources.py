import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import time
import streamlit as st
from app.services.api_client import BackendAPIClient

st.set_page_config(page_title="Source Monitor", page_icon="📡", layout="wide")

client = BackendAPIClient()

st.title("📡 Market Source Monitor")
st.markdown(
    "Live status of all data providers registered in the system. "
    "Sources update their status automatically when the analysis pipeline fetches data."
)

STATUS_COLOR = {
    "OK": "🟢",
    "WARN": "🟡",
    "ERROR": "🔴",
    "OFFLINE": "⚫",
    "FUTURE": "🔵",
}

STATUS_CAPTION = {
    "OK": "Active and healthy",
    "WARN": "Active with limitations",
    "ERROR": "Recently failed",
    "OFFLINE": "Configured but not active",
    "FUTURE": "Planned — not yet implemented",
}

# ---------------------------------------------------------------------------
# Auto-refresh
# ---------------------------------------------------------------------------
col_refresh, col_auto, _ = st.columns([1, 2, 4])
with col_refresh:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
with col_auto:
    auto_refresh = st.checkbox("Auto-refresh every 10 seconds", value=False)

st.divider()

# ---------------------------------------------------------------------------
# Fetch source data
# ---------------------------------------------------------------------------
try:
    data = client.get_sources()
    sources = data.get("sources", [])
    summary = data.get("summary", {})

    # Summary KPIs
    by_status = summary.get("by_status", {})
    total = summary.get("total", 0)
    kpi_cols = st.columns(6)
    with kpi_cols[0]:
        st.metric("Total Sources", total)
    for i, (status, count) in enumerate(by_status.items()):
        if i + 1 < len(kpi_cols):
            with kpi_cols[i + 1]:
                icon = STATUS_COLOR.get(status, "⚪")
                st.metric(f"{icon} {status}", count)

    st.divider()

    # Source table
    st.markdown("### Source Details")

    for src in sources:
        status = src["status"]
        icon = STATUS_COLOR.get(status, "⚪")
        last_fetch = src.get("last_fetch")
        last_str = last_fetch[:19].replace("T", " ") if last_fetch else "Never"
        latency = src.get("latency_ms", 0)
        records = src.get("records_returned", 0)
        assets = src.get("assets_covered", 0)

        with st.container():
            c1, c2, c3, c4, c5 = st.columns([3, 1, 2, 1, 1])
            with c1:
                st.markdown(f"**{icon} {src['name']}**")
                st.caption(src.get("description", ""))
            with c2:
                st.markdown(f"`{status}`")
                st.caption(STATUS_CAPTION.get(status, ""))
            with c3:
                st.markdown(f"Last fetch: `{last_str}`")
                if latency:
                    st.caption(f"Latency: {latency:.0f} ms")
            with c4:
                if records:
                    st.metric("Records", records, label_visibility="visible")
            with c5:
                if assets:
                    st.metric("Assets", assets, label_visibility="visible")

            notes = src.get("notes", "")
            error = src.get("error_message", "")
            if error:
                st.caption(f"⚠️ {error}")
            elif notes:
                st.caption(f"ℹ️ {notes}")

            asset_types = src.get("asset_types", "")
            if asset_types:
                st.caption(f"Coverage: {asset_types}")

        st.divider()

    # Architecture note
    st.markdown("### Architecture Notes")
    st.info(
        "**Active providers** (OK / WARN): Yahoo Finance and News API are currently integrated. "
        "**Offline**: Alpha Vantage key is reserved in config but the provider is not yet active. "
        "**Future**: Finnhub and Polygon.io are designed into the source registry for future integration "
        "— the pluggable architecture makes adding new providers a matter of implementing an adapter."
    )

    with st.expander("Execution Mode × Source Mapping", expanded=False):
        st.markdown("""
| Execution Mode | Sources Used |
|----------------|-------------|
| RAG Only | Yahoo Finance (price, financials, technicals, sector, risk), News API / Fallback |
| Agent Only | Agents call Yahoo Finance and News tools on-demand |
| Hybrid | Pre-fetches Yahoo Finance + News (RAG pass), then agents run with that context |

All three modes route through the **MCP Gateway** which provides a provider-agnostic tool interface.
New providers can be added by implementing an adapter and registering it with the gateway — no changes
to the agent or orchestration layer are required.
        """)

except Exception as e:
    st.error(f"Could not reach backend: {e}")
    st.caption("Make sure the backend is running.")

# ---------------------------------------------------------------------------
# Auto-refresh
# ---------------------------------------------------------------------------
if auto_refresh:
    time.sleep(10)
    st.rerun()

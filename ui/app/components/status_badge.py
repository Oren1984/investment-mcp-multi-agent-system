import streamlit as st


STATUS_COLORS = {
    "PENDING": "🟡",
    "RUNNING": "🔵",
    "COMPLETED": "🟢",
    "FAILED": "🔴",
}


def render_status_badge(status: str) -> None:
    icon = STATUS_COLORS.get(status, "⚪")
    st.markdown(f"**Status:** {icon} `{status}`")


def render_progress_bar(status: str) -> None:
    progress_map = {"PENDING": 0.1, "RUNNING": 0.6, "COMPLETED": 1.0, "FAILED": 1.0}
    value = progress_map.get(status, 0.0)
    color = "red" if status == "FAILED" else None

    if status == "RUNNING":
        st.info("Analysis in progress — agents are working...")
        st.progress(value, text="Running multi-agent analysis...")
    elif status == "COMPLETED":
        st.success("Analysis complete!")
        st.progress(value)
    elif status == "FAILED":
        st.error("Analysis failed.")
    else:
        st.progress(value, text="Queued...")

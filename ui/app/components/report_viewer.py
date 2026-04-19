import streamlit as st


def render_report(report: dict) -> None:
    st.markdown(f"## 📄 Investment Report: **{report.get('ticker', '')}**")
    st.caption(f"Generated: {report.get('created_at', '')} | Run ID: `{report.get('run_id', '')}`")

    content = report.get("content", "")
    structured = report.get("structured", {}) or {}

    _render_validation_warnings(structured)

    if structured and any(v for k, v in structured.items() if not k.startswith("_")):
        _render_structured(structured, content)
    else:
        st.markdown(content)

    with st.expander("📥 Export Report"):
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download Markdown",
                data=content,
                file_name=f"{report.get('ticker', 'report')}_analysis.md",
                mime="text/markdown",
            )
        with col2:
            import json
            st.download_button(
                label="Download JSON",
                data=json.dumps(report, indent=2, default=str),
                file_name=f"{report.get('ticker', 'report')}_analysis.json",
                mime="application/json",
            )


def _render_validation_warnings(structured: dict) -> None:
    warnings = structured.get("_validation_warnings", {})
    if not warnings:
        return
    missing = warnings.get("missing_sections", [])
    if missing:
        st.warning(
            f"⚠️ **Incomplete report** — the following required sections are missing or "
            f"could not be detected: **{', '.join(missing)}**. "
            "The full report content is still available in the 'Full Report' tab.",
            icon="⚠️",
        )


def _render_structured(structured: dict, full_content: str) -> None:
    sections = {
        "📊 Executive Summary": structured.get("executive_summary", ""),
        "💰 Fundamental Analysis": structured.get("fundamentals", ""),
        "📈 Technical Analysis": structured.get("technical_analysis", ""),
        "🏭 Sector Context": structured.get("sector_context", ""),
        "⚠️ Risk Profile": structured.get("risk_profile", ""),
        "🎯 Recommendation": structured.get("recommendation", ""),
    }

    non_empty = {k: v for k, v in sections.items() if v}

    if not non_empty:
        st.markdown(full_content)
        return

    tabs = st.tabs(list(non_empty.keys()) + ["📋 Full Report"])
    for tab, (_, content) in zip(tabs[:-1], non_empty.items()):
        with tab:
            st.markdown(content)
    with tabs[-1]:
        st.markdown(full_content)

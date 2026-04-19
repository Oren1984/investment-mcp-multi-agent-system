from datetime import datetime


def fmt_datetime(dt_str: str | None) -> str:
    if not dt_str:
        return "—"
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return dt_str


def fmt_status_emoji(status: str) -> str:
    return {"PENDING": "🟡 Pending", "RUNNING": "🔵 Running", "COMPLETED": "🟢 Completed", "FAILED": "🔴 Failed"}.get(
        status, status
    )

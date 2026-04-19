# Purpose

This folder defines observability for agent systems.

Agent observability is broader than normal app logging because we need visibility into:
- reasoning steps
- tool calls
- approvals
- retries
- failures
- memory usage
- end-to-end workflow traces

# Key signals

- trace per user task
- tool execution logs
- approval decisions
- retries and fallback paths
- token usage
- step duration
- failure point identification

# Example tooling

- OpenTelemetry
- Phoenix
- LangSmith
- structured JSON logs

# Important

Keep this replaceable.
Do not lock the skeleton to one observability vendor.
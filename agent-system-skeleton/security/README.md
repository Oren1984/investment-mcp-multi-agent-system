# Purpose

This folder defines the security baseline for agent systems.

Agents have more risk than basic chat or RAG because they may act on tools and external systems.

# Main concerns

- prompt injection
- tool misuse
- excessive permissions
- unsafe execution
- secret leakage
- unintended side effects
- unsafe autonomy

# Security baseline

- least privilege for tools
- explicit approval for sensitive actions
- no raw secret logging
- input/output validation
- safe tool schemas
- audit trail for actions
- clear allow/deny rules

# What belongs here

- guardrails notes
- secret handling notes
- tool execution rules
- approval rules
- audit recommendations
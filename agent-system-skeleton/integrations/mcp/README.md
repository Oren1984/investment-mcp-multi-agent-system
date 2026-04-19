# Purpose

This folder is reserved for MCP-related integrations.

MCP can be used as a standard way to connect agents to external tools, data sources, and APIs.

# Template role

The skeleton should support MCP as an extension point,
not require it for every project.

# What belongs here

- MCP adapter notes
- supported integration patterns
- client/server mapping notes
- security considerations
- schema compatibility notes

# Important

Keep MCP optional and modular.
Projects may use MCP, direct SDKs, or internal adapters depending on context.
# Purpose

Shared LLM gateway conventions.

This folder defines how projects choose models and providers without tightly coupling business logic to a vendor SDK.

# Typical responsibilities

- model selection
- provider selection
- fallback routing
- capability-based routing
- cost/performance routing

# Important

This is a contract layer, not a full production gateway implementation.
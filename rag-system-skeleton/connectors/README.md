# Purpose

This folder is for optional external connectors used by RAG projects.

Examples:
- web search
- internal API retrieval
- document systems
- databases
- enterprise search engines

# Important

Connectors are optional.
They must not be mandatory for the basic RAG skeleton.

# Design principles

- disabled by default
- explicit configuration
- replaceable adapters
- clear input/output contracts
- no hidden network dependency

# Example connector groups

- web_search/
- file_store/
- knowledge_base/
- internal_api/
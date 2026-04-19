# Purpose

This directory contains lightweight tests for the shared platform layer.

Its role is to verify that the infrastructure foundation behaves correctly and remains stable as it evolves.

Tests here should be fast, focused, and independent from project-specific application logic.

# What goes here

Files in this directory may include tests for:

- settings loading
- validation helpers
- retry helpers
- logger initialization
- base reusable components

Typical examples:

- `test_config.py`
- `test_retry.py`
- `test_validation.py`

# What NOT goes here

This directory should NOT contain:

- business tests
- API endpoint tests for specific apps
- model tests
- RAG pipeline tests
- agent orchestration tests
- UI tests
- product integration tests
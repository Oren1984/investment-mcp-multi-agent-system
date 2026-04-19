# Purpose

This directory contains small reusable helper functions that support the platform layer.

Utilities here should remain generic, lightweight, and independent from business logic.

They are meant to reduce duplication and keep common technical helpers centralized.

# What goes here

Files in this directory may include:

- path utilities
- time utilities
- ID generation helpers
- text normalization helpers
- small generic helper functions

Typical examples:

- `paths.py`
- `time_utils.py`
- `id_utils.py`
- `text_utils.py`

# What NOT goes here

This directory should NOT contain:

- business workflows
- domain-specific helpers
- model-specific preprocessing
- RAG-specific chunking
- prompt builders
- agent orchestration helpers
- large utility classes that belong to application logic
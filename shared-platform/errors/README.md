# Purpose

This directory defines the shared exception layer for the platform.

Its goal is to provide a clean and reusable error structure that can be extended across projects without mixing infrastructure concerns with business logic.

A shared error hierarchy improves consistency, readability, and debugging.

# What goes here

Files in this directory may include:

- base exception classes
- configuration-related errors
- validation-related errors
- external dependency errors
- generic reusable infrastructure exceptions

Typical examples:

- `base.py`
- `config_errors.py`
- `validation_errors.py`
- `external_errors.py`

# What NOT goes here

This directory should NOT contain:

- business-specific exceptions
- product workflow failures
- user-facing UI messages
- model prediction failures tied to one project
- RAG-specific retrieval exceptions
- agent task orchestration exceptions tied to one system
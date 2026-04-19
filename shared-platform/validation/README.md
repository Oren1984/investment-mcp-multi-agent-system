# Purpose

This directory contains generic validation helpers for the shared platform layer.

Its purpose is to provide reusable validation patterns that can be shared across projects without embedding domain or product logic.

Validation here should remain simple, generic, and infrastructure-oriented.

# What goes here

Files in this directory may include:

- basic schemas
- reusable validators
- generic type checks
- value checks
- required field checks
- shared validation utilities

Typical examples:

- `schemas.py`
- `validators.py`

# What NOT goes here

This directory should NOT contain:

- product-specific request validation
- API endpoint validation tied to one application
- model input validation specific to one use case
- RAG document validation rules
- agent task validation rules
- business rule enforcement
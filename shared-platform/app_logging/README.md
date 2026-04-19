# Purpose

This directory contains the shared logging layer for the platform.

Its goal is to provide a consistent and reusable way to initialize and format logs across AI projects.

It should help standardize:

- logger creation
- log formatting
- log level handling
- file and console logging patterns

# What goes here

Files in this directory may include:

- logger factory functions
- formatter definitions
- structured logging helpers
- shared logging setup logic

Typical examples:

- `logger.py`
- `formatters.py`

# What NOT goes here

This directory should NOT contain:

- business event logging logic
- product-specific audit trails
- domain-specific messages
- analytics tracking
- prompt traces
- RAG-specific telemetry
- agent execution history tied to one project
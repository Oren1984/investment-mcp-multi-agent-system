# Purpose

This directory contains optional reusable base classes for platform-level components.

It is meant for lightweight abstractions only, when they help standardize shared behavior across services or components.

Base classes here should remain minimal and generic.

# What goes here

Files in this directory may include:

- base service classes
- base component classes
- common lifecycle patterns
- small abstract reusable foundations

Typical examples:

- `base_service.py`
- `base_component.py`

# What NOT goes here

This directory should NOT contain:

- business services
- domain services
- RAG pipelines
- agent managers
- API controllers
- project-specific workflow classes
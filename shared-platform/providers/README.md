# Purpose

Shared provider abstractions for all templates.

This layer exists so that RAG, agents, and future systems can all use:
- the same provider interface
- the same model registry
- the same configuration conventions

# Design goals

- vendor-agnostic
- swappable adapters
- environment-driven configuration
- minimal shared contracts
# Purpose

This folder defines the security and safety baseline for RAG systems.

A RAG project may look simple, but it still handles:
- user input
- retrieved documents
- external model calls
- possibly sensitive internal knowledge

# Core concerns

- prompt injection through retrieved content
- leaking confidential knowledge
- sending sensitive input to external LLM APIs
- weak access boundaries between datasets
- unsafe logging of user or document content

# What belongs here

- prompt injection notes
- input/output sanitization guidance
- PII masking guidance
- access control notes
- safe logging rules
- vendor data handling guidance

# Minimum baseline

- never trust retrieved text blindly
- separate system instructions from retrieved context
- mask PII before external calls when needed
- avoid logging raw secrets or personal data
- define which data may leave the system

# Notes

This template provides structure only.
Real implementations should adapt controls to the actual project.
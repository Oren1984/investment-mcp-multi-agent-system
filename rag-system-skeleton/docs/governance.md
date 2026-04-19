# Governance, Safety, and Responsible Use

This document defines the non-functional expectations of projects created from the RAG skeleton.

## Goals

- keep answers grounded in retrieved evidence
- reduce hallucinations
- protect sensitive data
- support traceability and review
- make model/provider choices replaceable

## Core rules

1. Retrieved content is evidence, not truth by default.
2. Sensitive data must be handled explicitly.
3. External LLM calls must be configurable and reviewable.
4. Logging must avoid secrets and unnecessary personal data.
5. Projects should support observability and debugging from day one.

## Recommended checks

- prompt injection review
- citation validation
- retrieval quality evaluation
- vendor data exposure review
- fallback behavior review

## Ethics and compliance

Projects based on this skeleton should document:
- where data came from
- which provider was used
- what limitations exist
- which human review points are required
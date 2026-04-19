# Purpose

This folder defines observability expectations for the RAG system skeleton.

The goal is not to force a specific vendor, but to make every RAG project ready for:

- tracing
- logging
- latency measurement
- retrieval quality analysis
- token usage analysis
- debugging of failed or weak answers

# What belongs here

- tracing integration notes
- logging strategy
- metrics definitions
- evaluation hooks
- retrieval diagnostics
- reranking diagnostics

# Typical metrics

- query latency
- retrieval latency
- reranker latency
- answer generation latency
- token usage
- top-k retrieval quality
- groundedness / citation quality
- failure cases

# Notes

Recommended tools may include:
- OpenTelemetry
- Arize Phoenix
- LangSmith
- custom structured logs

Do not hardcode one observability stack in the template.
Keep this layer replaceable.
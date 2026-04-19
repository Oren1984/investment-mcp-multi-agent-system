# Purpose

This folder defines how an agent project can work with multiple LLM providers.

The template should support:
- GPT
- Claude
- Gemini
- local models
- self-hosted endpoints

# Design rule

The agent should depend on a common provider interface,
not on a single vendor SDK directly.

# What belongs here

- provider adapter notes
- model routing notes
- fallback strategy
- cost/performance notes
- structured output guidance
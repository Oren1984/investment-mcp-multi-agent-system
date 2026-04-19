# Purpose

This folder describes how the RAG skeleton connects to different model providers.

The template should remain provider-agnostic.

Supported provider categories may include:
- OpenAI
- Anthropic
- Google Gemini
- local models
- self-hosted inference endpoints

# Design rule

The template must not be tightly coupled to one provider.

Use:
- shared interfaces
- adapter pattern
- environment-based configuration
- model registry

# What belongs here

- provider notes
- environment variable mapping
- adapter examples
- fallback strategy notes
- model selection notes

# Recommended approach

All provider-specific code should implement a shared interface from the shared-platform layer.
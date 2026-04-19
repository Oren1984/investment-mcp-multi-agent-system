# Platform Usage

This document explains how to integrate the shared-platform layer into real AI projects.

## Basic Steps

1. Copy the shared-platform folder into your project
2. Merge relevant directories into your project structure
3. Remove unused components
4. Extend config/settings based on your project needs
5. Use shared logging across services
6. Use validation/retry utilities where needed

## Integration Examples

- RAG system → use config + logging + retry
- Agent system → use logging + errors + base
- API system → use config + validation + errors

## Important Notes

- Do not place business logic here
- Do not modify core structure unless reusable
- Always keep platform generic
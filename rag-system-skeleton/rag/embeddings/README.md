# Embeddings

## Purpose
This folder contains logic for converting text chunks into vector representations.

## What Belongs Here
- Embedding provider adapters
- Embedding generation workflows
- Batch embedding logic
- Embedding validation helpers

## Notes
Embedding logic should stay isolated from storage and retrieval so providers can be swapped more easily.
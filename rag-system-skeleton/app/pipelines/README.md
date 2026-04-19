# Pipelines

## Purpose
This folder contains application-facing pipeline orchestration.

It is useful for defining complete flows that combine multiple internal components into a single executable business process.

## What Belongs Here
- End-to-end query pipelines
- End-to-end ingestion pipelines
- Evaluation execution flows
- Batch processing workflows

## Notes
This layer focuses on orchestration.  
The implementation details of retrieval, chunking, embeddings, and reranking should remain under the `rag/` folder.
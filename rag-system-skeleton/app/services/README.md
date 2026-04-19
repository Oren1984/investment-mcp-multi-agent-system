# Services

## Purpose
This folder contains application services that coordinate higher-level operations.

Services act as the bridge between the API layer and the lower-level RAG components.

## What Belongs Here
- Query services
- Ingestion services
- Document management services
- Evaluation services
- Workflow coordination services

## Notes
Services should orchestrate work, not become large unstructured logic containers.  
Whenever possible, keep responsibilities narrow and explicit.
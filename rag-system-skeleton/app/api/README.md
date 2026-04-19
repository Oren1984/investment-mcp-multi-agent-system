# API

## Purpose
This folder is reserved for the external interface of the application.

It will eventually contain the HTTP API layer used to expose the RAG system to clients, services, or frontend applications.

## What Belongs Here
- Route definitions
- API versioning
- Request handlers
- Health endpoints
- Query endpoints
- Ingestion endpoints
- Evaluation endpoints if exposed externally

## Notes
Keep this layer thin.  
Business logic should stay in services or pipeline-related components, not directly in route handlers.
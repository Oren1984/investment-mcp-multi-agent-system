# App Layer

## Purpose
This folder contains the application-level structure of the system.

It is responsible for organizing the service as an application, independently from the internal RAG pipeline implementation.

## What Belongs Here
- API entrypoints
- Core application configuration
- Shared services
- Request and response schemas
- Utility helpers
- Pipeline orchestration from the app side

## Notes
The `app/` folder should remain clean and focused on application composition.  
Low-level RAG logic should stay under the `rag/` folder.
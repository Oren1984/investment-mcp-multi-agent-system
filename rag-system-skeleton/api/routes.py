from __future__ import annotations


def health() -> dict:
    return {"status": "ok", "service": "rag-template"}


def query(payload: dict) -> dict:
    """
    Thin placeholder route for RAG query handling.
    Real retrieval/generation logic should live elsewhere.
    """
    return {
        "message": "RAG query route placeholder",
        "received": payload,
    }
from __future__ import annotations


class WebSearchClient:
    def search(self, query: str) -> dict:
        return {
            "enabled": False,
            "query": query,
            "results": [],
            "message": "Agent web search placeholder only",
        }
from __future__ import annotations


class WebSearchClient:
    """
    Thin placeholder for optional web search integration.
    Disabled by default in template-based projects.
    """

    def search(self, query: str) -> dict:
        return {
            "enabled": False,
            "query": query,
            "results": [],
            "message": "Web search placeholder only",
        }
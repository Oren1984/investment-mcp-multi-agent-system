from __future__ import annotations


class OpenAIAdapter:
    """
    Thin placeholder adapter.
    Real implementation belongs in a concrete project, not in the template.
    """

    provider_name = "openai"

    def generate(self, payload: dict) -> dict:
        return {
            "provider": self.provider_name,
            "message": "OpenAI adapter placeholder",
            "payload": payload,
        }
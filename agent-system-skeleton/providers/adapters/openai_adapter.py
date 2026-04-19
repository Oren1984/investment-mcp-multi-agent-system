from __future__ import annotations


class OpenAIAdapter:
    provider_name = "openai"

    def generate(self, payload: dict) -> dict:
        return {
            "provider": self.provider_name,
            "message": "OpenAI agent adapter placeholder",
            "payload": payload,
        }
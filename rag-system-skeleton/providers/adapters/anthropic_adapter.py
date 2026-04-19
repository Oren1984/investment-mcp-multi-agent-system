from __future__ import annotations


class AnthropicAdapter:
    provider_name = "anthropic"

    def generate(self, payload: dict) -> dict:
        return {
            "provider": self.provider_name,
            "message": "Anthropic adapter placeholder",
            "payload": payload,
        }
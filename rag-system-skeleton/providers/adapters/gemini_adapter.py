from __future__ import annotations


class GeminiAdapter:
    provider_name = "gemini"

    def generate(self, payload: dict) -> dict:
        return {
            "provider": self.provider_name,
            "message": "Gemini adapter placeholder",
            "payload": payload,
        }
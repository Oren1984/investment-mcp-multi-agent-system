from __future__ import annotations


class GeminiAdapter:
    provider_name = "gemini"

    def generate(self, payload: dict) -> dict:
        return {
            "provider": self.provider_name,
            "message": "Gemini agent adapter placeholder",
            "payload": payload,
        }
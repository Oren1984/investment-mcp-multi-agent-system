from __future__ import annotations

import os
from typing import Any

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_BASE = f"{BACKEND_URL}/api/v1"


class BackendAPIClient:
    def __init__(self, base_url: str = API_BASE, timeout: int = 30):
        self._base = base_url.rstrip("/")
        self._timeout = timeout

    def _get(self, path: str) -> dict[str, Any]:
        resp = requests.get(f"{self._base}{path}", timeout=self._timeout)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, payload: dict) -> dict[str, Any]:
        resp = requests.post(f"{self._base}{path}", json=payload, timeout=self._timeout)
        resp.raise_for_status()
        return resp.json()

    def submit_analysis(self, ticker: str, period: str = "1y") -> dict:
        return self._post("/analyze", {"ticker": ticker, "period": period})

    def get_status(self, run_id: str) -> dict:
        return self._get(f"/analyze/{run_id}/status")

    def get_report(self, run_id: str) -> dict | None:
        try:
            return self._get(f"/analyze/{run_id}/report")
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 202:
                return None
            raise

    def get_history(self, limit: int = 20) -> dict:
        return self._get(f"/analyze?limit={limit}")

    def health(self) -> dict:
        return self._get("/health")

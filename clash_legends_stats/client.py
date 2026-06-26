from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests

from .settings import BASE_URL


@dataclass
class ClashApiClient:
    token: str
    timeout: int = 30
    max_retries: int = 3

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        url = f"{BASE_URL}{path}"
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            if response.status_code < 400:
                return response.json()
            last_error = requests.HTTPError(
                f"GET {path} failed with {response.status_code}: {response.text[:500]}",
                response=response,
            )
            if response.status_code not in {429, 500, 502, 503, 504}:
                break
            retry_after = response.headers.get("Retry-After")
            sleep_for = float(retry_after) if retry_after and retry_after.isdigit() else (2 ** attempt)
            time.sleep(min(sleep_for, 30.0))
        assert last_error is not None
        raise last_error


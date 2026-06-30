from __future__ import annotations

from typing import Any

import requests


class ComfyClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def submit(
        self,
        workflow: dict[str, Any],
    ) -> str:
        response = self.session.post(
            f"{self.base_url}/prompt",
            json={
                "prompt": workflow,
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        return data["prompt_id"]

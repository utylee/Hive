from __future__ import annotations

from typing import Any

import requests

from hive.comfy.models import Prompt


class ComfyClient:
    def __init__(
        self,
        base_url: str,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()

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

        # return data["prompt_id"]
        return Prompt(
            id=data["prompt_id"],
        )

    def history(
        self,
        prompt_id: str,
    ) -> dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/history/{prompt_id}",
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

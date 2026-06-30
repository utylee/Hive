from __future__ import annotations

from typing import Any

import requests
import time
from typing import Any

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

    def _history(
        self,
        prompt_id: str,
    ) -> dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/history/{prompt_id}",
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def wait(
        self,
        prompt: Prompt,
        poll_interval: float = 1.0,
        timeout: float = 300.0,
    ) -> None:
        start = time.time()

        while True:
            history = self._history(prompt.id)

            job = history.get(prompt.id)

            # 아직 결과가 없으면 계속 기다림
            if job is None:
                pass
            else:
                # ComfyUI completed 구조 가정
                status = job.get("status", {})
                if status.get("completed", False):
                    return

            if time.time() - start > timeout:
                raise TimeoutError(
                    f"Comfy job timeout: {prompt.id}"
                )

            time.sleep(poll_interval)

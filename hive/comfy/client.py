from __future__ import annotations


class ComfyClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def submit(self, workflow: dict) -> str:
        raise NotImplementedError

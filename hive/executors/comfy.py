from __future__ import annotations

from pathlib import Path
from typing import Any


class ComfyExecutor:
    def execute(self, job_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
        return {
            "ok": True,
            "executor": "comfy",
        }

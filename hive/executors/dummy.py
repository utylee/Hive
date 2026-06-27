from __future__ import annotations

import time
from pathlib import Path


class DummyExecutor:
    def execute(self, job_dir: Path, manifest: dict) -> dict:
        time.sleep(2)

        return {
            "ok": True,
            "executor": "dummy",
        }

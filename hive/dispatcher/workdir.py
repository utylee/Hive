from __future__ import annotations

from pathlib import Path


class WorkDir:
    def __init__(self, root: str | Path):
        self.root = Path(root)

    def create(self, job_id: str) -> Path:
        job_dir = self.root / job_id

        for name in ["input", "output", "logs"]:
            (job_dir / name).mkdir(parents=True, exist_ok=True)

        return job_dir

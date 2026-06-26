from __future__ import annotations

from pathlib import Path


class Scanner:
    def __init__(self, root: str | Path):
        self.root = Path(root)

    def scan(self, pattern: str = "*.mp4") -> list[Path]:
        if not self.root.exists():
            return []

        return sorted(
            file
            for file in self.root.iterdir()
            if file.is_file() and file.match(pattern)
        )



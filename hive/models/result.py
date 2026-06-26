from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(slots=True)
class Result:
    ok: bool

    worker: str

    elapsed_sec: float

    error: str = ""

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            json.dumps(
                asdict(self),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path) -> "Result":
        return cls(
            **json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )
        )


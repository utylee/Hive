from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Job:
    version: int = 1

    id: str = ""

    project: str = ""

    type: str = ""

    source: Path = Path()

    destination: Path = Path()

    parameters: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)

        data["source"] = str(self.source)
        data["destination"] = str(self.destination)

        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Job":
        data = dict(data)

        data["source"] = Path(data["source"])
        data["destination"] = Path(data["destination"])

        return cls(**data)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            json.dumps(
                self.to_dict(),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path) -> "Job":
        return cls.from_dict(
            json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )
        )


from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Profile:
    frames_per_batch: int = 1

    @classmethod
    def from_dict(cls, data: dict | None) -> "Profile":
        data = data or {}
        return cls(
            frames_per_batch=int(data.get("frames_per_batch", 1)),
        )

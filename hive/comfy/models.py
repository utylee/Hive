from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Prompt:
    id: str


@dataclass(slots=True, frozen=True)
class Output:
    filename: str
    subfolder: str
    type: str

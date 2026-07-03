from __future__ import annotations

from pathlib import Path
from typing import Protocol

from hive.runtime.task import Task


class Workflow(Protocol):
    def plan(
        self,
        source: Path,
    ) -> list[Task]:
        ...

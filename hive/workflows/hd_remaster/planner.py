from __future__ import annotations

from pathlib import Path

from hive.runtime.task import Task


class Planner:
    def plan(
        self,
        movie: Path,
    ) -> list[Task]:
        return [
            Task(
                command=[
                    "echo",
                    str(movie),
                ],
            )
        ]

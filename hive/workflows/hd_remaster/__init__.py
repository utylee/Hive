from __future__ import annotations

from pathlib import Path

from hive.runtime.task import Task


class HDRemasterWorkflow:
    def plan(
        self,
        source: Path,
    ) -> list[Task]:
        return [
            Task(
                command=[
                    "echo",
                    str(source),
                ],
            )
        ]

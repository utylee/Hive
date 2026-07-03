from __future__ import annotations

from pathlib import Path

from hive.runtime.task import Task
from hive.workflows.hd_remaster.probe import MovieProbe
from hive.workflows.hd_remaster.splitter import MovieSplitter


class HDRemasterWorkflow:
    def __init__(self) -> None:
        self.probe = MovieProbe()
        self.splitter = MovieSplitter()

    def plan(
        self,
        source: Path,
    ) -> list[Task]:
        duration = self.probe.duration(source)

        segments = self.splitter.split(
            duration=duration,
            segment_length=10,
        )

        tasks: list[Task] = []

        for segment in segments:
            tasks.append(
                Task(
                    command=[
                        "echo",
                        str(segment.index),
                    ],
                )
            )

        return tasks



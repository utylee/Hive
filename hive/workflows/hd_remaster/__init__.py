from __future__ import annotations

from pathlib import Path

from hive.runtime.task import Task
from hive.media.probe import MovieProbe
from hive.media.splitter import MovieSplitter


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
            output = Path(
                f"segment_{segment.index:04d}.mp4"
            )

            tasks.append(
                Task(
                    command=[
                        "ffmpeg",
                        "-y",
                        "-ss",
                        str(segment.start),
                        "-t",
                        str(segment.duration),
                        "-i",
                        str(source),
                        str(output),
                    ],
                    inputs=[
                        source,
                    ],
                    outputs=[
                        output,
                    ],
                )
            )

        return tasks



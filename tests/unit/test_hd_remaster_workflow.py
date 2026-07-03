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


# from pathlib import Path

# from hive.runtime.task import Task
# from hive.workflows.hd_remaster import HDRemasterWorkflow
# from hive.workflows.hd_remaster.splitter import MovieSplitter


# def test_hd_remaster_workflow() -> None:
#     workflow = HDRemasterWorkflow()

#     tasks = workflow.plan(Path("movie.mp4"))

#     assert len(tasks) == 3
#     assert isinstance(tasks[0], Task)
#     # assert tasks[0].command == [
#     #     "echo",
#     #     "movie.mp4",
#     # ]

#     assert tasks[0].command == [
#         "echo",
#         "0",
#     ]

#     assert tasks[1].command == [
#         "echo",
#         "1",
#     ]

#     assert tasks[2].command == [
#         "echo",
#         "2",
#     ]

# def test_split() -> None:

#     splitter = MovieSplitter()

#     segments = splitter.split(
#         duration=25,
#         segment_length=10,
#     )

#     assert len(segments) == 3

#     assert segments[0].start == 0
#     assert segments[1].start == 10
#     assert segments[2].start == 20

#     assert segments[2].duration == 5

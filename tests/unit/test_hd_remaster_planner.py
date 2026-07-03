from pathlib import Path

from hive.runtime.task import Task
from hive.workflows.hd_remaster.planner import Planner


def test_plan_single_task() -> None:
    planner = Planner()

    tasks = planner.plan(
        Path("movie.mp4"),
    )

    assert len(tasks) == 1

    assert isinstance(tasks[0], Task)

    assert tasks[0].command == [
        "echo",
        "movie.mp4",
    ]

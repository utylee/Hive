from pathlib import Path

from hive.runtime.task import Task
from hive.workflows.hd_remaster import HDRemasterWorkflow


def test_hd_remaster_workflow() -> None:
    workflow = HDRemasterWorkflow()

    tasks = workflow.plan(Path("movie.mp4"))

    assert len(tasks) == 1
    assert isinstance(tasks[0], Task)
    assert tasks[0].command == [
        "echo",
        "movie.mp4",
    ]

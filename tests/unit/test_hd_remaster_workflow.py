from pathlib import Path

from hive.runtime.task import Task
from hive.workflows.hd_remaster import HDRemasterWorkflow
from hive.workflows.hd_remaster.splitter import MovieSplitter


def test_hd_remaster_workflow() -> None:
    workflow = HDRemasterWorkflow()

    tasks = workflow.plan(Path("movie.mp4"))

    assert len(tasks) == 3
    assert isinstance(tasks[0], Task)
    # assert tasks[0].command == [
    #     "echo",
    #     "movie.mp4",
    # ]

    assert tasks[0].command == [
        "echo",
        "0",
    ]

    assert tasks[1].command == [
        "echo",
        "1",
    ]

    assert tasks[2].command == [
        "echo",
        "2",
    ]

def test_split() -> None:

    splitter = MovieSplitter()

    segments = splitter.split(
        duration=25,
        segment_length=10,
    )

    assert len(segments) == 3

    assert segments[0].start == 0
    assert segments[1].start == 10
    assert segments[2].start == 20

    assert segments[2].duration == 5

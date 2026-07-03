from pathlib import Path
from unittest.mock import patch

from hive.runtime.task import Task
from hive.workflows.hd_remaster import HDRemasterWorkflow
from hive.media.splitter import MovieSplitter


def test_hd_remaster_workflow() -> None:
    workflow = HDRemasterWorkflow()

    with patch.object(workflow.probe, "duration", return_value=25):
        tasks = workflow.plan(Path("movie.mp4"))

    assert len(tasks) == 3
    assert isinstance(tasks[0], Task)

    assert tasks[0].command[0] == "ffmpeg"
    assert tasks[0].inputs == [Path("movie.mp4")]
    assert tasks[0].outputs == [Path("segment_0000.mp4")]

    assert tasks[1].outputs == [Path("segment_0001.mp4")]
    assert tasks[2].outputs == [Path("segment_0002.mp4")]


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



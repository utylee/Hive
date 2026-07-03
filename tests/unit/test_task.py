from pathlib import Path

from hive.runtime.task import Task


def test_task() -> None:
    task = Task(
        command=["echo", "hello"],
        inputs=[
            Path("input.txt"),
        ],
        outputs=[
            Path("output.txt"),
        ],
    )

    assert task.command == ["echo", "hello"]

    assert task.inputs == [
        Path("input.txt"),
    ]

    assert task.outputs == [
        Path("output.txt"),
    ]

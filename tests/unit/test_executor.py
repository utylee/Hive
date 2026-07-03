from pathlib import Path

from hive.runtime.executor import Executor
from hive.runtime.task import Task


class DummyWorker:
    def __init__(self) -> None:
        self.tasks: list[Task] = []

    def execute(
        self,
        task: Task,
    ) -> None:
        self.tasks.append(task)


def test_executor_submit() -> None:
    worker = DummyWorker()
    executor = Executor(worker)

    task = Task(
        command=["echo", "hello"],
        inputs=[Path("input.txt")],
        outputs=[Path("output.txt")],
    )

    executor.submit(task)

    assert worker.tasks == [task]

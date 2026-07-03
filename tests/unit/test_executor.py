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


class DummyWorkerPool:
    def __init__(
        self,
        worker: DummyWorker,
    ) -> None:
        self.worker = worker

    def acquire(self) -> DummyWorker:
        return self.worker


def test_executor_submit() -> None:
    worker = DummyWorker()
    pool = DummyWorkerPool(worker)
    executor = Executor(pool)

    task = Task(
        command=["echo", "hello"],
        inputs=[Path("input.txt")],
        outputs=[Path("output.txt")],
    )

    executor.submit(task)

    assert worker.tasks == [task]


def test_executor_map() -> None:
    worker = DummyWorker()
    pool = DummyWorkerPool(worker)
    executor = Executor(pool)

    tasks = [
        Task(command=["echo", "one"]),
        Task(command=["echo", "two"]),
    ]

    executor.map(tasks)

    assert worker.tasks == tasks

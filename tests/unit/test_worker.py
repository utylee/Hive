from pathlib import Path

from hive.runtime.task import Task
from hive.runtime.worker import Worker


class DummyTransport:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def upload(self, source: Path, destination: str) -> None:
        self.calls.append(("upload", source, destination))

    def execute(
        self,
        command: list[str],
        *,
        cwd: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.calls.append(("execute", command))

    def download(
        self,
        source: str,
        destination: Path,
    ) -> None:
        self.calls.append(("download", source, destination))


def test_worker_execute() -> None:
    transport = DummyTransport()

    worker = Worker(transport)

    task = Task(
        command=["echo", "hello"],
        inputs=[
            Path("input.txt"),
        ],
        outputs=[
            Path("output.txt"),
        ],
    )

    worker.execute(task)

    assert transport.calls == [
        (
            "upload",
            Path("input.txt"),
            "input.txt",
        ),
        (
            "execute",
            ["echo", "hello"],
        ),
        (
            "download",
            "output.txt",
            Path("output.txt"),
        ),
    ]

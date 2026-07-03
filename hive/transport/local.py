from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class LocalTransport:
    def __init__(
        self,
        workspace: Path,
    ) -> None:
        self.workspace = workspace

    def upload(
        self,
        source: Path,
    ) -> None:
        destination = self.workspace / "input" / source.name

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(source, destination)


    def execute(
        self,
        command: list[str],
        *,
        cwd: str | None = None,
        timeout: float | None = None,
    ) -> None:
        subprocess.run(
            command,
            cwd=cwd,
            timeout=timeout,
            check=True,
        )


    def download(
        self,
        destination: Path,
    ) -> None:
        source = self.workspace / "output" / destination.name

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(source, destination)


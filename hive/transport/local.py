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
        destination: str,
    ) -> None:
        target = self.workspace / destination

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(source, target)

    def execute(
        self,
        command: list[str],
        *,
        cwd: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.workspace.mkdir(
            parents=True,
            exist_ok=True,
        )

        subprocess.run(
            command,
            cwd=cwd or self.workspace,
            timeout=timeout,
            check=True,
        )

    def download(
        self,
        source: str,
        destination: Path,
    ) -> None:
        origin = self.workspace / source

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(origin, destination)

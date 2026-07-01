from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class LocalTransport:
    def upload(
        self,
        source: Path,
        destination: str,
    ) -> None:
        dest = Path(destination)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)

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
        source: str,
        destination: Path,
    ) -> None:
        src = Path(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, destination)

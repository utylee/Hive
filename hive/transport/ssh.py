from __future__ import annotations

import subprocess
from pathlib import Path


class SSHTransport:
    def __init__(
        self,
        host: str,
    ) -> None:
        self.host = host

    def upload(
        self,
        source: Path,
        destination: str,
    ) -> None:
        subprocess.run(
            [
                "rsync",
                "-az",
                str(source),
                f"{self.host}:{destination}",
            ],
            check=True,
        )

    def execute(
        self,
        command: list[str],
        *,
        cwd: str | None = None,
        timeout: float | None = None,
    ) -> None:
        if cwd is not None:
            raise NotImplementedError(
                "cwd is not supported yet."
            )

        subprocess.run(
            [
                "ssh",
                self.host,
                *command,
            ],
            timeout=timeout,
            check=True,
        )

    def download(
        self,
        source: str,
        destination: Path,
    ) -> None:
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        subprocess.run(
            [
                "rsync",
                "-az",
                f"{self.host}:{source}",
                str(destination),
            ],
            check=True,
        )

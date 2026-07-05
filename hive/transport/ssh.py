from __future__ import annotations

import subprocess
import shlex
from pathlib import Path


class SSHTransport:
    # def __init__(
    #     self,
    #     host: str,
    # ) -> None:
    #     self.host = host

    def __init__(
        self,
        host: str,
        workspace: Path,
    ) -> None:
        self.host = host
        self.workspace = workspace

    def upload(
        self,
        source: Path,
        destination: str,
    ) -> None:
        subprocess.run(
            [
                "ssh",
                self.host,
                "mkdir",
                "-p",
                str(self.workspace),
            ],
            check=True,
        )

        subprocess.run(
            [
                "rsync",
                "-az",
                str(source),
                f"{self.host}:{self.workspace / destination}",
            ],
            check=True,
        )


        # subprocess.run(
        #     [
        #         "rsync",
        #         "-az",
        #         str(source),
        #         f"{self.host}:{destination}",
        #     ],
        #     check=True,
        # )


    
    def execute(
        self,
        command: list[str],
        *,
        cwd: str | None = None,
        timeout: float | None = None,
    ) -> None:

        remote = (
            f"cd {shlex.quote(str(self.workspace))} && "
            + shlex.join(command)
        )

        subprocess.run(
            [
                "ssh",
                self.host,
                # "bash",
                # "-lc",
                remote,
            ],
            timeout=timeout,
            check=True,
        )
        
        # if cwd is not None:
        #     raise NotImplementedError(
        #         "cwd is not supported."
        #     )

        # remote = (
        #     f"cd {shlex.quote(str(self.workspace))} && "
        #     + shlex.join(command)
        # )

        # subprocess.run(
        #     [
        #         "ssh",
        #         self.host,
        #         "bash",
        #         "-lc",
        #         remote,
        #     ],
        #     timeout=timeout,
        #     check=True,
        # )

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
                f"{self.host}:{self.workspace / source}",
                str(destination),
            ],
            check=True,
        )

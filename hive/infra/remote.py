from __future__ import annotations

from pathlib import Path
import subprocess


class RemoteError(RuntimeError):
    pass


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        raise RemoteError(
            "\n".join([
                f"Command : {' '.join(args)}",
                f"Exit    : {result.returncode}",
                f"stdout:\n{result.stdout}",
                f"stderr:\n{result.stderr}",
            ])
        )

    return result

def run(server, command: str) -> str:
    return _run(["ssh", server.ssh_alias, command]).stdout

# def exec(server, command: str) -> str:
#     return _run(
#         ["ssh", server.ssh_alias, command]
#     ).stdout


def mkdir(server, remote_dir: str):
    exec(server, f"mkdir -p '{remote_dir}'")


def copy_to(server, local: str | Path, remote: str):
    _run([
        "rsync",
        "-az",
        "--info=progress2",
        str(local),
        f"{server.ssh_alias}:{remote}",
    ])


def copy_from(server, remote: str, local: str | Path):
    _run([
        "rsync",
        "-az",
        "--info=progress2",
        f"{server.ssh_alias}:{remote}",
        str(local),
    ])



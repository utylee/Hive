from __future__ import annotations

import subprocess
from pathlib import Path


class RemoteError(RuntimeError):
    pass


def run_local(
    args: list[str],
    *,
    check: bool = True,
) -> subprocess.CompletedProcess:
    result = subprocess.run(
        args,
        text=True,
        capture_output=True,
    )

    if check and result.returncode != 0:
        cmd = " ".join(args)
        raise RemoteError(
            f"Command failed: {cmd}\n"
            f"returncode={result.returncode}\n"
            f"stdout={result.stdout}\n"
            f"stderr={result.stderr}"
        )

    return result



def exec(
    alias: str,
    command: str,
    *,
    check: bool = True,
) -> subprocess.CompletedProcess:
    return run_local(
        ["ssh", alias, command],
        check=check,
    )


def mkdir(
    alias: str,
    remote_dir: str,
) -> None:
    exec(alias, f"mkdir -p {shell_quote(remote_dir)}")


def copy_to(
    local: str | Path,
    alias: str,
    remote: str,
) -> None:
    run_local(
        [
            "rsync",
            "-az",
            "--delete",
            str(local),
            f"{alias}:{remote}",
        ]
    )


def copy_from(
    alias: str,
    remote: str,
    local: str | Path,
) -> None:
    run_local(
        [
            "rsync",
            "-az",
            f"{alias}:{remote}",
            str(local),
        ]
    )


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"



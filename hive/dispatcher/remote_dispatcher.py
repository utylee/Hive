from __future__ import annotations

from pathlib import Path

from hive.core import remote


def dispatch_remote_job(server, local_job_dir: Path) -> None:
    remote_root = server.worker_root.rstrip("/")
    remote_job_dir = f"{remote_root}/{local_job_dir.name}"

    alias = server.ssh_alias
    hive_root = getattr(server, "hive_root", "/home/utylee/temp/Hive")
    python = f"{hive_root}/.venv/bin/python"

    remote.mkdir(alias, remote_root)

    remote.copy_to(
        str(local_job_dir) + "/",
        alias,
        remote_job_dir + "/",
    )

    remote.exec(
        alias,
        f"{python} -m hive.worker.main run {remote_job_dir}",
    )

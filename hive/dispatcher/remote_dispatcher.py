from __future__ import annotations

from pathlib import Path

from hive.core import remote


def dispatch_remote_job(server, local_job_dir: Path) -> None:
    remote_root = server.worker_root.rstrip("/")
    remote_job_dir = f"{remote_root}/{local_job_dir.name}"

    alias = server.ssh_alias

    remote.mkdir(alias, remote_root)

    remote.copy_to(
        str(local_job_dir) + "/",
        alias,
        remote_job_dir + "/",
    )

    remote.exec(
        alias,
        f"hive-worker run {remote_job_dir}",
    )

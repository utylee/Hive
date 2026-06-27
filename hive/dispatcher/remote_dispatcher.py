from __future__ import annotations

from pathlib import Path
import json

from hive.core import remote

def load_result(job_dir: Path) -> dict:
    return json.loads(
        (job_dir / "result.json").read_text(
            encoding="utf-8",
        )
    )


def dispatch_remote_job(server, local_job_dir: Path): 
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

    remote.copy_from(
        str(local_job_dir / "result.json"),
        alias,
        f"{remote_job_dir}/result.json",
    )

    return load_result(local_job_dir)

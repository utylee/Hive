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
    python = server.hive_python
    hive_root = server.hive_root.rstrip("/")

    local_project_root = Path(__file__).resolve().parents[2]
    local_hive_dir = local_project_root / "hive"
    remote_hive_dir = f"{hive_root}/hive"

    remote.mkdir(
        alias,
        hive_root,
    )

    remote.copy_to(
        str(local_hive_dir) + "/",
        alias,
        remote_hive_dir + "/",
    )


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

    # remote.copy_from(
    #     str(local_job_dir / "result.json"),
    #     alias,
    #     f"{remote_job_dir}/result.json",
    # )

    # return load_result(local_job_dir)

    remote.copy_from(
        str(local_job_dir / "result.json"),
        alias,
        f"{remote_job_dir}/result.json",
    )

    result = load_result(local_job_dir)

    if result.get("outputs"):
        local_output_dir = local_job_dir / "output"
        local_output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        remote.copy_from(
            str(local_output_dir) + "/",
            alias,
            f"{remote_job_dir}/output/",
        )

    return result



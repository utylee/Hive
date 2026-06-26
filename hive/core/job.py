from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def make_job_id(input_path: Path) -> str:
    stem = input_path.stem.replace(" ", "_")
    return f"{stem}-{uuid.uuid4().hex[:8]}"


@dataclass
class JobPaths:
    remote_job_dir: str
    remote_input_dir: str
    remote_output_dir: str
    remote_logs_dir: str
    remote_job_json: str
    remote_result_json: str


def build_job_paths(worker_root: str, job_id: str) -> JobPaths:
    remote_job_dir = f"{worker_root.rstrip('/')}/{job_id}"

    return JobPaths(
        remote_job_dir=remote_job_dir,
        remote_input_dir=f"{remote_job_dir}/input",
        remote_output_dir=f"{remote_job_dir}/output",
        remote_logs_dir=f"{remote_job_dir}/logs",
        remote_job_json=f"{remote_job_dir}/job.json",
        remote_result_json=f"{remote_job_dir}/result.json",
    )


def make_job_json(
    *,
    job_id: str,
    job_type: str,
    input_file: Path,
    server_name: str,
    server: dict[str, Any],
    paths: JobPaths,
    profile: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": job_id,
        "type": job_type,
        "server_name": server_name,
        "server": server,
        "input": {
            "filename": input_file.name,
            "source": paths.remote_input_dir,
        },
        "output": {
            "target": paths.remote_output_dir,
        },
        "logs": {
            "dir": paths.remote_logs_dir,
        },
        "profile": profile,
    }


def write_job_json(path: Path, job: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(job, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

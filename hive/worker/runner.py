from __future__ import annotations

import json
import time
from pathlib import Path

# from hive.worker.dummy import DummyExecutor
# from hive.worker.comfy import ComfyExecutor

from hive.executors.dummy import DummyExecutor
from hive.executors.comfy import ComfyExecutor



def load_manifest(job_dir: Path) -> dict:
    manifest_path = job_dir / "manifest.json"

    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest.json not found: {manifest_path}")

    return json.loads(manifest_path.read_text(encoding="utf-8"))


def write_result(job_dir: Path, result: dict) -> None:
    result_path = job_dir / "result.json"

    result_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def run_job(job_dir: Path) -> int:
    if not job_dir.exists():
        return 1

    started = time.time()

    try:
        manifest = load_manifest(job_dir)


        # executor = DummyExecutor()

        job_type = manifest.get("type")

        if job_type == "dummy":
            executor = DummyExecutor()

        elif job_type == "comfy":
            executor = ComfyExecutor()

        else:
            raise ValueError(f"Unknown job type: {job_type}")



        result = executor.execute(job_dir, manifest)

        result["job_id"] = manifest.get("id")
        result["job_type"] = manifest.get("type")
        result["elapsed_sec"] = round(time.time() - started, 3)

        write_result(job_dir, result)
        return 0

    except Exception as e:
        result = {
            "ok": False,
            "error": str(e),
            "elapsed_sec": round(time.time() - started, 3),
        }

        write_result(job_dir, result)
        return 1


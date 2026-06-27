from pathlib import Path
import json
import shutil

from hive.worker.runner import run_job

def test_worker_runs_comfy_executor() -> None:
    job_dir = Path("/tmp/hive_worker_comfy_test")

    if job_dir.exists():
        shutil.rmtree(job_dir)

    job_dir.mkdir(parents=True)

    manifest = {
        "version": 1,
        "id": "job-comfy-001",
        "project": "vhs_restore",
        "type": "comfy",
        "source": "/tmp/input.mp4",
        "parameters": {},
        "metadata": {},
    }

    (job_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    rc = run_job(job_dir)

    assert rc == 0

    result = json.loads(
        (job_dir / "result.json").read_text(encoding="utf-8")
    )

    assert result["ok"] is True
    assert result["executor"] == "comfy"
    assert result["job_id"] == "job-comfy-001"
    assert result["job_type"] == "comfy"


def test_worker_reads_manifest_and_writes_result() -> None:
    job_dir = Path("/tmp/hive_worker_test")

    if job_dir.exists():
        shutil.rmtree(job_dir)

    job_dir.mkdir(parents=True)

    manifest = {
        "version": 1,
        "id": "job001",
        "project": "vhs_restore",
        "type": "dummy",
        "source": "/tmp/input.mp4",
        "parameters": {},
        "metadata": {},
    }

    (job_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    rc = run_job(job_dir)

    assert rc == 0

    result_path = job_dir / "result.json"

    assert result_path.exists()

    result = json.loads(result_path.read_text(encoding="utf-8"))

    assert result["ok"] is True
    assert result["job_id"] == "job001"
    assert result["job_type"] == "dummy"

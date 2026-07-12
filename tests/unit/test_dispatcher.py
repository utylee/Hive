from pathlib import Path
import shutil
from types import SimpleNamespace

from hive.dispatcher.dispatcher import Dispatcher


def test_dispatcher_run_once(monkeypatch) -> None:
    jobs = Path("/tmp/hive_jobs")
    work = Path("/tmp/hive_work")

    for p in (jobs, work):
        if p.exists():
            shutil.rmtree(p)
        p.mkdir(parents=True)

    (jobs / "001.mp4").touch()
    (jobs / "002.mp4").touch()

    server = SimpleNamespace(
        enabled=True,
        ssh_alias="dummy",
        worker_root="/tmp/hive_jobs",
        comfy_url="http://localhost:8188",
        comfy_input_batches="/data/temp/ComfyUI/input/batches",
    )

    def fake_dispatch_remote_job(server, job_dir):
        return {"ok": True, "executor": "dummy"}

    monkeypatch.setattr(
        "hive.dispatcher.dispatcher.dispatch_remote_job",
        fake_dispatch_remote_job,
    )

    dispatcher = Dispatcher(
        jobs_dir=jobs,
        work_root=work,
        project="vhs_restore",
        job_type="comfy",
        servers=[server],
    )

    created = dispatcher.run_once()

    assert created == 2

    manifests = list(work.glob("*/manifest.json"))

    assert len(manifests) == 2


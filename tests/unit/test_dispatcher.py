from pathlib import Path
import shutil

from hive.dispatcher.dispatcher import Dispatcher


def test_dispatcher_run_once() -> None:
    jobs = Path("/tmp/hive_jobs")
    work = Path("/tmp/hive_work")

    for p in (jobs, work):
        if p.exists():
            shutil.rmtree(p)
        p.mkdir(parents=True)

    (jobs / "001.mp4").touch()
    (jobs / "002.mp4").touch()

    dispatcher = Dispatcher(
        jobs_dir=jobs,
        work_root=work,
        project="vhs_restore",
        job_type="comfy",
    )

    created = dispatcher.run_once()

    assert created == 2

    manifests = list(work.glob("*/manifest.json"))

    assert len(manifests) == 2

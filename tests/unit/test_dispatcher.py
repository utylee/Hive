from pathlib import Path
import shutil
import json
import time
from types import SimpleNamespace

from hive.dispatcher.dispatcher import Dispatcher
from threading import Lock


def test_dispatcher_run_once(tmp_path: Path, monkeypatch) -> None:
    jobs = Path("/tmp/hive_jobs")
    work = Path("/tmp/hive_work")

    for p in (jobs, work):
        if p.exists():
            shutil.rmtree(p)
        p.mkdir(parents=True)

    (jobs / "001.mp4").touch()
    (jobs / "002.mp4").touch()

    # server = SimpleNamespace(
    #     enabled=True,
    #     ssh_alias="dummy",
    #     worker_root="/tmp/hive_jobs",
    #     comfy_url="http://localhost:8188",
    #     comfy_input_batches="/data/temp/ComfyUI/input/batches",
    # )

    server = SimpleNamespace(
        name="dummy",
        enabled=True,
        ssh_alias="dummy",
        worker_root="/tmp/hive_jobs",
        comfy_url="http://localhost:8188",
        comfy_input_batches="/data/temp/ComfyUI/input/batches",
        profile={
            "frames_per_batch": 16,
        },
    )

    def fake_dispatch_remote_job(server, job_dir):
        return {"ok": True, "executor": "dummy"}

    monkeypatch.setattr(
        "hive.dispatcher.dispatcher.dispatch_remote_job",
        fake_dispatch_remote_job,
    )

    workflow = tmp_path / "workflow.json"
    workflow.write_text("{}", encoding="utf-8")

    dispatcher = Dispatcher(
        jobs_dir=jobs,
        work_root=work,
        project="vhs_restore",
        job_type="comfy",
        servers=[server],
        parameters={
            "workflow": str(workflow),
        },
    )

    created = dispatcher.run_once()

    assert created == 2

    manifests = list(work.glob("*/manifest.json"))

    assert len(manifests) == 2

    assert not (jobs / "001.mp4").exists()
    assert not (jobs / "002.mp4").exists()

    assert (jobs / "done" / "001.mp4").exists()
    assert (jobs / "done" / "002.mp4").exists()


def test_dispatcher_moves_failed_input(
        tmp_path: Path,
        monkeypatch,
    ) -> None:
        jobs = tmp_path / "jobs"
        work = tmp_path / "work"

        jobs.mkdir()
        work.mkdir()

        source = jobs / "broken.mp4"
        source.touch()

        workflow = tmp_path / "workflow.json"
        workflow.write_text("{}", encoding="utf-8")

        server = SimpleNamespace(
            name="dummy",
            enabled=True,
            ssh_alias="dummy",
            worker_root="/tmp/hive_jobs",
            comfy_url="http://localhost:8188",
            comfy_input_batches="/data/temp/ComfyUI/input/batches",
            profile={
                "frames_per_batch": 16,
            },
        )

        def fake_dispatch_remote_job(server, job_dir):
            raise RuntimeError("remote failure")

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
            parameters={
                "workflow": str(workflow),
            },
        )

        created = dispatcher.run_once()

        assert created == 0
        assert not source.exists()
        assert (jobs / "failed" / "broken.mp4").exists()

        error_files = list(
            work.glob("*/error.txt")
        )

        assert len(error_files) == 1
        assert "remote failure" in error_files[0].read_text(
            encoding="utf-8",
        )


def test_dispatcher_increments_retry_count(
        tmp_path: Path,
        monkeypatch,
    ) -> None:
        jobs = tmp_path / "jobs"
        work = tmp_path / "work"

        jobs.mkdir()
        work.mkdir()

        source = jobs / "broken.mp4"
        source.touch()

        retry_path = jobs / "broken.mp4.retry.json"
        retry_path.write_text(
            json.dumps(
                {
                    "retry_count": 1,
                }
            ),
            encoding="utf-8",
        )

        workflow = tmp_path / "workflow.json"
        workflow.write_text("{}", encoding="utf-8")

        server = SimpleNamespace(
            name="dummy",
            enabled=True,
            ssh_alias="dummy",
            worker_root="/tmp/hive_jobs",
            comfy_url="http://localhost:8188",
            comfy_input_batches="/data/temp/ComfyUI/input/batches",
            profile={
                "frames_per_batch": 16,
            },
        )

        def fake_dispatch_remote_job(server, job_dir):
            raise RuntimeError("remote failure again")

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
            parameters={
                "workflow": str(workflow),
            },
        )

        created = dispatcher.run_once()

        assert created == 0

        failed_retry_path = (
            jobs
            / "failed"
            / "broken.mp4.retry.json"
        )

        retry_data = json.loads(
            failed_retry_path.read_text(
                encoding="utf-8",
            )
        )

        assert retry_data["retry_count"] == 2
        assert "remote failure again" in retry_data["last_error"]

def test_dispatcher_runs_jobs_in_parallel(
    tmp_path: Path,
    monkeypatch,
) -> None:
    jobs = tmp_path / "jobs"
    work = tmp_path / "work"

    jobs.mkdir()
    work.mkdir()

    (jobs / "001.mp4").touch()
    (jobs / "002.mp4").touch()

    workflow = tmp_path / "workflow.json"
    workflow.write_text("{}", encoding="utf-8")

    servers = [
        SimpleNamespace(
            name="server-a",
            enabled=True,
            ssh_alias="server-a",
            worker_root="/tmp/hive_jobs",
            comfy_url="http://localhost:8188",
            comfy_input_batches="/tmp/comfy-a",
            profile={"frames_per_batch": 16},
        ),
        SimpleNamespace(
            name="server-b",
            enabled=True,
            ssh_alias="server-b",
            worker_root="/tmp/hive_jobs",
            comfy_url="http://localhost:8188",
            comfy_input_batches="/tmp/comfy-b",
            profile={"frames_per_batch": 16},
        ),
    ]

    started_servers = []

    def fake_dispatch_remote_job(server, job_dir):
        started_servers.append(server.name)
        time.sleep(0.3)

        return {
            "ok": True,
            "executor": "dummy",
        }

    monkeypatch.setattr(
        "hive.dispatcher.dispatcher.dispatch_remote_job",
        fake_dispatch_remote_job,
    )

    dispatcher = Dispatcher(
        jobs_dir=jobs,
        work_root=work,
        project="vhs_restore",
        job_type="comfy",
        servers=servers,
        parameters={
            "workflow": str(workflow),
        },
        max_workers=2,
    )

    started_at = time.monotonic()

    completed = dispatcher.run_once()

    elapsed = time.monotonic() - started_at

    assert completed == 2
    assert set(started_servers) == {
        "server-a",
        "server-b",
    }

    # 순차라면 약 0.6초이므로 병렬 실행 여부 확인
    assert elapsed < 0.55

def test_dispatcher_serializes_jobs_on_same_server(
    tmp_path: Path,
    monkeypatch,
) -> None:
    jobs = tmp_path / "jobs"
    work = tmp_path / "work"

    jobs.mkdir()
    work.mkdir()

    (jobs / "001.mp4").touch()
    (jobs / "002.mp4").touch()

    workflow = tmp_path / "workflow.json"
    workflow.write_text("{}", encoding="utf-8")

    server = SimpleNamespace(
        name="server-a",
        enabled=True,
        ssh_alias="server-a",
        worker_root="/tmp/hive_jobs",
        comfy_url="http://localhost:8188",
        comfy_input_batches="/tmp/comfy-a",
        profile={
            "frames_per_batch": 16,
        },
    )

    active = 0
    max_active = 0
    state_lock = Lock()

    def fake_dispatch_remote_job(server, job_dir):
        nonlocal active, max_active

        with state_lock:
            active += 1
            max_active = max(
                max_active,
                active,
            )

        time.sleep(0.2)

        with state_lock:
            active -= 1

        return {
            "ok": True,
            "executor": "dummy",
        }

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
        parameters={
            "workflow": str(workflow),
        },
        max_workers=2,
    )

    completed = dispatcher.run_once()

    assert completed == 2
    assert max_active == 1

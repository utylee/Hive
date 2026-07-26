from pathlib import Path
import shutil
import json
import time
from types import SimpleNamespace
from threading import Lock
import pytest

from hive.dispatcher.dispatcher import Dispatcher
from hive.server import Server


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
        comfy_output_dir="/tmp/comfy-output",
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
            comfy_output_dir="/tmp/comfy-output",
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
            comfy_output_dir="/tmp/comfy-output",
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
            comfy_output_dir="/tmp/comfy-output",
            profile={"frames_per_batch": 16},
        ),
        SimpleNamespace(
            name="server-b",
            enabled=True,
            ssh_alias="server-b",
            worker_root="/tmp/hive_jobs",
            comfy_url="http://localhost:8188",
            comfy_input_batches="/tmp/comfy-b",
            comfy_output_dir="/tmp/comfy-output",
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
        comfy_output_dir="/tmp/comfy-output",
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

def test_dispatcher_retries_failed_job_on_another_server(
    tmp_path,
    monkeypatch,
):
    jobs_dir = tmp_path / "jobs"
    work_root = tmp_path / "work"
    workflow = tmp_path / "workflow.json"

    jobs_dir.mkdir()
    workflow.write_text(
        "{}",
        encoding="utf-8",
    )

    source = jobs_dir / "segment.mp4"
    source.write_bytes(b"video")

    servers = [
        Server(
            name="server-a",
            ssh_alias="server-a",
            worker_root="/tmp/hive_jobs",
            comfy_url="http://server-a",
            comfy_input_batches="/tmp/input",
            comfy_output_dir="/tmp/output",
            hive_root="/tmp/Hive",
            hive_python="/tmp/Hive/.venv/bin/python",
            enabled=True,
            profile={},
        ),
        Server(
            name="server-b",
            ssh_alias="server-b",
            worker_root="/tmp/hive_jobs",
            comfy_url="http://server-b",
            comfy_input_batches="/tmp/input",
            comfy_output_dir="/tmp/output",
            hive_root="/tmp/Hive",
            hive_python="/tmp/Hive/.venv/bin/python",
            enabled=True,
            profile={},
        ),
    ]

    calls = []

    def fake_dispatch_remote_job(
        server,
        job_dir,
    ):
        calls.append(server.name)

        if server.name == "server-a":
            raise RuntimeError("temporary failure")

        return {
            "ok": True,
            "outputs": [],
        }

    monkeypatch.setattr(
        "hive.dispatcher.dispatcher.dispatch_remote_job",
        fake_dispatch_remote_job,
    )

    dispatcher = Dispatcher(
        jobs_dir=jobs_dir,
        work_root=work_root,
        project="test",
        job_type="comfy",
        servers=servers,
        parameters={
            "workflow": str(workflow),
        },
    )

    completed = dispatcher.run_once()

    assert completed == 1
    assert calls == [
        "server-a",
        "server-b",
    ]

    assert (
        jobs_dir / "done" / source.name
    ).exists()

    assert not (
        jobs_dir / "failed" / source.name
    ).exists()

    assert not (
        jobs_dir
        / f"{source.name}.retry.json"
    ).exists()


def test_server_rejoins_after_cooldown(
    tmp_path,
    monkeypatch,
):
    jobs_dir = tmp_path / "jobs"
    work_root = tmp_path / "work"
    workflow = tmp_path / "workflow.json"

    jobs_dir.mkdir()
    workflow.write_text(
        "{}",
        encoding="utf-8",
    )

    for index in range(3):
        (
            jobs_dir / f"segment-{index}.mp4"
        ).write_bytes(b"video")

    server = Server(
        name="server-a",
        ssh_alias="server-a",
        worker_root="/tmp/hive_jobs",
        comfy_url="http://server-a",
        comfy_input_batches="/tmp/input",
        comfy_output_dir="/tmp/output",
        hive_root="/tmp/Hive",
        hive_python="/tmp/Hive/.venv/bin/python",
        enabled=True,
        profile={},
    )

    calls = []

    def fake_dispatch_remote_job(
        server,
        job_dir,
    ):
        calls.append(server.name)
        raise RuntimeError("remote failure")

    monkeypatch.setattr(
        "hive.dispatcher.dispatcher.dispatch_remote_job",
        fake_dispatch_remote_job,
    )

    dispatcher = Dispatcher(
        jobs_dir=jobs_dir,
        work_root=work_root,
        project="test",
        job_type="comfy",
        servers=[server],
        parameters={
            "workflow": str(workflow),
        },
        server_failure_threshold=2,
        server_cooldown_seconds=0.01,
    )

    completed = dispatcher.run_once()

    assert completed == 0
    assert len(calls) == 3

    assert (
        dispatcher._server_failures["server-a"]
        == 3
    )


def test_server_events_are_written(
    tmp_path,
):
    jobs_dir = tmp_path / "jobs"
    work_root = tmp_path / "work"

    jobs_dir.mkdir()

    server = Server(
        name="server-a",
        ssh_alias="server-a",
        worker_root="/tmp/hive_jobs",
        comfy_url="http://server-a",
        comfy_input_batches="/tmp/input",
        comfy_output_dir="/tmp/output",
        hive_root="/tmp/Hive",
        hive_python="/tmp/Hive/.venv/bin/python",
        enabled=True,
        profile={},
    )

    dispatcher = Dispatcher(
        jobs_dir=jobs_dir,
        work_root=work_root,
        project="test",
        job_type="comfy",
        servers=[server],
        server_failure_threshold=2,
        server_cooldown_seconds=60.0,
    )

    dispatcher._record_server_failure(server)
    dispatcher._record_server_failure(server)
    dispatcher._record_server_success(server)

    event_path = (
        work_root / "server_events.jsonl"
    )

    records = [
        json.loads(line)
        for line in event_path.read_text(
            encoding="utf-8",
        ).splitlines()
    ]

    assert [
        record["event"]
        for record in records
    ] == [
        "server_failure",
        "server_failure",
        "server_cooldown",
        "server_recovered",
    ]

    assert records[0][
        "consecutive_failures"
    ] == 1

    assert records[1][
        "consecutive_failures"
    ] == 2

    assert records[2][
        "cooldown_seconds"
    ] == 60.0

    assert records[3][
        "previous_failures"
    ] == 2

    assert all(
        record["server"] == "server-a"
        for record in records
    )

    assert all(
        "timestamp" in record
        for record in records
    )

def test_server_state_persists_across_dispatcher_restart(
    tmp_path,
):
    jobs_dir = tmp_path / "jobs"
    work_root = tmp_path / "work"

    jobs_dir.mkdir()

    server = Server(
        name="server-a",
        ssh_alias="server-a",
        worker_root="/tmp/hive_jobs",
        comfy_url="http://server-a",
        comfy_input_batches="/tmp/input",
        comfy_output_dir="/tmp/output",
        hive_root="/tmp/Hive",
        hive_python="/tmp/Hive/.venv/bin/python",
        enabled=True,
        profile={},
    )

    first = Dispatcher(
        jobs_dir=jobs_dir,
        work_root=work_root,
        project="test",
        job_type="comfy",
        servers=[server],
        server_failure_threshold=2,
        server_cooldown_seconds=60.0,
    )

    first._record_server_failure(server)
    first._record_server_failure(server)

    state_path = (
        work_root / "server_state.json"
    )

    assert state_path.exists()

    second = Dispatcher(
        jobs_dir=jobs_dir,
        work_root=work_root,
        project="test",
        job_type="comfy",
        servers=[server],
        server_failure_threshold=2,
        server_cooldown_seconds=60.0,
    )

    assert (
        second._server_failures["server-a"]
        == 2
    )

    assert (
        second._server_cooldown_until[
            "server-a"
        ]
        > time.time()
    )

    assert (
        second._server_is_available(server)
        is False
    )


def test_corrupt_server_state_is_preserved_and_ignored(
    tmp_path,
):
    jobs_dir = tmp_path / "jobs"
    work_root = tmp_path / "work"

    jobs_dir.mkdir()
    work_root.mkdir()

    state_path = (
        work_root / "server_state.json"
    )

    state_path.write_text(
        "{invalid json",
        encoding="utf-8",
    )

    server = Server(
        name="server-a",
        ssh_alias="server-a",
        worker_root="/tmp/hive_jobs",
        comfy_url="http://server-a",
        comfy_input_batches="/tmp/input",
        comfy_output_dir="/tmp/output",
        hive_root="/tmp/Hive",
        hive_python=(
            "/tmp/Hive/.venv/bin/python"
        ),
        enabled=True,
        profile={},
    )

    dispatcher = Dispatcher(
        jobs_dir=jobs_dir,
        work_root=work_root,
        project="test",
        job_type="comfy",
        servers=[server],
    )

    corrupt_path = (
        work_root
        / "server_state.json.corrupt"
    )

    assert state_path.exists() is False
    assert corrupt_path.exists()
    assert (
        corrupt_path.read_text(
            encoding="utf-8",
        )
        == "{invalid json"
    )

    assert (
        dispatcher._server_failures[
            "server-a"
        ]
        == 0
    )

    assert (
        dispatcher._server_cooldown_until[
            "server-a"
        ]
        == 0.0
    )

@pytest.mark.parametrize(
    "state_text",
    [
        "[]",
        '{"server-a": []}',
        (
            '{"server-a": {'
            '"consecutive_failures": -1'
            "}}"
        ),
        (
            '{"server-a": {'
            '"cooldown_until": "not-a-date"'
            "}}"
        ),
    ],
)
def test_invalid_server_state_is_preserved_and_ignored(
    tmp_path,
    state_text,
):
    jobs_dir = tmp_path / "jobs"
    work_root = tmp_path / "work"

    jobs_dir.mkdir()
    work_root.mkdir()

    state_path = (
        work_root / "server_state.json"
    )

    state_path.write_text(
        state_text,
        encoding="utf-8",
    )

    server = Server(
        name="server-a",
        ssh_alias="server-a",
        worker_root="/tmp/hive_jobs",
        comfy_url="http://server-a",
        comfy_input_batches="/tmp/input",
        comfy_output_dir="/tmp/output",
        hive_root="/tmp/Hive",
        hive_python=(
            "/tmp/Hive/.venv/bin/python"
        ),
        enabled=True,
        profile={},
    )

    dispatcher = Dispatcher(
        jobs_dir=jobs_dir,
        work_root=work_root,
        project="test",
        job_type="comfy",
        servers=[server],
    )

    corrupt_path = (
        work_root
        / "server_state.json.corrupt"
    )

    assert not state_path.exists()
    assert corrupt_path.exists()

    assert (
        corrupt_path.read_text(
            encoding="utf-8",
        )
        == state_text
    )

    assert (
        dispatcher._server_failures[
            "server-a"
        ]
        == 0
    )

    assert (
        dispatcher._server_cooldown_until[
            "server-a"
        ]
        == 0.0
    )

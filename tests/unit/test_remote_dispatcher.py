from pathlib import Path
from types import SimpleNamespace

from hive.dispatcher.remote_dispatcher import dispatch_remote_job


def test_dispatch_remote_job_syncs_hive_code(
    tmp_path,
    monkeypatch,
):
    job_dir = tmp_path / "job-123"
    job_dir.mkdir()

    (job_dir / "result.json").write_text(
        '{"ok": true, "outputs": []}',
        encoding="utf-8",
    )

    server = SimpleNamespace(
        ssh_alias="m5",
        worker_root="/tmp/hive_jobs",
        hive_root="/data/temp/Hive",
        hive_python="/data/temp/Hive/.venv/bin/python",
    )

    mkdir_calls = []
    copy_to_calls = []
    exec_calls = []
    copy_from_calls = []

    monkeypatch.setattr(
        "hive.dispatcher.remote_dispatcher.remote.mkdir",
        lambda alias, remote_dir: mkdir_calls.append(
            (alias, remote_dir)
        ),
    )

    monkeypatch.setattr(
        "hive.dispatcher.remote_dispatcher.remote.copy_to",
        lambda local, alias, remote: copy_to_calls.append(
            (local, alias, remote)
        ),
    )

    monkeypatch.setattr(
        "hive.dispatcher.remote_dispatcher.remote.exec",
        lambda alias, command: exec_calls.append(
            (alias, command)
        ),
    )

    monkeypatch.setattr(
        "hive.dispatcher.remote_dispatcher.remote.copy_from",
        lambda local, alias, remote: copy_from_calls.append(
            (local, alias, remote)
        ),
    )

    result = dispatch_remote_job(
        server,
        job_dir,
    )

    assert result == {
        "ok": True,
        "outputs": [],
    }

    assert mkdir_calls == [
        ("m5", "/data/temp/Hive"),
        ("m5", "/tmp/hive_jobs"),
    ]

    assert len(copy_to_calls) == 2

    hive_copy = copy_to_calls[0]

    assert hive_copy[1:] == (
        "m5",
        "/data/temp/Hive/hive/",
    )

    assert hive_copy[0].endswith(
        "/hive/"
    )

    assert copy_to_calls[1] == (
        str(job_dir) + "/",
        "m5",
        "/tmp/hive_jobs/job-123/",
    )

    assert exec_calls == [
        (
            "m5",
            (
                "/data/temp/Hive/.venv/bin/python "
                "-m hive.worker.main run "
                "/tmp/hive_jobs/job-123"
            ),
        )
    ]

    assert copy_from_calls == [
        (
            str(job_dir / "result.json"),
            "m5",
            "/tmp/hive_jobs/job-123/result.json",
        )
    ]

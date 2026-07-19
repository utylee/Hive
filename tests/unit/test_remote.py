import subprocess

import pytest

from hive.core import remote

@pytest.fixture(autouse=True)
def no_retry_delay(monkeypatch):
    monkeypatch.setattr(
        remote,
        "sleep",
        lambda _: None,
    )


def completed_process(
    returncode: int,
) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(
        args=["ssh", "m5", "true"],
        returncode=returncode,
        stdout="",
        stderr="temporary failure",
    )


def test_run_local_retries_returncode_255(
    monkeypatch,
):
    results = iter(
        [
            completed_process(255),
            completed_process(0),
        ]
    )

    calls = []

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return next(results)

    monkeypatch.setattr(
        remote.subprocess,
        "run",
        fake_run,
    )

    result = remote.run_local(
        ["ssh", "m5", "true"],
    )

    assert result.returncode == 0
    assert len(calls) == 2


def test_run_local_stops_after_retries(
    monkeypatch,
):
    calls = []

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return completed_process(255)

    monkeypatch.setattr(
        remote.subprocess,
        "run",
        fake_run,
    )

    with pytest.raises(
        remote.RemoteError,
        match="returncode=255",
    ):
        remote.run_local(
            ["ssh", "m5", "true"],
        )

    assert len(calls) == 3


def test_run_local_does_not_retry_other_errors(
    monkeypatch,
):
    calls = []

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return completed_process(1)

    monkeypatch.setattr(
        remote.subprocess,
        "run",
        fake_run,
    )

    with pytest.raises(
        remote.RemoteError,
        match="returncode=1",
    ):
        remote.run_local(
            ["ssh", "m5", "true"],
        )

    assert len(calls) == 1

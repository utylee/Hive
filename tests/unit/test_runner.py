from pathlib import Path

from hive.worker.runner import run_job


def test_run_job_missing_directory():
    rc = run_job(Path("/this/path/does/not/exist"))

    assert rc == 1

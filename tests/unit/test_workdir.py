from pathlib import Path
import shutil

from hive.dispatcher.workdir import WorkDir


def test_create_workdir() -> None:
    root = Path("/tmp/hive_workdir_test")

    if root.exists():
        shutil.rmtree(root)

    workdir = WorkDir(root)
    job_dir = workdir.create("job001")

    assert job_dir.exists()
    assert (job_dir / "input").is_dir()
    assert (job_dir / "output").is_dir()
    assert (job_dir / "logs").is_dir()

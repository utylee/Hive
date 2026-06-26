from pathlib import Path

from hive.models.job import Job


def test_job_roundtrip() -> None:
    job = Job(
        id="job001",
        project="vhs_restore",
        type="comfy",
        source=Path("/nas/jobs/001.mp4"),
        destination=Path("/nas/output"),
        parameters={
            "frames_per_batch": 16,
        },
        metadata={
            "creator": "Hive",
        },
    )

    path = Path("/tmp/hive_test/manifest.json")

    job.save(path)

    loaded = Job.load(path)

    assert loaded == job

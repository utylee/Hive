from pathlib import Path

from hive.models.job import Job


job = Job(
    id="test001",
    type="dummy",
    input_dir="/tmp/input",
    output_dir="/tmp/output",
)

path = Path("/tmp/hive_test/manifest.json")

job.save(path)

job2 = Job.load(path)

assert job == job2

print(job2)

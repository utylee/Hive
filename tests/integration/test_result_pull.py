from pathlib import Path
import json
import shutil

from hive.core.config import load_servers
from hive.dispatcher.remote_dispatcher import dispatch_remote_job


def test_result_pull():

    servers = load_servers("configs/servers.yaml")

    server = servers[0]

    job_dir = Path("/tmp/hive_result_pull")

    if job_dir.exists():
        shutil.rmtree(job_dir)

    (job_dir / "input").mkdir(parents=True)
    (job_dir / "output").mkdir()
    (job_dir / "logs").mkdir()

    manifest = {
        "version": 1,
        "id": job_dir.name,
        "project": "vhs_restore",
        "type": "dummy",
        "source": "/tmp/input.mp4",
        "parameters": {},
        "metadata": {},
    }

    (job_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    result = dispatch_remote_job(server, job_dir)

    assert result["ok"] is True
    assert result["executor"] == "dummy"

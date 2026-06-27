from pathlib import Path
import json
import shutil

from hive.core.config import load_servers
from hive.dispatcher.remote_dispatcher import dispatch_remote_job


def test_remote_worker_on_first_server() -> None:
    servers = load_servers("configs/servers.yaml")
    server = servers[0]

    local_job_dir = Path("/tmp/hive_remote_worker_test")

    if local_job_dir.exists():
        shutil.rmtree(local_job_dir)

    (local_job_dir / "input").mkdir(parents=True)
    (local_job_dir / "output").mkdir()
    (local_job_dir / "logs").mkdir()

    manifest = {
        "version": 1,
        "id": local_job_dir.name,
        "project": "vhs_restore",
        "type": "dummy",
        "source": "/tmp/input.mp4",
        "parameters": {},
        "metadata": {},
    }

    (local_job_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    dispatch_remote_job(server, local_job_dir)

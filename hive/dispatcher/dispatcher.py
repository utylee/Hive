from __future__ import annotations

from pathlib import Path

from hive.dispatcher.manifest import create_manifest, save_manifest
from hive.dispatcher.scanner import Scanner
from hive.dispatcher.workdir import WorkDir
from hive.dispatcher.remote_dispatcher import dispatch_remote_job
from hive.scheduler import pick_server


class Dispatcher:
    def __init__(
        self,
        jobs_dir,
        work_root,
        project,
        job_type,
        servers,
    ):
        self.scanner = Scanner(jobs_dir)
        self.workdir = WorkDir(work_root)

        self.project = project
        self.job_type = job_type
        self.servers = servers

    def run_once(self) -> int:
        created = 0

        for source in self.scanner.scan():
            manifest = create_manifest(
                project=self.project,
                job_type=self.job_type,
                source=source,
            )

            job_dir = self.workdir.create(manifest["id"])

            save_manifest(
                manifest,
                job_dir / "manifest.json",
            )
            server = pick_server(self.servers)

            result = dispatch_remote_job(
                server,
                job_dir,
            )

            assert result["ok"] is True

            created += 1

        return created


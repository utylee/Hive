from __future__ import annotations

from pathlib import Path

import shutil

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
        parameters=None,
    ):
        self.scanner = Scanner(jobs_dir)
        self.workdir = WorkDir(work_root)

        self.project = project
        self.job_type = job_type
        self.servers = servers
        self.parameters = parameters or {}

    def run_once(self) -> int:
        created = 0

        for source in self.scanner.scan():
            server = pick_server(self.servers)

            staged_source = Path("input") / source.name

            parameters = {
                **self.parameters,
                "comfy_url": server.comfy_url,
                "comfy_input_batches": server.comfy_input_batches,
            }

            manifest = create_manifest(
                project=self.project,
                job_type=self.job_type,
                source=staged_source,
                parameters=parameters,
            )

            job_dir = self.workdir.create(manifest["id"])

            shutil.copy2(
                source,
                job_dir / staged_source,
            )

            save_manifest(
                manifest,
                job_dir / "manifest.json",
            )

            result = dispatch_remote_job(
                server,
                job_dir,
            )

            assert result["ok"] is True

            created += 1

        return created

        # for source in self.scanner.scan():
        #     staged_source = Path("input") / source.name

        #     manifest = create_manifest(
        #         project=self.project,
        #         job_type=self.job_type,
        #         source=staged_source,
        #         parameters=self.parameters,
        #     )

        #     job_dir = self.workdir.create(manifest["id"])

        #     shutil.copy2(
        #         source,
        #         job_dir / staged_source,
        #     )

        #     save_manifest(
        #         manifest,
        #         job_dir / "manifest.json",
        #     )

        #     server = pick_server(self.servers)

        #     result = dispatch_remote_job(
        #         server,
        #         job_dir,
        #     )

        #     assert result["ok"] is True

        #     created += 1

        # return created


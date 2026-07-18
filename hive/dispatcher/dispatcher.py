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

            # parameters = {
            #     **self.parameters,
            #     "comfy_url": server.comfy_url,
            #     "comfy_input_batches": server.comfy_input_batches,
            # }

            parameters = {
                **self.parameters,
                "comfy_url": server.comfy_url,
                "comfy_input_batches": server.comfy_input_batches,
                "profile": server.profile,
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

            workflow_source = Path(parameters["workflow"])
            workflow_target = job_dir / "workflow.json"

            shutil.copy2(
                workflow_source,
                workflow_target,
            )

            manifest["parameters"]["workflow"] = "workflow.json"

            save_manifest(
                manifest,
                job_dir / "manifest.json",
            )

            try:
                result = dispatch_remote_job(
                    server,
                    job_dir,
                )

                if not result.get("ok"):
                    raise RuntimeError(
                        f"Remote job failed: {result}"
                    )

            except Exception as exc:
                failed_dir = self.scanner.root / "failed"
                failed_dir.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                shutil.move(
                    str(source),
                    failed_dir / source.name,
                )

                (job_dir / "error.txt").write_text(
                    f"{type(exc).__name__}: {exc}\n",
                    encoding="utf-8",
                )

                continue

            done_dir = self.scanner.root / "done"
            done_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.move(
                str(source),
                done_dir / source.name,
            )

            created += 1


        return created
    

from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed

from pathlib import Path

import shutil
import json

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
        max_workers=None,
    ):
        self.scanner = Scanner(jobs_dir)
        self.workdir = WorkDir(work_root)

        self.project = project
        self.job_type = job_type
        self.servers = servers
        self.parameters = parameters or {}
        self._server_index = 0
        self.max_workers = max_workers or len(
            [
                server
                for server in servers
                if server.enabled
            ]
        )

    def run_once(self) -> int:
        jobs = []

        for source in self.scanner.scan():
            source_retry_path = (
                self.scanner.root
                / f"{source.name}.retry.json"
            )

            failed_servers: set[str] = set()

            if source_retry_path.exists():
                retry_data = json.loads(
                    source_retry_path.read_text(
                        encoding="utf-8",
                    )
                )

                failed_servers = set(
                    retry_data.get(
                        "failed_servers",
                        [],
                    )
                )

            try:
                server, selected_index = pick_server(
                    self.servers,
                    excluded=failed_servers,
                    start_index=self._server_index,
                )
            except RuntimeError:
                server, selected_index = pick_server(
                    self.servers,
                    start_index=self._server_index,
                )

            self._server_index = (
                selected_index + 1
            ) % len(self.servers)

            jobs.append(
                (
                    source,
                    server,
                    failed_servers,
                )
            )

        completed = 0

        with ThreadPoolExecutor(
            max_workers=self.max_workers,
        ) as executor:
            futures = [
                executor.submit(
                    self._process_source,
                    source,
                    server,
                    failed_servers,
                )
                for source, server, failed_servers in jobs
            ]

            for future in as_completed(futures):
                if future.result():
                    completed += 1

        return completed

    def _process_source(
        self,
        source: Path,
        server,
        failed_servers: set[str],
    ) -> bool:
        staged_source = Path("input") / source.name

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

        job_dir = self.workdir.create(
            manifest["id"]
        )

        shutil.copy2(
            source,
            job_dir / staged_source,
        )

        workflow_source = Path(
            parameters["workflow"]
        )

        workflow_target = (
            job_dir / "workflow.json"
        )

        shutil.copy2(
            workflow_source,
            workflow_target,
        )

        manifest["parameters"]["workflow"] = (
            "workflow.json"
        )

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
            failed_dir = (
                self.scanner.root / "failed"
            )

            failed_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            source_retry_path = (
                self.scanner.root
                / f"{source.name}.retry.json"
            )

            retry_path = (
                failed_dir
                / f"{source.name}.retry.json"
            )

            retry_count = 0

            if source_retry_path.exists():
                retry_data = json.loads(
                    source_retry_path.read_text(
                        encoding="utf-8",
                    )
                )

                retry_count = int(
                    retry_data.get(
                        "retry_count",
                        0,
                    )
                )

                source_retry_path.unlink()

            shutil.move(
                str(source),
                failed_dir / source.name,
            )

            failed_servers.add(server.name)

            retry_path.write_text(
                json.dumps(
                    {
                        "retry_count": retry_count + 1,
                        "last_job_id": manifest["id"],
                        "last_error": (
                            f"{type(exc).__name__}: {exc}"
                        ),
                        "failed_servers": sorted(
                            failed_servers
                        ),
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            (job_dir / "error.txt").write_text(
                f"{type(exc).__name__}: {exc}\n",
                encoding="utf-8",
            )

            return False

        source_retry_path = (
            self.scanner.root
            / f"{source.name}.retry.json"
        )

        if source_retry_path.exists():
            source_retry_path.unlink()

        done_dir = self.scanner.root / "done"

        done_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.move(
            str(source),
            done_dir / source.name,
        )

        return True

    # def run_once(self) -> int:
    #     created = 0

    #     for source in self.scanner.scan():

    #         source_retry_path = (
    #             self.scanner.root
    #             / f"{source.name}.retry.json"
    #         )

    #         failed_servers: set[str] = set()

    #         if source_retry_path.exists():
    #             retry_data = json.loads(
    #                 source_retry_path.read_text(
    #                     encoding="utf-8",
    #                 )
    #             )

    #             failed_servers = set(
    #                 retry_data.get(
    #                     "failed_servers",
    #                     [],
    #                 )
    #             )

    #         try:
    #             server, selected_index = pick_server(
    #                 self.servers,
    #                 excluded=failed_servers,
    #                 start_index=self._server_index,
    #             )
    #         except RuntimeError:
    #             server, selected_index = pick_server(
    #                 self.servers,
    #                 start_index=self._server_index,
    #             )

    #         self._server_index = (
    #             selected_index + 1
    #         ) % len(self.servers)


    #         staged_source = Path("input") / source.name

    #         # parameters = {
    #         #     **self.parameters,
    #         #     "comfy_url": server.comfy_url,
    #         #     "comfy_input_batches": server.comfy_input_batches,
    #         # }

    #         parameters = {
    #             **self.parameters,
    #             "comfy_url": server.comfy_url,
    #             "comfy_input_batches": server.comfy_input_batches,
    #             "profile": server.profile,
    #         }

    #         manifest = create_manifest(
    #             project=self.project,
    #             job_type=self.job_type,
    #             source=staged_source,
    #             parameters=parameters,
    #         )

    #         job_dir = self.workdir.create(manifest["id"])

    #         shutil.copy2(
    #             source,
    #             job_dir / staged_source,
    #         )

    #         workflow_source = Path(parameters["workflow"])
    #         workflow_target = job_dir / "workflow.json"

    #         shutil.copy2(
    #             workflow_source,
    #             workflow_target,
    #         )

    #         manifest["parameters"]["workflow"] = "workflow.json"

    #         save_manifest(
    #             manifest,
    #             job_dir / "manifest.json",
    #         )

    #         try:
    #             result = dispatch_remote_job(
    #                 server,
    #                 job_dir,
    #             )

    #             if not result.get("ok"):
    #                 raise RuntimeError(
    #                     f"Remote job failed: {result}"
    #                 )

    #         except Exception as exc:
    #             failed_dir = self.scanner.root / "failed"
    #             failed_dir.mkdir(
    #                 parents=True,
    #                 exist_ok=True,
    #             )

    #             source_retry_path = (
    #                 self.scanner.root
    #                 / f"{source.name}.retry.json"
    #             )

    #             retry_path = (
    #                 failed_dir
    #                 / f"{source.name}.retry.json"
    #             )

    #             retry_count = 0

    #             if source_retry_path.exists():
    #                 retry_data = json.loads(
    #                     source_retry_path.read_text(
    #                         encoding="utf-8",
    #                     )
    #                 )

    #                 retry_count = int(
    #                     retry_data.get("retry_count", 0)
    #                 )

    #                 source_retry_path.unlink()

    #             shutil.move(
    #                 str(source),
    #                 failed_dir / source.name,
    #             )

    #             failed_servers.add(server.name)

    #             retry_path.write_text(
    #                 json.dumps(
    #                     {
    #                         "retry_count": retry_count + 1,
    #                         "last_job_id": manifest["id"],
    #                         "last_error": (
    #                             f"{type(exc).__name__}: {exc}"
    #                         ),
    #                         "failed_servers": sorted(
    #                             failed_servers
    #                         ),
    #                     },
    #                     indent=2,
    #                     ensure_ascii=False,
    #                 ),
    #                 encoding="utf-8",
    #             )

    #             (job_dir / "error.txt").write_text(
    #                 f"{type(exc).__name__}: {exc}\n",
    #                 encoding="utf-8",
    #             )

    #             continue

    #         source_retry_path = (
    #             self.scanner.root
    #             / f"{source.name}.retry.json"
    #         )

    #         if source_retry_path.exists():
    #             source_retry_path.unlink()

    #         done_dir = self.scanner.root / "done"
    #         done_dir.mkdir(
    #             parents=True,
    #             exist_ok=True,
    #         )

    #         shutil.move(
    #             str(source),
    #             done_dir / source.name,
    #         )

    #         created += 1


    #     return created
    

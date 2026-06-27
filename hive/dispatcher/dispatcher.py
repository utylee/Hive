from __future__ import annotations

from pathlib import Path

from hive.dispatcher.manifest import create_manifest, save_manifest
from hive.dispatcher.scanner import Scanner
from hive.dispatcher.workdir import WorkDir


class Dispatcher:
    def __init__(
        self,
        jobs_dir: str | Path,
        work_root: str | Path,
        project: str,
        job_type: str,
    ) -> None:
        self.scanner = Scanner(jobs_dir)
        self.workdir = WorkDir(work_root)

        self.project = project
        self.job_type = job_type

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

            created += 1

        return created


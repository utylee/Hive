
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from queue import Empty, Queue

from threading import Lock
# from time import monotonic, perf_counter
from time import perf_counter, time


import json
import shutil

from hive.dispatcher.manifest import create_manifest, save_manifest
from hive.dispatcher.scanner import Scanner
from hive.dispatcher.workdir import WorkDir
from hive.dispatcher.remote_dispatcher import dispatch_remote_job


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
        max_retries=3,
        server_failure_threshold=2,
        server_cooldown_seconds=60.0,
    ):
        self.scanner = Scanner(jobs_dir)
        self.workdir = WorkDir(work_root)

        self.project = project
        self.job_type = job_type
        self.servers = servers
        self.parameters = parameters or {}
        self.max_workers = max_workers or len(
            [
                server
                for server in servers
                if server.enabled
            ]
        )
        self.max_retries = max_retries
        self.server_failure_threshold = (
            server_failure_threshold
        )
        self.server_cooldown_seconds = (
            server_cooldown_seconds
        )

        self._server_failures = {
            server.name: 0
            for server in servers
        }

        self._server_cooldown_until = {
            server.name: 0.0
            for server in servers
        }

        self._server_state_lock = Lock()
        self._server_state_file_lock = Lock()
        self._server_event_lock = Lock()

        self._server_state_path = (
            self.workdir.root
            / "server_state.json"
        )

        self._load_server_state()

    def _save_server_state(
        self,
    ) -> None:
        with self._server_state_lock:
            state = {
                server.name: {
                    "consecutive_failures": (
                        self._server_failures[
                            server.name
                        ]
                    ),
                    "cooldown_until": (
                        datetime.fromtimestamp(
                            self._server_cooldown_until[
                                server.name
                            ],
                            tz=timezone.utc,
                        ).isoformat()
                        if self._server_cooldown_until[
                            server.name
                        ] > 0
                        else None
                    ),
                }
                for server in self.servers
            }

        with self._server_state_file_lock:

            self._server_state_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            temporary_path = (
                self._server_state_path
                .with_suffix(".json.tmp")
            )

            temporary_path.write_text(
                json.dumps(
                    state,
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            temporary_path.replace(
                self._server_state_path
            )


    def _load_server_state(
        self,
    ) -> None:
        if not self._server_state_path.exists():
            return

        state = json.loads(
            self._server_state_path.read_text(
                encoding="utf-8",
            )
        )

        now = time()

        with self._server_state_lock:
            for server in self.servers:
                server_state = state.get(
                    server.name,
                    {},
                )

                failures = int(
                    server_state.get(
                        "consecutive_failures",
                        0,
                    )
                )

                cooldown_text = server_state.get(
                    "cooldown_until"
                )

                cooldown_until = 0.0

                if cooldown_text:
                    cooldown_until = (
                        datetime.fromisoformat(
                            cooldown_text
                        ).timestamp()
                    )

                if cooldown_until <= now:
                    cooldown_until = 0.0

                self._server_failures[
                    server.name
                ] = failures

                self._server_cooldown_until[
                    server.name
                ] = cooldown_until

    def run_once(self) -> int:
        enabled_servers = [
            server
            for server in self.servers
            if server.enabled
        ]

        if not enabled_servers:
            raise RuntimeError(
                "No enabled servers available"
            )

        worker_servers = enabled_servers[
            : self.max_workers
        ]

        active_names = {
            source.name
            for source in self.scanner.scan()
        }

        completed = 0

        while active_names:
            completed += self._run_round(
                worker_servers,
            )

            restored = self._restore_retryable_failed(
                worker_servers,
                active_names,
            )

            if restored == 0:
                break

        return completed
    
    def _run_round(
        self,
        worker_servers,
    ) -> int:
        job_queue: Queue = Queue()

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

            job_queue.put(
                (
                    source,
                    failed_servers,
                )
            )

        with ThreadPoolExecutor(
            max_workers=len(worker_servers),
        ) as executor:
            futures = [
                executor.submit(
                    self._server_worker,
                    server,
                    job_queue,
                )
                for server in worker_servers
            ]

            return sum(
                future.result()
                for future in futures
            )

    def _restore_retryable_failed(
        self,
        worker_servers,
        active_names: set[str],
    ) -> int:
        failed_dir = (
            self.scanner.root / "failed"
        )

        if not failed_dir.exists():
            return 0

        available_servers = {
            server.name
            for server in worker_servers
        }

        restored = 0

        for source in sorted(
            failed_dir.glob("*.mp4")
        ):
            if source.name not in active_names:
                continue

            retry_source = (
                failed_dir
                / f"{source.name}.retry.json"
            )

            if not retry_source.exists():
                continue

            retry_data = json.loads(
                retry_source.read_text(
                    encoding="utf-8",
                )
            )

            retry_count = int(
                retry_data.get(
                    "retry_count",
                    0,
                )
            )

            failed_servers = set(
                retry_data.get(
                    "failed_servers",
                    [],
                )
            )

            if retry_count >= self.max_retries:
                continue

            untried_servers = (
                available_servers - failed_servers
            )

            if not untried_servers:
                continue

            target = (
                self.scanner.root / source.name
            )

            retry_target = (
                self.scanner.root
                / f"{source.name}.retry.json"
            )

            if target.exists():
                raise FileExistsError(
                    f"Retry target already exists: {target}"
                )

            shutil.move(
                str(source),
                target,
            )

            shutil.move(
                str(retry_source),
                retry_target,
            )

            restored += 1

        return restored

    def _write_server_event(
        self,
        event: str,
        server,
        **details,
    ) -> None:
        record = {
            "timestamp": datetime.now(
                timezone.utc,
            ).isoformat(),
            "event": event,
            "server": server.name,
            **details,
        }

        event_path = (
            self.workdir.root
            / "server_events.jsonl"
        )

        with self._server_event_lock:
            event_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with event_path.open(
                "a",
                encoding="utf-8",
            ) as file:
                file.write(
                    json.dumps(
                        record,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

    def _server_is_available(
        self,
        server,
    ) -> bool:
        with self._server_state_lock:
            cooldown_until = (
                self._server_cooldown_until[
                    server.name
                ]
            )

            if time() >= cooldown_until:
                return True

            return False

    def _record_server_success(
        self,
        server,
    ) -> None:
        recovered = False
        previous_failures = 0

        with self._server_state_lock:
            previous_failures = (
                self._server_failures[
                    server.name
                ]
            )

            recovered = previous_failures > 0

            self._server_failures[
                server.name
            ] = 0

            self._server_cooldown_until[
                server.name
            ] = 0.0

        self._save_server_state()

        if recovered:
            self._write_server_event(
                "server_recovered",
                server,
                previous_failures=previous_failures,
            )

    def _record_server_failure(
        self,
        server,
    ) -> None:
        entered_cooldown = False

        with self._server_state_lock:
            failures = (
                self._server_failures[
                    server.name
                ]
                + 1
            )

            self._server_failures[
                server.name
            ] = failures

            if (
                failures
                >= self.server_failure_threshold
            ):
                self._server_cooldown_until[
                    server.name
                ] = (
                    time()
                    + self.server_cooldown_seconds
                )

                entered_cooldown = True

        self._save_server_state()

        self._write_server_event(
            "server_failure",
            server,
            consecutive_failures=failures,
        )

        if entered_cooldown:
            self._write_server_event(
                "server_cooldown",
                server,
                consecutive_failures=failures,
                cooldown_seconds=(
                    self.server_cooldown_seconds
                ),
            )


    def _server_worker(
        self,
        server,
        job_queue: Queue,
    ) -> int:
        completed = 0

        while True:
            job = self._take_job_for_server(
                server,
                job_queue,
            )

            if job is None:
                break

            source, failed_servers = job


            if not self._server_is_available(server):
                job_queue.put(
                    (
                        source,
                        failed_servers,
                    )
                )
                break

            if self._process_source(
                source,
                server,
                failed_servers,
            ):
                self._record_server_success(server)
                completed += 1
            else:
                self._record_server_failure(server)

        return completed

    def _take_job_for_server(
        self,
        server,
        job_queue: Queue,
    ):
        deferred = []

        queue_size = job_queue.qsize()

        for _ in range(queue_size):
            try:
                job = job_queue.get_nowait()
            except Empty:
                break

            _, failed_servers = job

            if server.name not in failed_servers:
                for deferred_job in deferred:
                    job_queue.put(deferred_job)

                return job

            deferred.append(job)

        for deferred_job in deferred:
            job_queue.put(deferred_job)

        return None

        # # 모든 남은 작업이 이 서버에서 실패한 이력이 있다면
        # # 예전 동작처럼 다른 선택지가 없을 때는 다시 허용한다.
        # try:
        #     return job_queue.get_nowait()
        # except Empty:
        #     return None

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
            "comfy_output_dir": server.comfy_output_dir,
            "profile": server.profile,
        }

        manifest = create_manifest(
            project=self.project,
            job_type=self.job_type,
            source=staged_source,
            parameters=parameters,
        )
        started_timer = perf_counter()

        manifest["server_name"] = server.name
        manifest["started_at"] = datetime.now(
            timezone.utc,
        ).isoformat()
        manifest["status"] = "running"

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
            manifest["finished_at"] = datetime.now(
                timezone.utc,
            ).isoformat()

            manifest["elapsed_seconds"] = round(
                perf_counter() - started_timer,
                3,
            )

            manifest["status"] = "failed"

            save_manifest(
                manifest,
                job_dir / "manifest.json",
            )



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

        manifest["finished_at"] = datetime.now(
            timezone.utc,
        ).isoformat()

        manifest["elapsed_seconds"] = round(
            perf_counter() - started_timer,
            3,
        )

        manifest["status"] = "completed"

        save_manifest(
            manifest,
            job_dir / "manifest.json",
        )

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



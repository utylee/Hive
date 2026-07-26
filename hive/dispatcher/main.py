from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import json
from collections import defaultdict
from datetime import datetime, timezone

from hive.core.config import load_servers
from hive.dispatcher.dispatcher import Dispatcher
from hive.dispatcher.preflight import (
    check_server,
    filter_healthy_servers,
)


MAX_RETRIES = 3

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dispatch Hive jobs to remote workers.",
    )

    parser.add_argument(
        "--reset-server-state",
        nargs="?",
        const="all",
        metavar="SERVER",
        help=(
            "Clear persisted state for one server "
            "or all servers, then exit."
        ),
    )


    parser.add_argument(
        "--server-events",
        type=int,
        metavar="N",
        help="Show the most recent N server events, then exit.",
    )

    parser.add_argument(
        "--server-status",
        action="store_true",
        help="Show server failure and cooldown events, then exit.",
    )

    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Check enabled server environments and exit.",
    )

    parser.add_argument(
        "--restore-quarantine",
        action="store_true",
        help="Move quarantined input files back into the jobs directory.",
    )

    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Move failed input files back into the jobs directory.",
    )

    parser.add_argument(
        "jobs_dir",
        type=Path,
        help="Directory containing input video files.",
    )

    parser.add_argument(
        "--work-root",
        type=Path,
        default=Path("/tmp/hive_test/work"),
    )

    parser.add_argument(
        "--servers",
        type=Path,
        default=Path("configs/servers.yaml"),
    )

    parser.add_argument(
        "--workflow",
        type=Path,
        default=Path(
            "hive/examples/workflows/"
            "hd_remaster_rope_facerestore_api.json"
        ),
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()


    if args.reset_server_state is not None:
        state_path = (
            args.work_root / "server_state.json"
        )

        if not state_path.exists():
            print("No persisted server state found")
            return 0

        server_name = args.reset_server_state

        if server_name == "all":
            state_path.unlink()

            print(
                f"Cleared persisted server state: "
                f"{state_path}"
            )

            return 0

        try:
            state = json.loads(
                state_path.read_text(
                    encoding="utf-8",
                )
            )

            if not isinstance(state, dict):
                raise TypeError(
                    "Server state must be an object"
                )

        except (
            json.JSONDecodeError,
            OSError,
            TypeError,
        ):
            corrupt_path = state_path.with_suffix(
                ".json.corrupt"
            )

            state_path.replace(corrupt_path)

            print(
                "Persisted server state was corrupt "
                f"and preserved as: {corrupt_path}"
            )

            return 0

        if server_name not in state:
            print(
                "No persisted state found for "
                f"server: {server_name}"
            )
            return 0

        del state[server_name]

        temporary_path = state_path.with_suffix(
            ".json.tmp"
        )

        temporary_path.write_text(
            json.dumps(
                state,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        temporary_path.replace(state_path)

        print(
            "Cleared persisted state for server: "
            f"{server_name}"
        )

        return 0




    if args.server_events is not None:
        event_path = (
            args.work_root / "server_events.jsonl"
        )

        if not event_path.exists():
            print("No server event log found")
            return 0

        if args.server_events < 1:
            raise ValueError(
                "--server-events must be at least 1"
            )

        records = [
            json.loads(line)
            for line in event_path.read_text(
                encoding="utf-8",
            ).splitlines()
            if line.strip()
        ]

        for record in records[
            -args.server_events:
        ]:
            details = {
                key: value
                for key, value in record.items()
                if key not in {
                    "timestamp",
                    "event",
                    "server",
                }
            }

            detail_text = " ".join(
                f"{key}={value}"
                for key, value in details.items()
            )

            print(
                f"{record.get('timestamp')} "
                f"{record.get('server')} "
                f"{record.get('event')}"
                + (
                    f" {detail_text}"
                    if detail_text
                    else ""
                )
            )

        return 0

    if args.server_status:
        event_path = (
            args.work_root / "server_events.jsonl"
        )

        state_path = (
            args.work_root / "server_state.json"
        )

        if (
            not event_path.exists()
            and not state_path.exists()
        ):
            print("No server status data found")
            return 0

        stats = defaultdict(
            lambda: {
                "failures": 0,
                "cooldowns": 0,
                "recoveries": 0,
                "last_event": None,
                "last_timestamp": None,
                "cooldown_started_at": None,
                "cooldown_seconds": 0.0,
            }
        )

        if event_path.exists():
            for line in event_path.read_text(
                encoding="utf-8",
            ).splitlines():
                if not line.strip():
                    continue

                record = json.loads(line)
                server_name = record["server"]
                event = record["event"]

                server_stats = stats[server_name]


                if event == "server_failure":
                    server_stats["failures"] += 1

                elif event == "server_cooldown":
                    server_stats["cooldowns"] += 1
                    server_stats["cooldown_started_at"] = (
                        record.get("timestamp")
                    )
                    server_stats["cooldown_seconds"] = float(
                        record.get(
                            "cooldown_seconds",
                            0.0,
                        )
                    )

                elif event == "server_recovered":
                    server_stats["recoveries"] += 1
                    server_stats["cooldown_started_at"] = None
                    server_stats["cooldown_seconds"] = 0.0


                server_stats["last_event"] = event
                server_stats["last_timestamp"] = (
                    record.get("timestamp")
                )

        persisted_state = {}

        if state_path.exists():
            persisted_state = json.loads(
                state_path.read_text(
                    encoding="utf-8",
                )
            )

            for server_name in persisted_state:
                stats[server_name]

        for server_name in sorted(stats):
            server_stats = stats[server_name]

            cooldown_active = False
            cooldown_remaining = 0.0
            
            state = persisted_state.get(
                server_name,
                {},
            )

            cooldown_until_text = state.get(
                "cooldown_until"
            )

            if cooldown_until_text:
                cooldown_until = datetime.fromisoformat(
                    cooldown_until_text
                )

                now = datetime.now(timezone.utc)

                cooldown_remaining = max(
                    0.0,
                    (
                        cooldown_until - now
                    ).total_seconds(),
                )

                cooldown_active = (
                    cooldown_remaining > 0
                )

            consecutive_failures = int(
                state.get(
                    "consecutive_failures",
                    0,
                )
            )

            print(
                f"{server_name}: "
                f"failures={server_stats['failures']} "
                f"cooldowns={server_stats['cooldowns']} "
                f"consecutive_failures="
                f"{consecutive_failures} "
                f"recoveries={server_stats['recoveries']} "
                f"cooldown_active={cooldown_active} "
                f"cooldown_remaining="
                f"{cooldown_remaining:.1f}s "
                f"last={server_stats['last_event']} "
                f"at={server_stats['last_timestamp']}"
            )


        return 0

    if args.restore_quarantine:
        quarantine_dir = args.jobs_dir / "quarantine"

        if not quarantine_dir.exists():
            print("No quarantine directory found")
            return 0

        restored = 0

        for source in sorted(quarantine_dir.glob("*.mp4")):
            target = args.jobs_dir / source.name

            if target.exists():
                raise FileExistsError(
                    f"Restore target already exists: {target}"
                )

            shutil.move(
                str(source),
                target,
            )

            retry_source = (
                quarantine_dir
                / f"{source.name}.retry.json"
            )

            # 격리 해제는 재시도 횟수를 초기화
            if retry_source.exists():
                retry_source.unlink()

            restored += 1

        print(
            f"Restored {restored} quarantined job(s)"
        )

        return 0

    if args.retry_failed:
        failed_dir = args.jobs_dir / "failed"

        if not failed_dir.exists():
            print("No failed directory found")
            return 0

        retried = 0

        for source in sorted(failed_dir.glob("*.mp4")):
            retry_source = failed_dir / f"{source.name}.retry.json"

            retry_count = 0

            if retry_source.exists():
                retry_data = json.loads(
                    retry_source.read_text(
                        encoding="utf-8",
                    )
                )
                retry_count = int(
                    retry_data.get("retry_count", 0)
                )

            if retry_count >= MAX_RETRIES:
                quarantine_dir = args.jobs_dir / "quarantine"
                quarantine_dir.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                shutil.move(
                    str(source),
                    quarantine_dir / source.name,
                )

                if retry_source.exists():
                    shutil.move(
                        str(retry_source),
                        quarantine_dir / retry_source.name,
                    )

                print(
                    f"Quarantined {source.name}: "
                    f"retry limit reached ({retry_count})"
                )

                continue


            target = args.jobs_dir / source.name

            if target.exists():
                raise FileExistsError(
                    f"Retry target already exists: {target}"
                )

            shutil.move(
                str(source),
                target,
            )

            retry_source = failed_dir / f"{source.name}.retry.json"
            retry_target = args.jobs_dir / f"{source.name}.retry.json"

            if retry_source.exists():
                shutil.move(
                    str(retry_source),
                    retry_target,
                )

            retried += 1

        print(f"Restored {retried} failed job(s)")

        if retried == 0:
            return 0

    servers = [
        server
        for server in load_servers(args.servers)
        if server.enabled
    ]

    if not servers:
        raise RuntimeError("No enabled servers configured")

    if args.preflight:
        all_ok = True

        for server in servers:
            result = check_server(server)

            print(
                f"{server.name}: "
                f"ssh={result.ssh_ok} "
                f"python={result.python_ok} "
                f"hive={result.hive_ok} "
                f"comfy={result.comfy_ok}"
            )

            if result.error:
                print(f"  error: {result.error}")

            if not result.ok:
                all_ok = False

        return 0 if all_ok else 1

    healthy_servers, preflight_results = (
        filter_healthy_servers(servers)
    )

    for result in preflight_results:
        if result.ok:
            continue

        print(
            f"Skipping {result.server_name}: "
            f"{result.error or 'preflight failed'}"
        )

    servers = healthy_servers

    if not servers:
        raise RuntimeError(
            "No healthy servers available"
        )

    if not args.workflow.exists():
        raise FileNotFoundError(
            f"Workflow not found: {args.workflow}"
        )

    dispatcher = Dispatcher(
        jobs_dir=args.jobs_dir,
        work_root=args.work_root,
        project="vhs_restore",
        job_type="comfy",
        servers=servers,
        parameters={
            "workflow": str(args.workflow),
        },
    )

    created = dispatcher.run_once()

    print(f"Completed {created} job(s)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

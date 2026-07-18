from __future__ import annotations

import argparse
from pathlib import Path
import shutil

from hive.core.config import load_servers
from hive.dispatcher.dispatcher import Dispatcher


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dispatch Hive jobs to remote workers.",
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

    if args.retry_failed:
        failed_dir = args.jobs_dir / "failed"

        if not failed_dir.exists():
            print("No failed directory found")
            return 0

        retried = 0

        for source in sorted(failed_dir.glob("*.mp4")):
            target = args.jobs_dir / source.name

            if target.exists():
                raise FileExistsError(
                    f"Retry target already exists: {target}"
                )

            shutil.move(
                str(source),
                target,
            )

            retried += 1

        print(f"Restored {retried} failed job(s)")

        return 0

    servers = [
        server
        for server in load_servers(args.servers)
        if server.enabled
    ]

    if not servers:
        raise RuntimeError("No enabled servers configured")

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

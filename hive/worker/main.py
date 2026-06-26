from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from hive.worker.runner import run_job


def main() -> int:
    parser = ArgumentParser()

    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run")
    run.add_argument("job_dir")

    args = parser.parse_args()

    if args.command == "run":
        return run_job(Path(args.job_dir))

    return 1


if __name__ == "__main__":
    raise SystemExit(main())


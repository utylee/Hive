from pathlib import Path

from hive.dispatcher.scanner import Scanner


def main() -> int:

    scanner = Scanner(
        Path("/tmp/hive_test/jobs")
    )

    jobs = scanner.scan()

    print(f"Found {len(jobs)} jobs")

    for job in jobs:
        print(job.name)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


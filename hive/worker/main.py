from argparse import ArgumentParser


def main() -> int:
    parser = ArgumentParser()

    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run")
    run.add_argument("job_dir")

    args = parser.parse_args()

    if args.command == "run":
        print(args.job_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

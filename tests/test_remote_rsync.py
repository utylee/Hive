from pathlib import Path

from hive import remote


def main() -> None:
    alias = "ccy2"

    local_root = Path("/tmp/hive_remote_test_local")
    local_root.mkdir(parents=True, exist_ok=True)

    local_file = local_root / "hello.txt"
    local_file.write_text("hello hive\n", encoding="utf-8")

    remote_dir = "/tmp/hive_remote_test"
    remote.mkdir(alias, remote_dir)

    remote.copy_to(local_file, alias, f"{remote_dir}/")

    result = remote.exec(alias, f"cat {remote_dir}/hello.txt")
    print(result.stdout.strip())

    back_dir = Path("/tmp/hive_remote_test_back")
    back_dir.mkdir(parents=True, exist_ok=True)

    remote.copy_from(alias, f"{remote_dir}/hello.txt", back_dir / "hello_back.txt")

    print((back_dir / "hello_back.txt").read_text(encoding="utf-8").strip())


if __name__ == "__main__":
    main()

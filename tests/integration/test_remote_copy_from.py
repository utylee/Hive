from pathlib import Path
import shutil

from hive.core.config import load_servers
from hive.core import remote


def test_remote_copy_from() -> None:
    server = load_servers("configs/servers.yaml")[0]
    alias = server.ssh_alias

    remote_dir = "/tmp/hive_copy_from_test"
    remote_file = f"{remote_dir}/hello.txt"

    local_dir = Path("/tmp/hive_copy_from_local")

    if local_dir.exists():
        shutil.rmtree(local_dir)

    local_dir.mkdir(parents=True)

    remote.mkdir(alias, remote_dir)
    remote.exec(alias, f"printf 'hello from remote\n' > {remote_file}")

    remote.copy_from(
        str(local_dir) + "/",
        alias,
        remote_file,
    )

    copied = local_dir / "hello.txt"

    assert copied.exists()
    assert copied.read_text(encoding="utf-8") == "hello from remote\n"

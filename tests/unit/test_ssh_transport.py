from hive.transport.ssh import SSHTransport
from pathlib import Path

def test_create_ssh_transport() -> None:
    transport = SSHTransport("m5", workspace=Path("/tmp"))

    transport = SSHTransport(
        host="m5",
        workspace=Path("/tmp"),
    )

    assert transport.host == "m5"

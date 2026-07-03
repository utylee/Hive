from hive.transport.ssh import SSHTransport


def test_create_ssh_transport() -> None:
    transport = SSHTransport("m5")

    assert transport.host == "m5"

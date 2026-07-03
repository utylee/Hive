from hive.runtime.server import Server


def test_server_defaults() -> None:
    server = Server("m5")

    assert server.name == "m5"
    assert server.enabled


def test_server_disabled() -> None:
    server = Server(
        "strix",
        enabled=False,
    )

    assert not server.enabled

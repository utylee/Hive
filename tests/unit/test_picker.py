from hive.scheduler import pick_server
from hive.core.config import load_servers

from types import SimpleNamespace


def test_pick_first_enabled_server():
    servers = load_servers(
        "configs/servers.yaml"
    )

    server, index = pick_server(servers)

    assert server.enabled is True
    assert index >= 0


def test_pick_server_from_start_index():
    servers = [
        SimpleNamespace(
            name="a",
            enabled=True,
        ),
        SimpleNamespace(
            name="b",
            enabled=True,
        ),
        SimpleNamespace(
            name="c",
            enabled=True,
        ),
    ]

    server, index = pick_server(
        servers,
        start_index=1,
    )

    assert server.name == "b"
    assert index == 1


def test_pick_server_skips_excluded():
    servers = [
        SimpleNamespace(
            name="a",
            enabled=True,
        ),
        SimpleNamespace(
            name="b",
            enabled=True,
        ),
    ]

    server, index = pick_server(
        servers,
        excluded={"a"},
        start_index=0,
    )

    assert server.name == "b"
    assert index == 1


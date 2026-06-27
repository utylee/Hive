
from hive.scheduler import pick_server
from hive.core.config import load_servers


def test_pick_first_enabled_server():
    servers = load_servers("configs/servers.yaml")

    server = pick_server(servers)

    assert server.enabled is True

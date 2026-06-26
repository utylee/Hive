
from hive.infra.config import load_servers
from hive.infra import remote


def main() -> None:
    servers = load_servers("configs/servers.yaml")

    for server in servers:
        print("=" * 50)
        print(f"name      : {server.name}")
        print(f"label     : {server.label}")
        print(f"ssh_alias : {server.ssh_alias}")

        hostname = remote.run(server, "hostname").strip()
        print(f"hostname  : {hostname}")


if __name__ == "__main__":
    main()

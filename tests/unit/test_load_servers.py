from hive.infra.config import load_servers


def main() -> None:
    servers = load_servers("configs/servers.yaml")

    assert servers, "No enabled servers loaded"

    for server in servers:
        print(
            server.name,
            server.label,
            server.ssh_alias,
            server.worker_root,
            server.profile.frames_per_batch,
            server.profile.cleanup_threshold,
        )

    assert servers[0].profile.frames_per_batch > 0


if __name__ == "__main__":
    main()

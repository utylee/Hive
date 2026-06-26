from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from hive.models.server import Server


def load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")

    return data


def load_servers(path: str | Path = "configs/servers.yaml") -> list[Server]:
    data = load_yaml(path)

    raw_servers = data.get("servers")
    if not isinstance(raw_servers, dict):
        raise ValueError("servers.yaml must contain a 'servers' mapping")

    servers: list[Server] = []

    for name, raw in raw_servers.items():
        if not isinstance(raw, dict):
            raise ValueError(f"Server entry must be a mapping: {name}")

        server = Server.from_dict(name, raw)

        if server.enabled:
            servers.append(server)

    return servers

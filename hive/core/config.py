from pathlib import Path
from typing import Any
from hive.server import Server

import yaml

def load_servers(path="configs/servers.yaml"):
    cfg = load_yaml(path)
    servers = []

    for name, s in cfg["servers"].items():
        servers.append(
            Server(
                name=name,
                ssh_alias=s["ssh_alias"],
                worker_root=s["worker_root"],
                comfy_url=s["comfy_url"],
                comfy_input_batches=s.get(
                    "comfy_input_batches",
                    "/data/temp/ComfyUI/input/batches",
                ),
                enabled=s.get("enabled", True),
                profile=s.get("profile", {}),
            )
        )

    return servers

def load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise ValueError(f"Config must be a YAML mapping: {path}")

    return data


def load_hive_config(path: str | Path = "configs/hive.yaml") -> dict[str, Any]:
    return load_yaml(path)


def load_servers_config(path: str | Path = "configs/servers.yaml") -> dict[str, Any]:
    return load_yaml(path)

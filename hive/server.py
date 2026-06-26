from dataclasses import dataclass


@dataclass(slots=True)
class Server:

    name: str

    ssh_alias: str

    worker_root: str

    comfy_url: str

    enabled: bool = True

    profile: dict | None = None

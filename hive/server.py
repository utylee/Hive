from dataclasses import dataclass


@dataclass(slots=True)
class Server:
    name: str
    ssh_alias: str
    worker_root: str
    comfy_url: str
    comfy_input_batches: str
    comfy_output_dir: str
    hive_root: str
    hive_python: str
    enabled: bool = True
    profile: dict | None = None


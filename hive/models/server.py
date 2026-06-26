from __future__ import annotations

from dataclasses import dataclass

from hive.models.profile import Profile


@dataclass(slots=True, frozen=True)
class Server:
    name: str
    label: str
    ssh_alias: str
    worker_root: str
    comfy_url: str
    enabled: bool
    profile: Profile

    @classmethod
    def from_dict(cls, name: str, data: dict) -> "Server":
        return cls(
            name=name,
            label=str(data.get("label", name)),
            ssh_alias=str(data["ssh_alias"]).strip(),
            worker_root=str(data.get("worker_root", "/tmp/hive_jobs")),
            comfy_url=str(data.get("comfy_url", "http://127.0.0.1:8188")),
            enabled=bool(data.get("enabled", True)),
            profile=Profile.from_dict(data.get("profile")),
        )

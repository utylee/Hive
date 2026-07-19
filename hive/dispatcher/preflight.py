from __future__ import annotations

from dataclasses import dataclass
from urllib.request import urlopen

from hive.core import remote
from hive.server import Server


@dataclass(slots=True)
class PreflightResult:
    server_name: str
    ssh_ok: bool
    python_ok: bool
    hive_ok: bool
    comfy_ok: bool
    error: str | None = None

    @property
    def ok(self) -> bool:
        return (
            self.ssh_ok
            and self.python_ok
            and self.hive_ok
            and self.comfy_ok
        )


def check_server(
    server: Server,
    *,
    timeout: float = 5.0,
) -> PreflightResult:
    ssh_ok = False
    python_ok = False
    hive_ok = False
    comfy_ok = False

    try:
        remote.exec(
            server.ssh_alias,
            "true",
        )
        ssh_ok = True

        remote.exec(
            server.ssh_alias,
            f"{server.hive_python} --version",
        )
        python_ok = True

        remote.exec(
            server.ssh_alias,
            (
                f"{server.hive_python} "
                "-c 'import hive'"
            ),
        )
        hive_ok = True

        with urlopen(
            server.comfy_url,
            timeout=timeout,
        ) as response:
            comfy_ok = 200 <= response.status < 500

    except Exception as exc:
        return PreflightResult(
            server_name=server.name,
            ssh_ok=ssh_ok,
            python_ok=python_ok,
            hive_ok=hive_ok,
            comfy_ok=comfy_ok,
            error=(
                f"{type(exc).__name__}: {exc}"
            ),
        )

    return PreflightResult(
        server_name=server.name,
        ssh_ok=ssh_ok,
        python_ok=python_ok,
        hive_ok=hive_ok,
        comfy_ok=comfy_ok,
    )

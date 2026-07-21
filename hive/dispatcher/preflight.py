from __future__ import annotations


from dataclasses import dataclass
from time import sleep
from urllib.error import HTTPError
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
    comfy_retries: int = 2,
    retry_delay: float = 0.5,
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


        for attempt in range(
            comfy_retries + 1
        ):
            try:
                with urlopen(
                    server.comfy_url,
                    timeout=timeout,
                ) as response:
                    comfy_ok = (
                        200
                        <= response.status
                        < 500
                    )

                break

            except HTTPError as exc:
                retryable = (
                    exc.code in {502, 503, 504}
                    and attempt < comfy_retries
                )

                if not retryable:
                    raise

                sleep(retry_delay)


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

def filter_healthy_servers(
    servers: list[Server],
    *,
    timeout: float = 5.0,
) -> tuple[list[Server], list[PreflightResult]]:
    healthy_servers = []
    results = []

    for server in servers:
        result = check_server(
            server,
            timeout=timeout,
        )

        results.append(result)

        if result.ok:
            healthy_servers.append(server)

    return healthy_servers, results

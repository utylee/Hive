from __future__ import annotations


def pick_server(
    servers,
    excluded: set[str] | None = None,
    start_index: int = 0,
):
    """
    Return the next enabled server
    that is not excluded.
    """

    excluded = excluded or set()

    if not servers:
        raise RuntimeError(
            "No servers configured."
        )

    for offset in range(len(servers)):
        index = (
            start_index + offset
        ) % len(servers)

        server = servers[index]

        if (
            server.enabled
            and server.name not in excluded
        ):
            return server, index

    raise RuntimeError(
        "No enabled server available."
    )

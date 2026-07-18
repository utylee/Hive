from __future__ import annotations


def pick_server(
    servers,
    excluded: set[str] | None = None,
):
    """
    Return the first enabled server
    that is not excluded.
    """

    excluded = excluded or set()

    for server in servers:
        if (
            server.enabled
            and server.name not in excluded
        ):
            return server

    raise RuntimeError(
        "No enabled server available."
    )

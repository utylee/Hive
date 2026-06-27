from __future__ import annotations


def pick_server(servers):
    """
    Return the first enabled server.

    This is intentionally simple.
    Future versions will consider
    GPU load, queue length, VRAM,
    CPU load, etc.
    """

    for server in servers:
        if server.enabled:
            return server

    raise RuntimeError("No enabled server found.")

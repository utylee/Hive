from __future__ import annotations

import json
from pathlib import Path

from hive.comfy.client import ComfyClient


def main() -> None:
    workflow = json.loads(
        Path("workflows/hd_remaster_rope_facerestore.json").read_text(
            encoding="utf-8",
        )
    )

    client = ComfyClient(
        # "http://localhost:8188",
        "http://192.168.1.122:8188",
    )

    prompt = client.submit(workflow)

    print(f"submitted: {prompt.id}")

    prompt.wait()

    print("completed")

    outputs = prompt.outputs()

    print(outputs)


if __name__ == "__main__":
    main()

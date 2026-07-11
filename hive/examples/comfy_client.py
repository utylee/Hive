from __future__ import annotations

import json
from pathlib import Path

from hive.comfy.client import ComfyClient
from hive.transport.ssh import SSHTransport

import pprint
import random
# import time


def main() -> None:
    workflow_path = (
        Path(__file__).parent
        / "workflows"
        / "hd_remaster_rope_facerestore_api.json"
    )

    workflow = json.loads(
        workflow_path.read_text(
            encoding="utf-8",
        )
    )

    segment = Path("outputs/segment_0000.mp4")
    batch_folder = "hive_test"

    transport = SSHTransport(
        host="m5",
        workspace=Path(
            "/data/temp/ComfyUI/input/batches"
        ) / batch_folder,
    )

    transport.upload(
        segment,
        segment.name,
    )

    workflow["75"]["inputs"]["batch_folder"] = batch_folder
    workflow["75"]["inputs"]["queue_nonce"] = random.randint(
        0,
        999_999_999,
    )

    client = ComfyClient(
        "http://192.168.1.122:8188",
    )

    # workflow["75"]["inputs"]["queue_nonce"] = random.randint(0, 999_999_999)
    # # workflow["75"]["inputs"]["queue_nonce"] = int(time.time()) % 1_000_000_000

    prompt = client.submit(workflow)
    print(f"submitted: {prompt.id}")


    def show_progress(
        current: int,
        total: int,
        elapsed: float,
    ) -> None:
        print(
            f"\rm5  {segment.name}  "
            f"batch {current}/{total}  "
            f"elapsed {elapsed:0.0f}s",
            end="",
            flush=True,
        )

    prompt = client.wait(
        prompt,
        timeout=3600,
        on_progress=show_progress,
    )

    print()

    # prompt = client.wait(
    #     prompt,
    #     timeout=3600,
    # )

    # prompt.wait()

    print("completed")

    pprint.pp(prompt.history)

    outputs = prompt.outputs()

    print(f"images: {len(outputs.images)}")
    print(f"videos: {len(outputs.videos)}")

    output_dir = Path("outputs/comfy")
    output_dir.mkdir(parents=True, exist_ok=True)

    for video in outputs.videos:
        target = output_dir / video.filename
        target.write_bytes(video.download())
        print(f"saved: {target}")

    # outputs = prompt.outputs()

    # output_dir = Path("outputs/comfy")
    # output_dir.mkdir(parents=True, exist_ok=True)

    # print(f"images: {len(outputs.images)}")

    # for image in outputs.images:
    #     target = output_dir / image.filename
    #     target.write_bytes(image.download())
    #     print(f"saved: {target}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import random
import shutil
from pathlib import Path
from typing import Any

from hive.comfy.client import ComfyClient
from hive.workflow_patch import build_comfy_workflow


class ComfyExecutor:
    def execute(
        self,
        job_dir: Path,
        manifest: dict[str, Any],
    ) -> dict[str, Any]:
        parameters = manifest["parameters"]

        source = job_dir / manifest["source"]
        workflow_path = job_dir / parameters["workflow"]

        batch_folder = manifest["id"]
        comfy_input_dir = (
            Path(parameters["comfy_input_batches"])
            / batch_folder
        )

        comfy_input_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            source,
            comfy_input_dir / source.name,
        )

        base_workflow = json.loads(
            workflow_path.read_text(
                encoding="utf-8",
            )
        )

        workflow = build_comfy_workflow(
            base_workflow,
            job={
                "remote_batch_folder": batch_folder,
                "queue_nonce": random.randint(
                    0,
                    999_999_999,
                ),
            },
            server={
                "profile": parameters.get("profile", {}),
            },
        )

        client = ComfyClient(
            parameters["comfy_url"],
        )

        prompt = client.submit(workflow)

        prompt = client.wait(
            prompt,
            timeout=float(
                parameters.get("timeout", 3600)
            ),
        )

        outputs = prompt.outputs()

        output_dir = job_dir / "output"
        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        saved = []

        for video in outputs.videos:
            target = output_dir / video.filename
            target.write_bytes(video.download())
            saved.append(str(target.relative_to(job_dir)))

        return {
            "ok": True,
            "executor": "comfy",
            "outputs": saved,
        }



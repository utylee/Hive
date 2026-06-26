from __future__ import annotations

import shutil
from pathlib import Path


def run_dummy(job: dict) -> dict:
    input_dir = Path(job["input"]["source"])
    output_dir = Path(job["output"]["target"])
    output_dir.mkdir(parents=True, exist_ok=True)

    copied = []

    for file in input_dir.iterdir():
        if file.is_file():
            target = output_dir / file.name
            shutil.copy2(file, target)
            copied.append(file.name)

    return {
        "type": "dummy",
        "copied_files": copied,
    }

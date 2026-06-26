from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path


def create_manifest(
    *,
    project: str,
    job_type: str,
    source: Path,
) -> dict:

    job_id = (
        datetime.now().strftime("%Y%m%d-%H%M%S")
        + "-"
        + uuid.uuid4().hex[:8]
    )

    return {
        "version": 1,
        "id": job_id,
        "project": project,
        "type": job_type,
        "source": str(source),
        "parameters": {},
        "metadata": {},
    }


def save_manifest(
    manifest: dict,
    path: Path,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

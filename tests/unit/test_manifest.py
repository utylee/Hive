from pathlib import Path

from hive.dispatcher.manifest import (
    create_manifest,
    save_manifest,
)


def test_manifest_generation():

    manifest = create_manifest(
        project="vhs_restore",
        job_type="comfy",
        source=Path("/nas/jobs/001.mp4"),
    )

    assert manifest["version"] == 1

    assert manifest["project"] == "vhs_restore"

    assert manifest["type"] == "comfy"

    assert manifest["source"] == "/nas/jobs/001.mp4"

    out = Path("/tmp/hive_test/manifest.json")

    save_manifest(manifest, out)

    assert out.exists()

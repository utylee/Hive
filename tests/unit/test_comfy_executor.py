from pathlib import Path
from types import SimpleNamespace

from hive.executors.comfy import ComfyExecutor


class DummyVideo:
    filename = "result.mp4"

    def download(self) -> bytes:
        return b"video-data"


class DummyPrompt:
    def outputs(self):
        return SimpleNamespace(
            videos=[DummyVideo()],
        )


class DummyClient:
    def __init__(self, base_url: str) -> None:
        assert base_url == "http://localhost:8188"

    def submit(self, workflow: dict):
        assert workflow["75"]["inputs"]["batch_folder"] == "job1"
        return DummyPrompt()

    def wait(
        self,
        prompt,
        timeout: float,
    ):
        assert timeout == 3600
        return prompt


def test_comfy_executor(
    tmp_path: Path,
    monkeypatch,
) -> None:
    job_dir = tmp_path / "job1"
    input_dir = job_dir / "input"
    input_dir.mkdir(parents=True)

    source = input_dir / "segment_0000.mp4"
    source.write_bytes(b"source-video")

    workflow = job_dir / "workflow.json"
    workflow.write_text(
        """
        {
          "7": {
            "class_type": "VHS_BatchManager",
            "inputs": {
              "frames_per_batch": 16
            }
          },
          "75": {
            "class_type": "VHSBatchPrecleanPro",
            "inputs": {
              "batch_folder": "old",
              "queue_nonce": 0
            }
          }
        }
        """,
        encoding="utf-8",
    )

    comfy_input_batches = tmp_path / "comfy_input_batches"

    monkeypatch.setattr(
        "hive.executors.comfy.ComfyClient",
        DummyClient,
    )

    manifest = {
        "id": "job1",
        "source": "input/segment_0000.mp4",
        "parameters": {
            "workflow": "workflow.json",
            "comfy_url": "http://localhost:8188",
            "comfy_input_batches": str(comfy_input_batches),
        },
    }

    executor = ComfyExecutor()

    result = executor.execute(
        job_dir,
        manifest,
    )

    assert result == {
        "ok": True,
        "executor": "comfy",
        "outputs": [
            "output/result.mp4",
        ],
    }

    uploaded = (
        comfy_input_batches
        / "job1"
        / "segment_0000.mp4"
    )

    assert uploaded.read_bytes() == b"source-video"
    assert (job_dir / "output" / "result.mp4").read_bytes() == b"video-data"

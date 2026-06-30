from pathlib import Path

from hive.executors.comfy import ComfyExecutor


def test_comfy_executor_stub() -> None:
    executor = ComfyExecutor()

    result = executor.execute(Path("/tmp"), {})

    assert result["ok"] is True
    assert result["executor"] == "comfy"

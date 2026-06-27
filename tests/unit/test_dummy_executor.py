from pathlib import Path

from hive.worker.dummy import DummyExecutor


def test_dummy_executor():

    ex = DummyExecutor()

    result = ex.execute(Path("/tmp"), {})

    assert result["ok"] is True
    assert result["executor"] == "dummy"

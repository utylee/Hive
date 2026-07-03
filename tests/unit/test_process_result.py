from hive.runtime.process import ProcessResult


def test_process_result_ok() -> None:
    result = ProcessResult(
        returncode=0,
        stdout="hello",
        stderr="",
    )

    assert result.ok


def test_process_result_fail() -> None:
    result = ProcessResult(
        returncode=1,
        stdout="",
        stderr="boom",
    )

    assert not result.ok

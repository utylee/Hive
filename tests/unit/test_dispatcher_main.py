import sys

from hive.dispatcher.main import main


def test_reset_server_state_removes_file(
    tmp_path,
    monkeypatch,
    capsys,
):
    jobs_dir = tmp_path / "jobs"
    work_root = tmp_path / "work"

    jobs_dir.mkdir()
    work_root.mkdir()

    state_path = (
        work_root / "server_state.json"
    )

    state_path.write_text(
        '{"server-a": {}}',
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "hive-dispatcher",
            str(jobs_dir),
            "--work-root",
            str(work_root),
            "--reset-server-state",
        ],
    )

    result = main()

    captured = capsys.readouterr()

    assert result == 0
    assert not state_path.exists()

    assert (
        "Cleared persisted server state"
        in captured.out
    )


def test_reset_server_state_without_file(
    tmp_path,
    monkeypatch,
    capsys,
):
    jobs_dir = tmp_path / "jobs"
    work_root = tmp_path / "work"

    jobs_dir.mkdir()
    work_root.mkdir()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "hive-dispatcher",
            str(jobs_dir),
            "--work-root",
            str(work_root),
            "--reset-server-state",
        ],
    )

    result = main()

    captured = capsys.readouterr()

    assert result == 0

    assert (
        captured.out.strip()
        == "No persisted server state found"
    )

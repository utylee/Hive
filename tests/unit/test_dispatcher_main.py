import sys
import json

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

def test_reset_server_state_for_one_server(
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
        """
{
  "m5": {
    "consecutive_failures": 2,
    "cooldown_until": "2099-01-01T00:00:00+00:00"
  },
  "ccy2": {
    "consecutive_failures": 1,
    "cooldown_until": null
  }
}
""".strip(),
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
            "m5",
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 0

    state = json.loads(
        state_path.read_text(
            encoding="utf-8",
        )
    )

    assert "m5" not in state
    assert "ccy2" in state

    assert (
        captured.out.strip()
        == (
            "Cleared persisted state "
            "for server: m5"
        )
    )

def test_reset_unknown_server_preserves_state(
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

    original_state = {
        "m5": {
            "consecutive_failures": 2,
            "cooldown_until": None,
        },
    }

    state_path.write_text(
        json.dumps(original_state),
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
            "unknown-server",
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 0

    state = json.loads(
        state_path.read_text(
            encoding="utf-8",
        )
    )

    assert state == original_state

    assert (
        captured.out.strip()
        == (
            "No persisted state found for "
            "server: unknown-server"
        )
    )

def test_reset_server_state_preserves_corrupt_file(
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
        "{invalid json",
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
            "m5",
        ],
    )

    result = main()
    captured = capsys.readouterr()

    corrupt_path = (
        work_root
        / "server_state.json.corrupt"
    )

    assert result == 0
    assert not state_path.exists()
    assert corrupt_path.exists()

    assert (
        corrupt_path.read_text(
            encoding="utf-8",
        )
        == "{invalid json"
    )

    assert (
        "Persisted server state was corrupt"
        in captured.out
    )

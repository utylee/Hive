from hive.server import Server

from hive.dispatcher import preflight


class DummyResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def make_server() -> Server:
    return Server(
        name="m5",
        ssh_alias="m5",
        worker_root="/tmp/hive_jobs",
        comfy_url="http://comfy.example",
        comfy_input_batches=(
            "/data/temp/ComfyUI/input/batches"
        ),
        comfy_output_dir=(
            "/data/temp/ComfyUI/output"
        ),
        hive_root="/data/temp/Hive",
        hive_python=(
            "/data/temp/Hive/.venv/bin/python"
        ),
        enabled=True,
        profile={},
    )



def test_check_server_success(
    monkeypatch,
):
    commands = []

    monkeypatch.setattr(
        preflight.remote,
        "exec",
        lambda alias, command: commands.append(
            (alias, command)
        ),
    )

    monkeypatch.setattr(
        preflight,
        "urlopen",
        lambda url, timeout: DummyResponse(),
    )

    result = preflight.check_server(
        make_server(),
    )

    assert result.ok is True
    assert result.error is None
    assert result.ssh_ok is True
    assert result.python_ok is True
    assert result.hive_ok is True
    assert result.comfy_ok is True

    assert commands == [
        ("m5", "true"),
        (
            "m5",
            (
                "/data/temp/Hive/.venv/bin/python "
                "--version"
            ),
        ),
        (
            "m5",
            (
                "/data/temp/Hive/.venv/bin/python "
                "-c 'import hive'"
            ),
        ),
    ]


def test_check_server_stops_on_ssh_failure(
    monkeypatch,
):
    def fail_exec(alias, command):
        raise RuntimeError("ssh failed")

    monkeypatch.setattr(
        preflight.remote,
        "exec",
        fail_exec,
    )

    result = preflight.check_server(
        make_server(),
    )

    assert result.ok is False
    assert result.ssh_ok is False
    assert result.python_ok is False
    assert result.hive_ok is False
    assert result.comfy_ok is False
    assert result.error == (
        "RuntimeError: ssh failed"
    )


def test_check_server_reports_comfy_failure(
    monkeypatch,
):
    monkeypatch.setattr(
        preflight.remote,
        "exec",
        lambda alias, command: None,
    )

    def fail_urlopen(url, timeout):
        raise TimeoutError("comfy timeout")

    monkeypatch.setattr(
        preflight,
        "urlopen",
        fail_urlopen,
    )

    result = preflight.check_server(
        make_server(),
    )

    assert result.ok is False
    assert result.ssh_ok is True
    assert result.python_ok is True
    assert result.hive_ok is True
    assert result.comfy_ok is False
    assert result.error == (
        "TimeoutError: comfy timeout"
    )

def test_filter_healthy_servers(
    monkeypatch,
):
    servers = [
        make_server(),
        Server(
            name="ccy2",
            ssh_alias="ccy2",
            worker_root="/tmp/hive_jobs",
            comfy_url="http://comfy2.example",
            comfy_input_batches="/tmp/input",
            comfy_output_dir="/tmp/output",
            hive_root="/home/utylee/temp/Hive",
            hive_python=(
                "/home/utylee/temp/Hive/"
                ".venv/bin/python"
            ),
            enabled=True,
            profile={},
        ),
    ]

    def fake_check_server(
        server,
        *,
        timeout=5.0,
    ):
        return preflight.PreflightResult(
            server_name=server.name,
            ssh_ok=True,
            python_ok=True,
            hive_ok=True,
            comfy_ok=(
                server.name == "m5"
            ),
            error=(
                None
                if server.name == "m5"
                else "TimeoutError: comfy timeout"
            ),
        )

    monkeypatch.setattr(
        preflight,
        "check_server",
        fake_check_server,
    )

    healthy, results = (
        preflight.filter_healthy_servers(
            servers,
        )
    )

    assert [
        server.name
        for server in healthy
    ] == ["m5"]

    assert [
        result.server_name
        for result in results
    ] == ["m5", "ccy2"]

    assert results[0].ok is True
    assert results[1].ok is False

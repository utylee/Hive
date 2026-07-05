from pathlib import Path

from hive.transport.local import LocalTransport


def test_local_transport_upload_download_execute(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"

    transport = LocalTransport(
        workspace=workspace,
    )

    source = tmp_path / "source.txt"
    downloaded = tmp_path / "downloaded.txt"

    source.write_text("hello", encoding="utf-8")

    # transport.upload(source)
    transport.upload(source, "source.txt")

    # uploaded = workspace / "input" / "source.txt"
    uploaded = workspace / "source.txt"

    assert uploaded.read_text(encoding="utf-8") == "hello"

    output = workspace / "output" / "downloaded.txt"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("done", encoding="utf-8")

    # transport.download(downloaded)
    transport.download(
    "output/downloaded.txt",
    downloaded,
)

    assert downloaded.read_text(encoding="utf-8") == "done"


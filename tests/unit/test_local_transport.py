from pathlib import Path

from hive.transport.local import LocalTransport


def test_local_transport_upload_download_execute(tmp_path: Path) -> None:
    transport = LocalTransport()

    source = tmp_path / "source.txt"
    uploaded = tmp_path / "remote" / "input.txt"
    downloaded = tmp_path / "downloaded.txt"

    source.write_text("hello", encoding="utf-8")

    transport.upload(source, str(uploaded))

    assert uploaded.read_text(encoding="utf-8") == "hello"

    output = tmp_path / "remote" / "output.txt"

    transport.execute(
        [
            "python",
            "-c",
            f"from pathlib import Path; Path({str(output)!r}).write_text('done', encoding='utf-8')",
        ]
    )

    transport.download(str(output), downloaded)

    assert downloaded.read_text(encoding="utf-8") == "done"

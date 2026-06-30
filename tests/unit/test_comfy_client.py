from hive.comfy.client import ComfyClient


def test_client_base_url() -> None:
    client = ComfyClient("http://localhost:8188/")

    assert client.base_url == "http://localhost:8188"

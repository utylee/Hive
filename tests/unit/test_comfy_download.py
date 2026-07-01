from hive.comfy.client import ComfyClient
from hive.comfy.outputs import ImageOutput


class DummyResponse:
    def raise_for_status(self):
        pass

    @property
    def content(self):
        return b"PNGDATA"


class DummySession:
    def get(self, url, *, params=None, timeout=None):
        assert url == "http://localhost:8188/view"

        assert params == {
            "filename": "cat.png",
            "subfolder": "",
            "type": "output",
        }

        return DummyResponse()


def test_download():
    client = ComfyClient(
        "http://localhost:8188",
        session=DummySession(),
    )

    image = ImageOutput(
        client=client,
        filename="cat.png",
        subfolder="",
        type="output",
    )

    data = client.download(image)

    assert data == b"PNGDATA"

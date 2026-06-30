from hive.comfy.client import ComfyClient


class DummyResponse:
    def raise_for_status(self) -> None:
        pass

    def json(self):
        return {
            "abc123": {
                "outputs": {},
            }
        }


class DummySession:
    def get(self, *args, **kwargs):
        return DummyResponse()


def test_history():
    client = ComfyClient(
        "http://localhost:8188",
        session=DummySession(),
    )

    history = client.history("abc123")

    assert "abc123" in history

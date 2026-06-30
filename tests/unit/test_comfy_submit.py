from hive.comfy.client import ComfyClient


class DummyResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {
            "prompt_id": "abc123",
        }


def test_submit(monkeypatch):
    def fake_post(self, *args, **kwargs):
        return DummyResponse()

    monkeypatch.setattr(
        "requests.Session.post",
        fake_post,
    )

    client = ComfyClient(
        "http://localhost:8188/"
    )

    prompt_id = client.submit(
        {
            "1": {
                "class_type": "EmptyLatentImage",
            }
        }
    )

    assert prompt_id == "abc123"

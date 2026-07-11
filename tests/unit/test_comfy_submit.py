from hive.comfy.client import ComfyClient


class DummyResponse:
    ok = True
    status_code = 200
    text = ""
    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return {
            "prompt_id": "abc123",
        }


class DummySession:
    def post(self, *args, **kwargs):
        return DummyResponse()


def test_submit() -> None:
    client = ComfyClient(
        "http://localhost:8188/",
        session=DummySession(),
    )

    prompt = client.submit(
        {
            "1": {
                "class_type": "EmptyLatentImage",
            }
        }
    )


    assert prompt.id == "abc123"

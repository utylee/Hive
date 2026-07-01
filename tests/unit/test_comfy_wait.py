from hive.comfy.client import ComfyClient
from hive.comfy.models import Prompt


class DummyResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


class DummySession:
    def __init__(self):
        self.calls = 0

    def get(self, *args, **kwargs):
        self.calls += 1

        if self.calls == 1:
            return DummyResponse({})

        return DummyResponse(
            {
                "job1": {
                    "status": {
                        "completed": True,
                    }
                }
            }
        )


def test_wait() -> None:
    client = ComfyClient(
        "http://localhost:8188",
        session=DummySession(),
    )

    # prompt = Prompt(id="job1")
    prompt = Prompt(id="job1", client=client)

    client.wait(
        prompt,
        poll_interval=0.001,
    )

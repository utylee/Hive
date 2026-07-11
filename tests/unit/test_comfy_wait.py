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


    def get(
        self,
        url: str,
        *,
        timeout: float,
    ) -> DummyResponse:
        if url.endswith("/history/job1"):
            return DummyResponse(
                {
                    "job1": {
                        "prompt": [
                            0,
                            "job1",
                            {},
                            {
                                "create_time": 123,
                            },
                            [],
                        ],
                        "outputs": {},
                        "status": {
                            "completed": True,
                        },
                    }
                }
            )

        if url.endswith("/queue"):
            return DummyResponse(
                {
                    "queue_running": [],
                    "queue_pending": [],
                }
            )

        if url.endswith("/history"):
            return DummyResponse(
                {
                    "job1": {
                        "prompt": [
                            0,
                            "job1",
                            {},
                            {
                                "create_time": 123,
                            },
                            [],
                        ],
                        "outputs": {},
                        "status": {
                            "completed": True,
                        },
                    }
                }
            )

        raise AssertionError(f"Unexpected URL: {url}")


    # def get(self, *args, **kwargs):
    #     self.calls += 1

    #     if self.calls == 1:
    #         return DummyResponse({})

    #     return DummyResponse(
    #     {
    #         "job1": {
    #             "prompt": [
    #                 0,
    #                 "job1",
    #                 {},
    #                 {
    #                     "create_time": 123,
    #                 },
    #                 [],
    #             ],
    #             "outputs": {},
    #             "status": {
    #                 "completed": True,
    #             },
    #         }
    #     }
    # )



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

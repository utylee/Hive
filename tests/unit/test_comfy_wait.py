from hive.comfy.client import ComfyClient
from hive.comfy.models import Prompt


class DummySession:
    def __init__(self):
        self.count = 0

    def get(self, *args, **kwargs):
        class R:
            def raise_for_status(self): pass

            def json(inner_self):
                # 2번째 호출에서 완료 처리
                if self.count < 1:
                    self.count += 1
                    return {"job1": None}
                return {
                    "job1": {
                        "status": {
                            "completed": True
                        }
                    }
                }

        return R()


def test_wait():
    client = ComfyClient(
        "http://localhost:8188",
        session=DummySession(),
    )

    prompt = Prompt(id="job1")

    client.wait(prompt, poll_interval=0.01)

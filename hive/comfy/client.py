from __future__ import annotations

import time
from typing import Any
from pathlib import Path

import requests

from collections.abc import Callable

from hive.comfy.models import Prompt
from hive.comfy.outputs import ImageOutput



class ComfyClient:
    def __init__(
        self,
        base_url: str,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()

    def save(self, path: str | Path) -> None:
        Path(path).write_bytes(self.download())

    def download(
        self,
        image: ImageOutput,
    ) -> bytes:
        response = self.session.get(
            f"{self.base_url}/view",
            params={
                "filename": image.filename,
                "subfolder": image.subfolder,
                "type": image.type,
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.content

    def submit(
        self,
        workflow: dict[str, Any],
    ) -> Prompt:
        response = self.session.post(
            f"{self.base_url}/prompt",
            json={
                "prompt": workflow,
            },
            timeout=30,
        )

        if not response.ok:
            raise RuntimeError(
                f"Comfy submit failed ({response.status_code})\n"
                f"{response.text}"
            )

        data = response.json()

        if "prompt_id" not in data:
            raise RuntimeError(
                f"Comfy submit returned no prompt_id\n"
                f"{data}"
            )

        return Prompt(
            id=data["prompt_id"],
            client=self,
        )


    # def submit(
    #     self,
    #     workflow: dict[str, Any],
    # ) -> Prompt:
    #     # response = self.session.post(
    #     #     f"{self.base_url}/prompt",
    #     #     json={
    #     #         "prompt": workflow,
    #     #     },
    #     #     timeout=30,
    #     # )

    #     response = requests.get(
    #         "http://192.168.1.122:8188/system_stats",
    #         timeout=10,
    #     )

    #     print(response.status_code)
    #     print(response.text[:1000])

    #     # response.raise_for_status()
    #     if not response.ok:
    #         raise RuntimeError(
    #             f"Comfy submit failed ({response.status_code})\n"
    #             f"{response.text}"
    #         )

    #     data = response.json()

    #     return Prompt(
    #         id=data["prompt_id"],
    #         client=self,
    #     )

    def _history(
        self,
        prompt_id: str,
    ) -> dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/history/{prompt_id}",
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def _queue(self) -> dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/queue",
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def _all_history(self) -> dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/history",
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def wait(
        self,
        prompt: Prompt,
        poll_interval: float = 1.0,
        timeout: float = 300.0,
        on_progress: Callable[[int, int, float], None] | None = None,
    ) -> Prompt:

    # def wait(
    #     self,
    #     prompt: Prompt,
    #     poll_interval: float = 1.0,
    #     timeout: float = 300.0,
    # ) -> Prompt:

        start = time.monotonic()
        create_time: int | None = None

        while True:
            history = self._history(prompt.id)
            job = history.get(prompt.id)

            if job is not None:
                create_time = job["prompt"][3]["create_time"]

                status = job["status"]

                if status["completed"]:
                    queue = self._queue()

                    queued = (
                        queue["queue_running"]
                        + queue["queue_pending"]
                    )

                    matching_item = next(
                        (
                            item
                            for item in queued
                            if item[3].get("create_time") == create_time
                        ),
                        None,
                    )

                    if matching_item is not None and on_progress is not None:
                        queued_workflow = matching_item[2]

                        batch_node = next(
                            (
                                node
                                for node in queued_workflow.values()
                                if node.get("class_type")
                                == "VHS_BatchManager"
                            ),
                            None,
                        )

                        if batch_node is not None:
                            inputs = batch_node["inputs"]
                            frame_count = inputs["count"]
                            frames_per_batch = inputs["frames_per_batch"]
                            current_batch = inputs.get("requeue", 1)

                            total_batches = (
                                frame_count + frames_per_batch - 1
                            ) // frames_per_batch

                            on_progress(
                                current_batch,
                                total_batches,
                                time.monotonic() - start,
                            )


                    # queued = (
                    #     queue["queue_running"]
                    #     + queue["queue_pending"]
                    # )

                    same_batch_running = any(
                        item[3].get("create_time") == create_time
                        for item in queued
                    )

                    if not same_batch_running:
                        histories = self._all_history()

                        matching_jobs = [
                            candidate
                            for candidate in histories.values()
                            if candidate["prompt"][3].get("create_time")
                            == create_time
                        ]

                        prompt.history = (
                            matching_jobs[-1]
                            if matching_jobs
                            else job
                        )

                        return prompt

            if time.monotonic() - start > timeout:
                raise TimeoutError(
                    f"Timed out waiting for prompt {prompt.id}"
                )

            time.sleep(poll_interval)

    # def wait(
    #     self,
    #     prompt: Prompt,
    #     poll_interval: float = 1.0,
    #     timeout: float = 300.0,
    # ) -> Prompt:
    #     start = time.monotonic()

    #     while True:
    #         history = self._history(prompt.id)

    #         job = history.get(prompt.id)

    #         if job is not None:
    #             status = job["status"]

    #             if status["completed"]:
    #                 prompt.history = job
    #                 return prompt

    #         if time.monotonic() - start > timeout:
    #             raise TimeoutError(
    #                 f"Timed out waiting for prompt {prompt.id}"
    #             )

    #         time.sleep(poll_interval)

    def history(
        self,
        prompt_id: str,
    ) -> dict[str, Any]:
        return self._history(prompt_id)


# from __future__ import annotations

# from typing import Any

# import requests
# import time
# from typing import Any

# from hive.comfy.models import Prompt



# class ComfyClient:
#     def __init__(
#         self,
#         base_url: str,
#         session: requests.Session | None = None,
#     ) -> None:
#         self.base_url = base_url.rstrip("/")
#         self.session = session or requests.Session()

#     def submit(
#         self,
#         workflow: dict[str, Any],
#     ) -> str:
#         response = self.session.post(
#             f"{self.base_url}/prompt",
#             json={
#                 "prompt": workflow,
#             },
#             timeout=30,
#         )

#         response.raise_for_status()

#         data = response.json()

#         # return data["prompt_id"]
#         # return Prompt(
#         #     id=data["prompt_id"],
#         # )

#         return Prompt(
#             id=data["prompt_id"],
#             client=self,
#         )

#     def _history(
#         self,
#         prompt: Prompt,
#     ) -> dict[str, Any]:
#         response = self.session.get(
#             f"{self.base_url}/history/{prompt.id}",
#             timeout=30,
#         )

#         response.raise_for_status()

#         return response.json()

#     def wait(
#         self,
#         prompt: Prompt,
#         poll_interval: float = 1.0,
#         timeout: float = 300.0,
#     ) -> None:
#         start = time.monotonic()

#         while True:
#             # history = self._history(prompt)
#             history = self._history(prompt.id)

#             job = history.get(prompt.id)

#             if job is not None:
#                 status = job["status"]

#                 if status["completed"]:
#                     return

#             if time.monotonic() - start > timeout:
#                 raise TimeoutError(
#                     f"Timed out waiting for prompt {prompt.id}"
#                 )

#             time.sleep(poll_interval)



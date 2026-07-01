from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from hive.comfy.outputs import ImageOutput, Outputs

if TYPE_CHECKING:
    from hive.comfy.client import ComfyClient


@dataclass(slots=True)
class Prompt:
    id: str
    client: ComfyClient
    history: dict[str, Any] | None = None

    def wait(self) -> Prompt:
        return self.client.wait(self)

    def outputs(self) -> Outputs:
        result = Outputs()

        if self.history is None:
            raise RuntimeError("Prompt has no history. Call wait() first.")

        for node in self.history.get("outputs", {}).values():
            for image in node.get("images", []):
                result.images.append(
                    ImageOutput(
                        client=self.client,
                        filename=image["filename"],
                        subfolder=image.get("subfolder", ""),
                        type=image.get("type", "output"),
                    )
                )

        return result

    def download(self) -> bytes:
        return self.client.download(self)

# # @dataclass(slots=True, frozen=True)
# @dataclass(slots=True)
# class Prompt:
#     id: str
#     client: "ComfyClient"
#     history: dict[str, Any] | None = None 

#     def outputs(self) -> Outputs:
#         result = Outputs()

#         if self.history is None:
#             raise RuntimeError("Prompt has no history. Call wait() first.")

#         for node in self.history.get("outputs", {}).values():
#             for image in node.get("images", []):
#                 result.images.append(
#                     ImageOutput(
#                         filename=image["filename"],
#                         subfolder=image.get("subfolder", ""),
#                         type=image.get("type", "output"),
#                     )
#                 )

#         return result


@dataclass(slots=True, frozen=True)
class Output:
    filename: str
    subfolder: str
    type: str

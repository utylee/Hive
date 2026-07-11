from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hive.comfy.client import ComfyClient


@dataclass(slots=True)
class ImageOutput:
    client: ComfyClient
    filename: str
    subfolder: str
    type: str

    def download(self) -> bytes:
        return self.client.download(self)


@dataclass(slots=True)
class VideoOutput:
    client: ComfyClient
    filename: str
    subfolder: str
    type: str
    format: str | None = None

    def download(self) -> bytes:
        return self.client.download(self)


@dataclass(slots=True)
class Outputs:
    images: list[ImageOutput] = field(default_factory=list)
    videos: list[VideoOutput] = field(default_factory=list)


# from __future__ import annotations

# from dataclasses import dataclass, field

# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#     from hive.comfy.client import ComfyClient


# @dataclass(slots=True)
# class ImageOutput:
#     client: ComfyClient

#     filename: str
#     subfolder: str
#     type: str

#     def download(self) -> bytes:
#         return self.client.download(self)


# @dataclass(slots=True)
# class Outputs:
#     images: list[ImageOutput] = field(default_factory=list)

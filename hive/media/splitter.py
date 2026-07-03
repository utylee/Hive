from __future__ import annotations

from dataclasses import dataclass
import math

@dataclass(slots=True, frozen=True)
class Segment:
    index: int

    start: float

    duration: float




class MovieSplitter:
    def split(
        self,
        *,
        duration: float,
        segment_length: float,
    ) -> list[Segment]:

        result: list[Segment] = []

        count = math.ceil(duration / segment_length)

        for i in range(count):

            start = i * segment_length

            remaining = duration - start

            result.append(
                Segment(
                    index=i,
                    start=start,
                    duration=min(
                        remaining,
                        segment_length,
                    ),
                )
            )

        return result

from __future__ import annotations

import json
import subprocess
from pathlib import Path


class MovieProbe:
    def duration(
        self,
        movie: Path,
    ) -> float:
        completed = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                str(movie),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        data = json.loads(completed.stdout)

        return float(data["format"]["duration"])

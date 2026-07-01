from __future__ import annotations

from typing import Protocol

from .job import Job
from .task import Task


class Backend(Protocol):
    def submit(self, job: Job) -> Task:
        ...

from __future__ import annotations


class ComfyExecutor:
    def execute(self, job_dir, manifest):
        return {
            "ok": True,
            "executor": "comfy",
        }

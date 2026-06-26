from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path

from worker.executors.dummy import run_dummy


def execute(job: dict) -> dict:
    job_type = job.get("type")

    if job_type == "dummy":
        return run_dummy(job)

    raise ValueError(f"Unsupported job type: {job_type}")


def run(job_path: Path) -> int:
    job = json.loads(job_path.read_text(encoding="utf-8"))
    result_path = job_path.parent / "result.json"

    started = time.time()

    try:
        result = execute(job)
        result["ok"] = True
        result["elapsed_sec"] = round(time.time() - started, 3)

    except Exception as e:
        result = {
            "ok": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "elapsed_sec": round(time.time() - started, 3),
        }

    result_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return 0 if result.get("ok") else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run")
    run_parser.add_argument("job_json")

    args = parser.parse_args()

    if args.command == "run":
        return run(Path(args.job_json))

    return 2


if __name__ == "__main__":
    raise SystemExit(main())



##!/usr/bin/env python3

#import json
#import sys
#import time
#import urllib.request
#from pathlib import Path

#from hive.workflow_patch import build_comfy_workflow


#def post_json(url: str, payload: dict) -> dict:
#    data = json.dumps(payload).encode("utf-8")
#    req = urllib.request.Request(
#        url,
#        data=data,
#        headers={"Content-Type": "application/json"},
#        method="POST",
#    )

#    with urllib.request.urlopen(req, timeout=30) as res:
#        return json.loads(res.read().decode("utf-8"))


#def run_comfy(job: dict) -> dict:
#    workflow_path = Path(job["workflow_path"])
#    base_workflow = json.loads(workflow_path.read_text(encoding="utf-8"))

#    workflow = build_comfy_workflow(
#        base_workflow=base_workflow,
#        job=job,
#        server=job["server"],
#    )

#    comfy_url = job["server"]["comfy_url"].rstrip("/")
#    response = post_json(
#        f"{comfy_url}/prompt",
#        {
#            "prompt": workflow,
#            "client_id": f"hive-{job['job_id']}",
#        },
#    )

#    return {
#        "ok": True,
#        "type": "comfy",
#        "prompt_response": response,
#    }


#def execute(job: dict) -> dict:
#    job_type = job["type"]

#    if job_type == "comfy":
#        return run_comfy(job)

#    raise ValueError(f"Unsupported job type: {job_type}")


#def main() -> int:
#    if len(sys.argv) != 3 or sys.argv[1] != "run":
#        print("Usage: hive-worker run /path/to/job.json", file=sys.stderr)
#        return 2

#    job_path = Path(sys.argv[2])
#    job = json.loads(job_path.read_text(encoding="utf-8"))

#    result_path = job_path.parent / "result.json"

#    try:
#        started = time.time()
#        result = execute(job)
#        result["elapsed_sec"] = round(time.time() - started, 3)
#        result_path.write_text(
#            json.dumps(result, ensure_ascii=False, indent=2),
#            encoding="utf-8",
#        )
#        return 0

#    except Exception as e:
#        error = {
#            "ok": False,
#            "error": str(e),
#        }
#        result_path.write_text(
#            json.dumps(error, ensure_ascii=False, indent=2),
#            encoding="utf-8",
#        )
#        return 1


#if __name__ == "__main__":
#    raise SystemExit(main())

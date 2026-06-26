from pathlib import Path

from hive.dispatcher.scanner import Scanner


def main() -> int:

    scanner = Scanner(
        Path("/tmp/hive_test/jobs")
    )

    jobs = scanner.scan()

    print(f"Found {len(jobs)} jobs")

    for job in jobs:
        print(job.name)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


##!/usr/bin/env python3

#import argparse
#import json
#import shutil
#import subprocess
#import time
#import uuid
#from pathlib import Path

#import yaml


#def sh(cmd: list[str]) -> None:
#    print("+", " ".join(cmd))
#    subprocess.run(cmd, check=True)


#def load_yaml(path: Path) -> dict:
#    return yaml.safe_load(path.read_text(encoding="utf-8"))


#def enabled_servers(servers_config: dict) -> dict:
#    return {
#        name: server
#        for name, server in servers_config["servers"].items()
#        if server.get("enabled", True)
#    }


#def scan_jobs(hive_config: dict) -> list[Path]:
#    jobs_dir = Path(hive_config["nas"]["jobs_dir"])
#    pattern = hive_config["job"]["file_pattern"]
#    return sorted(jobs_dir.glob(pattern))


#def make_job_id(input_file: Path) -> str:
#    safe_stem = input_file.stem.replace(" ", "_")
#    return f"{safe_stem}-{uuid.uuid4().hex[:8]}"


#def rsync_to_remote(local_path: Path, ssh_alias: str, remote_path: str) -> None:
#    sh([
#        "rsync",
#        "-av",
#        "--progress",
#        str(local_path),
#        f"{ssh_alias}:{remote_path}",
#    ])


#def rsync_from_remote(ssh_alias: str, remote_path: str, local_path: Path) -> None:
#    local_path.mkdir(parents=True, exist_ok=True)
#    sh([
#        "rsync",
#        "-av",
#        "--progress",
#        f"{ssh_alias}:{remote_path}",
#        str(local_path),
#    ])


#def ssh(ssh_alias: str, command: str) -> None:
#    sh(["ssh", ssh_alias, command])


#def build_remote_job(
#    job_id: str,
#    input_file: Path,
#    server_name: str,
#    server: dict,
#    workflow_remote_path: str,
#) -> dict:
#    worker_root = server["worker_root"]
#    remote_job_dir = f"{worker_root}/{job_id}"
#    remote_input_dir = f"{remote_job_dir}/input"
#    remote_output_dir = f"{remote_job_dir}/output"

#    return {
#        "job_id": job_id,
#        "type": "comfy",
#        "server_name": server_name,
#        "server": server,
#        "input_filename": input_file.name,
#        "remote_job_dir": remote_job_dir,
#        "remote_input_dir": remote_input_dir,
#        "remote_output_dir": remote_output_dir,
#        "remote_batch_folder": remote_input_dir,
#        "workflow_path": workflow_remote_path,
#    }


#def dispatch_one(
#    input_file: Path,
#    server_name: str,
#    server: dict,
#    hive_config: dict,
#    workflow_path: Path,
#) -> bool:
#    ssh_alias = server["ssh_alias"]
#    job_id = make_job_id(input_file)

#    worker_root = server["worker_root"]
#    remote_job_dir = f"{worker_root}/{job_id}"
#    remote_input_dir = f"{remote_job_dir}/input"
#    remote_output_dir = f"{remote_job_dir}/output"
#    remote_job_json = f"{remote_job_dir}/job.json"
#    remote_workflow_json = f"{remote_job_dir}/workflow_api.json"

#    local_tmp = Path("/tmp") / "hive_dispatcher" / job_id
#    local_tmp.mkdir(parents=True, exist_ok=True)

#    job = build_remote_job(
#        job_id=job_id,
#        input_file=input_file,
#        server_name=server_name,
#        server=server,
#        workflow_remote_path=remote_workflow_json,
#    )

#    local_job_json = local_tmp / "job.json"
#    local_job_json.write_text(
#        json.dumps(job, ensure_ascii=False, indent=2),
#        encoding="utf-8",
#    )

#    print(f"\n=== Dispatch {input_file.name} -> {server_name} / {job_id} ===")

#    ssh(ssh_alias, f"mkdir -p {remote_input_dir} {remote_output_dir}")

#    rsync_to_remote(input_file, ssh_alias, f"{remote_input_dir}/")
#    rsync_to_remote(local_job_json, ssh_alias, remote_job_json)
#    rsync_to_remote(workflow_path, ssh_alias, remote_workflow_json)

#    worker_cmd = f"python3 -m hive.worker run {remote_job_json}"
#    ssh(ssh_alias, worker_cmd)

#    local_result_dir = Path("/tmp") / "hive_results" / job_id
#    rsync_from_remote(ssh_alias, f"{remote_job_dir}/result.json", local_result_dir)

#    result_path = local_result_dir / "result.json"
#    result = json.loads(result_path.read_text(encoding="utf-8"))

#    if result.get("ok"):
#        output_dir = Path(hive_config["nas"]["output_dir"]) / job_id
#        archive_dir = Path(hive_config["nas"]["archive_dir"])
#        archive_dir.mkdir(parents=True, exist_ok=True)

#        rsync_from_remote(ssh_alias, f"{remote_output_dir}/", output_dir)

#        shutil.move(str(input_file), str(archive_dir / input_file.name))
#        print(f"OK: {job_id}")
#        return True

#    failed_dir = Path(hive_config["nas"]["failed"])
#    failed_dir.mkdir(parents=True, exist_ok=True)
#    shutil.move(str(input_file), str(failed_dir / input_file.name))

#    print(f"FAILED: {job_id}")
#    print(result)
#    return False


#def main() -> int:
#    parser = argparse.ArgumentParser()
#    parser.add_argument("--hive-config", default="configs/hive.yaml")
#    parser.add_argument("--servers-config", default="configs/servers.yaml")
#    parser.add_argument("--workflow", default="configs/workflow_api.json")
#    parser.add_argument("--once", action="store_true")
#    args = parser.parse_args()

#    hive_config = load_yaml(Path(args.hive_config))
#    servers_config = load_yaml(Path(args.servers_config))
#    servers = enabled_servers(servers_config)

#    if not servers:
#        raise RuntimeError("No enabled servers")

#    workflow_path = Path(args.workflow)

#    server_items = list(servers.items())
#    server_index = 0

#    while True:
#        files = scan_jobs(hive_config)

#        if not files:
#            print("No jobs.")
#            if args.once:
#                return 0
#            time.sleep(5)
#            continue

#        for input_file in files:
#            server_name, server = server_items[server_index % len(server_items)]
#            server_index += 1

#            try:
#                dispatch_one(
#                    input_file=input_file,
#                    server_name=server_name,
#                    server=server,
#                    hive_config=hive_config,
#                    workflow_path=workflow_path,
#                )
#            except Exception as e:
#                print(f"ERROR: {input_file.name}: {e}")

#        if args.once:
#            return 0


#if __name__ == "__main__":
#    raise SystemExit(main())

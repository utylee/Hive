# examples/hd_remaster.py

from pathlib import Path

from hive.runtime.executor import Executor
from hive.runtime.worker import Worker
from hive.runtime.worker_pool import WorkerPool
from hive.transport.local import LocalTransport
from hive.transport.ssh import SSHTransport
from hive.workflows.hd_remaster import HDRemasterWorkflow


def main() -> None:
    input_movie = Path("movie.mp4")
    workspace = Path("/home/utylee/hive_workspace")
    output_dir = Path("outputs")

    output_dir.mkdir(parents=True, exist_ok=True)

    workflow = HDRemasterWorkflow()
    tasks = workflow.plan(input_movie)

    worker = Worker(
        # transport=LocalTransport(
        #     workspace=workspace,
        # )
        transport = SSHTransport(
            host="m5",
            workspace=workspace
        )
    )

    pool = WorkerPool(
        workers=[worker],
    )
    executor = Executor(pool)

    executor.map(tasks)

    for task in tasks:
        for output in task.outputs:
            target = output_dir / output.name
            if output.exists():
                output.replace(target)

    print("done")

if __name__ == "__main__":
    main()

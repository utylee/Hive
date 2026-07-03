from hive.runtime.worker import Worker
from hive.runtime.worker_pool import WorkerPool


class DummyTransport:
    def upload(self, *args, **kwargs):
        pass

    def execute(self, *args, **kwargs):
        pass

    def download(self, *args, **kwargs):
        pass


def test_worker_pool_acquire() -> None:
    worker = Worker(DummyTransport())

    pool = WorkerPool([worker])

    assert pool.acquire() is worker


def test_empty_worker_pool() -> None:
    pool = WorkerPool([])

    try:
        pool.acquire()
    except RuntimeError:
        return

    assert False

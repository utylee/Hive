from pathlib import Path
import shutil

from hive.dispatcher.scanner import Scanner


def test_scan_mp4():
    root = Path("/tmp/hive_scanner")

    if root.exists():
        shutil.rmtree(root)

    root.mkdir(parents=True)

    (root / "001.mp4").touch()
    (root / "002.mp4").touch()
    (root / "003.mov").touch()
    (root / "README.txt").touch()

    scanner = Scanner(root)

    jobs = scanner.scan()

    assert len(jobs) == 2
    assert jobs[0].name == "001.mp4"
    assert jobs[1].name == "002.mp4"



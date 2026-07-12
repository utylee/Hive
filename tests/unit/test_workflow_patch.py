from hive.workflow_patch import build_comfy_workflow


def test_build_comfy_workflow() -> None:
    base_workflow = {
        "7": {
            "class_type": "VHS_BatchManager",
            "inputs": {
                "frames_per_batch": 16,
            },
        },
        "75": {
            "class_type": "VHSBatchPrecleanPro",
            "inputs": {
                "batch_folder": "old",
                "queue_nonce": 0,
            },
        },
    }

    workflow = build_comfy_workflow(
        base_workflow,
        job={
            "remote_batch_folder": "hive/job1",
            "queue_nonce": 123,
        },
        server={
            "profile": {
                "frames_per_batch": 8,
            },
        },
    )

    assert workflow["75"]["inputs"]["batch_folder"] == "hive/job1"
    assert workflow["75"]["inputs"]["queue_nonce"] == 123
    assert workflow["7"]["inputs"]["frames_per_batch"] == 8

    assert base_workflow["75"]["inputs"]["batch_folder"] == "old"

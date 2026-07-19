import copy


def find_nodes_by_class(workflow: dict, class_type: str) -> list[dict]:
    nodes = []
    for node_id, node in workflow.items():
        if isinstance(node, dict) and node.get("class_type") == class_type:
            nodes.append(node)
    return nodes


def patch_first_node_input(
    workflow: dict,
    class_type: str,
    input_name: str,
    value,
) -> None:
    nodes = find_nodes_by_class(workflow, class_type)

    if not nodes:
        raise ValueError(f"Node class_type not found: {class_type}")

    node = nodes[0]
    inputs = node.setdefault("inputs", {})
    inputs[input_name] = value

def build_comfy_workflow(
    base_workflow: dict,
    job: dict,
    server: dict,
) -> dict:
    workflow = copy.deepcopy(base_workflow)

    profile = server.get("profile", {})

    patch_first_node_input(
        workflow,
        "VHSBatchPrecleanPro",
        "batch_folder",
        job["remote_batch_folder"],
    )

    patch_first_node_input(
        workflow,
        "VHSBatchPrecleanPro",
        "output_folder",
        job["output_folder"],
    )

    patch_first_node_input(
        workflow,
        "VHSBatchPrecleanPro",
        "queue_nonce",
        job["queue_nonce"],
    )

    if "frames_per_batch" in profile:
        patch_first_node_input(
            workflow,
            "VHS_BatchManager",
            "frames_per_batch",
            profile["frames_per_batch"],
        )

    return workflow


# def build_comfy_workflow(
#     base_workflow: dict,
#     job: dict,
#     server: dict,
# ) -> dict:
#     workflow = copy.deepcopy(base_workflow)

#     profile = server.get("profile", {})
#     batch_folder = job["remote_batch_folder"]

#     patch_first_node_input(
#         workflow,
#         "VHS_BatchManager",
#         "batch_folder",
#         batch_folder,
#     )

#     if "frames_per_batch" in profile:
#         patch_first_node_input(
#             workflow,
#             "VHS_BatchManager",
#             "frames_per_batch",
#             profile["frames_per_batch"],
#         )

#     if "cleanup_threshold" in profile:
#         patch_first_node_input(
#             workflow,
#             "VHSBatchPrecleanPro",
#             "cleanup_threshold",
#             profile["cleanup_threshold"],
#         )

#     patch_first_node_input(
#         workflow,
#         "VHS_BatchManager",
#         "queue_nonce",
#         job["job_id"],
#     )

#     return workflow

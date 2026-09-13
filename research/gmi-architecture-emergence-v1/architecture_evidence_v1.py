"""Read exact pre-existing parent records; never execute their VM or campaign."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def read_parent(path):
    binding = json.loads((HERE/"PARENT_BINDINGS_V1.json").read_text())["files"][path]
    data = (REPO/path).read_bytes()
    if len(data) != binding["bytes"] or hashlib.sha256(data).hexdigest() != binding["sha256"]:
        raise ValueError("bound parent bytes changed")
    return json.loads(data)


def gradient_facts(row):
    graph = row["genotype"]
    grad = {n for n, (kind, _params) in graph["nodes"].items() if kind == "GRAD"}
    stages = {stage["stage"]: stage for stage in row["stages"]}
    outgoing = [edge for edge in graph["edges"] if edge[0] in grad]
    before = stages["query_before"]["cells"]["dense_w0"]
    after = stages["feedback_before_end_event"]["cells"]["dense_w0"]
    writes = stages["feedback_before_end_event"]["writes_in_event"]
    return {"outgoing_edges_from_graph": outgoing, "weight_before": before,
            "weight_after": after, "write_recorded": "dense_w0" in writes,
            "output_before": row["outputs"]["before"],
            "output_after": row["outputs"]["after"]}


def retained_evidence():
    nar = read_parent("research/gmi-native-adjoint-repair-v1/RECEIPT_V1.json")
    census = read_parent("research/gmi-b6-consumer-census-v1/CONSUMER_CENSUS_RECEIPT_V1.json")
    rows = {version: gradient_facts(nar["native_vm_controls"]["B0/"+version+"/nonzero_input"])
            for version in ("old", "corrected")}
    sources = census["source_archive_summaries"]
    return {"native_no_return_edge_controls": rows,
            "retained_source_archives": len(sources),
            "retained_source_cells": sum(a["summary"]["rows"] for a in sources),
            "retained_source_grad_rows": sum(len(a["GRAD_graphs"]) for a in sources),
            "exported_rows": len(census["all_arm_rows"]),
            "exported_distinct_graphs": census["all_arm_summary"]["distinct_serialized_graphs"],
            "reported_34_cell_capabilities_recomputed": False,
            "new_native_or_ecology_calls": 0}

"""No-alarm checks against all 437 previously retained structural descriptions."""
from pathlib import Path
import json
import sys
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from contract_v1 import require, same, strict_json, sha
from consumer_structure_v1 import inspect
from scan_retained_v1 import scan_record
from source_contract_v1 import bound_files, current_contract, retained_inputs


def run():
    binding, bound = bound_files()
    files = retained_inputs()
    kinds, roles = current_contract()
    prior = strict_json(bound["raw/parent/CONSUMER_CENSUS_RECEIPT_V1.json"])
    original = prior["all_arm_rows"] + prior["legacy_scan_rows"]
    scanned, by_origin = [], {}
    for name, raw in sorted(files.items()):
        if name.startswith(("sources/", "pr551/STAGE_B6_")):
            record = scan_record(name, raw, kinds, roles)
            scanned.append(record)
            for row in record["rows"]:
                by_origin[(name, tuple(row["source_fields"]))] = row
    for row in original:
        key = (row["origin"]["member"], tuple(row["origin"]["fields"]))
        same(by_origin[key]["native_role_adjacency"], row["native_role_adjacency"], "prior arm/scan roles")
    legacy = [by_origin[(r["origin"]["member"], tuple(r["origin"]["fields"]))] for r in prior["legacy_scan_rows"]]
    require(len(legacy) == 17 and sum(bool(r["numeric_parameter_routes"]) for r in legacy) == 6, "legacy typed-port baseline")
    source_rows = [r for rec in scanned if rec["source"].startswith("sources/") for r in rec["rows"]]
    # Independent retained graph oracle: enumerate each DENSE/EDGE closure by reverse source.
    comparisons = 0
    for rec in scanned:
        record = strict_json(files[rec["source"]])
        for row in rec["rows"]:
            require(row["status"] == "STRUCTURE_INSPECTED", "real retained graph unavailable")
            text = record
            for field in row["source_fields"]:
                text = text[field]
            graph = strict_json(text)
            nodes, edges = graph["nodes"], graph["edges"]
            observed = set()
            for start, value in nodes.items():
                if value[0] != "DENSE": continue
                for end, info in nodes.items():
                    if info[0] not in roles: continue
                    for a, b, port in edges:
                        if b != end: continue
                        cursor, visited = a, set()
                        while cursor != start and nodes[cursor][0] == "EDGE" and cursor not in visited:
                            visited.add(cursor)
                            incoming = [x for x, y, p in edges if y == cursor and p == 0]
                            if not incoming: break
                            cursor = incoming[0]
                        if cursor == start:
                            role = next(r for r, p in roles[info[0]].items() if p == port)
                            observed.add((start, end, role, port))
            actual = {(r["dense"], r["path"][-1], r["role"], r["port"])
                      for r in row["native_role_adjacency"]}
            require(actual == observed, "independent reverse-route oracle")
            comparisons += 1
    require(len(source_rows) == 350 and sum(bool(r["grad_nodes"]) for r in source_rows) == 8,
            "retained source no-alarm counts")
    return {"schema": "PR551_CONSUMER_REPAIR_V1", "status": "PASS",
            "base_commit": binding["base_commit"], "native_roles": roles,
            "prior_census_sha256": sha(bound["raw/parent/CONSUMER_CENSUS_RECEIPT_V1.json"]),
            "prior_arm_and_legacy_role_comparisons": len(original),
            "independent_reverse_route_comparisons": comparisons,
            "legacy_scan_rows": len(legacy), "legacy_numeric_parameter_rows": 6,
            "retained_source_rows": len(source_rows), "retained_grad_source_rows": 8,
            "records": scanned, "new_genotype_or_ecology_executions": 0,
            "live_34_of_677_population": "NOT_RECONSTRUCTED_OR_AUTHENTICATED"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True, allow_nan=False))

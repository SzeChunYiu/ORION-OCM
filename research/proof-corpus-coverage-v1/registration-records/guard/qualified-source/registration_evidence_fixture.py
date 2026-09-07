import copy
import hashlib
import json

COMMIT = "1" * 40
TREE = "2" * 40
STAGES = ["RESOURCE_SETUP", "ACQUISITION", "BUILD", "ASSOCIATION", "EXPORT", "PREPARE", "CHECK"]

def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()

def fixture():
    rows = []
    for key in ["alpha", "beta", "gamma", "delta", "epsilon"]:
        row = {"key": key, "assignment_digest": hashlib.sha256(b"ocm.f1.semantic-coverage.v1\0" + COMMIT.encode() + b"\0" + key.encode()).hexdigest()}
        for kind, prefix in [("wrapper", "Theorems/Thm_"), ("solution", "P2M/Sol/S_")]:
            row[kind] = {"path": prefix + key + ".lean", "oid": "3" * 40, "sha256": "4" * 64, "bytes": 4, "mode": "100644", "state": "ACCEPTED"}
        rows.append(row)
    rows.sort(key=lambda r: (r["assignment_digest"], r["key"]))
    pop = {"schema": "ocm.f1.population.v1", "commit": COMMIT, "tree": TREE, "count": len(rows), "rows": rows}
    chosen = copy.deepcopy(rows[:4])
    for rank, row in enumerate(chosen):
        row.update(assignment_rank=rank, state="ASSIGNED_NO_DISPATCH", stages=[{"stage": s, "state": "NOT_DISPATCHED", "cause": "REGISTRATION_ONLY", "measured_cost": None} for s in STAGES])
    raw = canonical(pop)
    ass = {"schema": "ocm.f1.assignments.v1", "denominator": 4, "continuation_cursor": 4, "population": {"path": "/original/POPULATION.json", "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}, "rows": chosen}
    reg = {"schema": "ocm.f1.registration.v1", "population_count": 5, "assignment_count": 4, "continuation_cursor": 4, "semantic_checks_reached": 0, "git_proof_blob_bodies_read": 0, "wrapper_source_parsed": False, "state": "PROVISIONAL_UNTIL_SEAL"}
    return pop, ass, reg

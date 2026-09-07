"""Check the already-registered full ordering; never rerun the registrar."""
import hashlib
import re
from registration_evidence_archive import canonical, identity, require

STAGES = ["RESOURCE_SETUP", "ACQUISITION", "BUILD", "ASSOCIATION", "EXPORT", "PREPARE", "CHECK"]


def exact_int(value, expected, reason):
    require(type(value) is int and value == expected, reason)


def verify_order(population, assignments, registration, expected_count, commit, tree):
    p, a, reg = population, assignments, registration
    require(set(p) == {"schema", "commit", "tree", "count", "rows"}, "population shape")
    require(p["schema"] == "ocm.f1.population.v1" and p["commit"] == commit and p["tree"] == tree, "population authority")
    exact_int(p["count"], expected_count, "population count")
    rows = p["rows"]
    require(isinstance(rows, list) and len(rows) == expected_count, "population denominator")
    keys = set(); order = []
    for row in rows:
        require(isinstance(row, dict) and set(row) == {"key", "assignment_digest", "wrapper", "solution"}, "row shape")
        key = row["key"]
        require(isinstance(key, str) and re.fullmatch("[A-Za-z0-9_']+", key) and key not in keys, "invalid or duplicate population key")
        keys.add(key)
        digest = hashlib.sha256(b"ocm.f1.semantic-coverage.v1\0" + commit.encode("ascii") + b"\0" + key.encode("utf-8")).hexdigest()
        require(row["assignment_digest"] == digest, "assignment digest differs")
        order.append((bytes.fromhex(digest), key.encode("utf-8")))
        for kind, prefix in [("wrapper", "Theorems/Thm_"), ("solution", "P2M/Sol/S_")]:
            item = row[kind]
            require(isinstance(item, dict) and set(item) == {"path", "oid", "sha256", "bytes", "mode", "state"}, "file metadata shape")
            require(item["path"] == prefix + key + ".lean" and item["mode"] == "100644" and item["state"] == "ACCEPTED", "file metadata scope")
            require(type(item["bytes"]) is int and item["bytes"] >= 0, "file metadata bytes")
            for field, length in [("oid", 40), ("sha256", 64)]:
                require(isinstance(item[field], str) and re.fullmatch("[0-9a-f]{" + str(length) + "}", item[field]), "file metadata digest")
    require(order == sorted(order), "complete population ordering differs")
    require(set(a) == {"schema", "denominator", "continuation_cursor", "population", "rows"} and a["schema"] == "ocm.f1.assignments.v1", "assignment shape")
    exact_int(a["denominator"], 4, "assignment denominator")
    exact_int(a["continuation_cursor"], 4, "continuation cursor")
    require(isinstance(a["population"], dict) and set(a["population"]) == {"path", "sha256", "bytes"}, "population reference shape")
    require({k: a["population"][k] for k in ("sha256", "bytes")} == identity(canonical(p)), "population reference identity")
    expected = []
    for rank, row in enumerate(rows[:4]):
        expected.append(dict(row, assignment_rank=rank, state="ASSIGNED_NO_DISPATCH",
            stages=[{"stage": s, "state": "NOT_DISPATCHED", "cause": "REGISTRATION_ONLY", "measured_cost": None} for s in STAGES]))
    require(canonical(a["rows"]) == canonical(expected), "assigned rows or stage states differ")
    require(reg["schema"] == "ocm.f1.registration.v1" and reg["state"] == "PROVISIONAL_UNTIL_SEAL", "registration state")
    for field, value in [("population_count", expected_count), ("assignment_count", 4), ("continuation_cursor", 4), ("semantic_checks_reached", 0), ("git_proof_blob_bodies_read", 0)]:
        exact_int(reg[field], value, "registration " + field)
    require(reg["wrapper_source_parsed"] is False, "wrapper source parsed")
    return {"population": expected_count, "assignments": 4, "continuation_cursor": 4}

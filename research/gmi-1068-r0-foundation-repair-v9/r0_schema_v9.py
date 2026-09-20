"""Closed schemas for the historical JSON records, including optional authority fields."""
TOP = {
    "ATOMIC_CHECKLIST_V1.json": {"schema": str, "source_issue": int, "source_main": str,
        "freeze_commit": str, "doctrine": str, "row_count": int, "rows": list},
    "THEORY_DAG_V1.json": {"schema": str, "source_issue": int, "nodes": list, "dependencies": dict},
    "PARENT_REGISTRY_V1.json": {"schema": str, "source_issue": int, "entries": list},
    "THEOREM_STATUS_V1.json": {"schema": str, "allowed_status": list, "entries": list},
    "MERGE_GATE_V1.json": {"schema": str, "source_issue": int, "requirements": list,
        "valid_nonpositive_terminals": list},
    "RESULT_V1.json": {"schema": str, "source_issue": int, "freeze_commit": str,
        "atomic_rows": int, "rounds": int, "parent_entries": int, "theorem_entries": int,
        "dag_nodes": int, "expected_hostiles": int, "status": str, "claim_ceiling": str},
}
ROWS = {
    "ATOMIC_CHECKLIST_V1.json": {"id": str, "round": str, "title": str, "evidence_kind": str,
        "status": str, "authoritative_owner": str, "closes_by_prose": bool},
    "PARENT_REGISTRY_V1.json": {"id": str, "source_id": str, "title": str, "role": str, "lane": str},
    "THEOREM_STATUS_V1.json": {"id": str, "title": str, "status": str, "owner_round": str},
}
EVIDENCE = {
    "T-TWO-FACTOR": "#929 finite witness; general theorem not yet mechanized",
    "T-STATE": "#914 finite response-signature reconstruction",
    "T-PRIOR": "NFL/algorithmic-search parents; GMI-specific formulation pending",
}
SOURCE_TYPES = {"P10": "POSITION_PAPER", "P11": "PREPRINT_PRIMARY",
                "P12": "PREPRINT_PRIMARY", "P13": "TUTORIAL_PREPRINT"}
DOCTRINE = "Every row is independent scientific debt until evidence earns it; UNKNOWN/CANNOT_CHECK remain valid."


def validate_structure(bundle, need):
    def fields(value, schema, label):
        need(type(value) is dict and set(value) == set(schema), "EXACT_KEYS:" + label)
        need(all(type(value[k]) is t for k, t in schema.items()), "FIELD_TYPES:" + label)
    for name, schema in TOP.items():
        fields(bundle[name], schema, name)
    need(bundle["ATOMIC_CHECKLIST_V1.json"]["doctrine"] == DOCTRINE, "REGISTERED_DOCTRINE")
    for name, schema in ROWS.items():
        for row in bundle[name]["rows" if "rows" in bundle[name] else "entries"]:
            need(type(row) is dict and type(row.get("id")) is str, "ROW_ID_TYPE:" + name)
            expected = dict(schema)
            optional = EVIDENCE if name == "THEOREM_STATUS_V1.json" else (
                SOURCE_TYPES if name == "PARENT_REGISTRY_V1.json" else {})
            field = "evidence" if name == "THEOREM_STATUS_V1.json" else "source_type"
            if row["id"] in optional:
                expected[field] = str
            fields(row, expected, name + ":" + row["id"])
            if row["id"] in optional:
                need(row[field] == optional[row["id"]], "REGISTERED_AUTHORITY:" + row["id"])
    dag = bundle["THEORY_DAG_V1.json"]
    need(all(type(n) is str for n in dag["nodes"]), "NODE_TYPES")
    need(all(type(k) is str and type(v) is list and all(type(n) is str for n in v)
             for k, v in dag["dependencies"].items()), "DEPENDENCY_TYPES")
    for name, field in (("THEOREM_STATUS_V1.json", "allowed_status"),
                        ("MERGE_GATE_V1.json", "requirements"),
                        ("MERGE_GATE_V1.json", "valid_nonpositive_terminals")):
        need(all(type(v) is str for v in bundle[name][field]), "VOCABULARY_TYPES:" + field)

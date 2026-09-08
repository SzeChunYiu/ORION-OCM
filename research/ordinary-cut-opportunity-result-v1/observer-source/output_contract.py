"""Validate the driver's retained output population, not candidate semantics."""
from pathlib import Path
import hashlib
import json

EMITTED = {"ENUMERATED", "UNKNOWN_INTERFACE", "TRACE_UNUSABLE"}
UNEMITTED = {"NOT_REACHED_RESOURCE", "EXCLUDED_PRIOR_PROTECTED",
             "EXCLUDED_DEPENDS_PRIOR_PROTECTED"}


def identity(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def inspect_outputs(folder, pid, request_pin, request):
    entries = list(folder.iterdir()) if folder.exists() else []
    names = [p.name for p in entries]
    raw = {p.name: p.read_bytes() for p in entries
           if p.is_file() and not p.is_symlink()}
    report = {"files": {n: identity(b) for n, b in raw.items()},
              "entries": names, "population_ok": False,
              "completed_contract": False, "errors": [], "status_counts": {}}
    try:
        if set(raw) != set(names) or "RESULT.json" not in raw:
            raise ValueError("missing result or nonregular output")
        result = json.loads(raw["RESULT.json"])
        report["recorded_terminal"] = result.get("terminal")
        expected = {"RESULT.json"}
        if "P1_contracts" in result:
            expected.add("P1-CONTRACTS.json")
            if result["P1_contracts"] != identity(raw["P1-CONTRACTS.json"]):
                raise ValueError("P1 output identity")
        rows = result["roots"]
        if not isinstance(rows, list) or len(rows) > 128:
            raise ValueError("root records")
        if [row["ordinal"] for row in rows] != list(range(4096, 4096 + len(rows))):
            raise ValueError("root ordinal prefix")
        if any(type(row["ordinal"]) is not int for row in rows):
            raise ValueError("ordinal type")
        labels = [row["label"] for row in rows]
        if any(type(x) is not str or not x for x in labels) or len(set(labels)) != len(labels):
            raise ValueError("root label population")
        for row in rows:
            status = row["status"]
            counts = report["status_counts"]
            counts[status] = counts.get(status, 0) + 1
            if status in EMITTED:
                name = "ROOT-" + str(row["ordinal"]) + ".json"
                expected.add(name)
                if json.loads(raw[name]) != row:
                    raise ValueError("emitted root differs from RESULT")
                if status == "TRACE_UNUSABLE" and row.get("P1_retained") is not True:
                    raise ValueError("unusable whole theorem retention")
            elif status not in UNEMITTED:
                raise ValueError("unregistered root disposition")
        report["expected_files"] = sorted(expected)
        if set(raw) != expected:
            raise ValueError("recorded output population")
        report["population_ok"] = True
        complete = (result["schema"] == "ordinary.training-only-opportunity.v3"
            and result["terminal"] == "TRAINING_ONLY_OPPORTUNITY_RECORDED"
            and len(rows) == 128 and type(result["pid"]) is int and result["pid"] == pid
            and result["request"] == request_pin and result["native_calls"] == 0
            and result.get("new_native_admissions") == 0
            and result.get("training_outcome_is_not_native_admission") is True
            and result.get("qualified_native_trace_authority") == request["qualified_native_trace_authority"]
            and result.get("P1_inventory") == request["P1_inventory"]
            and "P1_contracts" in result
            and all(result.get(k) is True for k in
                    ("inputs_unchanged", "sources_unchanged", "request_unchanged")))
        report["completed_contract"] = complete
    except (OSError, ValueError, KeyError, TypeError) as error:
        report["errors"].append(type(error).__name__ + ": " + str(error))
    return report

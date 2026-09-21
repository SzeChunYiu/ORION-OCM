"""Re-earn only R1 at its exact registered scope; all original atoms remain unchanged."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / "research/gmi-1068-recursive-audit-v28/SCOPE_SNAPSHOT_V28.json"
BASE_SHA = "72d1dd18bc4ce99d6bcd288722c58459e38b7ac8c2cae4292414cbe29322c4cb"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTRACT = load("audit_contract_v29", HERE / "audit_contract_v29.py")
CLOSING = set(CONTRACT.ATOM_SPECS)


def evaluate(current=None, receipt=None, accounting=None):
    """Optional in-memory inputs support hostile tests; source custody is mandatory."""
    gate = load("gate", ROOT / "research/gmi-1068-recursive-audit-v3/gate.py")
    need, exact = CONTRACT.need, CONTRACT.exact
    need(hashlib.sha256(BASE.read_bytes()).hexdigest() == BASE_SHA, "V28 baseline drift")
    before = json.loads(BASE.read_text())
    if current is None:
        current = json.loads((HERE / "SCOPE_SNAPSHOT_V29.json").read_text())
    if receipt is None:
        receipt = json.loads((ROOT / CONTRACT.PACKAGE / "RESULT_V29.json").read_text())
    need(type(current) is dict and set(current) == set(before), "snapshot top-level fields")
    for field in before:
        if field != "rounds":
            expected = "2405c7bd06f9236b545ce501e5b9f9b5f24fd5e5" if field in ("observed_main", "audited_base") else before[field]
            exact(current[field], expected, "snapshot provenance drift:" + field)
    artifacts = CONTRACT.validate_receipt(ROOT, receipt)
    gate.validate(before, ROOT)
    result = gate.validate(current, ROOT)
    additions, closed = set(), set()
    for name in gate.NODES:
        old, new = before["rounds"][name], current["rounds"][name]
        need(type(new) is dict and set(new) == set(old), "round field inventory drift:" + name)
        for field in ("scope", "historical_reconciliation_status", "status"):
            expected = (CONTRACT.SPECS.ROUND_SCOPE if field == "scope" else "EARNED") if (
                name == "R1" and field in {"scope", "status"}) else old[field]
            exact(new[field], expected, "original round scope/status drift:" + name)
        if name in CONTRACT.REPAIR_SCOPES:
            exact(new["artifacts"], old["artifacts"] + artifacts, "new artifact set drift:" + name)
            exact(new["local_repairs"], old["local_repairs"] + [CONTRACT.repair(ROOT, name)],
                  "registered repair drift:" + name)
            additions.update(artifact["path"] for artifact in artifacts)
        else:
            exact(new["artifacts"], old["artifacts"], "unregistered artifacts:" + name)
            exact(new["local_repairs"], old["local_repairs"], "unregistered repair:" + name)
        exact(new["obligations"], old["obligations"], "original atom records drift:" + name)
    need(CLOSING == set(), "no original atomic closure permitted")
    need(result["registered_atoms"] == 222 and result["unresolved_atoms"] == 187,
         "original coverage mismatch")
    need(result["earned_rounds"] == ["R0", "R1"], "unsupported whole-round closure")
    gate.validate_baseline(current, before, sorted(additions))
    scientific = [atom["id"] for name in gate.NODES if name != "R0"
                  for atom in current["rounds"][name]["obligations"] if atom["status"] == "CLOSED"]
    need(len(scientific) == 27, "scientific closure count drift")
    expected_accounting = CONTRACT.current_accounting(current, receipt["amendment_carry"])
    if accounting is None:
        accounting = json.loads((HERE / "CURRENT_ACCOUNTING_V29.json").read_text())
    exact(accounting, expected_accounting, "current accounting drift")
    for key, value in {"original_total": 222, "original_fulfilled": 35, "original_unresolved": 187,
                       "qualified_replacements": 2, "active_unresolved": 185}.items():
        exact(accounting[key], value, "current count drift:" + key)
    return {"status": "PASS", "registered_atoms": 222, "governance_atoms_closed": 8,
            "scientific_atoms_closed": sorted(scientific), "new_scientific_atoms_closed": sorted(closed),
            "remaining_atoms": accounting["original_unresolved"], "original_fulfilled": accounting["original_fulfilled"],
            "qualified_replacements": accounting["qualified_replacements"], "active_unresolved": accounting["active_unresolved"],
            "earned_rounds": ["R0", "R1"], "overall_closure": "OPEN",
            "scientific_truth_certified": False}


if __name__ == "__main__":
    try:
        print(json.dumps(evaluate(), sort_keys=True))
    except OSError as exc:
        print("CANNOT_CHECK:" + str(exc), file=sys.stderr)
        sys.exit(2)
    except (ValueError, KeyError, TypeError) as exc:
        print("CHECKED_INVALID:" + str(exc), file=sys.stderr)
        sys.exit(1)

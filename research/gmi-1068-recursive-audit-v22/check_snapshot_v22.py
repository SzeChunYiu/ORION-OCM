"""Close only the registered R3-007 barrier atom; preserve every other original record; enforce complete adjudication records."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / "research/gmi-1068-recursive-audit-v21/SCOPE_SNAPSHOT_V21.json"
BASE_SHA = "2ae7e752d97a411a5bbad8cda89c169dfdd109cca99a3f23d48f2b0ab29a068a"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTRACT = load("audit_contract_v22", HERE / "audit_contract_v22.py")
CLOSING = set(CONTRACT.ATOM_SPECS)


def evaluate(current=None, receipt=None, accounting=None):
    """Optional in-memory inputs support hostile tests; source custody is mandatory."""
    gate = load("gate", ROOT / "research/gmi-1068-recursive-audit-v3/gate.py")
    need, exact = CONTRACT.need, CONTRACT.exact
    need(hashlib.sha256(BASE.read_bytes()).hexdigest() == BASE_SHA, "V21 baseline drift")
    before = json.loads(BASE.read_text())
    if current is None:
        current = json.loads((HERE / "SCOPE_SNAPSHOT_V22.json").read_text())
    if receipt is None:
        receipt = json.loads((ROOT / CONTRACT.PACKAGE / "RESULT_V22.json").read_text())
    need(type(current) is dict and set(current) == set(before), "snapshot top-level fields")
    for field in before:
        if field != "rounds":
            expected = "120ced06e21bcc590db4c7033d4313c5a099b943" if field in ("observed_main", "audited_base") else before[field]
            exact(current[field], expected, "snapshot provenance drift:" + field)
    artifacts = CONTRACT.validate_receipt(ROOT, receipt)
    gate.validate(before, ROOT)
    result = gate.validate(current, ROOT)
    additions, closed = set(), set()
    for name in gate.NODES:
        old, new = before["rounds"][name], current["rounds"][name]
        for field in ("scope", "historical_reconciliation_status", "status"):
            exact(new[field], old[field], "original round scope/status drift:" + name)
        if name in CONTRACT.REPAIR_SCOPES:
            exact(new["artifacts"], old["artifacts"] + artifacts, "new artifact set drift:" + name)
            exact(new["local_repairs"], old["local_repairs"] + [CONTRACT.repair(ROOT, name)],
                  "registered repair drift:" + name)
            additions.update(artifact["path"] for artifact in artifacts)
        else:
            exact(new["artifacts"], old["artifacts"], "unregistered artifacts:" + name)
            exact(new["local_repairs"], old["local_repairs"], "unregistered repair:" + name)
        need(len(new["obligations"]) == len(old["obligations"]), "original count drift")
        for original, actual in zip(old["obligations"], new["obligations"]):
            atom = original["id"]
            expected = dict(original)
            if atom in CLOSING:
                title, scope = CONTRACT.ATOM_SPECS[atom]
                need(original["status"] == "UNKNOWN" and original["title"] == title,
                     "original closure identity drift")
                expected.update(status="CLOSED", disposition=scope, evidence=CONTRACT.atom_evidence(ROOT, atom))
                closed.add(atom)
            exact(actual, expected, "original atom adjudication drift:" + atom)
    need(closed == CLOSING, "closure set mismatch")
    need(result["registered_atoms"] == 222 and result["unresolved_atoms"] == 194,
         "original coverage mismatch")
    need(result["earned_rounds"] == ["R0"], "unsupported whole-round closure")
    gate.validate_baseline(current, before, sorted(additions))
    scientific = [atom["id"] for name in gate.NODES if name != "R0"
                  for atom in current["rounds"][name]["obligations"] if atom["status"] == "CLOSED"]
    need(len(scientific) == 20, "scientific closure count drift")
    expected_accounting = CONTRACT.current_accounting(current, receipt["amendment_carry"])
    if accounting is None:
        accounting = json.loads((HERE / "CURRENT_ACCOUNTING_V22.json").read_text())
    exact(accounting, expected_accounting, "current accounting drift")
    for key, value in {"original_total": 222, "original_fulfilled": 28, "original_unresolved": 194,
                       "qualified_replacements": 2, "active_unresolved": 192}.items():
        exact(accounting[key], value, "current count drift:" + key)
    return {"status": "PASS", "registered_atoms": 222, "governance_atoms_closed": 8,
            "scientific_atoms_closed": sorted(scientific), "new_scientific_atoms_closed": sorted(closed),
            "remaining_atoms": accounting["original_unresolved"], "original_fulfilled": accounting["original_fulfilled"],
            "qualified_replacements": accounting["qualified_replacements"], "active_unresolved": accounting["active_unresolved"],
            "earned_rounds": ["R0"], "overall_closure": "OPEN",
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

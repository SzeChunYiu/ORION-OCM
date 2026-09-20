"""Integrated R1 round contract preserving all original atoms and source custody."""
import hashlib
import importlib.util
import json
from pathlib import Path
QUALIFIED = ["GMI2-R2-003@r1", "GMI2-R2-007@r1"]

def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    if type(value) is dict:
        need(all(type(key) is str for key in value), "non-string JSON key")
        for item in value.values():
            canonical(item)
    elif type(value) is list:
        for item in value:
            canonical(item)
    else:
        need(type(value) in (str, int, bool, type(None)), "noncanonical JSON value")
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def exact(actual, expected, message):
    need(canonical(actual) == canonical(expected), message)


def load(path):
    spec = importlib.util.spec_from_file_location("v29_contract_" + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SPECS = load(Path(__file__).with_name("audit_specs_v29.py"))
PINS = load(Path(__file__).with_name("audit_pins_v29.py"))
PACKAGE, RESULTS, BOUNDARIES, REPAIR_SCOPES = (
    SPECS.PACKAGE, SPECS.RESULTS, SPECS.BOUNDARIES, SPECS.REPAIR_SCOPES)
ATOM_SPECS = {}
COSTS = load(Path(__file__).with_name("audit_costs_v29.py"))
SOURCE_PATHS, SOURCE_NAMES = PINS.SOURCE_PATHS, PINS.SOURCE_NAMES
SOURCE_HASHES = PINS.SOURCE_HASHES
PROOF_CONTRACT_SHA, PROOF_AUDIT_SHA, PROOF_COUNT = PINS.PROOF_CONTRACT_SHA, PINS.PROOF_AUDIT_SHA, PINS.PROOF_COUNT
REVIEWED_INPUTS, SOURCE_ASSUMPTIONS = PINS.REVIEWED_INPUTS, PINS.SOURCE_ASSUMPTIONS


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_artifacts(root):
    return [{"path": str(path.relative_to(root)), "sha256": digest(path)}
            for path in sorted((root / PACKAGE).iterdir())
            if path.is_file() and path.suffix in {".py", ".md", ".lean", ".json"}]


def witness(root, name, kind, locator):
    path = name if name.startswith("research/") else PACKAGE + "/" + name
    return {"path": path, "sha256": digest(root / path), "kind": kind, "locator": locator}


def round_evidence(root):
    if not PINS.FINAL:
        raise OSError("final reviewed V29 proof pins unavailable")
    return [witness(root, "RESULT_V29.json", "json_pointer", "/round_adjudication/R1"),
            witness(root, "ORIGINAL_CROSSWALK_V29.json", "json_pointer", "/required_results"),
            witness(root, "oracle_v29.py", "python_symbol", "certify")] + [
        witness(root, name, "lean_declaration", symbol.rsplit(".", 1)[-1])
        for name, symbol in PINS.ROUND_DECLARATIONS]


def repair(root, name):
    if not PINS.FINAL:
        raise OSError("final reviewed V29 proof pins unavailable")
    evidence = [witness(root, "check_integration_v29.py", "python_symbol", "evaluate"),
                witness(root, "RESULT_V29.json", "json_pointer", "/kernel" if name == "R14" else "/coverage")]
    extras = {"R1": PINS.REPAIR_DECLARATION,
              "R14": ("proof_contract_v29.py", "python_symbol", "audit_source"),
              "R15": ("oracle_v29.py", "python_symbol", "certify")}
    file, kind, locator = extras[name]
    if kind == "lean_declaration":
        locator = locator.rsplit(".", 1)[-1]
    evidence.insert(0, witness(root, file, kind, locator))
    if name == "R1":
        evidence.extend(round_evidence(root))
    return {"id": name + "-integration-v29", "scope": REPAIR_SCOPES[name],
            "status": "LOCAL_VERIFIED", "evidence": evidence}


def validate_receipt(root, receipt):
    if not PINS.FINAL:
        raise OSError("final reviewed V29 proof pins unavailable")
    need(type(receipt) is dict and set(receipt) == {
        "schema", "tests_run", "kernel", "coverage", "source_bindings", "round_adjudication", "inputs",
        "inherited_receipts", "amendment_carry", "registered_results", "overall_closure", "scientific_truth_certified",
        "claim_boundaries", "rollup_reconciliation", "codec_costs", "source_costs"}, "receipt fields")
    fixed = {"schema": "GMI_1068_R1_INTEGRATED_CORE_V29", "tests_run": 13,
             "overall_closure": "OPEN", "scientific_truth_certified": False, "claim_boundaries": BOUNDARIES,
             "rollup_reconciliation": SPECS.ROLLUP}
    for key, value in fixed.items():
        exact(receipt[key], value, "receipt field drift:" + key)
    exact(receipt["round_adjudication"], {"R1": {"status": "VERIFIED_AT_REGISTERED_SCOPE",
          "scope": SPECS.ROUND_SCOPE}}, "registered round adjudication drift")
    exact(receipt["codec_costs"], COSTS.codec_costs(), "registered codec costs drift")
    exact(receipt["source_costs"], COSTS.source_costs(root), "registered source costs drift")
    results = {key: {"status": "VERIFIED_AT_REGISTERED_SCOPE", "scope": scope}
               for key, scope in RESULTS.items()}
    exact(receipt["registered_results"], results, "registered result adjudication drift")
    artifacts = package_artifacts(root)
    inputs = {entry["path"].rsplit("/", 1)[-1]: entry["sha256"] for entry in artifacts
              if entry["path"].rsplit("/", 1)[-1] not in {"RESULT_V29.json", "RUN_TIMINGS_V29.json"}}
    exact(receipt["inputs"], inputs, "package input custody drift")
    package = root / PACKAGE
    for name, expected in REVIEWED_INPUTS.items():
        need(digest(package / name) == expected, "reviewed evaluator/input drift:" + name)
    exact(load(package / "audit_rollup_v29.py").verify(root), SPECS.ROLLUP, "original witness reconciliation drift")
    custody = load(package / "custody_v29.py")
    try:
        expected_custody = custody.verify(root)
    except custody.CannotCheck as exc:
        raise OSError(str(exc)) from exc
    for key, value in expected_custody.items():
        exact(receipt[key], value, "inherited custody drift:" + key)
    exact(receipt["coverage"], load(package / "coverage_v29.py").REQUIRED, "coverage receipt drift")
    need(digest(package / "proof_contract_v29.py") == PROOF_CONTRACT_SHA, "reviewed proof-type drift")
    proof = load(package / "proof_contract_v29.py")
    need(proof.SOURCE_NAMES == SOURCE_NAMES and proof.SOURCE_PATHS == SOURCE_PATHS
         and len(proof.ENTRIES) == PROOF_COUNT, "registered proof inventory drift")
    need(hashlib.sha256(proof.audit_source().encode()).hexdigest() == PROOF_AUDIT_SHA, "proof audit drift")
    for path, expected in SOURCE_HASHES.items():
        need(digest(root / path) == expected, "reviewed formal source drift:" + path)
    expected_kernel = {"status": "PASS", "lean_version": "4.19.0", "proof_entry_count": PROOF_COUNT,
        "audit_sha256": PROOF_AUDIT_SHA,
        "sources": SOURCE_HASHES,
        "source_assumptions": SOURCE_ASSUMPTIONS}
    exact(receipt["kernel"], expected_kernel, "kernel receipt drift")
    return artifacts


def current_accounting(snapshot, amendment_carry):
    records = [atom for row in snapshot["rounds"].values() for atom in row["obligations"]]
    atoms = {atom["id"]: atom for atom in records}
    need(len(atoms) == len(records), "duplicate original atoms")
    exact(amendment_carry["qualified_revision_ids"], QUALIFIED, "qualified reading drift")
    originals = [revision.split("@")[0] for revision in QUALIFIED]
    need(all(atoms[atom]["status"] == "UNKNOWN" for atom in originals), "qualified original promoted")
    fulfilled = sum(atom["status"] == "CLOSED" for atom in records)
    unresolved = len(records) - fulfilled
    snapshot_sha = hashlib.sha256(json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"schema": "GMI_1068_CURRENT_ACCOUNTING_V29", "snapshot_content_sha256": snapshot_sha,
            "original_total": len(records), "original_fulfilled": fulfilled, "original_unresolved": unresolved,
            "qualified_replacements": len(originals), "qualified_original_ids": originals,
            "active_unresolved": unresolved - len(originals), "amendment_carry": amendment_carry,
            "overall_closure": "OPEN", "scientific_truth_certified": False}

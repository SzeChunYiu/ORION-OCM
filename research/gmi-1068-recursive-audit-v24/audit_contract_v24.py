"""Fixed legacy-transport closure contract and inherited source custody."""
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
    spec = importlib.util.spec_from_file_location("v24_contract_" + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SPECS = load(Path(__file__).with_name("audit_specs_v24.py"))
PINS = load(Path(__file__).with_name("audit_pins_v24.py"))
PACKAGE, ATOM_SPECS, RESULTS, BOUNDARIES, REPAIR_SCOPES = (
    SPECS.PACKAGE, SPECS.ATOM_SPECS, SPECS.RESULTS, SPECS.BOUNDARIES, SPECS.REPAIR_SCOPES)
SOURCE_PATHS, SOURCE_NAMES = PINS.SOURCE_PATHS, PINS.SOURCE_NAMES
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


def atom_evidence(root, atom):
    need(atom in ATOM_SPECS, "unregistered original closure")
    if not PINS.FINAL:
        raise OSError("final reviewed V24 proof pins unavailable")
    return [witness(root, "RESULT_V24.json", "json_pointer", "/atoms/" + atom),
            witness(root, "oracle_v24.py", "python_symbol", "verify_context")] + [
        witness(root, name, "lean_declaration", symbol) for name, symbol in PINS.ATOM_DECLARATIONS]



def repair(root, name):
    evidence = [witness(root, "check_transports_v24.py", "python_symbol", "evaluate"),
                witness(root, "RESULT_V24.json", "json_pointer", "/kernel" if name == "R14" else "/coverage")]
    extras = {"R3": PINS.REPAIR_DECLARATION,
              "R14": ("proof_contract_v24.py", "python_symbol", "audit_source"),
              "R15": ("oracle_v24.py", "python_symbol", "verify_context")}
    evidence.insert(0, witness(root, *extras[name]))
    return {"id": name + "-legacy-v24", "scope": REPAIR_SCOPES[name],
            "status": "LOCAL_VERIFIED", "evidence": evidence}


def validate_receipt(root, receipt):
    if not PINS.FINAL:
        raise OSError("final reviewed V24 proof pins unavailable")
    need(type(receipt) is dict and set(receipt) == {
        "schema", "tests_run", "kernel", "coverage", "source_bindings", "atoms", "inputs",
        "inherited_receipts", "amendment_carry", "registered_results", "overall_closure", "scientific_truth_certified",
        "claim_boundaries"}, "receipt fields")
    fixed = {"schema": "GMI_1068_LEGACY_TRANSPORTS_V24", "tests_run": 14,
             "overall_closure": "OPEN", "scientific_truth_certified": False, "claim_boundaries": BOUNDARIES}
    for key, value in fixed.items():
        exact(receipt[key], value, "receipt field drift:" + key)
    atoms = {key: {"title": title, "scope": scope, "status": "VERIFIED_AT_REGISTERED_SCOPE"}
             for key, (title, scope) in ATOM_SPECS.items()}
    exact(receipt["atoms"], atoms, "registered atom adjudication drift")
    results = {key: {"status": "VERIFIED_AT_REGISTERED_SCOPE", "scope": scope}
               for key, scope in RESULTS.items()}
    exact(receipt["registered_results"], results, "registered result adjudication drift")
    artifacts = package_artifacts(root)
    inputs = {entry["path"].rsplit("/", 1)[-1]: entry["sha256"] for entry in artifacts
              if not entry["path"].endswith("/RESULT_V24.json")}
    exact(receipt["inputs"], inputs, "package input custody drift")
    package = root / PACKAGE
    for name, expected in REVIEWED_INPUTS.items():
        need(digest(package / name) == expected, "reviewed evaluator/input drift:" + name)
    custody = load(package / "custody_v24.py")
    try:
        expected_custody = custody.verify(root)
    except custody.CannotCheck as exc:
        raise OSError(str(exc)) from exc
    for key, value in expected_custody.items():
        exact(receipt[key], value, "inherited custody drift:" + key)
    exact(receipt["coverage"], load(package / "coverage_v24.py").REQUIRED, "coverage receipt drift")
    need(digest(package / "proof_contract_v24.py") == PROOF_CONTRACT_SHA, "reviewed proof-type drift")
    proof = load(package / "proof_contract_v24.py")
    need(proof.SOURCE_NAMES == SOURCE_NAMES and proof.SOURCE_PATHS == SOURCE_PATHS
         and len(proof.ENTRIES) == PROOF_COUNT, "registered proof inventory drift")
    need(hashlib.sha256(proof.audit_source().encode()).hexdigest() == PROOF_AUDIT_SHA, "proof audit drift")
    expected_kernel = {"status": "PASS", "lean_version": "4.19.0", "proof_entry_count": PROOF_COUNT,
        "audit_sha256": PROOF_AUDIT_SHA,
        "sources": {path: digest(root / path) for path in SOURCE_PATHS},
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
    return {"schema": "GMI_1068_CURRENT_ACCOUNTING_V24", "snapshot_content_sha256": snapshot_sha,
            "original_total": len(records), "original_fulfilled": fulfilled, "original_unresolved": unresolved,
            "qualified_replacements": len(originals), "qualified_original_ids": originals,
            "active_unresolved": unresolved - len(originals), "amendment_carry": amendment_carry,
            "overall_closure": "OPEN", "scientific_truth_certified": False}

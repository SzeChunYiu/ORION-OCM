"""Reviewed exact optional-structure adjudications and source custody."""
import hashlib
import importlib.util
import json

PACKAGE = "research/gmi-1068-optional-structure-v13"
ATOM_SPECS = {
    "GMI2-R1-004": ("adjudicate parallel composition", "The unchanged lawful reset-process category admits no monoidal structure; weak-unit necessary conditions and the concrete obstruction are kernel checked, with extraction from the standard full definition proved on paper."),
    "GMI2-R1-005": ("test symmetry necessity", "Registered lawful monoidal models, including nonidentity C2 loops, admit no braiding for their specified tensor; this does not exclude alternative tensors on the underlying category."),
    "GMI2-R1-010": ("mechanize universal process claims", "Fresh V11 kernel replay establishes the original R1 freeze result7: constructed universal category-law consequences and general quotient presentation; this does not mechanize all minimality or physical-adequacy claims."),
}
REPAIR_SCOPES = {
    "R1": "Unchanged reset-process category has no monoidal tensor; specified lawful monoidal models have no braiding. Fresh V11 proof replay supplies the original universal category-law component. Only parallel composition, symmetry necessity and that formal-law atom close; other process obligations remain open.",
    "R14": "Thirty-seven registered new statement types and fourteen inherited V11 types are freshly checked by Lean 4.19.0. General interchange, actual finite obstructions and typed loop coherence are kernel checked; extraction from the full monoidal definition and bundled packaging remain paper-level.",
    "R15": "Independent actual bit-function composition, exhaustive tensor candidates and failed equations, typed monoidal laws, weak-unit naturality, no-alarm C2 models and hostile evidence controls. Exact coverage and source-bound three-atom adjudication prevent broader promotion.",
}
BOUNDARIES = [
    "three original scientific requirements only; R1 remains open",
    "general monoidal extraction and bundled packaging remain paper-level",
    "no tensor on unchanged reset category; enlarging the category changes the claim",
    "no braiding for the registered tensor; alternative tensors are not excluded",
    "R1-010 covers original freeze result7 category laws, not every process assertion",
    "207 remaining original requirements retain their unresolved statuses",
    "no absolute minimality, architecture recovery or empirical novelty",
]
INHERITED_RECEIPT = "research/gmi-1068-typed-foundation-v11/RESULT_V11.json"
SOURCE_BINDINGS = {
    "research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json": "4cc262d491fbcdccf2b4c8656e80dcdb06e1795344500e46ac980ca09a679574",
    "research/gmi-1068-r1-minimal-process-core-v1/FREEZE_V1.md": "5f755106e6e5e2fcda6257d71e6eda6f2d895adf817834b2f2464685a491558a",
    "research/gmi-1068-recursive-audit-v12/SCOPE_SNAPSHOT_V12.json": "1b6eed814493b0dfc8914bdb102e1f4c4494cff34db16ba7b991adcfa636846f",
    INHERITED_RECEIPT: "598a325e75a7005ca906dd0d21f2feea1aab9de561b0a83219b475f944c59d65",
}
SOURCE_NAMES = ("InterchangeV13.lean", "DiscreteMonoidalV13.lean", "LoopMonoidalV13.lean")
PROOF_CONTRACT_SHA = "cfa7071c182881edf5a34ee7fbf04a5fbfe35111d6c8ea85c78a0834b0e37b79"
PROOF_AUDIT_SHA = "c55f5303e9eac6b9583360f31c423d37b114cf3e62f434ef2411276e1f699db2"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def exact(actual, expected, message):
    need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), message)


def load(path):
    spec = importlib.util.spec_from_file_location("v13_contract_" + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_artifacts(root):
    return [{"path": str(path.relative_to(root)), "sha256": digest(path)}
            for path in sorted((root / PACKAGE).iterdir())
            if path.is_file() and path.suffix in {".py", ".md", ".lean", ".json"}]


def witness(root, name, kind, locator):
    path = PACKAGE + "/" + name
    return {"path": path, "sha256": digest(root / path), "kind": kind, "locator": locator}


def atom_evidence(root, atom):
    need(atom in ATOM_SPECS, "unregistered atom")
    evidence = [witness(root, "RESULT_V13.json", "json_pointer", "/atoms/" + atom)]
    if atom == "GMI2-R1-010":
        return evidence + [witness(root, "RESULT_V13.json", "json_pointer", "/inherited_kernel"),
                           witness(root, "inherited_kernel_v13.py", "python_symbol", "evaluate")]
    declarations = {"GMI2-R1-004": (("InterchangeV13.lean", "no_any_tensor"), ("InterchangeV13.lean", "tensor_units_derived")),
                    "GMI2-R1-005": (("DiscreteMonoidalV13.lean", "no_discrete_braiding"), ("LoopMonoidalV13.lean", "no_braiding"))}
    return evidence + [witness(root, name, "lean_declaration", declaration)
                       for name, declaration in declarations[atom]]


def repair(root, name):
    evidence = [witness(root, "check_optional_v13.py", "python_symbol", "evaluate"),
                witness(root, "RESULT_V13.json", "json_pointer", "/kernel" if name == "R14" else "/coverage")]
    extras = {"R1": ("InterchangeV13.lean", "lean_declaration", "no_any_tensor"),
              "R14": ("proof_contract_v13.py", "python_symbol", "audit_source"),
              "R15": ("independent_oracle_v13.py", "python_symbol", "verify_obstruction")}
    evidence.insert(0, witness(root, *extras[name]))
    if name in ("R1", "R14"):
        evidence.append(witness(root, "inherited_kernel_v13.py", "python_symbol", "evaluate"))
    return {"id": name + "-optional-v13", "scope": REPAIR_SCOPES[name],
            "status": "LOCAL_VERIFIED", "evidence": evidence}


def validate_receipt(root, receipt):
    need(type(receipt) is dict and set(receipt) == {
        "schema", "tests_run", "kernel", "inherited_kernel", "coverage", "source_bindings", "atoms", "inputs",
        "overall_closure", "scientific_truth_certified", "claim_boundaries"}, "receipt fields")
    fixed = {"schema": "GMI_1068_OPTIONAL_STRUCTURE_V13", "tests_run": 9,
             "overall_closure": "OPEN", "scientific_truth_certified": False, "claim_boundaries": BOUNDARIES}
    for key, value in fixed.items():
        exact(receipt[key], value, "receipt field drift:" + key)
    atoms = {key: {"title": title, "scope": scope, "status": "VERIFIED_AT_REGISTERED_SCOPE"}
             for key, (title, scope) in ATOM_SPECS.items()}
    exact(receipt["atoms"], atoms, "registered atom adjudication drift")
    artifacts = package_artifacts(root)
    inputs = {entry["path"].rsplit("/", 1)[-1]: entry["sha256"] for entry in artifacts
              if not entry["path"].endswith("/RESULT_V13.json")}
    exact(receipt["inputs"], inputs, "package input custody drift")
    exact(receipt["source_bindings"], SOURCE_BINDINGS, "historical source receipt drift")
    for path, expected in SOURCE_BINDINGS.items():
        need(digest(root / path) == expected, "historical source drift:" + path)
    package = root / PACKAGE
    exact(receipt["coverage"], load(package / "coverage_v13.py").REQUIRED, "coverage receipt drift")
    need(digest(package / "proof_contract_v13.py") == PROOF_CONTRACT_SHA, "reviewed proof-type drift")
    proof = load(package / "proof_contract_v13.py")
    need(proof.SOURCE_NAMES == SOURCE_NAMES and len(proof.ENTRIES) == 37, "registered proof inventory drift")
    need(hashlib.sha256(proof.audit_source().encode()).hexdigest() == PROOF_AUDIT_SHA, "proof audit drift")
    expected_kernel = {"status": "PASS", "lean_version": "4.19.0", "proof_entry_count": 37,
        "audit_sha256": PROOF_AUDIT_SHA,
        "sources": {PACKAGE + "/" + name: digest(package / name) for name in SOURCE_NAMES},
        "source_assumptions": "generic monoid/interchange laws and actual finite models; full monoidal extraction paper-only"}
    exact(receipt["kernel"], expected_kernel, "kernel receipt drift")
    inherited = json.loads((root / INHERITED_RECEIPT).read_text())
    exact(receipt["inherited_kernel"], inherited["kernel"], "inherited kernel receipt drift")
    need(inherited["kernel"]["proof_entry_count"] == 14, "inherited proof inventory drift")
    for path, expected in inherited["kernel"]["sources"].items():
        need(digest(root / path) == expected, "inherited proof source drift:" + path)
    for name in ("proof_contract_v11.py", "check_lean_v11.py"):
        need(digest((root / INHERITED_RECEIPT).parent / name) == inherited["inputs"][name], "inherited checker drift")
    return artifacts

"""Reviewed exact partial-context adjudications and source custody."""
import hashlib
import importlib.util
import json

PACKAGE = "research/gmi-1068-partial-context-v15"
ATOM_SPECS = {
    "GMI2-R2-001": ("formalize context/preorder", "Partial evaluation on admitted histories is constructed by restricting an ambient evaluator to the admission/evaluation intersection. Its pullback comparison is a preorder on that defined domain, and mutual comparison yields a partial-order quotient."),
    "GMI2-R2-004": ("generalize AJ7 countermodel", "For two distinct admitted/evaluated histories, a strict result pair and a permitted evaluator class containing the constructed separating functions, the same full process admits opposite rankings. Actual ordering functions differ, so the V9 collision theorem rules out recovery from that full process."),
}
REPAIR_SCOPES = {
    "R2": "Admission and evaluator definedness are separated, and their intersection carries the induced preorder and partial-order quotient. Permitted separating evaluators on a fixed admitted domain give opposite rankings with the complete process unchanged. Only context/preorder and general AJ7 separation close; reverse-admission recovery and remaining requirements stay open.",
    "R14": "Lean 4.19.0 checks explicit partial-domain observation laws, preorder antisymmetrization, actual separating functions and ordering-map nonrecovery. The unchanged V9 source is freshly replayed and its generic collision and fiber-criterion types are registered alongside the new proofs.",
    "R15": "Independent enumeration checks all registered preorders, partial contexts, representative and quotient equations, exact separating-function formulas and a full lawful C3 process witness. Failed hypotheses, illegal ambient evaluations, weakened diagnostics and evidence mutations prevent broader closure.",
}
BOUNDARIES = [
    "two original scientific requirements only; R2 remains open",
    "admission and defined evaluation remain distinct",
    "the induced preorder is on the admitted evaluated domain only",
    "contextual comparison equivalence is not behavioral equivalence",
    "reversal requires a strict result pair and both permitted separating evaluators",
    "the same full process is preserved; semantic nonrecovery is not statistical independence",
    "204 original requirements retain their unresolved statuses",
    "no reverse-admission recovery closure, universal value rule or empirical novelty",
]
V9_SOURCE = "research/gmi-1068-r0-foundation-repair-v9/RecoverabilityV9.lean"
SOURCE_BINDINGS = {
    "research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json": "4cc262d491fbcdccf2b4c8656e80dcdb06e1795344500e46ac980ca09a679574",
    "research/gmi-1068-r2-context-irreducibility-v1/FREEZE_V1.md": "cd3754eb383e2796c3fe06dc7e9fbb7cf17d9d0bca35bea983e43fbc6b6ae320",
    "research/gmi-1068-recursive-audit-v14/SCOPE_SNAPSHOT_V14.json": "f692d247f459ccd0d4b51b542f856450d043203c078cd7922e1539335776c7af",
    V9_SOURCE: "164768fbda9a973001312c04e8ad07626de64b3fa0ec44fbd45391d7a0a704bd",
}
SOURCE_NAMES = ("RecoverabilityV9.lean", "PartialContextV15.lean", "QuotientOrderV15.lean", "SeparationV15.lean")
SOURCE_PATHS = (V9_SOURCE,) + tuple(PACKAGE + "/" + name for name in SOURCE_NAMES[1:])
PROOF_CONTRACT_SHA = "1b0e89666e9871cf1bd3382244bcdc24e3eb75481eeaa99e7ac47116d5d045c3"
PROOF_AUDIT_SHA = "f00d0ce7682107423295dea0364591b4919d48b2c2bf2d9321da3ca73c3f2380"
PROOF_COUNT = 28


def need(condition, message):
    if not condition:
        raise ValueError(message)


def exact(actual, expected, message):
    need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), message)


def load(path):
    spec = importlib.util.spec_from_file_location("v15_contract_" + path.stem, path)
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
    path = name if name == V9_SOURCE else PACKAGE + "/" + name
    return {"path": path, "sha256": digest(root / path), "kind": kind, "locator": locator}


def atom_evidence(root, atom):
    need(atom in ATOM_SPECS, "unregistered atom")
    declarations = {
        "GMI2-R2-001": (("PartialContextV15.lean", "observe_has_value"),
                         ("QuotientOrderV15.lean", "context_quotient_comparison"),
                         ("QuotientOrderV15.lean", "quotient_antisymm")),
        "GMI2-R2-004": (("SeparationV15.lean", "admitted_nonrecovery"),
                         ("SeparationV15.lean", "orders_different"),
                         (V9_SOURCE, "no_recovery_of_collision")),
    }
    return [witness(root, "RESULT_V15.json", "json_pointer", "/atoms/" + atom)] + [
        witness(root, name, "lean_declaration", declaration) for name, declaration in declarations[atom]]


def repair(root, name):
    evidence = [witness(root, "check_context_v15.py", "python_symbol", "evaluate"),
                witness(root, "RESULT_V15.json", "json_pointer", "/kernel" if name == "R14" else "/coverage")]
    extras = {"R2": ("SeparationV15.lean", "lean_declaration", "admitted_nonrecovery"),
              "R14": ("proof_contract_v15.py", "python_symbol", "audit_source"),
              "R15": ("independent_oracle_v15.py", "python_symbol", "quotient")}
    evidence.insert(0, witness(root, *extras[name]))
    return {"id": name + "-context-v15", "scope": REPAIR_SCOPES[name],
            "status": "LOCAL_VERIFIED", "evidence": evidence}


def validate_receipt(root, receipt):
    need(type(receipt) is dict and set(receipt) == {
        "schema", "tests_run", "kernel", "coverage", "source_bindings", "atoms", "inputs",
        "overall_closure", "scientific_truth_certified", "claim_boundaries"}, "receipt fields")
    fixed = {"schema": "GMI_1068_PARTIAL_CONTEXT_V15", "tests_run": 9,
             "overall_closure": "OPEN", "scientific_truth_certified": False, "claim_boundaries": BOUNDARIES}
    for key, value in fixed.items():
        exact(receipt[key], value, "receipt field drift:" + key)
    atoms = {key: {"title": title, "scope": scope, "status": "VERIFIED_AT_REGISTERED_SCOPE"}
             for key, (title, scope) in ATOM_SPECS.items()}
    exact(receipt["atoms"], atoms, "registered atom adjudication drift")
    artifacts = package_artifacts(root)
    inputs = {entry["path"].rsplit("/", 1)[-1]: entry["sha256"] for entry in artifacts
              if not entry["path"].endswith("/RESULT_V15.json")}
    exact(receipt["inputs"], inputs, "package input custody drift")
    exact(receipt["source_bindings"], SOURCE_BINDINGS, "historical source receipt drift")
    for path, expected in SOURCE_BINDINGS.items():
        need(digest(root / path) == expected, "historical source drift:" + path)
    package = root / PACKAGE
    exact(receipt["coverage"], load(package / "coverage_v15.py").REQUIRED, "coverage receipt drift")
    need(digest(package / "proof_contract_v15.py") == PROOF_CONTRACT_SHA, "reviewed proof-type drift")
    proof = load(package / "proof_contract_v15.py")
    need(proof.SOURCE_NAMES == SOURCE_NAMES and proof.SOURCE_PATHS == SOURCE_PATHS
         and len(proof.ENTRIES) == PROOF_COUNT, "registered proof inventory drift")
    need(hashlib.sha256(proof.audit_source().encode()).hexdigest() == PROOF_AUDIT_SHA, "proof audit drift")
    expected_kernel = {"status": "PASS", "lean_version": "4.19.0", "proof_entry_count": PROOF_COUNT,
        "audit_sha256": PROOF_AUDIT_SHA,
        "sources": {path: digest(root / path) for path in SOURCE_PATHS},
        "source_assumptions": "declared preorder, explicit partial domains and permitted separating evaluators; full fixed process and actual ordering maps"}
    exact(receipt["kernel"], expected_kernel, "kernel receipt drift")
    return artifacts

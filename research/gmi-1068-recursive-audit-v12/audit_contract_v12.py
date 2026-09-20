"""Exact reviewed scalarization adjudication and custody; no kernel replay here."""
import hashlib
import importlib.util
import json

PACKAGE = "research/gmi-1068-scalarization-v12"
ATOM_SPECS = {
    "GMI2-R2-006": ("prove scalarization boundaries",
        "General finite-vector weighted-order preservation, constructive reversal for every incomparable pair, and scalar/Pareto converse boundaries; real proofs are mathematical, generic ordered-ring proofs and the Int instance are kernel checked."),
}
REPAIR_SCOPES = {
    "R2": "General finite-vector weighted-order preservation, constructive incomparable-pair reversal, scalar order-reflection obstruction and positive-minimizer efficiency. Closes only original scalarization boundaries; no preferred weights, derived objectives or complete Pareto-frontier recovery.",
    "R14": "Seventeen exact statement contracts checked under Lean 4.19.0, with generic primitive ordered-ring assumptions and an actual Int instance. Real-valued specialization remains paper-only; three source-valid proof-registration corruptions are rejected.",
    "R15": "Independent exact rational order, dot-product and separator checks over the frozen dimension-zero-through-four grids, attained-minimizer and unsupported-frontier controls. Strict mandatory coverage, malformed-input controls and sole-atom custody prevent broader promotion.",
}
BOUNDARIES = [
    "one original scientific requirement only; R2 remains open",
    "explicit primitive ordered-ring laws; Int instance kernel checked; real instance paper-only",
    "all positive scalarizations characterize order; no single scalar reflects incomparables",
    "positive weighted sums need not select every Pareto-efficient point",
    "210 remaining original requirements retain their unresolved statuses",
    "no derived objective or preferred weights, architecture recovery or empirical novelty",
]
SOURCE_BINDINGS = {
    "research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json": "4cc262d491fbcdccf2b4c8656e80dcdb06e1795344500e46ac980ca09a679574",
    "research/gmi-1068-r2-context-irreducibility-v1/FREEZE_V1.md": "cd3754eb383e2796c3fe06dc7e9fbb7cf17d9d0bca35bea983e43fbc6b6ae320",
    "research/gmi-1068-recursive-audit-v11/SCOPE_SNAPSHOT_V11.json": "579e9ae78bf992b13ea5449b756f7da17ae6a694afe95dfc28989a79a6e56c07",
}
SOURCE_NAMES = ("ScalarLawsV12.lean", "FiniteSumsV12.lean", "ScalarizationV12.lean")
PROOF_CONTRACT_SHA = "07026a5467ab3a8a3581ba1e51a934c86078b15795c74a6df5a007732ec04959"
PROOF_AUDIT_SHA = "f2da29ab236601208c096f320aac24952aacdd2a4fbf2b534769a25f18a00767"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def exact(actual, expected, message):
    need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), message)


def load(path):
    spec = importlib.util.spec_from_file_location("v12_contract_" + path.stem, path)
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
    evidence = [witness(root, "RESULT_V12.json", "json_pointer", "/atoms/" + atom)]
    declarations = {"FiniteSumsV12.lean": ("dot_monotone", "dot_strict"),
                    "ScalarizationV12.lean": ("positive_family_recovers_order", "incomparable_reversal",
                                              "coordinate_no_total_reflection", "positive_minimizer_efficient")}
    return evidence + [witness(root, name, "lean_declaration", declaration)
                       for name, names in declarations.items() for declaration in names]


def repair(root, name):
    evidence = [witness(root, "check_scalarization_v12.py", "python_symbol", "evaluate"),
                witness(root, "RESULT_V12.json", "json_pointer", "/kernel" if name == "R14" else "/coverage")]
    extras = {"R2": ("ScalarizationV12.lean", "lean_declaration", "positive_family_recovers_order"),
              "R14": ("proof_contract_v12.py", "python_symbol", "audit_source"),
              "R15": ("independent_oracle_v12.py", "python_symbol", "check_separator")}
    evidence.insert(0, witness(root, *extras[name]))
    return {"id": name + "-scalar-v12", "scope": REPAIR_SCOPES[name],
            "status": "LOCAL_VERIFIED", "evidence": evidence}


def validate_receipt(root, receipt):
    need(type(receipt) is dict and set(receipt) == {
        "schema", "tests_run", "kernel", "coverage", "source_bindings", "atoms", "inputs",
        "overall_closure", "scientific_truth_certified", "claim_boundaries"}, "receipt fields")
    fixed = {"schema": "GMI_1068_SCALARIZATION_V12", "tests_run": 8,
             "overall_closure": "OPEN", "scientific_truth_certified": False, "claim_boundaries": BOUNDARIES}
    for key, value in fixed.items():
        exact(receipt[key], value, "receipt field drift:" + key)
    atoms = {key: {"title": title, "scope": scope, "status": "VERIFIED_AT_REGISTERED_SCOPE"}
             for key, (title, scope) in ATOM_SPECS.items()}
    exact(receipt["atoms"], atoms, "registered atom adjudication drift")
    artifacts = package_artifacts(root)
    inputs = {entry["path"].rsplit("/", 1)[-1]: entry["sha256"] for entry in artifacts
              if not entry["path"].endswith("/RESULT_V12.json")}
    exact(receipt["inputs"], inputs, "package input custody drift")
    exact(receipt["source_bindings"], SOURCE_BINDINGS, "historical source receipt drift")
    for path, expected in SOURCE_BINDINGS.items():
        need(digest(root / path) == expected, "historical source drift:" + path)
    package = root / PACKAGE
    exact(receipt["coverage"], load(package / "coverage_v12.py").REQUIRED, "coverage receipt drift")
    need(digest(package / "proof_contract_v12.py") == PROOF_CONTRACT_SHA, "reviewed proof-type drift")
    proof = load(package / "proof_contract_v12.py")
    need(proof.SOURCE_NAMES == SOURCE_NAMES and len(proof.ENTRIES) == 17, "registered proof inventory drift")
    need(hashlib.sha256(proof.audit_source().encode()).hexdigest() == PROOF_AUDIT_SHA, "proof audit drift")
    expected_kernel = {
        "status": "PASS", "lean_version": "4.19.0", "proof_entry_count": 17,
        "audit_sha256": PROOF_AUDIT_SHA,
        "sources": {PACKAGE + "/" + name: digest(package / name) for name in SOURCE_NAMES},
        "source_assumptions": BOUNDARIES[1],
    }
    exact(receipt["kernel"], expected_kernel, "kernel receipt drift")
    return artifacts

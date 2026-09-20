"""Reviewed exact V11 adjudications and receipt custody, not kernel replay."""
import hashlib
import importlib.util
import json

PACKAGE = "research/gmi-1068-typed-foundation-v11"
ATOM_SPECS = {
    "GMI2-R1-002": ("prove typing/associativity", "Constructed typed path concatenation and congruence quotient laws, with a general lawful-category presentation isomorphism; substrate adequacy remains conditional."),
    "GMI2-R1-003": ("prove identities", "Constructed typed empty paths and both unit laws, inherited by typed congruence quotients; no independent physical no-op assumption is eliminated."),
    "GMI2-R2-002": ("prove context not derived from process law", "Same full process and admitted history domain, opposite actual evaluator rankings: no uniform context recovery over any model class containing these two expansions."),
}
REPAIR_SCOPES = {
    "R1": "Constructed typed path category, unique generator interpretation and lawful-category presentation by evaluation-kernel quotient. Closes exactly original typing/associativity and identity requirements; no substrate or primitive-minimality claim.",
    "R2": "Fresh kernel replay and independent actual same-process, same-admitted-domain context collision and opposite rankings. Closes the original existential context nonrecoverability requirement; no probabilistic independence or universal restricted-class claim.",
    "R14": "Arbitrary typed paths, congruence quotients and lawful-category presentation isomorphism checked by Lean 4.19.0. Fourteen explicit statement types registered and their axioms inspected; three source-valid proof corruptions rejected.",
    "R15": "Independent finite paths, concrete interpretations, all edge-admission subsets, actual context witnesses, hostile inputs and proof-registration controls. Mandatory coverage gate and exact original-atom adjudication.",
}
BOUNDARIES = [
    "three original scientific requirements only; R1 and R2 remain open",
    "lawful target categories and typed congruences are explicit premises",
    "no claim every physical substrate already has these laws",
    "whole-round dependencies and 211 remaining requirements stay unresolved",
    "no primitive-count minimality, all-family derivation or empirical novelty",
]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def exact(actual, expected, message):
    # JSON equality also distinguishes bool/int/float aliases in nested records.
    need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), message)


def load(path):
    spec = importlib.util.spec_from_file_location("v11_contract_" + path.stem, path)
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
    evidence = [witness(root, "RESULT_V11.json", "json_pointer", "/atoms/" + atom)]
    if atom == "GMI2-R1-002":
        declarations = [("TypedPathsV11.lean", "append_assoc"), ("QuotientPathsV11.lean", "presentationIso")]
    elif atom == "GMI2-R1-003":
        declarations = [("TypedPathsV11.lean", "nil_append"), ("TypedPathsV11.lean", "append_nil")]
    else:
        return evidence + [witness(root, "independent_context_v11.py", "python_symbol", "audit")]
    return evidence + [witness(root, name, "lean_declaration", declaration)
                       for name, declaration in declarations]


def repair(root, name):
    evidence = [witness(root, "check_foundation_v11.py", "python_symbol", "evaluate"),
                witness(root, "RESULT_V11.json", "json_pointer", "/coverage")]
    extras = {"R1": ("QuotientPathsV11.lean", "lean_declaration", "presentationIso"),
              "R2": ("independent_context_v11.py", "python_symbol", "audit"),
              "R14": ("proof_contract_v11.py", "python_symbol", "audit_source")}
    if name in extras:
        evidence.insert(0, witness(root, *extras[name]))
    return {"id": name + "-typed-v11", "scope": REPAIR_SCOPES[name],
            "status": "LOCAL_VERIFIED", "evidence": evidence}


def validate_receipt(root, receipt):
    need(type(receipt) is dict and set(receipt) == {
        "schema", "tests_run", "kernel", "coverage", "context", "atoms", "inputs",
        "overall_closure", "scientific_truth_certified", "claim_boundaries"}, "receipt fields")
    fixed = {"schema": "GMI_1068_TYPED_FOUNDATION_V11", "tests_run": 12,
             "overall_closure": "OPEN", "scientific_truth_certified": False,
             "claim_boundaries": BOUNDARIES}
    for key, value in fixed.items():
        exact(receipt[key], value, "receipt field drift:" + key)
    atoms = {key: {"title": title, "scope": scope, "status": "VERIFIED_AT_REGISTERED_SCOPE"}
             for key, (title, scope) in ATOM_SPECS.items()}
    exact(receipt["atoms"], atoms, "registered atom adjudication drift")
    artifacts = package_artifacts(root)
    inputs = {entry["path"].rsplit("/", 1)[-1]: entry["sha256"] for entry in artifacts
              if not entry["path"].endswith("/RESULT_V11.json")}
    exact(receipt["inputs"], inputs, "package input custody drift")
    package = root / PACKAGE
    coverage = load(package / "coverage_v11.py")
    exact(receipt["coverage"], coverage.REQUIRED, "coverage receipt drift")
    proof = load(package / "proof_contract_v11.py")
    need(len(proof.ENTRIES) == 14, "registered proof count drift")
    sources = [PACKAGE + "/TypedPathsV11.lean", PACKAGE + "/QuotientPathsV11.lean",
               "research/gmi-1068-r0-foundation-repair-v9/RecoverabilityV9.lean"]
    expected_kernel = {
        "status": "PASS", "lean_version": "4.19.0", "proof_entry_count": 14,
        "audit_sha256": hashlib.sha256(proof.audit_source().encode()).hexdigest(),
        "sources": {path: digest(root / path) for path in sources},
        "source_assumptions": "lawful target categories and typed congruences are explicit",
    }
    exact(receipt["kernel"], expected_kernel, "kernel receipt drift")
    context = load(package / "independent_context_v11.py").audit(root)
    exact(receipt["context"], context, "context receipt drift")
    return artifacts

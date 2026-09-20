"""Reviewed specialization scope, immutable custody and derived current accounting."""
import hashlib
import importlib.util
import json

PACKAGE = "research/gmi-1068-context-specializations-v17"
ATOM_SPECS = {"GMI2-R2-005": (
    "characterize scalar/vector/viability contexts",
    "Actual partial contexts instantiate scalar utility, Boolean acceptance, finite Pareto vectors, explicitly dual cost preference, nonempty-set information order and existential viability. Codomain maps and products preserve their declared domain and order laws. Viability is the greatest safe postfixed set and, with classical choice, exactly admits an infinite safe trajectory; arbitrary finite-horizon survival is insufficient.")}
REPAIR_SCOPES = {
    "R2": "Actual scalar, Boolean, vector, dual-cost, nonempty-set and existential-viability contexts preserve their declared partial domains and induce the specified orders. Monotone maps preserve comparison; reflection needs its own premise. Shared and independent products retain their distinct empty-family domains. Only the original specialization requirement closes.",
    "R14": "Lean 4.19.0 checks actual context constructors, value and domain equations, comparison transport and reflection, products, duality and greatest safe postfixed viability. Classical successor choice connects viability to infinite safe trajectories; an infinite-branching countdown model refutes finite-horizon substitution. Immutable V15 partial-context source is freshly replayed.",
    "R15": "Independent exhaustive finite calibration checks all registered maps, partial specializations, products and discrete viability against cycle reachability and all safe postfixed sets. Malformed, missing-premise, custody and source-valid kernel corruptions are rejected. Two immutable V16 qualified readings remain separate from original requirement closure.",
}
BOUNDARIES = [
    "only original R2-005 closes; R2 remains OPEN",
    "preorders, admission, evaluator domains and evolution are declared",
    "monotonicity preserves comparison; reflection requires its own premise",
    "shared and independent empty products have different declared domains",
    "confidence is nonempty-set information order, not statistical calibration",
    "viability is existential discrete safety with explicit classical choice",
    "no automatic identity stuttering, adversarial safety or continuous-time limit",
    "finite exhaustive calibration is distinct from arbitrary-state kernel proofs",
    "classical parent constructions; no novel mechanism or empirical prediction claimed",
    "19 original fulfilled and 203 unresolved; two qualified replacements separately leave 201 active",
    "no canonical utility, universal scalar, assumption-free theory or full-family derivation",
]
SOURCE_NAMES = ("PartialContextV15.lean", "ContextMapsV17.lean", "ProductContextsV17.lean",
                "SpecializationsV17.lean", "ConfidenceV17.lean", "ViabilityV17.lean", "CountdownV17.lean")
SOURCE_PATHS = ("research/gmi-1068-partial-context-v15/PartialContextV15.lean",) + tuple(
    PACKAGE + "/" + name for name in SOURCE_NAMES[1:])
PROOF_CONTRACT_SHA = "4f06f8f0379a1d9dc49e0b1b4ba5a047a4f68725ce93e0b9acff8c3272550538"
PROOF_AUDIT_SHA = "f126965ec5a7d17593b2743cfad158147a5b6481d79ae0f2a79e6436d9a5c7ea"
PROOF_COUNT = 97
CUSTODY_SHA = "ca57b6bb39727f8363978396605ac47849143a92108b13db424387a4d7696f9b"
QUALIFIED = ["GMI2-R2-003@r1", "GMI2-R2-007@r1"]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def exact(actual, expected, message):
    need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), message)


def load(path):
    spec = importlib.util.spec_from_file_location("v17_contract_" + path.stem, path)
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
    declarations = (("ContextMapsV17.lean", "post_comparison_iff"),
        ("ProductContextsV17.lean", "independent_comparison"),
        ("SpecializationsV17.lean", "utility_comparison"),
        ("SpecializationsV17.lean", "acceptance_comparison"),
        ("SpecializationsV17.lean", "pareto_comparison"),
        ("SpecializationsV17.lean", "cost_comparison"),
        ("ConfidenceV17.lean", "confidence_comparison"),
        ("ViabilityV17.lean", "viable_iff_trajectory"),
        ("ViabilityV17.lean", "viability_comparison"),
        ("CountdownV17.lean", "finite_horizons_do_not_imply_viability"))
    return [witness(root, "RESULT_V17.json", "json_pointer", "/atoms/" + atom)] + [
        witness(root, name, "lean_declaration", declaration) for name, declaration in declarations]


def repair(root, name):
    evidence = [witness(root, "check_specializations_v17.py", "python_symbol", "evaluate"),
                witness(root, "RESULT_V17.json", "json_pointer", "/kernel" if name == "R14" else "/coverage")]
    extras = {"R2": ("ViabilityV17.lean", "lean_declaration", "viability_comparison"),
              "R14": ("proof_contract_v17.py", "python_symbol", "audit_source"),
              "R15": ("oracle_v17.py", "python_symbol", "cycle_survivors")}
    evidence.insert(0, witness(root, *extras[name]))
    return {"id": name + "-specializations-v17", "scope": REPAIR_SCOPES[name],
            "status": "LOCAL_VERIFIED", "evidence": evidence}


def validate_receipt(root, receipt):
    need(type(receipt) is dict and set(receipt) == {
        "schema", "tests_run", "kernel", "coverage", "source_bindings", "atoms", "inputs",
        "inherited_receipts", "amendment_carry", "overall_closure", "scientific_truth_certified",
        "claim_boundaries"}, "receipt fields")
    fixed = {"schema": "GMI_1068_CONTEXT_SPECIALIZATIONS_V17", "tests_run": 12,
             "overall_closure": "OPEN", "scientific_truth_certified": False, "claim_boundaries": BOUNDARIES}
    for key, value in fixed.items():
        exact(receipt[key], value, "receipt field drift:" + key)
    atoms = {key: {"title": title, "scope": scope, "status": "VERIFIED_AT_REGISTERED_SCOPE"}
             for key, (title, scope) in ATOM_SPECS.items()}
    exact(receipt["atoms"], atoms, "registered atom adjudication drift")
    artifacts = package_artifacts(root)
    inputs = {entry["path"].rsplit("/", 1)[-1]: entry["sha256"] for entry in artifacts
              if not entry["path"].endswith("/RESULT_V17.json")}
    exact(receipt["inputs"], inputs, "package input custody drift")
    package = root / PACKAGE
    need(digest(package / "custody_v17.py") == CUSTODY_SHA, "reviewed custody evaluator drift")
    custody = load(package / "custody_v17.py")
    try:
        expected_custody = custody.verify(root)
    except custody.CannotCheck as exc:
        raise OSError(str(exc)) from exc
    for key, value in expected_custody.items():
        exact(receipt[key], value, "inherited custody drift:" + key)
    exact(receipt["coverage"], load(package / "coverage_v17.py").REQUIRED, "coverage receipt drift")
    need(digest(package / "proof_contract_v17.py") == PROOF_CONTRACT_SHA, "reviewed proof-type drift")
    proof = load(package / "proof_contract_v17.py")
    need(proof.SOURCE_NAMES == SOURCE_NAMES and proof.SOURCE_PATHS == SOURCE_PATHS
         and len(proof.ENTRIES) == PROOF_COUNT, "registered proof inventory drift")
    need(hashlib.sha256(proof.audit_source().encode()).hexdigest() == PROOF_AUDIT_SHA, "proof audit drift")
    expected_kernel = {"status": "PASS", "lean_version": "4.19.0", "proof_entry_count": PROOF_COUNT,
        "audit_sha256": PROOF_AUDIT_SHA,
        "sources": {path: digest(root / path) for path in SOURCE_PATHS},
        "source_assumptions": "declared preorders, admission and evaluator domains; explicit monotonicity/reflection; existential discrete evolution and classical successor choice"}
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
    return {"schema": "GMI_1068_CURRENT_ACCOUNTING_V17", "snapshot_content_sha256": snapshot_sha,
            "original_total": len(records), "original_fulfilled": fulfilled, "original_unresolved": unresolved,
            "qualified_replacements": len(originals), "qualified_original_ids": originals,
            "active_unresolved": unresolved - len(originals), "amendment_carry": amendment_carry,
            "overall_closure": "OPEN", "scientific_truth_certified": False}

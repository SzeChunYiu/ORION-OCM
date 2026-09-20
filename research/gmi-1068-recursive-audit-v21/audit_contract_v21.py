"""Fixed weighted-execution closure contract and inherited source custody."""
import hashlib
import importlib.util
import json

PACKAGE = "research/gmi-1068-resource-attainability-v21"
ATOM_SPECS = {
    'GMI2-R3-001': ('formalize contextual attainability', 'Actual fixed partial contexts evaluate selected physically successful finite histories; the unrestricted finite-history image is the union of bounded-length images. Infinite traces and unattained limits are excluded.'),
    'GMI2-R3-002': ('formalize budget restriction', 'Actual V8 residual execution succeeds exactly when unrestricted finite execution succeeds with affordable accumulated Nat cost, preserving endpoint and successful full response; its contextual image is an actual restriction.'),
    'GMI2-R3-003': ('prove monotonicity', 'Fixed-context image inclusion follows from nested history selectors; actual resource execution derives capacity nesting. Changing the evaluator or arbitrarily labelling restrictions does not establish the premise.'),
    'GMI2-R3-005': ('derive capability projection', 'Capability for a declared target is exactly an admitted evaluated execution witness in the attainable image, equivalently an affordable target value in the actual joint cost/value relation.'),
    'GMI2-R3-006': ('derive resource response', 'Declared value-coordinate projections and resource-indexed admission images are separately constructed and related by actual joint cost/value fibers; Nat target response has an attained least finite threshold when nonempty.'),
    'GMI2-R3-010': ('mechanize attainability lemmas', 'Fresh typed replay of original attain_mono, maximal_is_attainable and impossible_means_no_target is bridged to actual partial-context images, alongside operational restriction, filtration and capability proofs.'),
}
RESULTS = {
    'U1': 'Actual weighted finite execution, concatenation and Nat residual accounting preserve successful complete V8 Responses.',
    'U2': 'Actual fixed V15 partial-context admission constructs finite-history images, selection monotonicity, horizon unions and operational capacity filtrations.',
    'U3': 'Joint execution-cost/value fibers determine resource-indexed capability and attained least Nat target costs; declared coordinate projection remains separate.',
    'U4': 'Noncommutative ordered accumulation supports prefix-based capacity nesting; nonnegative increments justify final-aggregate affordability, with an actual Nat residual bridge.',
}
REPAIR_SCOPES = {
    'R3': 'Actual weighted finite histories and fixed partial contexts construct attainable images, physical and Nat budget restrictions, selector/capacity monotonicity, declared target capability, joint cost/value resource responses and coordinate projections. Only original R3-001/002/003/005/006/010 close; prior R3-004 evidence is unchanged.',
    'R4': 'Declared ordered resource composition supports cumulative-prefix capacity nesting. Nonnegative increments justify final-cost affordability; actual Nat residual execution implements that specialization. Generic subtraction, least vector capacities and endpoint-only reduction for arbitrary history evaluators are not inferred. No R4 original requirement closes.',
    'R14': 'Fresh Lean 4.19.0 typed replay binds actual weighted execution, residual/full-response preservation, fixed partial-context images, horizon and budget unions, joint filtration, capability and attained Nat thresholds. Original Attainability lemmas are replayed and bridged; ordered-resource constructor and prefix hypotheses remain explicit.',
    'R15': 'Independent literal cumulative-prefix traversal checks actual V8 raw runs and budget lifts. Exhaustive actual V15 fibers, target witnesses, coordinate-composed evaluators and declared resource folds calibrate the registered finite scope; malformed, missing-source, coupled-custody and exact coverage attacks remain mandatory.',
}
BOUNDARIES = ['only original R3-001/002/003/005/006/010 close; R3 retains its inherited whole-round stale status', 'all histories are finite; an unbounded set of lengths is not an infinite trace or limit completion', 'history selection, process admission and evaluator definedness remain separate', 'capacity image nesting requires fixed evaluator, domain and interpretation', 'capability uses a declared target; neither target nor cost/value pairing is inferred from an unlabelled value image', 'resource-coordinate projection and resource-indexed admission are different operations', 'least attained Nat thresholds are semantic and may be noncomputable for arbitrary history-dependent contexts', 'ordered composition alone supplies neither positivity nor universal subtraction', 'final-aggregate affordability requires nonnegative increments; generic prefix semantics includes initial affordability', 'Python evidence concerns finite rosters and concrete resource operations; arbitrary generality belongs to its explicitly registered kernel statements', '27 original fulfilled and 195 unresolved; two qualified replacements separately leave 193 active', 'classical parent mathematics and scoped integration; no originality, universal objective or full GMI claimed']
SOURCE_PATHS = (
    'research/gmi-1068-partial-context-v15/PartialContextV15.lean',
    'research/gmi-1068-continuation-v8/ContinuationV8.lean',
    'research/gmi-1068-r3-contextual-attainability-v1/Attainability.lean',
    'research/gmi-1068-frontier-simulation-v20/FrontierOrderV20.lean',
    'research/gmi-1068-frontier-simulation-v20/GuardedMapsV20.lean',
    'research/gmi-1068-frontier-simulation-v20/PartialPostcontextV20.lean',
    'research/gmi-1068-resource-attainability-v21/OrderedCostsV21.lean',
    'research/gmi-1068-resource-attainability-v21/WeightedExecutionV21.lean',
    'research/gmi-1068-resource-attainability-v21/CumulativeV21.lean',
    'research/gmi-1068-resource-attainability-v21/BudgetResidualV21.lean',
    'research/gmi-1068-resource-attainability-v21/SuccessfulResponseV21.lean',
    'research/gmi-1068-resource-attainability-v21/HistoryContextsV21.lean',
    'research/gmi-1068-resource-attainability-v21/JointImagesV21.lean',
    'research/gmi-1068-resource-attainability-v21/HistoryUnionsV21.lean',
    'research/gmi-1068-resource-attainability-v21/CapabilityThresholdV21.lean',
    'research/gmi-1068-resource-attainability-v21/PathPositiveV21.lean',
    'research/gmi-1068-resource-attainability-v21/ConstructorBindingsV21.lean',
    'research/gmi-1068-resource-attainability-v21/ResourceControlsV21.lean',
    'research/gmi-1068-resource-attainability-v21/ProofTargetsV21.lean',
)
SOURCE_NAMES = tuple(path.rsplit("/",1)[1] for path in SOURCE_PATHS)
PROOF_CONTRACT_SHA = 'c34abddda77f8252b0926a81619a17f376baad72984342e8d68796bdfb033d95'
PROOF_AUDIT_SHA = '4cfeda2438df892f1dfbd5a5318ac4498aee853ea9dcf0bd3d98f3bfe6c80a80'
PROOF_COUNT = 152
REVIEWED_INPUTS = {
    'check_lean_v21.py': 'a07556f9261f59bd5d6633322ad61a25f881d4f9f758203832a63be054058096',
    'FORMAL_SCOPE_V21.md': 'a82b6062f895b24266e9fb92ecce413fcff8aa68092bbc51a93260c90e6a995c',
    'custody_v21.py': 'cdfa5176b9205457431b96211f8075bf5ae66df5e7310ebb05f83037889053ac',
    'coverage_v21.py': '8849436d258f13d5c349ef5376931f52b5d9c0a4ebc166d38ba147e0c16e8172',
}
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
    spec = importlib.util.spec_from_file_location("v21_contract_" + path.stem, path)
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
    path = name if name.startswith("research/") else PACKAGE + "/" + name
    return {"path": path, "sha256": digest(root / path), "kind": kind, "locator": locator}


def atom_evidence(root, atom):
    need(atom in ATOM_SPECS, "unregistered original closure")
    declarations = {
        "001": (("HistoryUnionsV21.lean", "from_image"), ("HistoryUnionsV21.lean", "all_horizon_union"),
                ("HistoryUnionsV21.lean", "v15_active_bridge")),
        "002": (("BudgetResidualV21.lean", "residual_iff"), ("SuccessfulResponseV21.lean", "successful_full_response"),
                ("HistoryContextsV21.lean", "bounded_subset")),
        "003": (("HistoryContextsV21.lean", "selector_mono"), ("HistoryContextsV21.lean", "bounded_mono")),
        "005": (("JointImagesV21.lean", "capability_joint"),),
        "006": (("JointImagesV21.lean", "projection_image"), ("JointImagesV21.lean", "joint_filtration"),
                ("CapabilityThresholdV21.lean", "capability_cutoff"), ("CapabilityThresholdV21.lean", "threshold_attained")),
        "010": (("HistoryUnionsV21.lean", "original_attain_bridge"), ("HistoryUnionsV21.lean", "original_maximal_bridge"),
                ("research/gmi-1068-r3-contextual-attainability-v1/Attainability.lean", "attain_mono"),
                ("research/gmi-1068-r3-contextual-attainability-v1/Attainability.lean", "maximal_is_attainable"),
                ("research/gmi-1068-r3-contextual-attainability-v1/Attainability.lean", "impossible_means_no_target")),
    }
    return [witness(root, "RESULT_V21.json", "json_pointer", "/atoms/" + atom)] + [
        witness(root, name, "lean_declaration", symbol) for name, symbol in declarations[atom[-3:]]]


def repair(root, name):
    evidence = [witness(root, "check_attainability_v21.py", "python_symbol", "evaluate"),
                witness(root, "RESULT_V21.json", "json_pointer", "/kernel" if name == "R14" else "/coverage")]
    extras = {"R3": ("HistoryContextsV21.lean", "lean_declaration", "bounded_mono"),
              "R4": ("CumulativeV21.lean", "lean_declaration", "prefix_iff_final"),
              "R14": ("proof_contract_v21.py", "python_symbol", "audit_source"),
              "R15": ("oracle_v21.py", "python_symbol", "execute")}
    evidence.insert(0, witness(root, *extras[name]))
    return {"id": name + "-resource-v21", "scope": REPAIR_SCOPES[name],
            "status": "LOCAL_VERIFIED", "evidence": evidence}


def validate_receipt(root, receipt):
    need(type(receipt) is dict and set(receipt) == {
        "schema", "tests_run", "kernel", "coverage", "source_bindings", "atoms", "inputs",
        "inherited_receipts", "amendment_carry", "registered_results", "overall_closure", "scientific_truth_certified",
        "claim_boundaries"}, "receipt fields")
    fixed = {"schema": "GMI_1068_RESOURCE_ATTAINABILITY_V21", "tests_run": 13,
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
              if not entry["path"].endswith("/RESULT_V21.json")}
    exact(receipt["inputs"], inputs, "package input custody drift")
    package = root / PACKAGE
    for name, expected in REVIEWED_INPUTS.items():
        need(digest(package / name) == expected, "reviewed evaluator/input drift:" + name)
    custody = load(package / "custody_v21.py")
    try:
        expected_custody = custody.verify(root)
    except custody.CannotCheck as exc:
        raise OSError(str(exc)) from exc
    for key, value in expected_custody.items():
        exact(receipt[key], value, "inherited custody drift:" + key)
    exact(receipt["coverage"], load(package / "coverage_v21.py").REQUIRED, "coverage receipt drift")
    need(digest(package / "proof_contract_v21.py") == PROOF_CONTRACT_SHA, "reviewed proof-type drift")
    proof = load(package / "proof_contract_v21.py")
    need(proof.SOURCE_NAMES == SOURCE_NAMES and proof.SOURCE_PATHS == SOURCE_PATHS
         and len(proof.ENTRIES) == PROOF_COUNT, "registered proof inventory drift")
    need(hashlib.sha256(proof.audit_source().encode()).hexdigest() == PROOF_AUDIT_SHA, "proof audit drift")
    expected_kernel = {"status": "PASS", "lean_version": "4.19.0", "proof_entry_count": PROOF_COUNT,
        "audit_sha256": PROOF_AUDIT_SHA,
        "sources": {path: digest(root / path) for path in SOURCE_PATHS},
        "source_assumptions": "actual V8 deterministic partial transitions; fixed V15 partial history evaluators; associative order-compatible cost product with explicit identity and no commutativity assumption; pathwise nonnegative increments for prefix/final equivalence; classical minimum characterization for Nat target costs"}
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
    return {"schema": "GMI_1068_CURRENT_ACCOUNTING_V21", "snapshot_content_sha256": snapshot_sha,
            "original_total": len(records), "original_fulfilled": fulfilled, "original_unresolved": unresolved,
            "qualified_replacements": len(originals), "qualified_original_ids": originals,
            "active_unresolved": unresolved - len(originals), "amendment_carry": amendment_carry,
            "overall_closure": "OPEN", "scientific_truth_certified": False}

"""Reviewed reference-envelope scope, immutable custody and derived current accounting."""
import hashlib
import importlib.util
import json

PACKAGE = "research/gmi-1068-reference-envelope-v18"
ATOM_SPECS = {'GMI2-R2-008': ('relate Legg-Hutter and intelligence measures',
                 'Legg-Hutter scores instantiate declared evaluation contexts with a chosen environment class, coding, rewards and '
                 'reference machine. Actual prefix wrappers expose reference dependence; the full bounded-profile score envelope equals '
                 'pointwise order at paper-proof scope. Declared expectation, lower-envelope and free-conversion target contexts recover '
                 'their parent constructions with explicit dynamic-consistency and completeness boundaries.')}
REPAIR_SCOPES = {'R14': 'Lean 4.19.0 checks actual Boolean-program wrapping, successful-domain classification, prefix freedom and shortest-description '
        'laws; finite scaled score separation; declared expectation and lower-envelope constructors; and free-category conversion with '
        'complete target contexts. Turing-machine universality, infinite Kraft sums and the countable Real envelope theorem remain paper '
        'proofs.',
 'R15': 'Independent flat-antichain enumeration calibrates finite interpreters against literal decoding and one shortest-program weight '
        'per distinct output. Exact finite profiles, probability families, operational one-shot reward timing, rectangularity controls, '
        'resource preorders, malformed inputs and custody mutations test their registered boundaries. Finite interpreters are never '
        'claimed universal.',
 'R2': 'Declared Legg-Hutter reference scores expose reference dependence through actual prefix wrappers. The full bounded-profile '
       'reference envelope equals pointwise order at paper-proof scope. Expectation, lower-envelope and free-conversion target contexts '
       'preserve declared domains and parent assumptions. Only the original measure-relation requirement closes; no canonical prior or '
       'universal scalar is selected.'}
BOUNDARIES = ['only original R2-008 closes; R2 remains OPEN',
 'fixed countable environment class, injective coding and bounded reward semantics',
 'unnormalized shortest-description weights; no inferred probability simplex',
 'the full reference-machine family must contain arbitrary target/padding wrappers',
 'Option-machine kernel semantics is not a universal Turing-machine implementation',
 'TM realizability, infinite Kraft and Real score-envelope proofs are paper-level',
 'finite prefix books are calibration models, never universal reference machines',
 'lower-envelope recursion requires additional assumptions; the example tests rectangular repair only',
 'complete resource signatures require every target and full observed object domain',
 'classical parent constructions and elementary adaptations; no originality or empirical prediction claimed',
 '20 original fulfilled and 202 unresolved; two qualified replacements separately leave 200 active',
 'no canonical prior, unique intelligence scalar, efficient selector or full-family derivation']
SOURCE_PATHS = ('research/gmi-1068-foundation-repair-v5/AdmissibilityV5.lean',
 'research/gmi-1068-partial-context-v15/PartialContextV15.lean',
 'research/gmi-1068-scalarization-v12/ScalarLawsV12.lean',
 'research/gmi-1068-scalarization-v12/FiniteSumsV12.lean',
 'research/gmi-1068-reference-envelope-v18/PrefixWrapperV18.lean',
 'research/gmi-1068-reference-envelope-v18/ShortestCodesV18.lean',
 'research/gmi-1068-reference-envelope-v18/FiniteMarginsV18.lean',
 'research/gmi-1068-reference-envelope-v18/LowerFiniteV18.lean',
 'research/gmi-1068-reference-envelope-v18/ExpectationContextsV18.lean',
 'research/gmi-1068-reference-envelope-v18/FreeMonotonesV18.lean')
SOURCE_NAMES = tuple(path.rsplit("/",1)[1] for path in SOURCE_PATHS)
PROOF_CONTRACT_SHA = "bebb46e4961b599955ef717df0371ffc289087e8a83c996a2154cd0b5031dda3"
PROOF_AUDIT_SHA = "6a474d99cd5c5b51c6c511fe9bd58e1340627edd712bb4e175b1e2883192cb09"
PROOF_COUNT = 75
CUSTODY_SHA = "0dc17d2527b456a5520b5b2ba60aa7edad97bb9429ef912546e37b73bdc1641c"
QUALIFIED = ["GMI2-R2-003@r1", "GMI2-R2-007@r1"]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def exact(actual, expected, message):
    need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), message)


def load(path):
    spec = importlib.util.spec_from_file_location("v18_contract_" + path.stem, path)
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
    declarations = (("PrefixWrapperV18.lean", "wrapper_prefix_free"),
        ("ShortestCodesV18.lean", "nontarget_minimum_iff"),
        ("FiniteMarginsV18.lean", "strict_separation"),
        ("ExpectationContextsV18.lean", "expectation_comparison"),
        ("ExpectationContextsV18.lean", "lower_comparison"),
        ("FreeMonotonesV18.lean", "target_family_complete"))
    return [witness(root, "RESULT_V18.json", "json_pointer", "/atoms/" + atom)] + [
        witness(root, name, "lean_declaration", declaration) for name, declaration in declarations]


def repair(root, name):
    evidence = [witness(root, "check_envelope_v18.py", "python_symbol", "evaluate"),
                witness(root, "RESULT_V18.json", "json_pointer", "/kernel" if name == "R14" else "/coverage")]
    extras = {"R2": ("ShortestCodesV18.lean", "lean_declaration", "nontarget_minimum_iff"),
              "R14": ("proof_contract_v18.py", "python_symbol", "audit_source"),
              "R15": ("oracle_v18.py", "python_symbol", "wrapper_decode")}
    evidence.insert(0, witness(root, *extras[name]))
    return {"id": name + "-envelope-v18", "scope": REPAIR_SCOPES[name],
            "status": "LOCAL_VERIFIED", "evidence": evidence}


def validate_receipt(root, receipt):
    need(type(receipt) is dict and set(receipt) == {
        "schema", "tests_run", "kernel", "coverage", "source_bindings", "atoms", "inputs",
        "inherited_receipts", "amendment_carry", "overall_closure", "scientific_truth_certified",
        "claim_boundaries"}, "receipt fields")
    fixed = {"schema": "GMI_1068_REFERENCE_ENVELOPE_V18", "tests_run": 16,
             "overall_closure": "OPEN", "scientific_truth_certified": False, "claim_boundaries": BOUNDARIES}
    for key, value in fixed.items():
        exact(receipt[key], value, "receipt field drift:" + key)
    atoms = {key: {"title": title, "scope": scope, "status": "VERIFIED_AT_REGISTERED_SCOPE"}
             for key, (title, scope) in ATOM_SPECS.items()}
    exact(receipt["atoms"], atoms, "registered atom adjudication drift")
    artifacts = package_artifacts(root)
    inputs = {entry["path"].rsplit("/", 1)[-1]: entry["sha256"] for entry in artifacts
              if not entry["path"].endswith("/RESULT_V18.json")}
    exact(receipt["inputs"], inputs, "package input custody drift")
    package = root / PACKAGE
    need(digest(package / "custody_v18.py") == CUSTODY_SHA, "reviewed custody evaluator drift")
    custody = load(package / "custody_v18.py")
    try:
        expected_custody = custody.verify(root)
    except custody.CannotCheck as exc:
        raise OSError(str(exc)) from exc
    for key, value in expected_custody.items():
        exact(receipt[key], value, "inherited custody drift:" + key)
    exact(receipt["coverage"], load(package / "coverage_v18.py").REQUIRED, "coverage receipt drift")
    need(digest(package / "proof_contract_v18.py") == PROOF_CONTRACT_SHA, "reviewed proof-type drift")
    proof = load(package / "proof_contract_v18.py")
    need(proof.SOURCE_NAMES == SOURCE_NAMES and proof.SOURCE_PATHS == SOURCE_PATHS
         and len(proof.ENTRIES) == PROOF_COUNT, "registered proof inventory drift")
    need(hashlib.sha256(proof.audit_source().encode()).hexdigest() == PROOF_AUDIT_SHA, "proof audit drift")
    expected_kernel = {"status": "PASS", "lean_version": "4.19.0", "proof_entry_count": PROOF_COUNT,
        "audit_sha256": PROOF_AUDIT_SHA,
        "sources": {path: digest(root / path) for path in SOURCE_PATHS},
        "source_assumptions": "partial-function machine denotations; prefix-free base domains; primitive ordered-ring laws with actual Int instance; supplied closed free-arrow predicates; external probability weights and nonempty finite families"}
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
    return {"schema": "GMI_1068_CURRENT_ACCOUNTING_V18", "snapshot_content_sha256": snapshot_sha,
            "original_total": len(records), "original_fulfilled": fulfilled, "original_unresolved": unresolved,
            "qualified_replacements": len(originals), "qualified_original_ids": originals,
            "active_unresolved": unresolved - len(originals), "amendment_carry": amendment_carry,
            "overall_closure": "OPEN", "scientific_truth_certified": False}

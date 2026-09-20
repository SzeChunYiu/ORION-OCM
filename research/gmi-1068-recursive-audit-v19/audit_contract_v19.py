"""Reviewed partial-algebra reconstruction scope, immutable custody and derived current accounting."""
import hashlib
import importlib.util
import json

PACKAGE = "research/gmi-1068-arrows-only-v19"
ATOM_SPECS = {}
RESULTS = {'S1': 'Two-sided local units, strong partial associativity and coherence derive unique endpoints, exact matching and an actual typed category.',
 'S2': 'Actual bundled category arrows give a partial algebra; both object-changing roundtrips preserve and reflect operations.',
 'S3': 'Actual raw words and unit-anchored empty histories are preserved; their full responses and the partial table contain equivalent '
       'recoverable information.',
 'S4': 'Isolated finite law and information-loss witnesses delimit the construction, including the minimum three-element unital associativity '
       'failure.'}
REPAIR_SCOPES = {'R1': 'The partial operation with strong associativity, two-sided local units and coherence reconstructs objects and typed arrows. Actual '
       'object-changing roundtrips preserve and reflect operations and raw-query responses. Complete response information is equivalent to the '
       'table for the declared interface; named-field erasure is not information loss. No original requirement closes.',
 'R14': 'Lean 4.19.0 checks the arbitrary partial-algebra construction, category bundling, object and arrow inverse maps, tagged operation and '
        'raw-response preservation, and attained-image recovery equivalence. Explicit law independence, weak-definedness and minimum-size '
        'controls delimit the reconstruction; no unrestricted signature minimum is inferred.',
 'R15': 'Every registered partial table is compared to an independent typed-endpoint criterion. Accepted tables undergo all registered words, '
        'anchored empties, arrow and object relabelings and both operational roundtrips. Finite decoder enumeration, named information-loss '
        'controls and malformed/custody mutations calibrate the scope without replacing arbitrary-carrier proofs.'}
BOUNDARIES = ['no original requirement closes and no new qualified replacement is authorized',
 'arbitrary small carriers and empty categories; laws are explicit assumptions',
 'units require both-sided conditional neutrality and self-composition',
 'strong associativity includes definedness; coherence is separately necessary',
 'roundtrip maps preserve and reflect partial multiplication; arbitrary multiplicative maps need not preserve units',
 'classical choice and equality may support abstract reconstruction; no general effective algorithm',
 'information sufficiency is relative to all raw words and unit-anchored empty histories',
 'retaining named symbols differs from retaining their reconstructible information',
 'finite tables supplement arbitrary-carrier and arbitrary-word kernel proofs',
 'classical parent mathematics and integration; no originality or empirical prediction claimed',
 '20 original fulfilled and 202 unresolved; two qualified replacements separately leave 200 active',
 'no signature-independent minimum, canonical prior, universal ontology or full intelligence theory']
SOURCE_PATHS = ('research/gmi-1068-r0-foundation-repair-v9/RecoverabilityV9.lean',
 'research/gmi-1068-typed-foundation-v11/TypedPathsV11.lean',
 'research/gmi-1068-corrected-targets-v16/GroupLawsV16.lean',
 'research/gmi-1068-arrows-only-v19/PartialUnitsV19.lean',
 'research/gmi-1068-arrows-only-v19/ReconstructedV19.lean',
 'research/gmi-1068-arrows-only-v19/BundledCategoryV19.lean',
 'research/gmi-1068-arrows-only-v19/ArrowRoundtripV19.lean',
 'research/gmi-1068-arrows-only-v19/CategoryRoundtripV19.lean',
 'research/gmi-1068-arrows-only-v19/TableTransportV19.lean',
 'research/gmi-1068-arrows-only-v19/ResponsesV19.lean',
 'research/gmi-1068-arrows-only-v19/RoundtripResponsesV19.lean',
 'research/gmi-1068-arrows-only-v19/CountermodelsV19.lean',
 'research/gmi-1068-arrows-only-v19/InformationControlsV19.lean')
SOURCE_NAMES = tuple(path.rsplit("/",1)[1] for path in SOURCE_PATHS)
PROOF_CONTRACT_SHA = "b696d032e88e3b48c48f1dc311ef909e769a88f3f5915653bb23466139420bf4"
PROOF_AUDIT_SHA = "05a24aca7d0a1bdc21bae626c37519995c6738b15a8502d181ad040c7fb3894f"
PROOF_COUNT = 123
CUSTODY_SHA = "1403e8144411d8af88caa7ca35f50d26400b153a153ee908ac64857bc89a322d"
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
    spec = importlib.util.spec_from_file_location("v19_contract_" + path.stem, path)
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
    raise ValueError("no original closure is authorized in V19")


def repair(root, name):
    evidence = [witness(root, "check_reconstruction_v19.py", "python_symbol", "evaluate"),
                witness(root, "RESULT_V19.json", "json_pointer", "/kernel" if name == "R14" else "/coverage")]
    extras = {"R1": ("ReconstructedV19.lean", "lean_declaration", "category_composition"),
              "R14": ("proof_contract_v19.py", "python_symbol", "audit_source"),
              "R15": ("oracle_v19.py", "python_symbol", "typed_reconstruction")}
    evidence.insert(0, witness(root, *extras[name]))
    return {"id": name + "-arrows-v19", "scope": REPAIR_SCOPES[name],
            "status": "LOCAL_VERIFIED", "evidence": evidence}


def validate_receipt(root, receipt):
    need(type(receipt) is dict and set(receipt) == {
        "schema", "tests_run", "kernel", "coverage", "source_bindings", "atoms", "inputs",
        "inherited_receipts", "amendment_carry", "registered_results", "overall_closure", "scientific_truth_certified",
        "claim_boundaries"}, "receipt fields")
    fixed = {"schema": "GMI_1068_ARROWS_ONLY_V19", "tests_run": 11,
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
              if not entry["path"].endswith("/RESULT_V19.json")}
    exact(receipt["inputs"], inputs, "package input custody drift")
    package = root / PACKAGE
    need(digest(package / "custody_v19.py") == CUSTODY_SHA, "reviewed custody evaluator drift")
    custody = load(package / "custody_v19.py")
    try:
        expected_custody = custody.verify(root)
    except custody.CannotCheck as exc:
        raise OSError(str(exc)) from exc
    for key, value in expected_custody.items():
        exact(receipt[key], value, "inherited custody drift:" + key)
    exact(receipt["coverage"], load(package / "coverage_v19.py").REQUIRED, "coverage receipt drift")
    need(digest(package / "proof_contract_v19.py") == PROOF_CONTRACT_SHA, "reviewed proof-type drift")
    proof = load(package / "proof_contract_v19.py")
    need(proof.SOURCE_NAMES == SOURCE_NAMES and proof.SOURCE_PATHS == SOURCE_PATHS
         and len(proof.ENTRIES) == PROOF_COUNT, "registered proof inventory drift")
    need(hashlib.sha256(proof.audit_source().encode()).hexdigest() == PROOF_AUDIT_SHA, "proof audit drift")
    expected_kernel = {"status": "PASS", "lean_version": "4.19.0", "proof_entry_count": PROOF_COUNT,
        "audit_sha256": PROOF_AUDIT_SHA,
        "sources": {path: digest(root / path) for path in SOURCE_PATHS},
        "source_assumptions": "actual Option-valued operations with strong associativity, both-sided local units and coherence; supplied lawful typed categories; arbitrary carriers including empty; classical choices for abstract reconstruction"}
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
    return {"schema": "GMI_1068_CURRENT_ACCOUNTING_V19", "snapshot_content_sha256": snapshot_sha,
            "original_total": len(records), "original_fulfilled": fulfilled, "original_unresolved": unresolved,
            "qualified_replacements": len(originals), "qualified_original_ids": originals,
            "active_unresolved": unresolved - len(originals), "amendment_carry": amendment_carry,
            "overall_closure": "OPEN", "scientific_truth_certified": False}

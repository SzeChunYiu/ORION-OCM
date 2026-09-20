"""Fixed permission-barrier closure and inherited source custody contract."""
import hashlib
import importlib.util
import json

PACKAGE = "research/gmi-1068-permission-barriers-v22"
ATOM_SPECS = {'GMI2-R3-007': ['derive impossibility and barriers',
                 'Actual permission-gated execution and fixed partial contexts derive target impossibility, relative enabling deficits and deletion '
                 'blockers. Minimal blockers require blocking plus private eligible witnesses; the generic history-admission specialization '
                 'preserves the original one-step relief scope.']}
RESULTS = {'V1': 'Actual state/action-sensitive edge gating succeeds exactly when the physical history succeeds and its accumulated permissions are enabled, '
       'preserving complete successful V8 Responses.',
 'V2': 'Actual fixed V15 contexts derive target capability and impossibility from eligible physical history requirements, with history identities '
       'and partial evaluation retained.',
 'V3': 'Relative additions are characterized by available witness deficits; deletion blockers are hitting sets of currently available target '
       'supports, with exact minimality/private-witness certificates and explicit finite enumeration scope.'}
BOUNDARIES = ['only original R3-007 closes; R3 remains stale overall and R3-008/009 remain unresolved',
 'optional positive edge permissions preserve observations, physical edges, payloads, costs and fixed evaluator meanings',
 'raw finite histories retain their identities; equal endpoints, supports or values do not make histories identical',
 'gated success preserves full responses; failed gated and unrestricted responses need not agree',
 'generic incidence requires exact admission semantics; actual edge gating earns that bridge',
 'relative additions range over all subsets of available permissions outside the baseline; arbitrary restricted intervention families need separate '
 'constraints',
 'blockers concern currently available eligible target histories; off-universe supports do not impose deletion constraints',
 'private witnesses certify minimality only together with actual blocking',
 'minimal by inclusion does not mean least cardinality, least cost or unique',
 'finite roster impossibility is not all-word impossibility; infinite witness families need separate completeness or computability premises',
 '28 fulfilled and 194 unresolved originals; two unchanged qualified replacements separately leave 192 active unresolved',
 'classical parent integration; no identified physical cause, universal intervention family, novelty or complete GMI claim']
REPAIR_SCOPES = {'R14': 'Fresh Lean 4.19.0 typed replay binds the actual gated machine, recursive state/action support, complete successful responses, fixed partial-context '
        'incidence, available-universe deficits, blocker/private-witness equivalence and finite subset enumeration. Generic history admission is distinguished '
        'from independently realizable graph edge gates.',
 'R15': 'Independent literal gated traversal and exhaustive finite intervention enumeration check actual V8 responses, fixed V15 history identities, '
        'available-universe restrictions and private witnesses. Original R3 fixture replay, malformed inputs, inherited byte custody and exact coverage '
        'attacks calibrate the registered finite scope without all-word completeness claims.',
 'R3': 'Actual positive permission gating preserves physical edges, payloads and successful full responses. Fixed partial contexts derive target '
       'impossibility, relative enabling deficits and deletion blockers with blocking plus private eligible witnesses; generic history admission retains '
       'original distinct one-step relief witnesses. Only original R3-007 closes; all inherited R3 closures and unresolved R3-008/009 remain unchanged.'}
SOURCE_PATHS = (
    'research/gmi-1068-partial-context-v15/PartialContextV15.lean',
    'research/gmi-1068-continuation-v8/ContinuationV8.lean',
    'research/gmi-1068-resource-attainability-v21/OrderedCostsV21.lean',
    'research/gmi-1068-resource-attainability-v21/WeightedExecutionV21.lean',
    'research/gmi-1068-resource-attainability-v21/CumulativeV21.lean',
    'research/gmi-1068-resource-attainability-v21/BudgetResidualV21.lean',
    'research/gmi-1068-frontier-simulation-v20/FrontierOrderV20.lean',
    'research/gmi-1068-frontier-simulation-v20/GuardedMapsV20.lean',
    'research/gmi-1068-frontier-simulation-v20/PartialPostcontextV20.lean',
    'research/gmi-1068-permission-barriers-v22/PermissionSetsV22.lean',
    'research/gmi-1068-permission-barriers-v22/PermissionMachineV22.lean',
    'research/gmi-1068-permission-barriers-v22/PermissionExecutionV22.lean',
    'research/gmi-1068-permission-barriers-v22/PermissionIncidenceV22.lean',
    'research/gmi-1068-permission-barriers-v22/PermissionMinimalityV22.lean',
    'research/gmi-1068-permission-barriers-v22/PermissionContextsV22.lean',
    'research/gmi-1068-permission-barriers-v22/HistoryPermissionsV22.lean',
    'research/gmi-1068-permission-barriers-v22/FinitePermissionsV22.lean',
    'research/gmi-1068-permission-barriers-v22/SupportFrontierV22.lean',
    'research/gmi-1068-permission-barriers-v22/ConstructorBindingsV22.lean',
    'research/gmi-1068-permission-barriers-v22/PermissionControlsV22.lean',
    'research/gmi-1068-permission-barriers-v22/ProofTargetsV22.lean',
)
SOURCE_NAMES = tuple(path.rsplit("/",1)[1] for path in SOURCE_PATHS)
PROOF_CONTRACT_SHA = 'e85def9e00fbfe4ab120559414dad59c6997907e27f1ac8c26eb5f729144f98a'
PROOF_AUDIT_SHA = 'be0d49a99862b18e5da14f6c0760aa603400559198eb1364a4782632a5119968'
PROOF_COUNT = 145
REVIEWED_INPUTS = {'custody_v22.py': '4aefd2fa603857fd38dae41a521ed8076c7be8f0c1b18820489cb11d82c35786', 'coverage_v22.py': 'f1d3ec4bddee8007cdd47b0e34aad1272ae3ead589ea7b89615dfc8182040fe6', 'check_lean_v22.py': '6c6e7cedd882cbdd620a2699051bbdbc39428381aa97f2c66570677d718f5e76', 'FORMAL_SCOPE_V22.md': '860962aef8b56f466a90953dc775aec1e9c9f5e9f33e3340e1e06a1229d425ae'}
QUALIFIED = ["GMI2-R2-003@r1", "GMI2-R2-007@r1"]

SOURCE_ASSUMPTIONS = 'actual V8 deterministic partial transitions; fixed state/action permission requirements; fixed V15 partial evaluators and history selectors; positive requirement admission; full powerset of permitted additions; classical finite predicate enumeration and infinite-family incidence; no causal identification'

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
    spec = importlib.util.spec_from_file_location("v22_contract_" + path.stem, path)
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
    declarations = (("PermissionExecutionV22.lean", "gated_success"),
        ("PermissionExecutionV22.lean", "full_successful_response"),
        ("PermissionContextsV22.lean", "context_incidence"),
        ("PermissionContextsV22.lean", "context_impossible"),
        ("PermissionMinimalityV22.lean", "minimal_enabling"),
        ("PermissionMinimalityV22.lean", "minimal_blocker"),
        ("HistoryPermissionsV22.lean", "one_history_relief"))
    return [witness(root, "RESULT_V22.json", "json_pointer", "/atoms/" + atom)] + [
        witness(root, name, "lean_declaration", symbol) for name, symbol in declarations]


def repair(root, name):
    evidence = [witness(root, "check_barriers_v22.py", "python_symbol", "evaluate"),
                witness(root, "RESULT_V22.json", "json_pointer", "/kernel" if name == "R14" else "/coverage")]
    extras = {"R3": ("PermissionContextsV22.lean", "lean_declaration", "context_impossible"),
              "R14": ("proof_contract_v22.py", "python_symbol", "audit_source"),
              "R15": ("oracle_v22.py", "python_symbol", "execute")}
    evidence.insert(0, witness(root, *extras[name]))
    return {"id": name + "-barriers-v22", "scope": REPAIR_SCOPES[name],
            "status": "LOCAL_VERIFIED", "evidence": evidence}


def validate_receipt(root, receipt):
    need(type(receipt) is dict and set(receipt) == {
        "schema", "tests_run", "kernel", "coverage", "source_bindings", "atoms", "inputs",
        "inherited_receipts", "amendment_carry", "registered_results", "overall_closure", "scientific_truth_certified",
        "claim_boundaries"}, "receipt fields")
    fixed = {"schema": "GMI_1068_PERMISSION_BARRIERS_V22", "tests_run": 12,
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
              if not entry["path"].endswith("/RESULT_V22.json")}
    exact(receipt["inputs"], inputs, "package input custody drift")
    package = root / PACKAGE
    for name, expected in REVIEWED_INPUTS.items():
        need(digest(package / name) == expected, "reviewed evaluator/input drift:" + name)
    custody = load(package / "custody_v22.py")
    try:
        expected_custody = custody.verify(root)
    except custody.CannotCheck as exc:
        raise OSError(str(exc)) from exc
    for key, value in expected_custody.items():
        exact(receipt[key], value, "inherited custody drift:" + key)
    exact(receipt["coverage"], load(package / "coverage_v22.py").REQUIRED, "coverage receipt drift")
    need(digest(package / "proof_contract_v22.py") == PROOF_CONTRACT_SHA, "reviewed proof-type drift")
    proof = load(package / "proof_contract_v22.py")
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
    return {"schema": "GMI_1068_CURRENT_ACCOUNTING_V22", "snapshot_content_sha256": snapshot_sha,
            "original_total": len(records), "original_fulfilled": fulfilled, "original_unresolved": unresolved,
            "qualified_replacements": len(originals), "qualified_original_ids": originals,
            "active_unresolved": unresolved - len(originals), "amendment_carry": amendment_carry,
            "overall_closure": "OPEN", "scientific_truth_certified": False}

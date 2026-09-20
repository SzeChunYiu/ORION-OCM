"""Fixed frontier closure contract, inherited custody and derived current accounting."""
import hashlib
import importlib.util
import json

PACKAGE = "research/gmi-1068-frontier-simulation-v20"
ATOM_SPECS = {'GMI2-R3-004': ('prove frontier construction conditions',
                 'Actual finite attainable images under declared admission and evaluator domains have a constructed maximal '
                 'frontier, cofinality and equal downward closure. Equivalent maximal values remain distinct unless an '
                 'explicit representative selector is used. Infinite existence requires additional assumptions; the '
                 'original finite-frontier requirement alone closes.')}
RESULTS = {'T1': 'Construct finite maximal frontiers and class representatives for actual attained images; well-founded strict ascent '
       'separately supplies maximal extensions on arbitrary attained preorders.',
 'T2': 'Guarded partial maps are exactly those preserving downward output images under every finite cofinal pruning; actual '
       'partial context postcomposition preserves admission and updates evaluator definedness.',
 'T3': 'Greatest base-contained deterministic forward simulation equals one-sided preservation of all same finite action '
       'words and makes continuation pruning safe at the declared endpoint scope.',
 'T4': 'Independent finite refinement, distinguishing words, actual residual-budget lifting and guarded endpoint evaluation '
       'repair unsafe pruning under explicit observer assumptions.'}
REPAIR_SCOPES = {'R14': 'Lean 4.19.0 checks actual frontier and partial-context constructors, well-founded maximal extension, guarded-map '
        'equivalence and composition, greatest deterministic simulation and same-word endpoint pruning. Python refinement '
        'and representative minimality remain separately identified finite calibration.',
 'R15': 'Independent exhaustive subset covers, partial-map image checks and pair-BFS witnesses calibrate actual finite '
        'constructions. Residual-budget and endpoint-context controls demonstrate unsafe-pruning recovery; malformed data, '
        'custody and exact coverage mutations delimit the evidence.',
 'R3': 'Constructed finite attained frontiers are cofinal and have equal downward closure under declared admission and '
       'evaluator domains. Explicit representatives choose one member per maximal equivalence class; minimum-cardinality '
       'correspondence is finite calibration. Only original R3-004 closes; arbitrary infinite frontiers require additional '
       'assumptions.',
 'R4': 'Guarded partial maps preserve downward outputs exactly under all finite cofinal prunings. Greatest base-contained '
       'deterministic simulation preserves the same action words, enabling safe continuation pruning and guarded endpoint '
       'evaluation. This does not certify nondeterministic trace equivalence or arbitrary goal preservation.'}
BOUNDARIES = ['only original R3-004 closes; R3 retains its inherited whole-round stale status',
 'finite attained image is required for finite frontier construction; finite individual histories alone do not imply it',
 'preorder-equivalent maximal values remain distinct until an explicit representative choice',
 'representative minimality is among cofinal subsets of the attained set, not absolute encoding size',
 'well-founded strict ascent is sufficient for maximal extensions, not necessary or a finite-frontier guarantee',
 'partial context postcomposition preserves admission and changes evaluator definedness',
 'pruning preserves existential upward goals, not arbitrary targets, probabilities, multiplicities or history identity',
 'greatest simulation concerns one-sided same-word admission for deterministic partial actions',
 'state simulation needs guarded active endpoint evaluation to preserve attained value goals',
 'finite refinement and budget adapter evidence does not certify full V8 output/cost trace equality',
 '21 original fulfilled and 201 unresolved; two qualified replacements separately leave 199 active',
 'classical parent mathematics and scoped integration; no originality, universal objective or full GMI claimed']
SOURCE_PATHS = ('research/gmi-1068-partial-context-v15/PartialContextV15.lean',
 'research/gmi-1068-frontier-simulation-v20/FrontierOrderV20.lean',
 'research/gmi-1068-frontier-simulation-v20/WellFoundedFrontierV20.lean',
 'research/gmi-1068-frontier-simulation-v20/GuardedMapsV20.lean',
 'research/gmi-1068-frontier-simulation-v20/PartialPostcontextV20.lean',
 'research/gmi-1068-frontier-simulation-v20/AttainedFrontierV20.lean',
 'research/gmi-1068-frontier-simulation-v20/SimulationV20.lean',
 'research/gmi-1068-frontier-simulation-v20/SimulationPruningV20.lean',
 'research/gmi-1068-frontier-simulation-v20/ConstructorBindingsV20.lean',
 'research/gmi-1068-frontier-simulation-v20/ProofTargetsV20.lean')
SOURCE_NAMES = tuple(path.rsplit("/",1)[1] for path in SOURCE_PATHS)
PROOF_CONTRACT_SHA = "45e0a2a53ad5f2cb43dff277dcdba6ce2dedae65ef0a8d869fdd0a6ad4bd9794"
PROOF_AUDIT_SHA = "5eecc29b032a58934de79edd0383da1858ddfa09963b69bc31dd4d57660f90fc"
PROOF_COUNT = 100
REVIEWED_INPUTS = {'FORMAL_SCOPE_V20.md': 'b5661db987ccdb406204f3b1954c35dbe9a586d3231b167a72e6e83c87aad920',
 'check_lean_v20.py': '52a7f8fcc8628091326511dce58622358a9d1050f5fa8c3479a2d63bd7eaa7a4',
 'coverage_v20.py': '9a56ba49cb0b1218f81872926893b5e073de5b263de5247db7f5aa4871a504d8',
 'custody_v20.py': '1fd68de800fce1b84dd5f0d7aaec5dab6a9d4b215fa94683cd00a8886eb184d6'}
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
    spec = importlib.util.spec_from_file_location("v20_contract_" + path.stem, path)
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
    need(atom in ATOM_SPECS, "unregistered original closure")
    return [witness(root, "RESULT_V20.json", "json_pointer", "/atoms/" + atom),
            witness(root, "AttainedFrontierV20.lean", "lean_declaration", "attained_frontier_cofinal"),
            witness(root, "AttainedFrontierV20.lean", "lean_declaration", "attained_frontier_down"),
            witness(root, "FrontierOrderV20.lean", "lean_declaration", "frontier_mem")]


def repair(root, name):
    evidence = [witness(root, "check_frontier_v20.py", "python_symbol", "evaluate"),
                witness(root, "RESULT_V20.json", "json_pointer", "/kernel" if name == "R14" else "/coverage")]
    extras = {"R3": ("AttainedFrontierV20.lean", "lean_declaration", "attained_frontier_cofinal"),
              "R4": ("SimulationPruningV20.lean", "lean_declaration", "endpoint_value_pruning"),
              "R14": ("proof_contract_v20.py", "python_symbol", "audit_source"),
              "R15": ("oracle_v20.py", "python_symbol", "witness")}
    evidence.insert(0, witness(root, *extras[name]))
    return {"id": name + "-frontier-v20", "scope": REPAIR_SCOPES[name],
            "status": "LOCAL_VERIFIED", "evidence": evidence}


def validate_receipt(root, receipt):
    need(type(receipt) is dict and set(receipt) == {
        "schema", "tests_run", "kernel", "coverage", "source_bindings", "atoms", "inputs",
        "inherited_receipts", "amendment_carry", "registered_results", "overall_closure", "scientific_truth_certified",
        "claim_boundaries"}, "receipt fields")
    fixed = {"schema": "GMI_1068_FRONTIER_SIMULATION_V20", "tests_run": 14,
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
              if not entry["path"].endswith("/RESULT_V20.json")}
    exact(receipt["inputs"], inputs, "package input custody drift")
    package = root / PACKAGE
    for name, expected in REVIEWED_INPUTS.items():
        need(digest(package / name) == expected, "reviewed evaluator/input drift:" + name)
    custody = load(package / "custody_v20.py")
    try:
        expected_custody = custody.verify(root)
    except custody.CannotCheck as exc:
        raise OSError(str(exc)) from exc
    for key, value in expected_custody.items():
        exact(receipt[key], value, "inherited custody drift:" + key)
    exact(receipt["coverage"], load(package / "coverage_v20.py").REQUIRED, "coverage receipt drift")
    need(digest(package / "proof_contract_v20.py") == PROOF_CONTRACT_SHA, "reviewed proof-type drift")
    proof = load(package / "proof_contract_v20.py")
    need(proof.SOURCE_NAMES == SOURCE_NAMES and proof.SOURCE_PATHS == SOURCE_PATHS
         and len(proof.ENTRIES) == PROOF_COUNT, "registered proof inventory drift")
    need(hashlib.sha256(proof.audit_source().encode()).hexdigest() == PROOF_AUDIT_SHA, "proof audit drift")
    expected_kernel = {"status": "PASS", "lean_version": "4.19.0", "proof_entry_count": PROOF_COUNT,
        "audit_sha256": PROOF_AUDIT_SHA,
        "sources": {path: digest(root / path) for path in SOURCE_PATHS},
        "source_assumptions": "arbitrary preorders and Option-valued deterministic actions; decidable comparison for finite frontier computation; explicit well-founded reverse strict ascent for the infinite extension; guarded endpoint evaluators; classical choice for abstract partial contexts"}
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
    return {"schema": "GMI_1068_CURRENT_ACCOUNTING_V20", "snapshot_content_sha256": snapshot_sha,
            "original_total": len(records), "original_fulfilled": fulfilled, "original_unresolved": unresolved,
            "qualified_replacements": len(originals), "qualified_original_ids": originals,
            "active_unresolved": unresolved - len(originals), "amendment_carry": amendment_carry,
            "overall_closure": "OPEN", "scientific_truth_certified": False}

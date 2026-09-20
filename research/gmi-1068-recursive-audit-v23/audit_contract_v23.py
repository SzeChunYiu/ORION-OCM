"""Fixed affine-regime closure contract and inherited source custody."""
import hashlib
import importlib.util
import json

PACKAGE = "research/gmi-1068-affine-regimes-v23"
ATOM_SPECS = {'GMI2-R3-008': ['derive phase/frontier change',
                 'Actual affine families of partial contexts admit a common decoded value space and preserve all winning identities. Whole-interval endpoint '
                 'laws hold under explicit ordered-ring assumptions; exact rational root/cell diagrams and independent interval certificates establish the '
                 'registered finite affine regimes, including ties.']}
RESULTS = {'W1': 'Actual V15 code and common-value contexts, explicit injective decoders and V20 full maximality preserve all active winning identities and '
       'partial-evaluation tags.',
 'W2': 'Primitive ordered-ring laws derive affine whole-interval weak and strict endpoint dominance, universal weak-winner intersection and the exact '
       'universal-unique criterion, without division or density.',
 'W3': 'Exact rational boundary/open-cell diagrams retain all winner identities and admit independent whole-interval inequality certificates; existential and '
       'universal parameter claims remain distinct.'}
BOUNDARIES = ['only original R3-008 closes at registered affine context-family scope; R3 remains stale and R3-009 remains unresolved',
 'candidate identities, affine coefficients, admission and evaluator domain are fixed across the parameter interval',
 'actual values inhabit a common identity/scalar space; parameter-indexed integer codes require their explicit decoder',
 'all ties and distinct equal-score identities are retained; a preorder quotient or tie breaker does not give the same winner set',
 'whole-interval endpoint laws require lo<=hi and primitive ordered-ring structure; they do not require density or division',
 'singleton universal weak-winner intersection does not imply uniqueness everywhere; the exact unique criterion retains strict comparisons to all other active '
 'identities',
 'general rational root existence and full cell/sample completeness are paper plus exact Fraction evidence, not a claimed ordered-field kernel construction',
 'only winner identities are constant on open cells; numeric attainable values may vary',
 'all-pair roots refine the envelope, and nonwinning crossings need not change winners',
 'explicit-roster root counts are not efficient compact-graph path-envelope bounds or universal nonlinear regime algorithms',
 '29 fulfilled and 193 unresolved originals; two unchanged qualified replacements separately leave 191 active unresolved',
 'classical parent integration; no thermodynamic transition, universal objective, originality or complete GMI claimed']
REPAIR_SCOPES = {'R14': 'Fresh Lean 4.19.0 typed replay binds actual V15 affine code/common contexts, V17 decoder postcomposition, V20 full maximality, primitive ordered-ring '
        'endpoint dominance and universal weak/unique criteria. Actual Int and conditional root certificates retain their declared premises; general rational '
        'root enumeration and cell completeness remain paper plus finite evidence.',
 'R15': 'Independent rational half-line intersections certify complete closed winning intervals, every open-cell label and all-pair refinement. Exhaustive '
        'actual partial contexts preserve P/E, IDs and decoder meanings. Actual legacy affine helpers and original R3 ties are replayed, with diagram/codec '
        'mutations, malformed inputs, inherited custody and exact coverage controls.',
 'R3': 'Actual affine partial-context families and explicit common-value decoders retain every winning identity. Primitive ordered-ring endpoint laws and '
       'exact rational whole-cell certificates derive registered parameter regimes. Only original R3-008 closes; all inherited records, including R3-007 and '
       'unresolved R3-009, remain unchanged.'}
SOURCE_PATHS = (
    'research/gmi-1068-partial-context-v15/PartialContextV15.lean',
    'research/gmi-1068-context-specializations-v17/ContextMapsV17.lean',
    'research/gmi-1068-scalarization-v12/ScalarLawsV12.lean',
    'research/gmi-1068-scalarization-v12/FiniteSumsV12.lean',
    'research/gmi-1068-frontier-simulation-v20/FrontierOrderV20.lean',
    'research/gmi-1068-frontier-simulation-v20/GuardedMapsV20.lean',
    'research/gmi-1068-frontier-simulation-v20/PartialPostcontextV20.lean',
    'research/gmi-1068-affine-regimes-v23/AffineArithmeticV23.lean',
    'research/gmi-1068-affine-regimes-v23/AffineIntervalsV23.lean',
    'research/gmi-1068-affine-regimes-v23/AffineContextsV23.lean',
    'research/gmi-1068-affine-regimes-v23/AffineDecodersV23.lean',
    'research/gmi-1068-affine-regimes-v23/AffineWinnersV23.lean',
    'research/gmi-1068-affine-regimes-v23/FiniteWinnersV23.lean',
    'research/gmi-1068-affine-regimes-v23/PossibleWinnersV23.lean',
    'research/gmi-1068-affine-regimes-v23/RootCertificatesV23.lean',
    'research/gmi-1068-affine-regimes-v23/AffineControlsV23.lean',
    'research/gmi-1068-affine-regimes-v23/ConstructorBindingsV23.lean',
    'research/gmi-1068-affine-regimes-v23/ProofTargetsV23.lean',
)
SOURCE_NAMES = tuple(path.rsplit("/",1)[1] for path in SOURCE_PATHS)
PROOF_CONTRACT_SHA = '7dd44e1e03e5f815d16152a597ca62a66d89df5f66093c4be29e60462b1c79dc'
PROOF_AUDIT_SHA = '0b71961a6c39f735a8ca6bcb4c294428e49021f05bcd02529e980a56b4fd62ed'
PROOF_COUNT = 122
REVIEWED_INPUTS = {'custody_v23.py': '91b5a4fc643000928c38ae0984bc3d255e9eb8251300fbd3985ab551a6479a57', 'coverage_v23.py': 'ae302daa13fe9703c5af4a42f9b867afc77af6809106ac2b439cba7d43b181cd', 'check_lean_v23.py': '9376b2f266b22695c4f4f932c3e13b1907eb94e476ede178fa71c3add6d6496b', 'FORMAL_SCOPE_V23.md': '5b5ec966ba1275d0462a34dea32a7928d544a013a961f4af618f2183bc87a606'}
QUALIFIED = ["GMI2-R2-003@r1", "GMI2-R2-007@r1"]
SOURCE_ASSUMPTIONS = 'actual V12 ordered commutative ring primitive laws and Int instance; fixed candidate admission and evaluator domain; actual V15/V17/V20 Context-decoder-attained-frontier construction; nonempty closed parameter interval; complete finite active roster for existence; root certificates conditional on actual affine equality, not root existence'

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
    spec = importlib.util.spec_from_file_location("v23_contract_" + path.stem, path)
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
    declarations = (("AffineDecodersV23.lean", "decoded_maximal_image"),
        ("AffineIntervalsV23.lean", "interval_le_iff"),
        ("AffineIntervalsV23.lean", "interval_lt_iff"),
        ("AffineWinnersV23.lean", "universal_winner"),
        ("AffineWinnersV23.lean", "universal_unique_explicit"))
    return [witness(root, "RESULT_V23.json", "json_pointer", "/atoms/" + atom),
            witness(root, "oracle_v23.py", "python_symbol", "verify_diagram")] + [
        witness(root, name, "lean_declaration", symbol) for name, symbol in declarations]


def repair(root, name):
    evidence = [witness(root, "check_regimes_v23.py", "python_symbol", "evaluate"),
                witness(root, "RESULT_V23.json", "json_pointer", "/kernel" if name == "R14" else "/coverage")]
    extras = {"R3": ("AffineWinnersV23.lean", "lean_declaration", "universal_winner"),
              "R14": ("proof_contract_v23.py", "python_symbol", "audit_source"),
              "R15": ("oracle_v23.py", "python_symbol", "verify_diagram")}
    evidence.insert(0, witness(root, *extras[name]))
    return {"id": name + "-affine-v23", "scope": REPAIR_SCOPES[name],
            "status": "LOCAL_VERIFIED", "evidence": evidence}


def validate_receipt(root, receipt):
    need(type(receipt) is dict and set(receipt) == {
        "schema", "tests_run", "kernel", "coverage", "source_bindings", "atoms", "inputs",
        "inherited_receipts", "amendment_carry", "registered_results", "overall_closure", "scientific_truth_certified",
        "claim_boundaries"}, "receipt fields")
    fixed = {"schema": "GMI_1068_AFFINE_REGIMES_V23", "tests_run": 12,
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
              if not entry["path"].endswith("/RESULT_V23.json")}
    exact(receipt["inputs"], inputs, "package input custody drift")
    package = root / PACKAGE
    for name, expected in REVIEWED_INPUTS.items():
        need(digest(package / name) == expected, "reviewed evaluator/input drift:" + name)
    custody = load(package / "custody_v23.py")
    try:
        expected_custody = custody.verify(root)
    except custody.CannotCheck as exc:
        raise OSError(str(exc)) from exc
    for key, value in expected_custody.items():
        exact(receipt[key], value, "inherited custody drift:" + key)
    exact(receipt["coverage"], load(package / "coverage_v23.py").REQUIRED, "coverage receipt drift")
    need(digest(package / "proof_contract_v23.py") == PROOF_CONTRACT_SHA, "reviewed proof-type drift")
    proof = load(package / "proof_contract_v23.py")
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
    return {"schema": "GMI_1068_CURRENT_ACCOUNTING_V23", "snapshot_content_sha256": snapshot_sha,
            "original_total": len(records), "original_fulfilled": fulfilled, "original_unresolved": unresolved,
            "qualified_replacements": len(originals), "qualified_original_ids": originals,
            "active_unresolved": unresolved - len(originals), "amendment_carry": amendment_carry,
            "overall_closure": "OPEN", "scientific_truth_certified": False}

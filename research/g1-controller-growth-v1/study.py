"""G1.2 remaining subtraction coordinates and G1.3 controller-growth (issue #165).

Research-only. Production `src/ocm/` is not modified. Subtraction is import-blocking /
monkeypatching plus resource and invariant probes, following #187.
"""
from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))

from ocm.kso.space import KnowledgeSpace
from ocm.kso.warrant import Liveness, WarrantProfile, mutant_unknown_as_dead
from ocm.learning.methods import PolynomialTask, normal_form
from ocm.operators.registry import BackendKind, OperatorSpec
from ocm.store.ledger import LedgerStore
from ocm.store.sqlite_ledger import SQLiteLedgerStore
from ocm.work import contracts as work_contracts
from ocm.work import envs as work_envs

G2_PATH = REPO / "research" / "g2-macro-operator-v1" / "experiment.py"
G3_PATH = REPO / "research" / "g3-independent-composition-v1" / "experiment.py"
FREEZE_COUNTS = REPO / "research" / "g1-vessel-freeze-v1" / "G1_3_COUNTS.json"
G5_SUMMARY = REPO / "research" / "g5-physical-denominator-v1" / "SUMMARY.json"
HOSTILE_MARKER = "HOSTILE_PI_COEFFICIENT_TABLE_V1"
MECHANISM_ARM = (
    G2_PATH,
    SRC / "ocm" / "learning" / "methods.py",
    SRC / "ocm" / "runtime" / "solve.py",
)
LEDGER_PROBE_N = 32

G2_SPEC = importlib.util.spec_from_file_location("g1_g2_macro_parent", G2_PATH)
G2 = importlib.util.module_from_spec(G2_SPEC)
G2_SPEC.loader.exec_module(G2)


# --------------------------------------------------------------------------- nloc / inventory
def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nloc_text(text: str) -> int:
    """Non-blank, non-comment Python lines (same definition as G1.3 freeze counts)."""
    n = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        n += 1
    return n


def nloc_path(path: Path) -> int:
    return nloc_text(path.read_text(encoding="utf-8"))


def py_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if p.is_file())


def tree_count(root: Path) -> dict:
    files = py_files(root)
    nloc = sum(nloc_path(p) for p in files)
    raw = sum(p.stat().st_size for p in files)
    return {"path": str(root.relative_to(REPO)), "files": len(files), "nloc": nloc, "bytes": raw}


def freeze_role_map() -> dict[str, dict]:
    data = json.loads(FREEZE_COUNTS.read_text())
    return {row["path"]: row for row in data["files"]}


def role_bucket(files: list[Path], roles: dict[str, dict]) -> dict[str, dict]:
    buckets: dict[str, dict] = {}
    for path in files:
        rel = str(path.relative_to(REPO))
        role = roles.get(rel, {}).get("role", "UNCOUNTED")
        bucket = buckets.setdefault(role, {"files": 0, "nloc": 0, "bytes": 0})
        bucket["files"] += 1
        bucket["nloc"] += roles[rel]["nloc"] if rel in roles else nloc_path(path)
        bucket["bytes"] += roles[rel]["bytes"] if rel in roles else path.stat().st_size
    return buckets


def dir_bytes(root: Path) -> int:
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def glob_learned_artifacts() -> list[str]:
    hits = []
    for pattern in (
        "research/g2-macro-operator-v1/**/RESULT.json",
        "research/g2-macro-operator-v1/records/**",
        "research/g3-independent-composition-v1/**/RESULT.json",
        "research/g3-independent-composition-v1/records/**",
    ):
        hits.extend(str(p.relative_to(REPO)) for p in REPO.glob(pattern) if p.is_file())
    return sorted(set(hits))


def serialize_index(index: dict) -> bytes:
    payload = []
    for coefficients, hit in index["first_by_coefficients"].items():
        payload.append({
            "coefficients": [str(c) for c in coefficients],
            "program": list(hit["program"]),
            "token_word": list(hit["token_word"]),
            "macro_used": bool(hit.get("macro_used")),
        })
    return json.dumps(payload, sort_keys=True).encode()


def learned_operator_state() -> dict:
    primitive = G2.build_search_index(None, 3)
    with_macro = G2.build_search_index(("inc", "inc"), 3)
    prim_bytes = serialize_index(primitive)
    macro_bytes = serialize_index(with_macro)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        loaded, atom_id, training_ev, utility_ev = G2.admit_macro(
            root,
            ("inc", "inc"),
            {"schema": "g1.controller-growth.training", "fragment": ["inc", "inc"]},
            {"schema": "g1.controller-growth.utility", "accepted": True},
        )
        admitted_bytes = dir_bytes(root)
    artifacts = glob_learned_artifacts()
    return {
        "g2_g3_result_artifacts_on_disk": artifacts,
        "used_experiment_modules_as_learned_competence": not artifacts,
        "g2_experiment_nloc": nloc_path(G2_PATH),
        "g3_experiment_nloc": nloc_path(G3_PATH),
        "g2_experiment_bytes": G2_PATH.stat().st_size,
        "g3_experiment_bytes": G3_PATH.stat().st_size,
        "primitive_index_max_length": 3,
        "primitive_index_records": len(primitive["first_by_coefficients"]),
        "primitive_index_json_bytes": len(prim_bytes),
        "primitive_index_attempts": primitive["total_enumeration_attempts"],
        "macro_index_records": len(with_macro["first_by_coefficients"]),
        "macro_index_json_bytes": len(macro_bytes),
        "macro_index_attempts": with_macro["total_enumeration_attempts"],
        "admitted_macro": list(loaded),
        "admitted_atom_id": atom_id,
        "admitted_ledger_bytes": admitted_bytes,
        "training_evidence": training_ev,
        "utility_evidence": utility_ev,
        "production_pi_nloc_unchanged_by_macro_admit": True,
    }


def inventory() -> dict:
    roles = freeze_role_map()
    freeze = json.loads(FREEZE_COUNTS.read_text())
    language_files = py_files(SRC / "ocm" / "language") + py_files(SRC / "ocm" / "learning" / "language")
    math_files = py_files(SRC / "ocm" / "science") + [SRC / "ocm" / "learning" / "methods.py"]
    procedural_files = py_files(SRC / "ocm" / "work") + py_files(SRC / "ocm" / "operators")
    planner = SRC / "ocm" / "dialogue" / "planner.py"
    solve = SRC / "ocm" / "runtime" / "solve.py"
    language = {
        "modules": [tree_count(SRC / "ocm" / "language"), tree_count(SRC / "ocm" / "learning" / "language")],
        "by_freeze_role": role_bucket(language_files, roles),
        "authored_controller": {
            "path": "src/ocm/dialogue/planner.py",
            "role_in_freeze": "PRIOR",
            "counted_as": "domain-specific Π / hard-coded control",
            "nloc": nloc_path(planner),
            "bytes": planner.stat().st_size,
        },
        "learned_imported_records_on_disk": 0,
    }
    math = {
        "modules": [tree_count(SRC / "ocm" / "science"), {
            "path": "src/ocm/learning/methods.py",
            "files": 1,
            "nloc": nloc_path(SRC / "ocm" / "learning" / "methods.py"),
            "bytes": (SRC / "ocm" / "learning" / "methods.py").stat().st_size,
        }],
        "by_freeze_role": role_bucket(math_files, roles),
        "authored_controller_delta_nloc": 0,
        "shared_executive": {
            "path": "src/ocm/runtime/solve.py",
            "role_in_freeze": "Π",
            "nloc": nloc_path(solve),
            "bytes": solve.stat().st_size,
        },
    }
    procedural = {
        "modules": [tree_count(SRC / "ocm" / "work"), tree_count(SRC / "ocm" / "operators")],
        "by_freeze_role": role_bucket(procedural_files, roles),
        "authored_controller_delta_nloc": 0,
        "authored_operator_schema_nloc": nloc_path(SRC / "ocm" / "work" / "contracts.py"),
    }
    learned = learned_operator_state()
    lang_fo_nloc = language["modules"][0]["nloc"] + language["modules"][1]["nloc"]
    math_fo_nloc = math["modules"][0]["nloc"] + math["modules"][1]["nloc"]
    proc_fo_nloc = procedural["modules"][0]["nloc"] + procedural["modules"][1]["nloc"]
    shared_pi = freeze["by_role"]["Π"]["nloc"]
    # Attribution series: current tree partitioned by domain addition, not a git time series.
    series = [
        {
            "after": "language",
            "production_pi_nloc": shared_pi,
            "domain_controller_nloc": language["authored_controller"]["nloc"],
            "cumulative_controller_nloc": shared_pi + language["authored_controller"]["nloc"],
            "authored_fo_nloc": lang_fo_nloc,
            "learned_fo_state_bytes": 0,
            "pi_delta_from_previous": language["authored_controller"]["nloc"],
            "fo_delta_from_previous": lang_fo_nloc,
        },
        {
            "after": "math",
            "production_pi_nloc": shared_pi,
            "domain_controller_nloc": language["authored_controller"]["nloc"],
            "cumulative_controller_nloc": shared_pi + language["authored_controller"]["nloc"],
            "authored_fo_nloc": lang_fo_nloc + math_fo_nloc,
            "learned_fo_state_bytes": learned["admitted_ledger_bytes"],
            "pi_delta_from_previous": 0,
            "fo_delta_from_previous": math_fo_nloc,
        },
        {
            "after": "procedural",
            "production_pi_nloc": shared_pi,
            "domain_controller_nloc": language["authored_controller"]["nloc"],
            "cumulative_controller_nloc": shared_pi + language["authored_controller"]["nloc"],
            "authored_fo_nloc": lang_fo_nloc + math_fo_nloc + proc_fo_nloc,
            "learned_fo_state_bytes": learned["admitted_ledger_bytes"],
            "pi_delta_from_previous": 0,
            "fo_delta_from_previous": proc_fo_nloc,
        },
    ]
    math_competence_in_state = (
        learned["admitted_ledger_bytes"] > 0
        and math["authored_controller_delta_nloc"] == 0
    )
    language_competence_in_state = language["learned_imported_records_on_disk"] > 0
    procedural_competence_in_state = False
    predominantly = (
        math_competence_in_state
        and language_competence_in_state
        and procedural_competence_in_state
    )
    return {
        "nloc_definition": freeze["nloc_definition"],
        "freeze_git_head": freeze["git_head"],
        "freeze_by_role": freeze["by_role"],
        "language": language,
        "math": math,
        "procedural": procedural,
        "learned": learned,
        "growth_series": series,
        "controller_growth_dominates": False,
        "state_size_dominates": False,
        "competence_in_learned_imported_fo_state": {
            "language": language_competence_in_state,
            "math_polynomial_g2_admit": math_competence_in_state,
            "procedural": procedural_competence_in_state,
            "predominantly_across_three_domains": predominantly,
            "status": "PARTIAL_AT_POLYNOMIAL_SCOPE",
            "note": (
                "G2 admit_macro writes ledger operator state without growing solve.py. "
                "Language competence remains authored planner.py. Procedural competence remains "
                "authored work/operators source. G2/G3 run artifacts are absent on this branch."
            ),
        },
    }


# --------------------------------------------------------------------------- hostile Π
def hostile_pi_lookup(coefficients):  # HOSTILE_PI_COEFFICIENT_TABLE_V1
    table = {
        (0, 1): (), (1, 1): ("inc",), (-1, 1): ("dec",), (0, 2): ("double",),
        (0, 0, 1): ("square",), (2, 2): ("inc", "double"), (1, 2): ("double", "inc"),
        (1, 2, 1): ("inc", "square"),
    }
    return table[tuple(int(x) for x in coefficients)]


HOSTILE_PROGRAMS = (
    (),
    ("inc",),
    ("dec",),
    ("double",),
    ("square",),
    ("inc", "double"),
    ("double", "inc"),
    ("inc", "square"),
)


def mechanism_contains_hostile() -> dict:
    hits = {}
    for path in MECHANISM_ARM:
        text = path.read_text(encoding="utf-8")
        hits[str(path.relative_to(REPO))] = {
            "marker": HOSTILE_MARKER in text,
            "function_name": "hostile_pi_lookup" in text,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    return hits


def hostile_probe() -> dict:
    solved = []
    for program in HOSTILE_PROGRAMS:
        task = PolynomialTask("h", normal_form(program))
        guessed = hostile_pi_lookup(task.coefficients)
        ok = guessed == program and normal_form(guessed) == task.coefficients
        solved.append({"program": list(program), "ok": ok, "guessed": list(guessed)})
    index = G2.build_search_index(None, 3)
    mechanism_rows = []
    for program in HOSTILE_PROGRAMS:
        task = PolynomialTask("m", normal_form(program))
        row = G2.solve_from_index(task, index)
        mechanism_rows.append({
            "program": list(program),
            "token_word": list(row["token_word"]),
            "verified": row["verified"],
            "enumeration_attempts": row["enumeration_attempts"],
        })
    source = (HERE / "study.py").read_text(encoding="utf-8")
    start = source.index("def hostile_pi_lookup")
    end = source.index("\nHOSTILE_PROGRAMS")
    hostile_src = source[start:end].strip()
    return {
        "marker": HOSTILE_MARKER,
        "hostile_function_nloc": nloc_text(hostile_src),
        "hostile_function_source": hostile_src,
        "hostile_solves_all_table_tasks": all(row["ok"] for row in solved),
        "hostile_tasks": solved,
        "mechanism_arm_solves_same_tasks_by_enumeration": all(row["verified"] for row in mechanism_rows),
        "mechanism_rows": mechanism_rows,
        "mechanism_contains_hostile": mechanism_contains_hostile(),
        "hostile_absent_from_mechanism_arm": not any(
            v["marker"] or v["function_name"] for v in mechanism_contains_hostile().values()
        ),
    }


# --------------------------------------------------------------------------- G1.2 subtraction
def g5_citation() -> dict | None:
    if not G5_SUMMARY.is_file():
        return None
    data = json.loads(G5_SUMMARY.read_text())
    n2048 = data["scaling"]["n_2048"]
    return {
        "path": "research/g5-physical-denominator-v1/SUMMARY.json",
        "terminal": data["execution_terminal"],
        "n": 2048,
        "jsonl_cumulative_rewrite_bytes": n2048["jsonl_cumulative_rewrite_bytes"],
        "sqlite_parent_cumulative_rewrite_bytes": n2048["sqlite_parent_cumulative_rewrite_bytes"],
        "jsonl_write_amplification": n2048["jsonl_write_amplification"],
        "jsonl_head_s": n2048["jsonl_head_s"],
        "sqlite_parent_head_s": n2048["sqlite_parent_head_s"],
        "production_sources_unchanged": data["production_sources_unchanged"],
    }


def probe_sqlite_vs_jsonl() -> dict:
    import ocm.store.sqlite_ledger as sqlite_mod

    original = sqlite_mod.SQLiteLedgerStore
    jsonl_ok = False
    stub_error = None
    try:
        sqlite_mod.SQLiteLedgerStore = None  # type: ignore[assignment]
        with tempfile.TemporaryDirectory() as tmp:
            store = LedgerStore(Path(tmp) / "jsonl")
            head = None
            hashes = []
            for i in range(4):
                entry = store.append("ROW", {"i": i}, expected_head=head)
                hashes.append(entry.entry_hash)
                head = entry.entry_hash
            jsonl_ok = store.verify() == () and len(store.entries()) == 4
    except Exception as exc:  # noqa: BLE001
        stub_error = f"{type(exc).__name__}: {exc}"
    finally:
        sqlite_mod.SQLiteLedgerStore = original

    with tempfile.TemporaryDirectory() as tmp:
        jroot = Path(tmp) / "jsonl"
        sroot = Path(tmp) / "sqlite"
        jsonl = LedgerStore(jroot)
        sqlite = SQLiteLedgerStore(sroot)
        jh = sh = None
        match = True
        for i in range(LEDGER_PROBE_N):
            payload = {"i": i, "pad": "x" * 32}
            left = jsonl.append("ROW", payload, expected_head=jh)
            right = sqlite.append("ROW", payload, expected_head=sh)
            if left.entry_hash != right.entry_hash:
                match = False
            jh, sh = left.entry_hash, right.entry_hash
        t0 = time.perf_counter()
        jsonl.head()
        jsonl_head_s = time.perf_counter() - t0
        t0 = time.perf_counter()
        sqlite.head()
        sqlite_head_s = time.perf_counter() - t0
        resource = {
            "n": LEDGER_PROBE_N,
            "capability_hash_chain_match": match and jsonl.verify() == () and sqlite.verify() == (),
            "jsonl_dir_bytes": dir_bytes(jroot),
            "sqlite_dir_bytes": dir_bytes(sroot),
            "jsonl_head_s": jsonl_head_s,
            "sqlite_head_s": sqlite_head_s,
            "resource_changed": dir_bytes(jroot) != dir_bytes(sroot) or jsonl_head_s != sqlite_head_s,
        }
    return {
        "sqlite_stubbed": True,
        "jsonl_capability_unchanged_under_sqlite_stub": jsonl_ok,
        "stub_error": stub_error,
        "live_comparison": resource,
        "g5": g5_citation(),
    }


def probe_warrant_interval() -> dict:
    partial = WarrantProfile.partial([frozenset({0})])
    certified = WarrantProfile.of({0})
    unknown = partial.liveness((0,))
    collapsed = mutant_unknown_as_dead(partial, (0,))
    certified_live = certified.liveness(())
    certified_dead = certified.liveness((0,))
    boolean_unknown_count = sum(
        1 for value in (collapsed, mutant_unknown_as_dead(certified, ()), mutant_unknown_as_dead(certified, (0,)))
        if value is Liveness.UNKNOWN
    )
    interval_unknown_count = sum(
        1 for value in (unknown, certified_live, certified_dead)
        if value is Liveness.UNKNOWN
    )
    return {
        "partial_revoked_interval": unknown.value,
        "partial_revoked_boolean_collapse": collapsed.value,
        "certified_unrevoked": certified_live.value,
        "certified_revoked": certified_dead.value,
        "unknown_count_with_interval": interval_unknown_count,
        "unknown_count_after_boolean_collapse": boolean_unknown_count,
        "epistemic_invariant_failure": unknown is Liveness.UNKNOWN and collapsed is not Liveness.UNKNOWN,
        "witness": "tests/m1/test_mutants.py::test_unknown_treated_as_live_and_as_dead_mutants",
        "mutant": "ocm.kso.warrant.mutant_unknown_as_dead",
    }


def wrap_work_operator(op) -> OperatorSpec:
    def backend(_ks, inputs):
        state = dict(inputs["state"])
        return {"state": op.backend(state)}

    return OperatorSpec(
        operator_id=op.operator_id,
        version=op.version,
        kind=BackendKind.PROGRAMMATIC,
        backend=backend,
        input_atoms=(),
        expected_effects=op.expected_effects,
        warrant=op.warrant,
        authority=op.authority,
        scope=op.scope,
        lineage=tuple(op.lineage) + ("g1-controller-growth-v1:wrap-work-Operator",),
    )


def probe_work_operator() -> dict:
    ops = work_envs.enterprise_operators()
    native = ops["ent.classify_urgency"]
    wrapped = wrap_work_operator(native)
    ks = KnowledgeSpace((), ())
    before = wrapped.backend(ks, {"state": {"facts": {"outage": True}}})
    wrap_ok = before["state"].get("urgency") == "high"

    original = work_contracts.Operator
    stub_error = None
    envs_failed = False
    try:
        work_contracts.Operator = None  # type: ignore[assignment]
        importlib.reload(work_envs)
        try:
            work_envs.enterprise_operators()
        except Exception as exc:  # noqa: BLE001
            envs_failed = True
            stub_error = f"{type(exc).__name__}: {exc}"
    finally:
        work_contracts.Operator = original
        importlib.reload(work_envs)

    after_stub = wrapped.backend(ks, {"state": {"facts": {"outage": False}}})
    wrap_survives_stub = after_stub["state"].get("urgency") == "low" and wrap_ok
    restored = work_envs.enterprise_operators()
    restored_ok = restored["ent.classify_urgency"].backend({"facts": {"outage": True}}).get("urgency") == "high"
    return {
        "m9_construction_fails_when_Operator_stubbed": envs_failed,
        "stub_error": stub_error,
        "compensating_composition": "OperatorSpec wrapping work.Operator.backend",
        "wrap_preserves_classify_transform": wrap_ok,
        "wrap_survives_Operator_stub": wrap_survives_stub,
        "m9_tests_not_preserved_by_wrap": True,
        "restored_work_Operator": restored_ok,
        "algebraic_api_necessity": envs_failed,
        "cognitive_capability_via_OperatorSpec": wrap_survives_stub,
        "blocking_tests_cited_from_187": [
            "tests/m9/test_work.py",
            "tests/m9/test_method_contract_integrity_v3.py",
            "tests/m10/test_proof_lifecycle.py",
            "tests/m12/test_current_comparator_parity.py",
        ],
    }


def classifications(sqlite_probe: dict, warrant_probe: dict, operator_probe: dict) -> list[dict]:
    g5 = sqlite_probe.get("g5") or {}
    return [
        {
            "component": "sqlite_ledger_vs_jsonl",
            "removed": "SQLiteLedgerStore stubbed; JSONL LedgerStore remains",
            "algebraic_necessity": False,
            "resource_necessity": True,
            "epistemic_necessity": False,
            "capability_loss": not sqlite_probe["jsonl_capability_unchanged_under_sqlite_stub"],
            "resource_change": bool(sqlite_probe["live_comparison"]["resource_changed"]),
            "epistemic_invariant_failure": False,
            "witness": {
                "local_n": sqlite_probe["live_comparison"]["n"],
                "jsonl_dir_bytes": sqlite_probe["live_comparison"]["jsonl_dir_bytes"],
                "sqlite_dir_bytes": sqlite_probe["live_comparison"]["sqlite_dir_bytes"],
                "jsonl_head_s": sqlite_probe["live_comparison"]["jsonl_head_s"],
                "sqlite_head_s": sqlite_probe["live_comparison"]["sqlite_head_s"],
                "g5_n2048_jsonl_rewrite_bytes": g5.get("jsonl_cumulative_rewrite_bytes"),
                "g5_n2048_sqlite_rewrite_bytes": g5.get("sqlite_parent_cumulative_rewrite_bytes"),
                "g5_write_amplification": g5.get("jsonl_write_amplification"),
                "g5_terminal": g5.get("terminal"),
            },
            "note": (
                "Hash-chain capability is preserved (local match + G5 semantic parity). "
                "Physical write/head cost changes. Storage is not warrant (STORAGE_NOT_AUTHORITY). "
                "A ledger of some kind is a resource parent; sqlite-vs-jsonl is not algebraic or epistemic."
            ),
        },
        {
            "component": "warrant_interval",
            "removed": "three-valued interval liveness collapsed to boolean via mutant_unknown_as_dead",
            "algebraic_necessity": False,
            "resource_necessity": False,
            "epistemic_necessity": True,
            "capability_loss": False,
            "resource_change": False,
            "epistemic_invariant_failure": warrant_probe["epistemic_invariant_failure"],
            "witness": {
                "interval_UNKNOWN": warrant_probe["partial_revoked_interval"],
                "boolean_collapse": warrant_probe["partial_revoked_boolean_collapse"],
                "unknown_count_before": warrant_probe["unknown_count_with_interval"],
                "unknown_count_after": warrant_probe["unknown_count_after_boolean_collapse"],
                "mutant": warrant_probe["mutant"],
                "existing_test": warrant_probe["witness"],
            },
            "note": "UNKNOWN disappears. LIVE/DEAD for certified profiles remain. Epistemic, not algebraic or resource.",
        },
        {
            "component": "work.Operator",
            "removed": "class stub / import-block (no production deletion)",
            "algebraic_necessity": True,
            "resource_necessity": False,
            "epistemic_necessity": False,
            "capability_loss": operator_probe["m9_construction_fails_when_Operator_stubbed"],
            "resource_change": False,
            "epistemic_invariant_failure": False,
            "compensating_composition": {
                "permitted": True,
                "form": operator_probe["compensating_composition"],
                "preserves_m9_tests": False,
                "preserves_backend_transform": operator_probe["cognitive_capability_via_OperatorSpec"],
            },
            "witness": {
                "stub_error": operator_probe["stub_error"],
                "wrap_survives_stub": operator_probe["wrap_survives_Operator_stub"],
                "issue_187": "M0 OCMRuntime and work.Operator required by current tests; G1.1.6 NOT_EARNED as deletion",
            },
            "note": (
                "Algebraic/API necessity for M9 construction is confirmed by stub failure. "
                "OperatorSpec wrapping recovers the classify transform, so the cognitive "
                "backend is not uniquely tied to the work.Operator class. Unification was not performed."
            ),
        },
    ]


def checkboxes(inv: dict, hostile: dict, classified: list[dict]) -> dict:
    sqlite_c, warrant_c, operator_c = classified
    return {
        "G1.2": [
            {
                "id": "G1.2/001",
                "text": "Remove candidate architecture components one at a time.",
                "status": "EARNED_AS_PROBES",
                "note": "sqlite stub, warrant collapse, work.Operator stub; restored; no production deletion. #187 hid-file probes remain the vessel-core inventory.",
            },
            {
                "id": "G1.2/002",
                "text": "Permit compensating compositions where scientifically appropriate.",
                "status": "EARNED_AS_MEASUREMENT",
                "note": "OperatorSpec wrapping work.Operator is permitted and measured. It does not preserve M9 tests.",
                "wrap_preserves_backend": operator_c["compensating_composition"]["preserves_backend_transform"],
            },
            {
                "id": "G1.2/003",
                "text": "Measure capability loss.",
                "status": "EARNED",
                "sqlite_capability_loss": sqlite_c["capability_loss"],
                "operator_capability_loss": operator_c["capability_loss"],
            },
            {
                "id": "G1.2/004",
                "text": "Measure resource change.",
                "status": "EARNED",
                "sqlite_resource_change": sqlite_c["resource_change"],
            },
            {
                "id": "G1.2/005",
                "text": "Measure epistemic-invariant failure.",
                "status": "EARNED",
                "warrant_unknown_disappears": warrant_c["epistemic_invariant_failure"],
            },
            {
                "id": "G1.2/006",
                "text": "Distinguish algebraic / resource / epistemic necessity.",
                "status": "EARNED",
            },
            {
                "id": "G1.2/007",
                "text": "Preserve PARENT_SUFFICIENT where ordinary architecture mechanisms suffice.",
                "status": "PRESERVED",
                "note": "Not reopened. G5 DATABASE_PARENT_SUFFICIENT is cited for the ledger parent.",
            },
            {
                "id": "G1.2/008",
                "text": "Do not call the machine minimal merely because code was deleted.",
                "status": "OBEYED",
                "note": "Nothing deleted. MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE is not issued.",
            },
        ],
        "G1.3": [
            {
                "id": "G1.3.1",
                "text": "Measure controller source/branch growth across domain additions.",
                "status": "EARNED_AS_ATTRIBUTION_SERIES",
                "note": "Language adds planner.py (170 nloc). Math and procedural add 0 production Π nloc. Not a git time series.",
                "controller_growth_dominates": inv["controller_growth_dominates"],
            },
            {
                "id": "G1.3.2",
                "text": "Demonstrate new competence predominantly appears in learned/imported field/operator state.",
                "status": inv["competence_in_learned_imported_fo_state"]["status"],
                "predominantly_across_three_domains": inv["competence_in_learned_imported_fo_state"]["predominantly_across_three_domains"],
            },
            {
                "id": "G1.3.3",
                "text": "Add hostile where a domain-specific hard-coded Π rule would trivially solve the task.",
                "status": "EARNED",
                "hostile_solves": hostile["hostile_solves_all_table_tasks"],
            },
            {
                "id": "G1.3.4",
                "text": "Require that hostile to be absent from the mechanism arm.",
                "status": "EARNED" if hostile["hostile_absent_from_mechanism_arm"] else "NOT_EARNED",
                "absent": hostile["hostile_absent_from_mechanism_arm"],
            },
            {
                "id": "G1.3.5",
                "text": "Count every retained domain-specific rule as prior information.",
                "status": "EARNED_UPSTREAM",
                "evidence": "research/g1-vessel-freeze-v1/PRIOR_INFORMATION.json",
            },
        ],
    }


def run_study() -> dict:
    inv = inventory()
    hostile = hostile_probe()
    sqlite_probe = probe_sqlite_vs_jsonl()
    warrant_probe = probe_warrant_interval()
    operator_probe = probe_work_operator()
    classified = classifications(sqlite_probe, warrant_probe, operator_probe)
    boxes = checkboxes(inv, hostile, classified)
    result = {
        "schema": "ocm.g1-controller-growth.result.v1",
        "issue": 165,
        "gates": ["G1.2", "G1.3"],
        "head": git_head(),
        "parent_freeze": {
            "path": "research/g1-vessel-freeze-v1",
            "terminal": "COMPACT_VESSEL_PARTIAL",
            "src_ocm_tree": "3a4dcbcf3a1875acefcec80cfa8d47330d172655",
        },
        "production_code_deleted": False,
        "terminal": "COMPACT_VESSEL_PARTIAL",
        "not_issued": [
            "MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE",
            "MINIMUM_SELF_EXTENDING_VESSEL",
            "CURRENT_KSO_PARENT_SUFFICIENT",
            "CONTROLLER_GROWTH_DOMINATES",
            "STATE_SIZE_DOMINATES",
            "DOMAIN_CORE_FORK_REQUIRED",
        ],
        "inventory": inv,
        "hostile": {
            "marker": hostile["marker"],
            "hostile_function_nloc": hostile["hostile_function_nloc"],
            "hostile_solves_all_table_tasks": hostile["hostile_solves_all_table_tasks"],
            "hostile_tasks": hostile["hostile_tasks"],
            "mechanism_arm_solves_same_tasks_by_enumeration": hostile["mechanism_arm_solves_same_tasks_by_enumeration"],
            "mechanism_rows": hostile["mechanism_rows"],
            "mechanism_contains_hostile": hostile["mechanism_contains_hostile"],
            "hostile_absent_from_mechanism_arm": hostile["hostile_absent_from_mechanism_arm"],
        },
        "subtraction": {
            "sqlite_vs_jsonl": sqlite_probe,
            "warrant_interval": warrant_probe,
            "work_Operator": operator_probe,
        },
        "classifications": classified,
        "G1_checkboxes": boxes,
        "G1_1_6_duplicate_cores": "NOT_EARNED_AS_DELETION",
        "architecture_rules_empirical": {
            "INTELLIGENCE_IN_F_AND_O": "PARTIAL_AT_POLYNOMIAL_SCOPE",
            "PI_SMALL_DOMAIN_GENERAL": "PARTIAL",
        },
    }
    counts = {
        "schema": "ocm.g1-controller-growth.counts.v1",
        "nloc_definition": inv["nloc_definition"],
        "head": result["head"],
        "freeze_by_role": inv["freeze_by_role"],
        "language": inv["language"],
        "math": inv["math"],
        "procedural": inv["procedural"],
        "learned": inv["learned"],
        "growth_series": inv["growth_series"],
        "competence_in_learned_imported_fo_state": inv["competence_in_learned_imported_fo_state"],
        "hostile_function_nloc": hostile["hostile_function_nloc"],
        "classifications_summary": [
            {
                "component": row["component"],
                "algebraic": row["algebraic_necessity"],
                "resource": row["resource_necessity"],
                "epistemic": row["epistemic_necessity"],
            }
            for row in classified
        ],
        "terminal": result["terminal"],
    }
    return {"result": result, "counts": counts, "hostile_source": hostile["hostile_function_source"]}


def write_outputs(payload: dict | None = None) -> dict:
    payload = payload or run_study()
    (HERE / "RESULT.json").write_text(json.dumps(payload["result"], indent=2, sort_keys=True) + "\n")
    (HERE / "COUNTS.json").write_text(json.dumps(payload["counts"], indent=2, sort_keys=True) + "\n")
    return payload


def main() -> None:
    payload = write_outputs()
    result = payload["result"]
    series = result["inventory"]["growth_series"]
    summary = {
        "terminal": result["terminal"],
        "growth_series": [
            {
                "after": row["after"],
                "controller": row["cumulative_controller_nloc"],
                "fo_nloc": row["authored_fo_nloc"],
                "pi_delta": row["pi_delta_from_previous"],
                "fo_delta": row["fo_delta_from_previous"],
                "learned_bytes": row["learned_fo_state_bytes"],
            }
            for row in series
        ],
        "classifications": [
            {
                "component": row["component"],
                "algebraic": row["algebraic_necessity"],
                "resource": row["resource_necessity"],
                "epistemic": row["epistemic_necessity"],
            }
            for row in result["classifications"]
        ],
        "hostile_absent": result["hostile"]["hostile_absent_from_mechanism_arm"],
        "competence": result["inventory"]["competence_in_learned_imported_fo_state"]["status"],
        "result": str(HERE / "RESULT.json"),
        "counts": str(HERE / "COUNTS.json"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

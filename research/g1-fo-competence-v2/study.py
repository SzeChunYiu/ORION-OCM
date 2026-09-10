"""G1.3.2 v2: new competence in ledger F/O state at polynomial + L1 microworld.

Research-only. Production `src/ocm/` is not modified. Hostile Π table lives here.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))

from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.learning.methods import PolynomialTask, normal_form
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

G2_PATH = REPO / "research" / "g2-macro-operator-v1" / "experiment.py"
L1_PATH = REPO / "research" / "l1-linguistic-g2-v1" / "experiment.py"
HOSTILE_MARKER = "HOSTILE_PI_COEFFICIENT_TABLE_V1"
MECHANISM_ARM = (
    G2_PATH,
    L1_PATH,
    SRC / "ocm" / "learning" / "methods.py",
    SRC / "ocm" / "runtime" / "solve.py",
    SRC / "ocm" / "dialogue" / "planner.py",
)
SOLVE = SRC / "ocm" / "runtime" / "solve.py"
PLANNER = SRC / "ocm" / "dialogue" / "planner.py"
L1_SCOPE = Scope.of("l1-microworld.v1")
PARENT_V1 = REPO / "research" / "g1-controller-growth-v1" / "RESULT.json"

G2_SPEC = importlib.util.spec_from_file_location("g1_fo_g2_parent", G2_PATH)
G2 = importlib.util.module_from_spec(G2_SPEC)
sys.modules[G2_SPEC.name] = G2
G2_SPEC.loader.exec_module(G2)

L1_SPEC = importlib.util.spec_from_file_location("g1_fo_l1_parent", L1_PATH)
L1 = importlib.util.module_from_spec(L1_SPEC)
sys.modules[L1_SPEC.name] = L1
L1_SPEC.loader.exec_module(L1)


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nloc_text(text: str) -> int:
    n = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        n += 1
    return n


def nloc_path(path: Path) -> int:
    return nloc_text(path.read_text(encoding="utf-8"))


def dir_bytes(root: Path) -> int:
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def live_procedures(runtime: OCMRuntime) -> list[str]:
    revoked = runtime.state.revoked
    out = []
    for atom in runtime.state.ks.atoms:
        if atom.atom_type == "procedure" and atom.liveness(revoked) is Liveness.LIVE:
            out.append(atom.atom_id)
    return sorted(out)


def admit_l1_construction(root: Path) -> dict:
    train_pairs = [(a, n) for a in L1.TRAIN_ADJ for n in L1.TRAIN_NOUN]
    runtime = OCMRuntime(root)
    lesson_ids = []
    for adj, noun in train_pairs:
        _rec, eid = runtime.admit_evidence(
            {"schema": "g1.fo-competence.l1-lesson", "adj": adj, "noun": noun},
            Channel.OBSERVATION,
            "l1-adj-noun.v1",
            scope=L1_SCOPE,
        )
        lesson_ids.append(eid)
    warrant = WarrantProfile.of(set(lesson_ids))
    source_payload = {
        "kind": "l1.construction.support.v1",
        "lessons": [content_hash({"adj": a, "noun": n}) for a, n in train_pairs],
    }
    source_id = "l1-construction-support:" + content_hash(source_payload)
    runtime.admit_object(
        Atom(
            source_id,
            "proof",
            warrant,
            scope=L1_SCOPE,
            quarantined=True,
            content_ref=content_hash(source_payload),
            meta=tuple(source_payload.items()),
        ),
        (),
        "OBSERVATION",
    )
    payload = {
        "kind": "l1.construction.v1",
        "construction_id": "adj-noun-intersective.v1",
        "pattern": ["ADJ", "NOUN"],
        "fingerprint": content_hash({"id": "adj-noun-intersective.v1", "pattern": ["ADJ", "NOUN"]}),
    }
    atom_id = "l1-construction:" + content_hash(payload)
    edge = Hyperedge("support:" + atom_id, (source_id,), (atom_id,), "SUPPORT", warrant=warrant)
    runtime.admit_object(
        Atom(
            atom_id,
            "procedure",
            warrant,
            scope=L1_SCOPE,
            content_ref=content_hash(payload),
            meta=tuple(payload.items()),
        ),
        (edge,),
        "OBSERVATION",
    )
    runtime.persist()
    replay = OCMRuntime(root)
    atom = replay.state.ks.atom_map().get(atom_id)
    if atom is None or atom.liveness(replay.state.revoked) is not Liveness.LIVE:
        raise RuntimeError("L1 construction did not survive restart")
    stored = dict(atom.meta)
    if atom.content_ref != content_hash(stored):
        raise RuntimeError("L1 construction content identity mismatch")
    skill = L1.ConstructionSkill(stored["construction_id"], tuple(stored["pattern"]), tuple(lesson_ids), tuple(lesson_ids))
    words = {
        **{w: (L1.Category.ADJ, w) for w in L1.TRAIN_ADJ + L1.HELD_ADJ},
        **{w: (L1.Category.NOUN, w) for w in L1.TRAIN_NOUN + L1.HELD_NOUN},
        **{w: (L1.Category.DET, w) for w in L1.NUMBERS},
    }
    lex = L1.teach_lexicon(words)
    fresh = [(a, n) for a in L1.HELD_ADJ for n in L1.HELD_NOUN]
    fresh += [(L1.TRAIN_ADJ[0], L1.HELD_NOUN[0]), (L1.HELD_ADJ[0], L1.TRAIN_NOUN[0])]
    invoked_rows = []
    for pair in fresh:
        rec = L1.parse_with_skill(pair, skill, lex, set())
        invoked_rows.append({"tokens": list(pair), "invoked": rec["invoked"], "status": rec["status"]})
    reset_rows = [L1.parse_with_skill(pair, None, lex, set()) for pair in fresh]
    return {
        "atom_id": atom_id,
        "lesson_evidence": lesson_ids,
        "held_out_invoked": all(r["invoked"] for r in invoked_rows),
        "reset_has_no_construction": all(not r["invoked"] for r in reset_rows),
        "held_out_rows": invoked_rows,
        "live_after_restart": True,
        "construction_id": stored["construction_id"],
    }


def measure_microworld() -> dict:
    solve_before = nloc_path(SOLVE)
    planner_before = nloc_path(PLANNER)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "ledger"
        root.mkdir()
        bytes_empty = dir_bytes(root)
        loaded, atom_id, training_ev, utility_ev = G2.admit_macro(
            root,
            ("inc", "inc"),
            {"schema": "g1.fo-competence.training", "fragment": ["inc", "inc"]},
            {"schema": "g1.fo-competence.utility", "accepted": True},
        )
        after_g2 = OCMRuntime(root)
        bytes_after_g2 = dir_bytes(root)
        procs_after_g2 = live_procedures(after_g2)
        l1 = admit_l1_construction(root)
        after_both = OCMRuntime(root)
        bytes_after_both = dir_bytes(root)
        procs_after_both = live_procedures(after_both)
        macro_live = atom_id in procs_after_both
        l1_live = l1["atom_id"] in procs_after_both
        solve_after = nloc_path(SOLVE)
        planner_after = nloc_path(PLANNER)
        return {
            "solve_nloc_before": solve_before,
            "solve_nloc_after": solve_after,
            "planner_nloc_before": planner_before,
            "planner_nloc_after": planner_after,
            "solve_nloc_constant": solve_before == solve_after,
            "planner_nloc_constant": planner_before == planner_after,
            "admitted_macro": list(loaded),
            "macro_atom_id": atom_id,
            "macro_training_evidence": training_ev,
            "macro_utility_evidence": utility_ev,
            "macro_live_after_both_admits": macro_live,
            "l1": l1,
            "l1_live_after_both_admits": l1_live,
            "ledger_bytes_empty": bytes_empty,
            "ledger_bytes_after_g2": bytes_after_g2,
            "ledger_bytes_after_g2_and_l1": bytes_after_both,
            "fo_delta_bytes": bytes_after_both - bytes_empty,
            "g2_delta_bytes": bytes_after_g2 - bytes_empty,
            "l1_delta_bytes": bytes_after_both - bytes_after_g2,
            "live_procedure_atoms_after_g2": procs_after_g2,
            "live_procedure_atoms_after_both": procs_after_both,
            "new_competence_in_fo_state": (
                bytes_after_both > bytes_after_g2 > bytes_empty
                and macro_live
                and l1_live
                and l1["held_out_invoked"]
                and l1["reset_has_no_construction"]
                and solve_before == solve_after
                and planner_before == planner_after
            ),
        }


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
    contains = mechanism_contains_hostile()
    source = (HERE / "study.py").read_text(encoding="utf-8")
    start = source.index("def hostile_pi_lookup")
    end = source.index("\nHOSTILE_PROGRAMS")
    hostile_src = source[start:end].strip()
    return {
        "marker": HOSTILE_MARKER,
        "hostile_function_nloc": nloc_text(hostile_src),
        "hostile_solves_all_table_tasks": all(row["ok"] for row in solved),
        "hostile_tasks": solved,
        "mechanism_contains_hostile": contains,
        "hostile_absent_from_mechanism_arm": not any(
            v["marker"] or v["function_name"] for v in contains.values()
        ),
    }


def parent_v1_citation() -> dict:
    if not PARENT_V1.is_file():
        return {"path": str(PARENT_V1.relative_to(REPO)), "present": False}
    data = json.loads(PARENT_V1.read_text())
    g132 = next(row for row in data["G1_checkboxes"]["G1.3"] if row["id"] == "G1.3.2")
    return {
        "path": str(PARENT_V1.relative_to(REPO)),
        "present": True,
        "terminal": data["terminal"],
        "G1_3_2_status": g132["status"],
        "predominantly_across_three_domains": g132.get("predominantly_across_three_domains"),
        "not_rewritten": True,
    }


def run_study() -> dict:
    world = measure_microworld()
    hostile = hostile_probe()
    parent = parent_v1_citation()
    micro_ok = world["new_competence_in_fo_state"] and hostile["hostile_absent_from_mechanism_arm"]
    terminal = "COMPETENCE_IN_FO_STATE_AT_MICRO_SCOPE" if micro_ok else "PARTIAL_AT_MICRO_SCOPE"
    result = {
        "schema": "ocm.g1-fo-competence.result.v2",
        "issue": 165,
        "gates": ["G1.3.2"],
        "head": git_head(),
        "parent_v1": parent,
        "production_code_deleted": False,
        "terminal": terminal,
        "not_issued": [
            "MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE",
            "MINIMUM_SELF_EXTENDING_VESSEL",
            "CONTROLLER_GROWTH_DOMINATES",
            "STATE_SIZE_DOMINATES",
            "DOMAIN_CORE_FORK_REQUIRED",
        ],
        "microworld": world,
        "hostile": hostile,
        "G1_checkboxes": {
            "G1.3": [
                {
                    "id": "G1.3.2",
                    "text": "Demonstrate new competence predominantly appears in learned/imported field/operator state.",
                    "status": "EARNED_AT_MICRO_SCOPE" if micro_ok else "PARTIAL_AT_MICRO_SCOPE",
                    "predominantly_across_three_domains": False,
                    "polynomial_g2_admit": world["macro_live_after_both_admits"],
                    "l1_construction_admit": world["l1_live_after_both_admits"],
                    "procedural": False,
                    "solve_planner_nloc_constant": world["solve_nloc_constant"] and world["planner_nloc_constant"],
                    "fo_delta_bytes": world["fo_delta_bytes"],
                    "note": (
                        "Polynomial G2 macro + L1 Adj-Noun construction land in ledger F/O "
                        "procedure atoms. solve.py and planner.py nloc stay constant. "
                        "Procedural competence remains authored work/operators. Not three-domain predominance."
                    ),
                },
                {
                    "id": "G1.3.3",
                    "text": "Add hostile where a domain-specific hard-coded Π rule would trivially solve the task.",
                    "status": "EARNED" if hostile["hostile_solves_all_table_tasks"] else "NOT_EARNED",
                    "hostile_solves": hostile["hostile_solves_all_table_tasks"],
                },
                {
                    "id": "G1.3.4",
                    "text": "Require that hostile to be absent from the mechanism arm.",
                    "status": "EARNED" if hostile["hostile_absent_from_mechanism_arm"] else "NOT_EARNED",
                    "absent": hostile["hostile_absent_from_mechanism_arm"],
                },
            ]
        },
        "architecture_rules_empirical": {
            "INTELLIGENCE_IN_F_AND_O": "EARNED_AT_POLYNOMIAL_AND_L1_MICRO_SCOPE" if micro_ok else "PARTIAL_AT_MICRO_SCOPE",
            "PI_SMALL_DOMAIN_GENERAL": "PARTIAL",
        },
        "claim_ceiling": (
            "New competence after G2 macro admit + L1 construction admit appears in ledger "
            "F/O state bytes at this microworld, with constant solve.py/planner.py nloc. "
            "Not MINIMUM_SELF_EXTENDING_VESSEL. Procedural domain still authored."
        ),
    }
    return result


def write_outputs(payload: dict | None = None) -> dict:
    payload = payload or run_study()
    (HERE / "RESULT.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    summary = {
        "schema": "ocm.g1-fo-competence.summary.v2",
        "terminal": payload["terminal"],
        "solve_nloc": payload["microworld"]["solve_nloc_after"],
        "planner_nloc": payload["microworld"]["planner_nloc_after"],
        "fo_delta_bytes": payload["microworld"]["fo_delta_bytes"],
        "g2_delta_bytes": payload["microworld"]["g2_delta_bytes"],
        "l1_delta_bytes": payload["microworld"]["l1_delta_bytes"],
        "G1_3_2": payload["G1_checkboxes"]["G1.3"][0]["status"],
        "hostile_absent": payload["hostile"]["hostile_absent_from_mechanism_arm"],
        "not_issued": payload["not_issued"],
    }
    (HERE / "SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return payload


def main() -> None:
    result = write_outputs()
    print(json.dumps({
        "terminal": result["terminal"],
        "G1_3_2": result["G1_checkboxes"]["G1.3"][0]["status"],
        "fo_delta_bytes": result["microworld"]["fo_delta_bytes"],
        "solve_nloc": result["microworld"]["solve_nloc_after"],
        "planner_nloc": result["microworld"]["planner_nloc_after"],
        "hostile_absent": result["hostile"]["hostile_absent_from_mechanism_arm"],
        "not_issued_minimum_vessel": "MINIMUM_SELF_EXTENDING_VESSEL" in result["not_issued"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

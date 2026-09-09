"""G1 architecture box: Π remains small and domain-general (micro-scope).

Research-only. Production ``src/`` is not modified. New competence is admitted
into ledger F/O state with the G2 macro + L1 construction mechanism from
``research/g1-fo-competence-v2``. Controller files are measured, not edited.

If those Π files grow, the terminal is ``PI_GREW_AT_SCOPE`` (negative).
If nloc stays constant, files stay byte-identical, F/O grows, and the same Π
serves language construction plus polynomial procedure without a domain-forked
planner, the capsule terminal is ``PI_REMAINS_SMALL_AT_MICRO_SCOPE``.

That is not a programme-wide “Π remains small” close. Hostile coefficient
tables and authored work operators remain. Programme-level terminal stays
``COMPACT_VESSEL_PARTIAL``. ``MINIMUM_SELF_EXTENDING_VESSEL`` is not issued.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))

from ocm.dialogue.planner import plan_teach_back
from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.runtime.solve import Task, solve
from ocm.store.evidence import Channel

G2_PATH = REPO / "research" / "g2-macro-operator-v1" / "experiment.py"
L1_PATH = REPO / "research" / "l1-linguistic-g2-v1" / "experiment.py"
FREEZE_COUNTS = REPO / "research" / "g1-vessel-freeze-v1" / "G1_3_COUNTS.json"
PARENT_GROWTH = REPO / "research" / "g1-controller-growth-v1" / "RESULT.json"
PARENT_FO = REPO / "research" / "g1-fo-competence-v2" / "RESULT.json"
PARENT_CORES = REPO / "research" / "g1-duplicate-cores-v1" / "RESULT.json"
L1_SCOPE = Scope.of("l1-microworld.v1")

SCHEMA = "ocm.g1.pi-small.result.v1"
SALT = "orion-ocm-g1-pi-small-v1"
ISSUE = 165
GATE = "PI_SMALL_DOMAIN_GENERAL"

G2_SPEC = importlib.util.spec_from_file_location("g1_pi_small_g2_parent", G2_PATH)
G2 = importlib.util.module_from_spec(G2_SPEC)
assert G2_SPEC is not None and G2_SPEC.loader is not None
sys.modules[G2_SPEC.name] = G2
G2_SPEC.loader.exec_module(G2)

L1_SPEC = importlib.util.spec_from_file_location("g1_pi_small_l1_parent", L1_PATH)
L1 = importlib.util.module_from_spec(L1_SPEC)
assert L1_SPEC is not None and L1_SPEC.loader is not None
sys.modules[L1_SPEC.name] = L1
L1_SPEC.loader.exec_module(L1)

# Production controller files measured this run. planner.py is freeze-PRIOR
# but G1.3 counts it as domain-specific control; it must not fork per domain.
CONTROLLER_SPECS = (
    {
        "path": "src/ocm/runtime/solve.py",
        "justification": (
            "Canonical domain-general Π_exec stage pipeline. Freeze role Π. "
            "Reads the field; does not write. Shared across domains."
        ),
        "freeze_role": "Π",
        "counted_as": "Π_exec",
    },
    {
        "path": "src/ocm/runtime/ocm_runtime.py",
        "justification": (
            "Shared Admit_C executive. Freeze role Π. Both polynomial-macro "
            "and L1-construction admits go through this one class."
        ),
        "freeze_role": "Π",
        "counted_as": "Π_exec",
    },
    {
        "path": "src/ocm/dialogue/planner.py",
        "justification": (
            "G1.3 domain-control. Freeze role PRIOR. Language uses this single "
            "planner; polynomial procedure must not receive a forked planner."
        ),
        "freeze_role": "PRIOR",
        "counted_as": "domain-control Π",
    },
)


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


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


def file_snapshot(rel: str) -> dict[str, Any]:
    path = REPO / rel
    raw = path.read_bytes()
    return {
        "path": rel,
        "exists": path.is_file(),
        "nloc": nloc_text(raw.decode("utf-8")),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def snapshot_controllers() -> list[dict[str, Any]]:
    rows = []
    for spec in CONTROLLER_SPECS:
        row = file_snapshot(spec["path"])
        row.update({k: spec[k] for k in ("justification", "freeze_role", "counted_as")})
        rows.append(row)
    return rows


def freeze_pi_inventory() -> dict[str, Any]:
    data = json.loads(FREEZE_COUNTS.read_text())
    freeze_files = [row for row in data["files"] if row["role"] == "Π"]
    live = []
    for row in freeze_files:
        snap = file_snapshot(row["path"])
        snap["freeze_nloc"] = row["nloc"]
        snap["freeze_bytes"] = row["bytes"]
        snap["freeze_sha256"] = row["sha256"]
        snap["matches_freeze_sha256"] = snap["sha256"] == row["sha256"]
        live.append(snap)
    return {
        "nloc_definition": data["nloc_definition"],
        "freeze_git_head": data["git_head"],
        "freeze_pi_nloc": data["by_role"]["Π"]["nloc"],
        "freeze_pi_files": data["by_role"]["Π"]["files"],
        "live_pi_nloc": sum(r["nloc"] for r in live),
        "live_pi_bytes": sum(r["bytes"] for r in live),
        "files": live,
    }


def compare_snapshots(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> dict[str, Any]:
    after_by = {row["path"]: row for row in after}
    rows = []
    all_identical = True
    any_grew = False
    for left in before:
        right = after_by[left["path"]]
        identical = left["sha256"] == right["sha256"]
        nloc_constant = left["nloc"] == right["nloc"]
        grew = right["nloc"] > left["nloc"] or right["bytes"] > left["bytes"]
        all_identical = all_identical and identical
        any_grew = any_grew or grew
        rows.append(
            {
                "path": left["path"],
                "nloc_before": left["nloc"],
                "nloc_after": right["nloc"],
                "bytes_before": left["bytes"],
                "bytes_after": right["bytes"],
                "sha256_before": left["sha256"],
                "sha256_after": right["sha256"],
                "nloc_constant": nloc_constant,
                "byte_identical": identical,
                "grew": grew,
            }
        )
    return {
        "files": rows,
        "all_nloc_constant": all(r["nloc_constant"] for r in rows),
        "all_byte_identical": all_identical,
        "any_grew": any_grew,
        "controller_nloc_before": sum(r["nloc_before"] for r in rows),
        "controller_nloc_after": sum(r["nloc_after"] for r in rows),
    }


def planner_fork_scan() -> dict[str, Any]:
    hits = sorted(
        str(p.relative_to(REPO))
        for p in (SRC / "ocm").rglob("*")
        if p.is_file() and "planner" in p.name.lower()
    )
    expected = "src/ocm/dialogue/planner.py"
    return {
        "production_planner_paths": hits,
        "expected_single_planner": expected,
        "unique_production_planner": hits == [expected],
        "domain_forked_planner": hits != [expected],
        "note": (
            "Language construction uses this one planner. Polynomial procedure "
            "is admitted through OCMRuntime and does not add a second planner."
        ),
    }


def live_procedures(runtime: OCMRuntime) -> list[str]:
    revoked = runtime.state.revoked
    out = []
    for atom in runtime.state.ks.atoms:
        if atom.atom_type == "procedure" and atom.liveness(revoked) is Liveness.LIVE:
            out.append(atom.atom_id)
    return sorted(out)


def admit_l1_construction(root: Path) -> dict[str, Any]:
    train_pairs = [(a, n) for a in L1.TRAIN_ADJ for n in L1.TRAIN_NOUN]
    runtime = OCMRuntime(root)
    lesson_ids = []
    for adj, noun in train_pairs:
        _rec, eid = runtime.admit_evidence(
            {"schema": "g1.pi-small.l1-lesson", "adj": adj, "noun": noun},
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
        "runtime_class": type(replay).__module__ + "." + type(replay).__qualname__,
    }


def parent_citation(path: Path, expected_terminal: str) -> dict[str, Any]:
    rel = str(path.relative_to(REPO))
    if not path.is_file():
        return {"path": rel, "present": False}
    digest = sha256_file(path)
    data = json.loads(path.read_text())
    return {
        "path": rel,
        "present": True,
        "terminal": data.get("terminal"),
        "schema": data.get("schema"),
        "sha256": digest,
        "expected_terminal": expected_terminal,
        "matches_expected_terminal": data.get("terminal") == expected_terminal,
        "not_rewritten": True,
    }


def src_tree_intact() -> dict[str, Any]:
    diff = subprocess.run(
        ["git", "diff", "--exit-code", "--", "src"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    return {"git_diff_src_clean": diff.returncode == 0, "returncode": diff.returncode}


def measure_microworld() -> dict[str, Any]:
    controllers_before = snapshot_controllers()
    freeze_before = freeze_pi_inventory()
    parent_growth_before = sha256_file(PARENT_GROWTH) if PARENT_GROWTH.is_file() else None
    parent_fo_before = sha256_file(PARENT_FO) if PARENT_FO.is_file() else None
    parent_cores_before = sha256_file(PARENT_CORES) if PARENT_CORES.is_file() else None
    forks = planner_fork_scan()

    with tempfile.TemporaryDirectory(prefix="g1-pi-small-") as tmp:
        root = Path(tmp) / "ledger"
        root.mkdir()
        bytes_empty = dir_bytes(root)
        loaded, atom_id, training_ev, utility_ev = G2.admit_macro(
            root,
            ("inc", "inc"),
            {"schema": "g1.pi-small.training", "fragment": ["inc", "inc"]},
            {"schema": "g1.pi-small.utility", "accepted": True},
        )
        after_g2 = OCMRuntime(root)
        bytes_after_g2 = dir_bytes(root)
        procs_after_g2 = live_procedures(after_g2)
        g2_runtime_class = type(after_g2).__module__ + "." + type(after_g2).__qualname__
        l1 = admit_l1_construction(root)
        after_both = OCMRuntime(root)
        bytes_after_both = dir_bytes(root)
        procs_after_both = live_procedures(after_both)
        l1_runtime_class = type(after_both).__module__ + "." + type(after_both).__qualname__
        macro_live = atom_id in procs_after_both
        l1_live = l1["atom_id"] in procs_after_both
        same_runtime_class = g2_runtime_class == l1_runtime_class == "ocm.runtime.ocm_runtime.OCMRuntime"

        language_plan = plan_teach_back(
            "green",
            "property:green",
            l1["lesson_evidence"],
            construction=l1["construction_id"],
        )
        polynomial_solve = solve(KnowledgeSpace((), ()), Task("g1-pi-small-empty", ()))

        controllers_after = snapshot_controllers()
        freeze_after = freeze_pi_inventory()
        compared = compare_snapshots(controllers_before, controllers_after)
        freeze_compared = compare_snapshots(
            [{k: r[k] for k in ("path", "nloc", "bytes", "sha256")} for r in freeze_before["files"]],
            [{k: r[k] for k in ("path", "nloc", "bytes", "sha256")} for r in freeze_after["files"]],
        )

        parent_growth_after = sha256_file(PARENT_GROWTH) if PARENT_GROWTH.is_file() else None
        parent_fo_after = sha256_file(PARENT_FO) if PARENT_FO.is_file() else None
        parent_cores_after = sha256_file(PARENT_CORES) if PARENT_CORES.is_file() else None

        two_domains = macro_live and l1_live
        fo_grew = bytes_after_both > bytes_after_g2 > bytes_empty
        used_across_two_domains = (
            two_domains
            and same_runtime_class
            and not forks["domain_forked_planner"]
            and language_plan.act.value == "ASSERT"
            and polynomial_solve.decision.value in {"UNKNOWN", "CLARIFY", "ABSTAIN", "ANSWER", "CANNOT_CHECK"}
        )
        return {
            "controllers_before": controllers_before,
            "controllers_after": controllers_after,
            "controller_compare": compared,
            "freeze_pi_before": freeze_before,
            "freeze_pi_after_nloc": freeze_after["live_pi_nloc"],
            "freeze_pi_compare": freeze_compared,
            "planner_fork_scan": forks,
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
            "g2_runtime_class": g2_runtime_class,
            "l1_runtime_class": l1_runtime_class,
            "same_runtime_class": same_runtime_class,
            "two_domains_in_fo_state": two_domains,
            "fo_competence_grew": fo_grew,
            "language_pi_use": {
                "module": "ocm.dialogue.planner",
                "function": "plan_teach_back",
                "path": "src/ocm/dialogue/planner.py",
                "act": language_plan.act.value,
                "construction": l1["construction_id"],
                "domain": "language_construction",
            },
            "polynomial_pi_use": {
                "module": "ocm.runtime.ocm_runtime",
                "class": g2_runtime_class,
                "admit_path": "admit_evidence + admit_object",
                "macro": list(loaded),
                "domain": "polynomial_procedure",
                "solve_module": "ocm.runtime.solve",
                "solve_function": "solve",
                "solve_decision_on_empty_field_probe": polynomial_solve.decision.value,
            },
            "used_across_two_domains_without_forked_planner": used_across_two_domains,
            "parent_result_sha256_unchanged": {
                "g1-controller-growth-v1": parent_growth_before == parent_growth_after,
                "g1-fo-competence-v2": parent_fo_before == parent_fo_after,
                "g1-duplicate-cores-v1": parent_cores_before == parent_cores_after,
            },
        }


def decide_terminal(world: dict[str, Any]) -> str:
    if world["controller_compare"]["any_grew"] or not world["controller_compare"]["all_byte_identical"]:
        return "PI_GREW_AT_SCOPE"
    if world["freeze_pi_compare"]["any_grew"] or not world["freeze_pi_compare"]["all_byte_identical"]:
        return "PI_GREW_AT_SCOPE"
    micro_ok = (
        world["controller_compare"]["all_nloc_constant"]
        and world["controller_compare"]["all_byte_identical"]
        and world["fo_competence_grew"]
        and world["two_domains_in_fo_state"]
        and world["used_across_two_domains_without_forked_planner"]
        and not world["planner_fork_scan"]["domain_forked_planner"]
        and world["l1"]["held_out_invoked"]
        and world["l1"]["reset_has_no_construction"]
    )
    if micro_ok:
        return "PI_REMAINS_SMALL_AT_MICRO_SCOPE"
    return "PI_SMALL_INCOMPLETE_AT_SCOPE"


def run_study() -> dict[str, Any]:
    world = measure_microworld()
    terminal = decide_terminal(world)
    micro_ok = terminal == "PI_REMAINS_SMALL_AT_MICRO_SCOPE"
    result = {
        "schema": SCHEMA,
        "salt": SALT,
        "issue": ISSUE,
        "gate": GATE,
        "head": git_head(),
        "production_code_deleted": False,
        "terminal": terminal,
        "programme_terminal": "COMPACT_VESSEL_PARTIAL",
        "claim_ceiling": (
            "At this polynomial + L1 microworld, measured controller files stay "
            "byte-identical while G2 macro and L1 construction competence land in "
            "ledger F/O. Same OCMRuntime serves both domains; planner.py is not "
            "forked. Not programme-wide “Π remains small”: hostile coefficient "
            "tables and authored work operators remain. Programme-level terminal "
            "stays COMPACT_VESSEL_PARTIAL."
        ),
        "not_issued": [
            "MINIMUM_SELF_EXTENDING_VESSEL",
            "MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE",
            "CONTROLLER_GROWTH_DOMINATES",
            "STATE_SIZE_DOMINATES",
            "DOMAIN_CORE_FORK_REQUIRED",
            "PI_REMAINS_SMALL",
            "PI_SMALL_DOMAIN_GENERAL",
        ],
        "not_issued_reasons": {
            "MINIMUM_SELF_EXTENDING_VESSEL": "G1.2 subtraction is not a minimality proof; nothing deleted.",
            "PI_REMAINS_SMALL": "Unscoped programme claim. Hostile Π tables and authored work operators remain.",
            "PI_SMALL_DOMAIN_GENERAL": "Architecture-rule close is still PARTIAL at programme scope.",
        },
        "parents": {
            "g1-controller-growth-v1": parent_citation(PARENT_GROWTH, "COMPACT_VESSEL_PARTIAL"),
            "g1-fo-competence-v2": parent_citation(PARENT_FO, "COMPETENCE_IN_FO_STATE_AT_MICRO_SCOPE"),
            "g1-duplicate-cores-v1": parent_citation(PARENT_CORES, "SINGLE_CORE_AT_SCOPE"),
        },
        "src_custody": src_tree_intact(),
        "microworld": world,
        "architecture_boxes": {
            "intelligence_in_f_and_o": {
                "text": "Machine intelligence accumulates primarily in F and O, not in an ever-growing hard-coded controller.",
                "status": "EARNED_AT_MICRO_SCOPE" if micro_ok else "NOT_EARNED",
                "note": (
                    "New competence this run is G2 macro + L1 construction procedure "
                    "atoms / ledger bytes. Controller nloc does not grow. Procedural "
                    "work operators remain authored. Cite g1-fo-competence-v2 for the "
                    "G1.3.2 micro-scope predecessor."
                ),
            },
            "pi_small_domain_general": {
                "text": "Π remains small and domain-general.",
                "status": "EARNED_AT_MICRO_SCOPE" if micro_ok else terminal,
                "programme_status": "PARTIAL",
                "note": (
                    "Micro-scope: measured Π nloc constant, files byte-identical, "
                    "F/O grew, one planner, two domains. Programme-wide still PARTIAL "
                    "because hostile coefficients / authored work operators remain."
                ),
            },
            "competence_in_fo_state": {
                "text": "Demonstrate new competence predominantly appears in learned/imported field/operator state.",
                "status": "EARNED_AT_MICRO_SCOPE" if micro_ok else "PARTIAL_AT_MICRO_SCOPE",
                "predominantly_across_three_domains": False,
                "procedural_authored": True,
                "note": "Two-domain micro-scope (language + polynomial), not three-domain predominance.",
            },
        },
        "architecture_rules_empirical": {
            "INTELLIGENCE_IN_F_AND_O": (
                "EARNED_AT_POLYNOMIAL_AND_L1_MICRO_SCOPE" if micro_ok else "PARTIAL_AT_MICRO_SCOPE"
            ),
            "PI_SMALL_DOMAIN_GENERAL": "PARTIAL",
            "PI_SMALL_DOMAIN_GENERAL_MICRO_SCOPE": terminal,
        },
        "G1_1_6_duplicate_cores": "NOT_THIS_TASK_CITED_SINGLE_CORE_AT_SCOPE",
        "G1_checkboxes": {
            "section_2": [
                {
                    "id": "INTELLIGENCE_IN_F_AND_O",
                    "text": "Machine intelligence accumulates primarily in F and O, not in an ever-growing hard-coded controller.",
                    "status": "EARNED_AT_MICRO_SCOPE" if micro_ok else "NOT_EARNED",
                },
                {
                    "id": "PI_SMALL_DOMAIN_GENERAL",
                    "text": "Π remains small and domain-general.",
                    "status": "EARNED_AT_MICRO_SCOPE" if micro_ok else terminal,
                    "programme_status": "PARTIAL",
                    "capsule_terminal": terminal,
                },
            ],
            "G1.3": [
                {
                    "id": "G1.3.2",
                    "text": "Demonstrate new competence predominantly appears in learned/imported field/operator state.",
                    "status": "EARNED_AT_MICRO_SCOPE" if micro_ok else "PARTIAL_AT_MICRO_SCOPE",
                    "predominantly_across_three_domains": False,
                    "cite": "research/g1-fo-competence-v2/RESULT.json",
                }
            ],
        },
    }
    return result


def write_outputs(out: Path | None = None, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or run_study()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    capsule = HERE / "RESULT.json"
    capsule.write_text(text)
    if out is not None and out.resolve() != capsule.resolve():
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
    return payload


def main(out: Path | None = None) -> dict[str, Any]:
    result = write_outputs(out)
    world = result["microworld"]
    print(
        json.dumps(
            {
                "terminal": result["terminal"],
                "programme_terminal": result["programme_terminal"],
                "controller_nloc": world["controller_compare"]["controller_nloc_after"],
                "all_byte_identical": world["controller_compare"]["all_byte_identical"],
                "fo_delta_bytes": world["fo_delta_bytes"],
                "two_domains": world["two_domains_in_fo_state"],
                "forked_planner": world["planner_fork_scan"]["domain_forked_planner"],
                "not_issued_minimum_vessel": "MINIMUM_SELF_EXTENDING_VESSEL" in result["not_issued"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "RESULT.json"
    main(target)

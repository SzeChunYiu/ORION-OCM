"""G1 remaining: hostile work-operator Π, absent from the mechanism arm.

Research-only. Production ``src/`` is not modified. Parents
``g1-pi-small-v1``, ``g1-fo-competence-v2``, and ``g1-controller-growth-v1``
are cited, not overwritten.

A domain-specific hard-coded work Π would trivially solve the planted
enterprise tasks. G1.3.3/G1.3.4 already require that hostile to be planted and
then absent from the mechanism arm; this capsule measures it.

Legal terminals: ``PARENT_SUFFICIENT``, ``PI_GREW``, ``HOSTILE_PI_REQUIRED``.
``PARENT_SUFFICIENT`` is not programme failure. Programme-wide Π-small stays
``PARTIAL``. ``MINIMUM_SELF_EXTENDING_VESSEL`` is not issued.
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

HERE = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
sys.path.insert(0, str(SRC))

from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.runtime.solve import Task, solve
from ocm.store.evidence import Channel
from ocm.work.contracts import Skill
from ocm.work.envs import ROLES, enterprise_operators, enterprise_task
from ocm.work.methods import run_skill

G2_PATH = REPO / "research" / "g2-macro-operator-v1" / "experiment.py"
PARENT_PI = REPO / "research" / "g1-pi-small-v1" / "RESULT.json"
PARENT_FO = REPO / "research" / "g1-fo-competence-v2" / "RESULT.json"
PARENT_GROWTH = REPO / "research" / "g1-controller-growth-v1" / "RESULT.json"
METHODS = SRC / "ocm" / "learning" / "methods.py"

SCHEMA = "ocm.g1.hostile-pi.result.v1"
SALT = "orion-ocm-g1-hostile-pi-v1"
ISSUE = 165
GATE = "PI_SMALL_DOMAIN_GENERAL"
HOSTILE_MARKER = "HOSTILE_PI_WORK_OPERATOR_V1"
METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
WORK_SCOPE = Scope.of("g1-hostile-pi.work.v1")
PLANTED_N = 8
LEGAL_TERMINALS = frozenset({"PARENT_SUFFICIENT", "PI_GREW", "HOSTILE_PI_REQUIRED"})

G2_SPEC = importlib.util.spec_from_file_location("g1_hostile_pi_g2_parent", G2_PATH)
G2 = importlib.util.module_from_spec(G2_SPEC)
assert G2_SPEC is not None and G2_SPEC.loader is not None
sys.modules[G2_SPEC.name] = G2
G2_SPEC.loader.exec_module(G2)

CONTROLLER_SPECS = (
    {
        "path": "src/ocm/runtime/solve.py",
        "justification": "Canonical domain-general Π_exec. Freeze role Π.",
        "freeze_role": "Π",
        "counted_as": "Π_exec",
    },
    {
        "path": "src/ocm/runtime/ocm_runtime.py",
        "justification": "Shared Admit_C executive. Freeze role Π.",
        "freeze_role": "Π",
        "counted_as": "Π_exec",
    },
    {
        "path": "src/ocm/dialogue/planner.py",
        "justification": "G1.3 domain-control. Must not fork per domain.",
        "freeze_role": "PRIOR",
        "counted_as": "domain-control Π",
    },
)

MECHANISM_ARM = (
    SRC / "ocm" / "runtime" / "solve.py",
    SRC / "ocm" / "runtime" / "ocm_runtime.py",
    SRC / "ocm" / "dialogue" / "planner.py",
    SRC / "ocm" / "work" / "contracts.py",
    SRC / "ocm" / "work" / "envs.py",
    SRC / "ocm" / "work" / "methods.py",
    SRC / "ocm" / "operators" / "registry.py",
    METHODS,
    G2_PATH,
)

HOSTILE_CALLS = 0

ENTERPRISE_BINDINGS = {
    "gather": "ent.gather_facts",
    "classify": "ent.classify_urgency",
    "check_policy": "ent.check_policy",
    "act_smallest": "ent.smallest_action",
    "verify": "ent.verify",
    "document": "ent.document",
}


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def pin_methods() -> str:
    blob = git_blob_sha1(METHODS)
    if blob != METHOD_BLOB:
        raise RuntimeError(f"methods.py blob {blob} != pinned {METHOD_BLOB}")
    return blob


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


def plant_world() -> list[Any]:
    """Planted enterprise work tasks. Name is a load-path canary."""
    return [enterprise_task(i, version=1, seed="OCM-M9") for i in range(PLANTED_N)]


def hostile_work_pi_lookup(case_id, outage):  # HOSTILE_PI_WORK_OPERATOR_V1
    global HOSTILE_CALLS
    HOSTILE_CALLS += 1
    planted = {f"A{i}" for i in range(PLANTED_N)}
    if case_id not in planted:
        raise KeyError(case_id)
    return "escalate" if outage else "reply_faq"


def parent_mechanism_skill() -> Skill:
    return Skill(
        "g1-hostile-pi.enterprise.v1",
        ROLES,
        dict(ENTERPRISE_BINDINGS),
        "enterprise",
        WarrantProfile.one(),
    )


def live_procedures(runtime: OCMRuntime) -> list[str]:
    revoked = runtime.state.revoked
    out = []
    for atom in runtime.state.ks.atoms:
        if atom.atom_type == "procedure" and atom.liveness(revoked) is Liveness.LIVE:
            out.append(atom.atom_id)
    return sorted(out)


def admit_work_skill(root: Path, skill: Skill) -> dict[str, Any]:
    runtime = OCMRuntime(root)
    _rec, eid = runtime.admit_evidence(
        {
            "schema": "g1.hostile-pi.work-skill-lesson",
            "skill_id": skill.skill_id,
            "skeleton": list(skill.skeleton),
        },
        Channel.OBSERVATION,
        "g1-hostile-pi.work-skill.v1",
        scope=WORK_SCOPE,
    )
    warrant = WarrantProfile.of({eid})
    source_payload = {
        "kind": "g1.hostile-pi.work-skill.support.v1",
        "skill_id": skill.skill_id,
        "lesson": eid,
    }
    source_id = "g1-hostile-pi-work-support:" + content_hash(source_payload)
    runtime.admit_object(
        Atom(
            source_id,
            "proof",
            warrant,
            scope=WORK_SCOPE,
            quarantined=True,
            content_ref=content_hash(source_payload),
            meta=tuple(source_payload.items()),
        ),
        (),
        "OBSERVATION",
    )
    payload = {
        "kind": "g1.hostile-pi.work-skill.v1",
        "skill_id": skill.skill_id,
        "skeleton": list(skill.skeleton),
        "bindings": dict(skill.bindings),
        "domain": skill.domain,
        "fingerprint": content_hash(
            {"skill_id": skill.skill_id, "skeleton": list(skill.skeleton), "bindings": dict(skill.bindings)}
        ),
    }
    atom_id = "work-skill:" + content_hash(payload)
    edge = Hyperedge("support:" + atom_id, (source_id,), (atom_id,), "SUPPORT", warrant=warrant)
    runtime.admit_object(
        Atom(
            atom_id,
            "procedure",
            warrant,
            scope=WORK_SCOPE,
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
        raise RuntimeError("work skill did not survive restart")
    stored = dict(atom.meta)
    if atom.content_ref != content_hash(stored):
        raise RuntimeError("work skill content identity mismatch")
    return {
        "atom_id": atom_id,
        "lesson_evidence": eid,
        "live_after_restart": True,
        "skill_id": stored["skill_id"],
        "runtime_class": type(replay).__module__ + "." + type(replay).__qualname__,
    }


def mechanism_contains_hostile() -> dict[str, Any]:
    hits = {}
    for path in MECHANISM_ARM:
        text = path.read_text(encoding="utf-8")
        hits[str(path.relative_to(REPO))] = {
            "marker": HOSTILE_MARKER in text,
            "function_name": "hostile_work_pi_lookup" in text,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    return hits


def hostile_source_nloc() -> tuple[str, int]:
    source = (HERE / "experiment.py").read_text(encoding="utf-8")
    start = source.index("def hostile_work_pi_lookup")
    end = source.index("\ndef parent_mechanism_skill")
    hostile_src = source[start:end].strip()
    return hostile_src, nloc_text(hostile_src)


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


def reset_hostile_calls() -> None:
    global HOSTILE_CALLS
    HOSTILE_CALLS = 0


def measure() -> dict[str, Any]:
    blob = pin_methods()
    controllers_before = snapshot_controllers()
    parent_pi_before = sha256_file(PARENT_PI) if PARENT_PI.is_file() else None
    parent_fo_before = sha256_file(PARENT_FO) if PARENT_FO.is_file() else None
    parent_growth_before = sha256_file(PARENT_GROWTH) if PARENT_GROWTH.is_file() else None
    tasks = plant_world()
    ops = enterprise_operators(version=1)
    skill = parent_mechanism_skill()
    contains = mechanism_contains_hostile()
    hostile_src, hostile_nloc = hostile_source_nloc()

    reset_hostile_calls()
    hostile_rows = []
    for contract in tasks:
        guessed = hostile_work_pi_lookup(contract.initial_state["case_id"], contract.hidden["outage"])
        ok = guessed == contract.hidden["expected_action"]
        hostile_rows.append(
            {
                "task_id": contract.task_id,
                "case_id": contract.initial_state["case_id"],
                "outage": contract.hidden["outage"],
                "guessed": guessed,
                "expected": contract.hidden["expected_action"],
                "ok": ok,
            }
        )
    hostile_calls_probe = HOSTILE_CALLS

    reset_hostile_calls()
    mechanism_rows = []
    for contract in tasks:
        result = run_skill(skill, ops, contract)
        mechanism_rows.append(
            {
                "task_id": contract.task_id,
                "success": result.success,
                "cost": result.cost,
                "skill_id": result.skill_id,
                "action": result.final_state.get("action"),
                "expected": contract.hidden["expected_action"],
                "action_matches": result.final_state.get("action") == contract.hidden["expected_action"],
                "step_outcomes": [step.outcome.value for step in result.steps],
            }
        )
    hostile_calls_mechanism = HOSTILE_CALLS
    mechanism_solves_all = all(row["success"] and row["action_matches"] for row in mechanism_rows)

    with tempfile.TemporaryDirectory(prefix="g1-hostile-pi-") as tmp:
        root = Path(tmp) / "ledger"
        root.mkdir()
        bytes_empty = dir_bytes(root)
        loaded, macro_atom_id, training_ev, utility_ev = G2.admit_macro(
            root,
            ("inc", "inc"),
            {"schema": "g1.hostile-pi.training", "fragment": ["inc", "inc"]},
            {"schema": "g1.hostile-pi.utility", "accepted": True},
        )
        after_g2 = OCMRuntime(root)
        bytes_after_g2 = dir_bytes(root)
        procs_after_g2 = live_procedures(after_g2)
        work = admit_work_skill(root, skill)
        after_both = OCMRuntime(root)
        bytes_after_both = dir_bytes(root)
        procs_after_both = live_procedures(after_both)
        g2_runtime_class = type(after_g2).__module__ + "." + type(after_g2).__qualname__
        work_runtime_class = type(after_both).__module__ + "." + type(after_both).__qualname__
        polynomial_solve = solve(KnowledgeSpace((), ()), Task("g1-hostile-pi-empty", ()))

    controllers_after = snapshot_controllers()
    compared = compare_snapshots(controllers_before, controllers_after)
    parent_pi_after = sha256_file(PARENT_PI) if PARENT_PI.is_file() else None
    parent_fo_after = sha256_file(PARENT_FO) if PARENT_FO.is_file() else None
    parent_growth_after = sha256_file(PARENT_GROWTH) if PARENT_GROWTH.is_file() else None

    fo_grew = bytes_after_both > bytes_after_g2 > bytes_empty
    return {
        "methods_blob": blob,
        "controllers_before": controllers_before,
        "controllers_after": controllers_after,
        "controller_compare": compared,
        "planted_n": PLANTED_N,
        "hostile": {
            "marker": HOSTILE_MARKER,
            "hostile_function_nloc": hostile_nloc,
            "hostile_function_source": hostile_src,
            "hostile_solves_all_table_tasks": all(row["ok"] for row in hostile_rows),
            "hostile_tasks": hostile_rows,
            "hostile_calls_probe": hostile_calls_probe,
            "mechanism_contains_hostile": contains,
            "hostile_absent_from_mechanism_arm": not any(
                v["marker"] or v["function_name"] for v in contains.values()
            ),
        },
        "mechanism": {
            "skill_id": skill.skill_id,
            "skeleton": list(skill.skeleton),
            "bindings": dict(skill.bindings),
            "rows": mechanism_rows,
            "solves_all_planted_tasks": mechanism_solves_all,
            "hostile_calls": hostile_calls_mechanism,
            "runtime_class": "ocm.work.methods.run_skill",
        },
        "admitted_macro": list(loaded),
        "macro_atom_id": macro_atom_id,
        "macro_training_evidence": training_ev,
        "macro_utility_evidence": utility_ev,
        "macro_live_after_both_admits": macro_atom_id in procs_after_both,
        "work_skill": work,
        "work_skill_live_after_both_admits": work["atom_id"] in procs_after_both,
        "ledger_bytes_empty": bytes_empty,
        "ledger_bytes_after_g2": bytes_after_g2,
        "ledger_bytes_after_g2_and_work": bytes_after_both,
        "fo_delta_bytes": bytes_after_both - bytes_empty,
        "g2_delta_bytes": bytes_after_g2 - bytes_empty,
        "work_delta_bytes": bytes_after_both - bytes_after_g2,
        "live_procedure_atoms_after_g2": procs_after_g2,
        "live_procedure_atoms_after_both": procs_after_both,
        "g2_runtime_class": g2_runtime_class,
        "work_runtime_class": work_runtime_class,
        "same_runtime_class": g2_runtime_class == work_runtime_class == "ocm.runtime.ocm_runtime.OCMRuntime",
        "fo_competence_grew": fo_grew,
        "polynomial_empty_field_decision": polynomial_solve.decision.value,
        "parent_result_sha256_unchanged": {
            "g1-pi-small-v1": parent_pi_before == parent_pi_after,
            "g1-fo-competence-v2": parent_fo_before == parent_fo_after,
            "g1-controller-growth-v1": parent_growth_before == parent_growth_after,
        },
    }


def decide_terminal(world: dict[str, Any]) -> str:
    if world["controller_compare"]["any_grew"] or not world["controller_compare"]["all_byte_identical"]:
        return "PI_GREW"
    parent_ok = (
        world["controller_compare"]["all_nloc_constant"]
        and world["controller_compare"]["all_byte_identical"]
        and world["hostile"]["hostile_solves_all_table_tasks"]
        and world["hostile"]["hostile_absent_from_mechanism_arm"]
        and world["mechanism"]["solves_all_planted_tasks"]
        and world["mechanism"]["hostile_calls"] == 0
        and world["fo_competence_grew"]
        and world["macro_live_after_both_admits"]
        and world["work_skill_live_after_both_admits"]
        and world["same_runtime_class"]
    )
    if parent_ok:
        return "PARENT_SUFFICIENT"
    return "HOSTILE_PI_REQUIRED"


def run_study() -> dict[str, Any]:
    world = measure()
    terminal = decide_terminal(world)
    if terminal not in LEGAL_TERMINALS:
        raise RuntimeError(f"illegal terminal {terminal}")
    parent_ok = terminal == "PARENT_SUFFICIENT"
    result = {
        "schema": SCHEMA,
        "salt": SALT,
        "issue": ISSUE,
        "gate": GATE,
        "head": git_head(),
        "methods_blob": world["methods_blob"],
        "production_code_deleted": False,
        "terminal": terminal,
        "programme_terminal": "COMPACT_VESSEL_PARTIAL",
        "claim_ceiling": (
            "At this planted enterprise-work microscope, a hard-coded hostile Π "
            "solves the checker in one lookup and is absent from production Π, "
            "work.Operator/run_skill, and G2 admit. Parent Skill composition plus "
            "ledger F/O admission still solves the same tasks without calling the "
            "hostile. PARENT_SUFFICIENT is not programme failure. Programme-wide "
            "Π-small stays PARTIAL because authored work backends remain prior. "
            "Not MINIMUM_SELF_EXTENDING_VESSEL. G1.1.6 deletion is not this task."
        ),
        "not_issued": [
            "MINIMUM_SELF_EXTENDING_VESSEL",
            "MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED",
            "MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE",
            "PI_REMAINS_SMALL",
            "PI_SMALL_DOMAIN_GENERAL",
            "G1_1_6_DELETION",
        ],
        "not_issued_reasons": {
            "MINIMUM_SELF_EXTENDING_VESSEL": "No deletion, no minimality proof.",
            "PI_REMAINS_SMALL": "Unscoped programme claim. Authored work backends remain prior.",
            "PI_SMALL_DOMAIN_GENERAL": "Architecture-rule close is still PARTIAL at programme scope.",
            "G1_1_6_DELETION": "Cited from g1-duplicate-cores-v1 / controller-growth; not this task.",
        },
        "parents": {
            "g1-pi-small-v1": parent_citation(PARENT_PI, "PI_REMAINS_SMALL_AT_MICRO_SCOPE"),
            "g1-fo-competence-v2": parent_citation(PARENT_FO, "COMPETENCE_IN_FO_STATE_AT_MICRO_SCOPE"),
            "g1-controller-growth-v1": parent_citation(PARENT_GROWTH, "COMPACT_VESSEL_PARTIAL"),
        },
        "src_custody": src_tree_intact(),
        "microworld": world,
        "architecture_boxes": {
            "pi_small_domain_general": {
                "text": "Π remains small and domain-general.",
                "status": "PARTIAL",
                "programme_status": "PARTIAL",
                "capsule_terminal": terminal,
                "note": (
                    "Hostile work Π is planted and absent from the mechanism arm. "
                    "Parent sufficiency at this microscope does not close the "
                    "programme box: authored work backends remain prior information."
                ),
            }
        },
        "architecture_rules_empirical": {
            "PI_SMALL_DOMAIN_GENERAL": "PARTIAL",
            "HOSTILE_WORK_PI_ABSENT_FROM_MECHANISM": world["hostile"]["hostile_absent_from_mechanism_arm"],
            "PARENT_SUFFICIENT_WITHOUT_HOSTILE": parent_ok,
        },
        "G1_1_6_duplicate_cores": "NOT_THIS_TASK",
        "G1_checkboxes": {
            "G1.3": [
                {
                    "id": "G1.3.3",
                    "text": "Add hostile where a domain-specific hard-coded Π rule would trivially solve the task.",
                    "status": "EARNED" if world["hostile"]["hostile_solves_all_table_tasks"] else "NOT_EARNED",
                    "hostile_solves": world["hostile"]["hostile_solves_all_table_tasks"],
                    "marker": HOSTILE_MARKER,
                },
                {
                    "id": "G1.3.4",
                    "text": "Require that hostile to be absent from the mechanism arm.",
                    "status": "EARNED" if world["hostile"]["hostile_absent_from_mechanism_arm"] else "NOT_EARNED",
                    "absent": world["hostile"]["hostile_absent_from_mechanism_arm"],
                },
            ]
        },
    }
    return result


def write_outputs(out: Path, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Write RESULT only to ``out``. Tests must pass a tempfile, not the capsule."""
    payload = payload or run_study()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    return payload


def main(out: Path | None = None) -> dict[str, Any]:
    target = out if out is not None else HERE / "RESULT.json"
    result = write_outputs(target)
    print(
        json.dumps(
            {
                "terminal": result["terminal"],
                "programme_terminal": result["programme_terminal"],
                "hostile_absent": result["microworld"]["hostile"]["hostile_absent_from_mechanism_arm"],
                "mechanism_solves": result["microworld"]["mechanism"]["solves_all_planted_tasks"],
                "hostile_calls_mechanism": result["microworld"]["mechanism"]["hostile_calls"],
                "fo_delta_bytes": result["microworld"]["fo_delta_bytes"],
                "all_byte_identical": result["microworld"]["controller_compare"]["all_byte_identical"],
                "wrote": str(target),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "RESULT.json"
    main(target)

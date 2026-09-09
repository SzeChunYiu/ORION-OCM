"""E5 arms, custody and the two-set contrast.

This module runs every arm on both fresh-task sets, drives the real process
restart CL-T1 requires, and assembles the summary the receipt is a function of.

It is also the child entry point of the custody boundary.  Invoked as

    python -I -S -B libdisc_arms.py acquire <state.json> <report.json>
    python -I -S -B libdisc_arms.py use     <state.json> <report.json> [drop_id]

it performs exactly one half of the chain and then EXITS.  ``-I`` is isolated
mode: no ``PYTHONPATH``, no user site directory, no environment influence at
all.  ``-I`` also implies ``-P``, so the interpreter does NOT put the script's
directory on ``sys.path``; the two lines below put it back explicitly, which is
the only path manipulation in this module and is the reason a sibling import
works inside an isolated child.  ``-S`` skips ``site``, ``-B`` writes no
bytecode, and the environment handed to the child is a minimal dict.

The causal chain, in the order the receipt reports it:

    experience -> discovered schema -> independent check -> persist to disk ->
    REAL PROCESS RESTART -> fresh unseen task -> invocation with an
    execution-trace witness -> less search than the reset arm -> remove the
    schema -> advantage disappears

``pid_before``, ``pid_after``, the exit status of the acquiring process and the
state digest before and after are all recorded.  A run in which
``pid_before == pid_after`` is a ``CUSTODY_VIOLATION`` and is not analysable;
``test_libdisc.py`` fails if that equality ever holds.

The two fresh-task sets are never pooled.  A single total over both would
average an opportunity against its absence and would reproduce precisely the
confusion this experiment exists to remove.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json  # noqa: E402
import pathlib  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from typing import Sequence  # noqa: E402

from libdisc import (  # noqa: E402
    CONTROL_TASKS,
    ESSENTIAL_COMPOSITE_TASKS,
    MAX_SEARCH_DEPTH,
    TAUTOLOGICAL_CONTROL_TASKS,
    TRAINING_EPISODES,
    UNSOUND_TRAP_TASKS,
    CHAIN_SCHEMA,
    LearnerView,
    Schema,
    Task,
    certify_draw,
    digest_of,
    entails,
    learner_views,
    schema_from_body,
    solve,
)
from libdisc_discovery import (  # noqa: E402
    discover,
    flat_mining_ablation,
    polarity_blind_refutations,
    redundant_sound_matches,
)
from libdisc_parents import (  # noqa: E402
    PARENTS,
    ParentResult,
    replay_from_archive,
)

__all__ = [
    "discovery_arm",
    "ARMS",
    "TASK_SETS",
    "run_arm",
    "sweep",
    "custody_cycle",
    "summarise",
    "main",
]

#: The two headline sets plus the registered side controls.  Every set is
#: reported separately and no total is ever taken across the first two.
TASK_SETS: dict[str, tuple[Task, ...]] = {
    "essential_composite": ESSENTIAL_COMPOSITE_TASKS,
    "tautological_control": TAUTOLOGICAL_CONTROL_TASKS,
    "registered_controls": CONTROL_TASKS,
    "unsound_traps": UNSOUND_TRAP_TASKS,
}


def discovery_arm(views: Sequence[LearnerView]) -> ParentResult:
    """The arm under test: step-level discovery, composition, CL-D1 admission."""
    result = discover(views)
    funnel = dict(result.funnel)
    funnel["ablation_pool"] = flat_mining_ablation(views).funnel["pool"]
    return ParentResult(
        "libdisc_discovery_arm", result.library(), True, (),
        "signed-clause normalisation, anti-unification over proof steps, exact "
        "semantic-equivalence clustering, composition of admitted singleton "
        "fragments, MDL plus held-out validation, CL-D1 admission",
        funnel)


def flat_mining_ablation_arm(views: Sequence[LearnerView]) -> ParentResult:
    """The ablation: the same evidence mined at the flat surface level."""
    ab = flat_mining_ablation(views)
    return ParentResult(
        "flat_mining_ablation", (), True, (),
        "flat surface fragments plus the registered repeated-support gate; "
        "reproduces NO_METHOD_ACQUIRED", dict(ab.funnel))


#: Every arm, in the order the receipt reports them.  The discovery arm first,
#: its own ablation second, then the parents in registered order.
ARMS = (discovery_arm, flat_mining_ablation_arm) + PARENTS


# --------------------------------------------------------------------------
# running one arm on one task
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class TaskRow:
    """One arm on one fresh task.  All coordinates, no wall clock."""

    arm: str
    task_set: str
    task_id: str
    role: str
    entailed: bool
    solved: bool
    correct: bool
    depth: int
    macro_fired: bool
    macro_ids: tuple[str, ...]
    trace_length: int
    archive_hit: bool
    work_total: int
    resolution_attempts: int
    macro_match_attempts: int
    subsumption_checks: int
    checker_assignments: int
    redundant_sound_matches: int
    polarity_blind_matches: int
    polarity_blind_refuted: int

    def as_dict(self) -> dict:
        return {
            "arm": self.arm, "task_set": self.task_set, "task_id": self.task_id,
            "role": self.role, "entailed": self.entailed, "solved": self.solved,
            "correct": self.correct, "depth": self.depth,
            "macro_fired": self.macro_fired, "macro_ids": list(self.macro_ids),
            "trace_length": self.trace_length, "archive_hit": self.archive_hit,
            "work_total": self.work_total,
            "resolution_attempts": self.resolution_attempts,
            "macro_match_attempts": self.macro_match_attempts,
            "subsumption_checks": self.subsumption_checks,
            "checker_assignments": self.checker_assignments,
            "redundant_sound_matches": self.redundant_sound_matches,
            "polarity_blind_matches": self.polarity_blind_matches,
            "polarity_blind_refuted": self.polarity_blind_refuted,
        }


def run_arm(parent: ParentResult, task_set: str, task: Task) -> TaskRow:
    """One arm on one task, with the independent checker consulted separately.

    The checker is called by the evaluator, not by the arm, and its 256
    assignment evaluations are reported in their own coordinate.  They are not
    part of ``work_total``: every arm pays exactly the same verification cost on
    exactly the same tasks, so folding it into the comparison would only dilute
    whatever difference exists.
    """
    truth = entails(task.premises, task.query)
    archive_hit = False
    replay = None
    if parent.archive:
        replay = replay_from_archive(parent.archive, task.premises, task.query)
        archive_hit = replay is not None
    if replay is not None:
        res = replay
    else:
        res = solve(task.premises, task.query, parent.library, MAX_SEARCH_DEPTH,
                    check_answer=False, relevance_index=parent.relevance_index)
        if parent.archive:
            # the archive was consulted and missed; the look is still charged
            res.work.add(_archive_lookup_cost(parent))
    redundant = sum(
        redundant_sound_matches(s, task.premises, task.query)
        for s in parent.library)
    pb_matches, pb_refuted = polarity_blind_refutations(
        CHAIN_SCHEMA, task.premises)
    return TaskRow(
        arm=parent.name, task_set=task_set, task_id=task.task_id, role=task.role,
        entailed=truth, solved=res.solved, correct=(res.solved == truth),
        depth=res.depth, macro_fired=res.macro_fired,
        macro_ids=tuple(res.macro_ids), trace_length=len(res.trace),
        archive_hit=archive_hit, work_total=res.work.total,
        resolution_attempts=res.work.resolution_attempts,
        macro_match_attempts=res.work.macro_match_attempts,
        subsumption_checks=res.work.subsumption_checks,
        checker_assignments=256, redundant_sound_matches=redundant,
        polarity_blind_matches=pb_matches, polarity_blind_refuted=pb_refuted)


def _archive_lookup_cost(parent: ParentResult):
    """The miss cost of consulting an archive that did not hit."""
    from libdisc import SearchWork

    w = SearchWork()
    w.subsumption_checks += len(parent.archive)
    return w


# --------------------------------------------------------------------------
# the sweep
# --------------------------------------------------------------------------


def sweep(views: Sequence[LearnerView] | None = None) -> dict:
    """Every arm on every task set, plus the removal ablation on the arm."""
    views = list(learner_views()) if views is None else list(views)
    out: dict = {"arms": {}, "rows": []}
    for builder in ARMS:
        parent = builder(views)
        out["arms"][parent.name] = parent.as_dict()
        for set_name, tasks in TASK_SETS.items():
            for task in tasks:
                out["rows"].append(run_arm(parent, set_name, task).as_dict())
    # removal ablation on the arm under test: delete the composite and the
    # advantage must disappear, which is the last link of the causal chain.
    arm = discovery_arm(views)
    stripped = ParentResult(
        "libdisc_discovery_arm_schema_removed",
        tuple(s for s in arm.library if s.step_count < 2),
        arm.relevance_index, (),
        "the arm under test with the composite schema deleted from the store",
        {"removed": len(arm.applicable)})
    out["arms"][stripped.name] = stripped.as_dict()
    for set_name, tasks in TASK_SETS.items():
        for task in tasks:
            out["rows"].append(run_arm(stripped, set_name, task).as_dict())
    return out


def summarise(sweep_out: dict) -> dict:
    """Per-arm, per-set totals.  The two headline sets are never pooled."""
    table: dict = {}
    for row in sweep_out["rows"]:
        arm = table.setdefault(row["arm"], {})
        s = arm.setdefault(row["task_set"], {
            "tasks": 0, "work_total": 0, "macro_match_attempts": 0,
            "solved": 0, "correct": 0, "macro_fired": 0, "wrong_answers": 0,
            "redundant_sound_matches": 0, "archive_hits": 0,
            "per_task_work": {},
        })
        s["tasks"] += 1
        s["work_total"] += row["work_total"]
        s["macro_match_attempts"] += row["macro_match_attempts"]
        s["solved"] += int(row["solved"])
        s["correct"] += int(row["correct"])
        s["macro_fired"] += int(row["macro_fired"])
        s["wrong_answers"] += int(not row["correct"])
        s["redundant_sound_matches"] += row["redundant_sound_matches"]
        s["archive_hits"] += int(row["archive_hit"])
        s["per_task_work"][row["task_id"]] = row["work_total"]
    return table


def benefit_table(summary: dict, reference: str = "reset_arm") -> dict:
    """Work saved against the reset arm, per set, never pooled across sets."""
    out: dict = {}
    ref = summary[reference]
    for arm, sets in summary.items():
        out[arm] = {}
        for set_name, s in sets.items():
            base = ref[set_name]["work_total"]
            out[arm][set_name] = {
                "work_total": s["work_total"],
                "reset_arm_work_total": base,
                "delta_vs_reset": base - s["work_total"],
                "ratio_vs_reset": (
                    round(s["work_total"] / base, 4) if base else None),
                "tasks_helped": sum(
                    1 for tid, w in s["per_task_work"].items()
                    if w < ref[set_name]["per_task_work"][tid]),
                "tasks_harmed": sum(
                    1 for tid, w in s["per_task_work"].items()
                    if w > ref[set_name]["per_task_work"][tid]),
            }
    return out


# --------------------------------------------------------------------------
# custody: CL-T1, with a real operating-system process boundary
# --------------------------------------------------------------------------

#: The interpreter flags every custody child is launched with.  ``-I`` isolates
#: it from the environment, ``-S`` skips ``site``, ``-B`` writes no bytecode.
CHILD_FLAGS = ("-I", "-S", "-B")

#: Seconds a custody child may run before it is killed and the run is void.
CHILD_TIMEOUT = 300

#: The environment handed to a custody child.  Nothing from this process's
#: environment reaches it, which is CL-T1 clause 5: no environment variable may
#: carry a value derived from the acquiring process.
CHILD_ENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C"}


def _child(argv: list[str]) -> subprocess.CompletedProcess:
    here = pathlib.Path(__file__).resolve()
    return subprocess.run(
        [sys.executable, *CHILD_FLAGS, str(here), *argv],
        capture_output=True, text=True, timeout=CHILD_TIMEOUT, env=dict(CHILD_ENV),
        cwd=str(here.parent), check=False)


def _acquire(state_path: str, report_path: str) -> int:
    """Child half one: learn, certify, serialize, EXIT."""
    views = learner_views()
    result = discover(views)
    state = {
        "library": [d.schema.body for d in result.pool],
        "admissions": [d.admission.as_dict() for d in result.pool],
        "funnel": result.funnel,
        "ablation_pool": flat_mining_ablation(views).funnel["pool"],
    }
    body = json.dumps(state, sort_keys=True, separators=(",", ":"))
    pathlib.Path(state_path).write_text(body)
    report = {
        "phase": "acquire",
        "pid": os.getpid(),
        "state_digest": digest_of(state),
        "state_bytes": len(body),
        "schemas": [d.schema.schema_id for d in result.pool],
        "applicable": [
            d.schema.schema_id for d in result.pool if d.schema.step_count >= 2],
        "funnel": result.funnel,
    }
    pathlib.Path(report_path).write_text(json.dumps(report, indent=1))
    return 0


def _use(state_path: str, report_path: str, drop: str | None) -> int:
    """Child half two: read the state a DIFFERENT process wrote, then solve."""
    state = json.loads(pathlib.Path(state_path).read_text())
    library = tuple(schema_from_body(b) for b in state["library"])
    if drop:
        library = tuple(s for s in library if s.schema_id != drop)
    parent = ParentResult(
        "custody_reader" + ("_schema_removed" if drop else ""),
        library, True, (), "library read from disk after a real restart", {})
    rows = [
        run_arm(parent, set_name, task).as_dict()
        for set_name, tasks in TASK_SETS.items()
        for task in tasks
    ]
    report = {
        "phase": "use",
        "pid": os.getpid(),
        "state_digest": digest_of(state),
        "library": [s.schema_id for s in library],
        "dropped": drop,
        "rows": rows,
    }
    pathlib.Path(report_path).write_text(json.dumps(report, indent=1))
    return 0


def custody_cycle(workdir: str | None = None) -> dict:
    """Drive the full chain across three real processes and record the receipt.

    Process A acquires and exits.  Process B reads the file A left behind and
    solves the fresh tasks.  Process C does the same with the composite schema
    deleted, which is the removal ablation performed across the same boundary
    rather than in memory.  This orchestrator never passes an in-process object
    to any of them: the only channel is the state file, and its digest is
    recorded on both sides.
    """
    tmp = tempfile.TemporaryDirectory(prefix="libdisc-custody-") if workdir is None \
        else None
    root = pathlib.Path(workdir) if workdir else pathlib.Path(tmp.name)
    root.mkdir(parents=True, exist_ok=True)
    state = root / "library_state.json"
    ra, rb, rc = (root / f"report_{x}.json" for x in "abc")
    try:
        pa = _child(["acquire", str(state), str(ra)])
        if pa.returncode != 0:
            return {"terminal": "CUSTODY_VIOLATION",
                    "reason": "the acquiring process did not exit cleanly",
                    "stderr": pa.stderr[-2000:]}
        report_a = json.loads(ra.read_text())
        digest_before = digest_of(json.loads(state.read_text()))

        applicable = report_a["applicable"]
        pb = _child(["use", str(state), str(rb)])
        if pb.returncode != 0:
            return {"terminal": "CUSTODY_VIOLATION",
                    "reason": "the reading process failed",
                    "stderr": pb.stderr[-2000:]}
        report_b = json.loads(rb.read_text())

        drop = applicable[0] if applicable else "none"
        pc = _child(["use", str(state), str(rc), drop])
        report_c = json.loads(rc.read_text()) if pc.returncode == 0 else None
        digest_after = digest_of(json.loads(state.read_text()))

        return {
            "pid_orchestrator": os.getpid(),
            "pid_before": report_a["pid"],
            "pid_after": report_b["pid"],
            "pid_ablation": report_c["pid"] if report_c else None,
            "distinct_pids": len({
                report_a["pid"], report_b["pid"],
                report_c["pid"] if report_c else -1}),
            "acquire_exit_status": pa.returncode,
            "use_exit_status": pb.returncode,
            "ablation_exit_status": pc.returncode,
            "state_digest_before": digest_before,
            "state_digest_after": digest_after,
            "state_digest_acquire_child": report_a["state_digest"],
            "state_digest_use_child": report_b["state_digest"],
            "digests_agree": (
                digest_before == digest_after == report_a["state_digest"]
                == report_b["state_digest"]),
            "state_bytes": report_a["state_bytes"],
            "state_path": str(state),
            "interpreter_flags": list(CHILD_FLAGS),
            "child_environment": dict(CHILD_ENV),
            "schemas_persisted": report_a["schemas"],
            "applicable_persisted": applicable,
            "dropped_in_ablation": drop,
            "rows_after_restart": report_b["rows"],
            "rows_after_restart_schema_removed": (
                report_c["rows"] if report_c else []),
            "terminal": (
                "CUSTODY_VIOLATION"
                if report_a["pid"] == report_b["pid"] else "CUSTODY_OK"),
        }
    finally:
        if tmp is not None:
            tmp.cleanup()


def custody_benefit(custody: dict) -> dict:
    """Work per set after the restart, with and without the schema."""
    def totals(rows):
        out: dict = {}
        for r in rows:
            s = out.setdefault(r["task_set"], {"work_total": 0, "macro_fired": 0,
                                               "tasks": 0, "correct": 0})
            s["work_total"] += r["work_total"]
            s["macro_fired"] += int(r["macro_fired"])
            s["tasks"] += 1
            s["correct"] += int(r["correct"])
        return out

    with_schema = totals(custody.get("rows_after_restart", []))
    without = totals(custody.get("rows_after_restart_schema_removed", []))
    return {
        "with_schema": with_schema,
        "with_schema_removed": without,
        "delta_by_set": {
            k: without.get(k, {}).get("work_total", 0) - v["work_total"]
            for k, v in with_schema.items()
        },
    }


# --------------------------------------------------------------------------
# child entry point
# --------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: libdisc_arms.py acquire|use <state> <report> [drop_id]",
              file=sys.stderr)
        return 2
    verb, rest = argv[0], argv[1:]
    if verb == "acquire" and len(rest) == 2:
        return _acquire(rest[0], rest[1])
    if verb == "use" and len(rest) in (2, 3):
        return _use(rest[0], rest[1], rest[2] if len(rest) == 3 else None)
    print(f"unknown invocation: {argv}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

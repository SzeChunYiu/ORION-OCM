"""Prospective G2 causal-reuse test on a length-scaling polynomial ecology.

This is research-only. It uses the repository's existing exact polynomial learner,
solver, checker, OCM admission and revocation paths. The task partition is based
only on mathematical task identity and a frozen hash salt, never measured solve
outcomes.

Claim ceiling: bounded causal method reuse / negative terminal at this ecology.
No architecture net-benefit, cross-domain, or general-learning claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from itertools import product
from pathlib import Path
import tempfile

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"

import sys
sys.path.insert(0, str(SRC))

from ocm.learning import methods as M
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel
from ocm.kso.types import Scope

METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
VALIDATION_SALT = "orion-ocm-g2-length5-validation-v1"
TEST_SALT = "orion-ocm-g2-length6-test-v1"
VALIDATION_N = 32
TEST_N = 64
VALIDATION_BUDGET = M.SearchBudget(slots=200_000, max_length=5)
TEST_BUDGET = M.SearchBudget(slots=200_000, max_length=6)
TRAIN_BUDGET = M.SearchBudget(slots=1_000, max_length=4)

TRAINING_TASKS = (
    M.PolynomialTask("train-a", (2, 2, 1)),
    M.PolynomialTask("train-b", (2, 4, 2)),
)
LEGACY_VALIDATION = (
    M.PolynomialTask("validation-a", (0, 2, 1)),
    M.PolynomialTask("validation-b", (1, 4, 6, 4, 1)),
)


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def stable_rank(salt: str, fingerprint: str) -> str:
    return hashlib.sha256((salt + "\0" + fingerprint).encode()).hexdigest()


def minimal_length_population(max_length: int = 6):
    """Map each reachable polynomial fingerprint to its minimum primitive length."""
    best = {}
    for length in range(max_length + 1):
        for program in product(M.PRIMITIVES, repeat=length):
            task = M.PolynomialTask(f"length-{length}", M.normal_form(program))
            best.setdefault(task.fingerprint, (length, task))
    return best


def frozen_partition():
    excluded = {t.fingerprint for t in TRAINING_TASKS + LEGACY_VALIDATION}
    population = minimal_length_population(6)
    validation_pool = [
        task for fp, (length, task) in population.items()
        if length == 5 and fp not in excluded
    ]
    test_pool = [
        task for fp, (length, task) in population.items()
        if length == 6 and fp not in excluded
    ]
    validation = tuple(sorted(
        validation_pool,
        key=lambda t: (stable_rank(VALIDATION_SALT, t.fingerprint), t.fingerprint),
    )[:VALIDATION_N])
    test = tuple(sorted(
        test_pool,
        key=lambda t: (stable_rank(TEST_SALT, t.fingerprint), t.fingerprint),
    )[:TEST_N])
    if len(validation) != VALIDATION_N or len(test) != TEST_N:
        raise RuntimeError("frozen population too small")
    ids = [t.fingerprint for t in validation + test]
    if len(set(ids)) != len(ids):
        raise RuntimeError("validation/test overlap")
    return validation, test


class StreamTrace:
    def __init__(self):
        self.events = []

    def solve(self, task, budget, method=M.GeneratorMethod()):
        orig_primitive = M._primitive_programs
        orig_guided = M._guided_programs

        def primitive(max_length):
            for program in orig_primitive(max_length):
                self.events.append(("primitive", tuple(program)))
                yield program

        def guided(given_method, max_length):
            for program in orig_guided(given_method, max_length):
                self.events.append(("guided", tuple(program)))
                yield program

        M._primitive_programs = primitive
        M._guided_programs = guided
        try:
            result = M.solve(task, budget, method)
        finally:
            M._primitive_programs = orig_primitive
            M._guided_programs = orig_guided

        origin = None
        if result.program is not None:
            target = tuple(result.program)
            for source, program in self.events:
                if program == target:
                    origin = source
                    break
        return result, origin


def checked_solve(task, budget, method=M.GeneratorMethod()):
    trace = StreamTrace()
    result, origin = trace.solve(task, budget, method)
    if not M.verify_solution(task, result):
        raise RuntimeError("exact polynomial verification failed")
    return result, origin


def learn_fixed_method():
    training = []
    search_slots = 0
    for task in TRAINING_TASKS:
        result, _ = checked_solve(task, TRAIN_BUDGET)
        training.append((task, result))
        search_slots += result.slots
    method = M.learn_generator(training)
    if not method.fragments:
        raise RuntimeError("frozen training no longer yields a fragment")
    return tuple(training), method, search_slots


def utility_gate(method, validation):
    rows = []
    baseline_total = 0
    candidate_total = 0
    for task in validation:
        baseline, _ = checked_solve(task, VALIDATION_BUDGET)
        candidate, origin = checked_solve(task, VALIDATION_BUDGET, method)
        baseline_total += baseline.slots
        candidate_total += candidate.slots
        rows.append({
            "task": task.fingerprint,
            "baseline_slots": baseline.slots,
            "candidate_slots": candidate.slots,
            "delta_slots": baseline.slots - candidate.slots,
            "candidate_origin": origin,
            "candidate_program": candidate.program,
        })
    accepted = candidate_total < baseline_total
    return {
        "schema": "g2.length-scaling.utility-gate.v1",
        "accepted": accepted,
        "baseline_total_slots": baseline_total,
        "candidate_total_slots": candidate_total,
        "slot_saving": baseline_total - candidate_total,
        "harmful_tasks": sum(1 for r in rows if r["candidate_slots"] > r["baseline_slots"]),
        "strict_improvement_tasks": sum(1 for r in rows if r["candidate_slots"] < r["baseline_slots"]),
        "guided_wins": sum(
            1 for r in rows
            if r["candidate_origin"] == "guided" and r["candidate_slots"] < r["baseline_slots"]
        ),
        "rows": rows,
        "rule": "accept iff aggregate candidate search slots < aggregate primitive slots on all 32 frozen length-5 validation tasks",
    }


def save_method(path: Path, method: M.GeneratorMethod):
    payload = {
        "fragments": [list(p) for p in method.fragments],
        "training_tasks": list(method.training_tasks),
        "fingerprint": method.fingerprint,
    }
    tmp = path.with_suffix(".tmp")
    with tmp.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def load_method(path: Path):
    payload = json.loads(path.read_text())
    method = M.GeneratorMethod(
        tuple(tuple(p) for p in payload["fragments"]),
        tuple(payload["training_tasks"]),
    )
    if method.fingerprint != payload["fingerprint"]:
        raise RuntimeError("ordinary method persistence identity mismatch")
    return method


def prepare_ocm(root: Path, training, gate, revoke=False):
    rt = OCMRuntime(root)
    receipt = M.admit_generator(rt, training, LEGACY_VALIDATION, TRAIN_BUDGET)
    _, utility_evidence = rt.admit_evidence(
        gate,
        Channel.OBSERVATION,
        "g2-length-scaling-utility.v1",
        scope=Scope.of("polynomial-length-scaling.v1"),
    )
    if revoke:
        rt.revoke((receipt["training"][0]["evidence_id"],))
    rt.persist()
    replay = OCMRuntime(root)
    if revoke:
        try:
            M.load_generator(replay, receipt["generator_id"])
        except ValueError:
            return M.GeneratorMethod(), receipt, utility_evidence
        raise RuntimeError("revoked OCM generator remained live")
    method = M.load_generator(replay, receipt["generator_id"])
    return method, receipt, utility_evidence


def run_test_tasks(tasks, method):
    rows = []
    total = 0
    for task in tasks:
        result, origin = checked_solve(task, TEST_BUDGET, method)
        total += result.slots
        rows.append({
            "task": task.fingerprint,
            "slots": result.slots,
            "program": result.program,
            "origin": origin,
            "method": method.fingerprint,
        })
    return rows, total


def compare_rows(baseline_rows, candidate_rows):
    by_base = {r["task"]: r for r in baseline_rows}
    guided_wins = 0
    strict = 0
    harmful = 0
    for row in candidate_rows:
        base = by_base[row["task"]]
        if row["slots"] < base["slots"]:
            strict += 1
            if row["origin"] == "guided":
                guided_wins += 1
        elif row["slots"] > base["slots"]:
            harmful += 1
    return {"strict_improvement_tasks": strict, "harmful_tasks": harmful, "guided_wins": guided_wins}


def run():
    method_path = SRC / "ocm" / "learning" / "methods.py"
    observed_blob = git_blob_sha1(method_path)
    if observed_blob != METHOD_BLOB:
        raise RuntimeError(f"method source drift: {observed_blob}")

    validation, test = frozen_partition()
    training, learned, training_slots = learn_fixed_method()
    legacy = M.validate_generator(learned, LEGACY_VALIDATION, TRAIN_BUDGET)
    if not legacy["accepted"]:
        raise RuntimeError("legacy admission control no longer accepts frozen method")
    legacy_slots = sum(
        row[which]["slots"]
        for row in legacy["held_out"]
        for which in ("baseline", "candidate")
    )
    gate = utility_gate(learned, validation)

    with tempfile.TemporaryDirectory(prefix="ocm-g2-length-scaling-") as temp:
        root = Path(temp)
        ordinary_path = root / "ordinary-method.json"
        save_method(ordinary_path, learned)
        ordinary_loaded = load_method(ordinary_path)
        ordinary_deployed = ordinary_loaded if gate["accepted"] else M.GeneratorMethod()

        ocm_live, receipt, utility_evidence = prepare_ocm(
            root / "ocm-live", training, gate, revoke=False
        )
        if not gate["accepted"]:
            ocm_live = M.GeneratorMethod()
        ocm_revoked, revoked_receipt, _ = prepare_ocm(
            root / "ocm-revoked", training, gate, revoke=True
        )

        baseline_rows, baseline_total = run_test_tasks(test, M.GeneratorMethod())
        ordinary_rows, ordinary_total = run_test_tasks(test, ordinary_deployed)
        ocm_rows, ocm_total = run_test_tasks(test, ocm_live)
        revoked_rows, revoked_total = run_test_tasks(test, ocm_revoked)

    ordinary_cmp = compare_rows(baseline_rows, ordinary_rows)
    ocm_cmp = compare_rows(baseline_rows, ocm_rows)
    revoked_equal = all(
        a["slots"] == b["slots"] and tuple(a["program"]) == tuple(b["program"])
        for a, b in zip(baseline_rows, revoked_rows)
    )
    transplant_equal = all(
        a["slots"] == b["slots"] and tuple(a["program"]) == tuple(b["program"])
        for a, b in zip(ordinary_rows, ocm_rows)
    )

    predeployment_slots = training_slots + legacy_slots + gate["baseline_total_slots"] + gate["candidate_total_slots"]
    learned_lifetime_slots = predeployment_slots + ocm_total
    primitive_lifetime_slots = baseline_total

    if not revoked_equal:
        terminal = "CANNOT_CHECK_REVOCATION_ABLATION"
        causal = False
    elif not transplant_equal:
        terminal = "CANNOT_CHECK_COMPONENT_TRANSPLANT_PARITY"
        causal = False
    elif not gate["accepted"]:
        terminal = "UTILITY_GATE_REJECTS_METHOD"
        causal = False
    elif ocm_cmp["guided_wins"] <= 0:
        terminal = "NO_CAUSAL_METHOD_CONSUMPTION"
        causal = False
    elif ocm_total >= baseline_total:
        terminal = "NO_AMORTIZED_SEARCH_ON_LENGTH6_TEST"
        causal = False
    else:
        terminal = "CAUSAL_METHOD_REUSE_SUPPORTED_AT_LENGTH6"
        causal = True

    lifetime_terminal = (
        "LIFETIME_SEARCH_SLOTS_PAYBACK_AT_64_TEST_TASKS"
        if learned_lifetime_slots < primitive_lifetime_slots
        else "NO_LIFETIME_SEARCH_SLOTS_PAYBACK_AT_64_TEST_TASKS"
    )

    return {
        "schema": "g2.length-scaling.result.v1",
        "terminal": terminal,
        "causal_method_reuse_supported": causal,
        "lifetime_terminal": lifetime_terminal,
        "method_blob": METHOD_BLOB,
        "method_fingerprint": learned.fingerprint,
        "fragments": [list(p) for p in learned.fragments],
        "partition": {
            "validation_n": len(validation),
            "test_n": len(test),
            "validation_min_primitive_length": 5,
            "test_min_primitive_length": 6,
            "validation_salt": VALIDATION_SALT,
            "test_salt": TEST_SALT,
            "validation_ids": [t.fingerprint for t in validation],
            "test_ids": [t.fingerprint for t in test],
        },
        "utility_gate": gate,
        "test": {
            "primitive_total_slots": baseline_total,
            "ordinary_total_slots": ordinary_total,
            "ocm_total_slots": ocm_total,
            "revoked_total_slots": revoked_total,
            "ordinary_comparison": ordinary_cmp,
            "ocm_comparison": ocm_cmp,
            "revoked_equals_primitive": revoked_equal,
            "ordinary_equals_ocm": transplant_equal,
            "baseline_rows": baseline_rows,
            "ordinary_rows": ordinary_rows,
            "ocm_rows": ocm_rows,
            "revoked_rows": revoked_rows,
        },
        "accounting": {
            "training_slots": training_slots,
            "legacy_validation_slots": legacy_slots,
            "population_validation_slots_both_arms": gate["baseline_total_slots"] + gate["candidate_total_slots"],
            "predeployment_slots": predeployment_slots,
            "primitive_test_slots": primitive_lifetime_slots,
            "learned_test_plus_predeployment_slots": learned_lifetime_slots,
            "note": "Search-slot accounting only; wall/CPU/storage/provenance remain separate and no whole-architecture benefit is claimed.",
        },
        "ocm": {
            "generator_id": receipt["generator_id"],
            "utility_evidence": utility_evidence,
            "revoked_generator_id": revoked_receipt["generator_id"],
            "restart_before_test": True,
            "support_withdrawal_ablation": True,
        },
        "claim_boundary": (
            "Bounded causal method reuse in the registered polynomial length-scaling ecology only. "
            "No architecture net benefit, general learning, cross-domain transfer, or protected external replication."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, sort_keys=True, indent=2)
        handle.write("\n")
    print(json.dumps({
        "terminal": result["terminal"],
        "lifetime_terminal": result["lifetime_terminal"],
        "gate": result["utility_gate"]["accepted"],
        "guided_wins": result["test"]["ocm_comparison"]["guided_wins"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

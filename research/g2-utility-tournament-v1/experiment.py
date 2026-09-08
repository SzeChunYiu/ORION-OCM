"""Prospective exact utility-aware fragment tournament for #165 G2.4.

Research-only. Candidate construction uses training solutions only. Candidate
selection uses a disjoint validation stratum. The test stratum is untouched until
a method (or no method) is frozen by that rule.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from itertools import product
import json
import os
from pathlib import Path
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
sys.path.insert(0, str(SRC))

from ocm.kso.ids import content_hash
from ocm.kso.space import Atom
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.learning import methods as M
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
TRAIN_SALT = "orion-ocm-g2-utility-training-v1"
VALIDATION_SALT = "orion-ocm-g2-utility-validation-v1"
TEST_SALT = "orion-ocm-g2-utility-test-v1"
TRAIN_N = 48
VALIDATION_N = 32
TEST_N = 64
CANDIDATE_CAP = 16
MIN_SUPPORT = 2
FRAGMENT_MIN_LENGTH = 2
FRAGMENT_MAX_LENGTH = 4
TRAIN_BUDGET = M.SearchBudget(slots=200_000, max_length=5)
VALIDATION_BUDGET = M.SearchBudget(slots=200_000, max_length=6)
TEST_BUDGET = M.SearchBudget(slots=200_000, max_length=7)
SCOPE = Scope.of("polynomial-utility-tournament.v1")


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def stable_rank(salt: str, fingerprint: str) -> str:
    return hashlib.sha256((salt + "\0" + fingerprint).encode()).hexdigest()


def minimal_length_population(max_length: int = 7):
    best = {}
    for length in range(max_length + 1):
        for program in product(M.PRIMITIVES, repeat=length):
            task = M.PolynomialTask(f"length-{length}", M.normal_form(program))
            best.setdefault(task.fingerprint, (length, task))
    return best


def take_stratum(population, length: int, salt: str, n: int):
    pool = [task for _fp, (minimum, task) in population.items() if minimum == length]
    chosen = tuple(sorted(
        pool,
        key=lambda task: (stable_rank(salt, task.fingerprint), task.fingerprint),
    )[:n])
    if len(chosen) != n:
        raise RuntimeError(f"minimum-length-{length} population too small")
    return chosen


def frozen_partition():
    population = minimal_length_population(7)
    training = take_stratum(population, 5, TRAIN_SALT, TRAIN_N)
    validation = take_stratum(population, 6, VALIDATION_SALT, VALIDATION_N)
    test = take_stratum(population, 7, TEST_SALT, TEST_N)
    all_ids = [task.fingerprint for task in training + validation + test]
    if len(set(all_ids)) != len(all_ids):
        raise RuntimeError("partition overlap")
    return population, training, validation, test


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
        raise RuntimeError(f"exact solve failed for {task.fingerprint}: {result.status}")
    return result, origin


def solve_training(tasks):
    rows = []
    total = 0
    for task in tasks:
        result, _origin = checked_solve(task, TRAIN_BUDGET)
        total += result.slots
        rows.append((task, result))
    return tuple(rows), total


def proper_fragments(program):
    out = set()
    for start in range(len(program)):
        for end in range(start + FRAGMENT_MIN_LENGTH, min(len(program), start + FRAGMENT_MAX_LENGTH) + 1):
            fragment = tuple(program[start:end])
            if len(fragment) < len(program):
                out.add(fragment)
    return out


def candidate_pool(training_rows):
    support = Counter()
    for _task, result in training_rows:
        for fragment in proper_fragments(result.program):
            support[fragment] += 1
    ordered = sorted(
        (fragment for fragment, count in support.items() if count >= MIN_SUPPORT),
        key=lambda fragment: (-support[fragment], -len(fragment), fragment),
    )[:CANDIDATE_CAP]
    return tuple(ordered), {fragment: support[fragment] for fragment in ordered}


def baseline_validation(tasks):
    rows = []
    total = 0
    for task in tasks:
        result, origin = checked_solve(task, VALIDATION_BUDGET)
        rows.append({
            "task": task.fingerprint,
            "slots": result.slots,
            "program": result.program,
            "origin": origin,
        })
        total += result.slots
    return rows, total


def evaluate_candidate(fragment, training_ids, validation, baseline_rows, baseline_total):
    method = M.GeneratorMethod((fragment,), training_ids)
    rows = []
    total = 0
    baseline = {row["task"]: row for row in baseline_rows}
    strict = harmful = guided_wins = 0
    for task in validation:
        result, origin = checked_solve(task, VALIDATION_BUDGET, method)
        total += result.slots
        base = baseline[task.fingerprint]
        if result.slots < base["slots"]:
            strict += 1
            if origin == "guided":
                guided_wins += 1
        elif result.slots > base["slots"]:
            harmful += 1
        rows.append({
            "task": task.fingerprint,
            "slots": result.slots,
            "program": result.program,
            "origin": origin,
            "delta_slots": base["slots"] - result.slots,
        })
    return {
        "fragment": fragment,
        "method": method.fingerprint,
        "aggregate_slots": total,
        "baseline_aggregate_slots": baseline_total,
        "saving": baseline_total - total,
        "strict_improvement_tasks": strict,
        "harmful_tasks": harmful,
        "guided_wins": guided_wins,
        "rows": rows,
    }


def tournament(training_rows, validation):
    candidates, support = candidate_pool(training_rows)
    baseline_rows, baseline_total = baseline_validation(validation)
    training_ids = tuple(sorted(task.fingerprint for task, _result in training_rows))
    evaluations = []
    for fragment in candidates:
        row = evaluate_candidate(
            fragment, training_ids, validation, baseline_rows, baseline_total
        )
        row["support"] = support[fragment]
        evaluations.append(row)
    if not candidates:
        return {
            "terminal": "NO_REPEATED_FRAGMENT_CANDIDATES",
            "accepted": False,
            "selected": None,
            "candidate_order": [],
            "baseline_rows": baseline_rows,
            "baseline_aggregate_slots": baseline_total,
            "evaluations": [],
        }
    # evaluations are already in the frozen candidate-order tie break.
    selected = min(enumerate(evaluations), key=lambda item: (item[1]["aggregate_slots"], item[0]))[1]
    accepted = selected["aggregate_slots"] < baseline_total
    return {
        "terminal": "UTILITY_TOURNAMENT_SELECTED_METHOD" if accepted else "UTILITY_TOURNAMENT_SELECTS_NO_METHOD",
        "accepted": accepted,
        "selected": selected,
        "candidate_order": [fragment for fragment in candidates],
        "baseline_rows": baseline_rows,
        "baseline_aggregate_slots": baseline_total,
        "evaluations": evaluations,
    }


def ordinary_persist(path: Path, method: M.GeneratorMethod):
    payload = {
        "fragments": [list(fragment) for fragment in method.fragments],
        "training_tasks": list(method.training_tasks),
        "fingerprint": method.fingerprint,
    }
    temp = path.with_suffix(".tmp")
    with temp.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def ordinary_load(path: Path):
    payload = json.loads(path.read_text())
    method = M.GeneratorMethod(
        tuple(tuple(fragment) for fragment in payload["fragments"]),
        tuple(payload["training_tasks"]),
    )
    if method.fingerprint != payload["fingerprint"]:
        raise RuntimeError("ordinary persistence identity mismatch")
    return method


def admit_selected_method(root: Path, method, training_receipt, tournament_receipt, revoke=False):
    runtime = OCMRuntime(root)
    _training_record, training_evidence = runtime.admit_evidence(
        training_receipt,
        Channel.PROOF,
        "g2-utility-tournament-training.v1",
        scope=SCOPE,
    )
    _utility_record, utility_evidence = runtime.admit_evidence(
        tournament_receipt,
        Channel.OBSERVATION,
        "g2-utility-tournament-validation.v1",
        scope=SCOPE,
    )
    warrant = WarrantProfile.of({training_evidence, utility_evidence})
    payload = {
        "kind": "generator.utility-tournament.v1",
        "fragments": method.fragments,
        "training_tasks": method.training_tasks,
        "fingerprint": method.fingerprint,
    }
    atom_id = "generator-tournament:" + content_hash(payload)
    runtime.admit_object(
        Atom(
            atom_id,
            "procedure",
            warrant,
            scope=SCOPE,
            content_ref=content_hash(payload),
            meta=tuple(payload.items()),
        ),
        (),
        "OBSERVATION",
    )
    if revoke:
        runtime.revoke((training_evidence,))
    runtime.persist()
    replay = OCMRuntime(root)
    atom = replay.state.ks.atom_map().get(atom_id)
    if revoke:
        if atom is not None and atom.liveness(replay.state.revoked) is Liveness.LIVE:
            raise RuntimeError("revoked selected method remained live")
        return M.GeneratorMethod(), atom_id, training_evidence, utility_evidence
    if atom is None or atom.liveness(replay.state.revoked) is not Liveness.LIVE:
        raise RuntimeError("selected OCM method did not survive restart")
    stored = dict(atom.meta)
    if atom.content_ref != content_hash(stored):
        raise RuntimeError("selected OCM method content identity mismatch")
    loaded = M.GeneratorMethod(
        tuple(tuple(fragment) for fragment in stored["fragments"]),
        tuple(stored["training_tasks"]),
    )
    if loaded.fingerprint != stored["fingerprint"]:
        raise RuntimeError("selected OCM method fingerprint mismatch")
    return loaded, atom_id, training_evidence, utility_evidence


def run_test(tasks, method):
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
        })
    return rows, total


def compare(baseline_rows, candidate_rows):
    baseline = {row["task"]: row for row in baseline_rows}
    strict = harmful = guided_wins = 0
    for row in candidate_rows:
        base = baseline[row["task"]]
        if row["slots"] < base["slots"]:
            strict += 1
            if row["origin"] == "guided":
                guided_wins += 1
        elif row["slots"] > base["slots"]:
            harmful += 1
    return {
        "strict_improvement_tasks": strict,
        "harmful_tasks": harmful,
        "guided_wins": guided_wins,
    }


def exact_rows_equal(a_rows, b_rows):
    return all(
        a["task"] == b["task"]
        and a["slots"] == b["slots"]
        and tuple(a["program"]) == tuple(b["program"])
        for a, b in zip(a_rows, b_rows)
    )


def run():
    method_path = SRC / "ocm" / "learning" / "methods.py"
    observed_blob = git_blob_sha1(method_path)
    if observed_blob != METHOD_BLOB:
        raise RuntimeError(f"method source drift: {observed_blob}")

    population, training_tasks, validation_tasks, test_tasks = frozen_partition()
    training_rows, training_slots = solve_training(training_tasks)
    tour = tournament(training_rows, validation_tasks)

    candidate_validation_slots = sum(row["aggregate_slots"] for row in tour["evaluations"])
    validation_search_slots = tour["baseline_aggregate_slots"] + candidate_validation_slots

    if not tour["accepted"]:
        selected_method = M.GeneratorMethod()
    else:
        selected_method = M.GeneratorMethod(
            (tuple(tour["selected"]["fragment"]),),
            tuple(sorted(task.fingerprint for task, _result in training_rows)),
        )

    training_receipt = {
        "schema": "g2.utility-tournament.training.v1",
        "source_blob": METHOD_BLOB,
        "training_ids": [task.fingerprint for task, _result in training_rows],
        "training_programs": [result.program for _task, result in training_rows],
        "candidate_order": tour["candidate_order"],
        "candidate_support": [row.get("support") for row in tour["evaluations"]],
        "selected_method": selected_method.fingerprint if selected_method.fragments else None,
    }
    tournament_receipt = {
        "schema": "g2.utility-tournament.validation.v1",
        "terminal": tour["terminal"],
        "accepted": tour["accepted"],
        "baseline_aggregate_slots": tour["baseline_aggregate_slots"],
        "selected": tour["selected"],
        "validation_ids": [task.fingerprint for task in validation_tasks],
    }

    with tempfile.TemporaryDirectory(prefix="ocm-g2-utility-") as temp_dir:
        root = Path(temp_dir)
        ordinary_path = root / "ordinary.json"
        if selected_method.fragments:
            ordinary_persist(ordinary_path, selected_method)
            ordinary_method = ordinary_load(ordinary_path)
            ocm_method, atom_id, training_evidence, utility_evidence = admit_selected_method(
                root / "ocm-live", selected_method, training_receipt, tournament_receipt, revoke=False
            )
            revoked_method, revoked_atom, _revoked_training, _revoked_utility = admit_selected_method(
                root / "ocm-revoked", selected_method, training_receipt, tournament_receipt, revoke=True
            )
        else:
            ordinary_method = M.GeneratorMethod()
            ocm_method = M.GeneratorMethod()
            revoked_method = M.GeneratorMethod()
            atom_id = revoked_atom = None
            training_evidence = utility_evidence = None

        primitive_rows, primitive_total = run_test(test_tasks, M.GeneratorMethod())
        ordinary_rows, ordinary_total = run_test(test_tasks, ordinary_method)
        ocm_rows, ocm_total = run_test(test_tasks, ocm_method)
        revoked_rows, revoked_total = run_test(test_tasks, revoked_method)

    ordinary_equal_ocm = exact_rows_equal(ordinary_rows, ocm_rows)
    revoked_equal_primitive = exact_rows_equal(revoked_rows, primitive_rows)
    ocm_cmp = compare(primitive_rows, ocm_rows)

    if not tour["accepted"]:
        terminal = tour["terminal"]
        causal = False
    elif not ordinary_equal_ocm:
        terminal = "CANNOT_CHECK_COMPONENT_TRANSPLANT_PARITY"
        causal = False
    elif not revoked_equal_primitive:
        terminal = "CANNOT_CHECK_REVOCATION_ABLATION"
        causal = False
    elif ocm_cmp["guided_wins"] <= 0:
        terminal = "NO_CAUSAL_METHOD_CONSUMPTION"
        causal = False
    elif ocm_total >= primitive_total:
        terminal = "NO_AMORTIZED_SEARCH_ON_LENGTH7_TEST"
        causal = False
    else:
        terminal = "CAUSAL_UTILITY_SELECTED_METHOD_REUSE_SUPPORTED_AT_LENGTH7"
        causal = True

    learned_path_slots = training_slots + validation_search_slots + ocm_total
    lifetime_terminal = (
        "LIFETIME_SEARCH_SLOTS_PAYBACK_AT_64_LENGTH7_TESTS"
        if tour["accepted"] and learned_path_slots < primitive_total
        else "NO_LIFETIME_SEARCH_SLOTS_PAYBACK_AT_64_LENGTH7_TESTS"
    )

    return {
        "schema": "g2.utility-tournament.result.v1",
        "terminal": terminal,
        "causal_method_reuse_supported": causal,
        "lifetime_terminal": lifetime_terminal,
        "method_blob": METHOD_BLOB,
        "partition": {
            "training_n": TRAIN_N,
            "validation_n": VALIDATION_N,
            "test_n": TEST_N,
            "training_min_length": 5,
            "validation_min_length": 6,
            "test_min_length": 7,
            "training_salt": TRAIN_SALT,
            "validation_salt": VALIDATION_SALT,
            "test_salt": TEST_SALT,
            "training_ids": [task.fingerprint for task in training_tasks],
            "validation_ids": [task.fingerprint for task in validation_tasks],
            "test_ids": [task.fingerprint for task in test_tasks],
            "population_counts": {
                str(length): sum(1 for minimum, _task in population.values() if minimum == length)
                for length in (5, 6, 7)
            },
        },
        "training": {
            "total_slots": training_slots,
            "rows": [
                {"task": task.fingerprint, "program": result.program, "slots": result.slots}
                for task, result in training_rows
            ],
        },
        "tournament": tour,
        "selected_method": {
            "fragments": [list(fragment) for fragment in selected_method.fragments],
            "fingerprint": selected_method.fingerprint if selected_method.fragments else None,
        },
        "test": {
            "primitive_total_slots": primitive_total,
            "ordinary_total_slots": ordinary_total,
            "ocm_total_slots": ocm_total,
            "revoked_total_slots": revoked_total,
            "ordinary_equals_ocm": ordinary_equal_ocm,
            "revoked_equals_primitive": revoked_equal_primitive,
            "comparison": ocm_cmp,
            "primitive_rows": primitive_rows,
            "ordinary_rows": ordinary_rows,
            "ocm_rows": ocm_rows,
            "revoked_rows": revoked_rows,
        },
        "accounting": {
            "training_slots": training_slots,
            "baseline_validation_slots": tour["baseline_aggregate_slots"],
            "all_candidate_validation_slots": candidate_validation_slots,
            "full_selection_validation_slots": validation_search_slots,
            "learned_path_through_test_slots": learned_path_slots,
            "primitive_test_slots": primitive_total,
            "note": "Search slots only. CPU/wall/storage/custody remain separate and no architecture net-benefit claim is licensed.",
        },
        "ocm": {
            "atom_id": atom_id,
            "revoked_atom_id": revoked_atom,
            "training_evidence": training_evidence,
            "utility_evidence": utility_evidence,
            "restart_before_test": bool(selected_method.fragments),
            "support_withdrawal_ablation": bool(selected_method.fragments),
        },
        "claim_boundary": (
            "Bounded causal reuse of a utility-selected exact fragment in one polynomial ecology only. "
            "The selector is a conventional parent mechanism; no architecture uniqueness, cross-domain, or whole-resource benefit claim."
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
    selected = result["selected_method"]["fragments"]
    print(json.dumps({
        "terminal": result["terminal"],
        "lifetime_terminal": result["lifetime_terminal"],
        "selected": selected,
        "guided_wins": result["test"]["comparison"]["guided_wins"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

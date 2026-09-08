"""Prospective G2 macro-operator serving study.

Research-only. Candidate construction uses training solutions only. Candidate
selection uses a disjoint validation stratum. The test stratum is untouched until
a macro (or no macro) is frozen by that rule.
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
import time

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
sys.path.insert(0, str(SRC))

from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.learning import methods as M
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
TRAIN_SALT = "orion-ocm-g2-macro-training-v1"
VALIDATION_SALT = "orion-ocm-g2-macro-validation-v1"
TEST_SALT = "orion-ocm-g2-macro-test-v1"
TRAIN_N = 48
VALIDATION_N = 32
TEST_N = 64
CANDIDATE_CAP = 16
MIN_SUPPORT = 2
FRAGMENT_MIN_LENGTH = 2
FRAGMENT_MAX_LENGTH = 4
TRAIN_BUDGET = M.SearchBudget(slots=200_000, max_length=6)
VALIDATION_MAX_PRIMITIVE_LENGTH = 7
TEST_MAX_PRIMITIVE_LENGTH = 8
SCOPE = Scope.of("polynomial-macro-operator.v1")
MACRO_TOKEN = "MACRO"


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def stable_rank(salt: str, fingerprint: str) -> str:
    return hashlib.sha256((salt + "\0" + fingerprint).encode()).hexdigest()


def minimal_length_population(max_length: int = 8):
    """Exact mathematical identities and their minimum primitive length."""
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
        raise RuntimeError(f"minimum-length-{length} population too small: {len(chosen)} < {n}")
    return chosen


def frozen_partition():
    population = minimal_length_population(8)
    training = take_stratum(population, 6, TRAIN_SALT, TRAIN_N)
    validation = take_stratum(population, 7, VALIDATION_SALT, VALIDATION_N)
    test = take_stratum(population, 8, TEST_SALT, TEST_N)
    ids = [task.fingerprint for task in training + validation + test]
    if len(ids) != len(set(ids)):
        raise RuntimeError("train/validation/test overlap")
    return population, training, validation, test


def solve_training(tasks):
    rows = []
    total_slots = 0
    for task in tasks:
        result = M.solve(task, TRAIN_BUDGET)
        if not M.verify_solution(task, result):
            raise RuntimeError(f"training solve failed: {task.fingerprint} {result.status}")
        rows.append((task, result))
        total_slots += result.slots
    return tuple(rows), total_slots


def proper_fragments(program):
    out = set()
    for start in range(len(program)):
        stop = min(len(program), start + FRAGMENT_MAX_LENGTH)
        for end in range(start + FRAGMENT_MIN_LENGTH, stop + 1):
            fragment = tuple(program[start:end])
            if len(fragment) < len(program):
                out.add(fragment)
    return out


def candidate_pool(training_rows):
    support = Counter()
    for _task, result in training_rows:
        for fragment in proper_fragments(result.program):
            support[fragment] += 1
    candidates = tuple(sorted(
        (fragment for fragment, count in support.items() if count >= MIN_SUPPORT),
        key=lambda fragment: (-support[fragment], -len(fragment), fragment),
    )[:CANDIDATE_CAP])
    return candidates, {fragment: support[fragment] for fragment in candidates}


def expand_tokens(token_word, macro):
    expanded = []
    used = False
    for token in token_word:
        if token == MACRO_TOKEN:
            if macro is None:
                raise ValueError("macro token without macro")
            expanded.extend(macro)
            used = True
        else:
            if token not in M.PRIMITIVES:
                raise ValueError(f"unknown token {token}")
            expanded.append(token)
    return tuple(expanded), used


def build_search_index(macro, max_primitive_length: int):
    """One exact BFS grammar index, counting token enumeration and unique checks.

    Every token word whose expanded primitive length is within the registered
    bound increments ``enumeration_attempts``. Duplicate tokenizations therefore
    cost work. Exact polynomial checking is charged only on the first occurrence
    of each expanded primitive program.
    """
    macro = tuple(macro) if macro is not None else None
    tokens = ((MACRO_TOKEN,) + M.PRIMITIVES) if macro is not None else M.PRIMITIVES
    seen_programs = set()
    first_by_coefficients = {}
    enumeration_attempts = 0
    unique_candidates_checked = 0

    # Minimum token expansion length is one primitive, so token depth beyond the
    # primitive bound cannot produce a valid complete word.
    for token_depth in range(max_primitive_length + 1):
        for token_word in product(tokens, repeat=token_depth):
            expanded, macro_used = expand_tokens(token_word, macro)
            if len(expanded) > max_primitive_length:
                continue
            enumeration_attempts += 1
            if expanded in seen_programs:
                continue
            seen_programs.add(expanded)
            unique_candidates_checked += 1
            coefficients = M.normal_form(expanded)
            first_by_coefficients.setdefault(coefficients, {
                "enumeration_attempts": enumeration_attempts,
                "unique_candidates_checked": unique_candidates_checked,
                "token_word": token_word,
                "program": expanded,
                "macro_used": macro_used,
            })

    return {
        "macro": macro,
        "max_primitive_length": max_primitive_length,
        "total_enumeration_attempts": enumeration_attempts,
        "total_unique_candidates_checked": unique_candidates_checked,
        "first_by_coefficients": first_by_coefficients,
    }


def solve_from_index(task, index):
    hit = index["first_by_coefficients"].get(task.coefficients)
    if hit is None:
        raise RuntimeError(f"registered grammar failed to solve {task.fingerprint}")
    if M.normal_form(tuple(hit["program"])) != task.coefficients:
        raise RuntimeError("macro index exact verification failed")
    return {
        "task": task.fingerprint,
        "enumeration_attempts": hit["enumeration_attempts"],
        "unique_candidates_checked": hit["unique_candidates_checked"],
        "token_word": hit["token_word"],
        "program": hit["program"],
        "macro_used": hit["macro_used"],
        "verified": True,
    }


def evaluate_index(tasks, index):
    rows = [solve_from_index(task, index) for task in tasks]
    return rows, sum(row["enumeration_attempts"] for row in rows), sum(
        row["unique_candidates_checked"] for row in rows
    )


def tournament(training_rows, validation_tasks):
    candidates, support = candidate_pool(training_rows)
    primitive_index = build_search_index(None, VALIDATION_MAX_PRIMITIVE_LENGTH)
    primitive_rows, primitive_attempts, primitive_checks = evaluate_index(validation_tasks, primitive_index)
    evaluations = []
    build_wall_start = time.perf_counter()
    for candidate in candidates:
        index = build_search_index(candidate, VALIDATION_MAX_PRIMITIVE_LENGTH)
        rows, attempts, checks = evaluate_index(validation_tasks, index)
        baseline = {row["task"]: row for row in primitive_rows}
        strict = harmful = macro_wins = 0
        for row in rows:
            base = baseline[row["task"]]
            if row["enumeration_attempts"] < base["enumeration_attempts"]:
                strict += 1
                if row["macro_used"]:
                    macro_wins += 1
            elif row["enumeration_attempts"] > base["enumeration_attempts"]:
                harmful += 1
        evaluations.append({
            "fragment": candidate,
            "support": support[candidate],
            "aggregate_enumeration_attempts": attempts,
            "aggregate_unique_checks": checks,
            "baseline_aggregate_enumeration_attempts": primitive_attempts,
            "saving": primitive_attempts - attempts,
            "strict_improvement_tasks": strict,
            "harmful_tasks": harmful,
            "macro_strict_wins": macro_wins,
            "rows": rows,
        })
    candidate_index_build_wall = time.perf_counter() - build_wall_start

    if not candidates:
        return {
            "terminal": "NO_REPEATED_MACRO_CANDIDATES",
            "accepted": False,
            "selected": None,
            "candidate_order": [],
            "baseline_rows": primitive_rows,
            "baseline_aggregate_enumeration_attempts": primitive_attempts,
            "baseline_aggregate_unique_checks": primitive_checks,
            "evaluations": [],
            "candidate_index_build_wall_seconds": candidate_index_build_wall,
        }

    # Evaluations inherit the already-frozen candidate order, which is the tie-break.
    selected = min(
        enumerate(evaluations),
        key=lambda item: (item[1]["aggregate_enumeration_attempts"], item[0]),
    )[1]
    accepted = selected["aggregate_enumeration_attempts"] < primitive_attempts
    return {
        "terminal": "MACRO_TOURNAMENT_SELECTED_METHOD" if accepted else "MACRO_TOURNAMENT_SELECTS_NO_METHOD",
        "accepted": accepted,
        "selected": selected,
        "candidate_order": candidates,
        "baseline_rows": primitive_rows,
        "baseline_aggregate_enumeration_attempts": primitive_attempts,
        "baseline_aggregate_unique_checks": primitive_checks,
        "evaluations": evaluations,
        "candidate_index_build_wall_seconds": candidate_index_build_wall,
    }


def ordinary_persist(path: Path, macro):
    payload = {"macro": list(macro), "fingerprint": content_hash({"macro": macro})}
    temp = path.with_suffix(".tmp")
    with temp.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def ordinary_load(path: Path):
    payload = json.loads(path.read_text())
    macro = tuple(payload["macro"])
    if content_hash({"macro": macro}) != payload["fingerprint"]:
        raise RuntimeError("ordinary macro persistence identity mismatch")
    return macro


def admit_macro(root: Path, macro, training_receipt, utility_receipt, revoke=False):
    runtime = OCMRuntime(root)
    _tr, training_evidence = runtime.admit_evidence(
        training_receipt,
        Channel.PROOF,
        "g2-macro-training.v1",
        scope=SCOPE,
    )
    _ur, utility_evidence = runtime.admit_evidence(
        utility_receipt,
        Channel.OBSERVATION,
        "g2-macro-utility.v1",
        scope=SCOPE,
    )
    warrant = WarrantProfile.of({training_evidence, utility_evidence})
    source_payload = {
        "kind": "g2.macro.support.v1",
        "training": content_hash(training_receipt),
        "utility": content_hash(utility_receipt),
    }
    source_id = "g2-macro-support:" + content_hash(source_payload)
    runtime.admit_object(
        Atom(
            source_id,
            "proof",
            warrant,
            scope=SCOPE,
            quarantined=True,
            content_ref=content_hash(source_payload),
            meta=tuple(source_payload.items()),
        ),
        (),
        "OBSERVATION",
    )
    payload = {"kind": "macro.operator.v1", "macro": macro, "fingerprint": content_hash({"macro": macro})}
    atom_id = "macro-operator:" + content_hash(payload)
    edge = Hyperedge("support:" + atom_id, (source_id,), (atom_id,), "SUPPORT", warrant=warrant)
    runtime.admit_object(
        Atom(
            atom_id,
            "procedure",
            warrant,
            scope=SCOPE,
            content_ref=content_hash(payload),
            meta=tuple(payload.items()),
        ),
        (edge,),
        "OBSERVATION",
    )
    if revoke:
        runtime.revoke((training_evidence,))
    runtime.persist()

    replay = OCMRuntime(root)
    atom = replay.state.ks.atom_map().get(atom_id)
    if revoke:
        if atom is not None and atom.liveness(replay.state.revoked) is Liveness.LIVE:
            raise RuntimeError("revoked macro remained live")
        return None, atom_id, training_evidence, utility_evidence
    if atom is None or atom.liveness(replay.state.revoked) is not Liveness.LIVE:
        raise RuntimeError("macro did not survive restart")
    stored = dict(atom.meta)
    if atom.content_ref != content_hash(stored):
        raise RuntimeError("macro content identity mismatch")
    loaded = tuple(stored["macro"])
    if content_hash({"macro": loaded}) != stored["fingerprint"]:
        raise RuntimeError("macro fingerprint mismatch")
    return loaded, atom_id, training_evidence, utility_evidence


def compare_rows(primitive_rows, candidate_rows):
    baseline = {row["task"]: row for row in primitive_rows}
    strict = harmful = macro_wins = 0
    for row in candidate_rows:
        base = baseline[row["task"]]
        if row["enumeration_attempts"] < base["enumeration_attempts"]:
            strict += 1
            if row["macro_used"]:
                macro_wins += 1
        elif row["enumeration_attempts"] > base["enumeration_attempts"]:
            harmful += 1
    return {"strict_improvement_tasks": strict, "harmful_tasks": harmful, "macro_strict_wins": macro_wins}


def rows_equal(a_rows, b_rows):
    return all(
        a["task"] == b["task"]
        and a["enumeration_attempts"] == b["enumeration_attempts"]
        and a["unique_candidates_checked"] == b["unique_candidates_checked"]
        and tuple(a["program"]) == tuple(b["program"])
        and tuple(a["token_word"]) == tuple(b["token_word"])
        for a, b in zip(a_rows, b_rows)
    )


def run():
    source_path = SRC / "ocm" / "learning" / "methods.py"
    observed_blob = git_blob_sha1(source_path)
    if observed_blob != METHOD_BLOB:
        raise RuntimeError(f"method source drift: {observed_blob}")

    run_start = time.perf_counter()
    population, training_tasks, validation_tasks, test_tasks = frozen_partition()
    training_rows, training_slots = solve_training(training_tasks)
    tour = tournament(training_rows, validation_tasks)

    selected_macro = tuple(tour["selected"]["fragment"]) if tour["accepted"] else None
    training_receipt = {
        "schema": "g2.macro.training.v1",
        "source_blob": METHOD_BLOB,
        "training_ids": [task.fingerprint for task, _result in training_rows],
        "training_programs": [result.program for _task, result in training_rows],
        "candidate_order": tour["candidate_order"],
        "selected_macro": selected_macro,
    }
    utility_receipt = {
        "schema": "g2.macro.utility.v1",
        "terminal": tour["terminal"],
        "accepted": tour["accepted"],
        "baseline_attempts": tour["baseline_aggregate_enumeration_attempts"],
        "selected": tour["selected"],
        "validation_ids": [task.fingerprint for task in validation_tasks],
    }

    primitive_test_index = build_search_index(None, TEST_MAX_PRIMITIVE_LENGTH)
    primitive_rows, primitive_total, primitive_checks = evaluate_index(test_tasks, primitive_test_index)

    if selected_macro is None:
        ordinary_rows = ocm_rows = revoked_rows = primitive_rows
        ordinary_total = ocm_total = revoked_total = primitive_total
        ordinary_checks = ocm_checks = revoked_checks = primitive_checks
        ordinary_equal_ocm = revoked_equal_primitive = True
        ocm_atom_id = None
        training_evidence = utility_evidence = None
    else:
        selected_index = build_search_index(selected_macro, TEST_MAX_PRIMITIVE_LENGTH)
        selected_rows, selected_total, selected_checks = evaluate_index(test_tasks, selected_index)
        with tempfile.TemporaryDirectory(prefix="ocm-g2-macro-") as temp_dir:
            root = Path(temp_dir)
            ordinary_path = root / "ordinary-macro.json"
            ordinary_persist(ordinary_path, selected_macro)
            ordinary_macro = ordinary_load(ordinary_path)
            ocm_macro, ocm_atom_id, training_evidence, utility_evidence = admit_macro(
                root / "ocm-live", selected_macro, training_receipt, utility_receipt, revoke=False
            )
            revoked_macro, _revoked_atom, _rte, _rue = admit_macro(
                root / "ocm-revoked", selected_macro, training_receipt, utility_receipt, revoke=True
            )
        ordinary_rows, ordinary_total, ordinary_checks = evaluate_index(
            test_tasks, build_search_index(ordinary_macro, TEST_MAX_PRIMITIVE_LENGTH)
        )
        ocm_rows, ocm_total, ocm_checks = evaluate_index(
            test_tasks, build_search_index(ocm_macro, TEST_MAX_PRIMITIVE_LENGTH)
        )
        revoked_rows, revoked_total, revoked_checks = evaluate_index(
            test_tasks, build_search_index(revoked_macro, TEST_MAX_PRIMITIVE_LENGTH)
        )
        if not rows_equal(selected_rows, ordinary_rows):
            raise RuntimeError("ordinary persisted macro changed exact search behavior")
        ordinary_equal_ocm = rows_equal(ordinary_rows, ocm_rows)
        revoked_equal_primitive = rows_equal(revoked_rows, primitive_rows)

    comparison = compare_rows(primitive_rows, ocm_rows)

    if not tour["accepted"]:
        terminal = tour["terminal"]
        causal = False
    elif not ordinary_equal_ocm:
        terminal = "CANNOT_CHECK_COMPONENT_TRANSPLANT_PARITY"
        causal = False
    elif not revoked_equal_primitive:
        terminal = "CANNOT_CHECK_REVOCATION_ABLATION"
        causal = False
    elif comparison["macro_strict_wins"] <= 0:
        terminal = "NO_CAUSAL_MACRO_CONSUMPTION"
        causal = False
    elif ocm_total >= primitive_total:
        terminal = "NO_AMORTIZED_MACRO_SEARCH_ON_LENGTH8_TEST"
        causal = False
    else:
        terminal = "CAUSAL_MACRO_OPERATOR_REUSE_SUPPORTED_AT_LENGTH8"
        causal = True

    all_candidate_validation_attempts = sum(
        row["aggregate_enumeration_attempts"] for row in tour["evaluations"]
    )
    learned_path_attempts = (
        training_slots
        + tour["baseline_aggregate_enumeration_attempts"]
        + all_candidate_validation_attempts
        + ocm_total
    )
    lifetime_terminal = (
        "LIFETIME_MACRO_SEARCH_PAYBACK_AT_64_LENGTH8_TESTS"
        if tour["accepted"] and learned_path_attempts < primitive_total
        else "NO_LIFETIME_MACRO_SEARCH_PAYBACK_AT_64_LENGTH8_TESTS"
    )

    return {
        "schema": "g2.macro-operator.result.v1",
        "terminal": terminal,
        "causal_macro_reuse_supported": causal,
        "lifetime_terminal": lifetime_terminal,
        "method_blob": METHOD_BLOB,
        "partition": {
            "training_n": TRAIN_N,
            "validation_n": VALIDATION_N,
            "test_n": TEST_N,
            "training_min_length": 6,
            "validation_min_length": 7,
            "test_min_length": 8,
            "training_salt": TRAIN_SALT,
            "validation_salt": VALIDATION_SALT,
            "test_salt": TEST_SALT,
            "training_ids": [task.fingerprint for task in training_tasks],
            "validation_ids": [task.fingerprint for task in validation_tasks],
            "test_ids": [task.fingerprint for task in test_tasks],
            "population_counts": {
                str(length): sum(1 for minimum, _task in population.values() if minimum == length)
                for length in (6, 7, 8)
            },
        },
        "training": {
            "primitive_search_slots": training_slots,
            "rows": [
                {"task": task.fingerprint, "program": result.program, "slots": result.slots}
                for task, result in training_rows
            ],
        },
        "tournament": tour,
        "selected_macro": list(selected_macro) if selected_macro is not None else None,
        "test": {
            "primitive_total_enumeration_attempts": primitive_total,
            "primitive_total_unique_checks": primitive_checks,
            "ordinary_total_enumeration_attempts": ordinary_total,
            "ordinary_total_unique_checks": ordinary_checks,
            "ocm_total_enumeration_attempts": ocm_total,
            "ocm_total_unique_checks": ocm_checks,
            "revoked_total_enumeration_attempts": revoked_total,
            "revoked_total_unique_checks": revoked_checks,
            "ordinary_equals_ocm": ordinary_equal_ocm,
            "revoked_equals_primitive": revoked_equal_primitive,
            "comparison": comparison,
            "primitive_rows": primitive_rows,
            "ordinary_rows": ordinary_rows,
            "ocm_rows": ocm_rows,
            "revoked_rows": revoked_rows,
        },
        "accounting": {
            "training_primitive_search_slots": training_slots,
            "primitive_validation_attempts": tour["baseline_aggregate_enumeration_attempts"],
            "all_candidate_validation_attempts": all_candidate_validation_attempts,
            "all_candidate_validation_unique_checks": sum(
                row["aggregate_unique_checks"] for row in tour["evaluations"]
            ),
            "selected_path_through_test_attempts": learned_path_attempts,
            "primitive_test_attempts": primitive_total,
            "candidate_index_build_wall_seconds": tour["candidate_index_build_wall_seconds"],
            "study_wall_seconds": time.perf_counter() - run_start,
            "note": "Search attempts/checks are research coordinates only; no whole-architecture net-benefit claim.",
        },
        "ocm": {
            "atom_id": ocm_atom_id,
            "training_evidence": training_evidence,
            "utility_evidence": utility_evidence,
            "restart_before_test": selected_macro is not None,
            "support_withdrawal_ablation": selected_macro is not None,
        },
        "claim_boundary": (
            "Bounded causal reuse of one training-derived macro under exact macro-token search only. "
            "Macro/library search is a conventional parent mechanism; no OCM architecture uniqueness, cross-domain, or whole-resource benefit claim."
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
        "selected_macro": result["selected_macro"],
        "macro_strict_wins": result["test"]["comparison"]["macro_strict_wins"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

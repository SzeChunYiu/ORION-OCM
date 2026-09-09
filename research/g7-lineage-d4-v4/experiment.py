"""G7 microscope successor: five earned transitions on one lineage id.

T0: empty → OCM_0 / D0 exact interaction, one G2-style macro.
T1: that persisted machine → OCM_1 / D1 failure/scope memory, no reset in the
principal arm.
T2: that persisted machine → OCM_2 / D2 planning / uncertainty / information
gathering on a disjoint diagnosis family.
T3: that persisted machine → OCM_3 / D3 formal mathematics: miniature Hilbert/SK
named-lemma introduction (CUT_*, not PREFIX/SWAP, not Metamath, not FLT, not
historical M11 relabel).
T4: that persisted machine → OCM_4 / D4 coding/tools: exact string-rewrite
(RW_*, not REGEX/EVAL, not Metamath, not FLT, not historical M11 relabel).
Reset must re-acquire T0+T1+T2+T3+T4 in an isolated store. D5–D6 remain
registered and unrun. Constitution C is not mutated.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
import time

from lineage import (
    CONSTITUTION,
    D2_GRAMMAR_ID,
    D2_POLICY_GREEDY,
    D2_POLICY_ROUND_ROBIN,
    D3_FROZEN_LEMMA_NAMES,
    D3_GRAMMAR_ID,
    D4_FROZEN_RULE_NAMES,
    D4_GRAMMAR_ID,
    GRAMMAR_ID,
    IsolationError,
    LINEAGE_ID,
    LineageStore,
    ORIGIN_APPLICABILITY,
    ORIGIN_COMPOSITION,
    ORIGIN_REDISCOVERY,
    UNRUN_STAGES,
    admit_cut_lemma,
    admit_failure,
    admit_macro,
    admit_probe_policy,
    admit_rewrite_rule,
    arm_result,
    assert_constitution_frozen,
    assert_disjoint_stores,
    build_search_index,
    constitution_of,
    coordinate,
    cost,
    count_objects,
    current_cut_lemma,
    current_macro,
    current_probe_policy,
    current_rewrite_rule,
    d2_taught_donors,
    d2_tournament,
    d3_taught_donors,
    d3_tournament,
    d4_taught_donors,
    d4_tournament,
    diagnosis_population,
    discover_cut_lemma,
    discover_rewrite_rule,
    empty_bundle,
    emit_transition,
    evaluate_diagnosis,
    evaluate_hilbert,
    evaluate_index,
    evaluate_rewrite,
    failure_record,
    hilbert_population,
    rewrite_population,
    lemma_from_method,
    machine_identity,
    population_by_min_length,
    search_bundle,
    solve_training,
    take_diagnosis,
    take_hilbert,
    take_rewrite,
    take_stratum,
    taught_donors,
    tournament,
)

HERE = Path(__file__).resolve().parent
TRAIN_SALT = "orion-ocm-g7-t0-train-v1"
VAL_SALT = "orion-ocm-g7-t0-val-v1"
TEST_SALT = "orion-ocm-g7-t0-test-v1"
TRAP_TRAIN_SALT = "orion-ocm-g7-t1-trap-train-v1"
TRAP_TEST_SALT = "orion-ocm-g7-t1-trap-test-v1"
TRAIN_N = 8
VAL_N = 6
TEST_N = 8
TRAP_TRAIN_N = 6
TRAP_TEST_N = 6
TRAIN_LEN = 3
VAL_LEN = 3
TEST_LEN = 4
TRAP_LEN = 3
MAX_LEN_T0 = 4
MAX_LEN_T1 = 4
D2_TRAIN_SALT = "orion-ocm-g7-d2-train-v1"
D2_VAL_SALT = "orion-ocm-g7-d2-val-v1"
D2_TEST_SALT = "orion-ocm-g7-d2-test-v1"
D2_TRAIN_N = 12
D2_VAL_N = 8
D2_TEST_N = 15
D3_TRAIN_SALT = "orion-ocm-g7-d3-train-v1"
D3_VAL_SALT = "orion-ocm-g7-d3-val-v1"
D3_TEST_SALT = "orion-ocm-g7-d3-test-v1"
D3_TRAIN_N = 2
D3_VAL_N = 2
D3_TEST_N = 3
D4_TRAIN_SALT = "orion-ocm-g7-d4-train-v1"
D4_VAL_SALT = "orion-ocm-g7-d4-val-v1"
D4_TEST_SALT = "orion-ocm-g7-d4-test-v1"
D4_TRAIN_N = 8
D4_VAL_N = 6
D4_TEST_N = 10


def frozen_tasks():
    population = population_by_min_length(4)
    train = take_stratum(population, TRAIN_LEN, TRAIN_SALT, TRAIN_N, require_square=True)
    val = take_stratum(
        population, VAL_LEN, VAL_SALT, VAL_N,
        exclude={t["fingerprint"] for t in train},
        require_square=True,
    )
    test = take_stratum(
        population, TEST_LEN, TEST_SALT, TEST_N,
        exclude={t["fingerprint"] for t in train + val},
        require_square=True,
    )
    trap_train = take_stratum(
        population, TRAP_LEN, TRAP_TRAIN_SALT, TRAP_TRAIN_N,
        exclude={t["fingerprint"] for t in train + val + test},
        require_square=False,
    )
    trap_test = take_stratum(
        population, TRAP_LEN, TRAP_TEST_SALT, TRAP_TEST_N,
        exclude={t["fingerprint"] for t in train + val + test + trap_train},
        require_square=False,
    )
    diagnosis = diagnosis_population()
    d2_train = take_diagnosis(diagnosis, D2_TRAIN_SALT, D2_TRAIN_N)
    d2_val = take_diagnosis(
        diagnosis, D2_VAL_SALT, D2_VAL_N,
        exclude={t["fingerprint"] for t in d2_train},
    )
    d2_test = take_diagnosis(
        diagnosis, D2_TEST_SALT, D2_TEST_N,
        exclude={t["fingerprint"] for t in d2_train + d2_val},
    )
    hilbert = hilbert_population()
    d3_train = take_hilbert(hilbert, D3_TRAIN_SALT, D3_TRAIN_N)
    d3_val = take_hilbert(
        hilbert, D3_VAL_SALT, D3_VAL_N,
        exclude={t["fingerprint"] for t in d3_train},
    )
    d3_test = take_hilbert(
        hilbert, D3_TEST_SALT, D3_TEST_N,
        exclude={t["fingerprint"] for t in d3_train + d3_val},
    )
    rewrite = rewrite_population()
    d4_train = take_rewrite(rewrite, D4_TRAIN_SALT, D4_TRAIN_N)
    d4_val = take_rewrite(
        rewrite, D4_VAL_SALT, D4_VAL_N,
        exclude={t["fingerprint"] for t in d4_train},
    )
    d4_test = take_rewrite(
        rewrite, D4_TEST_SALT, D4_TEST_N,
        exclude={t["fingerprint"] for t in d4_train + d4_val},
    )
    poly_ids = [t["fingerprint"] for t in train + val + test + trap_train + trap_test]
    d2_ids = [t["fingerprint"] for t in d2_train + d2_val + d2_test]
    d3_ids = [t["fingerprint"] for t in d3_train + d3_val + d3_test]
    d4_ids = [t["fingerprint"] for t in d4_train + d4_val + d4_test]
    if len(poly_ids) != len(set(poly_ids)):
        raise RuntimeError("G7 partition overlap")
    if len(d2_ids) != len(set(d2_ids)):
        raise RuntimeError("G7 D2 partition overlap")
    if len(d3_ids) != len(set(d3_ids)):
        raise RuntimeError("G7 D3 partition overlap")
    if len(d4_ids) != len(set(d4_ids)):
        raise RuntimeError("G7 D4 partition overlap")
    if set(poly_ids) & set(d2_ids):
        raise RuntimeError("D2 diagnosis family is not disjoint from D0/D1 polynomial family")
    if set(poly_ids) & set(d3_ids) or set(d2_ids) & set(d3_ids):
        raise RuntimeError("D3 Hilbert family is not disjoint from D0/D1/D2 families")
    if set(poly_ids) & set(d4_ids) or set(d2_ids) & set(d4_ids) or set(d3_ids) & set(d4_ids):
        raise RuntimeError("D4 rewrite family is not disjoint from D0/D1/D2/D3 families")
    if any(t["domain"] != D2_GRAMMAR_ID for t in d2_train + d2_val + d2_test):
        raise RuntimeError("D2 tasks must use the diagnosis grammar")
    if any(t["domain"] != D3_GRAMMAR_ID for t in d3_train + d3_val + d3_test):
        raise RuntimeError("D3 tasks must use the Hilbert/SK grammar")
    if any(t["domain"] != D4_GRAMMAR_ID for t in d4_train + d4_val + d4_test):
        raise RuntimeError("D4 tasks must use the exact string-rewrite grammar")
    return {
        "population_size": len(population),
        "diagnosis_population_size": len(diagnosis),
        "hilbert_population_size": len(hilbert),
        "rewrite_population_size": len(rewrite),
        "train": train,
        "val": val,
        "test": test,
        "trap_train": trap_train,
        "trap_test": trap_test,
        "d2_train": d2_train,
        "d2_val": d2_val,
        "d2_test": d2_test,
        "d3_train": d3_train,
        "d3_val": d3_val,
        "d3_test": d3_test,
        "d4_train": d4_train,
        "d4_val": d4_val,
        "d4_test": d4_test,
        "poly_fingerprints": poly_ids,
        "d2_fingerprints": d2_ids,
        "d3_fingerprints": d3_ids,
        "d4_fingerprints": d4_ids,
    }


def donor_ids():
    return [d["identity"] for d in taught_donors()]


def prior_manifest():
    return {
        "items": [
            "four total arithmetic primitives inc/dec/double/square",
            "coefficient normal-form checker",
            "exact token-word BFS serving",
            "registered salts and stratum sizes",
        ],
        "charge": 4 + 1 + 1 + 5,
    }


def d2_prior_manifest():
    return {
        "items": [
            "four total arithmetic primitives inc/dec/double/square",
            "coefficient normal-form checker",
            "exact token-word BFS serving",
            "registered salts and stratum sizes",
            "T0 G2-style macro retained on the same lineage",
            "T1 degree-class failure memory retained on the same lineage",
            "taught D2 probe/replace operators and syndrome windows",
        ],
        "charge": 4 + 1 + 1 + 5 + 1 + 1 + (6 + 1 + 1),
    }


def d3_prior_manifest():
    return {
        "items": [
            "four total arithmetic primitives inc/dec/double/square",
            "coefficient normal-form checker",
            "exact token-word BFS serving",
            "registered salts and stratum sizes",
            "T0 G2-style macro retained on the same lineage",
            "T1 degree-class failure memory retained on the same lineage",
            "taught D2 probe/replace operators and syndrome windows",
            "T2 greedy posterior-split probe policy retained on the same lineage",
            "taught Hilbert K/S axiom schemas and MP",
        ],
        "charge": 4 + 1 + 1 + 5 + 1 + 1 + (6 + 1 + 1) + 1 + 3,
    }


def d4_prior_manifest():
    return {
        "items": [
            "four total arithmetic primitives inc/dec/double/square",
            "coefficient normal-form checker",
            "exact token-word BFS serving",
            "registered salts and stratum sizes",
            "T0 G2-style macro retained on the same lineage",
            "T1 degree-class failure memory retained on the same lineage",
            "taught D2 probe/replace operators and syndrome windows",
            "T2 greedy posterior-split probe policy retained on the same lineage",
            "taught Hilbert K/S axiom schemas and MP",
            "T3 CUT_* named lemma retained on the same lineage",
            "taught exact string-rewrite substitute and replace-all scan",
        ],
        "charge": 4 + 1 + 1 + 5 + 1 + 1 + (6 + 1 + 1) + 1 + 3 + 1 + 2,
    }


def witnesses_from_rows(rows, invoked):
    out = []
    for row in rows:
        identities = list(invoked) if row["macro_used"] else []
        out.append({
            "task_id": row["task"],
            "invoked_identities": identities,
            "token_word": list(row["token_word"]),
            "program": list(row["program"]),
            "enumeration_attempts": row["enumeration_attempts"],
            "verified": row["verified"],
        })
    return out


def persist_bytes(store: LineageStore) -> int:
    path = store.root / "bundle.json"
    return path.stat().st_size if path.is_file() else 0


def acquire_macro(parts, origin: str):
    training_rows, training_slots = solve_training(parts["train"], TRAIN_LEN)
    tour = tournament(training_rows, parts["val"], VAL_LEN, require_square_fragment=True)
    if not tour["accepted"]:
        raise RuntimeError("T0 tournament selected no macro; microscope acquisition failed")
    macro = tuple(tour["selected"]["fragment"])
    return {
        "macro": macro,
        "training_slots": training_slots,
        "tournament": tour,
        "origin": origin,
        "training_rows": training_rows,
    }


def evaluate_macro(macro, tasks, max_length, failure_records=()):
    primitive_index = build_search_index(None, max_length)
    primitive_rows, primitive_total, primitive_checks = evaluate_index(tasks, primitive_index)
    index = build_search_index(macro, max_length, failure_records)
    rows, total, checks = evaluate_index(tasks, index)
    strict = harmful = wins = 0
    baseline = {row["task"]: row for row in primitive_rows}
    for row in rows:
        base = baseline[row["task"]]
        if row["enumeration_attempts"] < base["enumeration_attempts"]:
            strict += 1
            if row["macro_used"]:
                wins += 1
        elif row["enumeration_attempts"] > base["enumeration_attempts"]:
            harmful += 1
    return {
        "primitive_total": primitive_total,
        "primitive_checks": primitive_checks,
        "total": total,
        "checks": checks,
        "rows": rows,
        "primitive_rows": primitive_rows,
        "strict": strict,
        "harmful": harmful,
        "macro_wins": wins,
        "skipped": index["skipped_by_failure"],
    }


def run_t0(continued: LineageStore, parent: LineageStore, parts):
    seed = empty_bundle()
    source_id = machine_identity(seed)
    acquired = acquire_macro(parts, ORIGIN_COMPOSITION)
    macro = acquired["macro"]
    bundle, method = admit_macro(seed, macro, ORIGIN_COMPOSITION, "OCM_0", "admit-g2-style-macro")
    continued.persist(bundle)
    loaded = continued.load()
    if current_macro(loaded) != macro:
        raise RuntimeError("T0 restart failed to restore the earned macro")
    if loaded["lineage_id"] != LINEAGE_ID:
        raise RuntimeError("lineage id mutated at T0")

    test = evaluate_macro(macro, parts["test"], MAX_LEN_T0)
    if test["macro_wins"] <= 0:
        raise RuntimeError("T0 test had no actual MACRO consumption")

    # Ordinary library parent receives the identical macro after its own persist.
    parent_seed = empty_bundle()
    parent_bundle, _pm = admit_macro(parent_seed, macro, ORIGIN_COMPOSITION, "OCM_0", "parent-admit-macro")
    parent.persist(parent_bundle)
    parent_loaded = parent.load()
    parent_test = evaluate_macro(current_macro(parent_loaded), parts["test"], MAX_LEN_T0)

    reset_work = acquired["training_slots"] + acquired["tournament"]["all_candidate_validation_attempts"] + test["primitive_total"]
    continued_work = acquired["training_slots"] + acquired["tournament"]["all_candidate_validation_attempts"] + test["total"]
    task_specific_work = test["primitive_total"]
    parent_work = continued_work

    ablation_index = build_search_index(None, MAX_LEN_T0)
    ablation_rows, ablation_total, _ = evaluate_index(parts["test"], ablation_index)
    effect_disappears = ablation_total == test["primitive_total"]

    loaded["resource_history"].append({
        "stage": "OCM_0",
        "acquisition_work_units": acquired["training_slots"],
        "test_work_units": test["total"],
    })
    continued.persist(loaded)
    loaded = continued.load()
    n_objects = count_objects(loaded)
    k = 1 + 4  # one macro + four taught primitives used by search
    bytes_written = persist_bytes(continued)
    composition_depth = max(0, len(macro) - 1)
    invoked = [method["identity"]]
    actual = [w for w in witnesses_from_rows(test["rows"], invoked) if w["invoked_identities"]]

    strongest = {
        "CONTINUED_OCM": arm_result("CONTINUED_OCM", continued_work, False, False, "T0 acquisition on empty seed; restart before test"),
        "RESET_OCM": arm_result("RESET_OCM", reset_work, False, False, "empty machine equals continued at T0 because there is no prior earned state"),
        "TASK_SPECIFIC_OCM": arm_result("TASK_SPECIFIC_OCM", task_specific_work, False, False, "primitive search on the test stratum only; no persistent method"),
        "STRONG_ADAPTIVE_PARENT": arm_result("STRONG_ADAPTIVE_PARENT", parent_work, False, False, "ordinary persistent macro library, identical serving grammar"),
        "reset_costs_more_or_fails_reuse": reset_work >= continued_work,
        "parent_ties_continued_mechanism": parent_test["total"] == test["total"],
        "winner": "TIE_CONTINUED_AND_PARENT" if parent_test["total"] == test["total"] else "CONTINUED_OCM",
        "notes": "T0 has no prior lineage state, so reset matches continued acquisition. Parent ties the mechanism.",
    }

    transition = emit_transition(
        lineage_id=LINEAGE_ID,
        source_stage="EMPTY",
        target_stage="OCM_0",
        source_machine_identity=source_id,
        target_bundle=loaded,
        imported_donor_identities=donor_ids(),
        prior_information_manifest=prior_manifest(),
        new_information_supplied={
            "training_task_ids": [t["fingerprint"] for t in parts["train"]],
            "examples": TRAIN_N,
            "labels": 0,
        },
        new_methods_schemas=[
            {
                "identity": method["identity"],
                "kind": "method",
                "origin_category": ORIGIN_COMPOSITION,
                "payload": method["payload"],
            },
            {
                "identity": loaded["method_schemas"][0]["identity"],
                "kind": "schema",
                "origin_category": ORIGIN_COMPOSITION,
                "payload": loaded["method_schemas"][0]["payload"],
            },
        ],
        reused_method_identities=[],
        actual_execution_witnesses=actual,
        primitive_operators_added=[],
        composition_depth=composition_depth,
        acquisition_cost=cost(acquired["training_slots"] + acquired["tournament"]["all_candidate_validation_attempts"], TRAIN_N + VAL_N, "train solve + validation tournament"),
        reasoning_cost=cost(test["total"], TEST_N, "exact token-word search on held-out D0 tasks"),
        verification_cost=cost(test["checks"], TEST_N, "unique expanded programs checked"),
        revision_cost=cost(0, 0, "no revision at T0"),
        self_change_cost=cost(1, 0, "one method admission"),
        maintenance_cost=cost(0, 0, "no index maintenance beyond the bundle write"),
        persistent_bytes=bytes_written,
        active_k_n={"k": k, "N": n_objects, "ratio": k / n_objects},
        kappa=coordinate(1 / n_objects, "MEASURED", "one admitted method against persisted object count"),
        omega=coordinate(0.0, "CANNOT_CHECK", "no diagnostic probe at D0 acquisition"),
        chi=coordinate(float(test["total"]), "MEASURED", "post-admission search space in enumeration attempts"),
        retention={
            "prior_methods_retained": True,
            "prior_failure_knowledge_retained": True,
            "notes": "seed donors and empty failure store retained",
        },
        negative_transfer={
            "observed": test["harmful"] > 0,
            "harmful_tasks": test["harmful"],
            "notes": "macro can increase attempts on some held-out tasks; recorded, not hidden",
        },
        ablation={
            "removed": method["identity"],
            "effect_disappears": effect_disappears,
            "notes": "serving without the macro reduces exactly to primitive search",
        },
        strongest_parent_result=strongest,
        terminal="OCM_0_D0_EXACT_MACRO_ACQUIRED",
    )
    return {
        "bundle": continued.load(),
        "transition": transition,
        "acquired": acquired,
        "test": test,
        "continued_work": continued_work,
        "method": method,
    }


def learn_failure(bundle, trap_train, trap_test, retention_tasks):
    macro = current_macro(bundle)
    if macro is None:
        raise RuntimeError("T1 continued arm missing T0 macro")
    method_id = bundle["learned_methods"][0]["identity"]
    # Confirm MACRO is a degree dead-end on the trap class and still useful outside it.
    trap_without = evaluate_macro(macro, trap_train, MAX_LEN_T1)
    retention_without = evaluate_macro(macro, retention_tasks, MAX_LEN_T1)
    rec = failure_record(method_id, macro, trap_train)
    if rec["scope"]["kind"] != "target_degree_lt":
        raise RuntimeError("failure scope must be degree-class, not task identity")
    if rec["task_ids"]:
        raise RuntimeError("failure record must not store task ids")
    updated = admit_failure(bundle, rec, "OCM_1")
    trap_with_rows, trap_with_total, trap_with_checks, trap_skipped = search_bundle(updated, trap_test, MAX_LEN_T1)
    trap_without_test = evaluate_macro(macro, trap_test, MAX_LEN_T1)
    retention_with_rows, retention_with_total, _, _ = search_bundle(updated, retention_tasks, MAX_LEN_T1)
    retention_without_test = evaluate_macro(macro, retention_tasks, MAX_LEN_T1)
    return {
        "record": rec,
        "bundle": updated,
        "trap_train_without": trap_without,
        "retention_without": retention_without,
        "trap_with_rows": trap_with_rows,
        "trap_with_total": trap_with_total,
        "trap_with_checks": trap_with_checks,
        "trap_skipped": trap_skipped,
        "trap_without_test": trap_without_test,
        "retention_with_rows": retention_with_rows,
        "retention_with_total": retention_with_total,
        "retention_without_test": retention_without_test,
        "failure_reduces_trap": trap_with_total < trap_without_test["total"],
        "retention_preserved": retention_with_total == retention_without_test["total"]
        or any(row["macro_used"] for row in retention_with_rows),
    }


def run_t1(continued: LineageStore, reset: LineageStore, parent: LineageStore, task_specific: LineageStore, parts, t0):
    assert_disjoint_stores(continued, reset)
    assert_disjoint_stores(continued, task_specific)
    loaded = continued.load()
    if loaded["lineage_id"] != LINEAGE_ID:
        raise RuntimeError("T1 must keep the T0 lineage id")
    source_id = machine_identity(loaded)
    if current_macro(loaded) is None:
        raise RuntimeError("principal arm reset illegally before T1")

    learned = learn_failure(loaded, parts["trap_train"], parts["trap_test"], parts["test"])
    learned["bundle"]["resource_history"].append({
        "stage": "OCM_1",
        "trap_work_units": learned["trap_with_total"],
        "failure_skips": learned["trap_skipped"],
    })
    continued.persist(learned["bundle"])
    restarted = continued.load()
    if restarted["lineage_id"] != LINEAGE_ID:
        raise RuntimeError("lineage id changed across T1 restart")
    if current_macro(restarted) != current_macro(loaded):
        raise RuntimeError("T0 macro was not retained at T1")
    if not restarted["failure_counterexample_knowledge"]:
        raise RuntimeError("failure knowledge did not survive restart")

    # Reset arm: isolated empty store, must re-acquire T0 then T1. Cannot see continued files.
    try:
        reset.load()
        saw_continued = True
    except FileNotFoundError:
        saw_continued = False
    if saw_continued:
        raise IsolationError("reset arm loaded a bundle before acquiring; isolation broken")
    reset_seed = empty_bundle()
    reset.persist(reset_seed)
    reset_acquired = acquire_macro(parts, ORIGIN_REDISCOVERY)
    reset_bundle, reset_method = admit_macro(
        reset.load(), reset_acquired["macro"], ORIGIN_REDISCOVERY, "OCM_0", "reset-reacquire-macro"
    )
    reset.persist(reset_bundle)
    reset_learned = learn_failure(reset.load(), parts["trap_train"], parts["trap_test"], parts["test"])
    reset.persist(reset_learned["bundle"])
    reset_final = reset.load()
    if Path(reset.root).resolve().is_relative_to(Path(continued.root).resolve()):
        raise IsolationError("reset nested under continued")
    continued_path = Path(continued.root / "bundle.json").resolve()
    if continued_path.is_relative_to(Path(reset.root).resolve()):
        raise IsolationError("reset root contains continued bundle")

    reset_t1_work = (
        reset_acquired["training_slots"]
        + reset_acquired["tournament"]["all_candidate_validation_attempts"]
        + reset_learned["trap_with_total"]
    )
    continued_t1_work = learned["trap_with_total"]
    if not (reset_t1_work > continued_t1_work or not reset_learned["failure_reduces_trap"]):
        # Reset re-acquired from scratch: acquisition is extra cost. Trap evaluation
        # alone may tie; the required comparison is full T1 cost including re-acquisition.
        pass
    if reset_t1_work <= continued_t1_work:
        raise RuntimeError(
            f"reset must cost more than continued at T1: reset={reset_t1_work} continued={continued_t1_work}"
        )

    # Task-specific: primitive search on trap tasks, no T0 macro, no failure schema.
    task_seed = empty_bundle()
    task_specific.persist(task_seed)
    task_eval = evaluate_macro(None, parts["trap_test"], MAX_LEN_T1)
    task_work = task_eval["primitive_total"]

    # Strong adaptive parent: same macro + same nogood table in its own store.
    parent_loaded = parent.load()
    parent_learned = learn_failure(parent_loaded, parts["trap_train"], parts["trap_test"], parts["test"])
    parent.persist(parent_learned["bundle"])
    parent_work = parent_learned["trap_with_total"]

    ablation_bundle = json_clone_without_failures(restarted)
    ablation_rows, ablation_total, _, _ = search_bundle(ablation_bundle, parts["trap_test"], MAX_LEN_T1)
    effect_disappears = ablation_total > learned["trap_with_total"]

    n_objects = count_objects(restarted)
    k = 1 + 1 + 4  # macro + failure record + primitives
    bytes_written = persist_bytes(continued)
    rec = learned["record"]
    method_id = restarted["learned_methods"][0]["identity"]
    actual = [
        w for w in witnesses_from_rows(learned["trap_with_rows"], [method_id])
    ]
    # Trap witnesses should not require MACRO; they witness scoped non-use.
    chi_before = float(learned["trap_without_test"]["total"])
    chi_after = float(learned["trap_with_total"])
    probes = TRAP_TRAIN_N
    omega = 1.0 / probes

    strongest = {
        "CONTINUED_OCM": arm_result(
            "CONTINUED_OCM",
            continued_t1_work,
            True,
            False,
            "loaded T0 bundle; added scoped failure memory; no reset",
        ),
        "RESET_OCM": arm_result(
            "RESET_OCM",
            reset_t1_work,
            False,
            False,
            "isolated empty store; re-acquired the macro then failure memory",
        ),
        "TASK_SPECIFIC_OCM": arm_result(
            "TASK_SPECIFIC_OCM",
            task_work,
            False,
            False,
            "primitive search on trap tasks; no T0 method and no failure schema",
        ),
        "STRONG_ADAPTIVE_PARENT": arm_result(
            "STRONG_ADAPTIVE_PARENT",
            parent_work,
            True,
            False,
            "ordinary library plus the same degree-nogood table; comparator evolved at T1",
        ),
        "reset_costs_more_or_fails_reuse": True,
        "parent_ties_continued_mechanism": parent_work == continued_t1_work,
        "winner": "CONTINUED_OCM_BEATS_RESET",
        "notes": (
            "Continued reuses the T0 method. Reset rediscovers independently and pays T0 again. "
            "The ordinary nogood parent may tie the T1 mechanism; that is absorption, not a reset."
        ),
    }

    transition = emit_transition(
        lineage_id=LINEAGE_ID,
        source_stage="OCM_0",
        target_stage="OCM_1",
        source_machine_identity=source_id,
        target_bundle=restarted,
        imported_donor_identities=donor_ids(),
        prior_information_manifest=prior_manifest(),
        new_information_supplied={
            "training_task_ids": [t["fingerprint"] for t in parts["trap_train"]],
            "examples": TRAP_TRAIN_N,
            "labels": 0,
        },
        new_methods_schemas=[
            {
                "identity": rec["identity"],
                "kind": "failure_record",
                "origin_category": ORIGIN_APPLICABILITY,
                "payload": rec["payload"],
            }
        ],
        reused_method_identities=[method_id],
        actual_execution_witnesses=actual,
        primitive_operators_added=[],
        composition_depth=max(0, len(current_macro(restarted)) - 1),
        acquisition_cost=cost(TRAP_TRAIN_N, TRAP_TRAIN_N, "scoped failure evidence from trap training class"),
        reasoning_cost=cost(learned["trap_with_total"], TRAP_TEST_N, "trap held-out search with failure memory"),
        verification_cost=cost(learned["trap_with_checks"], TRAP_TEST_N, "unique expanded programs checked"),
        revision_cost=cost(1, 0, "applicability restriction admitted"),
        self_change_cost=cost(1, 0, "one failure-memory admission"),
        maintenance_cost=cost(learned["trap_skipped"], 0, "nogood skips charged as maintenance of failure index"),
        persistent_bytes=bytes_written,
        active_k_n={"k": k, "N": n_objects, "ratio": k / n_objects},
        kappa=coordinate(2 / n_objects, "MEASURED", "macro retained plus one local failure record"),
        omega=coordinate(omega, "MEASURED", "degree-class diagnosis from trap-train probes; not a supplied root-cause label"),
        chi=coordinate(chi_after, "MEASURED", f"trap search space after nogoods; before={chi_before}"),
        retention={
            "prior_methods_retained": True,
            "prior_failure_knowledge_retained": True,
            "notes": "T0 macro identity retained; D0 held-out still uses MACRO outside the failure scope",
        },
        negative_transfer={
            "observed": not learned["retention_preserved"],
            "harmful_tasks": 0 if learned["retention_preserved"] else learned["retention_without_test"]["harmful"],
            "notes": "failure scope is degree class; MACRO remains available on higher-degree D0 tasks",
        },
        ablation={
            "removed": rec["identity"],
            "effect_disappears": effect_disappears,
            "notes": "dropping failure memory returns trap search to the unpruned MACRO grammar",
        },
        strongest_parent_result=strongest,
        terminal="OCM_1_D1_FAILURE_MEMORY_ADDED",
    )
    return {
        "bundle": restarted,
        "transition": transition,
        "learned": learned,
        "continued_t1_work": continued_t1_work,
        "reset_t1_work": reset_t1_work,
        "task_work": task_work,
        "parent_work": parent_work,
        "reset_origin": reset_method["origin_category"],
        "reset_macro": list(reset_acquired["macro"]),
        "continued_macro": list(current_macro(restarted)),
        "ablation_total": ablation_total,
        "t0_reacquire_work": (
            reset_acquired["training_slots"]
            + reset_acquired["tournament"]["all_candidate_validation_attempts"]
        ),
    }


def d2_witnesses(rows, invoked):
    out = []
    for row in rows:
        out.append({
            "task_id": row["task"],
            "invoked_identities": list(invoked) if row.get("policy_used") else [],
            "token_word": list(row["token_word"]),
            "program": list(row["program"]),
            "enumeration_attempts": row["enumeration_attempts"],
            "verified": row["verified"],
        })
    return out


def acquire_d2_policy(parts, origin: str):
    # Train is the evidence that a split policy is even a candidate; validation
    # tournament is the admission gate, matching T0's train-then-val pattern.
    train_rows, train_total, train_checks, train_probes = evaluate_diagnosis(
        parts["d2_train"], D2_POLICY_GREEDY
    )
    tour = d2_tournament(parts["d2_val"])
    if not tour["accepted"]:
        raise RuntimeError("D2 tournament selected no information-gain policy")
    return {
        "name": tour["selected"]["name"],
        "origin": origin,
        "tournament": tour,
        "train_total": train_total,
        "train_checks": train_checks,
        "train_probes": train_probes,
        "train_rows": train_rows,
    }


def run_t2(continued: LineageStore, reset: LineageStore, parent: LineageStore, task_specific: LineageStore, parts, t0, t1):
    assert_disjoint_stores(continued, reset)
    loaded = continued.load()
    if loaded["lineage_id"] != LINEAGE_ID:
        raise RuntimeError("T2 must keep the T0/T1 lineage id")
    assert_constitution_frozen(loaded)
    if constitution_of(loaded) != CONSTITUTION:
        raise RuntimeError("constitution mutated before T2")
    source_id = machine_identity(loaded)
    if current_macro(loaded) is None:
        raise RuntimeError("principal arm missing T0 macro at T2")
    if not loaded["failure_counterexample_knowledge"]:
        raise RuntimeError("principal arm missing T1 failure memory at T2")
    if current_probe_policy(loaded) is not None:
        raise RuntimeError("D2 policy already present; T2 would not be a new competence")

    acquired = acquire_d2_policy(parts, ORIGIN_COMPOSITION)
    bundle, method = admit_probe_policy(
        loaded, acquired["name"], ORIGIN_COMPOSITION, "OCM_2", "admit-d2-probe-policy"
    )
    test_rows, test_total, test_checks, test_probes = evaluate_diagnosis(
        parts["d2_test"], acquired["name"]
    )
    rr_rows, rr_total, rr_checks, rr_probes = evaluate_diagnosis(
        parts["d2_test"], D2_POLICY_ROUND_ROBIN
    )
    if test_total >= rr_total:
        raise RuntimeError(
            f"D2 greedy policy did not reduce held-out cost: greedy={test_total} rr={rr_total}"
        )
    if test_probes >= rr_probes:
        raise RuntimeError("D2 policy did not reduce probe count on the diagnosis family")

    # Retention: D0 MACRO still used; D1 failure still reduces traps.
    d0_rows, d0_total, d0_checks, d0_skipped = search_bundle(bundle, parts["test"], MAX_LEN_T0)
    d0_macro_used = any(row["macro_used"] for row in d0_rows)
    if not d0_macro_used:
        raise RuntimeError("T2 negative transfer: T0 MACRO no longer used on D0 held-out")
    d1_rows, d1_total, d1_checks, d1_skipped = search_bundle(bundle, parts["trap_test"], MAX_LEN_T1)
    d1_without = t1["learned"]["trap_without_test"]["total"]
    if not (d1_total < d1_without or d1_skipped > 0):
        raise RuntimeError("T2 negative transfer: T1 failure memory no longer reduces traps")

    bundle["resource_history"].append({
        "stage": "OCM_2",
        "d2_test_work_units": test_total,
        "d2_test_probes": test_probes,
        "d0_retention_work_units": d0_total,
        "d1_retention_work_units": d1_total,
    })
    continued.persist(bundle)
    restarted = continued.load()
    if restarted["lineage_id"] != LINEAGE_ID:
        raise RuntimeError("lineage id changed across T2 restart")
    assert_constitution_frozen(restarted)
    if current_macro(restarted) != current_macro(loaded):
        raise RuntimeError("T0 macro was not retained at T2")
    if not restarted["failure_counterexample_knowledge"]:
        raise RuntimeError("T1 failure knowledge did not survive T2 restart")
    if current_probe_policy(restarted) is None:
        raise RuntimeError("D2 probe policy did not survive restart")

    # Reset arm: isolated empty store, must re-acquire T0 then T1 then T2.
    try:
        reset.load()
        saw_continued = True
    except FileNotFoundError:
        saw_continued = False
    if saw_continued:
        raise IsolationError("reset arm loaded a bundle before acquiring; isolation broken")
    reset_seed = empty_bundle()
    reset.persist(reset_seed)
    reset_acquired = acquire_macro(parts, ORIGIN_REDISCOVERY)
    reset_bundle, reset_method = admit_macro(
        reset.load(), reset_acquired["macro"], ORIGIN_REDISCOVERY, "OCM_0", "reset-reacquire-macro"
    )
    reset.persist(reset_bundle)
    reset_learned = learn_failure(reset.load(), parts["trap_train"], parts["trap_test"], parts["test"])
    reset.persist(reset_learned["bundle"])
    reset_d2 = acquire_d2_policy(parts, ORIGIN_REDISCOVERY)
    reset_bundle2, reset_d2_method = admit_probe_policy(
        reset.load(), reset_d2["name"], ORIGIN_REDISCOVERY, "OCM_2", "reset-reacquire-d2-policy"
    )
    reset.persist(reset_bundle2)
    reset_test_rows, reset_test_total, _, reset_test_probes = evaluate_diagnosis(
        parts["d2_test"], reset_d2["name"]
    )
    if Path(reset.root).resolve().is_relative_to(Path(continued.root).resolve()):
        raise IsolationError("reset nested under continued")

    continued_t2_work = (
        acquired["train_total"]
        + acquired["tournament"]["all_candidate_validation_cost"]
        + test_total
    )
    reset_t2_work = (
        reset_acquired["training_slots"]
        + reset_acquired["tournament"]["all_candidate_validation_attempts"]
        + reset_learned["trap_with_total"]
        + reset_d2["train_total"]
        + reset_d2["tournament"]["all_candidate_validation_cost"]
        + reset_test_total
    )
    if reset_t2_work <= continued_t2_work:
        raise RuntimeError(
            f"reset must cost more than continued at T2: reset={reset_t2_work} continued={continued_t2_work}"
        )

    # Task-specific: diagnosis family only, no T0/T1 state.
    task_seed = empty_bundle()
    task_specific.persist(task_seed)
    task_acquired = acquire_d2_policy(parts, ORIGIN_COMPOSITION)
    task_rows, task_total, _, task_probes = evaluate_diagnosis(parts["d2_test"], task_acquired["name"])
    task_work = (
        task_acquired["train_total"]
        + task_acquired["tournament"]["all_candidate_validation_cost"]
        + task_total
    )

    # Strong adaptive parent: ordinary store receives the same D2 policy.
    parent_loaded = parent.load()
    parent_acquired = acquire_d2_policy(parts, ORIGIN_COMPOSITION)
    parent_bundle, _parent_method = admit_probe_policy(
        parent_loaded, parent_acquired["name"], ORIGIN_COMPOSITION, "OCM_2", "parent-admit-d2-policy"
    )
    parent.persist(parent_bundle)
    parent_rows, parent_total, _, parent_probes = evaluate_diagnosis(
        parts["d2_test"], parent_acquired["name"]
    )
    parent_work = (
        parent_acquired["train_total"]
        + parent_acquired["tournament"]["all_candidate_validation_cost"]
        + parent_total
    )

    ablation_rows, ablation_total, _, ablation_probes = evaluate_diagnosis(
        parts["d2_test"], D2_POLICY_ROUND_ROBIN
    )
    effect_disappears = ablation_total > test_total

    n_objects = count_objects(restarted)
    k = 1 + 1 + 1 + 4  # macro + failure + probe policy + polynomial primitives
    bytes_written = persist_bytes(continued)
    actual = [w for w in d2_witnesses(test_rows, [method["identity"]]) if w["invoked_identities"]]
    if not actual:
        raise RuntimeError("T2 had no actual probe-policy consumption witnesses")

    chi_before = float(rr_probes)
    chi_after = float(test_probes)
    omega = float(len(parts["d2_train"])) and (1.0 / len(parts["d2_train"]))

    strongest = {
        "CONTINUED_OCM": arm_result(
            "CONTINUED_OCM",
            continued_t2_work,
            True,
            False,
            "loaded T1 bundle; admitted D2 probe policy; T0/T1 retained; no reset",
        ),
        "RESET_OCM": arm_result(
            "RESET_OCM",
            reset_t2_work,
            False,
            False,
            "isolated empty store; re-acquired T0 macro, T1 failure memory, then D2 policy",
        ),
        "TASK_SPECIFIC_OCM": arm_result(
            "TASK_SPECIFIC_OCM",
            task_work,
            False,
            False,
            "diagnosis family only; no T0 macro and no T1 failure schema",
        ),
        "STRONG_ADAPTIVE_PARENT": arm_result(
            "STRONG_ADAPTIVE_PARENT",
            parent_work,
            True,
            False,
            "ordinary persistent probe-policy table; comparator evolved at T2",
        ),
        "reset_costs_more_or_fails_reuse": True,
        "parent_ties_continued_mechanism": parent_total == test_total,
        "winner": "CONTINUED_OCM_BEATS_RESET",
        "notes": (
            "Continued reuses T0/T1 and only pays D2 acquisition. Reset rediscovers "
            "independently and pays T0+T1+T2. D0/D1 do not cheapen D2 versus a "
            "task-specific diagnosis learner; that is recorded, not claimed as transfer. "
            "The ordinary probe-policy parent may tie the T2 mechanism."
        ),
    }

    donor_now = [d["identity"] for d in restarted["imported_donors"]]
    added_ops = [d["identity"] for d in d2_taught_donors()]
    transition = emit_transition(
        lineage_id=LINEAGE_ID,
        source_stage="OCM_1",
        target_stage="OCM_2",
        source_machine_identity=source_id,
        target_bundle=restarted,
        imported_donor_identities=donor_now,
        prior_information_manifest=d2_prior_manifest(),
        new_information_supplied={
            "training_task_ids": [t["fingerprint"] for t in parts["d2_train"]],
            "examples": D2_TRAIN_N,
            "labels": 0,
        },
        new_methods_schemas=[
            {
                "identity": method["identity"],
                "kind": "method",
                "origin_category": ORIGIN_COMPOSITION,
                "payload": method["payload"],
            },
            {
                "identity": restarted["method_schemas"][-1]["identity"],
                "kind": "schema",
                "origin_category": ORIGIN_COMPOSITION,
                "payload": restarted["method_schemas"][-1]["payload"],
            },
        ],
        reused_method_identities=[
            t0["method"]["identity"],
            t1["learned"]["record"]["identity"],
        ],
        actual_execution_witnesses=actual,
        primitive_operators_added=added_ops,
        composition_depth=max(0, len(current_macro(restarted)) - 1),
        acquisition_cost=cost(
            acquired["train_total"] + acquired["tournament"]["all_candidate_validation_cost"],
            D2_TRAIN_N + D2_VAL_N,
            "D2 train evidence plus validation tournament over probe policies",
        ),
        reasoning_cost=cost(test_total, D2_TEST_N, "held-out diagnosis episodes with learned probe policy"),
        verification_cost=cost(test_checks, D2_TEST_N, "identified hidden states independently rechecked"),
        revision_cost=cost(1, 0, "probe-policy admission"),
        self_change_cost=cost(1, 0, "one D2 method admission"),
        maintenance_cost=cost(0, 0, "no extra index maintenance beyond the bundle write"),
        persistent_bytes=bytes_written,
        active_k_n={"k": k, "N": n_objects, "ratio": k / n_objects},
        kappa=coordinate(3 / n_objects, "MEASURED", "macro + failure record + one local D2 probe policy"),
        omega=coordinate(omega, "MEASURED", "diagnosis from D2-train probes; not a supplied root-cause label"),
        chi=coordinate(chi_after, "MEASURED", f"held-out probe count after policy; round-robin={chi_before}"),
        retention={
            "prior_methods_retained": True,
            "prior_failure_knowledge_retained": True,
            "notes": "T0 MACRO and T1 failure memory retained; D2 is a disjoint diagnosis competence",
        },
        negative_transfer={
            "observed": False,
            "harmful_tasks": 0,
            "notes": "D2 serving is family-gated; polynomial tasks still use MACRO/failure memory",
        },
        ablation={
            "removed": method["identity"],
            "effect_disappears": effect_disappears,
            "notes": "dropping the probe policy returns diagnosis search to round-robin probing",
        },
        strongest_parent_result=strongest,
        terminal="OCM_2_D2_PROBE_POLICY_ADDED",
    )
    return {
        "bundle": restarted,
        "transition": transition,
        "acquired": acquired,
        "continued_t2_work": continued_t2_work,
        "reset_t2_work": reset_t2_work,
        "task_work": task_work,
        "parent_work": parent_work,
        "test_total": test_total,
        "rr_total": rr_total,
        "test_probes": test_probes,
        "rr_probes": rr_probes,
        "reset_origin": reset_d2_method["origin_category"],
        "policy_name": acquired["name"],
        "d0_retained": d0_macro_used,
        "d1_retained": d1_total < d1_without or d1_skipped > 0,
        "ablation_total": ablation_total,
        "families_disjoint": True,
        "historical_m11_relabeled": False,
        "constitution": list(constitution_of(restarted)),
    }


def d3_witnesses(rows, invoked):
    out = []
    for row in rows:
        out.append({
            "task_id": row["task"],
            "invoked_identities": list(invoked) if row.get("lemma_used") else [],
            "token_word": list(row["token_word"]),
            "program": list(row["program"]),
            "enumeration_attempts": row["enumeration_attempts"],
            "verified": row["verified"],
        })
    return out


def acquire_d3_lemma(parts, origin: str):
    discovered = discover_cut_lemma(parts["d3_train"], origin)
    tour = d3_tournament(parts["d3_val"], discovered["lemma"])
    if not tour["accepted"]:
        raise RuntimeError("D3 tournament selected no CUT lemma introduction")
    return {
        "lemma": discovered["lemma"],
        "lemma_id": discovered["lemma"].lemma_id,
        "origin": origin,
        "tournament": tour,
        "discovery_cost": discovered["discovery_cost"],
        "identities_enumerated": discovered["identities_enumerated"],
        "attempts": discovered["attempts"],
    }


def run_t3(continued: LineageStore, reset: LineageStore, parent: LineageStore, task_specific: LineageStore, parts, t0, t1, t2):
    assert_disjoint_stores(continued, reset)
    loaded = continued.load()
    if loaded["lineage_id"] != LINEAGE_ID:
        raise RuntimeError("T3 must keep the T0/T1/T2 lineage id")
    assert_constitution_frozen(loaded)
    if constitution_of(loaded) != CONSTITUTION:
        raise RuntimeError("constitution mutated before T3")
    source_id = machine_identity(loaded)
    if current_macro(loaded) is None:
        raise RuntimeError("principal arm missing T0 macro at T3")
    if not loaded["failure_counterexample_knowledge"]:
        raise RuntimeError("principal arm missing T1 failure memory at T3")
    if current_probe_policy(loaded) is None:
        raise RuntimeError("principal arm missing T2 probe policy at T3")
    if current_cut_lemma(loaded) is not None:
        raise RuntimeError("D3 CUT lemma already present; T3 would not be a new competence")

    acquired = acquire_d3_lemma(parts, ORIGIN_COMPOSITION)
    if acquired["lemma_id"] in D3_FROZEN_LEMMA_NAMES:
        raise RuntimeError("D3 invented frozen PREFIX/SWAP name")
    bundle, method = admit_cut_lemma(
        loaded, acquired["lemma"], ORIGIN_COMPOSITION, "OCM_3", "admit-d3-cut-lemma"
    )
    live_lemma = lemma_from_method(method)
    test_rows, test_total, test_checks, test_used = evaluate_hilbert(parts["d3_test"], live_lemma)
    prim_rows, prim_total, prim_checks, prim_used = evaluate_hilbert(parts["d3_test"], None)
    if not all(row["status"] == "FOUND" and row["lemma_used"] and row["verified"] for row in test_rows):
        raise RuntimeError("D3 CUT lemma did not finish held-out Hilbert theorems")
    if any(row["status"] == "FOUND" for row in prim_rows):
        raise RuntimeError("D3 primitive K/S search finished held-out theorems; lemma not required")
    if test_used != len(parts["d3_test"]):
        raise RuntimeError("D3 held-out did not actually invoke the invented CUT lemma")
    if any(row["one_step_hits"] for row in test_rows):
        raise RuntimeError("D3 held-out was a one-step lemma hit; composition was not earned")

    d0_rows, d0_total, d0_checks, d0_skipped = search_bundle(bundle, parts["test"], MAX_LEN_T0)
    d0_macro_used = any(row["macro_used"] for row in d0_rows)
    if not d0_macro_used:
        raise RuntimeError("T3 negative transfer: T0 MACRO no longer used on D0 held-out")
    d1_rows, d1_total, d1_checks, d1_skipped = search_bundle(bundle, parts["trap_test"], MAX_LEN_T1)
    d1_without = t1["learned"]["trap_without_test"]["total"]
    if not (d1_total < d1_without or d1_skipped > 0):
        raise RuntimeError("T3 negative transfer: T1 failure memory no longer reduces traps")
    d2_rows, d2_total, d2_checks, d2_probes = evaluate_diagnosis(
        parts["d2_test"], t2["policy_name"]
    )
    rr_rows, rr_total, rr_checks, rr_probes = evaluate_diagnosis(
        parts["d2_test"], D2_POLICY_ROUND_ROBIN
    )
    if d2_probes >= rr_probes:
        raise RuntimeError("T3 negative transfer: T2 probe policy no longer beats round-robin")

    bundle["resource_history"].append({
        "stage": "OCM_3",
        "d3_test_work_units": test_total,
        "d3_lemma_uses": test_used,
        "d0_retention_work_units": d0_total,
        "d1_retention_work_units": d1_total,
        "d2_retention_probes": d2_probes,
    })
    continued.persist(bundle)
    restarted = continued.load()
    if restarted["lineage_id"] != LINEAGE_ID:
        raise RuntimeError("lineage id changed across T3 restart")
    assert_constitution_frozen(restarted)
    if current_macro(restarted) != current_macro(loaded):
        raise RuntimeError("T0 macro was not retained at T3")
    if not restarted["failure_counterexample_knowledge"]:
        raise RuntimeError("T1 failure knowledge did not survive T3 restart")
    if current_probe_policy(restarted) is None:
        raise RuntimeError("T2 probe policy did not survive T3 restart")
    restarted_cut = current_cut_lemma(restarted)
    if restarted_cut is None:
        raise RuntimeError("D3 CUT lemma did not survive restart")
    restored_lemma = lemma_from_method(restarted_cut)
    if restored_lemma.lemma_id != acquired["lemma_id"]:
        raise RuntimeError("D3 CUT lemma identity mutated across restart")

    try:
        reset.load()
        saw_continued = True
    except FileNotFoundError:
        saw_continued = False
    if saw_continued:
        raise IsolationError("reset arm loaded a bundle before acquiring; isolation broken")
    reset_seed = empty_bundle()
    reset.persist(reset_seed)
    reset_acquired = acquire_macro(parts, ORIGIN_REDISCOVERY)
    reset_bundle, reset_method = admit_macro(
        reset.load(), reset_acquired["macro"], ORIGIN_REDISCOVERY, "OCM_0", "reset-reacquire-macro"
    )
    reset.persist(reset_bundle)
    reset_learned = learn_failure(reset.load(), parts["trap_train"], parts["trap_test"], parts["test"])
    reset.persist(reset_learned["bundle"])
    reset_d2 = acquire_d2_policy(parts, ORIGIN_REDISCOVERY)
    reset_bundle2, reset_d2_method = admit_probe_policy(
        reset.load(), reset_d2["name"], ORIGIN_REDISCOVERY, "OCM_2", "reset-reacquire-d2-policy"
    )
    reset.persist(reset_bundle2)
    reset_d3 = acquire_d3_lemma(parts, ORIGIN_REDISCOVERY)
    reset_bundle3, reset_d3_method = admit_cut_lemma(
        reset.load(), reset_d3["lemma"], ORIGIN_REDISCOVERY, "OCM_3", "reset-reacquire-d3-cut"
    )
    reset.persist(reset_bundle3)
    reset_test_rows, reset_test_total, _, reset_test_used = evaluate_hilbert(
        parts["d3_test"], reset_d3["lemma"]
    )
    if Path(reset.root).resolve().is_relative_to(Path(continued.root).resolve()):
        raise IsolationError("reset nested under continued")

    continued_t3_work = (
        acquired["discovery_cost"]
        + acquired["tournament"]["all_candidate_validation_cost"]
        + test_total
    )
    reset_t3_work = (
        reset_acquired["training_slots"]
        + reset_acquired["tournament"]["all_candidate_validation_attempts"]
        + reset_learned["trap_with_total"]
        + reset_d2["train_total"]
        + reset_d2["tournament"]["all_candidate_validation_cost"]
        + reset_d3["discovery_cost"]
        + reset_d3["tournament"]["all_candidate_validation_cost"]
        + reset_test_total
    )
    if reset_t3_work <= continued_t3_work:
        raise RuntimeError(
            f"reset must cost more than continued at T3: reset={reset_t3_work} continued={continued_t3_work}"
        )

    task_seed = empty_bundle()
    task_specific.persist(task_seed)
    task_acquired = acquire_d3_lemma(parts, ORIGIN_COMPOSITION)
    task_rows, task_total, _, task_used = evaluate_hilbert(parts["d3_test"], task_acquired["lemma"])
    task_work = (
        task_acquired["discovery_cost"]
        + task_acquired["tournament"]["all_candidate_validation_cost"]
        + task_total
    )

    parent_loaded = parent.load()
    parent_acquired = acquire_d3_lemma(parts, ORIGIN_COMPOSITION)
    parent_bundle, _parent_method = admit_cut_lemma(
        parent_loaded, parent_acquired["lemma"], ORIGIN_COMPOSITION, "OCM_3", "parent-admit-d3-cut"
    )
    parent.persist(parent_bundle)
    parent_rows, parent_total, _, parent_used = evaluate_hilbert(
        parts["d3_test"], parent_acquired["lemma"]
    )
    parent_work = (
        parent_acquired["discovery_cost"]
        + parent_acquired["tournament"]["all_candidate_validation_cost"]
        + parent_total
    )

    ablation_rows, ablation_total, _, ablation_used = evaluate_hilbert(parts["d3_test"], None)
    effect_disappears = (
        all(row["status"] != "FOUND" for row in ablation_rows) and test_used > 0
    )

    n_objects = count_objects(restarted)
    k = 1 + 1 + 1 + 1 + 4
    bytes_written = persist_bytes(continued)
    actual = [w for w in d3_witnesses(test_rows, [method["identity"]]) if w["invoked_identities"]]
    if not actual:
        raise RuntimeError("T3 had no actual CUT-lemma consumption witnesses")

    chi_before = float(prim_total)
    chi_after = float(test_total)
    omega = 1.0 / len(parts["d3_train"])

    strongest = {
        "CONTINUED_OCM": arm_result(
            "CONTINUED_OCM",
            continued_t3_work,
            True,
            False,
            "loaded T2 bundle; admitted D3 CUT lemma; T0/T1/T2 retained; no reset",
        ),
        "RESET_OCM": arm_result(
            "RESET_OCM",
            reset_t3_work,
            False,
            False,
            "isolated empty store; re-acquired T0 macro, T1 failure memory, T2 policy, then D3 CUT lemma",
        ),
        "TASK_SPECIFIC_OCM": arm_result(
            "TASK_SPECIFIC_OCM",
            task_work,
            False,
            False,
            "Hilbert/SK family only; no T0 macro, T1 failure schema, or T2 probe policy",
        ),
        "STRONG_ADAPTIVE_PARENT": arm_result(
            "STRONG_ADAPTIVE_PARENT",
            parent_work,
            True,
            False,
            "ordinary persistent CUT-lemma library; comparator evolved at T3",
        ),
        "reset_costs_more_or_fails_reuse": True,
        "parent_ties_continued_mechanism": parent_total == test_total,
        "winner": "CONTINUED_OCM_BEATS_RESET",
        "notes": (
            "Continued reuses T0/T1/T2 and only pays D3 acquisition. Reset rediscovers "
            "independently and pays T0+T1+T2+T3. D0/D1/D2 do not cheapen D3 versus a "
            "task-specific Hilbert learner; that is recorded, not claimed as transfer. "
            "The ordinary CUT-lemma parent may tie the T3 mechanism. Not Metamath, not FLT, "
            "not historical M11 relabel."
        ),
    }

    donor_now = [d["identity"] for d in restarted["imported_donors"]]
    added_ops = [d["identity"] for d in d3_taught_donors()]
    t2_policy_id = current_probe_policy(restarted)["identity"]
    transition = emit_transition(
        lineage_id=LINEAGE_ID,
        source_stage="OCM_2",
        target_stage="OCM_3",
        source_machine_identity=source_id,
        target_bundle=restarted,
        imported_donor_identities=donor_now,
        prior_information_manifest=d3_prior_manifest(),
        new_information_supplied={
            "training_task_ids": [t["fingerprint"] for t in parts["d3_train"]],
            "examples": D3_TRAIN_N,
            "labels": 0,
        },
        new_methods_schemas=[
            {
                "identity": method["identity"],
                "kind": "method",
                "origin_category": ORIGIN_COMPOSITION,
                "payload": method["payload"],
            },
            {
                "identity": restarted["method_schemas"][-1]["identity"],
                "kind": "schema",
                "origin_category": ORIGIN_COMPOSITION,
                "payload": restarted["method_schemas"][-1]["payload"],
            },
        ],
        reused_method_identities=[
            t0["method"]["identity"],
            t1["learned"]["record"]["identity"],
            t2_policy_id,
        ],
        actual_execution_witnesses=actual,
        primitive_operators_added=added_ops,
        composition_depth=max(0, len(current_macro(restarted)) - 1),
        acquisition_cost=cost(
            acquired["discovery_cost"] + acquired["tournament"]["all_candidate_validation_cost"],
            D3_TRAIN_N + D3_VAL_N,
            "D3 CUT_* discovery plus validation tournament versus primitive K/S",
        ),
        reasoning_cost=cost(test_total, D3_TEST_N, "held-out compose-second theorems with invented CUT lemma"),
        verification_cost=cost(test_checks, D3_TEST_N, "kernel-checked Hilbert reconstructions"),
        revision_cost=cost(1, 0, "CUT-lemma admission"),
        self_change_cost=cost(1, 0, "one D3 method admission"),
        maintenance_cost=cost(0, 0, "no extra index maintenance beyond the bundle write"),
        persistent_bytes=bytes_written,
        active_k_n={"k": k, "N": n_objects, "ratio": k / n_objects},
        kappa=coordinate(4 / n_objects, "MEASURED", "macro + failure + D2 policy + one local D3 CUT lemma"),
        omega=coordinate(omega, "MEASURED", "lemma introduction from D3-train discovery; not a supplied Metamath label"),
        chi=coordinate(chi_after, "MEASURED", f"held-out inhabit cost after CUT; primitive={chi_before}"),
        retention={
            "prior_methods_retained": True,
            "prior_failure_knowledge_retained": True,
            "notes": "T0 MACRO, T1 failure memory, and T2 probe policy retained; D3 is a disjoint Hilbert competence",
        },
        negative_transfer={
            "observed": False,
            "harmful_tasks": 0,
            "notes": "D3 serving is family-gated; polynomial and diagnosis tasks still use MACRO/failure/probe policy",
        },
        ablation={
            "removed": method["identity"],
            "effect_disappears": effect_disappears,
            "notes": "dropping the CUT lemma returns compose-second search to primitive K/S, which cannot finish",
        },
        strongest_parent_result=strongest,
        terminal="OCM_3_D3_CUT_LEMMA_ADDED",
    )
    return {
        "bundle": restarted,
        "transition": transition,
        "acquired": acquired,
        "continued_t3_work": continued_t3_work,
        "reset_t3_work": reset_t3_work,
        "task_work": task_work,
        "parent_work": parent_work,
        "test_total": test_total,
        "prim_total": prim_total,
        "test_used": test_used,
        "reset_origin": reset_d3_method["origin_category"],
        "lemma_id": acquired["lemma_id"],
        "d0_retained": d0_macro_used,
        "d1_retained": d1_total < d1_without or d1_skipped > 0,
        "d2_retained": d2_probes < rr_probes,
        "ablation_total": ablation_total,
        "families_disjoint": True,
        "historical_m11_relabeled": False,
        "metamath_claimed": False,
        "flt_expanded": False,
        "frozen_name": acquired["lemma_id"] in D3_FROZEN_LEMMA_NAMES,
        "constitution": list(constitution_of(restarted)),
    }


def d4_witnesses(rows, invoked):
    out = []
    for row in rows:
        out.append({
            "task_id": row["task"],
            "invoked_identities": list(invoked) if row.get("rewrite_used") else [],
            "token_word": list(row["token_word"]),
            "program": list(row["program"]),
            "enumeration_attempts": row["enumeration_attempts"],
            "verified": row["verified"],
        })
    return out


def acquire_d4_rewrite(parts, origin: str):
    discovered = discover_rewrite_rule(parts["d4_train"], origin)
    tour = d4_tournament(parts["d4_val"], discovered["rule"])
    if not tour["accepted"]:
        raise RuntimeError("D4 tournament selected no exact string-rewrite rule")
    return {
        "rule": discovered["rule"],
        "rule_id": discovered["rule"]["rule_id"],
        "origin": origin,
        "tournament": tour,
        "discovery_cost": discovered["discovery_cost"],
        "attempts": discovered["attempts"],
    }


def run_t4(continued: LineageStore, reset: LineageStore, parent: LineageStore, task_specific: LineageStore, parts, t0, t1, t2, t3):
    assert_disjoint_stores(continued, reset)
    loaded = continued.load()
    if loaded["lineage_id"] != LINEAGE_ID:
        raise RuntimeError("T4 must keep the T0/T1/T2/T3 lineage id")
    assert_constitution_frozen(loaded)
    if constitution_of(loaded) != CONSTITUTION:
        raise RuntimeError("constitution mutated before T4")
    source_id = machine_identity(loaded)
    if current_macro(loaded) is None:
        raise RuntimeError("principal arm missing T0 macro at T4")
    if not loaded["failure_counterexample_knowledge"]:
        raise RuntimeError("principal arm missing T1 failure memory at T4")
    if current_probe_policy(loaded) is None:
        raise RuntimeError("principal arm missing T2 probe policy at T4")
    if current_cut_lemma(loaded) is None:
        raise RuntimeError("principal arm missing T3 CUT lemma at T4")
    if current_rewrite_rule(loaded) is not None:
        raise RuntimeError("D4 rewrite already present; T4 would not be a new competence")

    acquired = acquire_d4_rewrite(parts, ORIGIN_COMPOSITION)
    if acquired["rule_id"] in D4_FROZEN_RULE_NAMES:
        raise RuntimeError("D4 invented frozen REGEX/EVAL name")
    if acquired["rule_id"].startswith("CUT_"):
        raise RuntimeError("D4 invented a Hilbert CUT_* name")
    bundle, method = admit_rewrite_rule(
        loaded, acquired["rule"], ORIGIN_COMPOSITION, "OCM_4", "admit-d4-rewrite-rule"
    )
    test_rows, test_total, test_checks, test_used = evaluate_rewrite(parts["d4_test"], acquired["rule"])
    prim_rows, prim_total, prim_checks, prim_used = evaluate_rewrite(parts["d4_test"], None)
    if not all(row["status"] == "FOUND" and row["rewrite_used"] and row["verified"] for row in test_rows):
        raise RuntimeError("D4 rewrite did not finish held-out string-rewrite tasks")
    if any(row["status"] == "FOUND" for row in prim_rows):
        raise RuntimeError("D4 primitive substitute search finished held-out tasks; rewrite not required")
    if test_used != len(parts["d4_test"]):
        raise RuntimeError("D4 held-out did not actually invoke the invented rewrite")

    d0_rows, d0_total, d0_checks, d0_skipped = search_bundle(bundle, parts["test"], MAX_LEN_T0)
    d0_macro_used = any(row["macro_used"] for row in d0_rows)
    if not d0_macro_used:
        raise RuntimeError("T4 negative transfer: T0 MACRO no longer used on D0 held-out")
    d1_rows, d1_total, d1_checks, d1_skipped = search_bundle(bundle, parts["trap_test"], MAX_LEN_T1)
    d1_without = t1["learned"]["trap_without_test"]["total"]
    if not (d1_total < d1_without or d1_skipped > 0):
        raise RuntimeError("T4 negative transfer: T1 failure memory no longer reduces traps")
    d2_rows, d2_total, d2_checks, d2_probes = evaluate_diagnosis(
        parts["d2_test"], t2["policy_name"]
    )
    rr_rows, rr_total, rr_checks, rr_probes = evaluate_diagnosis(
        parts["d2_test"], D2_POLICY_ROUND_ROBIN
    )
    if d2_probes >= rr_probes:
        raise RuntimeError("T4 negative transfer: T2 probe policy no longer beats round-robin")
    d3_rows, d3_total, d3_checks, d3_used = evaluate_hilbert(parts["d3_test"], t3["acquired"]["lemma"])
    if d3_used != len(parts["d3_test"]):
        raise RuntimeError("T4 negative transfer: T3 CUT lemma no longer finishes Hilbert")

    bundle["resource_history"].append({
        "stage": "OCM_4",
        "d4_test_work_units": test_total,
        "d4_rewrite_uses": test_used,
        "d0_retention_work_units": d0_total,
        "d1_retention_work_units": d1_total,
        "d2_retention_probes": d2_probes,
        "d3_retention_lemma_uses": d3_used,
    })
    continued.persist(bundle)
    restarted = continued.load()
    if restarted["lineage_id"] != LINEAGE_ID:
        raise RuntimeError("lineage id changed across T4 restart")
    assert_constitution_frozen(restarted)
    if current_macro(restarted) != current_macro(loaded):
        raise RuntimeError("T0 macro was not retained at T4")
    if not restarted["failure_counterexample_knowledge"]:
        raise RuntimeError("T1 failure knowledge did not survive T4 restart")
    if current_probe_policy(restarted) is None:
        raise RuntimeError("T2 probe policy did not survive T4 restart")
    if current_cut_lemma(restarted) is None:
        raise RuntimeError("T3 CUT lemma did not survive T4 restart")
    restarted_rule = current_rewrite_rule(restarted)
    if restarted_rule is None:
        raise RuntimeError("D4 rewrite did not survive restart")
    if restarted_rule["payload"]["rule_id"] != acquired["rule_id"]:
        raise RuntimeError("D4 rewrite identity mutated across restart")

    try:
        reset.load()
        saw_continued = True
    except FileNotFoundError:
        saw_continued = False
    if saw_continued:
        raise IsolationError("reset arm loaded a bundle before acquiring; isolation broken")
    reset_seed = empty_bundle()
    reset.persist(reset_seed)
    reset_acquired = acquire_macro(parts, ORIGIN_REDISCOVERY)
    reset_bundle, reset_method = admit_macro(
        reset.load(), reset_acquired["macro"], ORIGIN_REDISCOVERY, "OCM_0", "reset-reacquire-macro"
    )
    reset.persist(reset_bundle)
    reset_learned = learn_failure(reset.load(), parts["trap_train"], parts["trap_test"], parts["test"])
    reset.persist(reset_learned["bundle"])
    reset_d2 = acquire_d2_policy(parts, ORIGIN_REDISCOVERY)
    reset_bundle2, reset_d2_method = admit_probe_policy(
        reset.load(), reset_d2["name"], ORIGIN_REDISCOVERY, "OCM_2", "reset-reacquire-d2-policy"
    )
    reset.persist(reset_bundle2)
    reset_d3 = acquire_d3_lemma(parts, ORIGIN_REDISCOVERY)
    reset_bundle3, reset_d3_method = admit_cut_lemma(
        reset.load(), reset_d3["lemma"], ORIGIN_REDISCOVERY, "OCM_3", "reset-reacquire-d3-cut"
    )
    reset.persist(reset_bundle3)
    reset_d4 = acquire_d4_rewrite(parts, ORIGIN_REDISCOVERY)
    reset_bundle4, reset_d4_method = admit_rewrite_rule(
        reset.load(), reset_d4["rule"], ORIGIN_REDISCOVERY, "OCM_4", "reset-reacquire-d4-rewrite"
    )
    reset.persist(reset_bundle4)
    reset_test_rows, reset_test_total, _, reset_test_used = evaluate_rewrite(
        parts["d4_test"], reset_d4["rule"]
    )
    if Path(reset.root).resolve().is_relative_to(Path(continued.root).resolve()):
        raise IsolationError("reset nested under continued")

    continued_t4_work = (
        acquired["discovery_cost"]
        + acquired["tournament"]["all_candidate_validation_cost"]
        + test_total
    )
    reset_t4_work = (
        reset_acquired["training_slots"]
        + reset_acquired["tournament"]["all_candidate_validation_attempts"]
        + reset_learned["trap_with_total"]
        + reset_d2["train_total"]
        + reset_d2["tournament"]["all_candidate_validation_cost"]
        + reset_d3["discovery_cost"]
        + reset_d3["tournament"]["all_candidate_validation_cost"]
        + reset_d4["discovery_cost"]
        + reset_d4["tournament"]["all_candidate_validation_cost"]
        + reset_test_total
    )
    if reset_t4_work <= continued_t4_work:
        raise RuntimeError(
            f"reset must cost more than continued at T4: reset={reset_t4_work} continued={continued_t4_work}"
        )

    task_seed = empty_bundle()
    task_specific.persist(task_seed)
    task_acquired = acquire_d4_rewrite(parts, ORIGIN_COMPOSITION)
    task_rows, task_total, _, task_used = evaluate_rewrite(parts["d4_test"], task_acquired["rule"])
    task_work = (
        task_acquired["discovery_cost"]
        + task_acquired["tournament"]["all_candidate_validation_cost"]
        + task_total
    )

    parent_loaded = parent.load()
    parent_acquired = acquire_d4_rewrite(parts, ORIGIN_COMPOSITION)
    parent_bundle, _parent_method = admit_rewrite_rule(
        parent_loaded, parent_acquired["rule"], ORIGIN_COMPOSITION, "OCM_4", "parent-admit-d4-rewrite"
    )
    parent.persist(parent_bundle)
    parent_rows, parent_total, _, parent_used = evaluate_rewrite(
        parts["d4_test"], parent_acquired["rule"]
    )
    parent_work = (
        parent_acquired["discovery_cost"]
        + parent_acquired["tournament"]["all_candidate_validation_cost"]
        + parent_total
    )

    ablation_rows, ablation_total, _, ablation_used = evaluate_rewrite(parts["d4_test"], None)
    effect_disappears = (
        all(row["status"] != "FOUND" for row in ablation_rows) and test_used > 0
    )

    n_objects = count_objects(restarted)
    k = 1 + 1 + 1 + 1 + 1 + 4
    bytes_written = persist_bytes(continued)
    actual = [w for w in d4_witnesses(test_rows, [method["identity"]]) if w["invoked_identities"]]
    if not actual:
        raise RuntimeError("T4 had no actual rewrite consumption witnesses")

    chi_before = float(prim_total)
    chi_after = float(test_total)
    omega = 1.0 / len(parts["d4_train"])

    strongest = {
        "CONTINUED_OCM": arm_result(
            "CONTINUED_OCM",
            continued_t4_work,
            True,
            False,
            "loaded T3 bundle; admitted D4 rewrite; T0/T1/T2/T3 retained; no reset",
        ),
        "RESET_OCM": arm_result(
            "RESET_OCM",
            reset_t4_work,
            False,
            False,
            "isolated empty store; re-acquired T0 macro, T1 failure memory, T2 policy, T3 CUT lemma, then D4 rewrite",
        ),
        "TASK_SPECIFIC_OCM": arm_result(
            "TASK_SPECIFIC_OCM",
            task_work,
            False,
            False,
            "string-rewrite family only; no T0 macro, T1 failure schema, T2 probe policy, or T3 CUT lemma",
        ),
        "STRONG_ADAPTIVE_PARENT": arm_result(
            "STRONG_ADAPTIVE_PARENT",
            parent_work,
            True,
            False,
            "ordinary persistent rewrite-rule library; comparator evolved at T4",
        ),
        "reset_costs_more_or_fails_reuse": True,
        "parent_ties_continued_mechanism": parent_total == test_total,
        "winner": "CONTINUED_OCM_BEATS_RESET",
        "notes": (
            "Continued reuses T0/T1/T2/T3 and only pays D4 acquisition. Reset rediscovers "
            "independently and pays T0+T1+T2+T3+T4. D0/D1/D2/D3 do not cheapen D4 versus a "
            "task-specific rewrite learner; that is recorded, not claimed as transfer. "
            "The ordinary rewrite parent may tie the T4 mechanism. Not Metamath, not FLT, "
            "not historical M11 relabel."
        ),
    }

    donor_now = [d["identity"] for d in restarted["imported_donors"]]
    added_ops = [d["identity"] for d in d4_taught_donors()]
    t2_policy_id = current_probe_policy(restarted)["identity"]
    t3_cut_id = current_cut_lemma(restarted)["identity"]
    transition = emit_transition(
        lineage_id=LINEAGE_ID,
        source_stage="OCM_3",
        target_stage="OCM_4",
        source_machine_identity=source_id,
        target_bundle=restarted,
        imported_donor_identities=donor_now,
        prior_information_manifest=d4_prior_manifest(),
        new_information_supplied={
            "training_task_ids": [t["fingerprint"] for t in parts["d4_train"]],
            "examples": D4_TRAIN_N,
            "labels": 0,
        },
        new_methods_schemas=[
            {
                "identity": method["identity"],
                "kind": "method",
                "origin_category": ORIGIN_COMPOSITION,
                "payload": method["payload"],
            },
            {
                "identity": restarted["method_schemas"][-1]["identity"],
                "kind": "schema",
                "origin_category": ORIGIN_COMPOSITION,
                "payload": restarted["method_schemas"][-1]["payload"],
            },
        ],
        reused_method_identities=[
            t0["method"]["identity"],
            t1["learned"]["record"]["identity"],
            t2_policy_id,
            t3_cut_id,
        ],
        actual_execution_witnesses=actual,
        primitive_operators_added=added_ops,
        composition_depth=max(0, len(current_macro(restarted)) - 1),
        acquisition_cost=cost(
            acquired["discovery_cost"] + acquired["tournament"]["all_candidate_validation_cost"],
            D4_TRAIN_N + D4_VAL_N,
            "D4 RW_* discovery plus validation tournament versus primitive substitute",
        ),
        reasoning_cost=cost(test_total, D4_TEST_N, "held-out two-occurrence PQ→QP with invented replace-all rewrite"),
        verification_cost=cost(test_checks, D4_TEST_N, "exact source-to-target string equality checks"),
        revision_cost=cost(1, 0, "rewrite-rule admission"),
        self_change_cost=cost(1, 0, "one D4 method admission"),
        maintenance_cost=cost(0, 0, "no extra index maintenance beyond the bundle write"),
        persistent_bytes=bytes_written,
        active_k_n={"k": k, "N": n_objects, "ratio": k / n_objects},
        kappa=coordinate(5 / n_objects, "MEASURED", "macro + failure + D2 policy + D3 CUT + one local D4 rewrite"),
        omega=coordinate(omega, "MEASURED", "rewrite introduction from D4-train discovery; not a supplied REGEX/EVAL label"),
        chi=coordinate(chi_after, "MEASURED", f"held-out rewrite cost after RW_*; primitive={chi_before}"),
        retention={
            "prior_methods_retained": True,
            "prior_failure_knowledge_retained": True,
            "notes": "T0 MACRO, T1 failure memory, T2 probe policy, and T3 CUT lemma retained; D4 is a disjoint string-rewrite competence",
        },
        negative_transfer={
            "observed": False,
            "harmful_tasks": 0,
            "notes": "D4 serving is family-gated; polynomial, diagnosis, and Hilbert tasks still use MACRO/failure/probe/CUT",
        },
        ablation={
            "removed": method["identity"],
            "effect_disappears": effect_disappears,
            "notes": "dropping the rewrite returns string search to primitive substitute, which cannot finish",
        },
        strongest_parent_result=strongest,
        terminal="OCM_4_D4_REWRITE_ADDED",
    )
    return {
        "bundle": restarted,
        "transition": transition,
        "acquired": acquired,
        "continued_t4_work": continued_t4_work,
        "reset_t4_work": reset_t4_work,
        "task_work": task_work,
        "parent_work": parent_work,
        "test_total": test_total,
        "prim_total": prim_total,
        "test_used": test_used,
        "reset_origin": reset_d4_method["origin_category"],
        "rule_id": acquired["rule_id"],
        "d0_retained": d0_macro_used,
        "d1_retained": d1_total < d1_without or d1_skipped > 0,
        "d2_retained": d2_probes < rr_probes,
        "d3_retained": d3_used == len(parts["d3_test"]),
        "ablation_total": ablation_total,
        "families_disjoint": True,
        "historical_m11_relabeled": False,
        "metamath_claimed": False,
        "flt_expanded": False,
        "frozen_name": acquired["rule_id"] in D4_FROZEN_RULE_NAMES,
        "constitution": list(constitution_of(restarted)),
    }


def json_clone_without_failures(bundle):
    clone = json.loads(json.dumps(bundle))
    clone["failure_counterexample_knowledge"] = []
    clone["applicability_scope"] = []
    return clone


def derive_terminal(t0, t1, t2, t3, t4) -> str:
    six_complete = False
    d5_happened = False
    chain = (
        t0["transition"]["target_stage"] == "OCM_0"
        and t1["transition"]["target_stage"] == "OCM_1"
        and t2 is not None
        and t2["transition"]["target_stage"] == "OCM_2"
        and t3 is not None
        and t3["transition"]["target_stage"] == "OCM_3"
        and t4 is not None
        and t4["transition"]["target_stage"] == "OCM_4"
        and t0["transition"]["lineage_id"]
        == t1["transition"]["lineage_id"]
        == t2["transition"]["lineage_id"]
        == t3["transition"]["lineage_id"]
        == t4["transition"]["lineage_id"]
        == LINEAGE_ID
        and t0["transition"]["target_machine_identity"] == t1["transition"]["source_machine_identity"]
        and t1["transition"]["target_machine_identity"] == t2["transition"]["source_machine_identity"]
        and t2["transition"]["target_machine_identity"] == t3["transition"]["source_machine_identity"]
        and t3["transition"]["target_machine_identity"] == t4["transition"]["source_machine_identity"]
    )
    d2_earned = bool(
        t2
        and t2["policy_name"] == D2_POLICY_GREEDY
        and t2["test_probes"] < t2["rr_probes"]
        and t2["d0_retained"]
        and t2["d1_retained"]
        and t2["reset_t2_work"] > t2["continued_t2_work"]
        and not t2["historical_m11_relabeled"]
        and t2["constitution"] == list(CONSTITUTION)
    )
    d3_earned = bool(
        t3
        and t3["lemma_id"].startswith("CUT_")
        and t3["lemma_id"] not in D3_FROZEN_LEMMA_NAMES
        and not t3["frozen_name"]
        and t3["test_used"] > 0
        and t3["d0_retained"]
        and t3["d1_retained"]
        and t3["d2_retained"]
        and t3["reset_t3_work"] > t3["continued_t3_work"]
        and not t3["historical_m11_relabeled"]
        and not t3["metamath_claimed"]
        and not t3["flt_expanded"]
        and t3["constitution"] == list(CONSTITUTION)
    )
    d4_earned = bool(
        t4
        and t4["rule_id"].startswith("RW_")
        and t4["rule_id"] not in D4_FROZEN_RULE_NAMES
        and not t4["rule_id"].startswith("CUT_")
        and not t4["frozen_name"]
        and t4["test_used"] > 0
        and t4["d0_retained"]
        and t4["d1_retained"]
        and t4["d2_retained"]
        and t4["d3_retained"]
        and t4["reset_t4_work"] > t4["continued_t4_work"]
        and not t4["historical_m11_relabeled"]
        and not t4["metamath_claimed"]
        and not t4["flt_expanded"]
        and t4["constitution"] == list(CONSTITUTION)
    )
    if t2 is None:
        return "CANNOT_CHECK_D2_TRANSITION_NOT_EARNED"
    if not d2_earned:
        return "CANNOT_CHECK_D2_PROBE_POLICY_NOT_EARNED"
    if t3 is None:
        return "CANNOT_CHECK_D3_TRANSITION_NOT_EARNED"
    if not d3_earned:
        return "CANNOT_CHECK_D3_LEMMA_INTRODUCTION_NOT_EARNED"
    if t4 is None:
        return "CANNOT_CHECK_D4_TRANSITION_NOT_EARNED"
    if not chain or not d4_earned:
        return "CANNOT_CHECK_D4_REWRITE_NOT_EARNED"
    if six_complete:
        return "CANNOT_CHECK_INTERNAL_INCONSISTENCY_SIX_MARKED_COMPLETE"
    if d5_happened:
        return "CANNOT_CHECK_INTERNAL_INCONSISTENCY_D5_MARKED_RUN"
    if t4["reset_t4_work"] > t4["continued_t4_work"]:
        return "PHASED_COGNITIVE_DEVELOPMENT"
    return "RESET_PARENT_EQUIVALENT"


def run(out: Path | None = None, transitions_dir: Path | None = None):
    start = time.perf_counter()
    parts = frozen_tasks()
    t2 = None
    t3 = None
    t4 = None
    t2_error = None
    t3_error = None
    t4_error = None
    with tempfile.TemporaryDirectory(prefix="ocm-g7-lineage-d4-") as temp:
        root = Path(temp)
        continued = LineageStore(root / "continued", "CONTINUED_OCM")
        reset_t1 = LineageStore(root / "reset-t1", "RESET_OCM")
        reset_t2 = LineageStore(root / "reset-t2", "RESET_OCM")
        reset_t3 = LineageStore(root / "reset-t3", "RESET_OCM")
        reset_t4 = LineageStore(root / "reset-t4", "RESET_OCM")
        parent = LineageStore(root / "parent", "STRONG_ADAPTIVE_PARENT")
        task_specific_t1 = LineageStore(root / "task-specific-t1", "TASK_SPECIFIC_OCM")
        task_specific_t2 = LineageStore(root / "task-specific-t2", "TASK_SPECIFIC_OCM")
        task_specific_t3 = LineageStore(root / "task-specific-t3", "TASK_SPECIFIC_OCM")
        task_specific_t4 = LineageStore(root / "task-specific-t4", "TASK_SPECIFIC_OCM")
        t0 = run_t0(continued, parent, parts)
        t1 = run_t1(continued, reset_t1, parent, task_specific_t1, parts, t0)
        try:
            t2 = run_t2(continued, reset_t2, parent, task_specific_t2, parts, t0, t1)
        except RuntimeError as exc:
            t2_error = str(exc)
            if "D2" not in t2_error and "information-gain" not in t2_error and "probe" not in t2_error:
                raise
        if t2 is not None:
            try:
                t3 = run_t3(continued, reset_t3, parent, task_specific_t3, parts, t0, t1, t2)
            except RuntimeError as exc:
                t3_error = str(exc)
                if "D3" not in t3_error and "CUT" not in t3_error and "Hilbert" not in t3_error:
                    raise
        if t3 is not None:
            try:
                t4 = run_t4(continued, reset_t4, parent, task_specific_t4, parts, t0, t1, t2, t3)
            except RuntimeError as exc:
                t4_error = str(exc)
                if "D4" not in t4_error and "rewrite" not in t4_error and "RW_" not in t4_error:
                    raise
        final_bundle = continued.load()

    terminal = derive_terminal(t0, t1, t2, t3, t4)
    if t2 is None and t2_error:
        terminal = "CANNOT_CHECK_D2_PROBE_POLICY_NOT_EARNED"
    if t2 is not None and t3 is None and t3_error:
        terminal = "CANNOT_CHECK_D3_LEMMA_INTRODUCTION_NOT_EARNED"
    if t3 is not None and t4 is None and t4_error:
        terminal = "CANNOT_CHECK_D4_REWRITE_NOT_EARNED"
    t0_summary = {
        "id": "T0",
        "source_stage": t0["transition"]["source_stage"],
        "target_stage": t0["transition"]["target_stage"],
        "lineage_id": t0["transition"]["lineage_id"],
        "macro": list(t0["acquired"]["macro"]),
        "origin_category": ORIGIN_COMPOSITION,
        "macro_wins": t0["test"]["macro_wins"],
        "test_attempts": t0["test"]["total"],
        "primitive_attempts": t0["test"]["primitive_total"],
        "terminal": t0["transition"]["terminal"],
        "persistent_state_digest": t0["transition"]["persistent_state_digest"],
    }
    t1_summary = {
        "id": "T1",
        "source_stage": t1["transition"]["source_stage"],
        "target_stage": t1["transition"]["target_stage"],
        "lineage_id": t1["transition"]["lineage_id"],
        "reused_method_identities": t1["transition"]["reused_method_identities"],
        "origin_category": ORIGIN_APPLICABILITY,
        "continued_work_units": t1["continued_t1_work"],
        "reset_work_units": t1["reset_t1_work"],
        "task_specific_work_units": t1["task_work"],
        "parent_work_units": t1["parent_work"],
        "reset_origin_category": t1["reset_origin"],
        "failure_reduces_trap": t1["learned"]["failure_reduces_trap"],
        "retention_preserved": t1["learned"]["retention_preserved"],
        "terminal": t1["transition"]["terminal"],
        "persistent_state_digest": t1["transition"]["persistent_state_digest"],
    }
    t2_summary = None if t2 is None else {
        "id": "T2",
        "source_stage": t2["transition"]["source_stage"],
        "target_stage": t2["transition"]["target_stage"],
        "lineage_id": t2["transition"]["lineage_id"],
        "reused_method_identities": t2["transition"]["reused_method_identities"],
        "origin_category": ORIGIN_COMPOSITION,
        "policy_name": t2["policy_name"],
        "continued_work_units": t2["continued_t2_work"],
        "reset_work_units": t2["reset_t2_work"],
        "task_specific_work_units": t2["task_work"],
        "parent_work_units": t2["parent_work"],
        "reset_origin_category": t2["reset_origin"],
        "test_cost": t2["test_total"],
        "round_robin_cost": t2["rr_total"],
        "test_probes": t2["test_probes"],
        "round_robin_probes": t2["rr_probes"],
        "d0_retained": t2["d0_retained"],
        "d1_retained": t2["d1_retained"],
        "families_disjoint": t2["families_disjoint"],
        "historical_m11_relabeled": t2["historical_m11_relabeled"],
        "constitution": t2["constitution"],
        "terminal": t2["transition"]["terminal"],
        "persistent_state_digest": t2["transition"]["persistent_state_digest"],
    }
    t3_summary = None if t3 is None else {
        "id": "T3",
        "source_stage": t3["transition"]["source_stage"],
        "target_stage": t3["transition"]["target_stage"],
        "lineage_id": t3["transition"]["lineage_id"],
        "reused_method_identities": t3["transition"]["reused_method_identities"],
        "origin_category": ORIGIN_COMPOSITION,
        "lemma_id": t3["lemma_id"],
        "continued_work_units": t3["continued_t3_work"],
        "reset_work_units": t3["reset_t3_work"],
        "task_specific_work_units": t3["task_work"],
        "parent_work_units": t3["parent_work"],
        "reset_origin_category": t3["reset_origin"],
        "test_cost": t3["test_total"],
        "primitive_cost": t3["prim_total"],
        "lemma_uses": t3["test_used"],
        "d0_retained": t3["d0_retained"],
        "d1_retained": t3["d1_retained"],
        "d2_retained": t3["d2_retained"],
        "families_disjoint": t3["families_disjoint"],
        "historical_m11_relabeled": t3["historical_m11_relabeled"],
        "metamath_claimed": t3["metamath_claimed"],
        "flt_expanded": t3["flt_expanded"],
        "frozen_name": t3["frozen_name"],
        "constitution": t3["constitution"],
        "terminal": t3["transition"]["terminal"],
        "persistent_state_digest": t3["transition"]["persistent_state_digest"],
    }
    t4_summary = None if t4 is None else {
        "id": "T4",
        "source_stage": t4["transition"]["source_stage"],
        "target_stage": t4["transition"]["target_stage"],
        "lineage_id": t4["transition"]["lineage_id"],
        "reused_method_identities": t4["transition"]["reused_method_identities"],
        "origin_category": ORIGIN_COMPOSITION,
        "rule_id": t4["rule_id"],
        "continued_work_units": t4["continued_t4_work"],
        "reset_work_units": t4["reset_t4_work"],
        "task_specific_work_units": t4["task_work"],
        "parent_work_units": t4["parent_work"],
        "reset_origin_category": t4["reset_origin"],
        "test_cost": t4["test_total"],
        "primitive_cost": t4["prim_total"],
        "rewrite_uses": t4["test_used"],
        "d0_retained": t4["d0_retained"],
        "d1_retained": t4["d1_retained"],
        "d2_retained": t4["d2_retained"],
        "d3_retained": t4["d3_retained"],
        "families_disjoint": t4["families_disjoint"],
        "historical_m11_relabeled": t4["historical_m11_relabeled"],
        "metamath_claimed": t4["metamath_claimed"],
        "flt_expanded": t4["flt_expanded"],
        "frozen_name": t4["frozen_name"],
        "constitution": t4["constitution"],
        "terminal": t4["transition"]["terminal"],
        "persistent_state_digest": t4["transition"]["persistent_state_digest"],
    }
    earned = 2
    if t2 is not None:
        earned = 3
    if t3 is not None:
        earned = 4
    if t4 is not None:
        earned = 5
    result = {
        "schema": "ocm.g7.lineage-d4-result.v4",
        "terminal": terminal,
        "lineage_id": LINEAGE_ID,
        "earned_transitions": earned,
        "unrun_stages": list(UNRUN_STAGES),
        "d3_formal_mathematics_happened": t3 is not None,
        "d3_scope": "miniature Hilbert/SK CUT_* lemma introduction; not Metamath; not FLT",
        "d4_coding_happened": t4 is not None and terminal == "PHASED_COGNITIVE_DEVELOPMENT",
        "d4_scope": "exact string-rewrite RW_* replace-all PQ→QP; not Metamath; not FLT; not production src import",
        "d5_metacognition_happened": False,
        "d6_self_evolution_happened": False,
        "six_transitions_complete": False,
        "historical_m11_relabeled": False,
        "constitution": list(CONSTITUTION),
        "d2_error": t2_error,
        "d3_error": t3_error,
        "d4_error": t4_error,
        "claim_boundary": (
            "Microscope D0→D1→D2→D3→D4 on one lineage id. T4 is exact string-rewrite "
            "from a tiny coding/tool microscope, not Metamath, not FLT, and not historical "
            "M11 g0→g1→g2→g2 relabel. D5–D6 unrun. D5 metacognition did not happen. "
            "D0/D1/D2/D3 do not cheapen D4 versus task-specific; continued versus reset "
            "is the developmental comparison. Ordinary parent may tie the T4 mechanism."
        ),
        "d2_family": {
            "grammar": D2_GRAMMAR_ID,
            "d0_d1_grammar": GRAMMAR_ID,
            "train_n": D2_TRAIN_N,
            "val_n": D2_VAL_N,
            "test_n": D2_TEST_N,
            "disjoint_from_polynomial": True,
        },
        "d3_family": {
            "grammar": D3_GRAMMAR_ID,
            "d0_d1_grammar": GRAMMAR_ID,
            "d2_grammar": D2_GRAMMAR_ID,
            "train_n": D3_TRAIN_N,
            "val_n": D3_VAL_N,
            "test_n": D3_TEST_N,
            "disjoint_from_polynomial_and_diagnosis": True,
            "frozen_lemma_names_refused": sorted(D3_FROZEN_LEMMA_NAMES),
            "source_competence": "research/math-n4-subgoal-v2/",
        },
        "d4_family": {
            "grammar": D4_GRAMMAR_ID,
            "d0_d1_grammar": GRAMMAR_ID,
            "d2_grammar": D2_GRAMMAR_ID,
            "d3_grammar": D3_GRAMMAR_ID,
            "train_n": D4_TRAIN_N,
            "val_n": D4_VAL_N,
            "test_n": D4_TEST_N,
            "disjoint_from_polynomial_diagnosis_and_hilbert": True,
            "frozen_rule_names_refused": sorted(D4_FROZEN_RULE_NAMES),
            "source_competence": "exact replace-all string-rewrite microscope",
        },
        "t0": t0_summary,
        "t1": t1_summary,
        "t2": t2_summary,
        "t3": t3_summary,
        "t4": t4_summary,
        "transitions": (
            [t0["transition"], t1["transition"]]
            + ([] if t2 is None else [t2["transition"]])
            + ([] if t3 is None else [t3["transition"]])
            + ([] if t4 is None else [t4["transition"]])
        ),
        "final_stage": final_bundle["stage"],
        "persist_slots_present": [
            slot for slot in (
                "field_state", "learned_methods", "method_schemas", "imported_donors",
                "applicability_scope", "failure_counterexample_knowledge", "representations",
                "support_dependency", "acquisition_strategies", "executive_metareasoning_policy",
                "self_model", "self_change_history", "resource_history",
            )
            if slot in final_bundle
        ],
        "study_wall_seconds": time.perf_counter() - start,
    }
    if set(result["persist_slots_present"]) != {
        "field_state", "learned_methods", "method_schemas", "imported_donors",
        "applicability_scope", "failure_counterexample_knowledge", "representations",
        "support_dependency", "acquisition_strategies", "executive_metareasoning_policy",
        "self_model", "self_change_history", "resource_history",
    }:
        raise RuntimeError("earned persist slots missing from the final bundle")

    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            out.unlink()
        with out.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, sort_keys=True, indent=2)
            handle.write("\n")
    if transitions_dir is not None:
        transitions_dir.mkdir(parents=True, exist_ok=True)
        records = [("T0.json", t0["transition"]), ("T1.json", t1["transition"])]
        if t2 is not None:
            records.append(("T2.json", t2["transition"]))
        if t3 is not None:
            records.append(("T3.json", t3["transition"]))
        if t4 is not None:
            records.append(("T4.json", t4["transition"]))
        for name, record in records:
            path = transitions_dir / name
            if path.exists():
                path.unlink()
            with path.open("x", encoding="utf-8") as handle:
                json.dump(record, handle, sort_keys=True, indent=2)
                handle.write("\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "RESULT.json")
    parser.add_argument("--transitions", type=Path, default=HERE / "transitions")
    args = parser.parse_args()
    result = run(out=args.out, transitions_dir=args.transitions)
    print(json.dumps({
        "terminal": result["terminal"],
        "lineage_id": result["lineage_id"],
        "earned_transitions": result["earned_transitions"],
        "t0": {
            "stages": f"{result['t0']['source_stage']}->{result['t0']['target_stage']}",
            "macro": result["t0"]["macro"],
            "macro_wins": result["t0"]["macro_wins"],
        },
        "t1": {
            "stages": f"{result['t1']['source_stage']}->{result['t1']['target_stage']}",
            "continued": result["t1"]["continued_work_units"],
            "reset": result["t1"]["reset_work_units"],
            "failure_reduces_trap": result["t1"]["failure_reduces_trap"],
        },
        "t2": None if result["t2"] is None else {
            "stages": f"{result['t2']['source_stage']}->{result['t2']['target_stage']}",
            "continued": result["t2"]["continued_work_units"],
            "reset": result["t2"]["reset_work_units"],
            "policy": result["t2"]["policy_name"],
            "test_probes": result["t2"]["test_probes"],
            "round_robin_probes": result["t2"]["round_robin_probes"],
        },
        "t3": None if result["t3"] is None else {
            "stages": f"{result['t3']['source_stage']}->{result['t3']['target_stage']}",
            "continued": result["t3"]["continued_work_units"],
            "reset": result["t3"]["reset_work_units"],
            "lemma_id": result["t3"]["lemma_id"],
            "lemma_uses": result["t3"]["lemma_uses"],
        },
        "t4": None if result["t4"] is None else {
            "stages": f"{result['t4']['source_stage']}->{result['t4']['target_stage']}",
            "continued": result["t4"]["continued_work_units"],
            "reset": result["t4"]["reset_work_units"],
            "rule_id": result["t4"]["rule_id"],
            "rewrite_uses": result["t4"]["rewrite_uses"],
        },
        "unrun_stages": result["unrun_stages"],
        "d3_formal_mathematics_happened": result["d3_formal_mathematics_happened"],
        "d4_coding_happened": result["d4_coding_happened"],
        "d5_metacognition_happened": result["d5_metacognition_happened"],
        "d6_self_evolution_happened": result["d6_self_evolution_happened"],
        "historical_m11_relabeled": result["historical_m11_relabeled"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

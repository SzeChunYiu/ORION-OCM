"""Prospective G3 independent learned-method composition study.

Two single-macro learners receive disjoint train/validation evidence. The generic
held-out composition population is fixed independently of which macros are
selected. Composition counts only when exact search naturally uses both learned
identities and both single-method ablations are worse on the same fresh task.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
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

G2_PATH = REPO / "research" / "g2-macro-operator-v1" / "experiment.py"
G2_BLOB = "4c8cb45c182f12a5e09db873fb7625dc37dbf599"
SPEC = importlib.util.spec_from_file_location("g2_macro_parent", G2_PATH)
G2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G2)

from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

A_TRAIN_SALT = "orion-ocm-g3-a-training-v1"
B_TRAIN_SALT = "orion-ocm-g3-b-training-v1"
A_VALIDATION_SALT = "orion-ocm-g3-a-validation-v1"
B_VALIDATION_SALT = "orion-ocm-g3-b-validation-v1"
TEST_SALT = "orion-ocm-g3-composition-test-v1"
TRAIN_N = 48
VALIDATION_N = 32
TEST_N = 256
MAX_PRIMITIVE_LENGTH = 8
SCOPE = Scope.of("polynomial-independent-composition.v1")
LABEL_A = "MACRO_A"
LABEL_B = "MACRO_B"
LABEL_ORDER = (LABEL_A, LABEL_B)

# Prior outcome-exposed deterministic populations. Only salts/counts are reused.
PRIOR_LENGTH6 = (
    ("orion-ocm-g2-length6-test-v1", 64),
    ("orion-ocm-g2-utility-validation-v1", 32),
    (G2.TRAIN_SALT, G2.TRAIN_N),
)
PRIOR_LENGTH7 = (
    ("orion-ocm-g2-utility-test-v1", 64),
    (G2.VALIDATION_SALT, G2.VALIDATION_N),
)
PRIOR_LENGTH8 = (
    (G2.TEST_SALT, G2.TEST_N),
)


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def ranked_stratum(population, length: int, salt: str, n: int, exclude=()):
    excluded = set(exclude)
    pool = [
        task for _fp, (minimum, task) in population.items()
        if minimum == length and task.fingerprint not in excluded
    ]
    chosen = tuple(sorted(
        pool,
        key=lambda task: (G2.stable_rank(salt, task.fingerprint), task.fingerprint),
    )[:n])
    if len(chosen) != n:
        raise RuntimeError(f"stratum {length}/{salt} too small: {len(chosen)} < {n}")
    return chosen


def prior_exposure(population, length: int, specs):
    out = set()
    for salt, n in specs:
        out.update(task.fingerprint for task in ranked_stratum(population, length, salt, n))
    return out


def frozen_partition():
    population = G2.minimal_length_population(8)

    exposed6 = prior_exposure(population, 6, PRIOR_LENGTH6)
    a_train = ranked_stratum(population, 6, A_TRAIN_SALT, TRAIN_N, exposed6)
    b_train = ranked_stratum(
        population, 6, B_TRAIN_SALT, TRAIN_N,
        exposed6 | {task.fingerprint for task in a_train},
    )

    exposed7 = prior_exposure(population, 7, PRIOR_LENGTH7)
    a_validation = ranked_stratum(population, 7, A_VALIDATION_SALT, VALIDATION_N, exposed7)
    b_validation = ranked_stratum(
        population, 7, B_VALIDATION_SALT, VALIDATION_N,
        exposed7 | {task.fingerprint for task in a_validation},
    )

    exposed8 = prior_exposure(population, 8, PRIOR_LENGTH8)
    test = ranked_stratum(population, 8, TEST_SALT, TEST_N, exposed8)

    ids = [task.fingerprint for task in a_train + b_train + a_validation + b_validation + test]
    if len(ids) != len(set(ids)):
        raise RuntimeError("G3 partition overlap")
    return {
        "population": population,
        "exposed6": exposed6,
        "exposed7": exposed7,
        "exposed8": exposed8,
        "a_train": a_train,
        "b_train": b_train,
        "a_validation": a_validation,
        "b_validation": b_validation,
        "test": test,
    }


def expand_library_tokens(token_word, macros):
    expanded = []
    used = []
    for token in token_word:
        if token in LABEL_ORDER:
            macro = macros.get(token)
            if macro is None:
                raise ValueError(f"token {token} without admitted macro")
            expanded.extend(macro)
            if token not in used:
                used.append(token)
        else:
            if token not in G2.M.PRIMITIVES:
                raise ValueError(f"unknown token {token}")
            expanded.append(token)
    return tuple(expanded), tuple(used)


def build_library_index(macros, max_primitive_length: int = MAX_PRIMITIVE_LENGTH):
    macros = {label: tuple(value) for label, value in macros.items() if value is not None}
    tokens = tuple(label for label in LABEL_ORDER if label in macros) + G2.M.PRIMITIVES
    seen_programs = set()
    first_by_coefficients = {}
    attempts = 0
    checks = 0
    for token_depth in range(max_primitive_length + 1):
        for token_word in product(tokens, repeat=token_depth):
            program, used = expand_library_tokens(token_word, macros)
            if len(program) > max_primitive_length:
                continue
            attempts += 1
            if program in seen_programs:
                continue
            seen_programs.add(program)
            checks += 1
            coefficients = G2.M.normal_form(program)
            first_by_coefficients.setdefault(coefficients, {
                "enumeration_attempts": attempts,
                "unique_candidates_checked": checks,
                "token_word": token_word,
                "program": program,
                "macros_used": used,
            })
    return {
        "macros": macros,
        "max_primitive_length": max_primitive_length,
        "total_enumeration_attempts": attempts,
        "total_unique_candidates_checked": checks,
        "first_by_coefficients": first_by_coefficients,
    }


def solve_from_library(task, index):
    hit = index["first_by_coefficients"].get(task.coefficients)
    if hit is None:
        raise RuntimeError(f"library grammar did not solve {task.fingerprint}")
    if G2.M.normal_form(tuple(hit["program"])) != task.coefficients:
        raise RuntimeError("library exact verification failed")
    return {
        "task": task.fingerprint,
        "enumeration_attempts": hit["enumeration_attempts"],
        "unique_candidates_checked": hit["unique_candidates_checked"],
        "token_word": hit["token_word"],
        "program": hit["program"],
        "macros_used": hit["macros_used"],
        "verified": True,
    }


def evaluate_library(tasks, macros):
    index = build_library_index(macros)
    rows = [solve_from_library(task, index) for task in tasks]
    return rows, sum(r["enumeration_attempts"] for r in rows), sum(
        r["unique_candidates_checked"] for r in rows
    )


def ordinary_persist_library(path: Path, macro_a, macro_b):
    payload = {
        "macro_a": list(macro_a),
        "macro_b": list(macro_b),
        "fingerprint": content_hash({"macro_a": macro_a, "macro_b": macro_b}),
    }
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


def ordinary_load_library(path: Path):
    payload = json.loads(path.read_text())
    macro_a = tuple(payload["macro_a"])
    macro_b = tuple(payload["macro_b"])
    if content_hash({"macro_a": macro_a, "macro_b": macro_b}) != payload["fingerprint"]:
        raise RuntimeError("ordinary library identity mismatch")
    return {LABEL_A: macro_a, LABEL_B: macro_b}


def _admit_one(runtime, label, macro, training_receipt, utility_receipt):
    lower = label.lower()
    _tr, training_evidence = runtime.admit_evidence(
        training_receipt,
        Channel.PROOF,
        f"g3-{lower}-training.v1",
        scope=SCOPE,
    )
    _ur, utility_evidence = runtime.admit_evidence(
        utility_receipt,
        Channel.OBSERVATION,
        f"g3-{lower}-utility.v1",
        scope=SCOPE,
    )
    warrant = WarrantProfile.of({training_evidence, utility_evidence})
    source_payload = {
        "kind": "g3.method.support.v1",
        "label": label,
        "training": content_hash(training_receipt),
        "utility": content_hash(utility_receipt),
    }
    source_id = f"g3-support-{lower}:" + content_hash(source_payload)
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
    payload = {
        "kind": "macro.operator.g3.v1",
        "label": label,
        "macro": tuple(macro),
        "fingerprint": content_hash({"label": label, "macro": tuple(macro)}),
    }
    atom_id = f"g3-macro-{lower}:" + content_hash(payload)
    edge = Hyperedge(f"support:{atom_id}", (source_id,), (atom_id,), "SUPPORT", warrant=warrant)
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
    return atom_id, training_evidence, utility_evidence


def admit_library(root: Path, macro_a, macro_b, receipts, revoke_labels=()):
    runtime = OCMRuntime(root)
    atom_ids = {}
    training_evidence = {}
    utility_evidence = {}
    for label, macro in ((LABEL_A, macro_a), (LABEL_B, macro_b)):
        atom_id, te, ue = _admit_one(
            runtime,
            label,
            macro,
            receipts[label]["training"],
            receipts[label]["utility"],
        )
        atom_ids[label] = atom_id
        training_evidence[label] = te
        utility_evidence[label] = ue
    revoked = tuple(training_evidence[label] for label in revoke_labels)
    if revoked:
        runtime.revoke(revoked)
    runtime.persist()

    replay = OCMRuntime(root)
    loaded = {}
    for label in LABEL_ORDER:
        atom = replay.state.ks.atom_map().get(atom_ids[label])
        should_be_live = label not in set(revoke_labels)
        if should_be_live:
            if atom is None or atom.liveness(replay.state.revoked) is not Liveness.LIVE:
                raise RuntimeError(f"{label} did not survive restart")
            stored = dict(atom.meta)
            if atom.content_ref != content_hash(stored):
                raise RuntimeError(f"{label} content identity mismatch")
            macro = tuple(stored["macro"])
            expected = content_hash({"label": label, "macro": macro})
            if stored["fingerprint"] != expected:
                raise RuntimeError(f"{label} fingerprint mismatch")
            loaded[label] = macro
        else:
            if atom is not None and atom.liveness(replay.state.revoked) is Liveness.LIVE:
                raise RuntimeError(f"revoked {label} remained live")
    return loaded, atom_ids, training_evidence, utility_evidence


def rows_equal(a_rows, b_rows):
    return all(
        a["task"] == b["task"]
        and a["enumeration_attempts"] == b["enumeration_attempts"]
        and a["unique_candidates_checked"] == b["unique_candidates_checked"]
        and tuple(a["token_word"]) == tuple(b["token_word"])
        and tuple(a["program"]) == tuple(b["program"])
        and tuple(a["macros_used"]) == tuple(b["macros_used"])
        for a, b in zip(a_rows, b_rows)
    )


def composition_analysis(primitive_rows, a_rows, b_rows, full_rows):
    primitive = {r["task"]: r for r in primitive_rows}
    a_only = {r["task"]: r for r in a_rows}
    b_only = {r["task"]: r for r in b_rows}
    both_used = []
    strong = []
    for row in full_rows:
        used = set(row["macros_used"])
        if {LABEL_A, LABEL_B}.issubset(used):
            both_used.append(row["task"])
            if (
                row["enumeration_attempts"] < primitive[row["task"]]["enumeration_attempts"]
                and row["enumeration_attempts"] < a_only[row["task"]]["enumeration_attempts"]
                and row["enumeration_attempts"] < b_only[row["task"]]["enumeration_attempts"]
            ):
                strong.append({
                    "task": row["task"],
                    "full_attempts": row["enumeration_attempts"],
                    "primitive_attempts": primitive[row["task"]]["enumeration_attempts"],
                    "a_only_attempts": a_only[row["task"]]["enumeration_attempts"],
                    "b_only_attempts": b_only[row["task"]]["enumeration_attempts"],
                    "token_word": row["token_word"],
                    "program": row["program"],
                })
    return {"both_used_tasks": both_used, "strong_witnesses": strong}


def run():
    if git_blob_sha1(G2_PATH) != G2_BLOB:
        raise RuntimeError("G2 macro parent source drift")
    source_path = SRC / "ocm" / "learning" / "methods.py"
    if git_blob_sha1(source_path) != G2.METHOD_BLOB:
        raise RuntimeError("polynomial method source drift")

    start = time.perf_counter()
    parts = frozen_partition()

    a_training_rows, a_training_slots = G2.solve_training(parts["a_train"])
    b_training_rows, b_training_slots = G2.solve_training(parts["b_train"])
    a_tour = G2.tournament(a_training_rows, parts["a_validation"])
    b_tour = G2.tournament(b_training_rows, parts["b_validation"])

    pair_available = bool(a_tour["accepted"] and b_tour["accepted"])
    macro_a = tuple(a_tour["selected"]["fragment"]) if a_tour["accepted"] else None
    macro_b = tuple(b_tour["selected"]["fragment"]) if b_tour["accepted"] else None

    if not pair_available:
        terminal = "NO_INDEPENDENT_METHOD_PAIR"
        return {
            "schema": "g3.independent-composition.result.v1",
            "terminal": terminal,
            "method_composition_supported": False,
            "a_tournament": a_tour,
            "b_tournament": b_tour,
            "selected_a": list(macro_a) if macro_a else None,
            "selected_b": list(macro_b) if macro_b else None,
            "partition": _partition_receipt(parts),
            "study_wall_seconds": time.perf_counter() - start,
            "claim_boundary": "No independent method pair was selected; generic composition test remained unexecuted.",
        }
    if macro_a == macro_b:
        return {
            "schema": "g3.independent-composition.result.v1",
            "terminal": "NO_DISTINCT_METHOD_PAIR",
            "method_composition_supported": False,
            "a_tournament": a_tour,
            "b_tournament": b_tour,
            "selected_a": list(macro_a),
            "selected_b": list(macro_b),
            "partition": _partition_receipt(parts),
            "study_wall_seconds": time.perf_counter() - start,
            "claim_boundary": "Independent lanes selected the same macro; no second-best rescue was permitted.",
        }

    # The generic test was fixed independently of A/B outcomes.
    primitive_rows, primitive_total, primitive_checks = evaluate_library(parts["test"], {})
    a_rows, a_total, a_checks = evaluate_library(parts["test"], {LABEL_A: macro_a})
    b_rows, b_total, b_checks = evaluate_library(parts["test"], {LABEL_B: macro_b})
    full_rows, full_total, full_checks = evaluate_library(
        parts["test"], {LABEL_A: macro_a, LABEL_B: macro_b}
    )

    receipts = {
        LABEL_A: {
            "training": _training_receipt(LABEL_A, parts["a_train"], a_training_rows, a_tour),
            "utility": _utility_receipt(LABEL_A, parts["a_validation"], a_tour),
        },
        LABEL_B: {
            "training": _training_receipt(LABEL_B, parts["b_train"], b_training_rows, b_tour),
            "utility": _utility_receipt(LABEL_B, parts["b_validation"], b_tour),
        },
    }

    with tempfile.TemporaryDirectory(prefix="ocm-g3-compose-") as temp_dir:
        root = Path(temp_dir)
        ordinary_path = root / "ordinary-library.json"
        ordinary_persist_library(ordinary_path, macro_a, macro_b)
        ordinary_library = ordinary_load_library(ordinary_path)
        ordinary_rows, ordinary_total, ordinary_checks = evaluate_library(parts["test"], ordinary_library)

        ocm_full, atom_ids, training_evidence, utility_evidence = admit_library(
            root / "full", macro_a, macro_b, receipts, revoke_labels=()
        )
        ocm_revoke_a, _ids_a, _te_a, _ue_a = admit_library(
            root / "revoke-a", macro_a, macro_b, receipts, revoke_labels=(LABEL_A,)
        )
        ocm_revoke_b, _ids_b, _te_b, _ue_b = admit_library(
            root / "revoke-b", macro_a, macro_b, receipts, revoke_labels=(LABEL_B,)
        )
        ocm_revoke_both, _ids_both, _te_both, _ue_both = admit_library(
            root / "revoke-both", macro_a, macro_b, receipts, revoke_labels=LABEL_ORDER
        )

    ocm_full_rows, ocm_full_total, ocm_full_checks = evaluate_library(parts["test"], ocm_full)
    revoke_a_rows, revoke_a_total, revoke_a_checks = evaluate_library(parts["test"], ocm_revoke_a)
    revoke_b_rows, revoke_b_total, revoke_b_checks = evaluate_library(parts["test"], ocm_revoke_b)
    revoke_both_rows, revoke_both_total, revoke_both_checks = evaluate_library(parts["test"], ocm_revoke_both)

    parent_parity = rows_equal(ordinary_rows, ocm_full_rows) and rows_equal(full_rows, ocm_full_rows)
    local_revoke = (
        rows_equal(revoke_a_rows, b_rows)
        and rows_equal(revoke_b_rows, a_rows)
        and rows_equal(revoke_both_rows, primitive_rows)
    )
    composition = composition_analysis(primitive_rows, a_rows, b_rows, ocm_full_rows)

    if not parent_parity:
        terminal = "CANNOT_CHECK_COMPOSITION_PARENT_PARITY"
        supported = False
    elif not local_revoke:
        terminal = "CANNOT_CHECK_LOCAL_REVOCATION"
        supported = False
    elif not composition["both_used_tasks"]:
        terminal = "NO_FRESH_COMPOSITION_DEMAND"
        supported = False
    elif not composition["strong_witnesses"]:
        terminal = "NO_CAUSAL_COMPOSITION_ADVANTAGE"
        supported = False
    else:
        terminal = "METHOD_COMPOSITION_SUPPORTED_AT_SCOPE"
        supported = True

    a_candidate_validation = sum(r["aggregate_enumeration_attempts"] for r in a_tour["evaluations"])
    b_candidate_validation = sum(r["aggregate_enumeration_attempts"] for r in b_tour["evaluations"])

    return {
        "schema": "g3.independent-composition.result.v1",
        "terminal": terminal,
        "method_composition_supported": supported,
        "selected_a": list(macro_a),
        "selected_b": list(macro_b),
        "a_tournament": a_tour,
        "b_tournament": b_tour,
        "partition": _partition_receipt(parts),
        "composition": composition,
        "test": {
            "primitive_total_attempts": primitive_total,
            "a_only_total_attempts": a_total,
            "b_only_total_attempts": b_total,
            "full_total_attempts": full_total,
            "ordinary_total_attempts": ordinary_total,
            "ocm_full_total_attempts": ocm_full_total,
            "revoke_a_total_attempts": revoke_a_total,
            "revoke_b_total_attempts": revoke_b_total,
            "revoke_both_total_attempts": revoke_both_total,
            "primitive_total_unique_checks": primitive_checks,
            "a_only_total_unique_checks": a_checks,
            "b_only_total_unique_checks": b_checks,
            "full_total_unique_checks": full_checks,
            "ordinary_total_unique_checks": ordinary_checks,
            "ocm_full_total_unique_checks": ocm_full_checks,
            "revoke_a_total_unique_checks": revoke_a_checks,
            "revoke_b_total_unique_checks": revoke_b_checks,
            "revoke_both_total_unique_checks": revoke_both_checks,
            "ordinary_equals_ocm_full": parent_parity,
            "revoke_a_equals_b_only": rows_equal(revoke_a_rows, b_rows),
            "revoke_b_equals_a_only": rows_equal(revoke_b_rows, a_rows),
            "revoke_both_equals_primitive": rows_equal(revoke_both_rows, primitive_rows),
            "full_aggregate_saving_vs_primitive": primitive_total - full_total,
            "primitive_rows": primitive_rows,
            "a_only_rows": a_rows,
            "b_only_rows": b_rows,
            "full_rows": full_rows,
        },
        "accounting": {
            "a_training_slots": a_training_slots,
            "b_training_slots": b_training_slots,
            "a_primitive_validation_attempts": a_tour["baseline_aggregate_enumeration_attempts"],
            "b_primitive_validation_attempts": b_tour["baseline_aggregate_enumeration_attempts"],
            "a_all_candidate_validation_attempts": a_candidate_validation,
            "b_all_candidate_validation_attempts": b_candidate_validation,
            "test_full_attempts": full_total,
            "study_wall_seconds": time.perf_counter() - start,
        },
        "ocm": {
            "atom_ids": atom_ids,
            "training_evidence": training_evidence,
            "utility_evidence": utility_evidence,
            "fresh_restart": True,
            "local_revoke_a": True,
            "local_revoke_b": True,
            "revoke_both": True,
        },
        "claim_boundary": (
            "Bounded composition of two independently selected exact macros in one polynomial domain. "
            "The identical ordinary macro-library parent receives the same methods and search algorithm; no OCM architecture residual is claimed."
        ),
    }


def _partition_receipt(parts):
    return {
        "a_train_ids": [t.fingerprint for t in parts["a_train"]],
        "b_train_ids": [t.fingerprint for t in parts["b_train"]],
        "a_validation_ids": [t.fingerprint for t in parts["a_validation"]],
        "b_validation_ids": [t.fingerprint for t in parts["b_validation"]],
        "test_ids": [t.fingerprint for t in parts["test"]],
        "prior_exposed_length6": sorted(parts["exposed6"]),
        "prior_exposed_length7": sorted(parts["exposed7"]),
        "prior_exposed_length8": sorted(parts["exposed8"]),
        "salts": {
            "a_train": A_TRAIN_SALT,
            "b_train": B_TRAIN_SALT,
            "a_validation": A_VALIDATION_SALT,
            "b_validation": B_VALIDATION_SALT,
            "test": TEST_SALT,
        },
    }


def _training_receipt(label, tasks, training_rows, tour):
    rows = [
        {"task": task.fingerprint, "program": result.program, "slots": result.slots}
        for task, result in training_rows
    ]
    return {
        "schema": "g3.training.v1",
        "label": label,
        "task_ids": [t.fingerprint for t in tasks],
        "rows_hash": content_hash(rows),
        "candidate_order": tour["candidate_order"],
        "selected": tour["selected"]["fragment"] if tour["accepted"] else None,
    }


def _utility_receipt(label, tasks, tour):
    return {
        "schema": "g3.utility.v1",
        "label": label,
        "task_ids": [t.fingerprint for t in tasks],
        "accepted": tour["accepted"],
        "terminal": tour["terminal"],
        "baseline": tour["baseline_aggregate_enumeration_attempts"],
        "selected": tour["selected"],
        "tournament_hash": content_hash(tour),
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
        "selected_a": result.get("selected_a"),
        "selected_b": result.get("selected_b"),
        "strong_witnesses": len(result.get("composition", {}).get("strong_witnesses", [])),
    }, sort_keys=True))


if __name__ == "__main__":
    main()

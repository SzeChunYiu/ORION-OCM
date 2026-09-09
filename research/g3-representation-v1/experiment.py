"""Prospective G3.3 representation-improvement study.

Candidate representation languages are registered before any protected
partition is inspected for selection. Selection uses training construction
plus validation identity/cost only. The length-6 test stratum is untouched
until that rule freezes a representation (possibly the incumbent).
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
from itertools import product
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from fractions import Fraction

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
G2_COG = REPO / "research" / "g2-cognitive-objects-v1"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(G2_COG))

from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.learning import methods as M
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

from g2_cognitive_objects.types import (
    AcquisitionLineage,
    CheckStatus,
    CorrectnessEvidence,
    CurrentAuthorizationState,
    InformationVector,
    Liveness as G2Liveness,
    OriginCategory,
    PrimitiveAlias,
    RepresentationChangeV1,
    ResourceVector,
    ScopeState,
    UsefulnessEvidence,
    Verdict,
    emit,
    to_plain,
)

METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
REPR_SCHEMA_BLOB = "a75080c9a7e3e9a971215457c042e81c6f312e6b"
TRAIN_SALT = "orion-ocm-g3-repr-training-v1"
VALIDATION_SALT = "orion-ocm-g3-repr-validation-v1"
TEST_SALT = "orion-ocm-g3-repr-test-v1"
TRAIN_N = 48
VALIDATION_N = 32
TEST_N = 64
TRAIN_MIN_LENGTH = 4
VALIDATION_MIN_LENGTH = 5
TEST_MIN_LENGTH = 6
SHORT_FIT_MAX_LENGTH = 2
SCOPE = Scope.of("polynomial-representation.v1")
INCUMBENT_ID = "A_COEFFICIENT_TUPLE"
B_POINTS = (0, 1, 2)
PROBE_POINT = 4
B_WITNESS_PROGRAMS = (
    ("dec", "double", "double", "square"),
    ("dec", "double", "square", "square"),
)
ID_ORDER = (
    "A_COEFFICIENT_TUPLE",
    "B_EVAL_VECTOR",
    "C_DEGREE_LEADING",
    "D_MONOMIAL_SUPPORT",
)

# Registered before protected outcomes. Changing this object is a new language,
# not a salt/rescue of v1.
REGISTERED_LANGUAGE = {
    "schema": "g3.representation.language.v1",
    "incumbent_id": INCUMBENT_ID,
    "exact_identity_requirement": (
        "A candidate may be selected as a serving identity only if it is injective "
        "on the entire validation-bound grammar catalog (min-length <= 5). Sample "
        "injectivity of the 32 validation tasks is not sufficient."
    ),
    "selection_rule": (
        "Minimize (index_key_computations + validation_exact_identity_checks) among "
        "identity-safe candidates. The incumbent wins remaining ties, then id order."
    ),
    "candidates": (
        {
            "id": "A_COEFFICIENT_TUPLE",
            "kind": "exact-identity",
            "description": "Incumbent methods.normal_form coefficient tuple.",
        },
        {
            "id": "B_EVAL_VECTOR",
            "kind": "evaluation-vector",
            "points": B_POINTS,
            "description": (
                "Evaluation vector at frozen x in {0,1,2}. Injective on the complete "
                "min-length<=2 grammar; collides for some length>=3 programs with "
                "distinct full coefficients. Held-out probe is evaluate-at-x=4."
            ),
        },
        {
            "id": "C_DEGREE_LEADING",
            "kind": "misleading",
            "description": "Degree and leading coefficient only. Systematically collapses distinct tasks.",
        },
        {
            "id": "D_MONOMIAL_SUPPORT",
            "kind": "optional-bitmap",
            "description": "Nonzero monomial support bitmap (degrees 0..63). Coarser than A.",
        },
    ),
    "probe_operator": {
        "id": "EVAL_AT_HELD_OUT_POINT",
        "x": PROBE_POINT,
        "description": "Admitted operator that evaluates a polynomial at x=4.",
    },
    "b_witness_programs": B_WITNESS_PROGRAMS,
}


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def language_fingerprint() -> str:
    return content_hash(REGISTERED_LANGUAGE)


def stable_rank(salt: str, fingerprint: str) -> str:
    return hashlib.sha256((salt + "\0" + fingerprint).encode()).hexdigest()


def jsonable(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, tuple):
        return [jsonable(item) for item in value]
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    return value


def key_A(coefficients):
    return tuple(coefficients)


def key_B(coefficients):
    return tuple(M.evaluate_polynomial(coefficients, x) for x in B_POINTS)


def key_C(coefficients):
    coeffs = tuple(coefficients)
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs = coeffs[:-1]
    return (len(coeffs) - 1, coeffs[-1])


def key_D(coefficients):
    bits = 0
    for i, coefficient in enumerate(coefficients):
        if coefficient != 0 and i < 64:
            bits |= 1 << i
    return (bits,)


KEY_FNS = {
    "A_COEFFICIENT_TUPLE": key_A,
    "B_EVAL_VECTOR": key_B,
    "C_DEGREE_LEADING": key_C,
    "D_MONOMIAL_SUPPORT": key_D,
}


def encode_key(key):
    return tuple(str(item) for item in key)


def coefficients_of(program):
    return M.normal_form(program)


def program_fingerprint(coefficients):
    return M.PolynomialTask("identity", coefficients).fingerprint


def minimal_length_population(max_length: int = TEST_MIN_LENGTH):
    best = {}
    for length in range(max_length + 1):
        for program in product(M.PRIMITIVES, repeat=length):
            coefficients = M.normal_form(program)
            task = M.PolynomialTask(f"length-{length}", coefficients)
            best.setdefault(task.fingerprint, (length, task, program))
    return best


def take_stratum(population, length: int, salt: str, n: int):
    pool = [task for _fp, (minimum, task, _program) in population.items() if minimum == length]
    chosen = tuple(sorted(
        pool,
        key=lambda task: (stable_rank(salt, task.fingerprint), task.fingerprint),
    )[:n])
    if len(chosen) != n:
        raise RuntimeError(f"minimum-length-{length} population too small: {len(chosen)} < {n}")
    return chosen


def frozen_partition():
    population = minimal_length_population(TEST_MIN_LENGTH)
    training = take_stratum(population, TRAIN_MIN_LENGTH, TRAIN_SALT, TRAIN_N)
    validation = take_stratum(population, VALIDATION_MIN_LENGTH, VALIDATION_SALT, VALIDATION_N)
    test = take_stratum(population, TEST_MIN_LENGTH, TEST_SALT, TEST_N)
    ids = [task.fingerprint for task in training + validation + test]
    if len(ids) != len(set(ids)):
        raise RuntimeError("train/validation/test overlap")
    return population, training, validation, test


def grammar_catalog(max_length: int):
    """Parent enumeration: every program, first program per coefficient identity."""
    programs = []
    identities = {}
    attempts = 0
    unique_checked = 0
    seen_programs = set()
    for length in range(max_length + 1):
        for program in product(M.PRIMITIVES, repeat=length):
            attempts += 1
            if program in seen_programs:
                continue
            seen_programs.add(program)
            unique_checked += 1
            coefficients = M.normal_form(program)
            row = {
                "program": program,
                "coefficients": coefficients,
                "fingerprint": program_fingerprint(coefficients),
                "enumeration_attempts": attempts,
                "unique_candidates_checked": unique_checked,
            }
            programs.append(row)
            identities.setdefault(coefficients, row)
    return {
        "max_length": max_length,
        "programs": tuple(programs),
        "identities": identities,
        "total_enumeration_attempts": attempts,
        "total_unique_candidates_checked": unique_checked,
    }


def build_repr_index(identities, key_fn):
    classes = {}
    for coefficients, row in identities.items():
        key = key_fn(coefficients)
        classes.setdefault(key, []).append(row)
    class_sizes = [len(members) for members in classes.values()]
    colliding = {key: members for key, members in classes.items() if len(members) > 1}
    return {
        "classes": classes,
        "index_size": len(classes),
        "identity_count": len(identities),
        "collision_keys": len(colliding),
        "collision_identities": sum(len(members) for members in colliding.values()),
        "max_class_size": max(class_sizes) if class_sizes else 0,
        "key_computations": len(identities),
        "injective": not colliding,
    }


def induced_index(tasks, key_fn):
    classes = defaultdict(list)
    for task in tasks:
        classes[key_fn(task.coefficients)].append(task.fingerprint)
    colliding = {key: fps for key, fps in classes.items() if len(set(fps)) > 1}
    return {
        "index_size": len(classes),
        "identity_count": len(tasks),
        "collision_keys": len(colliding),
        "injective": not colliding,
    }


def lookup_task(task, index, key_fn):
    key = key_fn(task.coefficients)
    bucket = index["classes"].get(key, [])
    exact = 0
    for member in bucket:
        exact += 1
        if member["coefficients"] == task.coefficients:
            if M.normal_form(member["program"]) != task.coefficients:
                raise RuntimeError("representation index exact verification failed")
            return {
                "task": task.fingerprint,
                "found": True,
                "enumeration_attempts": member["enumeration_attempts"],
                "unique_candidates_checked": member["unique_candidates_checked"],
                "exact_identity_checks": exact,
                "class_size": len(bucket),
                "program": member["program"],
                "verified": True,
            }
    return {
        "task": task.fingerprint,
        "found": False,
        "enumeration_attempts": None,
        "unique_candidates_checked": None,
        "exact_identity_checks": exact,
        "class_size": len(bucket),
        "program": None,
        "verified": False,
    }


def evaluate_index(tasks, index, key_fn):
    rows = [lookup_task(task, index, key_fn) for task in tasks]
    if not all(row["found"] and row["verified"] for row in rows):
        missing = [row["task"] for row in rows if not row["found"]]
        raise RuntimeError(f"representation index failed to solve {missing[:4]}")
    return (
        rows,
        sum(row["enumeration_attempts"] for row in rows),
        sum(row["unique_candidates_checked"] for row in rows),
        sum(row["exact_identity_checks"] for row in rows),
    )


def protected_collisions_on_tasks(index, tasks, key_fn):
    """Collisions against the serving grammar, not only among the sample."""
    hits = 0
    witnesses = []
    for task in tasks:
        key = key_fn(task.coefficients)
        bucket = index["classes"].get(key, [])
        foreign = [row for row in bucket if row["coefficients"] != task.coefficients]
        if foreign:
            hits += 1
            if len(witnesses) < 4:
                witnesses.append({
                    "task": task.fingerprint,
                    "class_size": len(bucket),
                    "foreign_program": foreign[0]["program"],
                    "foreign_fingerprint": foreign[0]["fingerprint"],
                })
    return hits, witnesses


def candidate_report(repr_id, catalog, train_tasks, val_tasks):
    key_fn = KEY_FNS[repr_id]
    grammar_index = build_repr_index(catalog["identities"], key_fn)
    train_induced = induced_index(train_tasks, key_fn)
    val_induced = induced_index(val_tasks, key_fn)
    val_protected, val_witnesses = protected_collisions_on_tasks(grammar_index, val_tasks, key_fn)
    val_rows, val_attempts, val_unique, val_exact = evaluate_index(val_tasks, grammar_index, key_fn)
    selection_cost = grammar_index["key_computations"] + val_exact
    identity_safe = grammar_index["injective"]
    return {
        "id": repr_id,
        "grammar_index_size": grammar_index["index_size"],
        "grammar_identities": grammar_index["identity_count"],
        "grammar_collision_keys": grammar_index["collision_keys"],
        "grammar_collision_identities": grammar_index["collision_identities"],
        "grammar_max_class_size": grammar_index["max_class_size"],
        "grammar_injective": grammar_index["injective"],
        "train_induced": train_induced,
        "val_induced": val_induced,
        "val_protected_collisions": val_protected,
        "val_collision_witnesses": val_witnesses,
        "val_enumeration_attempts": val_attempts,
        "val_unique_candidates_checked": val_unique,
        "val_exact_identity_checks": val_exact,
        "index_key_computations": grammar_index["key_computations"],
        "selection_cost": selection_cost,
        "identity_safe": identity_safe,
        "index": grammar_index,
        "val_rows": val_rows,
    }


def select_representation(reports):
    """Frozen rule: identity-safe on the validation grammar, then min cost, incumbent ties."""
    eligible = [report for report in reports if report["identity_safe"]]
    if not eligible:
        return None, ()
    ordered = tuple(report["id"] for report in reports)
    selected = min(
        eligible,
        key=lambda report: (
            report["selection_cost"],
            0 if report["id"] == INCUMBENT_ID else 1,
            ordered.index(report["id"]),
        ),
    )
    return selected, tuple(report["id"] for report in eligible)


def program_key_A(program):
    return M.normal_form(program)


def program_key_B(program):
    return tuple(M.execute(program, x) for x in B_POINTS)


def program_key_C(program):
    degree = 1
    leading = Fraction(1)
    for op in program:
        if op == "double":
            leading *= 2
        elif op == "square":
            leading *= leading
            degree *= 2
    return (degree, leading)


def program_key_D(program):
    return key_D(M.normal_form(program))


PROGRAM_KEY_FNS = {
    "A_COEFFICIENT_TUPLE": program_key_A,
    "B_EVAL_VECTOR": program_key_B,
    "C_DEGREE_LEADING": program_key_C,
    "D_MONOMIAL_SUPPORT": program_key_D,
}


def sequential_filter_solve(task, catalog, repr_id):
    """Walk programs; cheap key may reject. Exact identity is always normal_form.

    For the incumbent, the key *is* normal_form, so every unique program until
    the hit pays one exact check. Collisions do not disqualify a filter.
    """
    target_key = KEY_FNS[repr_id](task.coefficients)
    key_from_program = PROGRAM_KEY_FNS[repr_id]
    incumbent = repr_id == INCUMBENT_ID
    filter_evals = 0
    exact = 0
    for row in catalog["programs"]:
        filter_evals += 1
        key = key_from_program(row["program"])
        if incumbent:
            exact += 1
            if key == target_key:
                if key != task.coefficients:
                    raise RuntimeError("incumbent sequential identity mismatch")
                return {
                    "task": task.fingerprint,
                    "found": True,
                    "enumeration_attempts": row["enumeration_attempts"],
                    "filter_evals": filter_evals,
                    "exact_identity_checks": exact,
                    "program": row["program"],
                    "verified": True,
                }
            continue
        if key != target_key:
            continue
        exact += 1
        coefficients = M.normal_form(row["program"])
        if coefficients == task.coefficients:
            return {
                "task": task.fingerprint,
                "found": True,
                "enumeration_attempts": row["enumeration_attempts"],
                "filter_evals": filter_evals,
                "exact_identity_checks": exact,
                "program": row["program"],
                "verified": True,
            }
    raise RuntimeError(f"sequential filter failed to solve {task.fingerprint}")


def evaluate_sequential(tasks, catalog, repr_id):
    rows = [sequential_filter_solve(task, catalog, repr_id) for task in tasks]
    return (
        rows,
        sum(row["enumeration_attempts"] for row in rows),
        sum(row["filter_evals"] for row in rows),
        sum(row["exact_identity_checks"] for row in rows),
    )


def b_witness_pair():
    left, right = B_WITNESS_PROGRAMS
    left_c = coefficients_of(left)
    right_c = coefficients_of(right)
    return {
        "left_program": left,
        "right_program": right,
        "left_coefficients": [str(c) for c in left_c],
        "right_coefficients": [str(c) for c in right_c],
        "same_A": key_A(left_c) == key_A(right_c),
        "same_B": key_B(left_c) == key_B(right_c),
        "same_C": key_C(left_c) == key_C(right_c),
        "left_probe": str(M.evaluate_polynomial(left_c, PROBE_POINT)),
        "right_probe": str(M.evaluate_polynomial(right_c, PROBE_POINT)),
        "probe_distinguishes": M.evaluate_polynomial(left_c, PROBE_POINT) != M.evaluate_polynomial(right_c, PROBE_POINT),
    }


def short_grammar_injective(key_fn, max_length=SHORT_FIT_MAX_LENGTH):
    catalog = grammar_catalog(max_length)
    index = build_repr_index(catalog["identities"], key_fn)
    return index["injective"], index["collision_keys"], len(catalog["identities"])


def distinguishing_operator_invalidation():
    """Lifecycle: a new probe splits a B-class; current B-answers may still agree."""
    witness = b_witness_pair()
    if witness["same_A"] or not witness["same_B"]:
        raise RuntimeError("registered B witness pair is not a B-only collision")
    if not witness["probe_distinguishes"]:
        raise RuntimeError("registered probe does not split the B witness pair")
    current_answer_still_equivalent = witness["same_B"]
    identified_after_probe = False
    b_invalidated = True
    reopened = True
    return {
        "witness": witness,
        "current_answer_equivalent_under_B": current_answer_still_equivalent,
        "probe_operator": REGISTERED_LANGUAGE["probe_operator"],
        "probe_distinguishes": True,
        "identified_after_probe": identified_after_probe,
        "representation_invalidated": b_invalidated,
        "representation_reopened": reopened,
        "lifecycle_equivalence": "MEASURED",
        "note": (
            "Current-answer equality under B (same evals at {0,1,2}) is preserved as a "
            "historical observation. Lifecycle identification is withdrawn because the "
            "admitted probe evaluate-at-4 distinguishes the states."
        ),
    }


def ordinary_persist(path: Path, representation_id: str):
    payload = {
        "representation_id": representation_id,
        "fingerprint": content_hash({"representation_id": representation_id}),
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


def ordinary_load(path: Path):
    payload = json.loads(path.read_text())
    representation_id = payload["representation_id"]
    if content_hash({"representation_id": representation_id}) != payload["fingerprint"]:
        raise RuntimeError("ordinary representation persistence identity mismatch")
    return representation_id


def admit_representation(root: Path, representation_id: str, training_receipt, utility_receipt, revoke=False):
    runtime = OCMRuntime(root)
    _tr, training_evidence = runtime.admit_evidence(
        training_receipt,
        Channel.PROOF,
        "g3-repr-training.v1",
        scope=SCOPE,
    )
    _ur, utility_evidence = runtime.admit_evidence(
        utility_receipt,
        Channel.OBSERVATION,
        "g3-repr-utility.v1",
        scope=SCOPE,
    )
    warrant = WarrantProfile.of({training_evidence, utility_evidence})
    source_payload = {
        "kind": "g3.representation.support.v1",
        "training": content_hash(training_receipt),
        "utility": content_hash(utility_receipt),
    }
    source_id = "g3-repr-support:" + content_hash(source_payload)
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
        "kind": "representation.g3.v1",
        "representation_id": representation_id,
        "language": language_fingerprint(),
        "fingerprint": content_hash({"representation_id": representation_id, "language": language_fingerprint()}),
    }
    atom_id = "representation-change:" + content_hash(payload)
    edge = Hyperedge("support:" + atom_id, (source_id,), (atom_id,), "SUPPORT", warrant=warrant)
    runtime.admit_object(
        Atom(
            atom_id,
            "representation",
            warrant,
            scope=SCOPE,
            content_ref=content_hash(payload),
            meta=tuple(payload.items()),
        ),
        (edge,),
        "OBSERVATION",
    )
    probe_payload = {
        "kind": "g3.probe.operator.v1",
        "operator": REGISTERED_LANGUAGE["probe_operator"],
    }
    probe_id = "g3-probe:" + content_hash(probe_payload)
    probe_edge = Hyperedge("support:" + probe_id, (source_id,), (probe_id,), "SUPPORT", warrant=warrant)
    runtime.admit_object(
        Atom(
            probe_id,
            "procedure",
            warrant,
            scope=SCOPE,
            content_ref=content_hash(probe_payload),
            meta=(("kind", probe_payload["kind"]), ("x", PROBE_POINT)),
        ),
        (probe_edge,),
        "OBSERVATION",
    )
    if revoke:
        runtime.revoke((training_evidence,))
    runtime.persist()

    replay = OCMRuntime(root)
    atom = replay.state.ks.atom_map().get(atom_id)
    probe = replay.state.ks.atom_map().get(probe_id)
    if revoke:
        if atom is not None and atom.liveness(replay.state.revoked) is Liveness.LIVE:
            raise RuntimeError("revoked representation remained live")
        return None, atom_id, training_evidence, utility_evidence, probe_id
    if atom is None or atom.liveness(replay.state.revoked) is not Liveness.LIVE:
        raise RuntimeError("representation did not survive restart")
    if probe is None or probe.liveness(replay.state.revoked) is not Liveness.LIVE:
        raise RuntimeError("probe operator did not survive restart")
    stored = dict(atom.meta)
    if atom.content_ref != content_hash(stored):
        raise RuntimeError("representation content identity mismatch")
    loaded = stored["representation_id"]
    expected = content_hash({"representation_id": loaded, "language": language_fingerprint()})
    if stored["fingerprint"] != expected:
        raise RuntimeError("representation fingerprint mismatch")
    return loaded, atom_id, training_evidence, utility_evidence, probe_id


def rows_equal(a_rows, b_rows):
    return all(
        a["task"] == b["task"]
        and a["enumeration_attempts"] == b["enumeration_attempts"]
        and a["unique_candidates_checked"] == b["unique_candidates_checked"]
        and a["exact_identity_checks"] == b["exact_identity_checks"]
        and tuple(a["program"]) == tuple(b["program"])
        for a, b in zip(a_rows, b_rows)
    )


def emit_representation_change(selected_id, terminal, test_summary, invalidation, lineage_resources):
    useful = terminal == "REPRESENTATION_CHANGE_CAUSALLY_USEFUL"
    selected_is_new = selected_id != INCUMBENT_ID
    usefulness = UsefulnessEvidence(
        fresh_task_id=test_summary["first_test_id"],
        effect_coordinate="exact_identity_checks",
        effect_observed=True if useful else False,
        invocation_witness_id=test_summary["invocation_witness_id"] if selected_is_new or useful else "UNKNOWN",
        ablation_witness_id=test_summary["ablation_witness_id"],
        restart_witness_id=test_summary["restart_witness_id"],
        independent_of_correctness=True,
        status=CheckStatus.MEASURED,
        cannot_check_reason=None,
    )
    change = RepresentationChangeV1(
        change_id="g3.representation.v1." + content_hash({
            "language": language_fingerprint(),
            "selected": selected_id,
            "terminal": terminal,
        })[:16],
        before_representation_id=INCUMBENT_ID,
        after_representation_id=selected_id,
        trigger="validation identity-safe cost tournament on frozen g3.representation.language.v1",
        primitive_alias=(
            PrimitiveAlias.NO_NEW_ABSTRACTION
            if selected_id == INCUMBENT_ID
            else PrimitiveAlias.NOT_ASSESSED
        ),
        lifecycle_equivalence=CheckStatus.MEASURED,
        acquisition_lineage=AcquisitionLineage(
            origin_category=OriginCategory.LEARNED_APPLICABILITY,
            episode_ids=("g3.representation.v1.selection",),
            donor_ids=(),
            prior_information_ids=(language_fingerprint(),),
            source_sha256=METHOD_BLOB,
            training_task_ids=tuple(test_summary["training_ids"][:8]),
            information=InformationVector(examples=TRAIN_N, labels=TRAIN_N),
            resources=lineage_resources,
            discovery_evidence_id=test_summary["discovery_evidence_id"],
            status=CheckStatus.MEASURED,
        ),
        correctness=CorrectnessEvidence(
            checker_id=M.CHECKER,
            proof_evidence_id=test_summary["correctness_evidence_id"],
            certificate_sha256=METHOD_BLOB,
            verdict=Verdict.PASS,
            counterexample=None,
            independent_of_usefulness=True,
            status=CheckStatus.MEASURED,
        ),
        usefulness=usefulness,
        authorization=CurrentAuthorizationState(
            admitted=True,
            proof_liveness=G2Liveness.LIVE,
            applicability_liveness=G2Liveness.LIVE,
            serving_liveness=G2Liveness.LIVE,
            revoked_support_ids=(),
            warrant_ids=(test_summary["training_evidence_id"], test_summary["utility_evidence_id"]),
            scope=ScopeState(contexts=("polynomial-representation.v1",), epoch_start=0.0, epoch_end=None),
            authority_ranks=(),
            status=CheckStatus.MEASURED,
        ),
        notes=(
            f"terminal={terminal}",
            f"B current-answer equivalent={invalidation['current_answer_equivalent_under_B']}",
            f"B invalidated by probe={invalidation['representation_invalidated']}",
            "lifecycle equivalence is not current-answer equality under a frozen point set",
        ),
    )
    return json.loads(emit(change).decode())


def summarize_report(report):
    return {
        "id": report["id"],
        "grammar_index_size": report["grammar_index_size"],
        "grammar_identities": report["grammar_identities"],
        "grammar_collision_keys": report["grammar_collision_keys"],
        "grammar_collision_identities": report["grammar_collision_identities"],
        "grammar_max_class_size": report["grammar_max_class_size"],
        "grammar_injective": report["grammar_injective"],
        "train_induced": report["train_induced"],
        "val_induced": report["val_induced"],
        "val_protected_collisions": report["val_protected_collisions"],
        "val_collision_witnesses": jsonable(report["val_collision_witnesses"]),
        "val_enumeration_attempts": report["val_enumeration_attempts"],
        "val_unique_candidates_checked": report["val_unique_candidates_checked"],
        "val_exact_identity_checks": report["val_exact_identity_checks"],
        "index_key_computations": report["index_key_computations"],
        "selection_cost": report["selection_cost"],
        "identity_safe": report["identity_safe"],
    }


def run_filter_successor(val_catalog, test_catalog, validation_tasks, test_tasks, incumbent_test_exact):
    """v2: different selection mechanism. Filter, then exact identity. Collisions do not disqualify."""
    val_costs = []
    for repr_id in ID_ORDER:
        _rows, _attempts, filter_evals, exact = evaluate_sequential(
            validation_tasks, val_catalog, repr_id
        )
        val_costs.append({
            "id": repr_id,
            "val_filter_evals": filter_evals,
            "val_exact_identity_checks": exact,
            "selection_cost": exact,
        })
    selected = min(
        val_costs,
        key=lambda row: (
            row["selection_cost"],
            0 if row["id"] == INCUMBENT_ID else 1,
            ID_ORDER.index(row["id"]),
        ),
    )
    selected_id = selected["id"]
    _s_rows, s_attempts, s_filters, s_exact = evaluate_sequential(
        test_tasks, test_catalog, selected_id
    )
    _a_rows, a_attempts, a_filters, a_exact = evaluate_sequential(
        test_tasks, test_catalog, INCUMBENT_ID
    )
    if selected_id == INCUMBENT_ID:
        terminal = "REPRESENTATION_PRIOR_DOMINATES"
        useful = False
    elif s_exact < a_exact:
        terminal = "REPRESENTATION_CHANGE_CAUSALLY_USEFUL"
        useful = True
    else:
        terminal = "REPRESENTATION_CHANNEL_INSUFFICIENT"
        useful = False
    return {
        "schema": "g3.representation.filter-successor.v2",
        "selection_mechanism": "sequential-filter-then-exact-identity",
        "terminal": terminal,
        "representation_change_causally_useful": useful,
        "selected_id": selected_id,
        "validation": val_costs,
        "test": {
            "selected_enumeration_attempts": s_attempts,
            "selected_filter_evals": s_filters,
            "selected_exact_identity_checks": s_exact,
            "incumbent_enumeration_attempts": a_attempts,
            "incumbent_filter_evals": a_filters,
            "incumbent_exact_identity_checks": a_exact,
            "exact_check_saving_vs_A": a_exact - s_exact,
            "v1_incumbent_index_exact_checks": incumbent_test_exact,
        },
        "claim_boundary": (
            "Successor mechanism only. Exact identity remains the checker; the representation "
            "is a filter. v2 does not overwrite the v1 identity-index terminal."
        ),
    }


def decide_v1_terminal(selected_id, eligible_ids, ordinary_equal_ocm, revoke_equals_A,
                      invalidation, a_exact, selected_exact, selected_protected_collisions):
    if not ordinary_equal_ocm:
        return "CANNOT_CHECK_REPRESENTATION_PARENT_PARITY", False
    if not revoke_equals_A:
        return "CANNOT_CHECK_REVOCATION_ABLATION", False
    if not invalidation["representation_invalidated"] or invalidation["identified_after_probe"]:
        return "CANNOT_CHECK_DISTINGUISHING_OPERATOR_INVALIDATION", False
    if invalidation["lifecycle_equivalence"] != "MEASURED":
        return "CANNOT_CHECK_LIFECYCLE_EQUIVALENCE", False
    if selected_id == INCUMBENT_ID:
        if set(eligible_ids) - {INCUMBENT_ID}:
            return "REPRESENTATION_PRIOR_DOMINATES", False
        return "PARENT_SUFFICIENT", False
    if selected_protected_collisions > 0:
        return "REPRESENTATION_CHANNEL_INSUFFICIENT", False
    if selected_exact >= a_exact:
        return "REPRESENTATION_CHANNEL_INSUFFICIENT", False
    return "REPRESENTATION_CHANGE_CAUSALLY_USEFUL", True


def run():
    source_path = SRC / "ocm" / "learning" / "methods.py"
    observed_blob = git_blob_sha1(source_path)
    if observed_blob != METHOD_BLOB:
        raise RuntimeError(f"method source drift: {observed_blob}")
    schema_path = G2_COG / "schemas" / "representation_change_v1.json"
    if git_blob_sha1(schema_path) != REPR_SCHEMA_BLOB:
        raise RuntimeError("RepresentationChangeV1 schema drift")

    run_start = time.perf_counter()
    language_hash = language_fingerprint()
    invalidation = distinguishing_operator_invalidation()
    b_short_ok, b_short_collisions, b_short_n = short_grammar_injective(key_B)
    c_short_ok, c_short_collisions, _n = short_grammar_injective(key_C)
    d_short_ok, d_short_collisions, _n = short_grammar_injective(key_D)
    a_short_ok, a_short_collisions, _n = short_grammar_injective(key_A)

    population, training_tasks, validation_tasks, test_tasks = frozen_partition()
    discovery_start = time.perf_counter()
    val_catalog = grammar_catalog(VALIDATION_MIN_LENGTH)
    test_catalog = grammar_catalog(TEST_MIN_LENGTH)
    reports = [
        candidate_report(repr_id, val_catalog, training_tasks, validation_tasks)
        for repr_id in ID_ORDER
    ]
    discovery_wall = time.perf_counter() - discovery_start
    discovery_key_computations = sum(report["index_key_computations"] for report in reports)
    discovery_val_exact = sum(report["val_exact_identity_checks"] for report in reports)
    selected, eligible_ids = select_representation(reports)
    if selected is None:
        raise RuntimeError("incumbent coefficient representation was not identity-safe")
    selected_id = selected["id"]

    a_report = next(report for report in reports if report["id"] == INCUMBENT_ID)
    a_test_index = build_repr_index(test_catalog["identities"], key_A)
    selected_test_index = build_repr_index(test_catalog["identities"], KEY_FNS[selected_id])
    a_rows, a_attempts, a_unique, a_exact = evaluate_index(test_tasks, a_test_index, key_A)
    selected_rows, s_attempts, s_unique, s_exact = evaluate_index(
        test_tasks, selected_test_index, KEY_FNS[selected_id]
    )
    selected_protected, selected_test_witnesses = protected_collisions_on_tasks(
        selected_test_index, test_tasks, KEY_FNS[selected_id]
    )
    b_test_index = build_repr_index(test_catalog["identities"], key_B)
    b_train_induced = induced_index(training_tasks, key_B)
    b_test_induced = induced_index(test_tasks, key_B)
    b_test_protected, b_test_witnesses = protected_collisions_on_tasks(
        b_test_index, test_tasks, key_B
    )

    training_receipt = {
        "schema": "g3.representation.training.v1",
        "source_blob": METHOD_BLOB,
        "language": language_hash,
        "training_ids": [task.fingerprint for task in training_tasks],
        "candidate_order": list(ID_ORDER),
        "selected": selected_id,
    }
    utility_receipt = {
        "schema": "g3.representation.utility.v1",
        "language": language_hash,
        "validation_ids": [task.fingerprint for task in validation_tasks],
        "eligible": list(eligible_ids),
        "selected": selected_id,
        "selection_cost": selected["selection_cost"],
        "identity_safe": selected["identity_safe"],
    }

    with tempfile.TemporaryDirectory(prefix="ocm-g3-repr-") as temp_dir:
        root = Path(temp_dir)
        ordinary_path = root / "ordinary-representation.json"
        ordinary_persist(ordinary_path, selected_id)
        ordinary_id = ordinary_load(ordinary_path)
        ocm_id, ocm_atom_id, training_evidence, utility_evidence, probe_id = admit_representation(
            root / "ocm-live", selected_id, training_receipt, utility_receipt, revoke=False
        )
        revoked_id, _revoked_atom, _rte, _rue, _rp = admit_representation(
            root / "ocm-revoked", selected_id, training_receipt, utility_receipt, revoke=True
        )

    ordinary_index = build_repr_index(test_catalog["identities"], KEY_FNS[ordinary_id])
    ordinary_rows, ordinary_attempts, ordinary_unique, ordinary_exact = evaluate_index(
        test_tasks, ordinary_index, KEY_FNS[ordinary_id]
    )
    ocm_index = build_repr_index(test_catalog["identities"], KEY_FNS[ocm_id])
    ocm_rows, ocm_attempts, ocm_unique, ocm_exact = evaluate_index(
        test_tasks, ocm_index, KEY_FNS[ocm_id]
    )
    fallback_id = revoked_id if revoked_id is not None else INCUMBENT_ID
    revoked_index = build_repr_index(test_catalog["identities"], KEY_FNS[fallback_id])
    revoked_rows, revoked_attempts, revoked_unique, revoked_exact = evaluate_index(
        test_tasks, revoked_index, KEY_FNS[fallback_id]
    )

    ordinary_equal_ocm = (
        ordinary_id == ocm_id == selected_id
        and rows_equal(selected_rows, ordinary_rows)
        and rows_equal(ordinary_rows, ocm_rows)
    )
    revoke_equals_A = fallback_id == INCUMBENT_ID and rows_equal(revoked_rows, a_rows)

    terminal, useful = decide_v1_terminal(
        selected_id,
        eligible_ids,
        ordinary_equal_ocm,
        revoke_equals_A,
        invalidation,
        a_exact,
        s_exact,
        selected_protected,
    )

    successor = run_filter_successor(
        val_catalog, test_catalog, validation_tasks, test_tasks, a_exact
    )

    test_summary = {
        "first_test_id": test_tasks[0].fingerprint,
        "training_ids": [task.fingerprint for task in training_tasks],
        "invocation_witness_id": content_hash({
            "selected": selected_id,
            "test_attempts": s_attempts,
            "test_exact": s_exact,
        }),
        "ablation_witness_id": content_hash({
            "revoked_equals_A": revoke_equals_A,
            "revoked_exact": revoked_exact,
        }),
        "restart_witness_id": ocm_atom_id,
        "discovery_evidence_id": content_hash({
            "language": language_hash,
            "key_computations": discovery_key_computations,
        }),
        "correctness_evidence_id": content_hash({
            "checker": M.CHECKER,
            "verified": True,
            "n": len(test_tasks),
        }),
        "training_evidence_id": training_evidence,
        "utility_evidence_id": utility_evidence,
    }
    change_record = emit_representation_change(
        selected_id,
        terminal,
        test_summary,
        invalidation,
        ResourceVector(
            wall_seconds=discovery_wall,
            work_units=discovery_key_computations + discovery_val_exact,
            preprocessing_work_units=discovery_key_computations,
            verifier_calls=discovery_val_exact,
            index_write_entries=sum(report["grammar_index_size"] for report in reports),
            notes=("representation discovery over A,B,C,D on the validation-bound catalog",),
        ),
    )

    claim_boundary = (
        "Bounded polynomial representation selection under a registered exact-identity "
        "requirement. Coarser keys are not licensed by sample non-collision. The identical "
        "ordinary representation parent receives the same selected language; no OCM "
        "architecture residual is claimed. v1 does not use sequential-filter savings."
    )
    if terminal in {"PARENT_SUFFICIENT", "REPRESENTATION_PRIOR_DOMINATES"}:
        root_cause = (
            "Only the incumbent coefficient tuple is injective on the min-length<=5 serving "
            "grammar. B (eval at {0,1,2}) already collides among length-4 programs, including "
            "the registered witness pair; C and D collapse many distinct identities. The frozen "
            "rule therefore keeps A. That is a valid parent/prior result, not a salt failure."
        )
    elif terminal == "REPRESENTATION_CHANGE_CAUSALLY_USEFUL":
        root_cause = None
    else:
        root_cause = terminal

    return {
        "schema": "g3.representation.result.v1",
        "terminal": terminal,
        "representation_change_causally_useful": useful,
        "method_blob": METHOD_BLOB,
        "representation_schema_blob": REPR_SCHEMA_BLOB,
        "language_fingerprint": language_hash,
        "registered_language": jsonable(REGISTERED_LANGUAGE),
        "selected_id": selected_id,
        "eligible_ids": list(eligible_ids),
        "partition": {
            "training_n": TRAIN_N,
            "validation_n": VALIDATION_N,
            "test_n": TEST_N,
            "training_min_length": TRAIN_MIN_LENGTH,
            "validation_min_length": VALIDATION_MIN_LENGTH,
            "test_min_length": TEST_MIN_LENGTH,
            "training_salt": TRAIN_SALT,
            "validation_salt": VALIDATION_SALT,
            "test_salt": TEST_SALT,
            "training_ids": [task.fingerprint for task in training_tasks],
            "validation_ids": [task.fingerprint for task in validation_tasks],
            "test_ids": [task.fingerprint for task in test_tasks],
            "population_counts": {
                str(length): sum(1 for minimum, _task, _p in population.values() if minimum == length)
                for length in range(TEST_MIN_LENGTH + 1)
            },
        },
        "language_properties": {
            "A_injective_on_minlen_le_2": a_short_ok,
            "A_collisions_on_minlen_le_2": a_short_collisions,
            "B_injective_on_minlen_le_2": b_short_ok,
            "B_collisions_on_minlen_le_2": b_short_collisions,
            "C_injective_on_minlen_le_2": c_short_ok,
            "C_collisions_on_minlen_le_2": c_short_collisions,
            "D_injective_on_minlen_le_2": d_short_ok,
            "D_collisions_on_minlen_le_2": d_short_collisions,
            "short_fit_identities": b_short_n,
            "B_fits_short_training_grammar": b_short_ok and a_short_ok,
            "B_disagrees_with_A_on_registered_witness": (
                not invalidation["witness"]["same_A"] and invalidation["witness"]["same_B"]
            ),
            "B_train_sample_injective": b_train_induced["injective"],
            "B_test_sample_injective": b_test_induced["injective"],
            "B_test_protected_collisions": b_test_protected,
            "B_test_collision_witnesses": jsonable(b_test_witnesses),
        },
        "candidates": [summarize_report(report) for report in reports],
        "invalidation": jsonable(invalidation),
        "representation_change": change_record,
        "test": {
            "incumbent_total_enumeration_attempts": a_attempts,
            "incumbent_total_unique_checks": a_unique,
            "incumbent_total_exact_identity_checks": a_exact,
            "selected_total_enumeration_attempts": s_attempts,
            "selected_total_unique_checks": s_unique,
            "selected_total_exact_identity_checks": s_exact,
            "ordinary_total_enumeration_attempts": ordinary_attempts,
            "ordinary_total_unique_checks": ordinary_unique,
            "ordinary_total_exact_identity_checks": ordinary_exact,
            "ocm_total_enumeration_attempts": ocm_attempts,
            "ocm_total_unique_checks": ocm_unique,
            "ocm_total_exact_identity_checks": ocm_exact,
            "revoked_total_enumeration_attempts": revoked_attempts,
            "revoked_total_unique_checks": revoked_unique,
            "revoked_total_exact_identity_checks": revoked_exact,
            "selected_protected_collisions": selected_protected,
            "selected_collision_witnesses": jsonable(selected_test_witnesses),
            "exact_check_saving_vs_A": a_exact - s_exact,
            "ordinary_equals_ocm": ordinary_equal_ocm,
            "revoked_equals_incumbent": revoke_equals_A,
            "incumbent_rows": jsonable(a_rows),
            "selected_rows": jsonable(selected_rows),
            "ordinary_rows": jsonable(ordinary_rows),
            "ocm_rows": jsonable(ocm_rows),
            "revoked_rows": jsonable(revoked_rows),
        },
        "accounting": {
            "parent_val_catalog_enumeration_attempts": val_catalog["total_enumeration_attempts"],
            "parent_test_catalog_enumeration_attempts": test_catalog["total_enumeration_attempts"],
            "discovery_key_computations_all_candidates": discovery_key_computations,
            "discovery_validation_exact_checks_all_candidates": discovery_val_exact,
            "discovery_wall_seconds": discovery_wall,
            "study_wall_seconds": time.perf_counter() - run_start,
            "note": "Discovery charges building A,B,C,D indexes on the validation-bound catalog plus validation lookups.",
        },
        "ocm": {
            "atom_id": ocm_atom_id,
            "probe_id": probe_id,
            "training_evidence": training_evidence,
            "utility_evidence": utility_evidence,
            "restart_before_test": True,
            "support_withdrawal_ablation": True,
            "atom_type": "representation",
        },
        "successor_v2": successor,
        "root_cause": root_cause,
        "claim_boundary": claim_boundary,
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
        "selected_id": result["selected_id"],
        "eligible_ids": result["eligible_ids"],
        "exact_check_saving_vs_A": result["test"]["exact_check_saving_vs_A"],
        "successor_v2_terminal": result["successor_v2"]["terminal"],
        "successor_v2_selected_id": result["successor_v2"]["selected_id"],
        "root_cause": result["root_cause"],
        "study_wall_seconds": result["accounting"]["study_wall_seconds"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

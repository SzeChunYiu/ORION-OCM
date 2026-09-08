"""Prospective G3.2 scoped failure-memory study.

A previously earned macro is held fixed. Exact development comparisons learn
method-specific resource-failure scopes over predeclared target features. Fresh
test identities evaluate generalization after subtracting an analytic static
applicability parent and a task-id cache parent.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import importlib.util
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
G3_PATH = REPO / "research" / "g3-independent-composition-v1" / "experiment.py"
G3_BLOB = "a54492b2de07d81c0c7765efd8a7958726559d74"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G2 = _load(G2_PATH, "g2_macro_parent_failure")
G3 = _load(G3_PATH, "g3_composition_parent_failure")

from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

MACRO = ("square", "dec", "square")
SEARCH_VERSION = "g2.macro-operator.v1"
RESOURCE_METRIC = "enumeration_attempts"
MAX_PRIMITIVE_LENGTH = 8
DEVELOPMENT_SALT = "orion-ocm-g3-failure-development-v1"
TEST_SALT = "orion-ocm-g3-failure-test-v1"
DEVELOPMENT_N = 128
TEST_N = 256
MIN_BUCKET_SUPPORT = 4
SCOPE = Scope.of("polynomial-scoped-failure.v1")
METHOD_FINGERPRINT = content_hash({
    "kind": "macro.operator.v1",
    "macro": MACRO,
    "search_version": SEARCH_VERSION,
})

FEATURE_FAMILIES = (
    ("F1", ("degree",)),
    ("F2", ("degree", "constant_sign")),
    ("F3", ("degree", "abs_constant_mod2")),
    ("F4", ("degree", "constant_sign", "abs_constant_mod2")),
    ("F5", ("degree", "nonzero_coeff_count")),
    ("F6", ("degree", "constant_sign", "nonzero_coeff_count")),
)


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def polynomial_degree(coefficients) -> int:
    last = 0
    for i, value in enumerate(coefficients):
        if value != 0:
            last = i
    return last


def feature_values(task):
    coefficients = tuple(task.coefficients)
    constant = coefficients[0] if coefficients else 0
    return {
        "degree": polynomial_degree(coefficients),
        "constant_sign": -1 if constant < 0 else (1 if constant > 0 else 0),
        "abs_constant_mod2": abs(int(constant)) % 2,
        "nonzero_coeff_count": sum(1 for value in coefficients if value != 0),
    }


def bucket_for(task, fields):
    features = feature_values(task)
    return tuple(features[field] for field in fields)


def macro_min_degree() -> int:
    return polynomial_degree(G2.M.normal_form(MACRO))


def exposed_length8(population):
    out = set()
    out.update(
        task.fingerprint
        for task in G2.take_stratum(population, 8, G2.TEST_SALT, G2.TEST_N)
    )
    g3_parts = G3.frozen_partition()
    out.update(task.fingerprint for task in g3_parts["test"])
    return out


def ranked_fresh(population, salt, n, exclude=()):
    excluded = set(exclude)
    pool = [
        task for _fp, (minimum, task) in population.items()
        if minimum == 8 and task.fingerprint not in excluded
    ]
    chosen = tuple(sorted(
        pool,
        key=lambda task: (G2.stable_rank(salt, task.fingerprint), task.fingerprint),
    )[:n])
    if len(chosen) != n:
        raise RuntimeError(f"fresh length-8 population too small: {len(chosen)} < {n}")
    return chosen


def frozen_partition():
    population = G2.minimal_length_population(8)
    exposed = exposed_length8(population)
    development = ranked_fresh(population, DEVELOPMENT_SALT, DEVELOPMENT_N, exposed)
    test = ranked_fresh(
        population,
        TEST_SALT,
        TEST_N,
        exposed | {task.fingerprint for task in development},
    )
    ids = [task.fingerprint for task in development + test]
    if len(ids) != len(set(ids)):
        raise RuntimeError("failure-memory population overlap")
    return population, exposed, development, test


def build_arm_rows(tasks):
    primitive_index = G2.build_search_index(None, MAX_PRIMITIVE_LENGTH)
    macro_index = G2.build_search_index(MACRO, MAX_PRIMITIVE_LENGTH)
    rows = []
    for task in tasks:
        primitive = G2.solve_from_index(task, primitive_index)
        macro = G2.solve_from_index(task, macro_index)
        delta = macro["enumeration_attempts"] - primitive["enumeration_attempts"]
        rows.append({
            "task": task.fingerprint,
            "features": feature_values(task),
            "primitive_attempts": primitive["enumeration_attempts"],
            "macro_attempts": macro["enumeration_attempts"],
            "macro_used": macro["macro_used"],
            "primitive_program": primitive["program"],
            "macro_program": macro["program"],
            "outcome": "HARMFUL" if delta > 0 else ("HELPFUL" if delta < 0 else "NEUTRAL"),
            "delta_macro_minus_primitive": delta,
        })
    return rows


def static_attempt(row):
    return row["primitive_attempts"] if row["features"]["degree"] < macro_min_degree() else row["macro_attempts"]


def induce_scopes(rows, family_name, fields):
    buckets = defaultdict(list)
    for row in rows:
        if row["features"]["degree"] < macro_min_degree():
            continue
        bucket = tuple(row["features"][field] for field in fields)
        buckets[bucket].append(row)
    blocked = []
    for bucket, members in sorted(buckets.items(), key=lambda item: repr(item[0])):
        if len(members) < MIN_BUCKET_SUPPORT:
            continue
        if all(member["outcome"] == "HARMFUL" for member in members):
            blocked.append({
                "family": family_name,
                "fields": fields,
                "bucket": bucket,
                "support": len(members),
                "support_task_ids": tuple(sorted(member["task"] for member in members)),
                "total_avoidable_attempts": sum(
                    member["macro_attempts"] - member["primitive_attempts"] for member in members
                ),
            })
    return tuple(blocked)


def policy_attempt(row, blocked, fields):
    if row["features"]["degree"] < macro_min_degree():
        return row["primitive_attempts"], "STATIC_PRIMITIVE"
    bucket = tuple(row["features"][field] for field in fields)
    blocked_keys = {tuple(scope["bucket"]) for scope in blocked}
    if bucket in blocked_keys:
        return row["primitive_attempts"], "FAILURE_SCOPE_PRIMITIVE"
    return row["macro_attempts"], "MACRO"


def select_failure_family(development_rows):
    static_total = sum(static_attempt(row) for row in development_rows)
    evaluations = []
    for order, (family_name, fields) in enumerate(FEATURE_FAMILIES):
        blocked = induce_scopes(development_rows, family_name, fields)
        decisions = []
        total = 0
        for row in development_rows:
            attempts, action = policy_attempt(row, blocked, fields)
            total += attempts
            decisions.append({"task": row["task"], "attempts": attempts, "action": action})
        evaluations.append({
            "family": family_name,
            "fields": fields,
            "blocked_scopes": blocked,
            "development_attempts": total,
            "static_development_attempts": static_total,
            "saving_vs_static": static_total - total,
            "decisions": decisions,
            "order": order,
        })
    best = min(evaluations, key=lambda item: (item["development_attempts"], item["order"]))
    accepted = bool(best["blocked_scopes"] and best["development_attempts"] < static_total)
    return {
        "accepted": accepted,
        "terminal": "FAILURE_SCOPE_SELECTED" if accepted else "NO_SCOPED_FAILURE_BUCKET",
        "static_development_attempts": static_total,
        "selected": best,
        "evaluations": evaluations,
    }


def evaluate_test_policy(rows, selection):
    fields = tuple(selection["selected"]["fields"])
    blocked = tuple(selection["selected"]["blocked_scopes"])
    static_total = sum(static_attempt(row) for row in rows)
    macro_total = sum(row["macro_attempts"] for row in rows)
    primitive_total = sum(row["primitive_attempts"] for row in rows)
    scoped_total = 0
    hits = 0
    false_blocks = []
    retained_macro_wins = []
    decisions = []
    for row in rows:
        attempts, action = policy_attempt(row, blocked, fields)
        scoped_total += attempts
        if action == "FAILURE_SCOPE_PRIMITIVE":
            hits += 1
            if row["macro_attempts"] < row["primitive_attempts"]:
                false_blocks.append(row["task"])
        elif action == "MACRO" and row["macro_attempts"] < row["primitive_attempts"] and row["macro_used"]:
            retained_macro_wins.append(row["task"])
        decisions.append({"task": row["task"], "attempts": attempts, "action": action})
    return {
        "primitive_attempts": primitive_total,
        "always_macro_attempts": macro_total,
        "static_attempts": static_total,
        "scoped_attempts": scoped_total,
        "fresh_failure_scope_hits": hits,
        "false_blocks": false_blocks,
        "retained_macro_win_tasks": retained_macro_wins,
        "decisions": decisions,
    }


def ordinary_persist(path: Path, scopes, family, fields):
    payload = {
        "method_fingerprint": METHOD_FINGERPRINT,
        "search_version": SEARCH_VERSION,
        "resource_metric": RESOURCE_METRIC,
        "max_primitive_length": MAX_PRIMITIVE_LENGTH,
        "family": family,
        "fields": list(fields),
        "scopes": list(scopes),
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
    return len(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())


def ordinary_load(path: Path, *, search_version=SEARCH_VERSION):
    payload = json.loads(path.read_text())
    if payload["method_fingerprint"] != METHOD_FINGERPRINT:
        return ()
    if payload["search_version"] != search_version:
        return ()
    if payload["resource_metric"] != RESOURCE_METRIC or payload["max_primitive_length"] != MAX_PRIMITIVE_LENGTH:
        return ()
    return tuple(payload["scopes"])


def _admit_method(runtime):
    receipt = {
        "schema": "g3.failure.imported-method.v1",
        "source": "merged-pr-192",
        "terminal": "CAUSAL_MACRO_OPERATOR_REUSE_SUPPORTED_AT_LENGTH8",
        "macro": MACRO,
        "method_fingerprint": METHOD_FINGERPRINT,
        "search_version": SEARCH_VERSION,
    }
    _rec, evidence = runtime.admit_evidence(
        receipt, Channel.IMPORTED, "g3.failure.pr192-method.v1", scope=SCOPE
    )
    warrant = WarrantProfile.of({evidence})
    source_id = "g3-failure-method-source:" + content_hash(receipt)
    runtime.admit_object(
        Atom(
            source_id,
            "proof",
            warrant,
            scope=SCOPE,
            quarantined=True,
            content_ref=content_hash(receipt),
            meta=tuple(receipt.items()),
        ),
        (),
        "IMPORTED",
    )
    payload = {
        "kind": "macro.operator.failure-study.v1",
        "macro": MACRO,
        "method_fingerprint": METHOD_FINGERPRINT,
        "search_version": SEARCH_VERSION,
    }
    method_id = "g3-failure-method:" + content_hash(payload)
    edge = Hyperedge(
        "support:" + method_id,
        (source_id,),
        (method_id,),
        "SUPPORT",
        warrant=warrant,
    )
    runtime.admit_object(
        Atom(
            method_id,
            "procedure",
            warrant,
            scope=SCOPE,
            content_ref=content_hash(payload),
            meta=tuple(payload.items()),
        ),
        (edge,),
        "IMPORTED",
    )
    return method_id


def admit_failure_memory(root: Path, scopes, family, fields, support_rows, *, revoke=False):
    runtime = OCMRuntime(root)
    method_id = _admit_method(runtime)
    evidence_ids = []
    constraint_ids = []
    row_by_task = {row["task"]: row for row in support_rows}
    for scope in scopes:
        support = [row_by_task[task_id] for task_id in scope["support_task_ids"]]
        receipt = {
            "schema": "g3.failure-scope.evidence.v1",
            "method_fingerprint": METHOD_FINGERPRINT,
            "macro": MACRO,
            "search_version": SEARCH_VERSION,
            "resource_metric": RESOURCE_METRIC,
            "max_primitive_length": MAX_PRIMITIVE_LENGTH,
            "family": family,
            "fields": fields,
            "bucket": scope["bucket"],
            "support_rows": support,
        }
        _rec, evidence = runtime.admit_evidence(
            receipt,
            Channel.EXPERIMENT,
            "g3.failure-scope-comparison.v1",
            scope=SCOPE,
        )
        evidence_ids.append(evidence)
        warrant = WarrantProfile.of({evidence})
        source_id = "g3-failure-source:" + content_hash(receipt)
        runtime.admit_object(
            Atom(
                source_id,
                "counterexample",
                warrant,
                scope=SCOPE,
                quarantined=True,
                content_ref=content_hash(receipt),
                meta=tuple(receipt.items()),
            ),
            (),
            "EXPERIMENTATION",
        )
        payload = {
            "kind": "method.failure-scope.v1",
            "method_fingerprint": METHOD_FINGERPRINT,
            "macro": MACRO,
            "feature_family": family,
            "fields": fields,
            "bucket": scope["bucket"],
            "resource_metric": RESOURCE_METRIC,
            "search_version": SEARCH_VERSION,
            "max_primitive_length": MAX_PRIMITIVE_LENGTH,
            "support_task_ids": scope["support_task_ids"],
            "support_count": scope["support"],
        }
        constraint_id = "g3-failure-constraint:" + content_hash(payload)
        edges = (
            Hyperedge(
                "support:" + constraint_id,
                (source_id,),
                (constraint_id,),
                "SUPPORT",
                warrant=warrant,
            ),
            Hyperedge(
                "constraint:" + constraint_id,
                (constraint_id,),
                (method_id,),
                "CONSTRAINT",
                warrant=warrant,
            ),
        )
        runtime.admit_object(
            Atom(
                constraint_id,
                "constraint",
                warrant,
                scope=SCOPE,
                content_ref=content_hash(payload),
                meta=tuple(payload.items()),
            ),
            edges,
            "EXPERIMENTATION",
        )
        constraint_ids.append(constraint_id)
    if revoke and evidence_ids:
        runtime.revoke(tuple(evidence_ids))
    runtime.persist()
    replay = OCMRuntime(root)
    loaded = load_failure_scopes(replay, search_version=SEARCH_VERSION)
    return loaded, tuple(constraint_ids), tuple(evidence_ids), method_id


def load_failure_scopes(runtime, *, search_version):
    loaded = []
    for atom in runtime.state.ks.atoms:
        if atom.atom_type != "constraint" or atom.liveness(runtime.state.revoked) is not Liveness.LIVE:
            continue
        meta = dict(atom.meta)
        if meta.get("kind") != "method.failure-scope.v1":
            continue
        if meta.get("method_fingerprint") != METHOD_FINGERPRINT:
            continue
        if meta.get("search_version") != search_version:
            continue
        if meta.get("resource_metric") != RESOURCE_METRIC:
            continue
        if int(meta.get("max_primitive_length")) != MAX_PRIMITIVE_LENGTH:
            continue
        loaded.append({
            "family": meta["feature_family"],
            "fields": tuple(meta["fields"]),
            "bucket": tuple(meta["bucket"]),
            "support": int(meta["support_count"]),
            "support_task_ids": tuple(meta["support_task_ids"]),
        })
    return tuple(sorted(loaded, key=lambda item: (item["family"], repr(item["bucket"]))))


def decisions_from_loaded(rows, scopes, fields):
    out = []
    total = 0
    for row in rows:
        attempts, action = policy_attempt(row, scopes, fields)
        total += attempts
        out.append({"task": row["task"], "attempts": attempts, "action": action})
    return out, total


def run():
    if git_blob_sha1(G2_PATH) != G2_BLOB:
        raise RuntimeError("G2 macro source drift")
    if git_blob_sha1(G3_PATH) != G3_BLOB:
        raise RuntimeError("G3 composition source drift")

    start = time.perf_counter()
    _population, exposed, development_tasks, test_tasks = frozen_partition()
    development_rows = build_arm_rows(development_tasks)
    test_rows = build_arm_rows(test_tasks)

    # The static parent is only licensed if the declared structural bound has no counterexample.
    below_bound_wins = [
        row["task"] for row in development_rows + test_rows
        if row["features"]["degree"] < macro_min_degree()
        and row["macro_attempts"] < row["primitive_attempts"]
    ]
    if below_bound_wins:
        return {
            "schema": "g3.scoped-failure.result.v1",
            "terminal": "CANNOT_CHECK_STATIC_APPLICABILITY",
            "failure_memory_useful": False,
            "below_bound_macro_wins": below_bound_wins,
        }

    selection = select_failure_family(development_rows)
    if not selection["accepted"]:
        return {
            "schema": "g3.scoped-failure.result.v1",
            "terminal": "NO_SCOPED_FAILURE_BUCKET",
            "failure_memory_useful": False,
            "selection": selection,
            "partition": _partition_receipt(exposed, development_tasks, test_tasks),
            "study_wall_seconds": time.perf_counter() - start,
        }

    test_eval = evaluate_test_policy(test_rows, selection)
    family = selection["selected"]["family"]
    fields = tuple(selection["selected"]["fields"])
    scopes = tuple(selection["selected"]["blocked_scopes"])

    # Exact task-id cache has no fresh hits by construction; policy is static applicability.
    development_ids = {row["task"] for row in development_rows}
    task_id_hits = [row["task"] for row in test_rows if row["task"] in development_ids]
    if task_id_hits:
        raise RuntimeError("fresh test unexpectedly overlaps development task-id cache")
    task_id_cache_total = test_eval["static_attempts"]

    with tempfile.TemporaryDirectory(prefix="ocm-g3-failure-") as temp_dir:
        root = Path(temp_dir)
        ordinary_path = root / "ordinary-failure.json"
        ordinary_bytes = ordinary_persist(ordinary_path, scopes, family, fields)
        ordinary_scopes = ordinary_load(ordinary_path)
        ordinary_decisions, ordinary_total = decisions_from_loaded(test_rows, ordinary_scopes, fields)

        ocm_scopes, constraint_ids, evidence_ids, method_id = admit_failure_memory(
            root / "ocm-live", scopes, family, fields, development_rows, revoke=False
        )
        ocm_decisions, ocm_total = decisions_from_loaded(test_rows, ocm_scopes, fields)

        revoked_scopes, _constraint_ids2, _evidence_ids2, _method_id2 = admit_failure_memory(
            root / "ocm-revoked", scopes, family, fields, development_rows, revoke=True
        )
        revoked_decisions, revoked_total = decisions_from_loaded(test_rows, revoked_scopes, fields)

        # Version mismatch must reopen rather than reusing stale failure claims.
        replay = OCMRuntime(root / "ocm-live")
        mismatched_scopes = load_failure_scopes(replay, search_version="g2.macro-operator.v2")

    ordinary_equals_ocm = ordinary_decisions == ocm_decisions and ordinary_total == ocm_total
    revoked_equals_static = revoked_total == test_eval["static_attempts"] and all(
        decision["attempts"] == static_attempt(row)
        for decision, row in zip(revoked_decisions, test_rows)
    )
    version_mismatch_reopens = not mismatched_scopes

    if not ordinary_equals_ocm or not revoked_equals_static or not version_mismatch_reopens:
        terminal = "CANNOT_CHECK_FAILURE_MEMORY_PERSISTENCE"
        useful = False
    elif test_eval["false_blocks"]:
        terminal = "HARMFUL_TRANSFER_LIMIT"
        useful = False
    elif test_eval["fresh_failure_scope_hits"] <= 0:
        terminal = "FAILURE_SCOPE_DOES_NOT_GENERALIZE"
        useful = False
    elif test_eval["scoped_attempts"] >= test_eval["static_attempts"]:
        terminal = "STATIC_APPLICABILITY_PARENT_SUFFICIENT"
        useful = False
    elif test_eval["scoped_attempts"] >= test_eval["always_macro_attempts"]:
        terminal = "FAILURE_MEMORY_NOT_USEFUL"
        useful = False
    elif not test_eval["retained_macro_win_tasks"]:
        terminal = "FAILURE_MEMORY_NOT_USEFUL"
        useful = False
    else:
        terminal = "FAILURE_MEMORY_USEFUL_AT_SCOPE"
        useful = True

    scope_payload = {
        "family": family,
        "fields": fields,
        "scopes": scopes,
        "method_fingerprint": METHOD_FINGERPRINT,
        "search_version": SEARCH_VERSION,
    }
    scope_bytes = len(json.dumps(scope_payload, sort_keys=True, separators=(",", ":")).encode())

    return {
        "schema": "g3.scoped-failure.result.v1",
        "terminal": terminal,
        "failure_memory_useful": useful,
        "method": {
            "macro": MACRO,
            "fingerprint": METHOD_FINGERPRINT,
            "search_version": SEARCH_VERSION,
            "macro_min_degree": macro_min_degree(),
        },
        "partition": _partition_receipt(exposed, development_tasks, test_tasks),
        "selection": selection,
        "test": {
            **test_eval,
            "task_id_cache_attempts": task_id_cache_total,
            "task_id_cache_fresh_hits": 0,
            "ordinary_attempts": ordinary_total,
            "ocm_attempts": ocm_total,
            "revoked_attempts": revoked_total,
            "ordinary_equals_ocm": ordinary_equals_ocm,
            "revoked_equals_static": revoked_equals_static,
            "version_mismatch_reopens": version_mismatch_reopens,
        },
        "persistence": {
            "ordinary_serialized_bytes": ordinary_bytes,
            "canonical_scope_payload_bytes": scope_bytes,
            "constraint_ids": constraint_ids,
            "failure_evidence_ids": evidence_ids,
            "method_id": method_id,
            "stored_scope_count": len(scopes),
        },
        "accounting": {
            "development_primitive_attempts": sum(row["primitive_attempts"] for row in development_rows),
            "development_macro_attempts": sum(row["macro_attempts"] for row in development_rows),
            "feature_family_count": len(FEATURE_FAMILIES),
            "feature_component_work": sum(len(fields) for _name, fields in FEATURE_FAMILIES) * len(development_rows),
            "bucket_induction_task_visits": len(FEATURE_FAMILIES) * len(development_rows),
            "test_scope_lookup_count": len(test_rows),
            "avoided_macro_attempts_vs_always_macro": test_eval["always_macro_attempts"] - test_eval["scoped_attempts"],
            "saving_vs_static": test_eval["static_attempts"] - test_eval["scoped_attempts"],
            "study_wall_seconds": time.perf_counter() - start,
        },
        "claim_boundary": (
            "Method-specific resource failure memory only. No task impossibility, truth, or global method invalidity is inferred. "
            "The ordinary scoped-nogood parent receives the identical learned scopes and policy; no OCM novelty claim."
        ),
    }


def _partition_receipt(exposed, development, test):
    return {
        "development_salt": DEVELOPMENT_SALT,
        "test_salt": TEST_SALT,
        "development_n": DEVELOPMENT_N,
        "test_n": TEST_N,
        "prior_exposed_length8_ids": sorted(exposed),
        "development_ids": [task.fingerprint for task in development],
        "test_ids": [task.fingerprint for task in test],
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
        "selected_family": result.get("selection", {}).get("selected", {}).get("family"),
        "scope_count": len(result.get("selection", {}).get("selected", {}).get("blocked_scopes", [])),
        "fresh_hits": result.get("test", {}).get("fresh_failure_scope_hits"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()

"""Host adapter for actual E1/E3 donor implementations; no oracle diagnoses.

Exact source is pinned in DONOR_MANIFEST.json. The proposer receives bounded
configuration choices and measured outcomes, never the human interpretation.
This imports individual components, not any original protected sweep runner.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "donor_runtime"))
import subspace as S
import subspace_arms as SA
import depend as D
import depend_arms as DA
from games import SubtractionGame

S_MODES = ("discovering_arm", "fixed_feature_arm", "exact_scan_parent",
           "signature_hash_parent", "nearest_neighbour_parent")
D_MODES = ("learned_dependency_arm", "lazy_learner_arm",
           "full_recomputation_parent", "co_occurrence_parent", "all_evidence_parent")
INITIAL_CONFIG = {"route_s": "s0", "route_d": "d0"}
ALLOWED = {"route_s": ["s" + str(i) for i in range(len(S_MODES))],
           "route_d": ["d" + str(i) for i in range(len(D_MODES))]}
TRACE_SINK = None  # External host output; never part of proposer inputs.


def task(domain, scale, instance, phase):
    # Contract identity excludes the display name and phase. Scale and probe
    # position/family subset change executable contracts, not just task labels.
    contract = {"domain": domain, "scale": scale, "instance": instance}
    identity = hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest()
    return {**contract, "task_id": phase + ":" + identity,
            "semantic_id": identity, "ecology": "development"}


def candidates():
    from evolution import Candidate
    result = []
    for key, values in ALLOWED.items():
        for value in values:
            ident = hashlib.sha256((key + value).encode()).hexdigest()[:12]
            result.append(Candidate("candidate-" + ident, "C1", "router.dispatch",
                {key: value}, "existing_alternative",
                "pinned cognitive-ladder existing arm; external DONOR_MANIFEST.json"))
    return result


def _subspace(config, item):
    start = time.perf_counter_ns()
    scale, instance = item["scale"], item["instance"]
    arm = SA.ARMS[S_MODES[int(config["route_s"][1:])]](S.build_catalogue(1))
    construction = [arm.install_record]
    if scale != 1:
        construction.append(arm.grow(S.build_catalogue(scale)))
    # The same source game's acquired rule objects and observation vectors are
    # used at fresh exact probe positions. No altered easy game generator.
    base_queries = S.query_stream()
    selected = [base_queries[i] for i in range(0, len(base_queries), 5)]
    position = 2003 + 2 * instance
    outcomes = []
    for q in selected:
        truth = SubtractionGame(q.moves).grundy_upto(position)[position] == 0
        query = S.Query(item["semantic_id"] + ":" + q.family_id, q.family_id,
                        q.moves, q.observations, position, q.in_store, truth)
        outcomes.append(arm.query(query))
    records = construction + [o.record for o in outcomes]
    if any(r.k is None or r.k_status.value != "MEASURED" for r in records):
        raise ValueError("CANNOT_CHECK: incomplete relevance resource measurement")
    # Source query_work excludes checker expansions; explicitly add them here.
    work = sum(r.charged_total_work + r.checker_expansions for r in records)
    return {"correct": all(o.decision_correct for o in outcomes),
            "violations": sum(o.false_match for o in outcomes),
            "work": work, "persistent_bytes": arm.store_bytes + arm.index_bytes,
            "query_work": sum(o.record.query_work for o in outcomes),
            "checker_expansions": sum(r.checker_expansions for r in records),
            "index_work": sum(r.triggered_index_work for r in records),
            "revision_work": 0,
            "k": max(o.record.k for o in outcomes), "N": arm.n_objects,
            "traces": [o.as_dict() for o in outcomes],
            "elapsed_ns": time.perf_counter_ns() - start}


def _dependency(config, item):
    start = time.perf_counter_ns()
    # Exact original catalogue and five-event lifecycle. Scale changes the
    # actual store; instance changes event order. Families overlap across
    # scales, so these are NOT independent family holdouts.
    catalogue = D.build_catalogue(item["scale"])
    arm = DA.ARMS[D_MODES[int(config["route_d"][1:])]](catalogue)
    schedule = D.revocation_schedule(catalogue)
    # Varying the order of independent-family events changes the executable
    # trace. Keep the redundant-support pair's order intact. Only two variants
    # are registered; larger instance IDs do not manufacture new identities.
    if item["instance"] not in (0, 1):
        raise ValueError("only two explicitly registered revision schedules")
    if item["instance"] == 1:
        schedule = tuple(reversed(schedule[:3])) + schedule[3:]
    revisions = [arm.revoke(step) for step in schedule]
    if any(r.k is None or r.revision_work is None or r.k_status.value != "MEASURED"
           for r in revisions):
        raise ValueError("CANNOT_CHECK: incomplete revision resource measurement")
    stale = sum(len(r.stale_survivor_ids) for r in revisions)
    collateral = sum(len(r.collateral_invalidated_ids) for r in revisions)
    work = arm.build_work + sum(r.revision_work for r in revisions)
    return {"correct": stale == collateral == 0,
            "violations": stale, "work": work,
            "persistent_bytes": arm.store.store_bytes + arm.index_bytes,
            "query_work": 0, "checker_expansions": 0,
            "index_work": arm.build_work,
            "revision_work": sum(r.revision_work for r in revisions),
            "k": max(r.k for r in revisions), "N": arm.n_objects,
            "traces": [r.as_dict() for r in revisions],
            "elapsed_ns": time.perf_counter_ns() - start}


def runner(config, tasks):
    rows = []
    for item in tasks:
        if item["ecology"] != "development":
            raise PermissionError("this adapter cannot execute protected tasks")
        if item["domain"] not in ("s", "d"):
            raise ValueError("unregistered actual-source adapter")
        row = (_subspace if item["domain"] == "s" else _dependency)(config, item)
        raw = json.dumps(row.pop("traces"), sort_keys=True).encode()
        trace_sha = hashlib.sha256(raw).hexdigest()
        if TRACE_SINK is not None:
            path = Path(TRACE_SINK) / (trace_sha + ".json")
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_bytes(raw)
        row["trace_sha256"] = trace_sha
        rows.append(row)
    return {"n": len(rows), "success": sum(r["correct"] for r in rows),
            "preservation_violations": sum(r["violations"] for r in rows),
            "resources": {"work": sum(r["work"] for r in rows),
                          "persistent_bytes": max(r["persistent_bytes"] for r in rows)},
            "details": rows}

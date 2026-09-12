#!/usr/bin/env python3
"""IG-4 trace extractor (RV-377-160). SAME-AUTHOR side of the independence gate.

Reads the 264 protected K4 V7 receipts and writes two files:

  k4_v7_traces_v1.json          label-free resource traces. The ONLY data the blind IG-4 author receives.
                                 Contains no registered axis label, no verdict, no family id, no cost total.
  k4_v7_native_buckets_v1.json  the native V4 meter's buckets and every verdict input (costs, scores,
                                 target vectors). Used only by the comparison script AFTER the blind meter
                                 has produced its buckets. Never shown to the blind author.

Every candidate referenced by a receipt (winner, expressibility witness, negative twin, six null-frontier
rows) is reconstructed from the receipt and its reconstruction is verified against the receipt's own
candidate id (sha256 of the candidate serial). A reconstruction that does not reproduce the receipt's id
aborts the extraction (fail closed).

The independent meter must NOT import this module or anything it imports.
"""
from __future__ import annotations

import glob
import hashlib
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.dirname(HERE)
sys.path.insert(0, M)

import gmi_k4_null_frontier_v5 as nf  # noqa: E402
import gmi_k4_resource_native_v4 as rn  # noqa: E402
import gmi_k4_search as base  # noqa: E402
import gmi_k4_search_v4 as v4  # noqa: E402

RES = os.path.join(M, "microscopes", "results", "k4_v7")
LOFO = os.path.join(M, "GMI_K4_LOFO_FREEZE_V1.json")
OUT_TRACES = os.path.join(HERE, "k4_v7_traces_v1.json")
OUT_NATIVE = os.path.join(HERE, "k4_v7_native_buckets_v1.json")

N_PROBES = 24
VARS = sorted(rn._RESOURCE_VARS)


def probe_world(i: int) -> dict:
    """Data-independent probe panel: every world quantity varies independently of every other one.
    world i, quantity v -> 2 + (sha256('IG4-TRACE-V1:i:v')[:8] mod 23)."""
    return {v: 2 + int(hashlib.sha256(f"IG4-TRACE-V1:{i}:{v}".encode()).hexdigest()[:8], 16) % 23 for v in VARS}


PROBES = [probe_world(i) for i in range(N_PROBES)]


def _sig(expr):
    return tuple(rn.eval_expr(expr, p) for p in PROBES)


def _check_panel_separates():
    for laws, name in ((rn.STATE_LAWS, "state"), (rn.SERVE_LAWS, "serve")):
        sigs = {}
        for e in laws:
            s = _sig(e)
            if s in sigs:
                raise SystemExit(f"probe panel aliases two {name} laws: {sigs[s]} vs {e}")
            sigs[s] = e


def _expr_hash10(expr):
    return hashlib.sha256(json.dumps(expr).encode()).hexdigest()[:10]


STATE_BY_HASH = {_expr_hash10(e): e for e in rn.STATE_LAWS}
SERVE_BY_HASH = {_expr_hash10(e): e for e in rn.SERVE_LAWS}
if len(STATE_BY_HASH) != len(rn.STATE_LAWS) or len(SERVE_BY_HASH) != len(rn.SERVE_LAWS):
    raise SystemExit("law hash collision")
CAP_BY_UPPER = {a.upper(): a for a in rn.CAP_ATOMS}
PREFIX_TO_GRAMMAR = {v: k for k, v in rn.PREFIX.items()}


def candidate_from_tokens(tokens: list[str], expected_cid: str) -> rn.Candidate:
    p = tokens[0].split("_")[0]
    grammar = PREFIX_TO_GRAMMAR[p]
    state = serve = None
    caps = []
    routing = sharing = retrieval = iterations = locality = None
    knob = None
    stoch = ver = ext = False
    for t in tokens:
        body = t[len(p) + 1:]
        if body.startswith("ALLOC_"):
            state = STATE_BY_HASH[body[6:]]
        elif body.startswith("WORK_"):
            serve = SERVE_BY_HASH[body[5:]]
        elif body.startswith("CAP_"):
            caps.append(CAP_BY_UPPER[body[4:]])
        elif body.startswith("ROUTE_"):
            routing = body[6:].lower()
        elif body.startswith("SHARE_"):
            sharing = body[6:].lower()
        elif body.startswith("READ_"):
            retrieval = body[5:].lower()
        elif body.startswith("STEP_"):
            iterations = body[5:].lower()
        elif body.startswith("WRITE_"):
            locality = body[6:].lower()
        elif body.startswith("WIDTH_"):
            knob = int(body[6:])
        elif body == "RAND":
            stoch = True
        elif body == "CHECK":
            ver = True
        elif body == "EXTERNAL":
            ext = True
        else:
            raise SystemExit(f"unknown token {t}")
    cand = rn.Candidate(grammar, state, serve, tuple(sorted(caps)), routing, sharing, retrieval, iterations,
                        stoch, ver, ext, locality, knob)
    if cand.cid != expected_cid:
        raise SystemExit(f"winner reconstruction mismatch: {cand.cid} != {expected_cid}")
    return cand


def _serial_cid(grammar, state, serve, atoms, vec, knob):
    serial = [grammar, state, serve, atoms, vec["routing"], vec["sharing"], vec["retrieval"], vec["serve_iterations"],
              bool(vec["stochastic_serve"]), bool(vec["verifier_gated"]), bool(vec["external_authority"]),
              vec["update_locality"], knob]
    return hashlib.sha256(json.dumps(serial, sort_keys=True).encode()).hexdigest()[:20]


def candidate_from_vector_and_cid(grammar: str, vec: dict, cid: str) -> rn.Candidate:
    """Brute-force inversion of a candidate id given its measured vector (the receipt carries both)."""
    states = [rn.STATE_REFERENCE[vec["state_scales_with"]]] if vec["state_scales_with"] in rn.STATE_REFERENCE else list(rn.STATE_DISTRACTORS)
    serves = [rn.SERVE_REFERENCE[vec["serve_scales_with"]]] if vec["serve_scales_with"] in rn.SERVE_REFERENCE else list(rn.SERVE_DISTRACTORS)
    for k in (1, 2, 3):
        for combo in itertools.combinations(rn.CAP_ATOMS, k):
            atoms = tuple(sorted(combo))
            for knob in (1, 2):
                for st in states:
                    for sv in serves:
                        if _serial_cid(grammar, st, sv, atoms, vec, knob) == cid:
                            cand = rn.Candidate(grammar, st, sv, atoms, vec["routing"], vec["sharing"], vec["retrieval"],
                                                vec["serve_iterations"], bool(vec["stochastic_serve"]), bool(vec["verifier_gated"]),
                                                bool(vec["external_authority"]), vec["update_locality"], knob)
                            if cand.cid != cid:
                                raise SystemExit("cid inversion inconsistency")
                            return cand
    raise SystemExit(f"could not invert candidate id {cid}")


def trace_of(cand: rn.Candidate, scale: int, profile: dict, is_null: bool) -> dict:
    gp = rn.GRAMMAR_PRICE[cand.grammar]
    env = rn.task_env(scale)
    cost = nf.null_cost(cand, scale, profile) if is_null else rn.lifecycle(cand, scale, profile)
    p0 = dict(profile); p0["dependence_density"] = 0.0
    p1 = dict(profile); p1["dependence_density"] = 1.0
    c0 = nf.null_cost(cand, scale, p0) if is_null else rn.lifecycle(cand, scale, p0)
    c1 = nf.null_cost(cand, scale, p1) if is_null else rn.lifecycle(cand, scale, p1)
    state_at, work_at = rn.resource_counts(cand, scale)
    return {
        "retained_state_cells": [rn.eval_expr(cand.state_expr, p) for p in PROBES],
        "per_query_work_units": [rn.eval_expr(cand.serve_expr, p) for p in PROBES],
        "cell_scale_probe": {"world": env, "retained_state_cells": state_at, "per_query_work_units": work_at},
        "feedback_probe": {
            "retained_state_cells": state_at,
            "state_cells_rewritten_per_feedback_event": float(cost["update_retraining"]) / gp,
        },
        "content_dependence_probe": {
            "per_query_work_at_dependence_0": float(c0["serve_compute_latency"]) / gp,
            "per_query_work_at_dependence_1": float(c1["serve_compute_latency"]) / gp,
        },
        "verification_probe": {
            "per_query_work_units": work_at,
            "verification_work_per_query": float(cost["verification"]) / gp,
        },
        "external_probe": {"external_interventions_per_lifecycle": float(cost["human_external_intervention"])},
        "declared_structure": {
            "parameter_blocks_shared_across_positions": cand.sharing == "shared",
            "lookup_mechanism": {"none": "none", "exact_key": "exact_key_match", "metric": "nearest_by_metric"}[cand.retrieval],
            "serve_passes_per_query": {"one": "single", "many": "repeated"}[cand.serve_iterations],
            "answer_varies_across_identical_queries": bool(cand.stochastic_serve),
        },
    }


def main() -> int:
    _check_panel_separates()
    freeze = json.load(open(LOFO))
    families = freeze["families"]
    files = sorted(glob.glob(os.path.join(RES, "K4V7_*.json")))
    if len(files) != 264:
        raise SystemExit(f"expected 264 receipts, found {len(files)}")
    traces = {"schema": "GMIIG4TraceFileV1", "n_probe_worlds": N_PROBES, "world_quantities": VARS,
              "probe_worlds": PROBES, "candidates": {}}
    native = {"schema": "GMIIG4NativeBucketsV1", "threshold": v4.THRESHOLD,
              "registered_budget": v4.REGISTERED_STOCHASTIC_BUDGET, "tasks": [], "candidates": {}}
    roles = {"winner": 0, "witness": 0, "twin": 0, "null": 0}
    for path in files:
        r = json.load(open(path))
        raw = r["raw_result"]
        i = int(r["task_index"])
        family, grammar, cell = raw["family"], raw["grammar"], raw["cell"]
        scale = int(cell[1:])
        profile = raw["world_profile"]
        task = base.OBLIGATION_KIND[raw["obligation_class"]]
        target = families[family]["property_vector"]
        entry = {"task_index": i, "family": family, "grammar": grammar, "cell": cell, "scale": scale,
                 "native_verdict": r["verdict"], "native_reason": raw.get("reason"), "target_vector": target,
                 "controls_recovered": all(x["recovered"] for x in raw["controls"].values()),
                 "budget_met": bool(raw["coverage"]["budget_requirement_met"]),
                 "winner": None, "witness": None, "twin": None, "nulls": []}

        def add(ref, cand, role, extra, is_null=False):
            traces["candidates"][ref] = {"ref": ref, "task_index": i, "role": role, **trace_of(cand, scale, profile, is_null)}
            native["candidates"][ref] = {"ref": ref, "task_index": i, "role": role, "native_vector": cand.vector(), **extra}
            roles[role] += 1

        if raw.get("winner_candidate_id"):
            w = candidate_from_tokens(raw["winner_program_tokens"], raw["winner_candidate_id"])
            if w.vector() != raw["measured_property_vector"]:
                raise SystemExit(f"winner vector mismatch at task {i}")
            ref = f"{i:05d}:winner"
            add(ref, w, "winner", {"scalar_lifecycle_cost": raw["scalar_lifecycle_cost"]})
            entry["winner"] = {"ref": ref, "scalar_lifecycle_cost": raw["scalar_lifecycle_cost"], "native_vector": w.vector()}
        wit = raw.get("expressibility_witness")
        if wit:
            wc = rn.witness_from_target(grammar, target, task)
            if wc.cid != wit["candidate_id"]:
                raise SystemExit(f"witness reconstruction mismatch at task {i}")
            ref = f"{i:05d}:witness"
            add(ref, wc, "witness", {"semantic_score": wit["semantic_score"], "scalar_lifecycle_cost": wit["scalar_lifecycle_cost"]})
            entry["witness"] = {"ref": ref, "semantic_score": wit["semantic_score"], "scalar_lifecycle_cost": wit["scalar_lifecycle_cost"],
                                "native_expressible": wit["expressible"], "native_vector": wc.vector()}
        if raw.get("negative_twin_candidate_id"):
            tw = candidate_from_vector_and_cid(grammar, raw["negative_twin_measured_vector"], raw["negative_twin_candidate_id"])
            ref = f"{i:05d}:twin"
            add(ref, tw, "twin", {})
            entry["twin"] = {"ref": ref, "native_vector": tw.vector()}
        nulls = nf.null_candidates(grammar)
        for row in raw["null_frontier"]["rows"]:
            nc = nulls[row["null_id"]]
            if nc.cid != row["candidate_id"]:
                raise SystemExit(f"null reconstruction mismatch at task {i} {row['null_id']}")
            ref = f"{i:05d}:null:{row['null_id']}"
            add(ref, nc, "null", {"null_id": row["null_id"], "admissible": row["admissible"], "scalar_lifecycle_cost": row["scalar_lifecycle_cost"]}, is_null=True)
            entry["nulls"].append({"ref": ref, "null_id": row["null_id"], "admissible": row["admissible"],
                                   "scalar_lifecycle_cost": row["scalar_lifecycle_cost"], "native_vector": nc.vector()})
        native["tasks"].append(entry)
    native["tasks"].sort(key=lambda e: e["task_index"])
    json.dump(traces, open(OUT_TRACES, "w"), indent=1, sort_keys=True)
    json.dump(native, open(OUT_NATIVE, "w"), indent=1, sort_keys=True)
    summary = {"receipts": len(files), "candidates": len(traces["candidates"]), "roles": roles,
               "traces_sha256": hashlib.sha256(open(OUT_TRACES, "rb").read()).hexdigest(),
               "native_sha256": hashlib.sha256(open(OUT_NATIVE, "rb").read()).hexdigest()}
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

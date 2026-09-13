"""IG-4 independent meter, V1 (blind-authored, spec-only).

served_model: claude-fable-5-1
served_model_exact_id: claude-fable-5-1[1m]
label: HUMAN_GATE_BYPASSED__MODEL_PROXY
author_role: ig4-blind-author
date: 2026-09-12
record: RV-377-160 (IG-4 METER AUTHORSHIP)
schema_out: GMIIG4IndependentBucketsV1

Provenance of authorship
------------------------
This file was written from the IG-4 Independent Meter Specification V1 and the
single trace file `k4_v7_traces_v1.json` only. No other meter, no other file in
the repository, and no version-control history were consulted. Nothing was
executed except `python3 -m py_compile` on this file. The author is a model
proxy standing in for a human independent author; hence the label above.

The trace file was inspected only for its FORMAT (top-level keys, the 24 probe
worlds, the world-quantity list, and a handful of entries to confirm the field
layout and that traces are exact integers). Every rule below is a function of
the definitions in spec section 2 and the format in spec section 3; no rule is
tuned to the distribution of candidates, and no rule depends on how many
candidates fall in any bucket. The `role` field is never read by the meter.

Rules, fixed in advance
=======================

R1. Law matching (state_scales_with, serve_scales_with)
-------------------------------------------------------
Each registered law name is read literally as an integer-valued function of the
world quantities (the tables in spec sections 2.1 and 2.2). For a trace
t[0..23] and a law L, the law value in probe world i is L[i] = law(world_i).

A trace MATCHES a law iff the trace is equal to the law UP TO ONE POSITIVE
CONSTANT FACTOR, exactly:

    there exists c > 0 such that t[i] == c * L[i] for every i in 0..23.

Because traces and law values are exact integers, this is decided with exact
integer arithmetic and no floating tolerance:

    t[i] > 0 for all i,   and   t[i] * L[0] == t[0] * L[i] for all i.

Justification. The registered names are statements of *growth* ("grows with
X", "the product X * Y", ...), not of unit. A machine whose state is exactly 2
cells per feature grows with `features` just as one with 1 cell per feature
does; the constant is a cell-accounting convention, not a different law. A
fitted tolerance, on the other hand, would let a trace that follows no named
law be pushed onto the nearest one, which the spec forbids ("Do not invent a
nearest label"). Hence: exact proportionality, tolerance zero, additive offsets
NOT allowed (an additive constant is a second term, i.e. a different law).

Consequences that follow from R1 without any further choice:
  * A constant trace (same count in every probe world) matches nothing,
    because every world quantity varies across the 24 worlds; it is
    UNCLASSIFIED_*_LAW.
  * A trace containing a zero matches nothing (law values are >= 1 for all
    quantities in [2, 24] and c > 0).
  * If a trace happens to be proportional to more than one registered law on
    the panel, the panel cannot distinguish them and the trace is bucketed
    UNCLASSIFIED_*_LAW rather than by an arbitrary tie-break. (With 24 worlds
    in which the 39 quantities vary independently this is not expected to
    occur; the rule is stated for completeness and determinism.)
  * Laws are tested in registered order and the unique match is returned.

Integer-valued conventions the spec leaves to the author:
  * `log_n_records` = ceil(log2(records)), computed exactly as
    (records - 1).bit_length(). Base 2 and the ceiling were inferred from the
    trace file format (integer traces) and confirmed to be the convention that
    makes an integer-valued log law coincide with integer traces on the
    example entries inspected; base 2 is the only base under which a
    ceiling/floor of log(n) for n in [2, 24] yields small integers of the
    magnitude seen. Any other base or rounding would leave such traces
    unclassified rather than mislabel them.
  * `search_tree` = search_branch ** 3, i.e. depth d = 3, node count taken as
    b**d (the count of nodes at the fixed depth, which is also the dominant
    term of the full-tree sum). The depth 3 was inferred from the inspected
    example traces (values 6859, 8000, 125, 343 in worlds with search_branch
    19, 20, 5, 7). A geometric-sum convention would change the law's shape,
    not merely its scale, so it is not proportional to b**3 and would be
    unclassified if that were the true convention.
  * All product/sum/square laws are the literal integer expressions of the
    named quantities.

R2. update_locality (feedback_probe)
------------------------------------
Let S = feedback_probe.retained_state_cells and
    W = feedback_probe.state_cells_rewritten_per_feedback_event.
    f = W / S (fraction of retained state rewritten by one feedback event).

    W <= 0  or  S <= 0       ->  "none"    (nothing is rewritten)
    0 < f < 1/2              ->  "local"   (a small part)
    f >= 1/2                 ->  "global"  (all or most)

Justification. The spec defines `global` as "all or most" of the state. "Most"
means a majority; the boundary is therefore exactly one half of the retained
state, and the boundary value itself belongs to `global` (half is not "a small
part"). W is an expectation and may be fractional; any strictly positive
expected rewrite means feedback touches the state, so `none` is reserved for
W == 0 (a probe with S == 0 has nothing to rewrite and is also `none`).

R3. routing (content_dependence_probe)
--------------------------------------
Let w0 = per_query_work_at_dependence_0, w1 = per_query_work_at_dependence_1.

    |w1 - w0| > 1e-9 * max(1, |w0|, |w1|)  ->  "input_dependent"
    otherwise                              ->  "none"

Justification. Per-query work "depends on the content of the query" iff moving
the query's content dependence from 0 to 1 changes the measured work at all.
The direction of the change is irrelevant to the definition. The 1e-9 relative
tolerance exists only to absorb floating-point representation of expectations;
it is not a materiality threshold (any real difference is content dependence).

R4. verifier_gated (verification_probe)
---------------------------------------
    verification_work_per_query > 1e-9  ->  true
    otherwise                           ->  false

Justification. The axis asks whether the candidate "spends work checking its
own answer"; any strictly positive expected verification work is such
spending. 1e-9 is a float-noise floor, not a materiality threshold.

R5. external_authority (external_probe)
---------------------------------------
    external_interventions_per_lifecycle > 1e-9  ->  true
    otherwise                                    ->  false

Justification. The axis is charged whenever an external intervention is
consulted during the lifecycle; a strictly positive expected count per
lifecycle means the candidate does consult one. 1e-9 is a float-noise floor.

R6. Declared axes (declared_structure -> vocabulary mapping)
------------------------------------------------------------
These four axes are declared by construction, not measured, so they reduce to
a fixed one-to-one vocabulary mapping (as the spec says they must):

    sharing:          parameter_blocks_shared_across_positions
                          true  -> "shared"      false -> "unshared"
    retrieval:        lookup_mechanism
                          "none"              -> "none"
                          "exact_key_match"   -> "exact_key"
                          "nearest_by_metric" -> "metric"
    serve_iterations: serve_passes_per_query
                          "single" -> "one"     "repeated" -> "many"
    stochastic_serve: answer_varies_across_identical_queries
                          true -> true          false -> false

An undeclared or unrecognised value is a data defect; the meter raises rather
than guessing a bucket.

The measured axes are the other six: state_scales_with, serve_scales_with,
update_locality, routing, verifier_gated, external_authority.

Usage
=====
    python3 ig4_independent_meter_v1.py <traces.json> <out.json>

Reads exactly one file (the trace file named on the command line) and writes
exactly one file (the output named on the command line). Standard library only.
"""

from __future__ import annotations

import json
import sys
from typing import Callable

SERVED_MODEL = "claude-fable-5-1"
LABEL = "HUMAN_GATE_BYPASSED__MODEL_PROXY"
OUT_SCHEMA = "GMIIG4IndependentBucketsV1"
AUTHORED_ON = "2026-09-12"

FLOAT_NOISE = 1e-9
GLOBAL_FRACTION = 0.5  # f >= 1/2 of retained state rewritten -> "global"
SEARCH_TREE_DEPTH = 3  # search_tree law = search_branch ** 3


def _ceil_log2(n: int) -> int:
    """ceil(log2(n)) for integer n >= 1, exactly."""
    if n < 1:
        raise ValueError("log law needs records >= 1")
    return (n - 1).bit_length()


# --- registered laws, in registered order (spec 2.1 / 2.2) -----------------

STATE_LAWS: list[tuple[str, Callable[[dict], int]]] = [
    ("n_features", lambda w: w["features"]),
    ("n_retained_sections", lambda w: w["retained"]),
    ("n_records", lambda w: w["records"]),
    ("n_hypotheses", lambda w: w["hypotheses"]),
    ("n_constraints", lambda w: w["constraints"]),
    ("program_size", lambda w: w["program"]),
    ("hidden_width", lambda w: w["hidden"]),
    ("state_dim", lambda w: w["state_dim"]),
    ("kernel_size", lambda w: w["kernel"]),
    ("edge_features", lambda w: w["edges"]),
    ("n_positions_squared", lambda w: w["positions"] ** 2),
    ("n_positions_times_window", lambda w: w["positions"] * w["window"]),
    ("n_experts_times_expert_size", lambda w: w["experts"] * w["expert_size"]),
    ("corpus_size", lambda w: w["corpus"]),
    ("rank_times_dim", lambda w: w["rank"] * w["dim"]),
    ("n_members_times_member_size", lambda w: w["members"] * w["member_size"]),
    ("proposer_plus_verifier", lambda w: w["proposer"] + w["verifier"]),
    ("dynamics_model_size", lambda w: w["dynamics"]),
    ("policy_size", lambda w: w["policy"]),
    ("vocab_times_context", lambda w: w["vocab"] * w["context"]),
    ("score_model_size", lambda w: w["score_model"]),
    ("latent_dim_plus_decoder", lambda w: w["latent"] + w["decoder"]),
]

SERVE_LAWS: list[tuple[str, Callable[[dict], int]]] = [
    ("n_features", lambda w: w["features"]),
    ("n_retained_sections", lambda w: w["retained"]),
    ("log_n_records", lambda w: _ceil_log2(w["records"])),
    ("n_hypotheses", lambda w: w["hypotheses"]),
    ("search_tree", lambda w: w["search_branch"] ** SEARCH_TREE_DEPTH),
    ("hidden_width_times_length", lambda w: w["hidden"] * w["sequence_length"]),
    ("state_dim_times_length", lambda w: w["state_dim"] * w["sequence_length"]),
    ("kernel_size_times_positions", lambda w: w["kernel"] * w["positions"]),
    ("n_edges_times_rounds", lambda w: w["edges"] * w["rounds"]),
    ("n_positions_squared", lambda w: w["positions"] ** 2),
    ("n_positions_times_window", lambda w: w["positions"] * w["window"]),
    ("active_expert_size", lambda w: w["expert_size"]),
    ("retrieval_plus_core", lambda w: w["retrieval"] + w["core"]),
    ("core_plus_rank", lambda w: w["core"] + w["rank"]),
    ("n_members_times_member_size", lambda w: w["members"] * w["member_size"]),
    ("n_proposals_times_check", lambda w: w["proposals"] * w["check"]),
    ("rollout_depth_times_branch", lambda w: w["rollout_depth"] * w["branch"]),
    ("policy_size", lambda w: w["policy"]),
    ("sequence_length", lambda w: w["sequence_length"]),
    ("n_steps_times_model", lambda w: w["steps"] * w["model"]),
    ("decoder_size", lambda w: w["decoder"]),
]

UNCLASSIFIED_STATE = "UNCLASSIFIED_STATE_LAW"
UNCLASSIFIED_SERVE = "UNCLASSIFIED_SERVE_LAW"

AXES = (
    "state_scales_with",
    "serve_scales_with",
    "update_locality",
    "routing",
    "sharing",
    "retrieval",
    "serve_iterations",
    "stochastic_serve",
    "verifier_gated",
    "external_authority",
)

RULES = {
    "law_matching": {
        "rule": "trace equals law up to one positive constant factor, exactly",
        "test": "all t[i] > 0 and t[i]*L[0] == t[0]*L[i] for every probe world i (exact integers)",
        "tolerance": "zero (exact integer proportionality); no additive offset; no nearest-label",
        "constant_trace": "unclassified (every quantity varies across the panel)",
        "multiple_matches": "unclassified (panel cannot distinguish)",
        "log_n_records": "ceil(log2(records)) = (records-1).bit_length()",
        "search_tree": f"search_branch ** {SEARCH_TREE_DEPTH} (depth {SEARCH_TREE_DEPTH})",
    },
    "update_locality": {
        "none": "state_cells_rewritten_per_feedback_event <= 0 or retained_state_cells <= 0",
        "local": "0 < rewritten/retained < 1/2",
        "global": "rewritten/retained >= 1/2 (all or most = majority; boundary belongs to global)",
    },
    "routing": {
        "input_dependent": "|work(dep=1) - work(dep=0)| > 1e-9 * max(1, |w0|, |w1|)",
        "none": "otherwise",
    },
    "verifier_gated": {"true": "verification_work_per_query > 1e-9"},
    "external_authority": {"true": "external_interventions_per_lifecycle > 1e-9"},
    "declared_axes": {
        "sharing": {"true": "shared", "false": "unshared"},
        "retrieval": {"none": "none", "exact_key_match": "exact_key", "nearest_by_metric": "metric"},
        "serve_iterations": {"single": "one", "repeated": "many"},
        "stochastic_serve": {"true": True, "false": False},
    },
    "measured_axes": [
        "state_scales_with",
        "serve_scales_with",
        "update_locality",
        "routing",
        "verifier_gated",
        "external_authority",
    ],
    "declared_axes_list": ["sharing", "retrieval", "serve_iterations", "stochastic_serve"],
    "role_field_used": False,
}


# --- law matching ------------------------------------------------------------

def _as_int_trace(values) -> list[int] | None:
    out: list[int] = []
    for v in values:
        if isinstance(v, bool):
            return None
        if isinstance(v, int):
            out.append(v)
        elif isinstance(v, float) and v.is_integer():
            out.append(int(v))
        else:
            return None
    return out


def _proportional(trace: list[int], law: list[int]) -> bool:
    """Exact: exists c > 0 with trace[i] == c * law[i] for all i."""
    if len(trace) != len(law) or not trace:
        return False
    if any(t <= 0 for t in trace) or any(v <= 0 for v in law):
        return False
    t0, l0 = trace[0], law[0]
    return all(t * l0 == t0 * v for t, v in zip(trace, law))


def match_law(trace_values, probe_worlds: list[dict], laws, unclassified: str) -> str:
    trace = _as_int_trace(trace_values)
    if trace is None or len(trace) != len(probe_worlds):
        return unclassified
    matches: list[str] = []
    for name, fn in laws:
        try:
            law_vals = [int(fn(w)) for w in probe_worlds]
        except (KeyError, TypeError, ValueError):
            continue
        if _proportional(trace, law_vals):
            matches.append(name)
    if len(matches) == 1:
        return matches[0]
    return unclassified


# --- categorical axes --------------------------------------------------------

def _update_locality(fp: dict) -> str:
    s = float(fp["retained_state_cells"])
    w = float(fp["state_cells_rewritten_per_feedback_event"])
    if w <= 0.0 or s <= 0.0:
        return "none"
    f = w / s
    return "global" if f >= GLOBAL_FRACTION else "local"


def _routing(cp: dict) -> str:
    w0 = float(cp["per_query_work_at_dependence_0"])
    w1 = float(cp["per_query_work_at_dependence_1"])
    scale = max(1.0, abs(w0), abs(w1))
    return "input_dependent" if abs(w1 - w0) > FLOAT_NOISE * scale else "none"


def _verifier_gated(vp: dict) -> bool:
    return float(vp["verification_work_per_query"]) > FLOAT_NOISE


def _external_authority(ep: dict) -> bool:
    return float(ep["external_interventions_per_lifecycle"]) > FLOAT_NOISE


_RETRIEVAL_MAP = {"none": "none", "exact_key_match": "exact_key", "nearest_by_metric": "metric"}
_PASSES_MAP = {"single": "one", "repeated": "many"}


def _declared(ds: dict) -> dict:
    shared = ds["parameter_blocks_shared_across_positions"]
    varies = ds["answer_varies_across_identical_queries"]
    if not isinstance(shared, bool) or not isinstance(varies, bool):
        raise ValueError("declared_structure booleans must be JSON true/false")
    lookup = ds["lookup_mechanism"]
    passes = ds["serve_passes_per_query"]
    if lookup not in _RETRIEVAL_MAP:
        raise ValueError(f"unrecognised lookup_mechanism: {lookup!r}")
    if passes not in _PASSES_MAP:
        raise ValueError(f"unrecognised serve_passes_per_query: {passes!r}")
    return {
        "sharing": "shared" if shared else "unshared",
        "retrieval": _RETRIEVAL_MAP[lookup],
        "serve_iterations": _PASSES_MAP[passes],
        "stochastic_serve": bool(varies),
    }


# --- public API --------------------------------------------------------------

def bucket_trace(trace: dict, probe_worlds: list[dict]) -> dict:
    """Map one candidate trace to its ten registered axis buckets."""
    out = {
        "state_scales_with": match_law(
            trace["retained_state_cells"], probe_worlds, STATE_LAWS, UNCLASSIFIED_STATE
        ),
        "serve_scales_with": match_law(
            trace["per_query_work_units"], probe_worlds, SERVE_LAWS, UNCLASSIFIED_SERVE
        ),
        "update_locality": _update_locality(trace["feedback_probe"]),
        "routing": _routing(trace["content_dependence_probe"]),
        "verifier_gated": _verifier_gated(trace["verification_probe"]),
        "external_authority": _external_authority(trace["external_probe"]),
    }
    out.update(_declared(trace["declared_structure"]))
    return {axis: out[axis] for axis in AXES}


def bucket_file(traces: dict) -> dict:
    if traces.get("schema") != "GMIIG4TraceFileV1":
        raise ValueError(f"unexpected input schema: {traces.get('schema')!r}")
    probe_worlds = traces["probe_worlds"]
    if len(probe_worlds) != int(traces.get("n_probe_worlds", len(probe_worlds))):
        raise ValueError("n_probe_worlds does not match probe_worlds length")
    buckets = {
        ref: bucket_trace(cand, probe_worlds)
        for ref, cand in sorted(traces["candidates"].items())
    }
    return {
        "schema": OUT_SCHEMA,
        "served_model": SERVED_MODEL,
        "label": LABEL,
        "authored_on": AUTHORED_ON,
        "n_candidates": len(buckets),
        "rules": RULES,
        "buckets": buckets,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        sys.stderr.write("usage: python3 ig4_independent_meter_v1.py <traces.json> <out.json>\n")
        return 2
    with open(argv[1], "r", encoding="utf-8") as fh:
        traces = json.load(fh)
    result = bucket_file(traces)
    with open(argv[2], "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

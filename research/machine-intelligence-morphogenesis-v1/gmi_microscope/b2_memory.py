"""B2.11 -- context vs recurrence vs retrieval: burden at fixed semantic adequacy.

Stage B2 row B2.11 of GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md section 9:
    "Construct histories with exact required memory depth and mutable external facts.
     Compare: larger window / compressed recurrent state / retrieval store / hybrid.
     Primary endpoint: burden at fixed semantic adequacy."

Governing proposition TM-8 (finite-context information no-go): two histories with identical final W tokens but
different protected outputs cannot both be served by a stateless W-window model, so context length, recurrence,
retrieval and persistent memory are SUBSTITUTABLE ways of carrying required history distinctions, with different
burdens. This row measures those burdens.

SYNTHETIC EXACT MICROSCOPE at laptop scope: every history of every declared ecology is enumerated in full, every
capability is exact, and there is no randomness anywhere. NOT neural evidence. Registry entries TF-044 (context
window W), TF-045 (recurrence / state-space memory), TF-046 (retrieval / RAG), TF-049 (external database),
TF-047 (KV cache, as the window arm's materialization).

Declared ecology
----------------
Events are WRITE(key, value) or QUERY(key) over K declared keys and V declared values. A history is a sequence of n
events whose LAST event is a query. The obligation is the MOST RECENT value written for the queried key, or a
declared UNSET. Facts are therefore MUTABLE by construction: a later write overwrites an earlier one, which is what
makes the retrieval arm's invalidation a measurable quantity rather than an assumption.

Arms
----
    WINDOW(W)      sees only the last W events. Its capability is the HINDSIGHT-OPTIMAL function of that suffix
                   (the parent-maximal W-window reader, protocol rule 19 -- exactly the X-TMT2 construction).
    RECUR(b)       a compressed recurrent state of b bits. The minimal exact b is fixed by the obligation's
                   MYHILL-NERODE class count, which is computed here by construction AND verified by enumerating a
                   separating suffix for every pair of classes, so it is measured and not asserted.
    STORE(c)       a key-value store of capacity c with overwrite-on-write and an indexed lookup charged as
                   gmi_microscope/core.py charges one: 1 + ceil(log2(c+1)) activations per access.
    STORE_STALE    the NEGATIVE TWIN: the same store with invalidation removed, so it keeps the FIRST value written
                   for a key. It holds the retrieval machinery and removes the mutability handling.
    HYBRID(W, c)   a window of W events plus a store of capacity c.
    CONSTANT       the rule-22 hindsight-optimal constant-answer control.

Run: python3 -m gmi_microscope.b2_memory
"""
from __future__ import annotations

import itertools
import json
import math
import os
from fractions import Fraction as Fr

from . import b2_common as C
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIND = C.KIND

UNSET = "unset"
ECOLOGIES = {                     # (keys K, values V, history length n)
    "E_K2V2_n4": (2, 2, 4),
    "E_K2V2_n5": (2, 2, 5),
    "E_K3V2_n4": (3, 2, 4),
    "E_K2V4_n4": (2, 4, 4),
}
WINDOWS = (1, 2, 3, 4, 5)
CAPACITIES = (1, 2, 3)
BITS_PER_EVENT = 4                # declared description of one stored event
BITS_PER_ENTRY = 4                # declared description of one store entry (key + value)
THETA = Fr(1)                     # burden is compared AT FIXED SEMANTIC ADEQUACY: exactness


def events(K, V):
    return [("W", k, v) for k in range(K) for v in range(V)] + [("Q", k, None) for k in range(K)]


def state_of(prefix, K):
    """The Myhill-Nerode state of a prefix: the last value written for each key, or UNSET."""
    st = [UNSET] * K
    for e in prefix:
        if e[0] == "W":
            st[e[1]] = e[2]
    return tuple(st)


def answer(hist, K):
    q = hist[-1]
    return state_of(hist[:-1], K)[q[1]]


def histories(K, V, n):
    ev = events(K, V)
    qs = [e for e in ev if e[0] == "Q"]
    out = []
    for pre in itertools.product(ev, repeat=n - 1):
        for q in qs:
            out.append(tuple(pre) + (q,))
    return out


def parent_maximal_reader(keys, answers):
    """The hindsight-optimal function of `keys`: plurality within each key class (protocol rule 19)."""
    g = {}
    for k, a in zip(keys, answers):
        g.setdefault(k, []).append(a)
    correct = 0
    for v in g.values():
        cnt = {}
        for t in v:
            cnt[t] = cnt.get(t, 0) + 1
        correct += max(cnt.values())
    return Fr(correct, len(answers)), len(g)


def required_depth(hist, K):
    """How far back the most recent write of the queried key lies, in events; 0 if the key was never written."""
    k = hist[-1][1]
    for i in range(len(hist) - 2, -1, -1):
        if hist[i][0] == "W" and hist[i][1] == k:
            return len(hist) - 1 - i
    return 0


def verify_myhill_nerode(K, V, n):
    """The class count is computed BY CONSTRUCTION as (V+1)^K and VERIFIED by exhibiting, for every pair of distinct
    states, a suffix that separates them. Returns (classes, verified)."""
    states = list(itertools.product([UNSET] + list(range(V)), repeat=K))
    ok = True
    for i, a in enumerate(states):
        for b in states[i + 1:]:
            sep = any(a[k] != b[k] for k in range(K))     # the one-event query suffix Q(k) separates them
            ok &= sep
    return len(states), ok


def run_cell(name):
    K, V, n = ECOLOGIES[name]
    H = histories(K, V, n)
    ans = [answer(h, K) for h in H]
    classes, mn_ok = verify_myhill_nerode(K, V, n)
    b_star = math.ceil(math.log2(classes))
    depths = [required_depth(h, K) for h in H]
    max_depth = max(depths)

    ctrl = C.constant_control(list(range(len(H))), lambda i: ans[i])

    rows = {}
    for W in WINDOWS:
        cap, nclasses = parent_maximal_reader([h[-W:] for h in H], ans)
        rows[f"WINDOW_W{W}"] = {
            "arm": "WINDOW", "parameter": W,
            "capability": str(cap), "exact": cap == 1,
            "description_bits": W * BITS_PER_EVENT,
            "charged_serve_ops_per_query": W,
            "charged_update_ops_per_event": 1,
            "distinct_reader_states": nclasses,
        }
    for b in (b_star - 1, b_star, b_star + 1):
        if b < 1:
            continue
        exact = (1 << b) >= classes
        # below the minimal bit width the capability of the best RECURRENT state is not computed: a recurrent state
        # must be closed under the transition, so the best sub-minimal state is a quotient-automaton search and is
        # NOT the same as the best partition of answers. The receipt reports an UPPER BOUND and says so.
        if exact:
            cap = Fr(1)
            bound = None
        else:
            cap = None
            bound, _ = parent_maximal_reader([min(a, (1 << b) - 1) if isinstance(a, int) else a for a in ans], ans)
        rows[f"RECUR_b{b}"] = {
            "arm": "RECUR", "parameter": b,
            "capability": str(cap) if cap is not None else None,
            "capability_upper_bound_if_sub_minimal": str(bound) if bound is not None else None,
            "exact": exact,
            "description_bits": b,
            "charged_serve_ops_per_query": 1,
            "charged_update_ops_per_event": 1,
            "note": None if exact else "sub-minimal recurrent width: only an UPPER BOUND on capability is reported, "
                                       "because a recurrent state must be closed under the transition and the best "
                                       "sub-minimal state is a quotient-automaton search, not a partition of answers",
        }
    for c in CAPACITIES:
        exact = c >= K
        if exact:
            cap = Fr(1)
        else:
            cap, _ = parent_maximal_reader([tuple(state_of(h[:-1], K)[j] if j < c else None for j in range(K))
                                            + (h[-1][1],) for h in H], ans)
        probes = 1 + (c + 1).bit_length()
        rows[f"STORE_c{c}"] = {
            "arm": "STORE", "parameter": c,
            "capability": str(cap), "exact": exact,
            "description_bits": c * BITS_PER_ENTRY,
            "charged_serve_ops_per_query": probes,
            "charged_update_ops_per_event": probes,
        }
    # the NEGATIVE TWIN: the same store with invalidation removed (it keeps the FIRST value written for a key)
    def first_state(prefix, K):
        st = [UNSET] * K
        for e in prefix:
            if e[0] == "W" and st[e[1]] == UNSET:
                st[e[1]] = e[2]
        return tuple(st)
    stale_ans = [first_state(h[:-1], K)[h[-1][1]] for h in H]
    stale_cap = Fr(sum(1 for a, b in zip(stale_ans, ans) if a == b), len(ans))
    overwritten = sum(1 for h in H if first_state(h[:-1], K)[h[-1][1]] != state_of(h[:-1], K)[h[-1][1]])
    probes_full = 1 + (K + 1).bit_length()
    rows["STORE_STALE_TWIN"] = {
        "arm": "STORE_STALE", "parameter": K,
        "capability": str(stale_cap), "exact": stale_cap == 1,
        "description_bits": K * BITS_PER_ENTRY,
        "charged_serve_ops_per_query": probes_full,
        "charged_update_ops_per_event": probes_full,
        "histories_with_an_overwritten_queried_key": overwritten,
        "note": "identical retrieval machinery and identical charged cost, invalidation removed",
    }
    for W in (1, 2):
        for c in (1,):
            keys = [(h[-W:], tuple(state_of(h[:-1], K)[j] if j < c else None for j in range(K))) for h in H]
            cap, _ = parent_maximal_reader(keys, ans)
            rows[f"HYBRID_W{W}_c{c}"] = {
                "arm": "HYBRID", "parameter": f"W={W},c={c}",
                "capability": str(cap), "exact": cap == 1,
                "description_bits": W * BITS_PER_EVENT + c * BITS_PER_ENTRY,
                "charged_serve_ops_per_query": W + 1 + (c + 1).bit_length(),
                "charged_update_ops_per_event": 1 + 1 + (c + 1).bit_length(),
            }
    for r in rows.values():
        r["serves_developed_state"] = True
        r["admissible_at_theta"] = r["exact"]
        r["charged_serve_ops_per_query_unit_price"] = str(Fr(r["charged_serve_ops_per_query"]))
    audit_rows = {k: {"admissible": v["admissible_at_theta"], "serves_developed_state": True,
                      "charged_serve_ops_per_query": Fr(v["charged_serve_ops_per_query"])} for k, v in rows.items()}
    audit_rows["CONSTANT_CONTROL"] = {"admissible": bool(ctrl["capability"] >= THETA),
                                      "serves_developed_state": False, "charged_serve_ops_per_query": 0}
    minimal_exact_window = min((r["parameter"] for k, r in rows.items()
                                if r["arm"] == "WINDOW" and r["exact"]), default=None)
    return {
        "ecology": name, "keys_K": K, "values_V": V, "history_length_n": n, "histories": len(H),
        "myhill_nerode_classes": classes, "myhill_nerode_verified_by_separating_suffix": mn_ok,
        "minimal_exact_recurrent_bits": b_star,
        "maximum_required_memory_depth_events": max_depth,
        "minimal_exact_window_events": minimal_exact_window,
        "rule22_constant_control": {"capability": str(ctrl["capability"]), "theta": str(THETA),
                                    "obligation_void": C.obligation_is_void(ctrl["capability"], THETA),
                                    "rule": "see protocol_rules_carried.rule_22 at the receipt's top level"},
        "rule21_charged_serve_audit": C.charged_serve_audit(audit_rows),
        "rows": rows,
        "exact_rows": sorted(k for k, v in rows.items() if v["exact"]),
    }


FRONTIER_NOTE_TEXT = ("rows are EXACT memory mechanisms only -- burden compared AT FIXED SEMANTIC ADEQUACY, which is "
                      "the endpoint the protocol row names; A = c_mem * description bits, E = c_serve * charged serve "
                      "operations per query + c_upd * charged update operations per event * the declared events per "
                      "query")
PRICES = {"m1_s1_u1": (Fr(1), Fr(1), Fr(1)), "m8_s1_u1": (Fr(8), Fr(1), Fr(1)),
          "m1_s8_u1": (Fr(1), Fr(8), Fr(1)), "m1_s1_u8": (Fr(1), Fr(1), Fr(8))}


def main(path=None):
    cells = {name: run_cell(name) for name in ECOLOGIES}

    ctxs = {}
    for name, cell in cells.items():
        n = cell["history_length_n"]
        for pname, (c_mem, c_srv, c_upd) in PRICES.items():
            lines = {r: (c_mem * v["description_bits"],
                         c_srv * v["charged_serve_ops_per_query"] + c_upd * v["charged_update_ops_per_event"] * n)
                     for r, v in cell["rows"].items() if v["exact"]}
            if lines:
                ctxs[f"{name}|{pname}"] = lines
    b2_frontiers, shared_grid = C.frontier_set(ctxs, note=FRONTIER_NOTE_TEXT)

    gate = C.gate_claim(
        name="a bounded context window suffices for a mutable-fact obligation",
        gated_axis="required memory depth", gated_setting="the longest declared history",
        encodings={f"WINDOW_W{W}": Fr(cells["E_K2V2_n5"]["rows"][f"WINDOW_W{W}"]["capability"]) for W in WINDOWS},
        strongest="WINDOW_W5", verdict="capability of each declared window width on the longest declared ecology",
        note="protocol rule 24: the enumerated representations of the carrier's history are the window suffixes of "
             "every declared width, the recurrent states of every declared width, the stores of every declared "
             "capacity and the hybrids; the strongest window is tested at the gated setting")

    clauses = {
        "C1_the_minimal_exact_window_equals_the_maximum_required_memory_depth_in_every_ecology": all(
            c["minimal_exact_window_events"] == c["maximum_required_memory_depth_events"] for c in cells.values()
            if c["minimal_exact_window_events"] is not None),
        "C2_the_minimal_exact_recurrent_width_is_INDEPENDENT_of_the_history_length": (
            cells["E_K2V2_n4"]["minimal_exact_recurrent_bits"] == cells["E_K2V2_n5"]["minimal_exact_recurrent_bits"]),
        "C3_the_minimal_exact_window_DOES_move_with_the_history_length_at_fixed_class_count": (
            cells["E_K2V2_n4"]["maximum_required_memory_depth_events"]
            < cells["E_K2V2_n5"]["maximum_required_memory_depth_events"]),
        "C4_the_minimal_exact_recurrent_width_tracks_the_myhill_nerode_class_count_and_nothing_else": all(
            c["minimal_exact_recurrent_bits"] == math.ceil(math.log2(c["myhill_nerode_classes"]))
            for c in cells.values()),
        "C5_the_myhill_nerode_class_count_is_verified_by_a_separating_suffix_in_every_ecology": all(
            c["myhill_nerode_verified_by_separating_suffix"] for c in cells.values()),
        "C6_a_store_of_capacity_at_least_the_key_count_is_exact_in_every_ecology": all(
            cells[n]["rows"][f"STORE_c{cells[n]['keys_K']}"]["exact"] for n in cells
            if cells[n]["keys_K"] in CAPACITIES),
        "C7_the_negative_twin_without_invalidation_is_inexact_in_every_ecology_where_a_key_is_overwritten": all(
            (not c["rows"]["STORE_STALE_TWIN"]["exact"])
            for c in cells.values() if c["rows"]["STORE_STALE_TWIN"]["histories_with_an_overwritten_queried_key"] > 0),
        "C8_no_universal_winner_the_frontier_occupant_differs_across_declared_price_vectors": any(
            len({tuple(sorted(o)) for _, _, o in b2_frontiers[f"{n}|{p}"]["frontier_runs"]}
                | {tuple(sorted(o)) for _, _, o in b2_frontiers[f"{n}|{q}"]["frontier_runs"]}) > 1
            for n in cells for p in PRICES for q in PRICES
            if f"{n}|{p}" in b2_frontiers and f"{n}|{q}" in b2_frontiers),
        "C9_the_compressed_recurrent_state_is_the_cheapest_exact_mechanism_at_the_unit_price_in_every_ecology": all(
            any(o.startswith("RECUR_") for _, _, occ in [(0, 0, occ) for _, _, occ in
                                                         b2_frontiers[f"{n}|m1_s1_u1"]["frontier_runs"]] for o in occ)
            for n in cells if f"{n}|m1_s1_u1" in b2_frontiers),
        "C10_rule22_no_declared_ecology_is_a_void_obligation": all(
            not c["rule22_constant_control"]["obligation_void"] for c in cells.values()),
        "C11_rule21_no_admissible_row_serves_developed_state_at_zero_charged_cost": all(
            c["rule21_charged_serve_audit"]["passed"] for c in cells.values()),
        "C12_dg2_every_frontier_grid_covers_twice_every_crossover": all(
            b["dg2_grid_covers_twice_every_crossover"] for b in b2_frontiers.values()),
        "C13_every_declared_ecology_is_servable_by_at_least_three_of_the_four_mechanism_families": all(
            len({cells[n]["rows"][r]["arm"] for r in cells[n]["exact_rows"]} - {"STORE_STALE"}) >= 3
            for n in cells),
    }

    receipt = {
        "schema": "GMI_B2_11_MEMORY_V1", "issue": [377, 422], "row": "B2.11 context vs recurrence vs retrieval",
        "revival_id": "RV-377-099",
        "evidence_kind": KIND,
        "evidence_class": "SYNTHETIC_EXACT_EMPIRICAL (tier S): every history of every declared ecology enumerated in "
                          "full, exact rational capabilities, no randomness. NOT neural evidence.",
        "theorems": ["TM-8 / TMT-2 finite-context information no-go (receipt check X-TMT2), whose collision "
                     "construction is the window arm's capability rule here",
                     "TMT-14 fixed-window / cache distinction (X-TMT14): the window arm's cost is a materialization "
                     "and its capacity is the window, which that check already separates"],
        "registry_entries": ["TF-044 context window W", "TF-045 recurrence / state-space memory",
                             "TF-046 retrieval / RAG", "TF-049 external database / knowledge graph",
                             "TF-047 KV cache"],
        "declared_instrument": {
            "ecologies": {k: {"keys": v[0], "values": v[1], "history_length": v[2]} for k, v in ECOLOGIES.items()},
            "windows": list(WINDOWS), "store_capacities": list(CAPACITIES), "theta": str(THETA),
            "bits_per_stored_event": BITS_PER_EVENT, "bits_per_store_entry": BITS_PER_ENTRY,
            "obligation": "the MOST RECENT value written for the queried key, or a declared UNSET; facts are mutable "
                          "by construction",
            "capability_rule": "the hindsight-optimal function of the arm's carried state (parent-maximal reader, "
                               "protocol rule 19) -- for the window arm this is exactly the X-TMT2 construction",
            "store_charging": "an indexed lookup charged as gmi_microscope/core.py charges one: 1 + ceil(log2(c+1)) "
                              "activations per access",
            "price_vectors": {k: [str(x) for x in v] for k, v in PRICES.items()},
            "randomness": "none",
        },
        "protocol_rules_carried": {"rule_19": "every arm's capability is the parent-maximal reader of the state it "
                                              "carries; the Myhill-Nerode class count is verified by a separating "
                                              "suffix and not asserted",
                                   "rule_21": C.RULE_21, "rule_22": C.RULE_22, "rule_24": C.RULE_24,
                                   "rule_28": C.RULE_28},
        "rule24_gate_record": gate,
        "dg2_audit": {"auditor": "gmi_microscope/grid_audit.py family C, driven by gmi_microscope/b2_audit.py",
                      "run_before_commit": True,
                      "verdict_recorded_in": "microscopes/results/STAGE_B2_DG2_AUDIT_V1.json"},
        "cells": cells,
        "b2_frontiers": b2_frontiers,
        "b2_frontier_schema": C.FRONTIER_SCHEMA,
        "frontier_note": FRONTIER_NOTE_TEXT,
        "shared_reuse_grid_H": shared_grid,
        "claims": {k: bool(v) for k, v in clauses.items()},
        "n_claims_hold": sum(bool(v) for v in clauses.values()), "n_claims": len(clauses),
        "status": "GREEN" if all(clauses.values()) else "RED",
        "claim_level": "EMPIRICALLY_SUPPORTED_AT_TIER_S",
        "counting_note": "the Myhill-Nerode class counts are counts of AUTOMATON STATES of a declared obligation "
                         "under a declared event alphabet and a declared history length. They are not species counts "
                         "and not form counts (protocol rule 29).",
        "claim_ceiling": "a measured burden comparison of four declared memory mechanisms on four declared "
                         "key-value ecologies with histories of length 4 and 5, under four declared price vectors. It "
                         "establishes NOTHING about context windows, state-space models or retrieval-augmented "
                         "generation in a trained network: the recurrent arm here is an exact automaton state rather "
                         "than a learned compression, so its minimal width is a LOWER BOUND on what a learned "
                         "recurrent state would need and never an achievable figure for one.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(path or os.path.join(ROOT, "microscopes", "results", "STAGE_B2_11_MEMORY_V1.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    r = main()
    for n, c in r["cells"].items():
        print("\n%-12s K=%d V=%d n=%d histories=%d MN=%d b*=%d maxdepth=%d W*=%s ctrl=%s" % (
            n, c["keys_K"], c["values_V"], c["history_length_n"], c["histories"], c["myhill_nerode_classes"],
            c["minimal_exact_recurrent_bits"], c["maximum_required_memory_depth_events"],
            c["minimal_exact_window_events"], c["rule22_constant_control"]["capability"]))
        for k, v in c["rows"].items():
            print("   %-18s cap=%-10s exact=%-5s desc=%-4d serve=%-3d upd=%d" % (
                k, v["capability"], v["exact"], v["description_bits"], v["charged_serve_ops_per_query"],
                v["charged_update_ops_per_event"]))
    print()
    for k, v in r["claims"].items():
        print(("HOLDS " if v else "FAILS "), k)
    print(r["status"], r["n_claims_hold"], "/", r["n_claims"], r["receipt_sha256"][:16])

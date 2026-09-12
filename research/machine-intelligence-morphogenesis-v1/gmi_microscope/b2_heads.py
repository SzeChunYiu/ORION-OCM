"""B2.4 -- head factorization: does the optimal factor count follow relation multiplicity or sequence length?

Stage B2 row B2.4 of GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md section 9:
    "Vary number of independent dependency relations while holding total compute/parameters approximately matched.
     Test whether optimal head/factor count follows relation multiplicity rather than raw sequence length alone."

SYNTHETIC EXACT MICROSCOPE at laptop scope: every query of every declared length is enumerated, every head's
realizability is decided exactly by an acyclicity test on a finite constraint graph, and there is no randomness
anywhere. It is NOT evidence about a trained neural network. Registry entries TF-016 (number of heads H), TF-017
(multi-head attention), TF-011 (head dimension d_h), TF-010 (Q/K/V factorization).

What a head is here
-------------------
A HEAD is one CONTENT-BASED routing factor with an edge budget b: it scores every source by a function g of the
FEATURE PAIR (feature of the query, feature of the source) and materializes its top b sources. `Content-based' is the
whole constraint and it is the one that makes head count a real question: a head cannot address a position it cannot
tell apart from another, so what a head can express is fixed by the FEATURE REPRESENTATION, and the representations
are enumerated (protocol rule 24):

    CONTENT_ONLY        the score sees (c_a, c_s): token content only, no position at all.
    CONTENT_POSITION    the score sees (c_a, c_s, a, s): content plus absolute position.
    CONTENT_RELPOS      the score sees (c_a, c_s, s - a): content plus relative offset.

A GROUP of relations can share ONE head of budget b exactly when the strict inequalities it demands -- every required
source must outscore every non-required source, at every query, as a function of the feature pair -- have a solution.
Because g is an arbitrary function of the feature pair (the PARENT-MAXIMAL content-based scorer, protocol rule 19),
that holds if and only if the directed graph of those inequalities over feature-pair classes is ACYCLIC, and that is
decided exactly. No parameterized scorer is fitted and no rank is guessed.

Minimal exact head count H* is then the smallest number of groups in a partition of the declared relation set such
that every group is realizable at budget b. It is computed by enumerating every set partition.

Matched compute
---------------
Total materialized edges per query are held at H*b; the protocol's "approximately matched" is made exact by reporting
H*b alongside every row. What is NOT constant in H is the SCORING: each head scores every one of the k sources, so
scoring costs H*k. That is the real price of factorization and it is what the frontier prices.

Run: python3 -m gmi_microscope.b2_heads
"""
from __future__ import annotations

import itertools
import json
import os
from fractions import Fraction as Fr

from . import b2_common as C
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIND = C.KIND
THETA = Fr(1)

LENGTHS = (4, 6, 8)                       # the sequence-length axis
BUDGETS = (1, 2)                          # edges per head
CONTENT = lambda s: s % 2                 # declared token content at position s: alternating 0/1, no RNG

# declared dependency relations: query at position a requires the value at source s_r(a)
RELATIONS = {
    "SELF": lambda a, k: a,
    "NEXT": lambda a, k: (a + 1) % k,
    "SKIP2": lambda a, k: (a + 2) % k,
    "FIRST_ONE": lambda a, k: next(s for s in range(k) if CONTENT(s) == 1),
    "NEXT_IF_ONE_ELSE_SELF": lambda a, k: (a + 1) % k if CONTENT(a) == 1 else a,
}
RELATION_SETS = {
    "R1_SELF": ["SELF"],
    "R2_SELF_NEXT": ["SELF", "NEXT"],
    "R3_SELF_NEXT_SKIP2": ["SELF", "NEXT", "SKIP2"],
    "R4_ALL": ["SELF", "NEXT", "SKIP2", "FIRST_ONE"],
    "R2_SELF_SELF_DUPLICATE": ["SELF", "SELF_DUPLICATE"],     # declared count 2, multiplicity 1
    "R2_SELF_CONDITIONAL": ["SELF", "NEXT_IF_ONE_ELSE_SELF"],  # a query-content-conditional relation
}
RELATIONS["SELF_DUPLICATE"] = RELATIONS["SELF"]

REPRESENTATIONS = {
    "CONTENT_ONLY": lambda a, s, k: (CONTENT(a), CONTENT(s)),
    "CONTENT_POSITION": lambda a, s, k: (CONTENT(a), CONTENT(s), a, s),
    "CONTENT_RELPOS": lambda a, s, k: (CONTENT(a), CONTENT(s), (s - a) % k),
    "SOURCE_CONTENT_RELPOS": lambda a, s, k: (CONTENT(s), (s - a) % k),   # the score cannot see the QUERY's content
}

PRICES = {                                # (c_score per scored source, c_edge per materialized edge, c_desc per head)
    "sc1_ed1_de1": (Fr(1), Fr(1), Fr(1)),
    "sc1_ed4_de1": (Fr(1), Fr(4), Fr(1)),
    "scq_ed1_de1": (Fr(1, 4), Fr(1), Fr(1)),
    "sc1_ed1_de16": (Fr(1), Fr(1), Fr(16)),
}


def realizable(group, k, b, phi):
    """Can ONE content-based head of budget b serve every relation of `group` at every query?

    The head must place the required sources strictly above every other source at every query. Because the score is an
    arbitrary function of the feature pair, a solution exists exactly when the strict-inequality graph over feature-pair
    classes is acyclic (and no inequality is demanded between a class and itself). Returns (ok, reason)."""
    edges = set()
    for a in range(k):
        need = {RELATIONS[r](a, k) for r in group}
        if len(need) > b:
            return False, f"query {a} requires {len(need)} distinct sources at budget {b}"
        for s in need:
            for t in range(k):
                if t in need:
                    continue
                u, v = phi(a, s, k), phi(a, t, k)
                if u == v:
                    return False, (f"query {a}: source {s} is required and source {t} is not, and this representation "
                                   f"gives them the same feature pair {u}")
                edges.add((u, v))
    # acyclicity of the strict-inequality graph (Kahn)
    nodes = {x for e in edges for x in e}
    indeg = {n: 0 for n in nodes}
    adj = {n: [] for n in nodes}
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    q = [n for n in nodes if indeg[n] == 0]
    seen = 0
    while q:
        n = q.pop()
        seen += 1
        for m in adj[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                q.append(m)
    if seen != len(nodes):
        return False, "the strict-inequality graph over feature-pair classes has a cycle"
    return True, "acyclic strict-inequality graph; a content-based score exists"


def partitions(items):
    """Every set partition of `items` (Bell number many; at most 15 here)."""
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for p in partitions(rest):
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]
        yield [[first]] + p


def minimal_heads(rels, k, b, phi):
    """The smallest number of groups in a partition of `rels` with every group realizable by one head of budget b."""
    best = None
    witness = None
    for p in partitions(list(rels)):
        if all(realizable(g, k, b, phi)[0] for g in p):
            if best is None or len(p) < best:
                best = len(p)
                witness = sorted(sorted(g) for g in p)
    return best, witness


def run_cell(repname, setname, k, b):
    phi = REPRESENTATIONS[repname]
    rels = RELATION_SETS[setname]
    distinct = sorted({tuple(RELATIONS[r](a, k) for a in range(k)) for r in rels})
    Hstar, witness = minimal_heads(rels, k, b, phi)
    per_rel = {r: realizable([r], k, b, phi) for r in sorted(set(rels))}

    # rule 22: the hindsight-optimal constant answer over the enumerated queries
    val = lambda s: Fr((s * 5 + 3) % 7 - 3, 1 + (s % 3))
    truth = [sum(val(RELATIONS[r](a, k)) for r in rels) for a in range(k)]
    ctrl = C.constant_control(list(range(k)), lambda a: truth[a])  # rule 22: best constant over the enumerated queries

    rows = {}
    for H in range(1, len(rels) + 2):
        exact = Hstar is not None and H >= Hstar
        rows[f"H{H}"] = {
            "heads": H, "edge_budget_per_head": b, "materialized_edges_per_query": H * b,
            "scored_sources_per_query": H * k,
            "exact": exact, "admissible_at_theta": exact,
            "serves_developed_state": True,
            "charged_serve_ops_per_query_unit_price": str(Fr(H * k + H * b)),
        }
    # the parent-maximal SINGLE-factor opponent (protocol rule 19): one head with the largest declared budget
    ok_big, why_big = realizable(rels, k, max(BUDGETS), phi)
    audit_rows = {n: {"admissible": r["admissible_at_theta"], "serves_developed_state": True,
                      "charged_serve_ops_per_query": Fr(r["charged_serve_ops_per_query_unit_price"])}
                  for n, r in rows.items()}
    audit_rows["CONSTANT_CONTROL"] = {"admissible": bool(ctrl["capability"] >= THETA),
                                      "serves_developed_state": False, "charged_serve_ops_per_query": 0}
    return {
        "representation": repname, "relation_set": setname, "relations": rels, "length_k": k, "edge_budget_b": b,
        "declared_relation_count": len(rels), "distinct_relation_multiplicity": len(distinct),
        "minimal_exact_head_count": Hstar, "minimal_partition_witness": witness,
        "per_relation_single_head_realizable": {r: {"realizable": v[0], "reason": v[1]} for r, v in per_rel.items()},
        "parent_maximal_single_head_at_largest_budget": {"realizable": ok_big, "reason": why_big,
                                                         "budget": max(BUDGETS)},
        "rule22_constant_control": {"best_constant_answer": str(ctrl["best_constant_answer"]),
                                    "capability": str(ctrl["capability"]),
                                    "theta": str(THETA),
                                    "obligation_void": C.obligation_is_void(ctrl["capability"], THETA),
                                    "rule": C.RULE_22},
        "rule21_charged_serve_audit": C.charged_serve_audit(audit_rows),
        "rows": rows,
    }


FRONTIER_NOTE_TEXT = ("rows are head counts whose minimal-partition test makes them EXACT (adequacy held at theta = 1); "
                      "A = c_desc * heads, E = c_score * (heads * k scored sources) + c_edge * (heads * b materialized "
                      "edges). Materialized edges per query are H*b and are reported per row, so the protocol's "
                      "'approximately matched compute' is exact and auditable rather than assumed.")


def main(path=None):
    cells = {}
    for rep in REPRESENTATIONS:
        for sn in RELATION_SETS:
            for k in LENGTHS:
                for b in BUDGETS:
                    cells[f"{rep}|{sn}|k={k}|b={b}"] = run_cell(rep, sn, k, b)

    ctxs = {}
    for key, cell in cells.items():
        k, b = cell["length_k"], cell["edge_budget_b"]
        for pname, (c_sc, c_ed, c_de) in PRICES.items():
            lines = {n: (c_de * r["heads"], c_sc * r["heads"] * k + c_ed * r["heads"] * b)
                     for n, r in cell["rows"].items() if r["exact"]}
            if lines:
                ctxs[f"{key}|{pname}"] = lines
    b2_frontiers, shared_grid = C.frontier_set(ctxs, note=FRONTIER_NOTE_TEXT)

    def Hstar(rep, sn, k, b):
        return cells[f"{rep}|{sn}|k={k}|b={b}"]["minimal_exact_head_count"]

    gates = {}
    for rep in REPRESENTATIONS:
        enc = {}
        for r in ("SELF", "NEXT", "SKIP2", "FIRST_ONE"):
            ok = all(realizable([r], k, 1, REPRESENTATIONS[rep])[0] for k in LENGTHS)
            enc[f"{rep}|{r}"] = Fr(1) if ok else Fr(0)
        gates[rep] = C.gate_claim(
            name=f"one content-based head of budget 1 can serve the relation, under representation {rep}",
            gated_axis="feature representation available to the score", gated_setting=rep, encodings=enc,
            strongest=f"{rep}|SELF", verdict="per-relation realizability at budget 1, by relation",
            note="the enumerated representations are CONTENT_ONLY, CONTENT_POSITION and CONTENT_RELPOS; the strongest "
                 "is tested at every gated setting by running all four relations under all three")

    clauses = {
        "C1_minimal_exact_head_count_is_independent_of_sequence_length": all(
            len({Hstar(rep, sn, k, b) for k in LENGTHS}) == 1 for rep in REPRESENTATIONS for sn in RELATION_SETS
            for b in BUDGETS),
        "C2_minimal_exact_head_count_follows_relation_MULTIPLICITY_not_declared_count": all(
            Hstar(rep, "R2_SELF_SELF_DUPLICATE", k, b) == Hstar(rep, "R1_SELF", k, b)
            for rep in REPRESENTATIONS for k in LENGTHS for b in BUDGETS),
        "C3_minimal_exact_head_count_is_nondecreasing_in_relation_multiplicity": all(
            Hstar(rep, a, k, b) <= Hstar(rep, c, k, b)
            for rep in REPRESENTATIONS for k in LENGTHS for b in BUDGETS
            for a, c in (("R1_SELF", "R2_SELF_NEXT"), ("R2_SELF_NEXT", "R3_SELF_NEXT_SKIP2"),
                         ("R3_SELF_NEXT_SKIP2", "R4_ALL"))
            if Hstar(rep, a, k, b) is not None and Hstar(rep, c, k, b) is not None),
        "C4_a_content_only_representation_cannot_serve_any_position_relation_at_any_length": all(
            not realizable([r], k, 1, REPRESENTATIONS["CONTENT_ONLY"])[0]
            for r in ("SELF", "NEXT", "SKIP2") for k in LENGTHS),
        "C5_a_relative_offset_representation_serves_every_position_relation_at_budget_1": all(
            realizable([r], k, 1, REPRESENTATIONS["CONTENT_RELPOS"])[0]
            for r in ("SELF", "NEXT", "SKIP2") for k in LENGTHS),
        "C6_raising_the_edge_budget_lowers_the_head_count_only_by_the_counting_bound": all(
            Hstar(rep, sn, k, 2) is None or Hstar(rep, sn, k, 1) is None or
            Hstar(rep, sn, k, 2) >= -(-Hstar(rep, sn, k, 1) // 2)
            for rep in REPRESENTATIONS for sn in RELATION_SETS for k in LENGTHS),
        "C7_rule19_the_parent_maximal_single_head_at_the_largest_budget_fails_on_every_servable_set_of_multiplicity_3_or_more": all(
            not cells[f"{rep}|{sn}|k={k}|b={max(BUDGETS)}"]["parent_maximal_single_head_at_largest_budget"]["realizable"]
            for rep in REPRESENTATIONS for sn in ("R3_SELF_NEXT_SKIP2", "R4_ALL") for k in LENGTHS
            if Hstar(rep, sn, k, max(BUDGETS)) is not None),
        "C8_rule22_no_declared_cell_is_a_void_obligation": all(
            not c["rule22_constant_control"]["obligation_void"] for c in cells.values()),
        "C9_rule21_no_admissible_row_serves_developed_state_at_zero_charged_cost": all(
            c["rule21_charged_serve_audit"]["passed"] for c in cells.values()),
        "C10_the_frontier_occupant_is_the_minimal_exact_head_count_at_every_reuse_horizon_and_price": all(
            occ == [f"H{cells[key]['minimal_exact_head_count']}"]
            for ctx in b2_frontiers for _, _, occ in b2_frontiers[ctx]["frontier_runs"]
            for key in ["|".join(ctx.split("|")[:4])] if cells[key]["minimal_exact_head_count"] is not None),
        "C11_dg2_every_frontier_grid_covers_twice_every_crossover": all(
            b["dg2_grid_covers_twice_every_crossover"] for b in b2_frontiers.values()),
        "C12_every_declared_relation_set_is_servable_under_at_least_one_representation": all(
            any(Hstar(rep, sn, k, b) is not None for rep in REPRESENTATIONS)
            for sn in RELATION_SETS for k in LENGTHS for b in BUDGETS),
        "C14_the_counting_bound_ceil_multiplicity_over_b_is_TIGHT_wherever_the_set_is_servable": all(
            Hstar(rep, sn, k, b) == -(-cells[f"{rep}|{sn}|k={k}|b={b}"]["distinct_relation_multiplicity"] // b)
            for rep in REPRESENTATIONS for sn in RELATION_SETS for k in LENGTHS for b in BUDGETS
            if Hstar(rep, sn, k, b) is not None),
        "C13_relative_and_absolute_representations_are_not_ordered_by_strength": (
            all(realizable([r], k, 1, REPRESENTATIONS["CONTENT_RELPOS"])[0]
                for r in ("SELF", "NEXT", "SKIP2") for k in LENGTHS)
            and all(not realizable(["FIRST_ONE"], k, b, REPRESENTATIONS["CONTENT_RELPOS"])[0]
                    for k in LENGTHS for b in BUDGETS)
            and all(realizable(["FIRST_ONE"], k, 1, REPRESENTATIONS["CONTENT_POSITION"])[0] for k in LENGTHS)),
    }

    receipt = {
        "schema": "GMI_B2_04_HEADS_V1", "issue": [377, 422], "row": "B2.4 head factorization",
        "revival_id": "RV-377-092",
        "evidence_kind": KIND,
        "evidence_class": "SYNTHETIC_EXACT_EMPIRICAL (tier S): measured minimal factor counts in a declared synthetic "
                          "ecology, frozen before the run. NOT a closed-form identity and NOT neural evidence.",
        "theorems": ["TM-2 / TMT-3 dynamic-routing union-cost (the sibling row B2.3, RV-377-056, prices the same "
                     "materialization; this row prices the FACTORIZATION of the criterion instead)"],
        "registry_entries": ["TF-016 number of heads H", "TF-017 multi-head attention", "TF-011 head dimension d_h",
                             "TF-010 Q/K/V factorization"],
        "declared_instrument": {
            "lengths_k": list(LENGTHS), "edge_budgets_b": list(BUDGETS), "theta": str(THETA),
            "relations": sorted(RELATIONS), "relation_sets": {k: v for k, v in RELATION_SETS.items()},
            "representations": sorted(REPRESENTATIONS),
            "price_vectors": {k: [str(x) for x in v] for k, v in PRICES.items()},
            "head_definition": "one content-based routing factor: an arbitrary score function of the FEATURE PAIR "
                               "(query feature, source feature), materializing its top b sources",
            "realizability_rule": "a group of relations shares one head iff the strict-inequality graph its "
                                  "requirements induce over feature-pair classes is acyclic and no required and "
                                  "non-required source share a feature pair at the same query. Decided exactly by "
                                  "topological sort; nothing is fitted and no rank is guessed.",
            "matched_compute": "materialized edges per query are H*b and are reported per row; scoring is H*k and is "
                               "the coordinate that actually varies with H",
            "arithmetic": "exact rationals and exact combinatorics; every query of every declared length enumerated",
            "randomness": "none",
        },
        "protocol_rules_carried": {"rule_19": "the single-factor opponent is the PARENT-MAXIMAL content-based head -- "
                                              "an arbitrary score function of the feature pair at the largest declared "
                                              "budget -- not a parameterized one",
                                   "rule_21": C.RULE_21, "rule_22": C.RULE_22, "rule_24": C.RULE_24,
                                   "rule_28": C.RULE_28},
        "rule24_gate_records": gates,
        "dg2_audit": {"auditor": "gmi_microscope/grid_audit.py family C, driven by gmi_microscope/b2_audit.py",
                      "run_before_commit": True,
                      "verdict_recorded_in": "microscopes/results/STAGE_B2_DG2_AUDIT_V1.json"},
        "cells": cells,
        "b2_frontiers": b2_frontiers,
        "frontier_note": FRONTIER_NOTE_TEXT,
        "shared_reuse_grid_H": shared_grid,
        "claims": {k: bool(v) for k, v in clauses.items()},
        "n_claims_hold": sum(bool(v) for v in clauses.values()), "n_claims": len(clauses),
        "status": "GREEN" if all(clauses.values()) else "RED",
        "claim_level": "EMPIRICALLY_SUPPORTED_AT_TIER_S",
        "counting_note": "every count here is a count of HEADS, of RELATIONS or of frontier CELLS. None is a count of "
                         "species and none is a count of forms.",
        "claim_ceiling": "a measured minimal factor count on four declared dependency relations, three declared feature "
                         "representations, three sequence lengths and two edge budgets, under one declared cost model. "
                         "It establishes NOTHING about attention heads in a trained network; in particular the head "
                         "here has an arbitrary content-based score rather than a rank-bounded bilinear form, so the "
                         "result is an upper bound on what head-count a rank-bounded head would need, never a lower one.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(path or os.path.join(ROOT, "microscopes", "results", "STAGE_B2_04_HEADS_V1.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    r = main()
    for rep in REPRESENTATIONS:
        print("\n%s" % rep)
        for sn in RELATION_SETS:
            print("  %-24s %s" % (sn, "  ".join(
                "k=%d,b=%d:H*=%s" % (k, b, r["cells"][f"{rep}|{sn}|k={k}|b={b}"]["minimal_exact_head_count"])
                for k in LENGTHS for b in BUDGETS)))
    print()
    for k, v in r["claims"].items():
        print(("HOLDS " if v else "FAILS "), k)
    print(r["status"], r["n_claims_hold"], "/", r["n_claims"], r["receipt_sha256"][:16])

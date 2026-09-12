"""B2.5 -- MHA -> GQA -> MQA: the quality vs cache frontier of key/value sharing, measured.

Stage B2 row B2.5 of GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md section 9:
    "Factorial: KV relation heterogeneity x sequence length x memory bandwidth price x cache capacity.
     Primary response: quality vs cache/memory frontier."

Governing proposition TM-7 (GMI_NEURAL_LLM_TRANSFORMER_MICROFEATURE_CALCULUS_V1.md section 3): autoregressive KV state
scales with the number of INDEPENDENTLY MATERIALIZED key/value heads H_kv rather than the query-head count H_q, so
sharing reduces memory burden; but if two query groups require functionally distinct K/V maps and no compensating
transform exists, forcing them to share destroys exact adequacy. TM-7 predicts a FRONTIER controlled by dependency
heterogeneity and serving prices, "not a universally best head ratio". This row measures it.

SYNTHETIC EXACT MICROSCOPE at laptop scope: every partition of the query heads is enumerated, every stored key/value
subset is enumerated, every capability and cost is exact, and there is no randomness anywhere. It is NOT evidence
about a trained neural network. Registry entries TF-018 (MHA / GQA / MQA sharing), TF-047 (KV cache), TF-048 (KV cache
compression), TF-016 (number of heads), TF-011 (head dimension).

Declared instrument
-------------------
There are four declared SOURCE-SIDE features a key may store -- CONTENT, POSITION, PARITY, BLOCK -- and three declared
PAYLOADS a value may carry -- VAL, PARITY_VAL, BLOCK_ID. A query head serves one declared dependency relation and
therefore REQUIRES a set of key features (what its score must be able to read off the stored key) and one payload.

A KV GROUP stores ONE key of width at most d_k and ONE value of width at most d_v, shared by every query head assigned
to it. That width cap is the whole mechanism: a wider key is strictly more informative, so sharing could never hurt if
keys were unbounded, and TM-7's adequacy loss is a WIDTH phenomenon, not a map-identity one. The stored subsets are
chosen with full hindsight to maximize the number of exact heads (protocol rule 19: the sharing is the best possible
one, never a convenient one), by enumerating every subset of the group's union.

    quality      the fraction of query heads still exact under the best assignment at that H_kv.
    cache        L * n * sum over groups of (stored key width + stored value width) elements retained per sequence.
    capacity     a declared cap on cache elements; a row exceeding it is INFEASIBLE, which is how sequence length
                 turns into a quality loss.
    price        total = compute + mu * cache, with compute = H_q * n scoring operations (independent of H_kv, so the
                 frontier prices the cache alone, which is what TM-7 is about).

Run: python3 -m gmi_microscope.b2_kvshare
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

L_LAYERS = 4
LENGTHS = (8, 16, 32)
D_K = (1, 2, 3)                       # stored key width cap
D_V = (1, 2)                          # stored value width cap
CAPACITY = (None, 512, 1024)          # declared cache-element caps
MU = (Fr(0), Fr(1, 8), Fr(1), Fr(8))  # declared memory-bandwidth prices

# a query head is (name, required key features, required payload)
HEADS_BY_PORTFOLIO = {
    "HET1_homogeneous": [("h_self", ("POSITION",), "VAL"), ("h_next", ("POSITION",), "VAL"),
                         ("h_skip", ("POSITION",), "VAL"), ("h_prev", ("POSITION",), "VAL")],
    "HET2_two_kinds": [("h_self", ("POSITION",), "VAL"), ("h_next", ("POSITION",), "VAL"),
                       ("h_first_one", ("CONTENT",), "VAL"), ("h_content2", ("CONTENT",), "VAL")],
    "HET3_three_kinds": [("h_self", ("POSITION",), "VAL"), ("h_first_one", ("CONTENT",), "VAL"),
                         ("h_parity", ("PARITY",), "PARITY_VAL"), ("h_next", ("POSITION",), "VAL")],
    "HET4_four_kinds": [("h_self", ("POSITION",), "VAL"), ("h_first_one", ("CONTENT",), "VAL"),
                        ("h_parity", ("PARITY",), "PARITY_VAL"), ("h_block", ("BLOCK",), "BLOCK_ID")],
    "HET2_wide_head": [("h_joint", ("CONTENT", "POSITION"), "VAL"), ("h_self", ("POSITION",), "VAL"),
                       ("h_first_one", ("CONTENT",), "VAL"), ("h_next", ("POSITION",), "VAL")],
}


def partitions_into(items, m):
    """Every partition of `items` into exactly m non-empty groups."""
    if m == 1:
        yield [list(items)]
        return
    if len(items) < m:
        return
    first, rest = items[0], items[1:]
    for p in partitions_into(rest, m):
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]
    for p in partitions_into(rest, m - 1):
        yield [[first]] + p


def group_best(group, d_k, d_v):
    """The stored key subset (size <= d_k) and value subset (size <= d_v) maximizing exact members, with ties broken
    by the smallest stored widths and then lexicographically. Returns (n_exact, key_subset, value_subset)."""
    kfeats = sorted({f for _, F, _ in group for f in F})
    pfeats = sorted({p for _, _, p in group})
    best = None
    for kk in range(min(d_k, len(kfeats)) + 1):
        for K in itertools.combinations(kfeats, kk):
            Ks = set(K)
            for vv in range(min(d_v, len(pfeats)) + 1):
                for V in itertools.combinations(pfeats, vv):
                    Vs = set(V)
                    n = sum(1 for _, F, p in group if set(F) <= Ks and p in Vs)
                    cand = (-n, kk + vv, K, V)
                    if best is None or cand < best:
                        best = cand
    return -best[0], list(best[2]), list(best[3])


def run_cell(portfolio, n, d_k, d_v):
    heads = HEADS_BY_PORTFOLIO[portfolio]
    Hq = len(heads)
    names = [h[0] for h in heads]
    het_key = len({tuple(sorted(F)) for _, F, _ in heads})
    het_pair = len({(tuple(sorted(F)), p) for _, F, p in heads})

    rows = {}
    for Hkv in range(1, Hq + 1):
        best = None
        for part in partitions_into(list(range(Hq)), Hkv):
            groups = [[heads[i] for i in g] for g in part]
            res = [group_best(g, d_k, d_v) for g in groups]
            n_exact = sum(r[0] for r in res)
            width = sum(len(r[1]) + len(r[2]) for r in res)
            cand = (-n_exact, width, sorted(sorted(names[i] for i in g) for g in part))
            if best is None or cand < best:
                best = cand
                witness = [{"members": sorted(names[i] for i in g),
                            "stored_key_features": r[1], "stored_value_payloads": r[2],
                            "exact_members": r[0]} for g, r in zip(part, res)]
        n_exact, width, _ = best
        n_exact = -n_exact
        cache = L_LAYERS * n * width
        rows[f"Hkv{Hkv}"] = {
            "H_kv": Hkv, "H_q": Hq,
            "quality": str(Fr(n_exact, Hq)), "quality_float": round(n_exact / Hq, 6),
            "exact_heads": n_exact,
            "stored_width_total": width,
            "cache_elements": cache,
            "cache_elements_formula": f"L({L_LAYERS}) * n({n}) * stored_width({width})",
            "grouping_witness": witness,
            "exact": n_exact == Hq, "admissible_at_theta": n_exact == Hq,
            "serves_developed_state": True,
            "charged_serve_ops_per_query_unit_price": str(Fr(Hq * n)),
            "feasible_under_capacity": {str(c): (c is None or cache <= c) for c in CAPACITY},
        }
    minimal_exact_Hkv = min((r["H_kv"] for r in rows.values() if r["exact"]), default=None)

    # rule 22: the hindsight-optimal CONSTANT answer over the declared query set. The obligation is the tuple of the
    # H_q head answers at each of the n query positions; the control answers one fixed tuple everywhere.
    val = lambda s: (s * 5 + 3) % 7 - 3
    truth = [tuple(val((q + i) % n) for i in range(Hq)) for q in range(n)]
    ctrl = C.constant_control(list(range(n)), lambda q: truth[q])

    audit_rows = {k: {"admissible": r["admissible_at_theta"], "serves_developed_state": True,
                      "charged_serve_ops_per_query": Fr(r["charged_serve_ops_per_query_unit_price"])}
                  for k, r in rows.items()}
    audit_rows["CONSTANT_CONTROL"] = {"admissible": bool(ctrl["capability"] >= THETA),
                                      "serves_developed_state": False, "charged_serve_ops_per_query": 0}
    return {
        "portfolio": portfolio, "length_n": n, "key_width_cap_d_k": d_k, "value_width_cap_d_v": d_v,
        "H_q": Hq, "kv_relation_heterogeneity_key_sets": het_key,
        "kv_relation_heterogeneity_key_payload_pairs": het_pair,
        "minimal_exact_H_kv": minimal_exact_Hkv,
        "rule22_constant_control": {"capability": str(ctrl["capability"]), "theta": str(THETA),
                                    "obligation_void": C.obligation_is_void(ctrl["capability"], THETA),
                                    "rule": "see protocol_rules_carried.rule_22 at the receipt's top level"},
        "rule21_charged_serve_audit": C.charged_serve_audit(audit_rows),
        "rows": rows,
        "tmt13_cache_elements_are_linear_in_H_kv_only_when_widths_are_equal":
            "cache = L*n*sum_g(stored key width + stored value width). TMT-13's 2 L n d H_kv is the special case in "
            "which every group stores the same width d; here the stored widths are measured per group, so the "
            "linear-in-H_kv form is a CONSEQUENCE and not an assumption.",
    }


FRONTIER_NOTE_TEXT = ("rows are key/value sharing ratios H_kv whose best hindsight grouping is EXACT (quality held at "
                      "theta = 1) AND feasible under the context's declared cache capacity; A = mu * cache elements, "
                      "E = scoring operations per query (H_q * n, independent of H_kv). The frontier therefore prices "
                      "the cache alone, which is what TM-7 is about.")


def main(path=None):
    cells = {}
    for pf in HEADS_BY_PORTFOLIO:
        for n in LENGTHS:
            for dk in D_K:
                for dv in D_V:
                    cells[f"{pf}|n={n}|dk={dk}|dv={dv}"] = run_cell(pf, n, dk, dv)

    ctxs = {}
    for key, cell in cells.items():
        for mu in MU:
            for cap in CAPACITY:
                lines = {r: (mu * cell["rows"][r]["cache_elements"],
                             Fr(cell["rows"][r]["charged_serve_ops_per_query_unit_price"]))
                         for r in cell["rows"]
                         if cell["rows"][r]["exact"] and cell["rows"][r]["feasible_under_capacity"][str(cap)]}
                if lines:
                    ctxs[f"{key}|mu={mu}|cap={cap}"] = lines
    b2_frontiers, shared_grid = C.frontier_set(ctxs, note=FRONTIER_NOTE_TEXT)

    def cell(pf, n, dk, dv):
        return cells[f"{pf}|n={n}|dk={dk}|dv={dv}"]

    gate = C.gate_claim(
        name="forcing query heads to share one key/value map destroys exact adequacy",
        gated_axis="stored key width cap d_k", gated_setting="d_k = 1, 2, 3 at H_kv = 1",
        encodings={f"d_k={dk}": Fr(cell("HET4_four_kinds", 16, dk, 2)["rows"]["Hkv1"]["quality"]) for dk in D_K},
        strongest="d_k=3", verdict="MQA quality on the most heterogeneous declared portfolio, by stored key width",
        note="the enumerated representations of the SHARED CARRIER's state are the stored key subsets of every size up "
             "to d_k and the stored value subsets up to d_v, all enumerated and the best chosen with full hindsight; "
             "the strongest is d_k = 3 and it is tested at the gated setting H_kv = 1 (protocol rule 24)")

    clauses = {
        "C1_minimal_exact_H_kv_equals_the_kv_relation_heterogeneity_when_the_width_cap_allows_it": all(
            cell(pf, n, 1, 1)["minimal_exact_H_kv"] == cell(pf, n, 1, 1)["kv_relation_heterogeneity_key_payload_pairs"]
            for pf in HEADS_BY_PORTFOLIO for n in LENGTHS
            if cell(pf, n, 1, 1)["minimal_exact_H_kv"] is not None),
        "C2_minimal_exact_H_kv_is_independent_of_sequence_length": all(
            len({cell(pf, n, dk, dv)["minimal_exact_H_kv"] for n in LENGTHS}) == 1
            for pf in HEADS_BY_PORTFOLIO for dk in D_K for dv in D_V),
        "C3_quality_is_nondecreasing_in_H_kv_in_every_cell": all(
            Fr(c["rows"][f"Hkv{h}"]["quality"]) <= Fr(c["rows"][f"Hkv{h+1}"]["quality"])
            for c in cells.values() for h in range(1, c["H_q"])),
        "C4_cache_elements_are_nonincreasing_as_heads_are_merged": all(
            c["rows"][f"Hkv{h}"]["cache_elements"] <= c["rows"][f"Hkv{h+1}"]["cache_elements"]
            for c in cells.values() for h in range(1, c["H_q"])),
        "C5_MQA_is_exact_on_the_homogeneous_portfolio_and_inexact_on_every_heterogeneous_one_at_d_k_1_d_v_1": (
            all(cell("HET1_homogeneous", n, 1, 1)["rows"]["Hkv1"]["exact"] for n in LENGTHS)
            and all(not cell(pf, n, 1, 1)["rows"]["Hkv1"]["exact"]
                    for pf in ("HET2_two_kinds", "HET3_three_kinds", "HET4_four_kinds") for n in LENGTHS)),
        "C6_raising_the_stored_key_width_cap_lowers_the_minimal_exact_H_kv": any(
            cell(pf, n, 3, 2)["minimal_exact_H_kv"] < cell(pf, n, 1, 1)["minimal_exact_H_kv"]
            for pf in HEADS_BY_PORTFOLIO for n in LENGTHS
            if cell(pf, n, 3, 2)["minimal_exact_H_kv"] is not None
            and cell(pf, n, 1, 1)["minimal_exact_H_kv"] is not None),
        "C7_a_declared_cache_capacity_turns_sequence_length_into_a_quality_loss": any(
            not cell(pf, n, dk, dv)["rows"][f"Hkv{cell(pf, n, dk, dv)['minimal_exact_H_kv']}"]["feasible_under_capacity"][str(cap)]
            for pf in HEADS_BY_PORTFOLIO for n in LENGTHS for dk in D_K for dv in D_V for cap in CAPACITY
            if cap is not None and cell(pf, n, dk, dv)["minimal_exact_H_kv"] is not None),
        "C8_no_universally_best_head_ratio_the_frontier_occupant_moves_with_the_memory_price": any(
            len({tuple(occ) for _, _, occ in b2_frontiers[f"{key}|mu={mu}|cap=None"]["frontier_runs"]}
                | {tuple(occ) for _, _, occ in b2_frontiers[f"{key}|mu={mu2}|cap=None"]["frontier_runs"]}) > 1
            for key in [f"{pf}|n={n}|dk={dk}|dv={dv}" for pf in HEADS_BY_PORTFOLIO for n in LENGTHS
                        for dk in D_K for dv in D_V]
            for mu, mu2 in ((MU[0], MU[-1]),)
            if f"{key}|mu={mu}|cap=None" in b2_frontiers and f"{key}|mu={mu2}|cap=None" in b2_frontiers),
        "C9_rule22_no_declared_cell_is_a_void_obligation": all(
            not c["rule22_constant_control"]["obligation_void"] for c in cells.values()),
        "C10_rule21_no_admissible_row_serves_developed_state_at_zero_charged_cost": all(
            c["rule21_charged_serve_audit"]["passed"] for c in cells.values()),
        "C11_dg2_every_frontier_grid_covers_twice_every_crossover": all(
            b["dg2_grid_covers_twice_every_crossover"] for b in b2_frontiers.values()),
        "C12_at_zero_memory_price_every_exact_and_feasible_sharing_ratio_TIES_so_the_sharing_question_exists_only_because_memory_is_priced": all(
            b.get("single_row_context") or
            ({tuple(sorted(occ)) for _, _, occ in b["frontier_runs"]} == {tuple(sorted(b["cost_coordinates_A_E"]))})
            for k, b in b2_frontiers.items() if k.split("|mu=")[1].startswith("0|")),
        "C13_a_head_requiring_two_key_features_is_inexact_at_every_stored_width_cap_below_two": all(
            cell("HET2_wide_head", n, 1, dv)["rows"][f"Hkv{h}"]["exact"] is False
            for n in LENGTHS for dv in D_V for h in range(1, 5)),
    }

    receipt = {
        "schema": "GMI_B2_05_KVSHARING_V1", "issue": [377, 422], "row": "B2.5 MHA -> GQA -> MQA",
        "revival_id": "RV-377-093",
        "evidence_kind": KIND,
        "evidence_class": "SYNTHETIC_EXACT_EMPIRICAL (tier S): measured quality/cache frontiers in a declared "
                          "synthetic ecology, frozen before the run. NOT neural evidence.",
        "theorems": ["TM-7 KV-sharing tradeoff (the proposition this row operationalizes)",
                     "TMT-13 key/value cache state scaling (receipt check X-TMT13), here recovered as the equal-width "
                     "special case of a measured per-group width sum rather than assumed"],
        "registry_entries": ["TF-018 MHA / GQA / MQA key-value head sharing", "TF-047 KV cache",
                             "TF-048 KV cache compression / quantization", "TF-016 number of heads H",
                             "TF-011 head dimension d_h"],
        "declared_instrument": {
            "layers_L": L_LAYERS, "lengths_n": list(LENGTHS), "key_width_caps_d_k": list(D_K),
            "value_width_caps_d_v": list(D_V), "cache_capacities": [str(c) for c in CAPACITY],
            "memory_prices_mu": [str(m) for m in MU], "theta": str(THETA),
            "source_side_key_features": ["CONTENT", "POSITION", "PARITY", "BLOCK"],
            "payloads": ["VAL", "PARITY_VAL", "BLOCK_ID"],
            "portfolios": {k: [[h[0], list(h[1]), h[2]] for h in v] for k, v in HEADS_BY_PORTFOLIO.items()},
            "sharing_rule": "a KV group stores ONE key of width at most d_k and ONE value of width at most d_v; the "
                            "stored subsets are chosen with FULL HINDSIGHT to maximize exact heads, by enumerating "
                            "every subset. The width cap is the whole mechanism: an unbounded key would make sharing "
                            "free, so TM-7's adequacy loss is a WIDTH phenomenon and not a map-identity one.",
            "arithmetic": "exact rationals and exact combinatorics; every partition of the query heads and every "
                          "stored subset enumerated; no randomness and no tolerance",
        },
        "protocol_rules_carried": {"rule_19": "the sharing is the BEST possible one at every ratio: every partition and "
                                              "every stored subset is enumerated and the hindsight optimum taken, so a "
                                              "reported quality loss is a loss no grouping could have avoided",
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
        "claim_ceiling": "a measured quality/cache frontier over five declared query-head portfolios, three sequence "
                         "lengths, three key-width caps, two value-width caps, three cache capacities and four memory "
                         "prices. It establishes NOTHING about GQA or MQA in a trained network: the key here stores a "
                         "SUBSET of four declared discrete features rather than a learned linear projection, so 'width' "
                         "is a feature count and not a dimension, and no compensating transform elsewhere in the model "
                         "is available to the sharing, which TM-7 explicitly allows for.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(path or os.path.join(ROOT, "microscopes", "results", "STAGE_B2_05_KVSHARING_V1.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    r = main()
    for pf in HEADS_BY_PORTFOLIO:
        print("\n%s" % pf)
        for dk in D_K:
            for dv in D_V:
                c = r["cells"][f"{pf}|n=16|dk={dk}|dv={dv}"]
                print("  dk=%d dv=%d het=%d H_kv*=%-4s  %s" % (
                    dk, dv, c["kv_relation_heterogeneity_key_payload_pairs"], c["minimal_exact_H_kv"],
                    "  ".join("Hkv%d:q=%s,c=%d" % (v["H_kv"], v["quality"], v["cache_elements"])
                              for v in c["rows"].values())))
    print()
    for k, v in r["claims"].items():
        print(("HOLDS " if v else "FAILS "), k)
    print(r["status"], r["n_claims_hold"], "/", r["n_claims"], r["receipt_sha256"][:16])

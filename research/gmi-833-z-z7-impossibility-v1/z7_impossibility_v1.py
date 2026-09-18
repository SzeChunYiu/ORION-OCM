"""Route A -- exact resource-dependent impossibility regions and prospectively
frozen capability ceilings (#833 Section Z, subsection Z7).

Route A simulates: every candidate is replayed over the eight input sequences in
both modes, and every hypothesis, ceiling, family, grid cell and counterexample
witness is decided by scanning the resulting list. Stdlib only, exact rational
arithmetic; no float appears in any claim.

Run:  python3 -I -B z7_impossibility_v1.py
"""
import hashlib
import itertools
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)
REPO = os.path.dirname(RESEARCH)
TRANS = os.path.join(RESEARCH, "gmi-833-heldout-20-transitions-v1", "RESULT_V1.json")

L = 3
N = (L - 1) * (2 ** L)          # 16 scored moments per mode
NULL_SEEDS = tuple(range(9500, 9700))

GRID_P = ("1/5", "2/5", "1/2", "3/5", "4/5")
GRID_ETA = ("1", "2", "3")
GRID_LAM = ("1/20", "1/10", "1/5", "1/2")
GRID_ANOW = (0, 4, 8, 16)
GRID_ADELAY = (0, 4, 8, 16)
GRID_C = ("1/10", "1/5", "1/2", "1")
GRID_B = (0, 1)


def fs(x):
    return str(Fraction(x))


def sequences(length):
    return tuple(itertools.product((0, 1), repeat=length))


SEQ = sequences(L)


def stateless_errors(table):
    e = [0, 0]
    for mode in (0, 1):
        for seq in SEQ:
            for t in range(1, L):
                cur = seq[t]
                got = (table >> (2 * mode + cur)) & 1
                want = cur if mode == 0 else seq[t - 1]
                if got != want:
                    e[mode] += 1
    return e[0], e[1]


def stateful_errors(nxt, table):
    e = [0, 0]
    for mode in (0, 1):
        for seq in SEQ:
            st = 0
            for t in range(L):
                cur = seq[t]
                idx = 4 * st + 2 * mode + cur
                got = (table >> idx) & 1
                if t >= 1:
                    want = cur if mode == 0 else seq[t - 1]
                    if got != want:
                        e[mode] += 1
                st = (nxt >> idx) & 1
    return e[0], e[1]


def build_universe():
    """(bits, nxt, table, e_now, e_delay); nxt is None for stateless."""
    out = []
    for table in range(16):
        e0, e1 = stateless_errors(table)
        out.append((0, None, table, e0, e1))
    for nxt in range(256):
        for table in range(256):
            e0, e1 = stateful_errors(nxt, table)
            out.append((1, nxt, table, e0, e1))
    return out


# ------------------------------------------------------------------ families
def is_dead_table(table):
    for m in (0, 1):
        for c in (0, 1):
            if ((table >> (2 * m + c)) & 1) != ((table >> (4 + 2 * m + c)) & 1):
                return False
    return True


def is_frozen_state(nxt):
    return nxt == 0 or nxt == 255


def is_moore(table):
    for s in (0, 1):
        for m in (0, 1):
            if ((table >> (4 * s + 2 * m)) & 1) != ((table >> (4 * s + 2 * m + 1)) & 1):
                return False
    return True


NXT_IDENTITY = 0b10101010  # nxt[4s+2m+c] = c


def families(universe):
    fam = {"F_STATELESS": [], "F_DEAD_TABLE": [], "F_FROZEN_STATE": [],
           "F_MOORE": [], "F_MEALY_PURE": [], "F_IDENTITY_STATE": []}
    for rec in universe:
        bits, nxt, table, _e0, _e1 = rec
        if bits == 0:
            fam["F_STATELESS"].append(rec)
            continue
        if is_dead_table(table):
            fam["F_DEAD_TABLE"].append(rec)
        if is_frozen_state(nxt):
            fam["F_FROZEN_STATE"].append(rec)
        if is_moore(table):
            fam["F_MOORE"].append(rec)
        else:
            fam["F_MEALY_PURE"].append(rec)
        if nxt == NXT_IDENTITY:
            fam["F_IDENTITY_STATE"].append(rec)
    return fam


# ------------------------------------------------------------------- worlds
def load_worlds():
    with open(TRANS) as fh:
        doc = json.load(fh)
    if doc.get("schema") != "GMI_833_HELDOUT_20_TRANSITIONS_RESULT_V1":
        raise SystemExit("transition receipt schema drift")
    out = []
    for case in doc["cases"]:
        p = Fraction(case["p"])
        eta = Fraction(case["eta"])
        star = eta * p / 2
        for tag, lam in (("low", Fraction(case["lambda_low"])),
                         ("high", Fraction(case["lambda_high"])),
                         ("boundary", star)):
            out.append({"case": case["case"], "tag": tag, "p": p, "eta": eta,
                        "lam": lam, "lam_star": star})
    return out


def risk(e0, e1, p):
    return (1 - p) * Fraction(e0, N) + p * Fraction(e1, N)


def objective(bits, e0, e1, p, eta, lam):
    return eta * risk(e0, e1, p) + lam * bits


# --------------------------------------------------- impossibility machinery
def attained_pairs(recs):
    return set([(r[3], r[4]) for r in recs])


def pareto_min(pairs):
    out = []
    for a in sorted(pairs):
        dominated = False
        for b in pairs:
            if b != a and b[0] <= a[0] and b[1] <= a[1]:
                dominated = True
                break
        if not dominated:
            out.append(list(a))
    return out


def claim_is_true(pairs, x, y):
    """`no candidate in this family attains e_now <= x and e_delay <= y`."""
    for (e0, e1) in pairs:
        if e0 <= x and e1 <= y:
            return False
    return True


def witness_for(recs, x, y):
    for r in recs:
        if r[3] <= x and r[4] <= y:
            return {"bits": r[0], "nxt": r[1], "table": r[2],
                    "e_now": r[3], "e_delay": r[4]}
    return None


def blob_sha(path):
    with open(path, "rb") as fh:
        data = fh.read()
    return hashlib.sha1(("blob %d\0" % len(data)).encode("ascii") + data).hexdigest()


# ------------------------------------------------------------------ the run
def main():
    universe = build_universe()
    worlds = load_worlds()
    st0 = [r for r in universe if r[0] == 0]
    st1 = [r for r in universe if r[0] == 1]
    S0 = attained_pairs(st0)
    S1 = attained_pairs(st1)
    fam = families(universe)

    rep = {"schema": "GMI_833_Z7_IMPOSSIBILITY_RESULT_V1", "issue": 833,
           "section": "Z", "subsection": "Z7",
           "source_main": "349c2e62c4ae01f52cf66f61e4dacdbdfcf10071",
           "claim_ceiling": ("GMI_833_Z7_EXACT_RESOURCE_DEPENDENT_IMPOSSIBILITY_REGIONS_"
                             "AND_PROSPECTIVELY_FROZEN_CAPABILITY_CEILINGS_AT_REGISTERED_"
                             "BINARY_TRANSDUCER_SCOPE"),
           "route": "A_simulation",
           "universe": {"candidates": len(universe), "stateless": len(st0),
                        "stateful": len(st1), "N_scored_moments": N}}

    # ---- IM-1 the impossible capability
    delay_vals_0 = sorted(set([e for _e, e in [(r[3], r[4]) for r in st0]]))
    rep["IM_1"] = {
        "constraint": "bits = 0",
        "capability": "zero-error delayed recall",
        "stateless_delay_values": delay_vals_0,
        "zero_error_delay_possible_at_bits_0": 0 in delay_vals_0,
        "failure_is_uniform": len(delay_vals_0) == 1,
        "delay_accuracy_ceiling_at_bits_0": fs(Fraction(N - delay_vals_0[0], N)),
        "zero_error_delay_possible_at_bits_1": (0, 0) in S1 or any(e1 == 0 for _e0, e1 in S1),
        "resource_dependent_not_task_dependent": True,
    }

    # ---- IM-2 impossibility regions
    grid_cells = 289
    rep["IM_2"] = {
        "R1_attainable": {
            "S0": sorted([list(x) for x in S0]),
            "S0_size": len(S0),
            "S0_impossibility_cells": grid_cells - len(S0),
            "S1_size": len(S1),
            "S1_impossibility_cells": grid_cells - len(S1),
            "S1_pareto_frontier": pareto_min(S1),
            "S0_pareto_frontier": pareto_min(S0),
            "lattice_cells": grid_cells,
        }
    }

    # R2: feasibility grid.
    # The objective and both error constraints depend on a candidate only through
    # the triple (bits, e_now, e_delay), so the scan runs over the 146 distinct
    # triples rather than over all 65552 candidates. The test asserts that the
    # reduced scan agrees with a direct scan on a sample of cells.
    by_budget = {0: st0, 1: st0 + st1}
    triples = {0: sorted(set([(r[0], r[3], r[4]) for r in st0])),
               1: sorted(set([(r[0], r[3], r[4]) for r in st0 + st1]))}
    infeasible = 0
    feasible = 0
    infeas_by_b = {0: 0, 1: 0}
    always_infeasible_targets = set()
    target_infeasible_counts = {}
    total_cells = 0
    for ps in GRID_P:
        p = Fraction(ps)
        for es in GRID_ETA:
            eta = Fraction(es)
            for ls in GRID_LAM:
                lam = Fraction(ls)
                for an in GRID_ANOW:
                    for ad in GRID_ADELAY:
                        for cs in GRID_C:
                            C = Fraction(cs)
                            for b in GRID_B:
                                total_cells += 1
                                ok = False
                                for tr in triples[b]:
                                    if tr[1] <= an and tr[2] <= ad and \
                                            objective(tr[0], tr[1], tr[2], p, eta, lam) <= C:
                                        ok = True
                                        break
                                key = (b, an, ad)
                                target_infeasible_counts.setdefault(key, [0, 0])
                                if ok:
                                    feasible += 1
                                    target_infeasible_counts[key][1] += 1
                                else:
                                    infeasible += 1
                                    infeas_by_b[b] += 1
                                    target_infeasible_counts[key][0] += 1
    for key in target_infeasible_counts:
        inf, fea = target_infeasible_counts[key]
        if fea == 0:
            always_infeasible_targets.add(key)
    rep["IM_2"]["R2_cost_grid"] = {
        "cells": total_cells,
        "feasible": feasible,
        "infeasible": infeasible,
        "infeasible_by_budget": {"0": infeas_by_b[0], "1": infeas_by_b[1]},
        "targets_infeasible_at_every_world_by_budget":
            sorted([{"b": k[0], "a_now": k[1], "a_delay": k[2]}
                    for k in always_infeasible_targets],
                   key=lambda d: (d["b"], d["a_now"], d["a_delay"])),
        "targets_infeasible_at_every_world_count": len(always_infeasible_targets),
        "grid": {"p": list(GRID_P), "eta": list(GRID_ETA), "lambda": list(GRID_LAM),
                 "a_now": list(GRID_ANOW), "a_delay": list(GRID_ADELAY),
                 "C": list(GRID_C), "b": list(GRID_B)},
    }

    # ---- IM-3 qualitative failure modes Q1..Q5
    hist = {}
    for r in st1:
        k = (r[3], r[4])
        hist[k] = hist.get(k, 0) + 1
    modal = max(hist.items(), key=lambda kv: (kv[1], -kv[0][0], -kv[0][1]))
    e_now_vals_0 = sorted(set([r[3] for r in st0]))
    q4_witness = None
    for r in st1:
        if r[4] == 0 and r[3] == 16:
            q4_witness = {"bits": r[0], "nxt": r[1], "table": r[2],
                          "e_now": r[3], "e_delay": r[4]}
            break
    q5_witness = None
    for r in st1:
        if r[4] > delay_vals_0[0]:
            q5_witness = {"bits": r[0], "nxt": r[1], "table": r[2],
                          "e_now": r[3], "e_delay": r[4]}
            break
    Q = {
        "Q1": {"text": "at bits=0 the delay channel fails on exactly N/2 moments, "
                       "identically for every member of the family",
               "label": "[DERIVED-AT-FREEZE]",
               "verdict": "CONFIRMED" if delay_vals_0 == [N // 2] else "REFUTED",
               "evidence": "stateless e_delay value set = %s" % delay_vals_0},
        "Q2": {"text": "at bits=0 the copy channel failure is not uniform: "
                       "e_now takes exactly {0, 8, 16}",
               "label": "[DERIVED-AT-FREEZE]",
               "verdict": "CONFIRMED" if e_now_vals_0 == [0, 8, 16] else "REFUTED",
               "evidence": "stateless e_now value set = %s" % e_now_vals_0},
        "Q3": {"text": "the modal failure profile of a one-state-bit mechanism is (8, 8)",
               "label": "[UNCOMPUTED]",
               "verdict": "CONFIRMED" if modal[0] == (8, 8) else "REFUTED",
               "evidence": "modal pair %s with multiplicity %d of %d"
                           % (list(modal[0]), modal[1], len(st1))},
        "Q4": {"text": "scarcity hypothesis: no one-state-bit mechanism attains "
                       "e_delay = 0 while e_now = 16",
               "label": "[NAIVE]",
               "verdict": "REFUTED" if q4_witness is not None else "CONFIRMED",
               "evidence": ("witness %s" % q4_witness) if q4_witness else "no witness found",
               "witness": q4_witness},
        "Q5": {"text": "some one-state-bit mechanism is strictly worse on the delay "
                       "channel than every stateless mechanism",
               "label": "[UNCOMPUTED]",
               "verdict": "CONFIRMED" if q5_witness is not None else "REFUTED",
               "evidence": ("witness %s" % q5_witness) if q5_witness else "no witness found",
               "witness": q5_witness},
    }
    rep["IM_3"] = Q

    # ---- IM-4 quantitative ceilings C1..C6, each validity + tightness
    def lower_ceiling(recs, field, K):
        """claim: field >= K over recs. valid iff min >= K; tight iff min == K."""
        vals = [r[field] for r in recs]
        mn = min(vals)
        viol = len([v for v in vals if v < K])
        return {"bound": K, "attained_min": mn, "valid": viol == 0,
                "violations": viol, "tight": mn == K}

    c1 = lower_ceiling(st0, 4, 8)
    p_probe = [Fraction(x) for x in GRID_P]
    c2_bad = 0
    c2_tight_all = True
    for p in p_probe:
        mn = min([risk(r[3], r[4], p) for r in st0])
        if mn < p / 2:
            c2_bad += 1
        if mn != p / 2:
            c2_tight_all = False
    c3_min = min([risk(t[1], t[2], p_probe[0]) for t in triples[1]])
    k4 = max([min(r[3], r[4]) for r in st1])
    k4_viol = len([r for r in st1 if min(r[3], r[4]) > k4])
    k5 = len(S1)
    c6_bad = 0
    for w in worlds:
        mn = min([objective(t[0], t[1], t[2], w["p"], w["eta"], w["lam"])
                  for t in triples[1]])
        if mn != min(w["eta"] * w["p"] / 2, w["lam"]):
            c6_bad += 1
    rep["IM_4"] = {
        "C1": dict(c1, family="bits=0", claim="e_delay >= 8", label="[DERIVED-AT-FREEZE]"),
        "C2": {"family": "bits=0", "claim": "weighted risk >= p/2 for every p",
               "label": "[DERIVED-AT-FREEZE]", "probe_p": list(GRID_P),
               "violations": c2_bad, "valid": c2_bad == 0, "tight": c2_tight_all},
        "C3": {"family": "bits<=1", "claim": "weighted risk >= 0, attained",
               "label": "[DERIVED-AT-FREEZE]", "attained_min": fs(c3_min),
               "valid": c3_min >= 0, "tight": c3_min == 0},
        "C4": {"family": "bits=1", "claim": "min(e_now, e_delay) <= K4",
               "label": "[UNCOMPUTED]", "K4": k4, "violations": k4_viol,
               "valid": k4_viol == 0,
               "tight": any(min(r[3], r[4]) == k4 for r in st1)},
        "C5": {"family": "bits=1", "claim": "|S_1| = K5", "label": "[UNCOMPUTED]",
               "K5": k5, "valid": True, "tight": True},
        "C6": {"family": "whole universe",
               "claim": "min J = min(eta*p/2, lambda) at every registered world",
               "label": "[DERIVED-AT-FREEZE]", "worlds": len(worlds),
               "violations": c6_bad, "valid": c6_bad == 0, "tight": c6_bad == 0},
    }

    # ---- IM-5 broad families against the predictions
    famrep = {}
    for name in sorted(fam):
        recs = fam[name]
        pairs = attained_pairs(recs)
        famrep[name] = {
            "size": len(recs),
            "attained_pair_count": len(pairs),
            "min_e_delay": min([r[4] for r in recs]),
            "min_e_now": min([r[3] for r in recs]),
            "pareto_frontier": pareto_min(pairs),
            "violates_C1_if_stateless": (name == "F_STATELESS" and
                                         min([r[4] for r in recs]) < 8),
            "contains_zero_zero": (0, 0) in pairs,
        }
    moore_min_now = famrep["F_MOORE"]["min_e_now"]
    mealy_min_now = famrep["F_MEALY_PURE"]["min_e_now"]
    rep["IM_5_structural"] = {
        "finding": ("a named structural family can carry its own impossibility: the "
                    "Moore family, whose output does not read the current symbol, "
                    "cannot reach fewer than %d copy-channel errors, while the "
                    "complementary family reaches %d"
                    % (moore_min_now, mealy_min_now)),
        "F_MOORE_min_e_now": moore_min_now,
        "F_MEALY_PURE_min_e_now": mealy_min_now,
        "separated": moore_min_now > mealy_min_now,
        "F_MOORE_pareto": famrep["F_MOORE"]["pareto_frontier"],
        "F_MEALY_PURE_pareto": famrep["F_MEALY_PURE"]["pareto_frontier"],
    }
    rep["IM_5"] = {"families": famrep,
                   "exhaustive_over_universe": True,
                   "universe_checked": len(universe)}

    # ---- IM-6 counterexample register
    reg_entries = []
    for qid in ("Q1", "Q2", "Q3", "Q4", "Q5"):
        q = Q[qid]
        if q["verdict"] != "REFUTED":
            continue
        w = q.get("witness")
        ok = False
        if qid == "Q4" and w is not None:
            ok = (w["e_delay"] == 0 and w["e_now"] == 16 and w["bits"] == 1)
        reg_entries.append({
            "hypothesis": qid,
            "frozen_text": q["text"],
            "label": q["label"],
            "witness": w,
            "witness_violates_hypothesis": ok,
            "assumption_that_failed":
                ("one bit of persistent state is a shared scarce resource, so accuracy "
                 "on one channel must be paid for with accuracy on the other"),
            "repair":
                ("the state index carries the mode bit, so the two channels address "
                 "disjoint table and next-state entries; a single state bit is not "
                 "shared between them, and perfect delay is compatible with maximal "
                 "copy error"),
            "claim_ceiling_consequence":
                ("no impossibility statement in this universe may be derived from "
                 "'one bit must be shared'; every such statement must be derived from "
                 "the per-mode index structure"),
        })
    reg = {"schema": "GMI_833_Z7_COUNTEREXAMPLE_REGISTER_V1", "issue": 833,
           "subsection": "Z7",
           "refuted_hypotheses": len(reg_entries),
           "entries": reg_entries,
           "surviving_hypotheses": [qid for qid in ("Q1", "Q2", "Q3", "Q4", "Q5")
                                    if Q[qid]["verdict"] == "CONFIRMED"]}
    with open(os.path.join(HERE, "COUNTEREXAMPLE_REGISTER_V1.json"), "w") as fh:
        json.dump(reg, fh, indent=1, sort_keys=True)
        fh.write("\n")
    rep["IM_6"] = {"refuted": len(reg_entries),
                   "all_witnesses_violate": all(e["witness_violates_hypothesis"]
                                                for e in reg_entries),
                   "register_written": "COUNTEREXAMPLE_REGISTER_V1.json"}

    # ---- hostiles
    hostiles = {}
    h1 = lower_ceiling(st0, 4, 9)
    hostiles["H1_WRONG_CEILING"] = {
        "quantity": "violation count for the C1 bound",
        "clean": c1["violations"], "hostile": h1["violations"],
        "moved": c1["violations"] == 0 and h1["violations"] == 16}
    h2 = lower_ceiling(st0, 4, 0)
    hostiles["H2_VACUOUS_CEILING"] = {
        "quantity": "tightness flag for the C1 bound",
        "clean": c1["tight"], "hostile": h2["tight"],
        "moved": c1["tight"] is True and h2["tight"] is False}
    S1_cut = attained_pairs(st0)
    infeasible_cut = 0
    for ps in GRID_P:
        p = Fraction(ps)
        for es in GRID_ETA:
            eta = Fraction(es)
            for ls in GRID_LAM:
                lam = Fraction(ls)
                for an in GRID_ANOW:
                    for ad in GRID_ADELAY:
                        for cs in GRID_C:
                            C = Fraction(cs)
                            ok = False
                            for tr in triples[0]:
                                if tr[1] <= an and tr[2] <= ad and \
                                        objective(tr[0], tr[1], tr[2], p, eta, lam) <= C:
                                    ok = True
                                    break
                            if not ok:
                                infeasible_cut += 1
    hostiles["H3_TRUNCATED_UNIVERSE"] = {
        "quantity": "|S_1| and the infeasible-cell count at budget b=1",
        "clean": [len(S1), infeas_by_b[1]],
        "hostile": [len(S1_cut), infeasible_cut],
        "moved": len(S1_cut) != len(S1) and infeasible_cut != infeas_by_b[1]}
    off = set()
    for table in range(16):
        e1 = 0
        for seq in SEQ:
            for t in range(0, L):
                cur = seq[t]
                got = (table >> (2 + cur)) & 1
                want = seq[t - 1] if t >= 1 else 0
                if got != want:
                    e1 += 1
        off.add(e1)
    hostiles["H4_SCORER_OFFSET"] = {
        "quantity": "stateless e_delay value set",
        "clean": delay_vals_0, "hostile": sorted(off),
        "moved": sorted(off) != delay_vals_0}
    fake = {"bits": 1, "nxt": 0, "table": 0, "e_now": 0, "e_delay": 0}
    fake_ok = (fake["e_delay"] == 0 and fake["e_now"] == 16 and fake["bits"] == 1)
    hostiles["H5_FAKE_WITNESS"] = {
        "quantity": "witness_violates_hypothesis flag on the Q4 register entry",
        "clean": all(e["witness_violates_hypothesis"] for e in reg_entries),
        "hostile": fake_ok,
        "moved": (all(e["witness_violates_hypothesis"] for e in reg_entries)
                  and fake_ok is False)}
    rep["hostiles"] = hostiles

    # ---- null: 200 random impossibility claims, witness soundness + tightness
    frozen_claims = [(0, 15, 7), (0, 16, 7)]
    random_true = 0
    random_tight = 0
    witness_required = 0
    witness_supplied = 0
    for seed in NULL_SEEDS:
        rnd = random.Random(seed)
        b = rnd.choice([0, 1])
        x = rnd.randrange(0, 17)
        y = rnd.randrange(0, 17)
        recs = by_budget[b]
        pairs = attained_pairs(recs)
        true = claim_is_true(pairs, x, y)
        if true:
            random_true += 1
            weaker = (not claim_is_true(pairs, x + 1, y)) or \
                     (not claim_is_true(pairs, x, y + 1))
            if weaker:
                random_tight += 1
        else:
            witness_required += 1
            w = witness_for(recs, x, y)
            if w is not None and w[ "e_now"] <= x and w["e_delay"] <= y:
                witness_supplied += 1
    frozen_tight = 0
    frozen_total = 0
    for (b, x, y) in frozen_claims:
        frozen_total += 1
        pairs = attained_pairs(by_budget[b])
        if claim_is_true(pairs, x, y):
            weaker = (not claim_is_true(pairs, x + 1, y)) or \
                     (not claim_is_true(pairs, x, y + 1))
            if weaker:
                frozen_tight += 1
    ceilings_tight = len([k for k in ("C1", "C2", "C3", "C4", "C6")
                          if rep["IM_4"][k]["tight"]])
    rep["null"] = {
        "seeds": len(NULL_SEEDS),
        "claim_form": "no candidate with bits <= b attains e_now <= x and e_delay <= y",
        "witness_required": witness_required,
        "witness_supplied": witness_supplied,
        "witness_soundness_complete": witness_required == witness_supplied,
        "random_true": random_true,
        "random_true_and_tight": random_tight,
        "frozen_probe_claims": frozen_total,
        "frozen_probe_tight": frozen_tight,
        "frozen_ceilings_checked": 5,
        "frozen_ceilings_tight": ceilings_tight,
        "tightness_discrimination":
            ("frozen ceilings tight %d/5; random claims true-and-tight %d/%d"
             % (ceilings_tight, random_tight, len(NULL_SEEDS))),
    }

    gates = {
        "zero_error_delay_impossible_at_bits_0":
            rep["IM_1"]["zero_error_delay_possible_at_bits_0"] is False,
        "failure_is_uniform_at_bits_0": rep["IM_1"]["failure_is_uniform"],
        "resource_dependent": rep["IM_1"]["zero_error_delay_possible_at_bits_1"] is True,
        "S0_is_three_points": len(S0) == 3,
        "grid_fully_classified": feasible + infeasible == total_cells,
        "Q1_confirmed": Q["Q1"]["verdict"] == "CONFIRMED",
        "Q2_confirmed": Q["Q2"]["verdict"] == "CONFIRMED",
        "naive_hypothesis_adjudicated": Q["Q4"]["verdict"] in ("CONFIRMED", "REFUTED"),
        "every_refutation_has_a_valid_witness": rep["IM_6"]["all_witnesses_violate"],
        "C1_valid_and_tight": rep["IM_4"]["C1"]["valid"] and rep["IM_4"]["C1"]["tight"],
        "C2_valid_and_tight": rep["IM_4"]["C2"]["valid"] and rep["IM_4"]["C2"]["tight"],
        "C3_valid_and_tight": rep["IM_4"]["C3"]["valid"] and rep["IM_4"]["C3"]["tight"],
        "C4_valid_and_tight": rep["IM_4"]["C4"]["valid"] and rep["IM_4"]["C4"]["tight"],
        "C6_valid_and_tight": rep["IM_4"]["C6"]["valid"] and rep["IM_4"]["C6"]["tight"],
        "families_cover_universe":
            famrep["F_STATELESS"]["size"] + famrep["F_MOORE"]["size"]
            + famrep["F_MEALY_PURE"]["size"] == len(universe),
        "hostiles_all_moved": all(h["moved"] for h in hostiles.values()),
        "witness_soundness_complete": rep["null"]["witness_soundness_complete"],
        "tightness_discriminates":
            rep["null"]["random_true_and_tight"] * 10 < rep["null"]["seeds"],
        "structural_family_impossibility_separated":
            rep["IM_5_structural"]["separated"],
    }
    rep["gates"] = gates
    rep["verdict"] = "GREEN" if all(gates.values()) else "RED"
    rep["forbidden_promotions"] = [
        "UNIVERSAL_IMPOSSIBILITY", "IMPOSSIBILITY_FOR_REAL_SYSTEMS",
        "CAPABILITY_CEILINGS_TRANSFER_TO_TRAINED_MODELS",
        "COMPLETE_ENUMERATION_OF_FAILURE_MODES",
        "RESOURCE_ACCOUNTING_IS_SUBSTRATE_INDEPENDENT",
        "IMPOSSIBILITY_REGION_IS_ARCHITECTURE_INDEPENDENT",
        "ZERO_STATE_MEANS_ZERO_MEMORY_IN_GENERAL"]

    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(rep, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("Z7 verdict:", rep["verdict"])
    for k in sorted(gates):
        print("  %-42s %s" % (k, gates[k]))
    print("  grid cells:", total_cells, "infeasible:", infeasible)
    print("  |S0| =", len(S0), " |S1| =", len(S1))
    print("  Q verdicts:", dict([(k, Q[k]["verdict"]) for k in sorted(Q)]))
    return 0 if rep["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())

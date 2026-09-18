#!/usr/bin/env python3
"""Route B: a materially independent oracle for the #833 Section K predictor.

This module MUST NOT import route A (`capability_predictor_v1`). It re-derives
everything from the frozen scope of SCOPE_V1.md using different data structures
and different algorithms:

  * sets of explicit realization dicts instead of bitmask integers;
  * integer common-denominator arithmetic for the contract score instead of
    Fraction accumulation;
  * ceilings obtained by scanning the registered capability value list downwards
    and testing membership, instead of `max`;
  * image cardinality obtained by sorting with explicit duplicate counting,
    instead of `set`;
  * failure-mode attribution by a TOP-DOWN scan for the last prefix that still
    attains the target, instead of the bottom-up first-crossing index.

Agreement between the two routes on every grid point is the certificate.
"""

from __future__ import annotations

import json
from fractions import Fraction

DENOM = 6
TASK_NUMERATORS = (3, 2, 1)          # (1/2, 1/3, 1/6) over the common denominator 6
RHO_DIM = 14
UNSATISFIED = "UNSATISFIED"

CUT_ORDER = ("Expr", "Res", "Reach", "Seen", "Epis")
CUT_TO_MODE = {
    "Expr": "FM_EXPRESSIVITY",
    "Res": "FM_RESOURCE",
    "Reach": "FM_REACHABILITY",
    "Seen": "FM_SEARCH_BUDGET",
    "Epis": "FM_OBSERVED_SHORTFALL",
}


def bit_list(value):
    out = []
    while value:
        out.append(value & 1)
        value >>= 1
    return out


def make_universe():
    people = []
    for a in range(8):
        for b in range(2):
            for c in range(2):
                bits = bit_list(a)
                while len(bits) < 3:
                    bits.append(0)
                ones = 0
                for bit in bits:
                    if bit:
                        ones += 1
                k = (a + b) % 3
                rho = []
                for j in range(RHO_DIM):
                    if j == 0:
                        rho.append(ones + 1)
                    elif j == 1:
                        rho.append(b + 1)
                    elif j == 2:
                        rho.append(c + 1)
                    else:
                        rho.append(0)
                people.append({
                    "a": a, "b": b, "c": c, "bits": tuple(bits), "ones": ones,
                    "k": k, "rho": tuple(rho), "dev": 2 * ones + k, "obs": (k, b),
                })
    ranked = sorted(people, key=lambda rec: (rec["rho"][0], rec["a"], rec["b"], rec["c"]))
    for position, rec in enumerate(ranked):
        rec["rank"] = position
    for index, rec in enumerate(people):
        rec["index"] = index
    return people


UNIVERSE = make_universe()
N = len(UNIVERSE)

VERIFIED = {"E_full": (1, 1, 1), "E_v0": (0, 1, 1)}


def score_numerator(rec, contract):
    mask = VERIFIED[contract]
    total = 0
    for j in range(3):
        if mask[j] and rec["bits"][j]:
            total += TASK_NUMERATORS[j]
    return total


SCORE_NUM = {name: tuple(score_numerator(rec, name) for rec in UNIVERSE)
             for name in VERIFIED}


def registered_values(contract):
    seen = []
    for value in SCORE_NUM[contract]:
        if value not in seen:
            seen.append(value)
    seen.sort()
    return tuple(seen)


VALUE_LADDER = {name: registered_values(name) for name in VERIFIED}

K_M_VALUES = tuple(tuple(j for j in range(3) if (bits >> j) & 1) for bits in range(8))
BUDGETS = ((2, 1, 1), (3, 2, 2), (9, 3, 3))
CHARGES = ((0, 0, 0), (1, 0, 0))
R_VALUES = tuple((b, m) for b in BUDGETS for m in CHARGES)
D_VALUES = (2, 6, 99)
B_VALUES = (0, 6, 12, 20, 32)
H_VALUES = ("NO_OBSERVATION", (1, 1), (2, 0))
TAU_NUM = (1, 3, 4, 6)          # 1/6, 1/2, 2/3, 1 over denominator 6
CONTRACTS = ("E_full", "E_v0")

BETA_PARTS = (Fraction(1, 100), Fraction(1, 200), Fraction(1, 500), Fraction(1, 50))
BETA_TOTAL = BETA_PARTS[0] + BETA_PARTS[1] + BETA_PARTS[2] + BETA_PARTS[3]

U_VALUES = (
    ("U0", "FEASIBLE_SET", None),
    ("U1", "CONFIDENCE_SET", Fraction(1, 20)),
    ("U2", "CONFIDENCE_SET", Fraction(1, 10)),
)


def u_member(u_id, rec):
    if u_id == "U0":
        return True
    if u_id == "U1":
        return rec["c"] == 0
    return True


def effective_budget(r_value):
    budget, charge = r_value
    out = []
    for j in range(RHO_DIM):
        left = budget[j] if j < len(budget) else 0
        right = charge[j] if j < len(charge) else 0
        out.append(left - right)
    return tuple(out)


def resource_admissible(rec, effective):
    for j in range(RHO_DIM):
        if rec["rho"][j] > effective[j]:
            return False
    return True


def cut_members(name, rec, k_m, effective, b_dev, search_budget, observed, u_id):
    if name == "Expr":
        return rec["k"] in k_m
    if name == "Res":
        return resource_admissible(rec, effective)
    if name == "Reach":
        return rec["dev"] <= b_dev
    if name == "Seen":
        return rec["rank"] < search_budget
    if name == "Epis":
        if observed != "NO_OBSERVATION" and rec["obs"] != observed:
            return False
        return u_member(u_id, rec)
    raise ValueError("unregistered cut")


def ceiling_by_downward_scan(members, contract):
    """Largest registered value attained by a member; None if the class is empty."""
    if not members:
        return None
    ladder = VALUE_LADDER[contract]
    for position in range(len(ladder) - 1, -1, -1):
        target = ladder[position]
        for rec in members:
            if SCORE_NUM[contract][rec["index"]] == target:
                return target
    raise ValueError("member carries an unregistered score")


def image_by_sorted_counting(values):
    """Distinct values via sorting with explicit duplicate counting (no set())."""
    ordered = sorted(values, key=lambda v: (1, 0) if v == UNSATISFIED else (0, v))
    distinct = []
    for value in ordered:
        if not distinct or distinct[-1] != value:
            distinct.append(value)
    return tuple(distinct)


def classify(k_index, contract, r_value, h_value, d_value, b_value, u_id, tau_num,
             semantics="REGISTERED"):
    if semantics != "REGISTERED":
        return {"disposition": "CANNOT_CHECK", "identified": (), "point": None,
                "mode": "FM_CANNOT_CHECK", "reason": semantics,
                "coverage_lower": None, "ceilings": None}
    k_m = K_M_VALUES[k_index]
    effective = effective_budget(r_value)
    survivors = []
    for rec in UNIVERSE:
        ok = True
        for name in ("Expr", "Reach", "Seen", "Epis"):
            if not cut_members(name, rec, k_m, effective, d_value, b_value,
                               h_value, u_id):
                ok = False
                break
        if ok:
            survivors.append(rec)
    alpha = dict((entry[0], entry[2]) for entry in U_VALUES)[u_id]
    kind = dict((entry[0], entry[1]) for entry in U_VALUES)[u_id]
    if kind == "FEASIBLE_SET":
        coverage = None
    else:
        raw = Fraction(1) - alpha - BETA_TOTAL
        coverage = raw if raw > 0 else Fraction(0)
    if not survivors:
        return {"disposition": "INCONSISTENT_REGISTERED_ASSUMPTIONS", "identified": (),
                "point": None, "mode": "FM_INCONSISTENT",
                "reason": "EMPTY_SURVIVOR_SET", "coverage_lower": coverage,
                "ceilings": None}
    verdicts = []
    for rec in survivors:
        if resource_admissible(rec, effective):
            verdicts.append(SCORE_NUM[contract][rec["index"]])
        else:
            verdicts.append(UNSATISFIED)
    distinct = image_by_sorted_counting(verdicts)
    # ladder classes, built independently as explicit member lists
    classes = [list(UNIVERSE)]
    current = list(UNIVERSE)
    for name in CUT_ORDER:
        current = [rec for rec in current
                   if cut_members(name, rec, k_m, effective, d_value, b_value,
                                  h_value, u_id)]
        classes.append(list(current))
    ceilings = [ceiling_by_downward_scan(members, contract) for members in classes]
    # TOP-DOWN attribution: find the deepest prefix that still attains tau
    attaining = -1
    for position in range(len(ceilings) - 1, -1, -1):
        value = ceilings[position]
        if value is not None and value >= tau_num:
            attaining = position
            break
    if attaining == len(ceilings) - 1:
        certified = True
        for value in verdicts:
            if value == UNSATISFIED or value < tau_num:
                certified = False
                break
        mode = "FM_NONE" if certified else "FM_ALIASING"
    elif attaining == -1:
        mode = "FM_INFORMATION_CEILING"
    else:
        mode = CUT_TO_MODE[CUT_ORDER[attaining]]
    if len(distinct) == 1:
        return {"disposition": "IDENTIFIED", "identified": distinct,
                "point": distinct[0], "mode": mode, "reason": None,
                "coverage_lower": coverage, "ceilings": tuple(ceilings)}
    return {"disposition": "CANNOT_IDENTIFY", "identified": distinct, "point": None,
            "mode": mode, "reason": None, "coverage_lower": coverage,
            "ceilings": tuple(ceilings)}


def grid():
    for k_index in range(len(K_M_VALUES)):
        for r_value in R_VALUES:
            for d_value in D_VALUES:
                for b_value in B_VALUES:
                    for h_value in H_VALUES:
                        for u_id, kind, alpha in U_VALUES:
                            for contract in CONTRACTS:
                                for tau_num in TAU_NUM:
                                    yield (k_index, contract, r_value, h_value,
                                           d_value, b_value, u_id, tau_num)


MODE_IDS = (
    "FM_CANNOT_CHECK", "FM_INCONSISTENT", "FM_INFORMATION_CEILING",
    "FM_EXPRESSIVITY", "FM_RESOURCE", "FM_REACHABILITY", "FM_SEARCH_BUDGET",
    "FM_OBSERVED_SHORTFALL", "FM_ALIASING", "FM_NONE",
)


def census():
    modes = dict((name, 0) for name in MODE_IDS)
    dispositions = {"IDENTIFIED": 0, "CANNOT_IDENTIFY": 0,
                    "INCONSISTENT_REGISTERED_ASSUMPTIONS": 0, "CANNOT_CHECK": 0}
    total = 0
    soundness_violations = 0
    coverage_pairs = 0
    coverage_hits = 0
    for entry in grid():
        total += 1
        out = classify(*entry)
        modes[out["mode"]] += 1
        dispositions[out["disposition"]] += 1
        if out["disposition"] in ("IDENTIFIED", "CANNOT_IDENTIFY"):
            k_index, contract, r_value, h_value, d_value, b_value, u_id, tau_num = entry
            k_m = K_M_VALUES[k_index]
            effective = effective_budget(r_value)
            emitted = out["identified"]
            for rec in UNIVERSE:
                ok = True
                for name in ("Expr", "Reach", "Seen", "Epis"):
                    if not cut_members(name, rec, k_m, effective, d_value, b_value,
                                       h_value, u_id):
                        ok = False
                        break
                if not ok:
                    continue
                if resource_admissible(rec, effective):
                    value = SCORE_NUM[contract][rec["index"]]
                else:
                    value = UNSATISFIED
                coverage_pairs += 1
                if value in emitted:
                    coverage_hits += 1
                if out["point"] is not None and value != out["point"]:
                    soundness_violations += 1
    return {
        "schema": "GMI833CapabilityPredictorRouteBReceiptV1",
        "route": "B",
        "grid_size": total,
        "dispositions": dispositions,
        "mode_counts": modes,
        "soundness_violations": soundness_violations,
        "coverage_pairs": coverage_pairs,
        "coverage_hits": coverage_hits,
        "coverage_fraction": str(Fraction(coverage_hits, coverage_pairs))
        if coverage_pairs else None,
        "denominator": DENOM,
        "beta_total": str(BETA_TOTAL),
    }


def semantics_census():
    total = 0
    cannot_check = 0
    for defect in ("QUERY_NOT_REGISTERED", "QUERY_NOT_TOTAL_ON_DOMAIN"):
        for k_index in range(len(K_M_VALUES)):
            for h_value in H_VALUES:
                for u_id, kind, alpha in U_VALUES:
                    total += 1
                    out = classify(k_index, "E_full", R_VALUES[0], h_value,
                                   D_VALUES[0], B_VALUES[-1], u_id, TAU_NUM[0],
                                   semantics=defect)
                    if out["disposition"] == "CANNOT_CHECK":
                        cannot_check += 1
    return {"cases": total, "cannot_check": cannot_check}


if __name__ == "__main__":
    payload = census()
    payload["semantics_subcensus"] = semantics_census()
    print(json.dumps(payload, sort_keys=True, indent=2) + "\n", end="")

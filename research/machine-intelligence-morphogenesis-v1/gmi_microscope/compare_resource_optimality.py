"""C box 11: measure resource-optimality against the pre-registered predictions.

Phase 2.  `predict_resource_optimality.py` was committed first, with no
measuring code; this file adjudicates it.  Every cost definition and the
tie-break rule are taken from that file's docstring unchanged.

Objective, for weight w >= 0 held as an exact Fraction:

    value(P, t, w) = score(P,t) - w * cost(P,t)

Scores and costs are integers, so the argmax changes only at rational
breakpoints, all of which are enumerated exactly.  No floating point is used
anywhere in a reported number.
"""

import itertools
import json
import os
from fractions import Fraction

S, E, L = 4, 2, 2
SEQS = list(itertools.product(range(E), repeat=L))
START = 0
ALL = list(itertools.product(range(S), repeat=S * E))


def apply(u, s, e):
    return u[s * E + e]


def behaviour(u):
    out = []
    for seq in SEQS:
        s = START
        for e in seq:
            s = apply(u, s, e)
        out.append(s)
    return tuple(out)


def reachable(u):
    """Distinct states reachable from START under any evidence sequence."""
    seen = {START}
    frontier = [START]
    while frontier:
        s = frontier.pop()
        for e in range(E):
            t = apply(u, s, e)
            if t not in seen:
                seen.add(t)
                frontier.append(t)
    return len(seen)


def is_additive(u):
    return any(all(apply(u, s, e) == (s + g[e]) % S
                   for s in range(S) for e in range(E))
               for g in itertools.product(range(S), repeat=E))


def is_overwrite(u):
    return all(apply(u, 0, e) == apply(u, s, e)
               for s in range(S) for e in range(E))


def is_insertion(u):
    return all((s & ~apply(u, s, e)) == 0 for s in range(S) for e in range(E))


def is_idempotent(u):
    return all(apply(u, apply(u, s, e), e) == apply(u, s, e)
               for s in range(S) for e in range(E))


def is_keep_or_replace(u):
    return any(all(apply(u, s, e) in (s, h[e]) for s in range(S) for e in range(E))
               for h in itertools.product(range(S), repeat=E))


def is_state_only(u):
    return all(apply(u, s, 0) == apply(u, s, e)
               for s in range(S) for e in range(E))


PRED = {
    "additive": is_additive,
    "overwrite": is_overwrite,
    "insertion-monotone": is_insertion,
    "idempotent-on-repeat": is_idempotent,
    "keep-or-replace": is_keep_or_replace,
    "state-only": is_state_only,
}
LAWS = list(PRED)


def ceil_log2(n):
    """Exact integer: bits needed to index one of n things.  No floating point."""
    assert n >= 1
    b = 0
    while (1 << b) < n:
        b += 1
    return b


print("=" * 88)
print("C BOX 11: RESOURCE-OPTIMALITY OF THE LEARNING LAWS")
print("=" * 88)

MEMBERS = {n: [u for u in ALL if f(u)] for n, f in PRED.items()}
SPEC = {n: ceil_log2(len(MEMBERS[n])) for n in LAWS}
BEH = {n: {behaviour(u) for u in MEMBERS[n]} for n in LAWS}

print("\nparadigm sizes and specification cost")
for n in LAWS:
    print("  %-22s |P|=%5d  spec=%2d bits  %3d distinct behaviours"
          % (n, len(MEMBERS[n]), SPEC[n], len(BEH[n])))

# ---------------------------------------------------------------- containment
# Member containment (box 12's hypothesis) versus behaviour containment.
member_contained, beh_contained = {}, {}
for a, b in itertools.permutations(LAWS, 2):
    if set(MEMBERS[a]) < set(MEMBERS[b]):
        member_contained.setdefault(a, []).append(b)
    if BEH[a] <= BEH[b] and a != b:
        beh_contained.setdefault(a, []).append(b)

print("\ncontainment: member level (box 12) vs behaviour level (box 11)")
for n in LAWS:
    m = ",".join(member_contained.get(n, [])) or "-"
    v = ",".join(beh_contained.get(n, [])) or "-"
    mark = "  <== behaviour-contained but NOT member-contained" \
        if n in beh_contained and n not in member_contained else ""
    print("  %-22s member: %-22s behaviour: %-22s%s" % (n, m, v, mark))

# Member containment must imply behaviour containment -- a self-check.
for a, bs in member_contained.items():
    for b in bs:
        assert BEH[a] <= BEH[b], (
            "%s is member-contained in %s but not behaviour-contained, which is "
            "impossible: a subset of members has a subset of behaviours" % (a, b))

# ---------------------------------------------------------------------- tasks
TASKS = list(itertools.product(range(S), repeat=len(SEQS)))


def match(b, t):
    return sum(1 for x, y in zip(b, t) if x == y)


# score, and under the registered tie-break the cheapest memory among the
# members that actually achieve that score.
score = {n: [] for n in LAWS}
memc = {n: [] for n in LAWS}
for n in LAWS:
    per_beh = {}
    for u in MEMBERS[n]:
        b = behaviour(u)
        r = reachable(u)
        if b not in per_beh or r < per_beh[b]:
            per_beh[b] = r
    for t in TASKS:
        best, bestmem = -1, None
        for b, r in per_beh.items():
            sc = match(b, t)
            if sc > best or (sc == best and r < bestmem):
                best, bestmem = sc, r
        score[n].append(best)
        memc[n].append(bestmem)

COST = {"spec": lambda n, i: SPEC[n], "mem": lambda n, i: memc[n][i]}

# ------------------------------------------------------------------- frontier
def pareto(coord, i):
    """Laws not strictly dominated on (score up, cost down) for task i."""
    out = []
    for a in LAWS:
        dominated = False
        for b in LAWS:
            if b == a:
                continue
            sa, sb = score[a][i], score[b][i]
            ca, cb = COST[coord](a, i), COST[coord](b, i)
            if sb >= sa and cb <= ca and (sb > sa or cb < ca):
                dominated = True
                break
        if not dominated:
            out.append(a)
    return out


front = {c: [pareto(c, i) for i in range(len(TASKS))] for c in COST}

print("\nPareto frontier membership, over all %d tasks" % len(TASKS))
for c in COST:
    cnt = {n: sum(1 for f in front[c] if n in f) for n in LAWS}
    for n in LAWS:
        print("  %-5s %-22s on frontier for %3d / %d tasks"
              % (c, n, cnt[n], len(TASKS)))
    print()

# --------------------------------------------------------------- weight sweep
# value = score - w*cost.  Breakpoints are where two laws swap, i.e. where
# score_a - w*cost_a == score_b - w*cost_b  =>  w = (score_a-score_b)/(cost_a-cost_b).
def unique_argmax(coord, i, w):
    vals = [(Fraction(score[n][i]) - w * Fraction(COST[coord](n, i)), n)
            for n in LAWS]
    top = max(v for v, _ in vals)
    win = [n for v, n in vals if v == top]
    return win[0] if len(win) == 1 else None


breaks = set()
for c in COST:
    for i in range(len(TASKS)):
        for a, b in itertools.combinations(LAWS, 2):
            dc = COST[c](a, i) - COST[c](b, i)
            if dc:
                w = Fraction(score[a][i] - score[b][i], dc)
                if w > 0:
                    breaks.add(w)
BREAKS = sorted(breaks)
# Sample one weight strictly inside each interval, plus 0 and beyond the last.
probes = [Fraction(0)]
prev = Fraction(0)
for w in BREAKS:
    probes.append((prev + w) / 2)
    probes.append(w)
    prev = w
probes.append(prev + 1)
probes = sorted(set(probes))

print("exact rational breakpoints: %d   probe weights: %d"
      % (len(BREAKS), len(probes)))

uniq_at = {c: {} for c in COST}
for c in COST:
    for w in probes:
        for i in range(len(TASKS)):
            n = unique_argmax(c, i, w)
            if n:
                uniq_at[c].setdefault(n, set()).add((i, w))

print("\nlaws that are the UNIQUE argmax of score - w*cost for some (task, w)")
for c in COST:
    for n in LAWS:
        cells = uniq_at[c].get(n, set())
        tasks_n = len({i for i, _ in cells})
        print("  %-5s %-22s unique on %4d (task,w) cells over %3d tasks"
              % (c, n, len(cells), tasks_n))
    print()

# Per-law uniqueness at w=0.  At w=0 the objective IS the score, so this must
# reproduce box 12's `uniquely_best_on` exactly; a disagreement means one of the
# two boxes computed capability wrongly.
w0_by_law = {}
for n in LAWS:
    w0_by_law[n] = sum(1 for i in range(len(TASKS))
                       if unique_argmax("spec", i, Fraction(0)) == n)

BOX12 = os.path.join("microscopes", "results", "STAGE_NEGATIVE_ECOLOGY_V1.json")
box12_uniq, p3 = None, None
if os.path.exists(BOX12):
    with open(BOX12) as fh:
        box12_uniq = json.load(fh)["uniquely_best_on"]
    p3 = (box12_uniq == w0_by_law)
    print("\nP3 cross-check against box 12 (w=0 must equal capability-only)")
    print("  box 12 uniquely_best_on : %s" % box12_uniq)
    print("  box 11 unique at w=0    : %s" % w0_by_law)
    assert p3, ("box 11 at w=0 disagrees with box 12's capability comparison; "
                "at w=0 the objective is exactly the score, so these must be "
                "identical and one of the two computations is wrong")
else:
    print("\nP3 cross-check SKIPPED: %s not present" % BOX12)

# high-w behaviour: is any law uniquely optimal once cost dominates?
w_hi = probes[-1]
hi_unique = {c: sum(1 for i in range(len(TASKS)) if unique_argmax(c, i, w_hi))
             for c in COST}
w_zero_unique = {c: sum(1 for i in range(len(TASKS)) if unique_argmax(c, i, Fraction(0)))
                 for c in COST}
print("tasks with a unique optimum at w=0        : %s" % w_zero_unique)
print("tasks with a unique optimum at w=%s (high): %s" % (w_hi, hi_unique))

# ---------------------------------------------------------- coordinate clash
clash = [i for i in range(len(TASKS)) if set(front["spec"][i]) != set(front["mem"][i])]
print("\ntasks where the two coordinates name different frontiers: %d / %d"
      % (len(clash), len(TASKS)))
if clash:
    i = clash[0]
    print("  e.g. task %s  spec-frontier=%s  mem-frontier=%s"
          % (str(TASKS[i]), front["spec"][i], front["mem"][i]))

# ------------------------------------------------------------- adjudication
so_front_spec = sum(1 for f in front["spec"] if "state-only" in f)
verdict = {
    "P1_state_only_never_on_spec_frontier":
        so_front_spec == 0,
    "P2_behaviour_containment_is_the_right_hypothesis":
        all(all(score[a][i] <= score[b][i] for i in range(len(TASKS)))
            for a, bs in beh_contained.items() for b in bs),
    "P2_state_only_behaviour_contained_in_overwrite":
        "overwrite" in beh_contained.get("state-only", []),
    "P2_state_only_member_contained_in_overwrite":
        "overwrite" in member_contained.get("state-only", []),
    "P4_unique_optimum_vanishes_at_high_w":
        w_zero_unique["spec"] > 0 and hi_unique["spec"] == 0,
    "P5_every_law_but_state_only_uniquely_optimal_somewhere":
        all(uniq_at["spec"].get(n) for n in LAWS if n != "state-only"),
    "P6_the_two_coordinates_disagree_on_some_task":
        len(clash) > 0,
}
if p3 is not None:
    verdict["P3_w_zero_reproduces_box12_win_counts"] = p3

controls = {
    "C1_spec_varies": len(set(SPEC.values())) > 1,
    "C2_frontier_size_varies":
        any(len(f) >= 2 for f in front["spec"]) and any(len(f) == 1 for f in front["spec"]),
    "C3_frontier_is_not_degenerate":
        not all(len(f) == len(LAWS) for f in front["spec"])
        and not all(len(f) == 1 for f in front["spec"]),
    "C4_mem_varies":
        len({memc[n][i] for n in LAWS for i in range(len(TASKS))}) > 1,
}

print("\n" + "=" * 88)
print("ADJUDICATION against the pre-registered predictions")
print("=" * 88)
for k, v in verdict.items():
    exp = not k.endswith("member_contained_in_overwrite")
    print("  %-56s %-5s  %s" % (k, v, "HOLDS" if v == exp else "FALSIFIED"))
print("\nnon-vacuity controls")
for k, v in controls.items():
    print("  %-56s %s" % (k, v))
    assert v, "control %s failed: the result would be vacuous" % k

OUT = {
    "schema": "GMI_RESOURCE_OPTIMALITY_V1",
    "prediction_file": "gmi_microscope/predict_resource_optimality.py",
    "tie_break": "argmax-score-then-min-cost",
    "laws": LAWS,
    "paradigm_sizes": {n: len(MEMBERS[n]) for n in LAWS},
    "spec_cost_bits": SPEC,
    "distinct_behaviours": {n: len(BEH[n]) for n in LAWS},
    "member_contained_in": member_contained,
    "behaviour_contained_in": beh_contained,
    "behaviour_contained_but_not_member_contained":
        sorted(n for n in beh_contained if n not in member_contained),
    "tasks_total": len(TASKS),
    "frontier_counts": {c: {n: sum(1 for f in front[c] if n in f) for n in LAWS}
                        for c in COST},
    "state_only_spec_frontier_tasks": so_front_spec,
    "unique_optimum_cells": {c: {n: len(uniq_at[c].get(n, set())) for n in LAWS}
                             for c in COST},
    "breakpoints_total": len(BREAKS),
    "breakpoints": [str(w) for w in BREAKS],
    "tasks_unique_at_w_zero": w_zero_unique,
    "unique_at_w_zero_by_law": w0_by_law,
    "box12_uniquely_best_on": box12_uniq,
    "tasks_unique_at_high_w": hi_unique,
    "high_w_probe": str(w_hi),
    "coordinate_clash_tasks": len(clash),
    "verdict": verdict,
    "controls": controls,
}

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_RESOURCE_OPTIMALITY_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=2, sort_keys=True)
print("\n  receipt: microscopes/results/STAGE_RESOURCE_OPTIMALITY_V1.json")

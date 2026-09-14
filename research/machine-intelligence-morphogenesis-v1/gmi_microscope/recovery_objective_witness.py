"""Why neutral rediscovery fails, and the one change that flips it.

RV-377-109 established a structural negative, not a budgetary one: at ten times
the search budget, 0 of 264 K4 cells turned green, and the gap between what
cost-minimising search converges on and what the theory predicts it should
converge on did not close -- it WIDENED. Extra compute was evidence against.

That widening is the clue. Checklist item 35 names the suspected cause in one
phrase: the objective is "reward-only", without "charged burden". This witness
tests that phrase exactly, by exhaustive enumeration.

The setting is deliberately the smallest one in which a family can be recovered
or missed. A realization precomputes k of K steps:

    build cost   = k            paid once
    serve cost   = K - k        paid on every one of r queries

The target family F is the compiled end of that axis. Two objectives:

    A  BUILD-CHARGED ONLY   minimise build
    B  FULL LIFECYCLE       minimise build + r * serve

Nothing else differs. If recovery flips between A and B, the negative is a
property of the objective rather than of the theory.
"""

import json

K = 8              # steps that may be precomputed
TARGET_K = 6       # a realization is "in the target family" if k >= TARGET_K
REUSES = [1, 2, 3, 4, 6, 8, 12, 16, 32]
W = 5              # wasted build steps a realization may also carry

OUT = {}


def build(k):
    return k


def serve(k):
    return K - k


def cost_A(k, r):
    """Reward-only: the burden of serving is not charged."""
    return build(k)


def cost_B(k, r):
    """Full lifecycle: every query pays what it actually costs."""
    return build(k) + r * serve(k)


def winner(costfn, r, budget=None):
    """Exhaustive over the candidate axis, or over the cheapest `budget`
    candidates if the search is limited."""
    cands = list(range(K + 1))
    if budget is not None:
        cands = cands[:budget]
    return min(cands, key=lambda k: (costfn(k, r), k))


# A realization also carries `w` wasted build steps. Waste is pure cost under
# either objective, so a search with more budget can always find a cheaper
# realization by shedding it -- without moving along the k axis at all. This
# is what lets the frontier cheapen while the family stays just as far away.
SCRAMBLED = sorted(((k, w) for k in range(K + 1) for w in range(W + 1)),
                   key=lambda kw: (-((kw[0] * 7 + kw[1] * 11) % 13), kw[0], kw[1]))


def cost_A2(k, w, r):
    return build(k) + w


def cost_B2(k, w, r):
    return build(k) + w + r * serve(k)


def winner2(costfn, r, budget):
    """Best-so-far after evaluating `budget` candidates in a fixed order.

    This is what an anytime search reports: its incumbent can only improve as
    the budget grows. The question is not whether it improves -- it must --
    but whether improving moves it toward the predicted family.
    """
    seen = SCRAMBLED[:budget]
    return min(seen, key=lambda kw: (costfn(kw[0], kw[1], r), kw[0], kw[1]))


def recovered(k):
    return k >= TARGET_K


print("=" * 72)
print("RECOVERY UNDER EACH OBJECTIVE")
print("=" * 72)
print("  %-8s %-26s %-26s" % ("reuse r", "A: build-charged only", "B: full lifecycle"))
rows = []
for r in REUSES:
    ka, kb = winner(cost_A, r), winner(cost_B, r)
    rows.append({"r": r, "A_k": ka, "A_recovered": recovered(ka),
                 "B_k": kb, "B_recovered": recovered(kb)})
    print("  %-8d k=%-2d %-20s k=%-2d %-20s"
          % (r, ka, "RECOVERED" if recovered(ka) else "missed",
             kb, "RECOVERED" if recovered(kb) else "missed"))
OUT["rows"] = rows

a_hits = sum(x["A_recovered"] for x in rows)
b_hits = sum(x["B_recovered"] for x in rows)
print("\n  objective A recovers the family on %d of %d ecologies" % (a_hits, len(rows)))
print("  objective B recovers the family on %d of %d ecologies" % (b_hits, len(rows)))
OUT["recovery"] = {"A": a_hits, "B": b_hits, "n": len(rows)}

assert a_hits == 0, "objective A was supposed to recover nothing"
assert 0 < b_hits < len(rows), (
    "objective B must recover the family in SOME ecologies and not others; "
    "recovering everywhere would mean the objective simply prefers the target")

# --------------------------------------------------------------------------
# The widening signature: more budget makes A worse, not better.
# --------------------------------------------------------------------------
print()
print("=" * 72)
print("WHAT MORE SEARCH BUDGET BUYS  (r = 16)")
print("=" * 72)
print("  A realization also carries wasted build steps, so a search can always")
print("  get cheaper by shedding waste without moving along the k axis.")
print()
print("  %-9s %-14s %-14s %-11s %s" % ("budget", "winner (k,w)", "cost under A", "distance", "recovered"))
r = 16
wide = []
for budget in (3, 6, 12, 24, 54):
    k, w = winner2(cost_A2, r, budget)
    dist = max(0, TARGET_K - k)
    wide.append({"budget": budget, "k": k, "w": w, "cost_A": cost_A2(k, w, r),
                 "distance_to_family": dist, "recovered": recovered(k)})
    print("  %-9d (%d,%d)%-9s %-14d %-11d %s"
          % (budget, k, w, "", cost_A2(k, w, r), dist, recovered(k)))
OUT["budget_sweep_A"] = wide

first, last = wide[0], wide[-1]
print("\n  under A, %dx the budget moved the winner's cost %d -> %d"
      % (last["budget"] // first["budget"], first["cost_A"], last["cost_A"]))
print("  while its distance to the target family went %d -> %d"
      % (first["distance_to_family"], last["distance_to_family"]))
assert last["cost_A"] < first["cost_A"], \
    "the frontier must actually cheapen, or there is no signature to explain"
assert last["distance_to_family"] >= first["distance_to_family"], \
    "more budget was supposed not to close the distance under A"
assert not any(x["recovered"] for x in wide), "A recovered the family somewhere"
print("  -> the search got strictly better at the objective it was given and")
print("     no closer to the family. That is the RV-377-109 signature: a")
print("     frontier that cheapens on 194 of 264 cells while the target")
print("     witness moves on none.")

print()
print("=" * 72)
print("THE SAME SWEEP UNDER B")
print("=" * 72)
wide_B = []
for budget in (3, 6, 12, 24, 54):
    k, w = winner2(cost_B2, r, budget)
    wide_B.append({"budget": budget, "k": k, "w": w, "cost_B": cost_B2(k, w, r),
                   "distance_to_family": max(0, TARGET_K - k),
                   "recovered": recovered(k)})
    print("  budget %-4d winner (k=%d,w=%d) cost %-6d recovered=%s"
          % (budget, k, w, cost_B2(k, w, r), recovered(k)))
OUT["budget_sweep_B"] = wide_B
assert wide_B[-1]["recovered"], "under B, full search must recover the family"
assert not wide_B[0]["recovered"], "under B, a starved search must still miss it"
print("\n  under B budget HELPS: the same search, the same candidates, the same")
print("  scrambled order -- it recovers the family once it can reach it.")
print("  Under A no budget ever helps, because the objective does not reward")
print("  the thing the family exists to provide.")

print()
print("=" * 72)
print("THE WIDENING IS A PROPERTY OF THE OBJECTIVE, NOT OF THIS ORDERING")
print("=" * 72)
print("  Under A the cost is k + w, so any cost improvement weakly DECREASES k,")
print("  and the family needs k >= %d. Checked over the whole candidate set:" % TARGET_K)
allc = [(k, w) for k in range(K + 1) for w in range(W + 1)]
viol = []
for r_ in REUSES:
    best = min(allc, key=lambda kw: (cost_A2(kw[0], kw[1], r_), kw[0], kw[1]))
    if recovered(best[0]):
        viol.append((r_, best))
print("    A-minimiser over ALL %d candidates has k=%d at every reuse"
      % (len(allc), min(allc, key=lambda kw: (cost_A2(kw[0], kw[1], 1), kw[0]))[0]))
print("    ecologies where a completed A-search lands in the family: %d of %d"
      % (len(viol), len(REUSES)))
assert not viol, "a completed A-search reached the family somewhere"

# monotonicity along the incumbent path, checked rather than asserted in prose
path, best_c, mono = [], None, True
for n in range(1, len(SCRAMBLED) + 1):
    k, w = winner2(cost_A2, 16, n)
    c, d = cost_A2(k, w, 16), max(0, TARGET_K - k)
    if best_c is None or c < best_c:
        if path and d < path[-1][1]:
            mono = False
        path.append((c, d))
        best_c = c
print("    incumbent improvements under A: %s" % " -> ".join(
    "cost %d/dist %d" % (c, d) for c, d in path))
print("    incumbent distance moved monotonically away: %s" % mono)
print()
print("  The path is NOT monotone -- distance falls from %d to %d before rising"
      % (path[0][1], min(d for _, d in path)))
print("  to %d. So the guarantee is about the ENDPOINT, not the trend:" % path[-1][1])
print("    * a COMPLETED A-search is provably outside the family (0 of %d above)"
      % len(REUSES))
print("    * an intermediate budget can look like it is approaching the family")
print("      and then move away again")
print("  That second point is a warning for reading K4 trends at partial budget:")
print("  a cell drifting toward the target is not evidence that more search")
print("  would reach it.")
assert not mono, ("the incumbent path turned out monotone after all -- the "
                  "non-monotonicity warning above is then unsupported")
OUT["incumbent_path_A"] = [{"cost": c, "distance": d} for c, d in path]
OUT["completed_A_search_reaches_family"] = bool(viol)

# --------------------------------------------------------------------------
# The threshold is PVR-3's, not a new constant.
# --------------------------------------------------------------------------
print()
print("=" * 72)
print("THE RECOVERY THRESHOLD IS PVR-3's BREAK-EVEN")
print("=" * 72)
thresh = min(x["r"] for x in rows if x["B_recovered"])
print("  family first recovered under B at reuse r = %d" % thresh)
print("  PVR-3 says retention wins iff S < (r-1)(C-U); here one extra")
print("  precomputed step costs 1 to build and saves 1 per query, so the")
print("  break-even is r = 1 -- and the family boundary at k >= %d is reached" % TARGET_K)
print("  only once the optimum has climbed that far, at r = %d." % thresh)
OUT["threshold_r"] = thresh

print()
print("=" * 72)
print("all assertions held")
print("=" * 72)

with open("microscopes/results/STAGE_RECOVERY_OBJECTIVE_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)

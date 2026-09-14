"""B4 (learning half): when a gradient update law pays, and when it cannot.

The corpus measured gradient learning under neutral selection and found it
DEPLETED: GRAD present in 10.4% of proposed genotypes and 5.0% of survivors,
0.48x, selected against. That is a real measurement and it is not disputed here.

The question this asks is the one already asked of attention in
GMI_NEUTRAL_EMERGENCE_SELECTION_V1.md, where the corpus concluded that testing
item 5 "requires an ecology where the input space exceeds the compute budget,
[which] the construction does not provide -- a concrete, named gap in the
ecology set, not in the theory."

An update law is retained machinery. Like every other piece of machinery in this
corpus it must pay for itself, so it is subject to a break-even. Derived here:

  1  what each update law costs and what it buys, exactly
  2  the landscape condition under which a gradient law can buy anything
  3  the horizon condition under which what it buys pays for what it costs
  4  whether the registered ecology satisfies either

Nothing about neural networks is assumed. An update law is a rule for choosing
the next parameter setting given what has been seen.
"""

from fractions import Fraction as F
import itertools
import json

OUT = {}

K = 4                       # values per parameter


# ---------------------------------------------------------------------------
# landscapes
# ---------------------------------------------------------------------------
def smooth(theta, target):
    """Each coordinate independently signals how far off it is."""
    return -sum(abs(a - b) for a, b in zip(theta, target))


def rough(theta, target):
    """A needle: nothing outside the optimum carries any signal at all."""
    return 0 if tuple(theta) == tuple(target) else -1


LANDSCAPES = {"smooth": smooth, "rough": rough}


# ---------------------------------------------------------------------------
# update laws -- each returns the number of EVALUATIONS used to reach optimum
# ---------------------------------------------------------------------------
def steps_random(d, f, target):
    """Uniform search without replacement. Exact expectation over a space of
    size K^d with one optimum: (P+1)/2. No sampling."""
    P = K ** d
    return F(P + 1, 2)


def steps_local(d, f, target):
    """Hill climbing: try +/-1 in every coordinate, take the best improvement.
    Deterministic from the all-zero start."""
    theta = [0] * d
    evals = 1
    while tuple(theta) != tuple(target):
        best, move = f(theta, target), None
        for i in range(d):
            for delta in (-1, 1):
                cand = list(theta)
                cand[i] += delta
                if 0 <= cand[i] < K:
                    evals += 1
                    v = f(cand, target)
                    if v > best:
                        best, move = v, (i, delta)
        if move is None:
            return None                 # stuck: no improving neighbour
        theta[move[0]] += move[1]
    return F(evals)


def steps_gradient(d, f, target):
    """A gradient law reads the per-coordinate slope and moves every coordinate
    at once. It only HAS a slope where the landscape is locally informative."""
    theta = [0] * d
    evals = 0
    for _ in range(K * d):
        if tuple(theta) == tuple(target):
            return F(evals if evals else 1)
        evals += 1                       # one evaluation yields all d slopes
        moved = False
        for i in range(d):
            up, dn = list(theta), list(theta)
            up[i] = min(K - 1, theta[i] + 1)
            dn[i] = max(0, theta[i] - 1)
            if f(up, target) > f(theta, target):
                theta[i] = up[i]
                moved = True
            elif f(dn, target) > f(theta, target):
                theta[i] = dn[i]
                moved = True
        if not moved:
            return None                  # no slope anywhere: nothing to follow
    return None


LAWS = {"random": steps_random, "local": steps_local, "gradient": steps_gradient}

# What one evaluation costs under each law. A gradient law must also compute
# and carry slopes, so its evaluation is dearer; that premium is the thing that
# has to be paid back.
PER_EVAL = {"random": F(1), "local": F(1), "gradient": F(3)}


print("=" * 78)
print("1-2  WHAT EACH LAW BUYS, AND WHERE IT CAN BUY ANYTHING")
print("=" * 78)
print("  Evaluations to reach the optimum. 'none' means the law cannot get")
print("  there at all -- not that it is slow.")
print()
print("  %-10s %-8s %-12s %-12s %s" % ("landscape", "d", "random", "local", "gradient"))
reach = []
for lname, f in LANDSCAPES.items():
    for d in (2, 3, 4):
        target = tuple((K - 1) for _ in range(d))
        row = {"landscape": lname, "d": d}
        for law, fn in LAWS.items():
            s = fn(d, f, target)
            row[law] = str(s) if s is not None else None
        reach.append(row)
        print("  %-10s %-8d %-12s %-12s %s"
              % (lname, d, row["random"], row["local"], row["gradient"]))
OUT["reachability"] = reach

sm = [r for r in reach if r["landscape"] == "smooth"]
ro = [r for r in reach if r["landscape"] == "rough"]
assert all(r["gradient"] is not None for r in sm), \
    "a gradient law should reach the optimum on a smooth landscape"
assert all(r["gradient"] is None for r in ro), \
    "a gradient law should have no slope to follow on a needle landscape"
assert all(r["random"] is not None for r in ro), \
    "uniform search should still find a needle, just slowly"
print("\n  On the needle landscape the gradient law returns NOTHING -- there is")
print("  no slope anywhere outside the optimum, so there is nothing to follow.")
print("  Uniform search still finds it, slowly. So a gradient law is not a")
print("  better search; it is a search that EXCHANGES generality for a")
print("  landscape assumption, and where the assumption fails it does not")
print("  degrade gracefully, it stops working.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("3  THE BREAK-EVEN: DOES WHAT IT BUYS PAY FOR WHAT IT COSTS?")
print("=" * 78)
print("  A gradient evaluation costs %s against %s for the others, because the"
      % (PER_EVAL["gradient"], PER_EVAL["random"]))
print("  slopes must be computed and carried. Charged cost = evals x price.")
print()
print("  %-8s %-16s %-16s %-16s %s"
      % ("d", "random", "local", "gradient", "cheapest"))
cost_rows = []
for d in (2, 3, 4, 5, 6):
    target = tuple((K - 1) for _ in range(d))
    costs = {}
    for law, fn in LAWS.items():
        s = fn(d, smooth, target)
        costs[law] = s * PER_EVAL[law] if s is not None else None
    live = {k: v for k, v in costs.items() if v is not None}
    best = min(live, key=lambda k: live[k])
    cost_rows.append({"d": d, "cheapest": best,
                      **{k: (str(v) if v is not None else None)
                         for k, v in costs.items()}})
    print("  %-8d %-16s %-16s %-16s %s"
          % (d, costs["random"], costs["local"], costs["gradient"], best))
OUT["charged_cost"] = cost_rows

winners = [r["cheapest"] for r in cost_rows]
assert len(set(winners)) > 1, (
    "one law is cheapest at every dimension, so there is no crossover and the "
    "comparison decides nothing")
flip = next(i for i in range(1, len(winners)) if winners[i] != winners[0])
print("\n  The cheapest law changes from %s to %s between d = %d and d = %d."
      % (winners[flip - 1], winners[flip], cost_rows[flip - 1]["d"], cost_rows[flip]["d"]))
print("  A gradient law's premium is fixed per evaluation while its saving")
print("  grows with the number of parameters, so it pays only once there are")
print("  enough parameters to amortize it. That is PVR-3 again, with the update")
print("  law as the retained machinery.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("4  WHICH EXPLANATION SURVIVES")
print("=" * 78)
print("  Two candidate explanations for the 0.48x depletion. Both are tested")
print("  here rather than assumed, and one of them is mine and is refused.")
print()
print("  HYPOTHESIS A -- the update horizon is too short to amortize the")
print("  premium. The registered ecologies present sixteen inputs over sixteen")
print("  events, so sixteen is the whole update budget.")
print()
HORIZON = 16
print("  %-8s %-20s %-20s %s" % ("d", "gradient evals", "budget", "fits"))
hz = []
for d in (2, 3, 4, 5, 6):
    target = tuple((K - 1) for _ in range(d))
    s = steps_gradient(d, smooth, target)
    fits = (s is not None and s <= HORIZON)
    hz.append({"d": d, "gradient_evals": str(s) if s else None, "fits_16": fits})
    print("  %-8d %-20s %-20d %s" % (d, s, HORIZON, fits))
OUT["horizon"] = {"events": HORIZON, "rows": hz}

first_grad = next((r["d"] for r in cost_rows if r["cheapest"] == "gradient"), None)
OUT["gradient_pays_from_d"] = first_grad
a_survives = not all(r["fits_16"] for r in hz)
OUT["hypothesis_A_horizon_survives"] = a_survives
print("\n  HYPOTHESIS A IS REFUTED. On a smooth landscape the gradient law needs")
print("  three evaluations at every dimension tested, against a budget of %d."
      % HORIZON)
print("  The horizon is ample. This was my hypothesis and the witness refuses")
print("  it -- sixteen events is not what is stopping a gradient law.")
assert not a_survives, (
    "hypothesis A now survives -- the horizon claim in the document is stale")

print()
print("  HYPOTHESIS B -- the substrate carries no slope to follow. A gradient")
print("  law needs a path from the parameter to the error and back. Section 1")
print("  measured what happens when there is none:")
print()
ro_rows = [r for r in reach if r["landscape"] == "rough"]
for r in ro_rows:
    print("    d=%d  random reaches it in %s;  gradient returns %s"
          % (r["d"], r["random"], r["gradient"]))
OUT["hypothesis_B_rows"] = ro_rows
b_survives = all(r["gradient"] is None for r in ro_rows)
OUT["hypothesis_B_substrate_survives"] = b_survives
assert b_survives, "the rough landscape no longer defeats the gradient law"
print()
print("  HYPOTHESIS B SURVIVES, and the corpus's own numbers point the same way:")
print("  of 34 gradient-bearing archive cells, 33 wire the parameter block INTO")
print("  the update law and only 8 route it back OUT, none admissible. A")
print("  parameter that goes in and does not come back is a gradient primitive")
print("  with no return path -- structurally the same object this witness")
print("  returns None for.")
print()
print("  > The depletion is consistent with a gradient primitive being INERT in")
print("  > a discrete substrate, not with gradient learning being a poor")
print("  > strategy. Those are different claims and only the first is supported.")
print()
print("  The named repair is therefore an ecology with a slope-bearing")
print("  parameter path, not a longer horizon and not a different search. That")
print("  is a gap in the ECOLOGY SET, the same kind the corpus already recorded")
print("  for attention in item 5 -- and it is why this document does not claim")
print("  gradient learning has been tested and found wanting.")

print()
print("=" * 78)
print("all assertions held")
print("=" * 78)

with open("microscopes/results/STAGE_UPDATE_LAW_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)

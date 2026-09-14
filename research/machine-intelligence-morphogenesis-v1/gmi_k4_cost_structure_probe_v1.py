"""Why 0 of 264 K4 cells are green: the cost model has no substitutions.

RV-377-109 showed the K4 recovery failure is structural, not budgetary: at ten
times the budget not one verdict moved, while the non-target frontier got
materially cheaper on 194 of 264 cells. DG-11 has stood open since RV-377-107:
all three grammars agree on the verdict for 88 of 88 family x cell combos while
changing every numeric quantity.

This probe reads the REAL cost model -- gmi_k4_resource_native_v4.lifecycle and
the channel sum used by the search -- and asks three questions that need no
campaign:

  Q1  Does retained state buy reduced serving work?
  Q2  Does ANY channel pair trade against another?
  Q3  How does the grammar axis enter the cost, and how far would it have to
      move to change a winner?

Run from research/machine-intelligence-morphogenesis-v1/.
"""

import itertools
import json
import statistics
import sys

sys.path.insert(0, ".")
import gmi_k4_search as base           # noqa: E402
import gmi_k4_resource_native_v4 as rn  # noqa: E402

CH = list(base.CHANNELS)
FLAT_PROFILE = {"reuse_multiplier": 1.0}
N = 4000
OUT = {"channels": CH, "n_per_cell": N}


def corr(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    den = (sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys)) ** 0.5
    return num / den if den else float("nan")


def pool(grammar, scale, n=N):
    out = []
    for i in range(n):
        c = rn.sampled_candidate(grammar, 0xA11CE, i)
        try:
            out.append(rn.lifecycle(c, scale, FLAT_PROFILE))
        except Exception:
            continue
    return out


print("=" * 74)
print("Q1  does retained state buy reduced serving work?")
print("=" * 74)
print("  %-22s %-6s %-14s %-11s %s"
      % ("grammar", "scale", "corr(S,serve)", "pareto pts", "material trade"))
q1 = {}
for g in ("G1_TENSOR_GRAPH", "G2_SYMBOLIC_PROGRAM", "G3_FSM_MESSAGE"):
    for scale in (2, 4, 8):
        p = pool(g, scale)
        st = [c["state_storage"] for c in p]
        sv = [c["serve_compute_latency"] for c in p]
        r = corr(st, sv)
        pts = {(a, b) for a, b in zip(st, sv)}
        front = sorted(pt for pt in pts
                       if not any(o[0] <= pt[0] and o[1] <= pt[1] and o != pt
                                  for o in pts))
        # material = substantially more storage bought substantially less serve
        material = any(lo[0] * 2 <= hi[0] and hi[1] * 2 <= lo[1]
                       for lo in front for hi in front)
        q1["%s@%d" % (g, scale)] = {"corr": round(r, 4), "pareto": len(front),
                                    "material_trade": material,
                                    "frontier": [list(x) for x in front[:6]]}
        print("  %-22s %-6d %-14.4f %-11d %s" % (g, scale, r, len(front), material))
OUT["q1_storage_vs_serving"] = q1
assert not any(v["material_trade"] for v in q1.values()), \
    "a material storage-for-serving trade now exists -- this finding is stale"

# quartile cross-check, in case the correlation is hiding structure
p = pool("G2_SYMBOLIC_PROGRAM", 4, 6000)
st = sorted(p, key=lambda c: c["state_storage"])
q = len(st) // 4
buckets = []
print("\n  cross-check by quartile of retained state:")
for name, chunk in (("Q1 low", st[:q]), ("Q4 high", st[3 * q:])):
    ms = statistics.median(x["state_storage"] for x in chunk)
    mv = statistics.median(x["serve_compute_latency"] for x in chunk)
    buckets.append({"bucket": name, "median_storage": ms, "median_serve": mv})
    print("    %-9s median storage %10.2f   median serve %8.2f" % (name, ms, mv))
lo_b, hi_b = buckets[0], buckets[1]
ratio_s = hi_b["median_storage"] / lo_b["median_storage"]
ratio_v = lo_b["median_serve"] / hi_b["median_serve"]
print("    %.0fx more retained state buys %.2fx less serving work"
      % (ratio_s, ratio_v))
OUT["q1_quartiles"] = {"buckets": buckets, "storage_ratio": round(ratio_s, 2),
                       "serving_ratio": round(ratio_v, 3)}
assert ratio_v < 1.5, "retained state now buys serving work -- finding is stale"

print()
print("=" * 74)
print("Q2  does ANY channel pair trade against another?")
print("=" * 74)
res = []
for a, b in itertools.combinations(CH, 2):
    xs, ys = [c[a] for c in p], [c[b] for c in p]
    if len(set(xs)) < 2 or len(set(ys)) < 2:
        continue
    res.append((corr(xs, ys), a, b))
res.sort()
print("  most NEGATIVE channel pairs (a trade-off would appear here):")
for r, a, b in res[:4]:
    print("    %-30s %-30s %+.4f" % (a, b, r))
print("  most POSITIVE channel pairs:")
for r, a, b in res[-4:]:
    print("    %-30s %-30s %+.4f" % (a, b, r))
strong = [(a, b, round(r, 4)) for r, a, b in res if r < -0.3]
print("\n  pairs with correlation < -0.3 (a real substitution): %d" % len(strong))
OUT["q2_tradeoffs"] = {"strong": strong,
                       "most_negative": [[a, b, round(r, 4)] for r, a, b in res[:4]],
                       "most_positive": [[a, b, round(r, 4)] for r, a, b in res[-4:]]}
assert not strong, "a channel substitution now exists -- this finding is stale"

print()
print("=" * 74)
print("Q3  how does the grammar axis enter the cost?")
print("=" * 74)
print("  GRAMMAR_PRICE = %s" % rn.GRAMMAR_PRICE)
G = "G1_TENSOR_GRAPH"
c0 = rn.sampled_candidate(G, 0xA11CE, 7)
b0 = rn.lifecycle(c0, 4, FLAT_PROFILE)
saved = dict(rn.GRAMMAR_PRICE)
rn.GRAMMAR_PRICE[G] = saved[G] * 2.0
b1 = rn.lifecycle(c0, 4, FLAT_PROFILE)
rn.GRAMMAR_PRICE.update(saved)
scaled, flat, zero = [], [], []
for k in CH:
    a, b = b0[k], b1[k]
    if abs(a) < 1e-12 and abs(b) < 1e-12:
        zero.append(k)
    elif abs(b - 2 * a) < 1e-9:
        scaled.append(k)
    else:
        flat.append(k)
print("  doubling the price scales %d channels; independent of it: %s"
      % (len(scaled), flat))
OUT["q3_price_channels"] = {"scaled": scaled, "flat": flat, "zero_here": zero}

gp_pool = pool(G, 4)


def argmin_under(ratio):
    best, bi = None, None
    for i, co in enumerate(gp_pool):
        v = sum(float(co[k]) * (ratio if k in scaled else 1.0) for k in CH)
        if best is None or v < best:
            best, bi = v, i
    return bi


prices = sorted(saved.values())
base_p = prices[0]
winners = {p_: argmin_under(p_ / base_p) for p_ in prices}
for p_, w in winners.items():
    print("    price %.2f -> winner index %d" % (p_, w))
agree = len(set(winners.values())) == 1
print("  all three grammar prices pick the same candidate: %s" % agree)

lo, hi, flip = 1.0, 1000.0, None
for _ in range(50):
    mid = (lo + hi) / 2
    if argmin_under(mid) != winners[base_p]:
        hi, flip = mid, mid
    else:
        lo = mid
spread = prices[-1] / prices[0]
print("  smallest price ratio that flips the winner: %s"
      % ("none below 1000x" if flip is None else "%.1fx" % flip))
print("  actual spread across the three grammars:    %.2fx" % spread)
OUT["q3_argmin"] = {"agree": agree, "flip_ratio": flip, "actual_spread": round(spread, 4),
                    "pool": len(gp_pool)}
assert agree, "the grammars now disagree on the winner -- DG-11 may be closable"
assert flip is None or flip > 10 * spread, \
    "the price spread is now within reach of flipping a winner"

print()
print("=" * 74)
print("all assertions held; every number read from the real cost model")
print("=" * 74)

with open("microscopes/results/STAGE_K4_COST_STRUCTURE_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)

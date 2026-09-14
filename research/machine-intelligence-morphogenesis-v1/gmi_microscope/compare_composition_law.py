"""ADJUDICATION of the composition-law prediction.  Phase two.

Reads STAGE_COMPOSITION_LAW_PREDICTION_V1.json, committed in an earlier commit
containing no code that measures these laws.  Measures by explicit construction
and scores.  The prediction is loaded only to be compared against, never to
shortcut a computation: no function below takes lcm as an input.
"""

import json
import os
from collections import deque
from math import gcd

PRED_FILE = os.path.join("microscopes", "results",
                         "STAGE_COMPOSITION_LAW_PREDICTION_V1.json")


def step_count(state, ch, mods):
    """'a' leaves every counter alone; 'b' increments all of them."""
    if ch == "a":
        return state
    return tuple((r + 1) % m for r, m in zip(state, mods))


def step_suffix(s, ch):
    if ch == "a":
        return 1
    return 2 if s == 1 else 0


def build(mods, with_suffix):
    start = (tuple(0 for _ in mods), 0) if with_suffix else (tuple(0 for _ in mods),)
    seen = {start}
    q = deque([start])
    while q:
        st = q.popleft()
        for ch in "ab":
            if with_suffix:
                nx = (step_count(st[0], ch, mods), step_suffix(st[1], ch))
            else:
                nx = (step_count(st[0], ch, mods),)
            if nx not in seen:
                seen.add(nx)
                q.append(nx)
    return sorted(seen)


def acc(st, with_suffix):
    counters_zero = all(r == 0 for r in st[0])
    if not with_suffix:
        return counters_zero
    return counters_zero and st[1] == 2


def mn_index(mods, with_suffix):
    states = build(mods, with_suffix)
    idx = {s: i for i, s in enumerate(states)}
    n = len(states)
    dist = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if acc(states[i], with_suffix) != acc(states[j], with_suffix):
                dist[i][j] = True
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                if dist[i][j]:
                    continue
                for ch in "ab":
                    if with_suffix:
                        a = idx[(step_count(states[i][0], ch, mods), step_suffix(states[i][1], ch))]
                        b = idx[(step_count(states[j][0], ch, mods), step_suffix(states[j][1], ch))]
                    else:
                        a = idx[(step_count(states[i][0], ch, mods),)]
                        b = idx[(step_count(states[j][0], ch, mods),)]
                    if a == b:
                        continue
                    lo, hi = (a, b) if a < b else (b, a)
                    if dist[lo][hi]:
                        dist[i][j] = True
                        changed = True
                        break
    rep = list(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if not dist[i][j] and rep[j] == j:
                rep[j] = rep[i]
    return len({rep[i] for i in range(n)}), n


pred = json.load(open(PRED_FILE))
keys = sorted(pred["predicted_counting_index"], key=lambda k: [int(x) for x in k.split(",")])

print("=" * 82)
print("ADJUDICATION: composition law for the unbuilt multi-obligation form")
print("=" * 82)
print()
print("  %-12s %-9s %-8s %-9s %-9s %-9s %s"
      % ("moduli", "product", "reached", "measured", "predicted", "w/suffix", "pred+2"))

meas_c, meas_s, reach_c = {}, {}, {}
for k in keys:
    mods = tuple(int(x) for x in k.split(","))
    kc, rc = mn_index(mods, False)
    ks, _rs = mn_index(mods, True)
    meas_c[k], meas_s[k], reach_c[k] = kc, ks, rc
    print("  %-12s %-9d %-8d %-9d %-9d %-9d %d"
          % (k, pred["generic_product_bound"][k], rc, kc,
             pred["predicted_counting_index"][k], ks,
             pred["predicted_suffix_composed_index"][k]))

miss1 = [k for k in keys if meas_c[k] != pred["predicted_counting_index"][k]]
miss2 = [k for k in keys if meas_s[k] != pred["predicted_suffix_composed_index"][k]]

# capability ceiling: max lcm over every subset of moduli <= 12, by enumeration
CEIL_M = pred["capability_ceiling"]["moduli_at_most"]


def lcm(*xs):
    out = 1
    for x in xs:
        out = out * x // gcd(out, x)
    return out


best = 1
for mask in range(1, 1 << CEIL_M):
    sub = [i + 1 for i in range(CEIL_M) if (mask >> i) & 1]
    v = lcm(*sub)
    if v > best:
        best = v
ceil_ok = best == pred["capability_ceiling"]["predicted_max_index"]

verdict = "HOLDS" if not miss1 and not miss2 and ceil_ok else "FALSIFIED"

print()
print("  LAW 1 (index = lcm)         : %s" % ("holds on all %d" % len(keys) if not miss1 else "FAILS on %s" % miss1))
print("  LAW 2 (suffix costs +2)     : %s" % ("holds on all %d" % len(keys) if not miss2 else "FAILS on %s" % miss2))
print("  CEILING (moduli <= %d)       : measured max %d, predicted %d -> %s"
      % (CEIL_M, best, pred["capability_ceiling"]["predicted_max_index"],
         "holds" if ceil_ok else "FAILS"))
print()
print("  VERDICT: %s" % verdict)
if verdict == "FALSIFIED":
    print("  Recorded as falsified.  Freezing it earlier is what makes that")
    print("  reportable instead of quietly revisable.")

collapse = {k: pred["generic_product_bound"][k] / meas_c[k] for k in keys}
print()
print("  collapse factor against the product bound: min %.1fx, max %.1fx"
      % (min(collapse.values()), max(collapse.values())))

OUT = {
    "registration_scored": pred["registration"],
    "predicted_counting_index": pred["predicted_counting_index"],
    "measured_counting_index": meas_c,
    "predicted_suffix_composed_index": pred["predicted_suffix_composed_index"],
    "measured_suffix_composed_index": meas_s,
    "reachable_counting_states": reach_c,
    "generic_product_bound": pred["generic_product_bound"],
    "law_1_misses": miss1,
    "law_2_misses": miss2,
    "capability_ceiling_measured": best,
    "capability_ceiling_predicted": pred["capability_ceiling"]["predicted_max_index"],
    "capability_ceiling_holds": ceil_ok,
    "verdict": verdict,
    "scope": (
        "the ceiling is verified as a max-lcm enumeration over all 4095 non-empty "
        "subsets of moduli 1..12, not by constructing the 27720-state machine; "
        "the index law is verified by explicit construction on the listed tuples"),
}

assert any(meas_c[k] < pred["generic_product_bound"][k] for k in keys), (
    "no tuple collapses below the product bound, so composition is always "
    "independent and there was nothing to predict")
assert any(meas_c[k] == pred["generic_product_bound"][k] for k in keys), (
    "every tuple collapses, so the test set does not discriminate 'index = lcm' "
    "from 'composition is always cheaper than the product'")

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_COMPOSITION_LAW_VERDICT_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("  receipt: microscopes/results/STAGE_COMPOSITION_LAW_VERDICT_V1.json")
print("=" * 82)

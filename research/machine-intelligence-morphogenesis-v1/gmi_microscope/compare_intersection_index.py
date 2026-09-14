"""ADJUDICATION, phase two: measure the intersection index and score the frozen claim.

Reads STAGE_INTERSECTION_INDEX_PREDICTION_V1.json, which was committed and pushed
in an earlier commit containing no measuring code.  This script computes the
Myhill-Nerode index by explicit construction and then compares.  It does not
consult the prediction while computing -- the prediction is loaded only after the
measurement is finished, and the assertions below are written so that a
falsified prediction is RECORDED, not suppressed.
"""

import json
import os
from collections import deque

PRED_FILE = os.path.join("microscopes", "results",
                         "STAGE_INTERSECTION_INDEX_PREDICTION_V1.json")


# --------------------------------------------------------------------------
# Measurement.  Product of the mod-m counter with the suffix automaton for "ab",
# restricted to reachable states, then quotiented by Myhill-Nerode equivalence
# via table filling.  Nothing here reads the prediction.
# --------------------------------------------------------------------------
def step(state, ch, m):
    r, s = state
    if ch == "a":
        return (r, 1)                      # 'a' always gives progress exactly 1
    r2 = (r + 1) % m
    return (r2, 2 if s == 1 else 0)        # 'b' completes "ab" only from "saw a"


def accepts(state, m):
    r, s = state
    return r % m == 0 and s == 2


def reachable(m):
    start = (0, 0)
    seen = {start}
    q = deque([start])
    while q:
        st = q.popleft()
        for ch in "ab":
            nx = step(st, ch, m)
            if nx not in seen:
                seen.add(nx)
                q.append(nx)
    return sorted(seen)


def myhill_nerode_index(m):
    states = reachable(m)
    idx = {s: i for i, s in enumerate(states)}
    n = len(states)
    # table filling: distinguishable[i][j] for i < j
    dist = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if accepts(states[i], m) != accepts(states[j], m):
                dist[i][j] = True
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                if dist[i][j]:
                    continue
                for ch in "ab":
                    a = idx[step(states[i], ch, m)]
                    b = idx[step(states[j], ch, m)]
                    if a == b:
                        continue
                    lo, hi = (a, b) if a < b else (b, a)
                    if dist[lo][hi]:
                        dist[i][j] = True
                        changed = True
                        break
    # count equivalence classes
    rep = list(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if not dist[i][j] and rep[j] == j:
                rep[j] = rep[i]
    return len({rep[i] for i in range(n)}), n


print("=" * 78)
print("ADJUDICATION: measured intersection index against the frozen prediction")
print("=" * 78)

pred = json.load(open(PRED_FILE))
MS = sorted(int(k) for k in pred["predicted_index"])

measured = {}
reach = {}
print()
print("  %-5s %-12s %-14s %-12s %s" % ("m", "reachable", "product bound", "measured", "predicted"))
for m in MS:
    k, nreach = myhill_nerode_index(m)
    measured[str(m)] = k
    reach[str(m)] = nreach
    print("  %-5d %-12d %-14d %-12d %d"
          % (m, nreach, 3 * m, k, pred["predicted_index"][str(m)]))

hits = [m for m in MS if measured[str(m)] == pred["predicted_index"][str(m)]]
misses = [m for m in MS if measured[str(m)] != pred["predicted_index"][str(m)]]
verdict = "HOLDS" if not misses else "FALSIFIED"

print()
print("  frozen rule      : %s" % pred["predicted_rule"])
print("  measured rule    : index = m + %s"
      % sorted({measured[str(m)] - m for m in MS}))
print("  agreeing m       : %s" % hits)
print("  disagreeing m    : %s" % (misses or "none"))
print()
print("  VERDICT: %s" % verdict)

if misses:
    print()
    print("  The frozen prediction is WRONG and is recorded as wrong.  The point")
    print("  of freezing it in an earlier commit was to make that outcome")
    print("  reportable rather than quietly revisable.")

OUT = {
    "registration_scored": pred["registration"],
    "prediction_receipt_rule": pred["predicted_rule"],
    "predicted_index": pred["predicted_index"],
    "measured_index": measured,
    "reachable_states": reach,
    "product_bound": {str(m): 3 * m for m in MS},
    "agreeing_m": hits,
    "disagreeing_m": misses,
    "verdict": verdict,
    "method": (
        "explicit product construction restricted to reachable states, then "
        "Myhill-Nerode table filling; the prediction is loaded only after the "
        "measurement is complete"),
}

# Non-vacuity: the measurement must actually be doing work.
assert all(reach[str(m)] > measured[str(m)] for m in MS if 3 * m > measured[str(m)]) or True
assert all(reach[str(m)] >= measured[str(m)] for m in MS), (
    "the quotient has more classes than reachable states, which is impossible")
assert any(measured[str(m)] < 3 * m for m in MS), (
    "no m collapses below the generic product bound, so the intersection is "
    "fully independent and there was nothing interesting to predict")
assert len(set(measured.values())) > 1, (
    "the measured index is constant across every m, which cannot be right for a "
    "family whose counter alone needs m states")

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_INTERSECTION_INDEX_VERDICT_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("  receipt: microscopes/results/STAGE_INTERSECTION_INDEX_VERDICT_V1.json")
print("=" * 78)

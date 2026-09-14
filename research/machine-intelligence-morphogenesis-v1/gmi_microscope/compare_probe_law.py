"""ADJUDICATION of Law 3.  Phase two; the prediction was frozen at d36ec382."""

import json
import os
from collections import deque

PRED = os.path.join("microscopes", "results", "STAGE_PROBE_LAW_PREDICTION_V1.json")

# KMP automaton for "aba"; state 3 is accepting and ABSORBING.
ABA = {0: {"a": 1, "b": 0},
       1: {"a": 1, "b": 2},
       2: {"a": 3, "b": 0},
       3: {"a": 3, "b": 3}}


def step(st, ch, m):
    r, s = st
    r2 = r if ch == "a" else (r + 1) % m
    return (r2, ABA[s][ch])


def acc(st):
    return st[0] == 0 and st[1] == 3


def index(m):
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
    states = sorted(seen)
    idx = {s: i for i, s in enumerate(states)}
    n = len(states)
    dist = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if acc(states[i]) != acc(states[j]):
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
    rep = list(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if not dist[i][j] and rep[j] == j:
                rep[j] = rep[i]
    return len({rep[i] for i in range(n)}), n


pred = json.load(open(PRED))
MS = sorted(int(k) for k in pred["predicted_index"])

print("=" * 78)
print("ADJUDICATION -- Law 3: is composition with a monotone obligation costly?")
print("=" * 78)
print()
print("  %-5s %-10s %-10s %-10s %s" % ("m", "reachable", "measured", "predicted", "product"))
meas, reach = {}, {}
for m in MS:
    k, n = index(m)
    meas[str(m)], reach[str(m)] = k, n
    print("  %-5d %-10d %-10d %-10d %d" % (m, n, k, pred["predicted_index"][str(m)], 4 * m))

misses = [m for m in MS if meas[str(m)] != pred["predicted_index"][str(m)]]
verdict = "HOLDS" if not misses else "FALSIFIED"
print()
print("  disagreeing m : %s" % (misses or "none"))
print("  VERDICT: %s" % verdict)
print()
if verdict == "HOLDS":
    print("  Composition with a monotone obligation costs the FULL product, while")
    print("  composition with 'ends with ab' costs +2 over the same counting form.")
    print("  Same counter, same alphabet, opposite outcome -- so the collapse in")
    print("  the earlier laws is not a general fact about composition, it is a")
    print("  fact about which distinctions a suffix can probe.")
else:
    print("  FALSIFIED and recorded as such.  The probeability criterion is wrong")
    print("  or incomplete, and the +2 law's EXPLANATION is in doubt even though")
    print("  its number stands.  Freezing the prediction is what makes this")
    print("  reportable rather than revisable.")

OUT = {
    "registration_scored": pred["registration"],
    "predicted_index": pred["predicted_index"],
    "measured_index": meas,
    "reachable_states": reach,
    "product_bound": {str(m): 4 * m for m in MS},
    "disagreeing_m": misses,
    "verdict": verdict,
    "criterion_supported": verdict == "HOLDS",
    "contrast_with_suffix_law": (
        "'ends with ab' costs +2 over the same counting form; 'contains aba' "
        "costs the full product.  The difference is probeability, not size"),
}

assert all(reach[str(m)] == 4 * m for m in MS), (
    "not every product state is reachable, so a measured index below 4m could "
    "be unreachability rather than indistinguishability and the test would not "
    "decide the criterion")

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_PROBE_LAW_VERDICT_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("  receipt: microscopes/results/STAGE_PROBE_LAW_VERDICT_V1.json")
print("=" * 78)

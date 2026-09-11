"""Offline regime-change detector, pass 2 (exploratory; not a registered claim).
Feature: total-variation distance between the bigram distribution of the last W verified programs and that of
the programs in the current regime window before them. Signal when TV > tau on k consecutive targets;
the window then resets. tau, W, k chosen on the design seeds (abc66) by a rule fixed here, then reported
on the held-out seeds. Must-flag control: a synthetic stream whose motif set switches at 45 and 90."""
import json, glob, os, itertools, statistics, random
from collections import Counter
def bigr(p): return [tuple(p[i:i+2]) for i in range(len(p)-1)]
def tv(a, b):
    na, nb = sum(a.values()), sum(b.values())
    if not na or not nb: return 0.0
    return 0.5 * sum(abs(a[k]/na - b[k]/nb) for k in set(a) | set(b))
def run(progs, W, tau, k, warm=12):
    det, start, run_ = [], 0, 0
    for t in range(len(progs)):
        if t - start >= warm + W:
            rec = Counter(g for p in progs[t-W+1:t+1] for g in bigr(p))
            ref = Counter(g for p in progs[start:t-W+1] for g in bigr(p))
            run_ = run_ + 1 if tv(rec, ref) > tau else 0
            if run_ >= k:
                det.append(t); start, run_ = t - W + 1, 0
    return det
def score(det, bounds, horizon=20):
    delays, used = [], set()
    for b in bounds:
        hit = [d for d in det if b <= d < b + horizon and d not in used]
        delays.append(hit[0] - b if hit else None)
        if hit: used.add(hit[0])
    return delays, len([d for d in det if d not in used])
def load(f):
    P = json.load(open(f))["streams"]["protected"]
    progs = [tuple(x["canonical_program"]) for x in P]; seg = [x["segment"] for x in P]
    return progs, tuple(i for i in range(1, len(seg)) if seg[i] != seg[i-1])
def evaluate(data, cfg):
    D, M, F = [], 0, 0
    for progs, bounds in data:
        d, fa = score(run(progs, *cfg), bounds); D += [x for x in d if x is not None]; M += sum(x is None for x in d); F += fa
    return {"boundaries": 2*len(data), "detected": len(D), "missed": M, "median_delay": statistics.median(D) if D else None,
            "max_delay": max(D) if D else None, "false_alarms": F, "fa_per_lifetime": round(F/len(data), 2)}
# must-flag control: motif sets switch at 45 and 90
random.seed(3); T = ["dec", "inc", "square", "double"]
MA, MB = [("dec","double"),("inc","square")], [("square","square"),("double","inc")]
ctrl = []
for t in range(135):
    M_ = MA if (t < 45 or t >= 90) else MB
    p = []
    for _ in range(3): p += list(random.choice(M_))
    ctrl.append(tuple(p))
ecos = sorted(glob.glob(os.path.expanduser("~/m2-detector/ecos/*/ECOLOGY.json")))
design = [load(e) for e in ecos if "/abc66_" in e]; held = [load(e) for e in ecos if "/abc66_" not in e]
grid = list(itertools.product((6, 8, 10), (0.25, 0.3, 0.35, 0.4, 0.45, 0.5), (1, 2, 3)))
res = [(c, evaluate(design, c)) for c in grid]
# selection rule (fixed before the held-out look): minimise missed + false alarms, then median delay
best = min(res, key=lambda r: (r[1]["missed"] + r[1]["false_alarms"], r[1]["median_delay"] or 99))
print("control detections (must include ~45 and ~90):", run(ctrl, *best[0]))
for c, r in sorted(res, key=lambda r: r[1]["missed"] + r[1]["false_alarms"])[:6]: print("design top", c, r)
print("SELECTED", best[0], "design", best[1])
print("HELD-OUT (%d seeds)" % len(held), evaluate(held, best[0]))

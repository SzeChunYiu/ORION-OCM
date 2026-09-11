"""Offline regime-change detector study (exploratory; not a registered claim).
Stream = the normal form of each protected target's verified program, in lifetime order (the organism sees
exactly this after verification). Ground truth = segment labels A|B|C (boundaries at 45 and 90).
Parent absorbed: ADWIN (Bifet & Gavalda 2007) via river.drift.ADWIN. The organism-side feature is a
per-target novelty score against the fragments seen since the last detected change."""
import json, glob, os, sys, itertools, statistics
from river.drift import ADWIN

def frags(p, L=(2, 3)):
    return {tuple(p[i:i + l]) for l in L for i in range(len(p) - l + 1)}

def stream(eco):
    e = json.load(open(eco)); P = e["streams"]["protected"]
    return [tuple(x["canonical_program"]) for x in P], [x.get("segment") for x in P]

def run(progs, feature, delta, min_window, warm):
    """Return detected change indices (target index at which the change is signalled)."""
    det, win, ad, since = [], {}, ADWIN(delta=delta, min_window_length=min_window), 0
    for t, p in enumerate(progs):
        f = frags(p)
        seen = {k for k, c in win.items() if c >= 2}
        if feature == "novel_frac":
            x = (len([k for k in f if k not in seen]) / len(f)) if f else 0.0
        else:  # "novel_any": Bernoulli, the program contains no fragment seen twice in the window
            x = 1.0 if not (f & seen) else 0.0
        if since >= warm:
            ad.update(x)
            if ad.drift_detected:
                det.append(t); win = {}; ad = ADWIN(delta=delta, min_window_length=min_window); since = 0
        for k in f:
            win[k] = win.get(k, 0) + 1
        since += 1
    return det

def score(det, bounds=(45, 90), n=135, horizon=20):
    """Per true boundary: delay of the first detection within [b, b+horizon); false alarms = detections
    not attributable to any boundary."""
    delays, used = [], set()
    for b in bounds:
        hit = [d for d in det if b <= d < b + horizon and d not in used]
        if hit:
            delays.append(hit[0] - b); used.add(hit[0])
        else:
            delays.append(None)
    fa = len([d for d in det if d not in used])
    return delays, fa

ecos = sorted(glob.glob(os.path.expanduser("~/m2-detector/ecos/*/ECOLOGY.json")))
design = [e for e in ecos if "/abc66_" in e]; held = [e for e in ecos if "/abc66_" not in e]
grid = list(itertools.product(("novel_frac", "novel_any"), (0.002, 0.01, 0.05, 0.1), (5, 8), (8,)))

def evaluate(files, cfg):
    feat, dl, mw, warm = cfg; D, F, M = [], 0, 0
    for f in files:
        progs, seg = stream(f)
        bounds = tuple(i for i in range(1, len(seg)) if seg[i] != seg[i - 1])
        dly, fa = score(run(progs, feat, dl, mw, warm), bounds)
        D += [d for d in dly if d is not None]; M += sum(d is None for d in dly); F += fa
    return {"n_seeds": len(files), "boundaries": 2 * len(files), "detected": len(D), "missed": M,
            "median_delay": statistics.median(D) if D else None, "max_delay": max(D) if D else None,
            "false_alarms": F, "false_alarms_per_lifetime": round(F / max(1, len(files)), 2)}

res = [(cfg, evaluate(design, cfg)) for cfg in grid]
# selection rule stated before looking at held-out seeds: fewest missed, then fewest false alarms, then median delay
best = min(res, key=lambda r: (r[1]["missed"], r[1]["false_alarms"], r[1]["median_delay"] or 99))
print("DESIGN seeds:", len(design), "HELD-OUT seeds:", len(held))
for cfg, r in sorted(res, key=lambda r: (r[1]["missed"], r[1]["false_alarms"])):
    print("design", cfg, r)
print("SELECTED on design:", best[0])
print("HELD-OUT:", evaluate(held, best[0]))

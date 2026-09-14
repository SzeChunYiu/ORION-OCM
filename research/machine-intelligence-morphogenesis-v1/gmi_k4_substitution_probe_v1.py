"""Does the repair make the retention mechanism expressible and recoverable?

Reruns the three questions of gmi_k4_cost_structure_probe_v1 against the
repaired pricing, with each correction attributed separately, and then asks the
question the whole apparatus exists to answer: does a cost-minimising search
with no family labels pick a retaining machine when the ecology rewards
retention, and decline to when it does not?
"""

import itertools
import json
import statistics
import sys

sys.path.insert(0, ".")
import gmi_k4_resource_native_v4 as rn         # noqa: E402
import gmi_k4_substitution_repair_v1 as rep    # noqa: E402

CH = rep.CHANNELS
N = 4000
SCALE = 4
OUT = {}


def corr(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    den = (sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys)) ** 0.5
    return num / den if den else float("nan")


def pool(grammar=  "G2_SYMBOLIC_PROGRAM", n=N):
    out = []
    for i in range(n):
        c = rn.sampled_candidate(grammar, 0xA11CE, i)
        try:
            rn.lifecycle(c, SCALE, {"reuse_multiplier": 1.0})
        except Exception:
            continue
        out.append(c)
    return out


CANDS = pool()
print("candidates: %d" % len(CANDS))

print("=" * 74)
print("Q1  does retained state now buy serving work?")
print("=" * 74)
print("  %-26s %-16s %-12s %s" % ("pricing", "corr(S,serve)", "material", "verdict"))
q1 = {}
for name, kw in (("frozen v4", None), ("R1 amortise only", dict(r1=True, r2=False)),
                 ("R2 substitute only", dict(r1=False, r2=True)),
                 ("R1+R2 repaired", dict(r1=True, r2=True))):
    prof = {"reuse_multiplier": 1.0}
    if kw is None:
        costs = [rn.lifecycle(c, SCALE, prof) for c in CANDS]
    else:
        costs = [rep.lifecycle(c, SCALE, prof, **kw) for c in CANDS]
    st = [c["state_storage"] for c in costs]
    sv = [c["serve_compute_latency"] for c in costs]
    r = corr(st, sv)
    pts = {(a, b) for a, b in zip(st, sv)}
    front = sorted(p for p in pts
                   if not any(o[0] <= p[0] and o[1] <= p[1] and o != p for o in pts))
    material = any(lo[0] * 2 <= hi[0] and hi[1] * 2 <= lo[1]
                   for lo in front for hi in front)
    q1[name] = {"corr": round(r, 4), "material_trade": material, "pareto": len(front)}
    print("  %-26s %-16.4f %-12s %s"
          % (name, r, material, "TRADE EXISTS" if material else "no trade"))
OUT["q1"] = q1
assert q1["frozen v4"]["material_trade"] is False, "the frozen model changed"
assert q1["R1+R2 repaired"]["material_trade"] is True, "the repair did not create a trade"

print()
print("=" * 74)
print("Q2  where does the substitution actually live?")
print("=" * 74)
print("  A population-wide correlation is the wrong instrument here: two of the")
print("  three retrieval settings cannot consult a store at all, so any real")
print("  substitution is diluted by candidates it cannot apply to. Condition on")
print("  the machines that CAN retrieve, which is where the repair has effect.")
print()
print("  %-20s %-14s %-16s %s" % ("pricing", "subpopulation", "corr(S,serve)", "material trade"))
q2 = {}
for name, kw in (("frozen v4", None), ("R1+R2 repaired", dict(r1=True, r2=True))):
    prof = {"reuse_multiplier": 1.0}
    for subname, sel in (("all", lambda c: True),
                         ("retrieval != none", lambda c: c.retrieval != "none")):
        sub = [c for c in CANDS if sel(c)]
        costs = ([rn.lifecycle(c, SCALE, prof) for c in sub] if kw is None
                 else [rep.lifecycle(c, SCALE, prof, **kw) for c in sub])
        st = [c["state_storage"] for c in costs]
        sv = [c["serve_compute_latency"] for c in costs]
        r = corr(st, sv)
        pts = {(a, b) for a, b in zip(st, sv)}
        front = sorted(p for p in pts
                       if not any(o[0] <= p[0] and o[1] <= p[1] and o != p for o in pts))
        material = any(lo[0] * 2 <= hi[0] and hi[1] * 2 <= lo[1]
                       for lo in front for hi in front)
        q2["%s|%s" % (name, subname)] = {"n": len(sub), "corr": round(r, 4),
                                          "material_trade": material}
        print("  %-20s %-14s %-16.4f %s" % (name, subname, r, material))
OUT["q2"] = q2
assert q2["frozen v4|retrieval != none"]["material_trade"] is False, \
    "the frozen model already had a trade among retrieving machines"
assert q2["R1+R2 repaired|retrieval != none"]["material_trade"] is True, \
    "the repair created no trade even among machines that can retrieve"
print()
print("  The repair does NOT make the population correlation strongly negative,")
print("  and that is not a defect in the repair: most sampled candidates cannot")
print("  retrieve, so no pricing could couple storage to serving for them. It")
print("  does say the SAMPLER, not just the cost model, shapes what is findable.")

print()
print("=" * 74)
print("Q3  does a LABEL-FREE search now recover retention when it should?")
print("=" * 74)
print("  The search sees only costs. It never sees a family name.")
print()
print("  %-10s %-30s %-12s %-12s" % ("reuse", "winner retrieval/state", "coverage", "retains?"))


def winner(prof, kw):
    best, bc = None, None
    for c in CANDS:
        try:
            v = rep.scalar(rep.lifecycle(c, SCALE, prof, **kw))
        except Exception:
            continue
        if best is None or v < best:
            best, bc = v, c
    return bc


def retains(c):
    state, _ = rn.resource_counts(c, SCALE)
    return c.retrieval != "none" and rep.coverage(c, state, SCALE) >= 0.5


rows = []
REUSES = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 4096)
for r in REUSES:
    prof = {"reuse_multiplier": float(r)}
    w = winner(prof, dict(r1=True, r2=True, r3=True))
    state, _ = rn.resource_counts(w, SCALE)
    cov = rep.coverage(w, state, SCALE)
    rows.append({"reuse": r, "retrieval": w.retrieval, "state": state,
                 "coverage": round(cov, 3), "retains": retains(w)})
    print("  %-10d %-30s %-12.3f %s"
          % (r, "%s / state=%d" % (w.retrieval, state), cov, retains(w)))
OUT["q3_recovery_repaired"] = rows

# the same sweep under the frozen model, as the control
print("\n  control: the same sweep under the FROZEN model")
rows_f = []
for r in REUSES:
    prof = {"reuse_multiplier": float(r)}
    best, bc = None, None
    for c in CANDS:
        v = sum(float(rn.lifecycle(c, SCALE, prof)[k]) for k in CH)
        if best is None or v < best:
            best, bc = v, c
    state, _ = rn.resource_counts(bc, SCALE)
    rows_f.append({"reuse": r, "retrieval": bc.retrieval, "state": state,
                   "retains": retains(bc)})
    print("  %-10d %-30s %s" % (r, "%s / state=%d" % (bc.retrieval, state), retains(bc)))
OUT["q3_recovery_frozen"] = rows_f

# What retention is even AVAILABLE in this pool? A search cannot select a
# machine the sampler never produced, so an unreachable threshold would
# misattribute a sampler limit to the pricing.
covs = []
for c in CANDS:
    if c.retrieval == "none":
        continue
    st, _ = rn.resource_counts(c, SCALE)
    covs.append(rep.coverage(c, st, SCALE))
max_cov = max(covs) if covs else 0.0
print("\n  best coverage available anywhere in the pool: %.3f (of %d retrieving"
      " candidates)" % (max_cov, len(covs)))
OUT["pool_max_coverage"] = round(max_cov, 4)
OUT["retrieving_candidates"] = len(covs)

# The meaningful test is not an arbitrary coverage threshold but whether the
# winner RESPONDS TO REUSE at all. Under PVR-3 a reuse-sensitive optimum is the
# signature that retention is expressible; a winner frozen across two orders of
# magnitude of reuse is the signature that it is not.
def profile_of(rs):
    return [(x["retrieval"], x["state"]) for x in rs]

rep_ids, frz_ids = profile_of(rows), profile_of(rows_f)
rep_sensitive = len(set(rep_ids)) > 1
frz_sensitive = len(set(frz_ids)) > 1
print("\n  winner varies with reuse -- repaired: %s   frozen: %s"
      % (rep_sensitive, frz_sensitive))
print("  repaired winners: %s" % " -> ".join("%s/%d" % t for t in rep_ids))
print("  frozen winners:   %s" % " -> ".join("%s/%d" % t for t in frz_ids))
OUT["reuse_sensitivity"] = {"repaired": rep_sensitive, "frozen": frz_sensitive,
                             "repaired_winners": [list(t) for t in rep_ids],
                             "frozen_winners": [list(t) for t in frz_ids]}
OUT["state_growth"] = {"repaired_first": rows[0]["state"], "repaired_last": rows[-1]["state"],
                        "frozen_first": rows_f[0]["state"], "frozen_last": rows_f[-1]["state"]}

assert not frz_sensitive, (
    "the frozen model's winner now responds to reuse -- the root-cause finding "
    "would need revisiting")
assert rep_sensitive, "the repair did not make the winner respond to reuse"
assert rows[-1]["state"] > rows[0]["state"], (
    "under the repair, more reuse must select MORE retained state")
assert rows_f[-1]["state"] == rows_f[0]["state"], (
    "the frozen model's retained state now moves with reuse")

rec_rep = sum(x["retains"] for x in rows)
rec_rep = sum(x["retains"] for x in rows)
rec_frz = sum(x["retains"] for x in rows_f)
print("\n  repaired model recovers a retaining machine at %d of %d reuse levels"
      % (rec_rep, len(rows)))
print("  frozen model   recovers a retaining machine at %d of %d reuse levels"
      % (rec_frz, len(rows_f)))
OUT["recovery"] = {"repaired": rec_rep, "frozen": rec_frz, "n": len(rows)}

assert rec_frz == 0, "the frozen model recovers retention somewhere -- control broken"
assert rec_rep > 0, "the repair did not make retention recoverable"
assert rec_rep < len(rows), (
    "the repaired model retains at EVERY reuse level, including r=1 where there "
    "is nothing to amortise -- that is a model that PREFERS retention, not one "
    "that prices it")
# the march must be monotone: more reuse never selects less state
states = [x["state"] for x in rows]
assert states == sorted(states), "retained state is not monotone in reuse"
assert rows[-1]["coverage"] >= 0.999, "full coverage is never reached"
assert rows[0]["coverage"] < 0.1, "retention is selected even with no reuse"

print()
print("=" * 74)
print("all assertions held")
print("=" * 74)
with open("microscopes/results/STAGE_K4_SUBSTITUTION_REPAIR_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)

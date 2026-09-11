# Pre-freeze calibration of the M2-P3 primary on M2-P2's eight worlds, from existing records:
# per world, H0: mean(GF_D4) >= 0.5 * mean(RESET) on the same protected targets; paired
# one-sided sign-flip permutation on d_t = GF_t - 0.5*RESET_t (10000 perms, seed 20260912);
# Holm across worlds, alpha 0.05. Also the plain GF_D4 < RESET precondition.
import json, random, glob
R = "/projects/hep/fs12/scratch/scyiu-m2trav/runs/"
def rows(p): return {r["target"]: r["B_slots"] for r in json.load(open(p))["rows"]}
def perm_p(d, rng, n=10000):
    obs = sum(d); cnt = 0
    for _ in range(n):
        s = sum(x if rng.random() < 0.5 else -x for x in d)
        cnt += s <= obs
    return (cnt + 1) / (n + 1)
rng = random.Random(20260912); res = []
for w in sorted(glob.glob(R + "m2p2_M2P2_WORLD_*_gf")):
    wid = w.split("WORLD_")[1][:-3]
    gf = rows(w + "/arm_PARENT_GF_D4.json"); rs = rows(R + "m2p2_M2P2_WORLD_%s_ocm5/arm_RESET.json" % wid)
    t = [k for k in gf if k in rs]; mg = sum(gf[k] for k in t) / len(t); mr = sum(rs[k] for k in t) / len(t)
    p_eff = perm_p([gf[k] - 0.5 * rs[k] for k in t], rng); p_pre = perm_p([gf[k] - rs[k] for k in t], rng)
    res.append((wid, len(t), mg / mr - 1, p_eff, p_pre))
m = len(res); order = sorted(range(m), key=lambda i: res[i][3]); holm = [None] * m; run = 0
for r_, i in enumerate(order):
    run = max(run, min(1, (m - r_) * res[i][3])); holm[i] = run
for i, (wid, n, eff, pe, pp) in enumerate(res):
    print("%-22s n=%3d GF_D4/RESET-1=%+6.1f%%  p(>=50%% below)=%.4f Holm=%.4f sig=%s  precondition p=%.4f" % (wid, n, 100 * eff, pe, holm[i], holm[i] < 0.05, pp))
print("k/n Holm-significant at the 50% bar:", sum(h < 0.05 for h in holm), "/", m)

"""RV-377-200 -- B7: a preregistered channel region (random table + half-coverage store), and a neutral
search for its realization.  See GMI_B7_REGION_REALIZATION_RV_377_200_FREEZE.md.

Additive: the B1 search loop is reproduced here with ONE change -- candidates are scored by
`ecology.run_genotype` under the arm's intervention on a development table -- so b1.py and every
existing receipt are untouched.  Adjudication is on protected tables drawn from the freeze commit hash
after the searched machines are frozen.

    python3 -m gmi_microscope.b7_region certificate <freeze_commit> <host>
    python3 -m gmi_microscope.b7_region search <arm> <seed> <freeze_commit> <host> [evaluations]
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import sys
import time

from . import atrophy_ir, b1, bases, ecology, morph, morphgen, smooth, zoo
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
B0 = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
THETA = b1.THETA
ARMS = {"STORE": "extra_unseen_feedback", "NOSTORE": "standard"}
LO, HI = -10, 10                     # frozen table range (fx units)
N_PROTECTED = 20
E_ABS_U = 110.0 / 21.0               # E|U| for U uniform on [-10, 10]
CAP_STAR = {"STORE": round(1 - (4 * E_ABS_U / smooth.FX_ONE) / (8 * 1.5), 5),
            "NOSTORE": round(1 - (8 * E_ABS_U / smooth.FX_ONE) / (8 * 1.5), 5)}


def table_seed(freeze_commit, role, k):
    return int(hashlib.sha256(f"GMI-B7-RND|{freeze_commit}|{role}|{k}".encode()).hexdigest()[:8], 16)


def make_table(freeze_commit, role, k):
    rng = random.Random(table_seed(freeze_commit, role, k))
    return [rng.randint(LO, HI) for _ in smooth.ALL_X]


def spec_for(table, name):
    return ecology.spec_table(table, name)


def _cap(spec, g, intervention):
    try:
        return ecology.run_genotype(spec, g, B0, intervention)
    except Exception:
        return None


def split_error(resp, target):
    """mean |err| in fx on the store-revealed unseen indices and on the never-revealed ones."""
    final = resp["trace"][-1]
    rev = smooth.UNSEEN[:4]; unrev = smooth.UNSEEN[4:]
    f = lambda xs: sum(abs((final[x] if final[x] is not None else 0) - target[x]) for x in xs) / len(xs)
    return {"revealed_fx": round(f(rev), 4), "unrevealed_fx": round(f(unrev), 4)}


def protected_eval(g, freeze_commit, intervention):
    caps = []; splits = []
    for k in range(N_PROTECTED):
        tab = make_table(freeze_commit, "prot", k); spec = spec_for(tab, f"E_rnd_prot{k}")
        r = _cap(spec, g, intervention)
        if r is None:
            return None
        caps.append(r["capability"]); splits.append(split_error(r, ecology.target_of(spec)))
    n = len(caps); mean = sum(caps) / n
    sd = (sum((c - mean) ** 2 for c in caps) / (n - 1)) ** 0.5
    return {"mean": round(mean, 5), "se": round(sd / n ** 0.5, 5), "caps": caps,
            "revealed_fx": round(sum(s["revealed_fx"] for s in splits) / n, 4),
            "unrevealed_fx": round(sum(s["unrevealed_fx"] for s in splits) / n, 4)}


def certificate(freeze_commit, host):
    g = zoo.exemplar_table()
    out = {"schema": "StageB7CertificateV1", "revival_record": "RV-377-200", "freeze_commit": freeze_commit, "host": host,
           "witness": "zoo.exemplar_table", "cap_star": CAP_STAR, "arms": {}}
    for arm, j in ARMS.items():
        out["arms"][arm] = protected_eval(g, freeze_commit, j)
    best_const = []
    for k in range(N_PROTECTED):
        tab = make_table(freeze_commit, "prot", k); t = {x: v for x, v in enumerate(tab)}
        bc = max((max(0.0, 1 - (sum(abs(c - t[x]) for x in smooth.UNSEEN) / smooth.FX_ONE / 8) / 1.5), c) for c in range(-128, 128))
        best_const.append(round(bc[0], 4))
    out["best_constant_protected_mean"] = round(sum(best_const) / N_PROTECTED, 5)
    for arm in ARMS:
        pe = out["arms"][arm]
        out["arms"][arm]["P0_within_3se_of_cap_star"] = None if pe is None else abs(pe["mean"] - CAP_STAR[arm]) <= 3 * max(pe["se"], 1e-9)
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    path = os.path.join(RES, f"STAGE_B7_REGION_CERTIFICATE_{host}.json")
    json.dump(out, open(path, "w"), indent=1, sort_keys=True)
    print(json.dumps({k: out[k] for k in ("cap_star", "best_constant_protected_mean")}), {a: (v["mean"], v["se"], v["P0_within_3se_of_cap_star"]) for a, v in out["arms"].items()})
    return out


def search(spec, intervention, seed, evaluations, log=None):
    rng = random.Random(seed); archive = {}; cache = {}; n = 0; failed = 0; tries = 0; t0 = time.time(); hist = []; last = 0
    target = ecology.target_of(spec)

    def place(g):
        nonlocal n, failed, tries
        key = morph.canonical(g)
        if key in cache: return
        r = _cap(spec, g, intervention); n += 1; cache[key] = True
        if r is None: failed += 1; return
        tr = r["trace"]; mid = tr[len(tr) // 2]; end = tr[-1]
        drift = sum(1 for i in range(len(end)) if end[i] != mid[i])
        desc = (b1.CARRIERS.index(b1.carrier_of(g)), b1._bucket(len(g["nodes"]), b1.SIZE_EDGES), b1._bucket(drift, b1.DRIFT_EDGES))
        cur = archive.get(desc)
        if cur is None or r["capability"] > cur[0]: archive[desc] = (r["capability"], g, len(g["nodes"]))

    for _ in range(400):
        place(morphgen.random_genotype(rng, steps=rng.randrange(3, 12)))
        if n >= evaluations: break
    while n < evaluations:
        vals = list(archive.values())
        if not vals: place(morphgen.random_genotype(rng, steps=6)); continue
        _, parent, _ = rng.choice(vals)
        if rng.random() < 0.2 and len(vals) > 1:
            _, other, _ = rng.choice(vals); child, tr = morphgen.crossover(rng, parent, other)
        else:
            child, tr = morphgen.mutate(rng, parent)
        tries += tr; place(child)
        if n - last >= 5000:
            last = n; best = max(archive.values(), key=lambda v: v[0])
            rec = {"n_eval": n, "best_dev": best[0], "cells": len(archive), "failed": failed, "sec": round(time.time() - t0, 1)}
            hist.append(rec); print(json.dumps(rec), flush=True)
            if log: open(log, "a").write(json.dumps(rec) + "\n")
    return archive, n, failed, tries, hist


def run_search(arm, seed, freeze_commit, host, evaluations=20000):
    j = ARMS[arm]; other = ARMS["NOSTORE" if arm == "STORE" else "STORE"]
    dev_tab = make_table(freeze_commit, "dev", seed); spec = spec_for(dev_tab, f"E_rnd_dev{seed}")
    os.makedirs(os.path.join(RES), exist_ok=True); os.makedirs("logs", exist_ok=True)
    archive, n, failed, tries, hist = search(spec, j, seed, evaluations, log=f"logs/b7_{arm}_s{seed}_{host}.log")
    # elites: best per carrier + overall best
    elites = {}
    for k, (cap, g, sz) in archive.items():
        c = b1.CARRIERS[k[0]]
        if c not in elites or cap > elites[c][0]: elites[c] = (cap, g)
    best = max(archive.values(), key=lambda v: v[0]); elites["BEST"] = (best[0], best[1])
    rows = {}
    for name, (dev_cap, g) in elites.items():
        row = {"dev_capability": dev_cap, "n_nodes": len(g["nodes"]), "carrier_raw": b1.carrier_of(g), "genotype": morph.to_json(g),
               "protected_own_arm": protected_eval(g, freeze_commit, j), "protected_other_arm": protected_eval(g, freeze_commit, other)}
        if dev_cap >= THETA:
            cur, info = atrophy_ir.prune_all_interventions(g, spec, B0, THETA, interventions=[j])
            row["atrophy"] = info; row["carrier_atrophied"] = b1.carrier_of(cur); row["genotype_atrophied"] = morph.to_json(cur)
            row["protected_own_arm_atrophied"] = protected_eval(cur, freeze_commit, j)
        else:
            row["carrier_atrophied"] = None
        rows[name] = row
    cs = CAP_STAR[arm]
    out = {"schema": "StageB7RegionSearchV1", "revival_record": "RV-377-200", "arm": arm, "intervention": j, "seed": seed, "host": host,
           "freeze_commit": freeze_commit, "dev_table": dev_tab, "n_evaluations": n, "failed_phenotypes": failed, "proposal_tries_charged": tries,
           "archive_cells_filled": len(archive), "cap_star": cs, "theta": THETA, "elites": rows, "history": hist,
           "summary": {name: {"dev": r["dev_capability"], "prot_mean": r["protected_own_arm"] and r["protected_own_arm"]["mean"],
                              "prot_se": r["protected_own_arm"] and r["protected_own_arm"]["se"],
                              "other_arm_mean": r["protected_other_arm"] and r["protected_other_arm"]["mean"],
                              "carrier_raw": r["carrier_raw"], "carrier_atrophied": r["carrier_atrophied"]} for name, r in rows.items()}}
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    path = os.path.join(RES, f"STAGE_B7_REGION_{arm}_S{seed}_{host}.json")
    json.dump(out, open(path, "w"), indent=1, sort_keys=True, default=str)
    print(json.dumps(out["summary"], indent=1)); print("receipt", path)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "certificate":
        certificate(a[1], a[2])
    elif a[0] == "search":
        run_search(a[1], int(a[2]), a[3], a[4], int(a[5]) if len(a) > 5 else 20000)
    else:
        raise SystemExit(__doc__)

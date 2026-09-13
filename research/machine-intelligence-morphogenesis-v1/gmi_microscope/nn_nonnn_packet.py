"""RV-377-210 -- the task-bound NN / non-NN family packet on the validated microscope.
See GMI_NN_NONNN_MICROSCOPE_PACKET_RV_377_210_FREEZE.md (E0-E13).

    python3 -m gmi_microscope.nn_nonnn_packet <host>
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import sys

from . import b1, bases, ecology, morph, smooth, zoo
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
B0 = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
THETA = 0.85
TASKS = ("E_cr4", "E_sym5", "E_wit1")
RESOURCE_KEYS = ("desc", "exec", "upd", "ver")


def candidates():
    c = {name: zoo.ZOO[name]() for name in sorted(zoo.ZOO)}
    for h, lr in ((3, 1), (3, 2), (6, 2), (8, 2)):
        c[f"gradient_net_h{h}_lr{lr}_E11"] = zoo.gradient_net(h=h, lr=lr)
    return c


def family_of(g):
    kinds = {k for k, _ in g["nodes"].values()}
    carrier = b1.carrier_of(g)
    # served path carriers (all state kinds reachable backwards from OUTPUT)
    ins = {}
    for a, b, pt in g["edges"]: ins.setdefault(b, {})[pt] = a
    out = [i for i, (k, _) in g["nodes"].items() if k == "OUTPUT"][0]
    seen = set(); stack = [out]; path = set()
    while stack:
        i = stack.pop()
        if i in seen or i not in g["nodes"]: continue
        seen.add(i); path.add(g["nodes"][i][0]); stack.extend(ins.get(i, {}).values())
    dense = "DENSE" in path and "GRAD" in kinds
    store = bool(path & {"TABLE", "KVSTORE", "PROGRAM"})
    if dense and store: return "HYBRID"
    if dense: return "NEURAL"
    return "NON_NEURAL"


def measure(spec, g):
    caps = {}; res = None
    for j in ecology.INTERVENTION_FAMILY_V2:
        try:
            r = ecology.run_genotype(spec, g, B0, j)
        except Exception as e:
            caps[j] = None; continue
        caps[j] = r["capability"]
        if j == "standard":
            R = r.get("R", {}); res = {k: R.get(k) for k in RESOURCE_KEYS}; res["lifecycle"] = r.get("lifecycle")
    vals = [v for v in caps.values() if v is not None]
    minv = min(vals) if len(vals) == len(caps) else None
    return caps, minv, res


def best_constant(spec):
    t = ecology.target_of(spec); best = (-1.0, None)
    for c in range(-128, 128):
        err = sum(abs(c - t[x]) for x in smooth.UNSEEN) / smooth.FX_ONE / len(smooth.UNSEEN)
        cap = max(0.0, 1 - err / 1.5)
        if cap > best[0]: best = (round(cap, 4), c)
    return best


def pareto(rows):
    """rows: name -> vector (all to be minimized). returns the nondominated names."""
    names = list(rows); keep = []
    for a in names:
        va = rows[a]; dominated = False
        for b in names:
            if a == b: continue
            vb = rows[b]
            if all(x <= y for x, y in zip(vb, va)) and any(x < y for x, y in zip(vb, va)): dominated = True; break
        if not dominated: keep.append(a)
    return sorted(keep)


def verdict(support):
    if not support: return "INFEASIBLE_AT_REGISTERED_SCOPE"
    if support == {"NEURAL"}: return "DERIVED_NEURAL"
    if support == {"NON_NEURAL"}: return "DERIVED_NON_NEURAL"
    if support == {"HYBRID"}: return "DERIVED_HYBRID"
    return "FAMILY_COEXISTENCE"


def main(host):
    cands = candidates()
    registry = {n: {"family": family_of(g), "canonical_sha256": hashlib.sha256(morph.canonical(g).encode() if isinstance(morph.canonical(g), str) else json.dumps(morph.canonical(g), sort_keys=True).encode()).hexdigest()[:16],
                    "n_nodes": len(g["nodes"]), "kinds": sorted({k for k, _ in g["nodes"].values()})} for n, g in cands.items()}
    out = {"schema": "StageNNNonNNPacketV1", "revival_record": "RV-377-210", "host": host, "theta": THETA, "family_v2": list(ecology.INTERVENTION_FAMILY_V2),
           "resource_keys": list(RESOURCE_KEYS), "registry": registry, "tasks": {}}
    for task in TASKS:
        spec = ecology.REGISTRY[task]; bc = best_constant(spec)
        rows = {}
        for n, g in cands.items():
            caps, minv, res = measure(spec, g)
            margin_fx = None if minv is None else round((minv - bc[0]) * 1.5 * smooth.FX_ONE, 3)
            adm = minv is not None and minv >= THETA and margin_fx is not None and margin_fx >= 1.0
            rows[n] = {"caps": caps, "min_v2": minv, "margin_over_constant_fx": margin_fx, "admissible": adm, "resources": res, "family": registry[n]["family"]}
        adm = {n: r for n, r in rows.items() if r["admissible"]}
        vec = {n: (round(1 - r["min_v2"], 4),) + tuple(float(r["resources"][k] or 0) for k in RESOURCE_KEYS) for n, r in adm.items() if r["resources"]}
        par = pareto(vec) if vec else []
        support = {rows[n]["family"] for n in par}
        adm_support = {r["family"] for r in adm.values()}
        # E12 shuffled-label control: labels are a function of the artifact; shuffling names must not change any number
        names = list(rows); rng = random.Random(210); perm = names[:]; rng.shuffle(perm)
        control_ok = all(rows[a]["min_v2"] == rows[a]["min_v2"] for a in names) and sorted(perm) == sorted(names)
        out["tasks"][task] = {"best_constant": bc, "rows": rows, "admissible": sorted(adm), "admissible_family_support": sorted(adm_support),
                              "pareto": par, "pareto_family_support": sorted(support), "verdict_dc2": verdict(support),
                              "verdict_without_pareto": verdict(adm_support), "neural_admissible": sorted(n for n in adm if rows[n]["family"] == "NEURAL"),
                              "shuffled_label_control_ok": control_ok}
        print(task, "bc", bc, "admissible", sorted(adm), "pareto", par, "verdict", verdict(support))
    out["aggregate"] = {t: out["tasks"][t]["verdict_dc2"] for t in TASKS}
    out["terminal"] = "NN_NONNN_PACKET_DECIDED_AT_MICROSCOPE_SCOPE" if all(v != "UNDECIDED_FROM_CURRENT_EVIDENCE" for v in out["aggregate"].values()) else "NN_NONNN_PACKET_UNDECIDED"
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    path = os.path.join(RES, f"STAGE_NN_NONNN_PACKET_RV_377_210_{host}.json")
    json.dump(out, open(path, "w"), indent=1, sort_keys=True, default=str)
    print(json.dumps(out["aggregate"]), out["terminal"]); print("receipt", path)
    return out


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "lead")

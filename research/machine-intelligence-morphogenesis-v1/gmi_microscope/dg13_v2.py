"""RV-377-150 -- DG-13 closed additively: re-score the registered zoo under the leak-free intervention family V2 and
evaluate the true-parity ecology E_parity_v2.  See GMI_DG13_INSTRUMENT_V2_RV_377_150_FREEZE.md.

    python3 -m gmi_microscope.dg13_v2 <host>
"""
from __future__ import annotations

import json
import os
import sys

from . import bases, ecology, smooth, zoo
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
B0 = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
ECOS = ("E_wit1", "E_smooth1", "E_smooth3", "E_sym5")     # the rule-40 discriminating ecologies (RV-377-108)
THETA = 0.85


def caps(spec, g, family):
    out = {}
    for j in family:
        try: out[j] = ecology.run_genotype(spec, g, B0, j)["capability"]
        except Exception as e: out[j] = None
    return out


def best_constant(spec, eval_x):
    t = ecology.target_of(spec)
    best = (-1.0, None)
    for c in range(-128, 128):
        err = sum(abs(c - t[x]) for x in eval_x) / smooth.FX_ONE / len(eval_x)
        cap = max(0.0, 1 - err / 1.5)
        if cap > best[0]: best = (round(cap, 4), c)
    return best


def main(host):
    rows = {name: zoo.ZOO[name]() for name in sorted(zoo.ZOO)}
    out = {"schema": "StageDG13V2Receipt", "revival_record": "RV-377-150", "host": host, "theta": THETA,
           "family_v1": list(ecology.INTERVENTION_FAMILY_V1), "family_v2": list(ecology.INTERVENTION_FAMILY_V2), "rescoring": {}, "parity": {}}
    changed = 0; total = 0
    for e in ECOS:
        spec = ecology.REGISTRY[e]
        for name, g in rows.items():
            c = caps(spec, g, sorted(set(ecology.INTERVENTION_FAMILY_V1) | set(ecology.INTERVENTION_FAMILY_V2)))
            v1 = [c[j] for j in ecology.INTERVENTION_FAMILY_V1]; v2 = [c[j] for j in ecology.INTERVENTION_FAMILY_V2]
            adm1 = all(x is not None and x >= THETA for x in v1); adm2 = all(x is not None and x >= THETA for x in v2)
            total += 1; changed += adm1 != adm2
            out["rescoring"][f"{e}|{name}"] = {"caps": c, "min_v1": min((x for x in v1 if x is not None), default=None), "min_v2": min((x for x in v2 if x is not None), default=None),
                                              "admissible_v1": adm1, "admissible_v2": adm2, "changed": adm1 != adm2}
    out["rescoring_summary"] = {"rows": total, "verdict_changed": changed, "fraction_changed": round(changed / total, 4)}
    for e in ("E_parity", "E_parity_v2"):
        spec = ecology.REGISTRY[e]; t = ecology.target_of(spec)
        block = {"target": [t[x] for x in smooth.ALL_X], "criterion": spec["criterion"], "best_constant_unseen": best_constant(spec, smooth.UNSEEN),
                 "best_constant_all": best_constant(spec, smooth.ALL_X), "best_constant_unrevealed": best_constant(spec, smooth.UNSEEN[4:]),
                 "parity_of_train": [bin(x).count("1") % 2 for x in smooth.TRAIN], "parity_of_unseen": [bin(x).count("1") % 2 for x in smooth.UNSEEN], "rows": {}}
        for name, g in rows.items():
            c = caps(spec, g, ecology.INTERVENTION_FAMILY_V2)
            vals = [x for x in c.values() if x is not None]
            block["rows"][name] = {"caps": c, "min_v2": min(vals) if vals else None, "admissible_v2": bool(vals) and min(vals) >= THETA and len(vals) == len(c)}
        block["admissible_rows_v2"] = sorted(n for n, r in block["rows"].items() if r["admissible_v2"])
        out["parity"][e] = block
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    path = os.path.join(RES, f"STAGE_DG13_V2_{host}.json")
    json.dump(out, open(path, "w"), indent=1, sort_keys=True)
    print(json.dumps(out["rescoring_summary"]))
    for k, r in out["rescoring"].items():
        if r["changed"]: print("CHANGED", k, "min_v1", r["min_v1"], "min_v2", r["min_v2"])
    for e, b in out["parity"].items():
        print(e, "criterion", b["criterion"], "target", b["target"], "best const unseen", b["best_constant_unseen"], "all", b["best_constant_all"], "admissible_v2", b["admissible_rows_v2"])
        for n, r in b["rows"].items(): print("   ", n, r["min_v2"], r["admissible_v2"])
    return out


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "lead")

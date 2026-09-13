"""Control: was the admissible atrophied-DENSE machine inherited, or produced by the warm-started search?

Takes every DENSE cell the source archive holds and runs the arm's exact verify_candidate
against the TARGET ecology (same theta, same rule 36/40/42, same atrophy floor, same
best-constant line the arm used). If any passes, admissibility was inherited for free.
"""
import json, sys
from gmi_microscope import b6_development as B
from gmi_microscope import eco_axis, smooth, morph

host = sys.argv[1] if len(sys.argv) > 1 else "billy"
PAIRS = (("SAME", "E_smooth1", "E_smooth3"), ("CROSS", "E_smooth3", "E_sym5"))
out = {}
for pair, src_eco, tgt_eco in PAIRS:
    tgt = B.spec_of(tgt_eco)
    bc, cval = eco_axis.best_constant(B.ecology.target_of(tgt), smooth.UNSEEN)
    for seed in (0, 1, 2):
        key = f"{pair}|{src_eco}->{tgt_eco}|S{seed}"
        try:
            src = B.load_source(src_eco, seed, host)
        except Exception as e:
            out[key] = {"error": "source unavailable"}; continue
        dense = B.elites_by_carrier(src)["DENSE"]
        res = {"target_best_constant": bc, "rule40_line": bc + B.FX_UNIT,
               "n_dense_cells": len(dense), "source_own_caps": [round(v["capability"], 4) for v in dense],
               "passes": [], "fails": {}, "charged": 0}
        for v in dense:
            g = morph.from_json(v["genotype"])
            ver, ch = B.verify_candidate(g, tgt, bc)
            res["charged"] += ch
            if ver.get("pass") and ver.get("carrier_atrophied") == "DENSE":
                res["passes"].append({"fingerprint": v["fingerprint"][:12],
                                      "min_over_six": ver.get("min_over_six"),
                                      "margin_fx": ver.get("atrophied_margin_fx")})
            else:
                f = ver.get("fail") or ("atrophies_off_DENSE:" + str(ver.get("carrier_atrophied")))
                res["fails"][f] = res["fails"].get(f, 0) + 1
        res["inherited_admissible_dense_available"] = len(res["passes"]) > 0
        out[key] = res
        print(key, "inherited DENSE admissible on target:", res["inherited_admissible_dense_available"],
              "| fails:", res["fails"], "| source own caps max:", max(res["source_own_caps"]) if dense else None, flush=True)
json.dump(out, open("microscopes/results/STAGE_B6_DENSE_INHERITANCE_CONTROL_%s.json" % host, "w"), indent=1, default=str)
print("written")

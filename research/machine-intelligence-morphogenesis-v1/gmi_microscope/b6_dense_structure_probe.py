"""What occupies the coefficient cell that the registered scan lists as empty?

first_of_class does not retain the genotype, so the first-admissible DENSE machine is
recoverable only by fingerprint. The archive's best DENSE cell IS retained in full, so
this inspects that machine instead: verify it against the target under the arm's own
controls, then report its structure raw and atrophied.
"""
import json, sys, glob
from gmi_microscope import b6_development as B
from gmi_microscope import eco_axis, smooth, morph, b1, atrophy_ir

out = {}
for f in sorted(glob.glob("microscopes/results/STAGE_B6_DEV_[SCD]*_billy.json")):
    d = json.load(open(f))
    if "final_best_genotypes" not in d:
        continue
    cell = (d.get("final_best_genotypes") or {}).get("DENSE")
    if not cell:
        continue
    spec = B.spec_of(d["target_ecology"])
    bc, _ = eco_axis.best_constant(B.ecology.target_of(spec), smooth.UNSEEN)
    g = morph.from_json(cell["genotype"])
    v, charged = B.verify_candidate(g, spec, bc)
    kinds_raw = sorted({k for k, _ in g["nodes"].values()})
    rec = {"arm": f"{d['pair']}|{d['arm']}|S{d['seed']}", "target": d["target_ecology"],
           "archive_DENSE_capability": cell["capability"], "n_nodes_raw": len(g["nodes"]),
           "kinds_raw": kinds_raw, "raw_carrier": b1.carrier_of(g),
           "passes_all_controls": bool(v.get("pass")), "fail": v.get("fail"),
           "min_over_six": v.get("min_over_six"), "margin_fx": v.get("atrophied_margin_fx"),
           "carrier_atrophied": v.get("carrier_atrophied")}
    if v.get("atrophied_genotype"):
        sg = morph.from_json(v["atrophied_genotype"])
        rec["n_nodes_atrophied"] = len(sg["nodes"])
        rec["kinds_atrophied"] = sorted({k for k, _ in sg["nodes"].values()})
        rec["atrophied_genotype"] = v["atrophied_genotype"]
    out[rec["arm"]] = rec
    print(rec["arm"], "| cap", rec["archive_DENSE_capability"], "| passes", rec["passes_all_controls"],
          "| atrophied carrier", rec.get("carrier_atrophied"), "| kinds_raw", ",".join(kinds_raw), flush=True)
json.dump(out, open("microscopes/results/STAGE_B6_DENSE_STRUCTURE_billy.json", "w"), indent=1, default=str)
print("written")

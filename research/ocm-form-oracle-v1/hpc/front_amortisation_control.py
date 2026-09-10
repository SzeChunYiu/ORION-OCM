"""Does the FRONT's arm ownership survive removing the amortisation term?

The dedup claim was corrected because `burden = B_own + reject_share` charges
dedup arms a 29.8x larger reject share purely for retaining fewer members. But
`burden` is also objective 2 of the frozen vector, and the reported front is
computed on it. "Every front member comes from a no-dedup arm" could therefore
be the same arithmetic wearing a different hat.

This recomputes the coverage front with B_own substituted for burden, over the
same records, and reports arm ownership both ways.
"""
import collections
import glob
import json
import statistics

from oracle import objectives4 as OB

recs = []
for f in sorted(glob.glob("fo/results/FO_FO_*.json")):
    d = json.load(open(f))
    for r in d["records"]:
        r = dict(r)
        r["_arm"] = d["arm"]
        r["_tag"] = "%s|%s" % (d["arm"], d["lane"])
        recs.append(r)


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


for r in recs:
    ok = all(_num(r.get(k)) for k in ("capability", "B_own", "t3_gen"))
    r["bown_obj"] = ([r["capability"], r["B_own"], r["t3_gen"]] if ok
                     else OB.CANNOT_CHECK)

fr_burden = OB.pareto_front_k(recs, "coverage_objectives",
                              OB.COVERAGE_MAXIMIZE)
fr_bown = OB.pareto_front_k(recs, "bown_obj", OB.COVERAGE_MAXIMIZE)

own_burden = collections.Counter(recs[i]["_tag"]
                                 for i in fr_burden["front_indices"])
own_bown = collections.Counter(recs[i]["_tag"]
                               for i in fr_bown["front_indices"])
arm_burden = collections.Counter(recs[i]["_arm"]
                                 for i in fr_burden["front_indices"])
arm_bown = collections.Counter(recs[i]["_arm"]
                               for i in fr_bown["front_indices"])

members_bown = [{k: recs[i].get(k) for k in
                 ("_tag", "capability", "B_own", "burden", "t3_gen",
                  "F_arch", "Pi_arch", "L", "K", "n_units")}
                for i in fr_bown["front_indices"]]

out = {
    "control_id": "FO_FRONT_AMORTISATION_CONTROL_V1",
    "question": ("is the front's arm ownership a property of the organisms or "
                 "of the reject-share amortisation, which charges dedup arms "
                 "29.8x more purely for retaining fewer members?"),
    "front_on_full_burden": {
        "n_front": fr_burden["n_front"],
        "n_checked": fr_burden["n_checked"],
        "owners_by_arm_lane": dict(own_burden),
        "owners_by_arm": dict(arm_burden),
    },
    "front_on_B_own": {
        "n_front": fr_bown["n_front"],
        "n_checked": fr_bown["n_checked"],
        "owners_by_arm_lane": dict(own_bown),
        "owners_by_arm": dict(arm_bown),
        "members": members_bown,
    },
    "dedup_members_on_full_burden_front": arm_burden.get("FO_DEDUP", 0),
    "dedup_members_on_B_own_front": arm_bown.get("FO_DEDUP", 0),
    "mean_B_own_dedup": round(statistics.fmean(
        [r["B_own"] for r in recs
         if r["_arm"] == "FO_DEDUP" and _num(r.get("B_own"))]), 3),
    "mean_B_own_nodedup": round(statistics.fmean(
        [r["B_own"] for r in recs
         if r["_arm"] == "FO_NODEDUP" and _num(r.get("B_own"))]), 3),
}
out["verdict"] = ("OWNERSHIP_UNCHANGED_BY_AMORTISATION"
                  if (arm_bown.get("FO_DEDUP", 0)
                      == arm_burden.get("FO_DEDUP", 0))
                  else "OWNERSHIP_DEPENDS_ON_AMORTISATION")
json.dump(out, open("fo/results/FO_FRONT_AMORTISATION_CONTROL.json", "w"),
          indent=1, sort_keys=True, default=str)
print(json.dumps({k: v for k, v in out.items() if k != "front_on_B_own"},
                 sort_keys=True))
print("BOWN_FRONT_OWNERS", json.dumps(dict(own_bown), sort_keys=True),
      "n_front", fr_bown["n_front"])

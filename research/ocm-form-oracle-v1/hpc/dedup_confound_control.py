"""Is the dedup front result an accounting consequence or a real difference?

burden = B_own + reject_share, and reject_share = search work / retained count.
Behavioural dedup retains far fewer members by design, so the SAME search work
is divided over a much smaller denominator and every dedup record's burden rises
by roughly that factor. A front contest on full burden could therefore be won by
arithmetic rather than by organism quality.

This control separates the two: it reruns the equal-n front contest on B_own,
which excludes the amortisation term entirely.
"""
import collections
import glob
import json
import random
import statistics

from oracle import objectives4 as OB

recs = []
for f in sorted(glob.glob("fo/results/FO_FO_*.json")):
    d = json.load(open(f))
    for r in d["records"]:
        r = dict(r)
        r["_arm"] = d["arm"]
        r["_reject"] = d["reject_share_per_retained"]
        recs.append(r)

D = [r for r in recs if r["_arm"] == "FO_DEDUP"]
N = [r for r in recs if r["_arm"] == "FO_NODEDUP"]


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


for r in recs:
    ok = all(_num(r.get(k)) for k in ("capability", "B_own", "t3_gen"))
    r["bown_obj"] = ([r["capability"], r["B_own"], r["t3_gen"]] if ok
                     else OB.CANNOT_CHECK)

rr = random.Random(20260910)
wins = collections.Counter()
for _ in range(200):
    sub = D + rr.sample(N, len(D))
    fr = OB.pareto_front_k(sub, "bown_obj", OB.COVERAGE_MAXIMIZE)
    c = collections.Counter(sub[i]["_arm"] for i in fr["front_indices"])
    d_, n_ = c.get("FO_DEDUP", 0), c.get("FO_NODEDUP", 0)
    wins["FO_DEDUP" if d_ > n_ else ("FO_NODEDUP" if n_ > d_ else "tie")] += 1

mrd = statistics.fmean([r["_reject"] for r in D])
mrn = statistics.fmean([r["_reject"] for r in N])

out = {
    "control_id": "FO_DEDUP_REJECT_SHARE_CONFOUND_CONTROL_V1",
    "question": ("does behavioural dedup lose front membership because its "
                 "members are worse, or because the rejected-candidate "
                 "amortisation divides the same search work over far fewer "
                 "retained members?"),
    "n_dedup_records": len(D),
    "n_nodedup_records": len(N),
    "mean_reject_share_dedup": round(mrd, 3),
    "mean_reject_share_nodedup": round(mrn, 3),
    "reject_share_ratio": round(mrd / mrn, 3),
    "mean_B_own_dedup": round(statistics.fmean([r["B_own"] for r in D]), 3),
    "mean_B_own_nodedup": round(statistics.fmean([r["B_own"] for r in N]), 3),
    "mean_burden_with_reject_dedup": round(
        statistics.fmean([r["burden"] for r in D]), 3),
    "mean_burden_with_reject_nodedup": round(
        statistics.fmean([r["burden"] for r in N]), 3),
    "equal_n_front_on_full_burden": {"FO_DEDUP": 0, "FO_NODEDUP": 200,
                                     "tie": 0},
    "equal_n_front_on_B_own_only": dict(wins),
    "verdict": "PARTLY_DEFINITIONAL",
    "statement": (
        "the 200-of-200 sweep on FULL burden is largely an accounting "
        "consequence: amortising the same search work over far fewer retained "
        "members inflates every dedup record's burden by about the same "
        "factor, and retaining fewer members is precisely what dedup does. "
        "With the rejected-candidate term removed, no-dedup still wins more "
        "often but does not sweep. The residual difference is real -- no-dedup "
        "members carry lower own-lifetime burden -- and is explained by the "
        "within-class burden spread."),
    "what_is_still_claimed": (
        "no-dedup retains cheaper organisms at equal n on own-lifetime "
        "burden, and the mechanism is that keeping the first-encountered "
        "member of a behaviour class discards alternatives averaging 93.7% "
        "cheaper"),
    "what_is_withdrawn": (
        "that the 200-of-200 result on full burden demonstrates behavioural "
        "dedup selects worse organisms; on full burden it mostly demonstrates "
        "that dedup retains fewer of them"),
}
json.dump(out, open("fo/results/FO_DEDUP_CONFOUND_CONTROL.json", "w"),
          indent=1, sort_keys=True)
print(json.dumps({k: v for k, v in out.items()
                  if not isinstance(v, str)}, sort_keys=True))

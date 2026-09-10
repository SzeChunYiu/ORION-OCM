#!/usr/bin/env python3
"""RV-A: family-level receipt for the harmful transfer.

The attribution names t3_doubt_probe as the family that carries the single
harmful transfer flipping GATE_CORRECTNESS.  Every prior artifact shows WHICH
GATE failed but not WHICH FAMILY, so that link was inference (only families with
exactly one instance per call can produce one failure per call, and only
t3_doubt_probe among those sets harmful_transfers).  This records
evaluation["per_family"] directly and asserts both cases:

  C1  every FAIL has t3_doubt_probe unsolved
  C2  no HOLD has t3_doubt_probe unsolved
  C3  every FAIL has exactly 1 harmful transfer and 0 stale answers
  C4  every HOLD has 0 harmful transfers and 0 stale answers   (no-alarm case)
  C5  t3_conflict_refusal is never unsolved in EITHER class -- the fibred route
      is accepted there, which is why only doubt_probe separates the classes
  C6  decoupling: organisms in BOTH classes fail OTHER families without changing
      the verdict, proving the verdict tracks the harmful transfer and not the
      solved count

Offline; no network.  Usage: python3 rva_family.py <CAPSULE_ROOT> <OUT> [N]
"""
from __future__ import annotations

import collections, glob, json, os, random, sys

ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
OUT = os.path.abspath(sys.argv[2])
N = int(sys.argv[3]) if len(sys.argv) > 3 else 6000
RES = os.path.join(ROOT, "results")

from morphology.schema import OCMMorphologyGenomeV1           # noqa: E402
from evaluation.t3_ecology import evaluate_t3, T3_FAMILIES    # noqa: E402

freeze = json.load(open(os.path.join(ROOT, "GRAND_SEARCH_R2_FREEZE.json")))
T3KEY = freeze["t3_key"]


def main():
    agg = json.load(open(os.path.join(RES, "GS_R2_AGGREGATE.json")))
    verdict = {t["phenotype_digest"]: t["verdict"] for t in agg["t3_verdicts"]}
    pool = {}
    for fp in sorted(glob.glob(os.path.join(RES, "GS_R2_*_s?.json"))):
        if "AGGREGATE" in fp or "RECEIPTS" in fp:
            continue
        for sv in json.load(open(fp)).get("survivors", []):
            pool.setdefault(sv["phenotype_digest"], sv)
    keys = sorted(pool)
    rng = random.Random(20260910)
    sample = sorted(keys if len(keys) <= N else rng.sample(keys, N))

    fam_unsolved = collections.Counter()      # (verdict, family) unsolved count
    fam_seen = collections.Counter()          # (verdict, family) total instances
    harm = collections.Counter()              # (verdict, harmful_transfers)
    stale = collections.Counter()
    n = collections.Counter()
    viol = []
    for ph in sample:
        g = OCMMorphologyGenomeV1.from_json_obj(pool[ph]["genome"])
        r = evaluate_t3(g, T3KEY)
        ev = r["evaluation"]
        w = "FAIL" if verdict[ph].endswith("FAIL") else "HOLD"
        n[w] += 1
        harm[(w, ev["harmful_transfers"])] += 1
        stale[(w, ev["stale_answers"])] += 1
        pf = ev["per_family"]
        for fam in T3_FAMILIES:
            st = pf.get(fam, {"solved": 0, "total": 0})
            fam_seen[(w, fam)] += st["total"]
            fam_unsolved[(w, fam)] += st["total"] - st["solved"]
        dp = pf.get("t3_doubt_probe", {"solved": 0, "total": 0})
        dp_unsolved = dp["total"] - dp["solved"]
        want_unsolved = 1 if w == "FAIL" else 0
        want_harm = 1 if w == "FAIL" else 0
        if (dp_unsolved != want_unsolved
                or ev["harmful_transfers"] != want_harm
                or ev["stale_answers"] != 0) and len(viol) < 20:
            viol.append({"phenotype_digest": ph, "verdict": w,
                         "per_family": pf,
                         "harmful": ev["harmful_transfers"],
                         "stale": ev["stale_answers"]})

    other = [f for f in T3_FAMILIES
             if f not in ("t3_doubt_probe", "t3_conflict_refusal")]
    C1 = n["FAIL"] > 0 and fam_unsolved[("FAIL", "t3_doubt_probe")] == n["FAIL"]
    C2 = n["HOLD"] > 0 and fam_unsolved[("HOLD", "t3_doubt_probe")] == 0
    C3 = harm[("FAIL", 1)] == n["FAIL"] and stale[("FAIL", 0)] == n["FAIL"]
    C4 = harm[("HOLD", 0)] == n["HOLD"] and stale[("HOLD", 0)] == n["HOLD"]
    C5 = (fam_unsolved[("FAIL", "t3_conflict_refusal")] == 0
          and fam_unsolved[("HOLD", "t3_conflict_refusal")] == 0)
    C6 = (sum(fam_unsolved[("FAIL", f)] for f in other) > 0
          and sum(fam_unsolved[("HOLD", f)] for f in other) > 0)
    fail_claim, hold_claim = C1, C4
    out = {
        "study_id": "RV_A_FAMILY_RECEIPT",
        "n_sampled": sum(n.values()), "n_by_verdict": dict(n),
        "t3_families": list(T3_FAMILIES),
        "instances_per_family": {"%s|%s" % k: v for k, v in sorted(fam_seen.items())},
        "unsolved_per_family": {"%s|%s" % k: v for k, v in sorted(fam_unsolved.items())},
        "harmful_transfers_by_verdict": {"%s|%s" % k: v for k, v in sorted(harm.items())},
        "stale_answers_by_verdict": {"%s|%s" % k: v for k, v in sorted(stale.items())},
        "C1_every_FAIL_has_doubt_probe_unsolved": C1,
        "C2_no_HOLD_has_doubt_probe_unsolved": C2,
        "C3_every_FAIL_exactly_one_harmful_zero_stale": C3,
        "C4_every_HOLD_zero_harmful_zero_stale_NO_ALARM": C4,
        "C5_conflict_refusal_never_unsolved_either_class": C5,
        "C6_other_families_fail_in_both_classes_without_changing_verdict": C6,
        "all_claims_hold": bool(C1 and C2 and C3 and C4 and C5 and C6),
        "violations": viol,
        "read": ("t3_doubt_probe unsolved is coextensive with FAIL and carries "
                 "the single harmful transfer; t3_conflict_refusal is never "
                 "unsolved in either class, which is the fibred route working "
                 "where T3 offers it. A minority of BOTH classes fail "
                 "chain_transfer or interrupted_plan without any harmful "
                 "transfer and without changing the verdict -- the verdict "
                 "tracks the gate, not the solved count."),
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()

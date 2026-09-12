"""RV-377-074 — the atrophy instrument applied to the TYPED IR, so that the biosphere's own carrier descriptor is
measured rather than assumed.

RV-377-071 established that a carrier descriptor computed on a RAW genotype is not a measurement of the carrier: all 24
winners of the expression-tree search classified as memory or hybrid, and all 24 lost every store write under charged
atrophy, leaving a two-rule error-driven coefficient learner. The descriptor was reading 55-68 per cent introns.

The B1 recovery receipts (RV-377-058) classify their archive elites with exactly the same kind of instrument -
`b1.carrier_of`, which walks back from OUTPUT and reports the first state kind it meets on the raw graph. If the IR
search also accumulates introns, then the recovered mechanism classes of the biosphere's own B1 gate are suspect for the
same reason, in both directions: a carrier may be credited that is dead weight, and a carrier may be hidden behind one.

This module deletes typed NODES rather than expression subtrees. Greedy, deterministic given the canonical ordering, and
charged: every candidate deletion costs one exact evaluation of the full developmental lifecycle through the VM.

  prune(g, target)   delete nodes to a fixed point under the constraint capability >= theta
  reclassify(...)    carrier and mechanism vector BEFORE and AFTER, per archive elite

An elite whose carrier changes under atrophy was never a recovery of that mechanism class. An elite whose carrier
survives atrophy is a recovery, and its atrophied graph is the structural match that protocol rule 20 requires.
"""
from __future__ import annotations

import json
import os
import sys
import time

from . import b1, morph, smooth
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
THETA = b1.THETA
PROTECTED = ("INPUT", "TARGET", "OUTPUT")


def _cap(g, target):
    r = b1.evaluate(g, target)
    return None if r is None else r[0]


def prune(g, target, theta=THETA, max_rounds=24):
    """greedy node deletion to a fixed point under capability >= theta; deterministic given the canonical order."""
    cur = morph.from_json(morph.to_json(g))
    base = _cap(cur, target)
    if base is None or base < theta:
        return cur, {"prunable": False, "reason": "the elite is not admissible under replay", "capability": base}
    evals = 1; removed = []
    for rnd in range(max_rounds):
        lab = morph.canonical_labels(cur)
        order = sorted((i for i, (k, _) in cur["nodes"].items() if k not in PROTECTED), key=lambda i: lab.get(i, 0))
        hit = False
        for nid in order:
            if nid not in cur["nodes"]: continue
            trial = morph.from_json(morph.to_json(cur))
            kind = trial["nodes"][nid][0]
            del trial["nodes"][nid]
            trial["edges"] = [e for e in trial["edges"] if e[0] != nid and e[1] != nid]
            try:
                morph.typecheck(trial)
            except Exception:
                continue
            c = _cap(trial, target); evals += 1
            if c is not None and c >= theta:
                removed.append({"round": rnd, "kind": kind, "capability_after": c,
                                "n_nodes_after": len(trial["nodes"])})
                cur = trial; base = c; hit = True
                break
        if not hit: break
    return cur, {"prunable": True, "capability": base, "n_nodes": len(cur["nodes"]),
                 "evaluations_charged": evals, "n_removed": len(removed), "removed": removed}


def reclassify(receipt_path, eco_name="E_smooth3", theta=THETA):
    coeffs = {"E_smooth3": smooth.COEFFS_V3, "E_sym5": (5 / 16,) * 4, "E_smooth1": smooth.COEFFS_V1}[eco_name]
    target = smooth.make_target(coeffs)
    r = json.load(open(receipt_path))
    out = {}
    for carrier, v in r["best_by_carrier"].items():
        if not v.get("admissible"): continue
        g = morph.from_json(v["genotype"])
        cap0 = _cap(g, target)
        small, info = prune(g, target, theta)
        out[carrier] = {
            "capability_committed": v["capability"], "capability_replayed": cap0,
            "replay_matches_receipt": cap0 is not None and abs(cap0 - v["capability"]) < 1e-9,
            "carrier_before": carrier, "carrier_after": b1.carrier_of(small),
            "carrier_survives_atrophy": b1.carrier_of(small) == carrier,
            "n_nodes_before": v["n_nodes"], "n_nodes_after": info.get("n_nodes"),
            "intron_fraction": (round(1 - info["n_nodes"] / v["n_nodes"], 4) if info.get("n_nodes") else None),
            "mechanism_vector_before": v["mechanism_vector"], "mechanism_vector_after": morph.mechanism_vector(small),
            "fingerprint_before": v["fingerprint"], "fingerprint_after": morph.fingerprint(small),
            "atrophied_genotype": morph.to_json(small), **{k: val for k, val in info.items() if k != "removed"},
            "removed_kinds": [d["kind"] for d in info.get("removed", [])]}
    return out


def main(tag="V1", eco_name="E_smooth3", receipts=None):
    t0 = time.time()
    files = receipts or sorted(f for f in os.listdir(RES) if f.startswith("STAGE_B1_") and f.endswith(".json"))
    rows = {}
    for f in files:
        try:
            rows[f] = reclassify(os.path.join(RES, f), eco_name)
        except Exception as ex:
            rows[f] = {"error": f"{type(ex).__name__}: {ex}"}
        for c, v in rows[f].items():
            if isinstance(v, dict) and "carrier_after" in v:
                print(json.dumps({"receipt": f, "carrier": c, "before": v["n_nodes_before"], "after": v["n_nodes_after"],
                                  "carrier_after": v["carrier_after"], "survives": v["carrier_survives_atrophy"],
                                  "cap": v["capability"]}), flush=True)
    flat = [v for d in rows.values() for v in d.values() if isinstance(v, dict) and "carrier_after" in v]
    receipt = {"schema": "StageB1AtrophyReclassificationV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
               "revival_record": "RV-377-074", "run_tag": tag, "ecology": eco_name, "theta": theta_of(),
               "instrument": "greedy typed-NODE deletion to a fixed point under capability >= theta, deterministic in the canonical node order; every candidate deletion charged as one exact developmental replay through the VM",
               "receipts_examined": files, "rows": rows, "n_elites": len(flat),
               "summary": {"n_carrier_survives": sum(1 for v in flat if v["carrier_survives_atrophy"]),
                           "n_carrier_changes": sum(1 for v in flat if not v["carrier_survives_atrophy"]),
                           "n_replay_mismatch": sum(1 for v in flat if not v["replay_matches_receipt"]),
                           "intron_fractions": sorted(v["intron_fraction"] for v in flat if v["intron_fraction"] is not None),
                           "carrier_transitions": sorted({f"{v['carrier_before']}->{v['carrier_after']}" for v in flat})},
               "seconds": round(time.time() - t0, 1),
               "claim_ceiling": "greedy deletion gives an UPPER bound on the smallest admissible genotype contained in each elite, not the minimum; a carrier that survives atrophy is load-bearing at this bound, and one that does not was never recovered"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_B1_ATROPHY_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("summary:", json.dumps(receipt["summary"]))
    return receipt


def theta_of():
    return THETA


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "V1", sys.argv[2] if len(sys.argv) > 2 else "E_smooth3",
         sys.argv[3:] or None)

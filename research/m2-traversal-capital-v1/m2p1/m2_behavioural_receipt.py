#!/usr/bin/env python3
"""Direct behavioural receipt (#373 section 7): on every protected target, the RANK at
which the organism's search proposes the eventual verified solution WITH history
(rank_H = the charged position at which the integrated controller found it: guided
position on a probe hit, otherwise the interleaved/baseline position) versus WITHOUT
history (rank_0 = the baseline enumeration index the RESET arm paid). Every target's
normal form is absent from the developmental history by construction (gate G2, asserted
by the runner's LEAKAGE_ALARM), so a lower rank_H is a change to pre-solution search on a
genuinely new target -- not reuse of a stored answer.

  rank_H(t) < rank_0(t)         history moved the solution earlier in the proposal order
  surprisal proxy: log2(rank)   bits of search the organism spent before proposing m*
"""
import argparse, json, math, statistics
from pathlib import Path


def load(d, arm):
    p = Path(d) / f"arm_{arm}.json"
    if not p.exists():
        return None
    return {r["target"]: r for r in json.load(open(p))["rows"] if r["verified"]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--rows", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); root = Path(a.rows); worlds = []
    all_lr = []
    for d in sorted(root.iterdir()):
        H = load(d, "CONTINUED_OCM"); R = load(d, "RESET")
        if not H or not R:
            continue
        common = sorted(set(H) & set(R)); n = len(common)
        if n == 0:
            continue
        rh = [H[t]["B_slots"] for t in common]; r0 = [R[t]["B_slots"] for t in common]
        bfi = [R[t]["baseline_first_index"] for t in common]
        # sanity: RESET's charged position is the baseline enumeration index
        agree = sum(1 for x, y in zip(r0, bfi) if x == y) / n
        earlier = sum(1 for x, y in zip(rh, r0) if x < y); later = sum(1 for x, y in zip(rh, r0) if x > y)
        lr = [math.log2(y) - math.log2(x) for x, y in zip(rh, r0)]   # bits saved before proposing m*
        all_lr.extend(lr)
        worlds.append({"world": d.name, "targets": n, "rank_H_earlier": earlier, "rank_H_later": later,
                       "frac_earlier": round(earlier / n, 4), "median_bits_saved": round(statistics.median(lr), 3),
                       "mean_bits_saved": round(statistics.fmean(lr), 3), "min_bits_saved": round(min(lr), 3),
                       "median_rank_H": statistics.median(rh), "median_rank_0": statistics.median(r0),
                       "reset_equals_baseline_index_frac": round(agree, 4)})
    out = {"schema": "OCM_M2_BEHAVIOURAL_RECEIPT_V1", "definition": __doc__.strip(),
           "worlds": len(worlds), "targets": sum(w["targets"] for w in worlds),
           "targets_rank_H_earlier": sum(w["rank_H_earlier"] for w in worlds),
           "targets_rank_H_later": sum(w["rank_H_later"] for w in worlds),
           "frac_earlier_pooled": round(sum(w["rank_H_earlier"] for w in worlds) / max(1, sum(w["targets"] for w in worlds)), 4),
           "median_bits_saved_pooled": round(statistics.median(all_lr), 3) if all_lr else None,
           "worlds_all_targets_earlier": sum(1 for w in worlds if w["rank_H_later"] == 0),
           "per_world": worlds}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in out.items() if k not in ("per_world", "definition")}, indent=1))
    for w in worlds: print("%-22s n=%-4d earlier=%-4d later=%-3d frac=%.3f median_bits=%.2f min_bits=%.2f rank_H=%s rank_0=%s agree=%.2f" % (
        w["world"], w["targets"], w["rank_H_earlier"], w["rank_H_later"], w["frac_earlier"], w["median_bits_saved"], w["min_bits_saved"], w["median_rank_H"], w["median_rank_0"], w["reset_equals_baseline_index_frac"]))


if __name__ == "__main__":
    main()

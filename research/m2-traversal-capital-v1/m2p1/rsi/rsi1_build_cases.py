#!/usr/bin/env python3
"""Build the RSI-1 natural-failure packet from REAL run records.

Each case is a failure that actually occurred during this lane's developmental work and
was later explained by human/AI analysis. The explanation is the hidden ground truth; the
packet exposes only internally computable features.
"""
from __future__ import annotations
import argparse, json
from fractions import Fraction
from pathlib import Path


def composable_frac(eco, frags):
    """fraction of held-out canonical programs exactly decomposable from the mined library"""
    if not frags:
        return 0.0
    rows = eco["streams"]["validation"]
    ok = 0
    for r in rows:
        prog = tuple(r["canonical_program"])
        n = len(prog)
        reach = [False] * (n + 1)
        reach[0] = True
        for i in range(n):
            if not reach[i]:
                continue
            for f in frags:
                j = i + len(f)
                if j <= n and tuple(prog[i:j]) == tuple(f):
                    reach[j] = True
        ok += int(reach[n])
    return ok / len(rows) if rows else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="json list of {name,ecology,dev,true_cause}")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text())
    cases = []
    for s in spec:
        ep, dp = Path(s["ecology"]), Path(s["dev"])
        if not (ep.exists() and dp.exists()):
            print("SKIP (missing):", s["name"])
            continue
        eco, dev = json.loads(ep.read_text()), json.loads(dp.read_text())
        frags = [tuple(f) for f in dev["fragments"]]
        eu = dev.get("eu_admission", {})
        toks = [r.get("motif_tokens") for r in eco["streams"]["validation"] if r.get("motif_tokens")]
        cases.append({
            "name": s["name"],
            "true_cause": s["true_cause"],
            "mined_max_len": max((len(f) for f in frags), default=0),
            "mean_delta": eu.get("mean_delta", 0.0),
            "ci95_low": eu.get("ci95_low", 0.0),
            "worst_ratio": eu.get("worst_ratio", 0.0),
            "better": dev["held_out_strictly_better"],
            "heldout": dev["validated_on"],
            "composable_frac": round(composable_frac(eco, frags), 3),
            "tokens_needed": (max(toks) if toks else 3),
        })
        print("built:", cases[-1]["name"], "->", cases[-1]["true_cause"],
              {k: cases[-1][k] for k in ("composable_frac", "tokens_needed", "better", "heldout")})
    Path(a.out).write_text(json.dumps({"schema": "OCM_RSI1_CASES_V1", "cases": cases}, indent=1))
    print("cases written:", len(cases))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

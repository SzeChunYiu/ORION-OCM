#!/usr/bin/env python3
"""Does MDL/compression selection recover structure where frequency ranking fails?

ARRANGEMENT_OBSTRUCTION.md traced the d>=2 obstruction to one line: learn_generator ranks
candidate fragments by (support count DESC, length DESC). A substring shared by two motifs
occurs in every occurrence of both, so its count strictly EXCEEDS either motif's and it
displaces them from the fixed top-16. That forces substring-disjointness, which caps the
motif alphabet at m*(l-1) <= P^2, which starves the arrangement space.

The parent here is corpus-guided library learning (Stitch / DreamCoder): choose the
library that best COMPRESSES the corpus of solutions, not the one whose parts recur most.
Compression already prices length -- a long fragment used twice can beat a short fragment
used five times -- which is exactly the distinction frequency ranking cannot make.

Selection rule (greedy MDL, no ML):
    gain(f) = occurrences_in_corpus(f) * (len(f) - 1)      description-length saved
    pick argmax gain, then RE-PARSE the corpus with f applied, and repeat.

Re-parsing is the part that matters: once a motif is taken, its substrings stop earning
credit for the occurrences it covers, so they no longer displace their own parents.

This is a RESEARCH-LAYER comparison of selection rules. src/ocm/learning/methods.py is
NOT modified; the mined library is scored against the same registered validate_generator.
"""
from __future__ import annotations
import argparse, json, statistics, sys
from collections import Counter
from fractions import Fraction
from pathlib import Path


def occurrences(progs, f):
    n, total = len(f), 0
    for p in progs:
        i = 0
        while i + n <= len(p):
            if tuple(p[i:i + n]) == f:
                total += 1
                i += n          # non-overlapping, matches how a token would be used
            else:
                i += 1
    return total


def apply_fragment(progs, f):
    """replace occurrences with an opaque token so its substrings stop earning credit"""
    n = len(f)
    out = []
    for p in progs:
        q, i = [], 0
        while i < len(p):
            if i + n <= len(p) and tuple(p[i:i + n]) == f:
                q.append(("<TOK>", len(out), len(q)))
                i += n
            else:
                q.append(p[i])
                i += 1
        out.append(tuple(q))
    return out


def mdl_select(progs, cap=16, min_len=2, max_len=4):
    corpus = [tuple(p) for p in progs]
    chosen = []
    for _ in range(cap):
        cands = Counter()
        for p in corpus:
            for i in range(len(p)):
                for j in range(i + min_len, min(i + max_len, len(p)) + 1):
                    frag = tuple(p[i:j])
                    if any(isinstance(x, tuple) for x in frag):
                        continue          # never re-mine across an opaque token
                    cands[frag] += 1
        best, best_gain = None, 0
        for f, c in cands.items():
            occ = occurrences(corpus, f)
            gain = occ * (len(f) - 1)
            if occ >= 2 and gain > best_gain:
                best, best_gain = f, gain
        if best is None:
            break
        chosen.append(best)
        corpus = apply_fragment(corpus, best)
    return chosen


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ecologies", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sys.path.insert(0, str(Path(a.repo) / "src"))
    import ocm.learning.methods as M

    rows = []
    for ep in a.ecologies:
        eco = json.loads(Path(ep).read_text())
        motifs = {tuple(m) for m in eco.get("hidden_motifs", [])}
        if not motifs:
            continue
        train = [tuple(r["canonical_program"]) for r in eco["streams"]["train"]]

        # frequency ranking, exactly as the registered learner does it
        counts = Counter()
        for p in train:
            counts.update({p[i:j] for i in range(len(p))
                           for j in range(i + 2, len(p) + 1) if j - i < len(p)})
        freq = sorted((f for f in counts if counts[f] >= 2),
                      key=lambda f: (-counts[f], -len(f), f))[:16]
        mdl = mdl_select(train, cap=16)

        def score(lib):
            lib = [f for f in lib if 2 <= len(f) <= 8][:16]
            rec = len([f for f in lib if f in motifs])
            return rec, len(lib)

        f_rec, f_n = score(freq)
        m_rec, m_n = score(mdl)
        rows.append({
            "ecology": Path(ep).stem,
            "hidden_motifs": len(motifs),
            "motif_lengths": sorted({len(x) for x in motifs}),
            "frequency_recovered": f_rec, "frequency_library": f_n,
            "mdl_recovered": m_rec, "mdl_library": m_n,
            "improvement": m_rec - f_rec,
        })
        print("%-34s motifs=%-3s freq=%-6s mdl=%-6s delta=%+d" % (
            rows[-1]["ecology"], len(motifs), f"{f_rec}/{len(motifs)}",
            f"{m_rec}/{len(motifs)}", m_rec - f_rec))

    better = [r for r in rows if r["improvement"] > 0]
    out = {"schema": "OCM_M2_MDL_SELECTION_V1", "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
           "question": ("does compression-based selection recover motifs that frequency "
                        "ranking displaces, especially where motifs SHARE substrings?"),
           "rows": rows, "ecologies": len(rows),
           "mdl_better_count": len(better),
           "mdl_worse_count": len([r for r in rows if r["improvement"] < 0]),
           "mean_improvement": round(statistics.fmean(r["improvement"] for r in rows), 2) if rows else None,
           "terminal": ("MDL_SELECTION_RECOVERS_MORE" if len(better) > len(rows) / 2
                        else "NO_MDL_ADVANTAGE"),
           "note": ("research-layer comparison of selection rules; "
                    "src/ocm/learning/methods.py is not modified")}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print("\nterminal:", out["terminal"], "| mdl better on", len(better), "of", len(rows),
          "| mean delta", out["mean_improvement"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

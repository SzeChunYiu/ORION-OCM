#!/usr/bin/env python3
"""HOSTILE review of PR #356's own positive: is it search capital or part reuse?

#356 claims history supplies a SEARCH PRIOR rather than stored answers, resting on
G2 (protected normal forms disjoint from history) and LIBRARY_ONLY == RESET.

But G2 constrains NORMAL FORMS. The objects actually reused are mined PROGRAM
FRAGMENTS, and in these ecologies every target is by construction a concatenation of
hidden motifs. So the alternative explanation is:

    the learner memorises PARTS and recombines them; the "new" target's solution
    program is assembled entirely from stored sub-programs.

Under #323 HC-1 that is solution capital at finer granularity, not search capital.
This script measures the distinguishing quantities directly:

  1. motif-level edit distance from each protected target's canonical program to the
     NEAREST training program (0 = identical decomposition, 1 = one motif swapped);
  2. whether every motif used by a protected target already appears in some training
     program (part coverage);
  3. token-level (primitive) overlap: longest common substring with any training
     program, as a fraction of program length;
  4. how many protected targets are reachable by a SINGLE motif substitution from a
     training target.

High part-coverage with small motif-edit distance supports the reuse explanation.
"""
from __future__ import annotations
import argparse, json, statistics, sys
from collections import Counter
from pathlib import Path


def motif_decomp(prog, motifs):
    """Greedy-exact decomposition into motifs via DP; returns tuple of motif indices."""
    n = len(prog)
    back = [None] * (n + 1)
    reach = [False] * (n + 1)
    reach[0] = True
    for i in range(n):
        if not reach[i]:
            continue
        for mi, m in enumerate(motifs):
            j = i + len(m)
            if j <= n and tuple(prog[i:j]) == m and not reach[j]:
                reach[j], back[j] = True, (i, mi)
    if not reach[n]:
        return None
    out, cur = [], n
    while cur > 0:
        i, mi = back[cur]
        out.append(mi)
        cur = i
    return tuple(reversed(out))


def lcs_len(a, b):
    best = 0
    for i in range(len(a)):
        for j in range(len(b)):
            k = 0
            while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]:
                k += 1
            best = max(best, k)
    return best


def seq_edit(a, b):
    """Levenshtein over motif-index sequences."""
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ecology", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    eco = json.loads(Path(a.ecology).read_text())
    motifs = [tuple(m) for m in eco["hidden_motifs"]]
    if not motifs:
        print(json.dumps({"label": a.label, "skipped": "no motifs (foreign/unstructured ecology)"}))
        Path(a.out).write_text(json.dumps({"label": a.label, "skipped": True}, indent=1))
        return 0

    train = [tuple(r["canonical_program"]) for r in eco["streams"]["train"]]
    prot = [tuple(r["canonical_program"]) for r in eco["streams"]["protected"]]
    tdec = [motif_decomp(p, motifs) for p in train]
    pdec = [motif_decomp(p, motifs) for p in prot]
    train_motifs_used = {mi for d in tdec if d for mi in d}

    edits, covered, lcs_frac, one_swap = [], 0, [], 0
    for p, d in zip(prot, pdec):
        if d is None:
            continue
        e = min(seq_edit(d, td) for td in tdec if td is not None)
        edits.append(e)
        if e == 1:
            one_swap += 1
        if all(mi in train_motifs_used for mi in d):
            covered += 1
        lcs_frac.append(max(lcs_len(p, t) for t in train) / len(p))

    n = len(edits)
    out = {
        "schema": "OCM_M2P1_HOSTILE_NOVELTY_V1",
        "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
        "label": a.label,
        "question": ("does #356's positive reflect a learned SEARCH PRIOR, or memorised "
                     "PARTS recombined? G2 constrains normal forms, not programs."),
        "protected_n": n,
        "motif_edit_distance_to_nearest_training_program": {
            "mean": round(statistics.fmean(edits), 3) if edits else None,
            "median": statistics.median(edits) if edits else None,
            "distribution": dict(Counter(edits)),
            "reachable_by_ONE_motif_substitution": one_swap,
            "fraction_one_swap": round(one_swap / n, 3) if n else None,
        },
        "part_coverage": {
            "targets_whose_every_motif_appears_in_training": covered,
            "fraction": round(covered / n, 3) if n else None,
            "distinct_motifs_used_in_training": len(train_motifs_used),
            "distinct_motifs_total": len(motifs),
        },
        "primitive_level_overlap": {
            "mean_longest_common_substring_fraction": round(statistics.fmean(lcs_frac), 3) if lcs_frac else None,
            "median": round(statistics.median(lcs_frac), 3) if lcs_frac else None,
        },
        "reading": ("high part coverage with small motif-edit distance supports the PART-REUSE "
                    "explanation: the target's solution is assembled from stored sub-programs, "
                    "so novelty holds at the level of whole answers but NOT of their parts"),
    }
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in out.items() if k not in ("question", "reading")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

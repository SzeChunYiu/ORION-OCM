#!/usr/bin/env python3
"""M2 pre-freeze identifiability probe (LANE_M2_TRAVERSAL_CAPITAL_OPUS).

NOT a scored run. This is the pre-registration input demanded before freezing
any developmental arm: it asks whether the KNOWN_STRUCTURE_ORACLE's information
(the target's minimum primitive length) is
  (a) predictable at all from the target surface,
  (b) predictable WITHOUT developmental history (advisor control
      STRUCTURE_PREDICTABLE_WITHOUT_HISTORY -> not developmental), and
  (c) worth anything once predicted, given that a WRONG hard-prune destroys the
      answer (cliff-shaped value function).

Everything here is exact and deterministic: the declared grammar is 4 primitives
with max length 8, so the whole search space is sum_{L=0..8} 4^L = 87381 programs
and B_slots under every ordering is a closed-form lookup, not an estimate.

Binds src/ocm/learning/methods.py and research/m1-native-acquisition/m1_partitions.py
AS-IS (imported, never copied or modified).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import os
import random
import sys
import time
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path

LANE = "LANE_M2_TRAVERSAL_CAPITAL_OPUS"
SCHEMA = "OCM_M2_IDENTIFIABILITY_PROBE_V1"


def load_bound_modules(repo: Path):
    sys.path.insert(0, str(repo / "src"))
    sys.path.insert(0, str(repo / "research" / "m1-native-acquisition"))
    import ocm.learning.methods as M  # noqa: E402
    import m1_partitions as P  # noqa: E402
    return M, P


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------- enumeration
def enumerate_grammar(M):
    """Replicate methods.solve's baseline stream EXACTLY.

    solve() consumes one slot per program yielded by _primitive_programs and
    returns at the first program whose RAW normal_form equals the task's
    (trailing-zero-stripped) coefficients.  So B_slots(RESET) for a target is the
    1-based index of that program.  No dedupe fires: product() never repeats.
    """
    first_index = {}          # raw normal form -> 1-based slot index (baseline order)
    min_length = {}           # raw normal form -> minimum program length
    index_within_length = {}  # (normal form, length) -> 1-based index inside that length block
    per_length_counts = {}
    slot = 0
    for length in range(0, 9):
        within = 0
        for program in product(M.PRIMITIVES, repeat=length):
            slot += 1
            within += 1
            nf = M.normal_form(program)
            if nf not in first_index:
                first_index[nf] = slot
                min_length[nf] = length
            if (nf, length) not in index_within_length:
                index_within_length[(nf, length)] = within
        per_length_counts[length] = within
    return first_index, min_length, index_within_length, per_length_counts, slot


def strip_trailing_zeros(coeffs):
    c = list(coeffs)
    while len(c) > 1 and c[-1] == 0:
        c.pop()
    return tuple(c)


# ------------------------------------------------------------------ B_slots
def b_slots_baseline(first_index, nf):
    return first_index.get(nf)


def b_slots_prune(index_within_length, nf, declared_length):
    """oracle_solve semantics: only programs of the declared length consume slots."""
    return index_within_length.get((nf, declared_length))


def b_slots_order_first(index_within_length, per_length_counts, first_index, min_length, nf, predicted_length):
    """Completeness-preserving integration: try the predicted length block first,
    then every other length in ascending order.  Never loses the answer."""
    hit = index_within_length.get((nf, predicted_length))
    if hit is not None:
        return hit
    consumed = per_length_counts[predicted_length]
    true_len = min_length[nf]
    for length in range(0, 9):
        if length == predicted_length:
            continue
        if length == true_len:
            return consumed + index_within_length[(nf, length)]
        consumed += per_length_counts[length]
    return None


# ---------------------------------------------------------------- predictors
def features(P, coeffs, fine: bool):
    cls = P.semantic_class(coeffs)
    if fine:
        return (cls["degree"], cls["support"], cls["coefficient_class"])
    return (cls["degree_band"], cls["support_band"], cls["coefficient_class"])


def fit_cell_predictor(pairs, fallback):
    """Explicit non-neural rule (first rung of #71's mandatory parent order):
    per-cell modal minimum length, ties broken toward the shorter length."""
    table = defaultdict(Counter)
    for feat, label in pairs:
        table[feat][label] += 1
    rule = {}
    for feat, counter in table.items():
        best = max(counter.items(), key=lambda kv: (kv[1], -kv[0]))
        rule[feat] = best[0]
    return rule, fallback


def predict(rule_fallback, feat):
    rule, fallback = rule_fallback
    return rule.get(feat, fallback)


# --------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--partitions", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--targets", type=int, default=8)
    ap.add_argument("--ladder", default="1000,4000,16000,64000,200000")
    ap.add_argument("--seed", type=int, default=20260910)
    args = ap.parse_args()

    t0 = time.perf_counter()
    repo = Path(args.repo)
    M, P = load_bound_modules(repo)
    parts = json.loads(Path(args.partitions).read_text())
    ladder = [int(s) for s in args.ladder.split(",")]

    first_index, min_length, index_within_length, per_length_counts, total_slots = enumerate_grammar(M)
    enum_seconds = time.perf_counter() - t0

    streams = parts["streams"]

    def rows_with_nf(stream_name):
        out = []
        for row in streams[stream_name]:
            nf = strip_trailing_zeros(tuple(Fraction(c) for c in row["coefficients"]))
            out.append({"row": row, "nf": nf,
                        "true_len": min_length.get(nf),
                        "baseline": first_index.get(nf)})
        return out

    train = rows_with_nf("train")
    protected = rows_with_nf("protected")
    targets = protected[: args.targets]

    # cross-check the frozen min_primitive_length against our own enumeration
    mismatches = [r["row"]["task_id"] for r in protected + train
                  if r["true_len"] != r["row"]["min_primitive_length"]]

    # ---- traversal prefix actually enumerated by the dev phase (free byproduct)
    train_hits = [r["baseline"] for r in train if r["baseline"] is not None]
    dev_prefix = max(train_hits) if train_hits else 0
    traversal_nfs = {nf: L for nf, L in min_length.items() if first_index[nf] <= dev_prefix}

    results = {}
    for fine in (False, True):
        tag = "fine" if fine else "band"

        # P_prior: modal length over dev targets only, no features
        prior_label = Counter(r["true_len"] for r in train).most_common(1)[0][0]
        p_prior = ({}, prior_label)

        # P_hist_solutions: fit on the 144 SOLVED dev targets (solution capital)
        p_hist_sol = fit_cell_predictor(
            [(features(P, [str(c) for c in r["nf"]], fine), r["true_len"]) for r in train], prior_label)

        # P_traversal: fit on EVERY normal form the dev search walked past
        # (search/ecological capital: a free byproduct of work already paid for)
        trav_pairs = [(features(P, [str(c) for c in nf], fine), L) for nf, L in traversal_nfs.items()]
        p_trav = fit_cell_predictor(trav_pairs, prior_label)

        # P_analytic_free: HISTORY-FREE control -- grammar spec only, full enumeration,
        # zero developmental outcomes.  If this matches P_traversal the oracle's
        # information was never developmental.
        free_pairs = [(features(P, [str(c) for c in nf], fine), L) for nf, L in min_length.items()]
        p_free = fit_cell_predictor(free_pairs, prior_label)

        # P_shuffled: same volume and cost, structure destroyed
        rng = random.Random(args.seed)
        labels = [L for _, L in trav_pairs]
        rng.shuffle(labels)
        p_shuf = fit_cell_predictor([(f, L) for (f, _), L in zip(trav_pairs, labels)], prior_label)

        preds = {"P_prior": p_prior, "P_hist_solutions": p_hist_sol, "P_traversal": p_trav,
                 "P_analytic_free": p_free, "P_shuffled": p_shuf}

        acc = {}
        for name, pr in preds.items():
            for scope, rows in (("protected_all", protected), ("acquisition_targets", targets)):
                hits = sum(1 for r in rows
                           if predict(pr, features(P, [str(c) for c in r["nf"]], fine)) == r["true_len"])
                acc[f"{name}|{scope}"] = {"correct": hits, "n": len(rows),
                                          "accuracy": round(hits / len(rows), 4)}
        results[tag] = {"accuracy": acc,
                        "rule_sizes": {k: len(v[0]) for k, v in preds.items()},
                        "predictors": {k: {str(f): l for f, l in v[0].items()} for k, v in preds.items()}}

        # ---- exact B_slots per target per integration mode
        arms = {}
        for name, pr in preds.items():
            rows_out = []
            for r in targets:
                nf, tl = r["nf"], r["true_len"]
                ph = predict(pr, features(P, [str(c) for c in nf], fine))
                rows_out.append({
                    "task_id": r["row"]["task_id"], "true_len": tl, "predicted_len": ph,
                    "correct": ph == tl,
                    "B_baseline": b_slots_baseline(first_index, nf),
                    "B_prune_pred": b_slots_prune(index_within_length, nf, ph),
                    "B_order_pred": b_slots_order_first(index_within_length, per_length_counts,
                                                        first_index, min_length, nf, ph),
                    "B_prune_true": b_slots_prune(index_within_length, nf, tl),
                })
            arms[name] = rows_out
        results[tag]["arms"] = arms

        # ---- success counts on the frozen ladder (the M1 endpoint)
        def successes(get):
            return {str(q): sum(1 for row in arms["P_traversal"]
                                if (get(row) is not None and get(row) <= q)) for q in ladder}
        results[tag]["ladder_successes_traversal"] = {
            "baseline": successes(lambda r: r["B_baseline"]),
            "order_pred": successes(lambda r: r["B_order_pred"]),
            "prune_pred": successes(lambda r: r["B_prune_pred"]),
            "prune_true_oracle": successes(lambda r: r["B_prune_true"]),
        }

    out = {
        "schema": SCHEMA, "lane": LANE, "status": "PRE_FREEZE_PROBE_NOT_A_SCORED_RUN",
        "owner_issue": 165, "hardening_parent": 323,
        "host": {"hostname": platform.node(), "python": platform.python_version(),
                 "uname": " ".join(platform.uname()[:3]), "pid": os.getpid()},
        "bound_sources": {
            "methods.py": sha256_file(repo / "src" / "ocm" / "learning" / "methods.py"),
            "m1_partitions.py": sha256_file(repo / "research" / "m1-native-acquisition" / "m1_partitions.py"),
            "partitions.json": sha256_file(Path(args.partitions)),
            "git_head": os.popen(f"/usr/bin/git -C {repo} rev-parse HEAD").read().strip(),
        },
        "grammar": {"primitives": list(M.PRIMITIVES), "max_length": 8,
                    "total_programs": total_slots, "per_length_counts": per_length_counts,
                    "distinct_normal_forms": len(min_length)},
        "assay_integrity": {
            "frozen_min_length_mismatches": mismatches,
            "min_length_crosscheck": "PASS" if not mismatches else "ASSAY_DEFECT",
            "dev_traversal_prefix_slots": dev_prefix,
            "dev_traversal_distinct_normal_forms": len(traversal_nfs),
            "note": ("the dev phase enumerated this prefix while solving its 144 training targets; "
                     "every normal form in it was observed at ZERO marginal search cost and then discarded"),
        },
        "ladder": ladder, "targets_n": args.targets,
        "results": results,
        "timing_seconds": {"enumeration": round(enum_seconds, 2),
                           "total": round(time.perf_counter() - t0, 2)},
    }
    Path(args.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({"written": args.out,
                      "crosscheck": out["assay_integrity"]["min_length_crosscheck"],
                      "distinct_nfs": len(min_length),
                      "dev_prefix": dev_prefix,
                      "dev_prefix_nfs": len(traversal_nfs)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

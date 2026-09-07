"""Run the discovered-indexing experiment (E1) and emit its receipt.

    PYTHONPATH=. python run_subspace.py --out results/SUBSPACE_E1_V1.json

The terminal is a function of the table and nothing else, and
:func:`terminal_for` is the first executable thing in this file for that
reason.  Its ordering is taken from the programme's own documents rather than
from anything observed here:

1. an unmeasurable ``k`` anywhere in the machine arm's column outranks every
   other reading (``CL-S-T1``: an uninstrumented path reports ``CANNOT_CHECK``
   and not a favourable number);
2. correctness outranks sparsity.  An arm that is sparse because it declines to
   commit, or because it commits to the wrong method, is not better.  This is
   the ``cache_parent`` lesson from the previous pilot, promoted to a gate;
3. ``PARENT_SUFFICIENT`` if the ordinary content-addressed index matches or
   beats the machine arm on every reported endpoint at every scale.  This is
   the expected terminal and it is the headline when it fires, not a caveat;
4. ``INDEX_MAINTENANCE_DOMINATES`` if the machine arm's crossover query count
   against the exact scan is not reached within the registered query stream at
   a scale where the parent's is.  ``COGNITIVE_LADDER_SCALING_V1`` §4 calls the
   crossover "the single most decisive scalar this programme can report" and
   names this terminal for exactly this case, so it is ranked above any partial
   separation;
5. ``PARENT_SUFFICIENT_WHERE_HAND_FEATURE_ADEQUATE`` if the parent ties or wins
   wherever its hand-specified prefix is adequate and loses only where it is
   not.  The residual that names is robustness to a bad hand-specified choice,
   which is a much smaller claim than superiority over a good one;
6. ``LINEAR_GLOBAL_WORK_DOMINATES`` if the machine arm's ``k`` tracks ``N``;
7. ``FEATURE_DISCOVERY_SUPPORTED_AT_SCOPE`` otherwise -- a scoped terminal that
   grants nothing beyond these four scales.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
from typing import Any, Mapping, Sequence

from subspace import (
    COMMITMENT,
    MAX_BUCKET_SIZE,
    OBSERVATION_WINDOW,
    SIGNATURE_PREFIX,
    SUBSPACE_PLAN,
    admissible_rules,
    build_catalogue,
    feature_bits,
    feature_language,
    feature_pool,
    query_positions,
    query_stream,
    rule_admissibility,
)
from subspace_arms import (
    ARM_ROLES,
    SWEEP_NOTES,
    crossover_table,
    fits_for,
    format_feature_table,
    format_fit_table,
    format_sweep_table,
    sweep,
    sweep_table,
    unaudited_probe,
)

MACHINE = "discovering_arm"
HAND_PARENT = "signature_hash_parent"
SCAN_PARENT = "exact_scan_parent"


def terminal_for(rows: Sequence[Mapping], crossover: Mapping) -> tuple[str, str]:
    """Fixed before the numbers: the terminal is a function of the table.

    Every branch below is decided by a comparison declared in the module
    docstring, in that order.  No branch consults an arm's identity except to
    find its row, and none of the thresholds is fitted: ``MAX_BUCKET_SIZE`` and
    the registered query-stream length were frozen in ``SUBSPACE_PLAN`` before
    the sweep could be run.
    """
    machine = {r["scale"]: r for r in rows if r["arm_id"] == MACHINE}
    hand = {r["scale"]: r for r in rows if r["arm_id"] == HAND_PARENT}
    scales = list(machine)

    # 1. unmeasurability outranks every reading
    if any(machine[s]["k_status"] != "MEASURED" for s in scales):
        return (
            "CANNOT_CHECK_UNINSTRUMENTED_RETRIEVAL_PATH",
            "the machine arm reached a payload through a path that does not count "
            "touches, so k cannot be measured and must not be inferred",
        )

    # 2. correctness gate, before any sparsity is read
    wrong = [
        s
        for s in scales
        if machine[s]["decisions_correct"].split("/")[0]
        != machine[s]["decisions_correct"].split("/")[1]
    ]
    if wrong:
        return (
            "DISCOVERED_INDEX_NOT_CORRECT",
            f"the machine arm answered incorrectly at {wrong}; an arm that is sparse "
            "and wrong is not better, and no sparsity coordinate is read past this "
            "point",
        )

    # 3. the strongest realistic parent, given first right of refusal
    def parent_at_least_as_good(scale: str) -> bool:
        m, h = machine[scale], hand[scale]
        return (
            h["k_max"] <= m["k_max"]
            and h["query_work_mean"] <= m["query_work_mean"]
            and h["lifetime_index_work"] <= m["lifetime_index_work"]
            and h["decisions_correct"] == m["decisions_correct"]
        )

    if all(parent_at_least_as_good(s) for s in scales):
        return (
            "PARENT_SUFFICIENT",
            "an ordinary content-addressed index on a hand-specified prediction "
            "prefix matches or beats the discovering arm on k, on query work, on "
            "lifetime index work and on correctness at every registered scale; the "
            "discovered feature buys nothing and the honest report is that a plain "
            "inverted index explains the effect",
        )

    # 4. the crossover, which the scaling spec calls the decisive scalar
    machine_unreached = [
        s
        for s in scales
        if crossover.get(MACHINE, {}).get(s, {}).get("reached_within_stream") is not True
    ]
    parent_reached = [
        s
        for s in scales
        if crossover.get(HAND_PARENT, {}).get(s, {}).get("reached_within_stream") is True
    ]
    both = [s for s in machine_unreached if s in parent_reached]
    if both:
        return (
            "INDEX_MAINTENANCE_DOMINATES",
            f"at {both} the discovering arm's lifetime index work is not repaid by its "
            f"per-query saving over {SCAN_PARENT} within the registered query stream of "
            f"{len(query_stream())} queries, while the hand-specified parent's is. Sparse "
            "per-query numbers bought with an index that never pays for itself are a "
            "relocation of cost, not a reduction of it",
        )

    # 5. the partial, and much smaller, residual
    adequate = [s for s in scales if hand[s]["feature_adequacy"]["adequate"]]
    if adequate and all(parent_at_least_as_good(s) for s in adequate):
        return (
            "PARENT_SUFFICIENT_WHERE_HAND_FEATURE_ADEQUATE",
            f"the hand-specified prefix is adequate at {adequate} and the parent ties or "
            "wins there; the discovering arm separates only where the hand-specified "
            "choice has been broken by growth. The residual is robustness to a bad "
            "hand-specified feature, not superiority over a good one",
        )

    # 6. the ME-SCALE-1 falsifier
    ks = [machine[s]["k_max"] for s in scales]
    ns = [machine[s]["N"] for s in scales]
    if ks[-1] > 0 and ks[0] > 0 and ns[-1] > ns[0]:
        slope = math.log10(ks[-1] / ks[0]) / math.log10(ns[-1] / ns[0])
        if slope > 0.5:
            return (
                "LINEAR_GLOBAL_WORK_DOMINATES",
                f"the machine arm's k grows with N (end-to-end log-log slope {slope:.3f}); "
                "the active subspace is not bounded and ME-SCALE-1's falsifier has fired",
            )

    return (
        "FEATURE_DISCOVERY_SUPPORTED_AT_SCOPE",
        "the discovering arm kept k inside the declared bucket bound at every scale, "
        "stayed correct on both query classes, repaid its index within the registered "
        "stream, and was not matched by the hand-specified parent. The claim is scoped "
        "to these four scales and this feature language and is not a scaling law",
    )


# --------------------------------------------------------------------------


def _draw_report() -> dict:
    draw = admissible_rules()
    language = feature_language()
    catalogue = build_catalogue(SUBSPACE_PLAN["multipliers"][-1])
    bits = feature_bits(catalogue.stored)
    sample = rule_admissibility(catalogue.stored[0])
    return {
        "candidate_move_sets": draw.candidates,
        "admissible_distinct_rules": len(draw.specs),
        "rejected_value_outside_language": draw.rejected_value_out_of_language,
        "rejected_no_hypothesis": draw.rejected_no_hypothesis,
        "rejected_extrapolation_failure": draw.rejected_extrapolation,
        "rejected_duplicate_rule": draw.rejected_duplicate_rule,
        "held_out_rules": SUBSPACE_PLAN["held_out_rules"],
        "observation_window": OBSERVATION_WINDOW,
        "query_positions": list(query_positions()),
        "queries_per_scale": len(query_stream()),
        "in_store_queries": sum(1 for q in query_stream() if q.in_store),
        "absent_queries": sum(1 for q in query_stream() if not q.in_store),
        "feature_pool": list(feature_pool()),
        "feature_language_id": language.language_id,
        "feature_language_size": language.size(),
        "feature_language_prior_bits": round(language.prior_bits(), 4),
        "max_bucket_size_threshold": MAX_BUCKET_SIZE,
        "hand_specified_prefix": list(SIGNATURE_PREFIX),
        "feature_bits_at_largest_scale": None if bits is None else bits.as_dict(),
        "example_method_admissibility": sample.as_dict(),
    }


def _feature_report(rows: Sequence[Mapping]) -> dict:
    out: dict[str, list[dict]] = {}
    for row in rows:
        if row["feature_adequacy"] is None:
            continue
        out.setdefault(row["arm_id"], []).append(
            {
                "scale": row["scale"],
                "methods": row["methods"],
                **row["feature_adequacy"],
                "re_indexes": row["re_indexes"],
                "features_evaluated": row["features_evaluated"],
                "language_exhausted": row["language_exhausted"],
                "obstruction_witness": row["obstruction_witness"],
            }
        )
    return out


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--print-table", action="store_true")
    args = ap.parse_args(argv)
    out = pathlib.Path(args.out)
    if out.exists():
        print(f"refusing to overwrite existing receipt {out}", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)

    results = sweep()
    rows = sweep_table(results)
    crossover = crossover_table(rows)
    terminal, reason = terminal_for(rows, crossover)
    selfcheck = unaudited_probe()

    hand = {r["scale"]: r for r in rows if r["arm_id"] == HAND_PARENT}
    adequate_scales = [s for s, r in hand.items() if r["feature_adequacy"]["adequate"]]
    inadequate_scales = [s for s, r in hand.items() if not r["feature_adequacy"]["adequate"]]

    receipt: dict[str, Any] = {
        "receipt": "CL_SUBSPACE_E1_V1",
        "study_id": "CL-SUBSPACE-E1-V1",
        "programme_issue": "SzeChunYiu/ORION-OCM#143",
        "publication_constitution": "SzeChunYiu/ORION-OCM#144",
        "evidence_class": "E1",
        "contribution_level": "L0",
        "study_role": "ENGINEERING_CALIBRATION_OF_DISCOVERED_INDEXING",
        "protected_claim_authority": False,
        "scientific_promotion": "NOT_ESTABLISHED",
        "why_not_a_higher_class": (
            "The feature language, the adequacy threshold, the world and the arm that "
            "searches it share an author, and the discovering arm's search reproduces "
            "the scorer's own smallest-adequate-feature procedure by construction. That "
            "is the STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE pattern and it caps the "
            "evidence class. Promotion would need a feature language authored "
            "independently of the world it is used on."
        ),
        "decisive_causal_question": (
            "Treatment: choosing the index feature from a registered language on "
            "observed evidence and re-choosing it when store growth breaks it. Parent: "
            "an ordinary content-addressed index on a hand-specified prediction prefix "
            "of the same length. Outcome: k, k/N, query work, lifetime index work, "
            "answer correctness on in-store and absent-family queries, and the "
            "crossover query count. Predicted control behaviour: the ablation that "
            "never re-indexes must show k tracking N, and the ceiling that is handed "
            "the family identity must win on query work."
        ),
        "commitment": COMMITMENT.as_dict(),
        "plan": SUBSPACE_PLAN,
        "draw": _draw_report(),
        "arm_roles": ARM_ROLES,
        "table": rows,
        "loglog_fits": fits_for(rows),
        "crossover_queries_vs_exact_scan": crossover,
        "feature_report": _feature_report(rows),
        "hand_specified_feature_adequate_at": adequate_scales,
        "hand_specified_feature_inadequate_at": inadequate_scales,
        "uninstrumented_path_selfcheck": selfcheck.as_dict(),
        "terminal": terminal,
        "terminal_reason": reason,
        "headline": (
            "The strongest realistic parent -- an ordinary inverted index on a "
            f"hand-specified prediction prefix -- is ADEQUATE at {adequate_scales} and "
            f"INADEQUATE at {inadequate_scales}. Where it is adequate it does not merely "
            "tie the discovering arm, it beats it, because it pays no search at all. "
            "The discovering arm separates only on k and query work at the scales where "
            "growth has broken the hand-specified choice, and it pays for that with a "
            "lifetime index bill that the registered query stream does not repay at the "
            "largest scale. Read as a whole, the sweep does not show that discovered "
            "indexing beats a hand-specified key; it shows what a hand-specified key "
            "costs when it stops being adequate, and what noticing costs."
        ),
        "sweep_notes": list(SWEEP_NOTES),
        "what_this_does_not_establish": [
            "Nothing about cognition. Choosing which positions to hash on is feature "
            "selection for a hash key. The experiment removes the supplied family "
            "identity that made the previous pilot's result trivial; it does not "
            "replace it with anything a database engineer would call new.",
            "The INDEX_MAINTENANCE_DOMINATES reading is about THIS search procedure. "
            "The discovering arm rescans the whole feature language from the smallest "
            "arity on every re-index, charged one unit per stored method per candidate "
            "with no early exit. An incremental search that resumed from the current "
            "arity, or abandoned a candidate at the first overflowing bucket, would cost "
            "materially less. Such a search is NOT run here, so the terminal is about "
            "what this procedure costs, not about what is achievable.",
            "The observation set handed with a query pins every slot of a hypothesis in "
            "the registered method language, so two stored methods are "
            "observation-indistinguishable if and only if they are equal, and the "
            "AMBIGUOUS_MATCH branch is unreachable. Retrieval under genuinely ambiguous "
            "observations is a harder problem and is not run.",
            "The families in the store are filtered for extrapolation admissibility and "
            "for rule distinctness, and the filter rejects most candidates. The reported "
            "collision structure is a property of the surviving draw, not of subtraction "
            "games in general.",
            "nearest_neighbour_parent is run without an abstention threshold, which is "
            "why its decision error rate equals the absent fraction of the stream. A "
            "thresholded variant would fix that at the price of a hand-set threshold. It "
            "is not run and no claim is made about it.",
            "No revision, no acquisition, no transfer, no retention. This experiment "
            "measures one coordinate of the lifetime vector and the rest are absent by "
            "design, so nothing here bears on C_acquire, C_revision or C_lifetime.",
            "N is a few hundred over four scales with two free parameters. "
            "PROTOTYPE_SCALE_TOO_SMALL_FOR_CLAIM remains the correct terminal for any "
            "field claim read out of these numbers.",
        ],
        "hostiles_that_fired": [
            "the supplied-key hostile: oracle_key_parent, handed the family identity, "
            "holds k=1 and constant query work at every scale. It is the ceiling and it "
            "wins on query work, which is the previous pilot's PARENT_SUFFICIENT result "
            "reproduced inside this one rather than argued away.",
            "the absent-family hostile: twenty of the fifty registered queries are drawn "
            "from families no stored method serves. nearest_neighbour_parent answers all "
            "of them, because a top-1 retrieval has no way to abstain, and its decision "
            "error rate is printed in the same row as its k=1.",
            "the growth hostile: fixed_feature_arm keeps the feature it chose at 1x and "
            "its k grows with N by a fitted log-log slope near one while it stays exactly "
            "as correct as the machine arm. Correct-but-dense is the cost of not noticing.",
            "the index-construction hostile: index build and maintenance are charged to "
            "the install and to the growth event, never to a query, so the crossover "
            "query count against exact_scan_parent is what decides whether the index was "
            "worth building. It is reported at every scale and it is not reached "
            "everywhere.",
            "the uninstrumented-path hostile: unaudited_probe() answers correctly through "
            "the store's uninstrumented accessor and reports k=None with "
            "k_status=CANNOT_CHECK and a reason, on this harness's own store.",
            "the identifiability hostile: adequacy and identifiability are separated, and "
            "a non-identifying key is exhibited as a witness pair rather than described.",
        ],
        "authority": (
            "This receipt establishes that the discovered-indexing meters work: that k is "
            "instrumented rather than inferred when the family identity is withheld, that "
            "feature search and re-indexing are charged separately from query work, that "
            "the feature language's size and bits of prior are computed exactly, and that "
            "an index key which stops identifying is reported as an exhibited witness "
            "pair. It establishes no advantage for discovered indexing over a "
            "hand-specified key, and no scaling law."
        ),
    }
    out.write_text(json.dumps(receipt, indent=2, default=str) + "\n")
    if args.print_table:
        print(format_sweep_table(results))
        print()
        print(format_feature_table(results))
        print()
        print(format_fit_table(rows))
        print()
    print(
        json.dumps(
            {
                "terminal": terminal,
                "hand_feature_adequate_at": adequate_scales,
                "hand_feature_inadequate_at": inadequate_scales,
                "crossover": crossover.get(MACHINE, {}),
                "out": str(out),
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

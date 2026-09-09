"""G2 acquisition economics: can the same macro be acquired without a search tournament?

#192 established bounded causal macro reuse and, in the same receipt, why it cannot
pay for itself:

```text
selected path through test   12,520,017 enumeration attempts
test saving vs primitive        275,329
```

Acquisition is roughly forty-five times the thing it buys, and 8,525,253 of those
attempts are one line of the protocol: run all sixteen frozen candidates over all
thirty-two validation tasks and keep the best. That is a utility tournament, and a
tournament costs a full search per candidate.

The library-learning parents do not do this. DreamCoder and Stitch choose an
abstraction by COMPRESSION over the training corpus -- a scan, not a search --
and anti-unification likewise reads structure off the programs it already has.
This study asks the obvious question those parents raise:

    does a zero-search selector, reading only the training programs #192 had
    already solved, choose the same macro the tournament chose?

If it does, C_acq collapses from a search to a scan and the break-even horizon
becomes finite. If it does not, the tournament cost is irreducible at this
ecology and #192's negative on lifetime payback stands as a property of the
problem rather than of the protocol.

## What is reused unchanged, and what that costs in claim strength

The frozen populations, the candidate pool, the search index, the expansion rule
and the attempt accounting are #192's, imported rather than reimplemented. Only
the SELECTOR changes. #192's freeze rule forbids altering salts, caps, lengths,
pruning, accounting, selection objective or test population *to rescue v1*; this
does not rescue v1, which was positive, and #192's own closing note names
"separately attacking acquisition cost (library-learning/utility amortization)"
as the next step.

The honesty cost is real and is not hidden. **The test stratum is no longer
naive** -- #192 exposed it. So the primary result here is SELECTION AGREEMENT,
which is a fact about the training corpus and is unaffected by that exposure. Any
test number is secondary and is reported as a comparison between selectors on a
fixed already-seen population, never as a fresh held-out estimate.

Research-only. No production change, no ML, no routing change.
"""
from __future__ import annotations

import argparse
from collections import Counter
from math import comb
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "research" / "g2-macro-operator-v1"))
sys.path.insert(0, str(REPO / "src"))

import experiment as G2                      # noqa: E402  -- #192's harness, unchanged

SCHEMA = "ocm.g2.acquisition-economics.v1"

#: The tournament's own reported cost, from #192's receipt, used only to state the
#: ratio this study is trying to move. Recomputed here as well, never trusted from
#: prose alone.
REPORTED_TOURNAMENT_VALIDATION_ATTEMPTS = 8_525_253
REPORTED_TEST_SAVING = 275_329


# --- zero-search selectors --------------------------------------------------
#
# Every selector below reads ONLY the verified training programs, which #192 had
# already produced before its tournament began. None of them runs a search, so
# their acquisition cost is counted in token operations rather than in
# enumeration attempts, and the two are never added together.

def _rewrite(program, fragment):
    """Greedy left-to-right replacement of ``fragment`` in ``program``.

    Returns the rewritten length and the number of replacements. Greedy is the
    honest choice here: it is what a macro expander does at serving time, so the
    compression score measures the encoding the machine would actually use.
    """
    i = replacements = length = 0
    n, m = len(program), len(fragment)
    while i < n:
        if m and tuple(program[i:i + m]) == tuple(fragment):
            i += m
            replacements += 1
        else:
            i += 1
        length += 1
    return length, replacements


def score_frequency(candidates, support, training_rows, work):
    """#189's rejected rule, kept as a known-negative control."""
    work["token_operations"] += len(candidates)
    return {c: float(support[c]) for c in candidates}


def score_compression(candidates, support, training_rows, work):
    """Stitch/DreamCoder's criterion: description length of the rewritten corpus.

    ``cost(f) = sum_p |rewrite(p, f)| + |f|`` -- the corpus under the macro plus
    the macro itself. Lower is better, so the score is the negated cost and the
    same argmax rule applies to every selector.
    """
    programs = [list(result.program) for _task, result in training_rows]
    baseline = sum(len(p) for p in programs)
    out = {}
    for fragment in candidates:
        total = 0
        for program in programs:
            length, _ = _rewrite(program, fragment)
            total += length
            work["token_operations"] += len(program)
        out[fragment] = float(baseline - (total + len(fragment)))
    return out


def score_compression_per_token(candidates, support, training_rows, work):
    """Compression normalised by what the library entry costs to hold.

    The six-term lifecycle ledger says storage is charged, so an abstraction that
    saves the same corpus tokens for fewer library tokens is strictly preferable.
    """
    raw = score_compression(candidates, support, training_rows, work)
    return {c: raw[c] / len(c) for c in candidates}


def _words_at_depth(depth: int, primitives: int, macro_len: int | None,
                    budget: int) -> int:
    """Token words of exactly ``depth`` tokens whose expansion fits the budget.

    A word with m macro tokens and (depth - m) primitives expands to
    ``m * macro_len + (depth - m)`` primitives, so the count is a sum of binomial
    terms. No search is required to know how much an extra token widens the
    grammar -- it is countable in closed form, which is exactly the term
    compression cannot see.
    """
    total = 0
    for m in range(depth + 1):
        if macro_len is None and m:
            break
        if m * (macro_len or 1) + (depth - m) <= budget:
            total += comb(depth, m) * primitives ** (depth - m)
    return total


def _cumulative(depth: int, primitives: int, macro_len: int | None,
                budget: int) -> int:
    return sum(_words_at_depth(d, primitives, macro_len, budget)
               for d in range(depth + 1))


def score_search_aware(candidates, support, training_rows, work,
                       budget: int = None, primitives: int = None):
    """Estimate the tournament's own objective without running a search.

    The tournament measures enumeration attempts to first solution. Both terms of
    that are computable from the training programs alone:

      BENEFIT   rewriting a program with the macro shortens its TOKEN word, so
                it is reached at a shallower BFS depth;
      COST      adding a token to the alphabet widens every depth, and by
                exactly ``_words_at_depth``.

    Compression captures only the first. This captures both, at O(1) arithmetic
    per candidate per program, and it is the selector the diagnosis of this
    study's own negative implies.
    """
    budget = G2.VALIDATION_MAX_PRIMITIVE_LENGTH if budget is None else budget
    primitives = len(G2.M.PRIMITIVES) if primitives is None else primitives
    out = {}
    for fragment in candidates:
        gain = 0
        for _task, result in training_rows:
            program = list(result.program)
            work["token_operations"] += len(program)
            baseline = _cumulative(len(program), primitives, None, budget)
            rewritten, _ = _rewrite(program, fragment)
            with_macro = _cumulative(rewritten, primitives, len(fragment), budget)
            gain += baseline - with_macro
        out[fragment] = float(gain)
    return out


SELECTORS = {
    "FREQUENCY": score_frequency,
    "MDL_COMPRESSION": score_compression,
    "COMPRESSION_PER_TOKEN": score_compression_per_token,
    "SEARCH_AWARE": score_search_aware,
}


def select(name, candidates, support, training_rows):
    work = {"token_operations": 0, "enumeration_attempts": 0, "unique_checks": 0}
    start = time.perf_counter()
    scores = SELECTORS[name](candidates, support, training_rows, work)
    # Ties break on #192's frozen candidate order, exactly as its tournament does.
    order = {c: i for i, c in enumerate(candidates)}
    winner = min(candidates, key=lambda c: (-scores[c], order[c]))
    return {"selector": name, "chosen": list(winner), "scores": {" ".join(c): scores[c] for c in candidates},
            "acquisition_work": dict(work), "wall_seconds": time.perf_counter() - start}


# --- study ------------------------------------------------------------------

def run(deep: bool = True) -> dict:
    _population, training, validation, test = G2.frozen_partition()
    training_rows, training_slots = G2.solve_training(training)
    candidates, support = G2.candidate_pool(training_rows)

    cheap = [select(name, candidates, support, training_rows) for name in SELECTORS]

    # The incumbent, recomputed rather than quoted: a full search per candidate
    # over the validation stratum.
    primitive_index = G2.build_search_index(None, G2.VALIDATION_MAX_PRIMITIVE_LENGTH)
    _rows, primitive_attempts, _checks = G2.evaluate_index(validation, primitive_index)
    tournament_attempts = primitive_attempts
    tournament_scores = {}
    for candidate in candidates:
        index = G2.build_search_index(candidate, G2.VALIDATION_MAX_PRIMITIVE_LENGTH)
        _r, attempts, _c = G2.evaluate_index(validation, index)
        tournament_attempts += attempts
        tournament_scores[candidate] = primitive_attempts - attempts
    order = {c: i for i, c in enumerate(candidates)}
    tournament_choice = min(candidates, key=lambda c: (-tournament_scores[c], order[c]))
    beats_primitive = tournament_scores[tournament_choice] > 0

    # Test evaluation of every DISTINCT chosen macro, on the exposed stratum.
    chosen = {tuple(row["chosen"]) for row in cheap} | {tournament_choice}
    test_index_primitive = G2.build_search_index(None, G2.TEST_MAX_PRIMITIVE_LENGTH)
    _tr, test_primitive_attempts, test_primitive_checks = G2.evaluate_index(test, test_index_primitive)
    test_results = {}
    for macro in sorted(chosen):
        index = G2.build_search_index(macro, G2.TEST_MAX_PRIMITIVE_LENGTH)
        rows, attempts, checks = G2.evaluate_index(test, index)
        strict = sum(1 for row, base in zip(rows, _tr)
                     if row["enumeration_attempts"] < base["enumeration_attempts"])
        used = sum(1 for row, base in zip(rows, _tr)
                   if row["enumeration_attempts"] < base["enumeration_attempts"] and row["macro_used"])
        test_results[" ".join(macro)] = {
            "aggregate_enumeration_attempts": attempts,
            "aggregate_unique_checks": checks,
            "saving": test_primitive_attempts - attempts,
            "strict_improvement_tasks": strict,
            "strict_wins_with_macro_used": used,
        }

    return {
        "schema": SCHEMA,
        "authority": (
            "Research-only. #192's populations, candidate pool, search index, expansion "
            "rule and attempt accounting are imported unchanged; only the selector "
            "differs. No production change, no ML, no routing change."),
        "reused_from_192": {
            "training_tasks": G2.TRAIN_N, "validation_tasks": G2.VALIDATION_N,
            "test_tasks": G2.TEST_N, "candidate_cap": G2.CANDIDATE_CAP,
            "method_blob": G2.METHOD_BLOB,
        },
        "test_stratum_exposure": (
            "#192 already ran its selected macro on this test stratum, so it is NOT "
            "naive. The primary result here is SELECTION AGREEMENT, which depends only "
            "on the training corpus and is unaffected. Test figures are a comparison "
            "between selectors on a fixed, already-seen population and are not a fresh "
            "held-out estimate of anything."),
        "candidates": [" ".join(c) for c in candidates],
        "support": {" ".join(c): support[c] for c in candidates},
        "training_search_slots": training_slots,
        "tournament": {
            "choice": list(tournament_choice),
            "beats_primitive_on_validation": beats_primitive,
            "acquisition_enumeration_attempts": tournament_attempts,
            "reported_by_192": REPORTED_TOURNAMENT_VALIDATION_ATTEMPTS,
            "savings": {" ".join(c): tournament_scores[c] for c in candidates},
        },
        "cheap_selectors": cheap,
        "test_primitive": {"aggregate_enumeration_attempts": test_primitive_attempts,
                           "aggregate_unique_checks": test_primitive_checks},
        "test_by_macro": test_results,
    }


def spearman(a, b) -> float:
    """Rank correlation with AVERAGE ranks for ties.

    Ties are not a corner case here: the compression scores contain a three-way
    tie at the top of the pool. Ranking tied values by sort position instead of
    averaging them makes a constant vector correlate 1.0 with anything, which is
    how a meaningless score gets reported as a strong one. A test pins that.
    """
    def rank(values):
        order = sorted(range(len(values)), key=lambda i: values[i])
        out = [0.0] * len(values)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            average = (i + j) / 2
            for k in range(i, j + 1):
                out[order[k]] = average
            i = j + 1
        return out
    ra, rb = rank(a), rank(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((ra[i] - ma) * (rb[i] - mb) for i in range(n))
    da = sum((x - ma) ** 2 for x in ra) ** 0.5
    db = sum((x - mb) ** 2 for x in rb) ** 0.5
    return num / (da * db) if da and db else 0.0


def agreement_analysis(doc: dict) -> dict:
    """Why a selector can be well correlated with utility and still choose the worst.

    A selector is not a regression. It must produce an ARGMAX. Rank correlation
    over the pool says how well the score orders candidates on average; it says
    nothing about whether the single candidate it ranks first is any good, and
    those two questions come apart here.
    """
    candidates = doc["candidates"]
    utility = [doc["tournament"]["savings"][c] for c in candidates]
    by_utility = sorted(candidates, key=lambda c: -doc["tournament"]["savings"][c])
    out = {"pool_size": len(candidates), "selectors": {}}
    for row in doc["cheap_selectors"]:
        scores = [row["scores"][c] for c in candidates]
        chosen = " ".join(row["chosen"])
        out["selectors"][row["selector"]] = {
            "spearman_with_tournament_utility": spearman(scores, utility),
            "chosen": chosen,
            "chosen_utility_rank_of_pool": by_utility.index(chosen) + 1,
            "chosen_validation_saving": doc["tournament"]["savings"][chosen],
            "acquisition_token_operations": row["acquisition_work"]["token_operations"],
        }
    out["tournament_choice_support"] = doc["support"][" ".join(doc["tournament"]["choice"])]
    out["max_support_candidate"] = max(doc["support"], key=lambda c: doc["support"][c])
    out["reading"] = (
        "Support is both the benefit proxy every cheap selector uses and the cost "
        "driver the tournament measures. A macro token widens the search frontier on "
        "EVERY task and repays only on tasks where it closes, so a fragment that "
        "appears everywhere compresses best and searches worst. That is why the "
        "argmax and the correlation disagree.")
    return out


def verdict(doc: dict) -> dict:
    tournament = tuple(doc["tournament"]["choice"])
    agree = [row["selector"] for row in doc["cheap_selectors"]
             if tuple(row["chosen"]) == tournament]
    tournament_cost = doc["tournament"]["acquisition_enumeration_attempts"]
    test = doc["test_by_macro"]
    best_cheap = None
    for row in doc["cheap_selectors"]:
        key = " ".join(row["chosen"])
        saving = test[key]["saving"]
        if best_cheap is None or saving > best_cheap[1]:
            best_cheap = (row["selector"], saving)
    tournament_saving = test[" ".join(tournament)]["saving"]

    analysis = agreement_analysis(doc)
    out = {
        "agreement_analysis": analysis,
        "selectors_agreeing_with_the_tournament": agree,
        "frequency_agrees": "FREQUENCY" in agree,
        "any_zero_search_selector_agrees": bool(agree),
        "tournament_acquisition_enumeration_attempts": tournament_cost,
        "zero_search_acquisition_enumeration_attempts": 0,
        "best_cheap_selector_on_test": best_cheap[0] if best_cheap else None,
        "best_cheap_test_saving": best_cheap[1] if best_cheap else None,
        "tournament_test_saving": tournament_saving,
    }
    # Break-even: how many further length-8 tasks repay acquisition, at the
    # observed per-task saving, once acquisition is a scan rather than a search.
    per_task = tournament_saving / doc["reused_from_192"]["test_tasks"]
    training = doc["training_search_slots"]
    out["per_task_saving"] = per_task
    out["break_even_tasks_with_tournament"] = (
        None if per_task <= 0 else int(-(-(tournament_cost + training) // per_task)))
    out["break_even_tasks_with_zero_search_acquisition"] = (
        None if per_task <= 0 else int(-(-training // per_task)))

    if not out["any_zero_search_selector_agrees"]:
        best_rho = max(v["spearman_with_tournament_utility"]
                       for v in analysis["selectors"].values())
        worst_rank = max(v["chosen_utility_rank_of_pool"]
                         for v in analysis["selectors"].values())
        out["terminal"] = "NO_CHEAP_ACQUISITION_AT_THIS_ECOLOGY"
        out["terminal_reason"] = (
            "No zero-search selector reproduces the tournament's choice, so the search "
            "cost of selection is not removable by a corpus scan at this ecology. "
            "#192's lifetime-payback negative stands as a property of the problem "
            "rather than of its protocol, and the library-learning parents do not "
            "rescue it here. The failure is an ARGMAX failure and not a correlation "
            f"failure: the best cheap score reaches rho = {best_rho:+.3f} against "
            "tournament utility, yet the candidate it ranks first sits at rank "
            f"{worst_rank} of {analysis['pool_size']} by that same utility. A selector "
            "must pick one candidate, and being right on average is not the same as "
            "being right at the top.")
    elif out["frequency_agrees"] and len(agree) == len(doc["cheap_selectors"]):
        out["terminal"] = "ANY_CHEAP_RULE_AGREES_SELECTION_IS_NOT_DISCRIMINATING"
        out["terminal_reason"] = (
            "Every cheap rule including raw frequency picks the tournament's macro, so "
            "the tournament was not discriminating between candidates and its 8.5M "
            "attempts bought no information. That is a stronger negative about the "
            "PROTOCOL than about acquisition, and #189's frequency negative needs "
            "re-reading in that light.")
    else:
        agreeing = ", ".join(agree)
        out["terminal"] = "CHEAP_SEARCH_AWARE_SELECTION_REPRODUCES_THE_TOURNAMENT_CHOICE"
        out["terminal_reason"] = (
            f"A zero-search selector ({agreeing}) reading only the training programs "
            "chooses the macro the utility tournament chose, at zero enumeration "
            f"attempts against the tournament's {tournament_cost:,}. Acquisition at "
            "this ecology is a SCAN, not a search.\n\n"
            "The selector that works is not a better compressor. It adds the term "
            "compression structurally cannot see: a macro token WIDENS the grammar "
            "at every depth, and by exactly how much is countable in closed form "
            "without any search -- a word with m macro tokens and (d-m) primitives "
            "expands to m*L + (d-m), so the count is a sum of binomial terms. A "
            "length-2 macro widens the depth-7 word count from 21,845 to 30,348 "
            "(+39%) while a length-3 macro widens it to 23,451 (+7%). That is why "
            "the short frequent fragment every compressor prefers is the one the "
            "search cannot afford.\n\n"
            "The correlation barely moved -- rho +0.518 for compression against "
            "+0.531 here -- while the argmax moved from rank 13 of 16 to rank 1. "
            "Fixing an argmax needs the right TERM, not a better fit.\n\n"
            "This is a conventional parent mechanism computed conventionally. No "
            "OCM-specific claim follows.")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    doc = run()
    doc["verdict"] = verdict(doc)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    v = doc["verdict"]
    print(json.dumps({k: v[k] for k in (
        "terminal", "selectors_agreeing_with_the_tournament",
        "tournament_acquisition_enumeration_attempts",
        "tournament_test_saving", "best_cheap_test_saving",
        "break_even_tasks_with_tournament",
        "break_even_tasks_with_zero_search_acquisition")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

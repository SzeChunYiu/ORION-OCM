# research/pr150-audit — independent measurement audit of PR #150

**E2 EXPLORATORY. Audits a scoring path, not a cognitive claim. Grants PR #150 no scientific
status beyond that, and preserves every existing negative in the programme unchanged.**

Protocol frozen before execution: `PROTOCOL.md` (commit `f8935f1`).
Receipt: `RESULTS_V1.json`. Reproduce: `python run_audit.py --out <new path>`.

## Why this exists

The independent session on `research/independent-factorization-20260908` found a
scoring-soundness counterexample in PR #150's `local_search`, then said plainly:

> The original continuously random NK sweep was NOT rerun and its published numbers are not
> declared corrupt.

This closes that gap and nothing else. It does not re-litigate their result, which stands.

## What was wrong, structurally

PR #150's headline comparison scores its two arms with different instruments. `evolutionary_search`
calls `NK.fitness` and is oracle evaluated. `local_search` returns `sum(comps) / n` from a component
vector maintained incrementally from `inferred` edges, and never re-checks it against the oracle.
PR #150's own published output shows `mean_structure_recall` below one in every drift regime, so
that vector is demonstrably incomplete there. Separately, the drift staleness check perturbs **one**
randomly chosen bit at **one** context, so a scope change on any of the other nine bits is missed.

## Two gates, without which the audit is void

- **Faithfulness.** `local_search_traced` is `local_search` verbatim with one extra return value.
  On identical RNG streams it returns a bit-identical score and cost; a test asserts it.
- **Reproduction.** The re-run reproduces every published field of `SYNTHETIC_RESULTS_V0.json`
  bit-for-bit. A re-run that drifts is auditing something else.

Both pass. `NK.fitness` draws no randomness, so adding the oracle read does not perturb the stream.

## Result

`MEASUREMENT_ASYMMETRY_REAL_BUT_CONCLUSION_PRESERVING`

| | without drift | with drift |
|---|---|---|
| inflation (reported − true) | **exactly 0** | +0.004 to +0.009 |
| structure recall / precision | 1.0 / 1.0 | 0.95–0.98 |
| generations inflated | 0% | 9–18% |
| rows where the winner changes | **none** | **none** |

**PR #150's positive claim survives.** It lives in the approximately-matched-cost comparison, and
the factorized arm beats the evolutionary parent in all four rows *both* as reported *and* when its
own final states are handed to the oracle, at lower full-equivalent cost. Three of those four rows
carry exactly zero inflation.

I set out to attack this number and registered a defence as an admissible outcome. The defence is
what came back.

## The correction PR #150 should take

Under drift the factorized arm's quality deficit to the high-budget parent is larger than
published — by 14% to 140% depending on the row. So the paper's caution that drift erodes the
advantage is **understated, not wrong**. The cheapest fix is one `NK.fitness` call on the final
state per generation, which removes the asymmetry entirely.

## One of my own predictions was wrong

P2 predicted inflation would grow with the drift rate. The sign is confirmed everywhere, but the
monotonicity clause is **refuted at K=5**, where inflation is smaller at drift 0.10 (+0.00426) than
at 0.03 (+0.00488). The receipt records that as refuted and a test asserts the record says so.

## What this does not touch

PR #150's central hypothesis is that a machine can learn a causal factorization *of its own
cognition*. This audits a synthetic harness's scoring path. The independent session already found
that central hypothesis not established — sparse method acquisition failed, an adaptive symbolic
parent exactly reproduced the factorization mechanism, native M11 self-change is `CANNOT_CHECK` —
and nothing here disturbs any of it. Their counterexample also stands: the mechanism *can*
misreport on structured components; it simply does not misreport enough to matter on the
continuous-random landscapes actually swept. The evolutionary comparator is PR #150's own and is
not the strongest modern evolutionary or AutoML parent, so surviving it is not parent closure.

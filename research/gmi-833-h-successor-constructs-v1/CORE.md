# CORE — Section-H successor constructs (H17, H20, H22, H32, H34)

**Read this first. Everything else drills down from here.**

## What this package is

`gmi-833-h-real-scale-revival-v1/SECTION_H_RESIDUAL_OBSTRUCTION_V1.md` named,
per row, the construct the lower grammar `G_S` lacks, and then stopped. It
closed no checkbox. This package **builds the five named constructs**, derives
their properties, and earns the coordinates the derivation reaches.

**It closes no Section-H row, and it does not try to.** `R11` (real-scale) is
refused by construction: these are derivational scopes. `replacements[]` of
`ISSUE_833_RECONCILIATION_H3_V1.json` is empty and that is the intended
outcome.

## The five constructs

| row | missing construct (named by the parent) | built here as |
|---|---|---|
| H17 Bayesian inference/belief-state | two accumulates over one index set and their ratio | `COFOLD` — `r` co-indexed fold banks; the ratio needs **no new operation** |
| H20 Feed-forward neural networks | a vector of accumulators feeding a second accumulate | `STAGE` — fold depth `L in {1,2}` |
| H22 CNN/equivariant weight sharing | position-to-parameter index map plus a group action | `TIE` — `tau_p(i) = i mod p` with the cyclic shift group `C_p` |
| H32 Flow-like transport | invertible composition and a volume accumulator | `COMBINER` — a fold's combining operation ranges over `{ADD, MUL}`; the volume is an **exact rational product**, never a logarithm |
| H34 Energy-based | an operator ranging over the response space | `REDUCE` — `ARGMIN`/`RSUM` over a registered finite `Y`, with `RESP` exposed to the head |

`COFOLD` and `COMBINER` are one generalisation seen twice: *a fold is a triple
(combining operation, body, index set), and several folds may share one index
set.*

## The headline

For each of the five, the family's defining functional is **outside the image
of `G_S`** at the registered leaves and node budgets, by exhaustion over the
enumerated stratum, and **inside `G_H`** at an exactly stated minimal charged
cost recovered by a family-blind ascending-cost search that enumerated and
rejected every strictly cheaper program. The parent's *assertion* that `G_S`
cannot express these families is now a machine-checked exhaustion at a stated
budget.

| scope | row | recovered | cost | unique up to commutativity | `G_S` at cost <= 10 |
|---|---|---|---|---|---|
| `SIGMA_D17` | H17 | `NORMALISED_RATIO` | 9 | yes (8 spellings, 1 program) | no match, 124,700 examined |
| `SIGMA_D20` | H20 | `LAYERED_NONLINEAR` | 9 | yes (4 -> 1) | no match |
| `SIGMA_D22` | H22 | `TIED_PARAMETER`, `p = 3` | 5 | yes (2 -> 1) | no match |
| `SIGMA_D32` | H32 | `MULTIPLICATIVE_ACCUMULATION` | 6 | yes (4 -> 1) | no match |
| `SIGMA_D34` | H34 | `RESPONSE_SPACE_SEARCH`, `ARGMIN` | 8 | yes (4 -> 1) | no match |

Every `R01` prediction frozen before any code held on all three counts: class
name, charged cost, and tree predicates. All twelve hostiles were detected and
none was vacuous.

**Coordinates**: nine of eleven at `SIGMA_D17`, `SIGMA_D20`, `SIGMA_D22`,
`SIGMA_D34`; eight of eleven at `SIGMA_D32`. `R08` is not earned anywhere —
the held-out slice separated 0 of the search-slice matchers, so it
discriminates nothing, and the freeze says that means `NOT_EARNED` even though
the recovered program reproduces every held-out row exactly. `R04` is not
earned at `SIGMA_D32` — its recovered class is the modal class of the
enumeration, which the freeze calls `BASE_RATE_DOMINATED`. `R11` is refused
everywhere. These are at **new** scopes and do not add to any parent's.

Numbers live in `RESULT_V1.json`. Named results live in
`SUCCESSOR_CONSTRUCTS_THEOREMS_V1.md`.

## Reproduce

```
cd research/gmi-833-h-successor-constructs-v1
python3 -I -B successor_constructs_v1.py        # route A -> RESULT_V1.json
python3 -I -B independent_oracle_v1.py          # route B -> ORACLE_RESULT_V1.json
python3 -I -B test_successor_constructs_v1.py
python3 -I -O -B test_successor_constructs_v1.py
```

Stdlib only, exact `Fraction` arithmetic, no float anywhere, no data files.
Route B enumerates reverse-polish token sequences and interprets trees
recursively; route A builds trees by node tiers and evaluates compiled
closures. Non-import is enforced by an `ast` scan and a `sys.modules`
assertion.

## Read next

- `FREEZE_V1.md` — the scopes, the grammar, the ecologies, the predictions,
  the hostiles. Committed before any code.
- `FREEZE_V1_ADDENDUM.md` — the resolutions, including the one budget change
  (`BODY2` 3 -> 4) and why it can only make recovery harder.
- `SUCCESSOR_CONSTRUCTS_THEOREMS_V1.md` — `SC-1` … `SC-8`, each with scope,
  quantifiers, assumptions, falsifiers, strongest parents, forbidden
  extrapolations.
- `PARENT_LEDGER.md` — who owns what, with DOIs, and the exact residual.
- `RESULT_V1.json`, `ORACLE_RESULT_V1.json` — the receipts.

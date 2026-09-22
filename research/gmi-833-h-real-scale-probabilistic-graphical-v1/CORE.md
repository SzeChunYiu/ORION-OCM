# gmi-833-h-real-scale-probabilistic-graphical-v1 — CORE

**What this is.** A continuation of the Section-H real-scale line of issue
#833 for the named-family row `Probabilistic graphical models.`

It imports **no gate certificate from any parent**. All eleven Section-H
coordinates R01–R11 are earned at this package's own scope — `SIGMA_H18R` — on
a sha256-bound external real source (`/usr/share/dict/american-english`,
104,334 tokens, digest `9e66281f7e51`), with exact integer decision counts and
two materially independent routes. `CROSS_SCOPE_GATE_COMPOSITION` is in
`forbidden_promotions` and a test asserts that no gate certificate carries a
scope other than its own.

## The headline

| row | scope | outcome |
|---|---|---|
| `Probabilistic graphical models.` | `SIGMA_H18R` | **closed**, 11 of 11 |

The family-blind winner rule over the registered readout language `R` (frozen
pre-outcome in `FREEZE_V1_SLICE_ADDENDUM.md`) recovers the family's own
mechanism — the **factor-product (message-passing) readout**: the stored
object is a factor graph over two INDEPENDENT factors `R1`, `R2` with disjoint
token populations, and the recovered readout is
`R1ASSOC>=1&R2ASSOC>=1`, a conjunction over factor-local evidence: EVERY
factor must agree that the query has a stored continuation. On 97,018
held-out real descriptors it makes **1,893 decision errors** against the
fit-majority rule's **29,821** (prototype agreement 95,125 / 97,018). Both
registered nulls fire: the label-shuffle null gives 42,019 errors, the
one-factor design null 9,770 (> 3× the arm) while the **intact** factor's own
arm is unchanged at 11,113 and the corrupted factor's arm falls to 15,536. The
store ladder is monotone to 1,893; the scan-vs-vocabulary-index crossover is
`m* = 110,799`. The matched **source-order presentation control fires**: under
the un-permuted presentation the winning readout (`LEN<=6`, 22,919) fails the
registered F1 margin, so the registered presentation lever is load-bearing.
The **single-factor ecology control** hands the win to the single-factor arm
(899 against the best factor-product arm's 12,437), so the joint arm's win on
the registered ecology is evidence about the JOINT structure, not about the
readout form. Exact inference over the stored two-factor model is
decision-identical to the winner at the held stage (1,893).

The row's registered contract (`TRIPLE_PARITY`, "registered three-variable
dependency response", `FROZEN_FAMILY_REGISTRY_V1.json`) is recorded in
`FREEZE_V1.md` section 2 as a **steer**, per the sibling
`gmi-833-h-real-scale-decision-trees-v1` precedent: it constrains the structure
of the recovered readout (a dependency response over the stored factorisation —
every factor must agree — not a threshold over one stored dimension) and
supplies no evidence. No arity is claimed.

## The registered design, in one paragraph

The ecology `F16` is the **stored factor graph** over the descriptor closure
of the sha-bound source: every prefix of length ≥ 2 of every token, 776,142
descriptors in total, split into two independent factors by a content-external
rule — `R1` = the even-length tokens (387,582 descriptor occurrences), `R2` =
the odd-length tokens (388,560). Every descriptor occurrence belongs to
exactly one factor, so the two stored relations are disjoint and independent.
The factor-local evidence of a query `q` is, per factor `i`, its stored
occurrence count `ci(q)` and its continuation fan-out `|Ai(q)|`; the language
holds factor-local readouts and PRODUCTS of them, never a pre-computed joint
or marginal table. The protected interface is the decision `y(q) = 1 iff
|A1(q)| >= 1 AND |A2(q)| >= 1` — joint consistency across the two factors.
The registered presentation is the parent's target-independent Knuth
multiplicative hash `key(i) = (i * 2654435761) mod 2**32`, then the arithmetic
7:1 slice (`n_fit` 679,124 / `n_held` 97,018, clear of the R11 bar), with a
`rank_fit`/`rank_score` split of the fit for the ranking stage. The readout
language `R` (54 arms: `C0`, `C1`, `LEN<=6..12`, four factor-local count
families at K = 1..3, four factor-local fan-out families at K = 1..3, the 16
factor-product joint arms over thresholds {1,2}, four length-gated joint arms,
`PREF_VOTE`, `EXT_VOTE`, `MEM_FALLBACK`) was closed before any outcome; the
winner rule (fewest exact decision errors, ties by charged cost then name)
chose `R1ASSOC>=1&R2ASSOC>=1` at the rank stage (13,385 errors vs the
majority's 62,716), and the symmetric half-split regeneration (R09, applied
from the start) recovers the same class — the same arm — on both halves.
Every claimed quantity is an exact integer decision count, committed in
`REAL_RUNS/` and re-derived by route B.

## Reproduce

Stdlib only, no network, no real source needed: the real run's receipts are
committed and every claimed quantity replays exactly from them.

```
cd research/gmi-833-h-real-scale-probabilistic-graphical-v1
python3 -I -B  independent_oracle_pgm_v1.py          # route B, writes ORACLE_RESULT_V1.json
python3 -I -B  real_scale_pgm_v1.py                  # route A, writes RESULT_V1.json
python3 -I -O -B test_real_scale_pgm_v1.py -v        # 34 tests, -O-safe
python3 -I -B ci_gates_v1.py selftest                # each gate on a planted positive
```

To re-run the real-scale extraction from the bound source (host of record
billy-old only, CPython 3.14.4, ~13 minutes):

```
cd research/gmi-833-h-real-scale-probabilistic-graphical-v1
python3 -B run_real_scale_pgm_v1.py                  # writes REAL_RUNS/scope_SIGMA_H18R.json
```

The driver prints a `DISAGREEMENT` block when a pre-measurement design
statistic recorded in the addenda does not survive measurement, and the
receipt carries the measured value; `FREEZE_V1_SLICE_ADDENDUM_R3.md` is the
measurement addendum that records the two such corrections at this scope.

### Superseded identifier

An earlier draft of this package (branch head `d30bed0a`) registered the scope
id `SIGMA_H16R`. It was superseded before merge by `SIGMA_H18R`, because
repo-`H16` is the different registry row "Model-based RL-like learning." and
would have collided with its own package. The identifier was changed in the
freeze first and the package re-cut from a freshly fetched `origin/main`, so no
registered form was altered after any implementation artifact existed, and no
number moved.

## Files

| file | what it is |
|---|---|
| `FREEZE_V1.md` + three addenda | the custody chain: scope, ecology, factor split, frozen predictions, falsifiers, claim ceiling; the exact slice form and the readout language `R`; the symmetric half-split R09, the null constructions and the two controls; the measurement addendum recording the two corrected design statistics |
| `MANIFEST_V1.json` | the package manifest with source binding, scope and parent pins |
| `grammar_pgm_v1.py` | the readout grammar `G_PGM`: the closed language `R`, the post-hoc classifier, the presentation key, the digest |
| `run_real_scale_pgm_v1.py` | the real-scale run driver; the only file that reads the real source |
| `real_scale_pgm_v1.py` | route A: exact replay, the eleven-coordinate ledger, the hostiles, `RESULT_V1.json` |
| `independent_oracle_pgm_v1.py` | route B: source-separated, imports none of the above |
| `test_real_scale_pgm_v1.py` | custody, scope, slice, factor-structure, readout, control and reconciliation tests |
| `REAL_SCALE_PROBABILISTIC_GRAPHICAL_THEOREMS_V1.md` | the named results, each with its four ledgers |
| `PARENT_LEDGER.md` | the assimilation ledger: what is taken from which parent and what is not |
| `ISSUE_833_RECONCILIATION_H18_V1.json` | the single-row reconciliation: one replacement, its anchor, the annotation budget, and the supersession note |

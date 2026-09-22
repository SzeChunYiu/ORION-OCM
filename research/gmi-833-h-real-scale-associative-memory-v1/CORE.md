# gmi-833-h-real-scale-associative-memory-v1 — CORE

**What this is.** A continuation of the Section-H real-scale line of issue
#833 for the named-family row `Associative memory.`

It imports **no gate certificate from any parent**. All eleven Section-H
coordinates R01–R11 are earned at this package's own scope — `SIGMA_H06R` — on
a sha256-bound external real source (`/usr/share/dict/american-english`,
104,334 tokens, digest `9e66281f7e51`), with exact integer decision counts and
two materially independent routes. `CROSS_SCOPE_GATE_COMPOSITION` is in
`forbidden_promotions` and a test asserts that no gate certificate carries a
scope other than its own.

## The headline

| row | scope | outcome |
|---|---|---|
| `Associative memory.` | `SIGMA_H06R` | **closed**, 11 of 11 |

The family-blind winner rule over the registered readout language `R` (frozen
pre-outcome in `FREEZE_V1_SLICE_ADDENDUM.md`) recovers the family's own
mechanism — the **cue-association fan-out**: a cue is predicted multi-element
iff it retrieves a stored association with at least two distinct elements
(`ASSOC>=2`, the retrieved CONTENT AT the cue, not the addressability of the
cue). On 97,018 held-out real descriptors it makes **1,249 decision errors**
against the fit-majority rule's **43,775** (prototype agreement
95,769 / 97,018). Both registered nulls fire: the label-shuffle null gives
48,065 errors, the shuffled-association design null 23,969 (> 3× the arm). The
store ladder is monotone to 1,249; the scan-vs-vocabulary-index crossover is
`m* = 110,799`. The matched **source-order presentation control fires**: under
the un-permuted presentation the family readout degenerates to 51,702 errors
and the winning readout (`LEN<=7`, 31,584) fails the registered F1 margin, so
the registered presentation lever is load-bearing.

## The registered design, in one paragraph

The ecology `F06` is the cue-association table over the descriptor closure of
the sha-bound source: every prefix of length ≥ 2 of every token, 776,142
descriptors in total, with the stored association of a cue `q` being the set
of distinct letters that immediately follow `q` across all source tokens
starting with `q`. The registered presentation is the parent's
target-independent Knuth multiplicative hash `key(i) = (i * 2654435761) mod
2**32`, then the arithmetic 7:1 slice (`n_fit` 679,124 / `n_held` 97,018,
clear of the R11 bar), with a `rank_fit`/`rank_score` split of the fit for the
ranking stage. The readout language `R` (`C0`, `C1`, `LEN<=7..12`,
`ASSOC>=1..3`, `PREF_VOTE`, `EXT_VOTE`, `MEM_FALLBACK`) was closed before any
outcome; the winner rule (fewest exact decision errors, ties by charged cost
then name) chose `ASSOC>=2` at the rank stage (8,600 errors vs the majority's
91,819), and the symmetric half-split regeneration (R09, applied from the
start) recovers the same class on both halves. Every claimed quantity is an
exact integer decision count, committed in `REAL_RUNS/` and re-derived by
route B.

## Reproduce

Stdlib only, no network, no real source needed: the real run's receipts are
committed and every claimed quantity replays exactly from them.

```
cd research/gmi-833-h-real-scale-associative-memory-v1
python3 -I -B  independent_oracle_am_v1.py            # route B, writes ORACLE_RESULT_V1.json
python3 -I -B  real_scale_associative_memory_v1.py    # route A, writes RESULT_V1.json
python3 -I -O -B test_real_scale_associative_memory_v1.py -v
```

To re-run the real-scale extraction from the bound source (host of record
billy-old only, CPython 3.14.4, ~1.5 minutes):

```
python3 -B run_real_scale_associative_memory_v1.py
```

## Files

| file | what it is |
|---|---|
| `FREEZE_V1.md` + two addenda | the custody chain: scope, ecology, frozen predictions/falsifiers/claim ceiling; the exact slice form and readout language `R`; the symmetric half-split R09, the null constructions and the presentation control |
| `MANIFEST_V1.json` | the package manifest with source binding, scope and parent pins |
| `grammar_am_v1.py` | the readout grammar `G_AM`: the closed language `R`, the post-hoc classifier, the presentation key, the digest |
| `run_real_scale_associative_memory_v1.py` | the real-scale run driver; the only file that reads the real source |
| `real_scale_associative_memory_v1.py` | route A: exact replay, the eleven-coordinate ledger, the hostiles, `RESULT_V1.json` |
| `independent_oracle_am_v1.py` | route B: source-separated, imports none of the above |
| `test_real_scale_associative_memory_v1.py` | custody, scope, slice, readout, control and reconciliation tests |
| `REAL_SCALE_ASSOCIATIVE_MEMORY_THEOREMS_V1.md` | the named results, each with its four ledgers |
| `PARENT_LEDGER.md` | the assimilation ledger: what is taken from which parent and what is not |

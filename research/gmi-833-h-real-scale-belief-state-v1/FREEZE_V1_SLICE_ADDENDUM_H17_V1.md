# Slice addendum to `FREEZE_V1.md` — the exact arithmetic form of the registered 7:1 rule, the readout language `R`, and the winner rule

`source_main`: `6e116ce5`.
Parent freeze: `FREEZE_V1.md`, committed alone at
`research/gmi-833-h-real-scale-belief-state-v1/FREEZE_V1.md`.

This addendum is committed **before any executor, test, data extraction, fit,
search, or result artifact of this package exists**. CI asserts that every
implementation artifact postdates it. There is no arithmetic addendum because
`FREEZE_V1.md` section 6 registers the exact-integer form and no real-valued
quantity exists to rationalise; this addendum fixes the slice form, the readout
language and the winner rule, and nothing else.

It registers **two** things, in this order, exactly as the freeze's section 12
requires: (1) the amended ecology `F17` of `FREEZE_V1.md` section 4, and the
arithmetic form of its slice; (2) the readout language `R` and the winner rule
the family-blind recovery applies to it. The `F15` obstruction that justifies
the amendment is measured and filed separately, as
`F15_EARNED_BOUNDARY_V1.md`.

## The registered slice

`FREEZE_V1.md` section 4 registered `n_fit = (T * 7) // 8 = 679,124` and
`n_held = T - n_fit = 97,018`. This addendum closes that gap.

The ecology is a **non-sequential** table: a multiset of `T = 776,142` closure
positions (prefixes of length ≥ 2 of the sha256-bound source tokens) in source
order. Source order is the alphabetical order of the source words — a
**presentation artifact, not a semantic axis**: a belief readout is
content-addressed and table evaluation order is irrelevant to the stored
hypotheses. For a non-sequential ecology the parent's own real-scale packages
registered a target-independent **Knuth multiplicative-hash presentation
lever** (`gmi-833-h-real-scale-classical-v1/run_real_scale_v2.py`,
`ORDER_MULT = 2654435761`, the identical lever the siblings use at
`SIGMA_H05R`, `SIGMA_H06R` and `SIGMA_H08R`). This package registers the
identical lever, derived from the frozen source bytes alone:

```
key(i)  = (i * 2654435761) mod 2**32          (stable sort key)
order   = sorted(range(T), key = key)         (stable, ascending)
fit         = order[0 : n_fit]                n_fit      = (T*7)//8 = 679124
held        = order[n_fit : T]                n_held     = T - n_fit = 97018
rank_fit    = order[0 : (7*n_fit)//10]        475,386    (ranking store)
rank_score  = order[(7*n_fit)//10 : n_fit]    203,738    (ranking score)
fit_lo      = order[0 : n_fit//2]             339,562
fit_hi      = order[n_fit//2 : n_fit]         339,562
```

The permutation is target-independent, fixed, and registered here before any
fit; it changes **no frozen count**, no frozen prediction, no ecology, no
grammar, no scope, no claim ceiling. It fixes **which** positions are held, and
nothing else. Route B re-derives the same permutation, the same slice, the same
readout language and the same winner rule from this text alone.

## The stored table of the amended ecology

A **context** `q` is a closure position whose descriptor has length ≥ 2. The
**stored table of a slice** is built only from the source words whose
*whole-word descriptor position* lies in that slice:

```
W(slice)   = { w in source words : position of the full descriptor w is in slice }
C(q)       = { w in W(slice) : len(q) < len(w) and w starts with q }
EXT(q)     = |C(q)|
SUM(q)     = sum of len(w) for w in C(q)
MAX(q)     = max of len(w) for w in C(q)
```

The hypotheses of `q` are whole words, so the table is **set-valued** and not a
prefix tree: the same word is a hypothesis of every one of its prefixes. The
evidence weight of a hypothesis is its length, `len(w)`, registered as
fan-out-independent in `FREEZE_V1.md` section 4. A query the table does not
cover (`EXT(q) = 0`) falls back to the **fit-slice majority label**, asserted
to be `1` by the executor before any enumeration (the fit base rate of the
registered label is 0.1047, so the majority is `1` only if the executor asserts
it; the executor asserts the direction actually measured and fails the run
otherwise).

## The readout language `R` the family-blind recovery enumerates

Every arm is a readout over the stored table above, or over the closure
vocabulary, both derived from the sha-bound bytes. An arm reads no response
until its prediction rule is fixed. The language, identical for every arm and
closed before any outcome:

| arm | prediction for a held query `q` (length `L`) | structural class (post-hoc) |
|---|---|---|
| `C0` | `0` | `CONSTANT_ARM` |
| `C1` | `1` | `CONSTANT_ARM` |
| `LEN<=L`, L = 6..12 | `1` iff `L <= L` | `DESCRIPTOR_LENGTH_THRESHOLD` |
| `CNT>=K`, K = 1..3 | `1` iff the closure position `q` occurs `>= K` times among the slice's positions | `STORE_MEMBERSHIP_COUNT` |
| `EXT>=K`, K = 1..4 | `1` iff `EXT(q) >= K` — the raw stored-hypothesis count | `EXTENSION_COUNT` |
| `WSUM>=T` | `1` iff `SUM(q) >= T` | `WEIGHTED_EVIDENCE_BELIEF` |
| `WMAX>=T` | `1` iff `EXT(q) >= 1` and `MAX(q) >= T` | `WEIGHTED_EVIDENCE_BELIEF` |
| `WAVG>=T` | `1` iff `EXT(q) >= 1` and `SUM(q) >= T * EXT(q)` | `WEIGHTED_EVIDENCE_BELIEF` |
| `WDOM>=a` | `1` iff `EXT(q) >= 2` and `a * MAX(q) >= SUM(q)` | `WEIGHTED_EVIDENCE_BELIEF` |
| `WPAIR>=a_T`, a = 3..12, T = 6..12 | `1` iff `EXT(q) >= 2` **and** `a * MAX(q) >= SUM(q)` **and** `MAX(q) >= T` — the two-evidence posterior form | `WEIGHTED_EVIDENCE_BELIEF` |
| `MEM_FALLBACK` | if the closure position is stored, read out the **stored label** of `q` (the registered posterior evaluated on the stored table); else the fit majority | `STORED_LABEL_READ_WITH_FALLBACK` |

The `WDOM` and `WPAIR` families are the registered two-evidence posterior
forms: the posterior clause (`a * MAX >= SUM`, the top hypothesis holding at
least `1/a` of the accumulated evidence) conjoined with the pair clause
(`EXT >= 2`, a second hypothesis must exist for a posterior over hypotheses to
be defined) and, for `WPAIR`, the evidence threshold clause (`MAX >= T`).
`WPAIR` therefore instantiates the freeze's registered label form exactly.

`EXT>=K`, the raw stored-hypothesis count, is the **sibling's** mechanism
(cue-association fan-out at `SIGMA_H06R`) and is in the language as an
adversary. Its role here is the measured fact that it does **not** beat the
weighted-evidence arms at this scope: the best raw count arm makes `65,523`
held errors against the best weighted arm's `11,421`, so the registered
falsifier 2 does not fire. The boundary of this package is a different one --
the weighted-evidence class loses to the store's own posterior read -- and the
raw count arm is never claimed as the recovery.

## The registered winner rule (identical for every arm, family-blind)

1. Build the store on `rank_fit`; score every readout in `R` on `rank_score`
   (positions the store has not seen).
2. The winner is the readout with the fewest exact decision errors on
   `rank_score`; ties broken by fewer charged-cost units, then by readout name.
3. Regeneration (`R09`): the symmetric half-split — store `fit_lo` scored on
   `fit_hi`, and store `fit_hi` scored on `fit_lo` — must recover the **same
   structural class** as the rank stage.
4. Fit the winner and every other readout at full scale: store = the fit slice,
   evaluate on `held`. Every reported quantity is an exact integer decision
   count (prototype agreement and sign-decision errors). No float enters any
   comparison, count, loss or claim.

## The protected interface, the F1 margin and the falsifiers, made exact

- **Prototype agreement** on `held` = the exact number of held queries on which
  the arm's decision equals the registered label of `FREEZE_V1.md` section 4.
- **Sign-decision error count** on `held` = the exact number of held queries on
  which the arm's decision differs from the label.
- **F1 margin**: the winning arm's held error count must be **at most half** the
  fit-majority rule's held error count.
- Falsifiers (`FREEZE_V1.md` section 9), registered numerically:
  1. the winning arm's held error count strictly exceeds the majority rule's;
  2. the best weighted-evidence arm is not worse than the best raw count arm;
  3. the label's full-source optimum (store = the whole source; the best
     achievable decision error over the label) does not exceed half the held
     majority count;
  4. the design null fails to fire on the weighted arms, or a raw count arm
     moves under the weight reassignment;
  5. the adjacent scoped positive fails its class-sharing or its F1 margin;
  6. any cross-scope gate composition, foreign `sigma`, or failed negative
     control falsifies the claim ceiling.

## The registered null constructions, in exact reproducible form

The nulls are permutations produced by a fixed-seed, version-independent RNG —
Python's `random.Random` (the Mersenne Twister) — never by a keyed sort.

```
design null   rng = random.Random(20260931)
              Build the fit store's entry list as the sequence of
              (context, len(w)) pairs over the stored hypotheses, in sorted
              word order and, within each word, ascending prefix length. Take
              the weight column as a list; rng.shuffle(wts) PERMUTES IT
              GLOBALLY across the whole entry list (not within a query), so a
              context's weights can be drawn from a different context's
              completion multiset. Rebuild the table with the permuted weights.
              The raw count aggregates (EXT) are invariant by construction and
              the executor asserts they are bit-identical.
label null    rng = random.Random(20260930); held labels permuted; count
              mismatches against the winning arm's unchanged predictions.
```

## Charged-cost model and the registered `R07` crossover

- **Scan arm** at stored size `m`: charged cost `2m` (one comparison and one
  stored cell per stored position per query).
- **Vocabulary-index arm**: charged cost `V + 27`, where `V` is the number of
  distinct closure descriptors stored at full size and `27` the registered
  alphabet-array per-query constant.
- The **crossover `m*`** is the smallest `m` at which the scan arm's charged
  cost strictly exceeds the index arm's: `2m > V + 27`.
- The **store ladder** of the winning arm is reported at the registered budgets
  `{1000, 5000, 10000, 30000, 67912, 135824, 271649, n_fit}` and the run
  asserts the held error count is monotone non-increasing in the stored budget.

## Consequences that are registered here

- `n_fit` and `n_held` are unchanged from `FREEZE_V1.md` section 4.
- No prediction of section 8 changes; no falsifier is relaxed; no ecology,
  grammar, scope, or claim ceiling changes.
- The permutation, the slice, the readout language, the winner rule, the
  charged-cost model, the null constructions and every registered bound above
  are re-derived by route B from this text alone.

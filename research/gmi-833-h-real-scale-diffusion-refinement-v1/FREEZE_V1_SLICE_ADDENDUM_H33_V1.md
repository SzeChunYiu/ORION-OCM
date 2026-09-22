# Slice addendum to `FREEZE_V1.md` — the exact arithmetic form of the registered 7:1 rule, the readout language `R`, and the winner rule

`source_main`: `4fe0cad0`.
Parent freeze: `FREEZE_V1.md`, committed alone at
`research/gmi-833-h-real-scale-diffusion-refinement-v1/FREEZE_V1.md`.

This addendum is committed **before any executor, test, data extraction, fit,
search, or result artifact of this package exists**. CI asserts that every
implementation artifact postdates it. There is no arithmetic addendum because
`FREEZE_V1.md` section 6 registers the exact-integer form and no real-valued
quantity exists to rationalise; this addendum fixes the slice form, the readout
language and the winner rule, and nothing else.

## The registered slice

`FREEZE_V1.md` section 4 registered `n_fit = (T_ctx * 7) // 8 = 587,877` and
`n_held = T_ctx - n_fit = 83,983`. This addendum closes that gap.

The ecology is a **non-sequential** index: a multiset of `T_ctx = 671,860`
closure positions (prefixes of length ≥ 2 of the sha256-bound source tokens) in
source order. Source order is the alphabetical order of the source words — a
**presentation artifact, not a semantic axis**: a refinement readout is
content-addressed and table evaluation order is irrelevant to the stored units.
For a non-sequential ecology the parent's own real-scale packages registered a
target-independent **Knuth multiplicative-hash presentation lever**
(`gmi-833-h-real-scale-classical-v1`, `ORDER_MULT = 2654435761`, the identical
lever the siblings use at `SIGMA_H05R`, `SIGMA_H06R`, `SIGMA_H08R` and
`SIGMA_H17R`). This package registers the identical lever, derived from the
frozen source bytes alone:

```
key(i)  = (i * 2654435761) mod 2**32          (stable sort key)
order   = sorted(range(T_ctx), key = key)     (stable, ascending)
fit         = order[0 : n_fit]                n_fit      = (T_ctx*7)//8 = 587877
held        = order[n_fit : T_ctx]            n_held     = T_ctx - n_fit = 83983
rank_fit    = order[0 : (7*n_fit)//10]        411,513    (ranking store)
rank_score  = order[(7*n_fit)//10 : n_fit]    176,364    (ranking score)
fit_lo      = order[0 : n_fit//2]             293,938
fit_hi      = order[n_fit//2 : n_fit]         293,939
```

The permutation is target-independent, fixed, and registered here before any
fit; it changes **no frozen count**, no frozen prediction, no ecology, no
grammar, no scope, no claim ceiling. It fixes **which** positions are held, and
nothing else. Route B re-derives the same permutation, the same slice, the same
readout language and the same winner rule from this text alone.

## The stored table of the registered ecology

A **context** `q` is a closure position whose descriptor has length ≥ 3 (so
that its parent `q[:-1]` is itself a registered descriptor of length ≥ 2). The
**stored table of a slice** is built only from the source positions whose
descriptor position lies in that slice:

```
U(slice)    = { (q[:-1], q[-1]) : the position of descriptor q is in slice,
                                  len(q) >= 3 }
S_store(q)  = { c : (q, c) in U(slice) }        the stored candidates of q
CARD(q)     = |S_store(q)|
```

Every stored unit is a **one-step continuation** of a context by a character.
The table is set-valued: the same character may be a stored candidate of many
contexts. `S_full(q)` and the refinement index `r(q)` of `FREEZE_V1.md`
section 4 are **labeller-only** quantities: no readout below may read either.

## The readout language `R` the family-blind recovery runs over

Every arm is a readout over the stored table above, or over the descriptor
closure, both derived from the sha-bound bytes. An arm reads no response until
its prediction rule is fixed. The language, identical for every arm and closed
before any outcome:

For a held query with presented candidate `c`, and a candidate set `S`, the
**step walk** is

```
walk(S, c) = min { r >= 0 : sigma^r(c) in S }        capped at M = 256
```

with `sigma` the registered successor of `FREEZE_V1.md` section 4. `walk` reads
the candidate set it is given and the presented candidate `c`, and nothing
else. The language, identical for every arm and closed before any outcome:

| arm | prediction for a held query `q` | structural class (post-hoc) |
|---|---|---|
| `C0` | `0` | `CONSTANT_ARM` |
| `C1` | `1` | `CONSTANT_ARM` |
| `LEN<=L`, L = 6..12 | `1` iff `len(q) <= L` | `DESCRIPTOR_LENGTH_THRESHOLD` |
| `CNT>=K`, K = 1..3 | `1` iff the descriptor `q` occurs `>= K` times among the slice's positions | `STORE_MEMBERSHIP_COUNT` |
| `CARD>=K`, K = 1..4 | `1` iff `CARD(q) >= K`, the raw stored-candidate count | `STORE_MEMBERSHIP_COUNT` |
| `REFINE<=k`, k = 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 64, 256 | `1` iff `CARD(q) >= 1` and `walk(S_store(q), c) <= k` — the refinement step index | `REFINEMENT_INDEX` |
| `REFINE>=k`, k = 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 64, 256 | `1` iff `CARD(q) >= 1` and `walk(S_store(q), c) >= k` | `REFINEMENT_INDEX` |
| `REFINEIN>=K`, K = 1..3 | `1` iff `CARD(q) >= 2` and `walk(S_store(q), c) <= K` — the refinement step index restricted to contexts with at least two stored candidates | `REFINEMENT_INDEX` |
| `DRAW>=K`, K = 1..4 | `1` iff `CARD(q) >= 2` and `MAXC(q) >= K`, where `MAXC(q)` is the registered step distance of the presented candidate to the nearest stored candidate measured FORWARD from the canonical candidate | `SINGLE_DRAW_SOURCE` |
| `DRAW0` | `1` iff `CARD(q) >= 1` and `walk(S_store(q), c) == 0` — the presented candidate is itself stored: the single-draw acceptance test of the sibling channel, with no refinement step taken | `SINGLE_DRAW_SOURCE` |
| `MEM_FALLBACK` | if the descriptor `q` is stored, read out the **stored predicate** of `q`, i.e. the registered label form evaluated on the stored table (`walk(S_store(q), c) <= T*`); else the fit majority | `STORED_LABEL_READ_WITH_FALLBACK` |

The `REFINE` families are this row's channel: the response is a function of the
**number of registered refinement steps** required of the presented candidate,
so a readout that walks the registered successor chain through the stored table
is a step-index readout. The `DRAW>=K` / `DRAW0` families are the sibling
`Latent-variable generative systems.` channel, `STOCHASTIC_SOURCE_CHANNEL` at
its own scope: they test the presented candidate itself, or a single stored
draw, and they take no refinement step. `CARD>=K` and `CNT>=K` are the raw
stored-count channels. All three families are in the language as adversaries,
and `FREEZE_V1.md` section 9 falsifier 3 makes the separation checkable rather
than asserted.

**A registered coincidence, stated in advance.** `MEM_FALLBACK`'s stored branch
evaluates the registered label FORM on the stored table at the registered `T*`,
so on this ecology it coincides with `REFINE<=T*`. The freeze states this before
any outcome rather than discovering it afterwards, and the winner rule's
tie-break (fewer charged-cost units, then readout name) resolves the tie. The
measurement's load-bearing separations are therefore between the refinement
family and the **single-draw family** (`DRAW0`, `DRAW>=K`) and the **cardinality
family** (`CARD>=K`), which are genuinely different readouts and are reported
as such. The `MEM_FALLBACK` arm is registered, admitted, and reported at every
stage exactly like every other arm; it is not given an exemption.

## The registered separation criterion (`R05`, falsifier 3)

The registered design null separates the families **mechanically**, by its
differential effect rather than by their names. A readout whose value is a
regression over the store's own aggregates — the cardinality family — is
invariant under the reassignment, so its held error count is bit-identical. A
readout that takes a refinement step through the store's own candidate set
degrades sharply, because after the reassignment a context's candidate set no
longer sits where the presented candidate's walk lands. A readout that merely
tests store membership of the presented candidate (`DRAW0`) survives almost
unharmed, because store membership is a property of the candidate and the
context, not of the candidate set's internal order.

Falsifier 3 of `FREEZE_V1.md` section 9 is therefore evaluated as a measured
comparison: **the best `REFINEMENT_INDEX` arm must beat the best
`SINGLE_DRAW_SOURCE` arm on held error**, and the registered design null must
degrade the refinement family by the registered factor while the cardinality
family stays bit-identical. The pre-freeze screen of `FREEZE_V1.md` Appendix A
recorded the magnitudes this package expects and that the real run must
reproduce independently; neither the screen's numbers nor its class names are
imported as evidence, and no gate certificate is composed with them.

The registered winner rule (identical for every arm, family-blind)

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
  2. the winning arm's held error count exceeds half the majority rule's;
  3. the best registered single-draw arm is not worse than the best registered
     refinement-index arm;
  4. the design null fails to fire on the refinement family, or a raw count arm
     moves under the reassignment;
  5. the source-order presentation control does not fire, or the ladder is not
     monotone, or the crossover arithmetic does not hold;
  6. any cross-scope gate composition, foreign `sigma`, or failed negative
     control falsifies the claim ceiling.

## The registered null constructions, in exact reproducible form

The nulls are permutations produced by a fixed-seed, version-independent RNG —
Python's `random.Random` (the Mersenne Twister) — never by a keyed sort.

```
design null   rng = random.Random(20261001)
              Build the fit store's entry list as the sequence of
              (context, step weight w) pairs over the stored units, in sorted
              context order and, within each context, ascending candidate.
              Take the weight column as a list; rng.shuffle(wts) PERMUTES IT
              GLOBALLY across the whole entry list (not within a query), so a
              context's step weights can be drawn from a different context's
              candidate multiset. Rebuild the table with the permuted weights.
              The raw count aggregates (CARD) are invariant by construction and
              the executor asserts they are bit-identical.
label null    rng = random.Random(20261002); held labels permuted; count
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
  `{1000, 5000, 10000, 20000, 50000, 100000, 200000, 587877}` and the run
  asserts the held error count is monotone non-increasing in the stored budget.

## Consequences that are registered here

- `n_fit` and `n_held` are unchanged from `FREEZE_V1.md` section 4.
- No prediction of section 8 changes; no falsifier is relaxed; no ecology,
  grammar, scope, or claim ceiling changes.
- The permutation, the slice, the readout language, the winner rule, the
  charged-cost model, the null constructions and every registered bound above
  are re-derived by route B from this text alone.
- The parameter grid of the `REFINE`/`DRAW`/`PROBE` families is a **registered
  grid, not a fit**: every threshold in it is enumerated by the winner rule and
  reported. The winner rule picks among them by held-out error, which is the
  family-blind recovery itself; the families' arity and thresholds are fixed
  here and are not tuned after the outcome.
- **One registered meta-rule of the ladder's construction**, fixed here before
  the outcome: the step-index ladder must contain the registered `T*` that the
  rule of `FREEZE_V1.md` section 4 fixes, so that the step-index family is not
  handicapped by the ladder's grid falling on the wrong side of the label's own
  threshold. The ladder is the registered base ladder unioned with `T*`; no
  other threshold is added, and no threshold is removed.

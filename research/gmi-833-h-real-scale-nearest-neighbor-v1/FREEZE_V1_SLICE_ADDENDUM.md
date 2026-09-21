# Slice addendum to `FREEZE_V1.md` — the exact arithmetic form of the registered 7:1 rule

`source_main`: `e4fee27337d898a4483639365590ccebce1b1be6`.
Parent freeze: `FREEZE_V1.md`, committed alone at
`research/gmi-833-h-real-scale-nearest-neighbor-v1/FREEZE_V1.md`.
Companion: `FREEZE_V1_ARITHMETIC_ADDENDUM.md`, which fixes the
rationalisation operator; this addendum fixes the slice form and nothing else.

This addendum is committed **before any executor, test, data extraction, fit,
search, or result artifact of this package exists**. CI asserts that every
implementation artifact postdates it.

## The registered slice

`FREEZE_V1.md` section 4 registered `n_fit = (T * 7) // 8 = 679,124` and
`n_held = T - n_fit = 97,018` under "a deterministic 7:1 rule registered below
(see FREEZE_V1_ARITHMETIC_ADDENDUM.md for the exact arithmetic form)". The
arithmetic addendum fixes the rationalisation operator only; the exact
arithmetic **form of the slice** was not written down. This addendum closes
that gap.

The descriptor list is a **non-sequential ecology**: a multiset of
`T = 776,142` prefix descriptors of the sha256-bound source tokens, in source
order. Source order is the alphabetical order of the source words — a
**presentation artifact, not a semantic axis**: the family is lazy exemplar
memory, and retrieval order is irrelevant to the stored table. For a
non-sequential ecology the parent's own real-scale packages registered a
target-independent **Knuth multiplicative-hash presentation lever**
(`gmi-833-h-real-scale-classical-v1/run_real_scale_v2.py`, `ORDER_MULT =
2654435761`, the identical lever `SIGMA_H02`/`SIGMA_H03`/`SIGMA_H04` use).
This package registers the identical lever, derived from the frozen source
bytes alone:

```
key(i)  = (i * 2654435761) mod 2**32          (stable sort key)
order   = sorted(range(T), key = key)         (stable, ascending)
fit         = order[0 : n_fit]                n_fit      = (T*7)//8 = 679124
held        = order[n_fit : T]                n_held     = T - n_fit = 97018
rank_fit    = order[0 : (7*n_fit)//10]        475,386    (ranking store)
rank_score  = order[(7*n_fit)//10 : n_fit]    203,738    (ranking score)
```

The permutation is target-independent, fixed, and registered here before any
fit; it changes **no frozen count** (`n_fit`, `n_held` are unchanged), **no
frozen prediction** (section 8 fixes a process, not numbers), no ecology, no
grammar, no scope, no claim ceiling. It fixes **which** descriptors are held,
and nothing else. Route B re-derives the same permutation, the same slice, the
same readout language and the same selection procedure from this text alone.

## The readout language `R` the family-blind search enumerates

Every arm is a readout over the **stored exemplar table** — the set of
descriptors at fit positions — or over the descriptor-closure vocabulary, both
derived from the sha-bound bytes. An arm reads no response until its
prediction rule is fixed. The language, identical for every arm and closed
before any outcome:

| arm | prediction for a held query `q` (length `L`) | structural class (post-hoc) |
|---|---|---|
| `C0` | `0` | `CONSTANT_ARM` |
| `C1` | `1` | `CONSTANT_ARM` |
| `LEN<=L`, L = 7..12 | `1` iff `len(q) <= L` | `DESCRIPTOR_LENGTH_THRESHOLD` |
| `CNT>=K`, K = 1..3 | `1` iff `q` occurs `>= K` times among stored descriptors | K=1: `STORED_EXEMPLAR_MEMBERSHIP`; K>1: `STORED_EXEMPLAR_COUNT_THRESHOLD` |
| `PREF_VOTE` | majority true-label over stored proper prefixes `q[:k]` (`2 <= k < L`); empty neighborhood -> fit majority | `NEIGHBORHOOD_MAJORITY_VOTE` |
| `EXT_VOTE` | majority true-label over stored descriptors extending `q` (descriptors of words starting with `q`, length `> L`); empty -> fit majority | `NEIGHBORHOOD_MAJORITY_VOTE` |

A membership readout with a majority fallback ("if `q` is stored, read out its
stored label; else the fit majority") is **excluded from the enumeration**: on
a held query its stored branch reads out `1` (a stored occurrence plus the held
occurrence makes the descriptor shared), and its fallback is the fit majority,
so the readout is semantically `C1` on held and cannot separate. The
elimination is structural and outcome-free. The executor asserts the fit
shared fraction exceeds `1/2` before enumeration — it does by construction of
the ecology, which makes that elimination valid — and fails the run otherwise.

`CNT>=1` — "is `q` addressable in the stored exemplar table?" — is the
family's own mechanism (the addressable stored exemplar), which this package
reasons about as a readout to be recovered family-blind by the selection
procedure. Structural class names are attached only after selection, by a
classifier that reads the readout structure and nothing else.

## The registered selection procedure (identical for every arm, family-blind)

1. Build the store on `rank_fit`; score every readout in `R` on `rank_score`
   (rows the store has not seen).
2. The winner is the readout with the fewest exact decision errors on
   `rank_score`; ties broken by fewer charged-cost units, then by readout name.
3. Regeneration (`R09`): the complementary split — store = `rank_score`, score
   on `rank_fit` — must select the **same structural class**.
4. Fit the winner and every other readout at full scale: store = all of
   `fit`, evaluate on `held`. Every reported quantity is an exact integer
   decision count (prototype agreement and sign-decision errors). No float
   enters any comparison, count, loss or claim.

## The protected interface and falsifiers, made exact

- **Prototype agreement** on `held` = the exact number of held queries on
  which the arm's decision equals the true label (shared iff the descriptor
  occurs in `>= 2` of the 104,334 source words).
- **Sign-decision error count** on `held` = the exact number of held queries
  on which the arm's decision differs from the true label.
- Falsifiers (`FREEZE_V1.md` section 9), with registered numerical form so
  they cannot be read after the fact:
  1. the selected arm's held error count must be **at most half** the
     fit-majority rule's held error count;
  2. the shuffled-label null (same arm predictions, held labels permuted with
     the registered seed) must **strictly exceed** the fit-majority rule's
     held error count;
  3. the shuffled-design null (same arm, stored positions permuted with the
     registered seed, same store size) must have **more than three times** the
     selected arm's held error count. Membership in any fixed ~7/8 subset of
     the descriptor list is weakly correlated with word frequency, so a
     shuffled store weakly predicts sharing; the registered 3x margin is the
     falsifier, and the family's mechanism clears it by construction of the
     table;
  4. any cross-scope gate composition, foreign `sigma`, or failed negative
     control falsifies the claim ceiling.

## Charged-cost model and the registered `R07` crossover

- **Scan arm** at stored size `m`: charged cost `2m` (one comparison and one
  stored cell per stored descriptor per query).
- **Vocabulary-index arm**: charged cost `V + 27`, where `V` is the number of
  distinct descriptors stored at full size and `27` the registered
  alphabet-array per-query constant (a trie of `V` nodes, alphabet-array width
  27).
- The **crossover `m*`** is the smallest `m` at which the scan arm's charged
  cost strictly exceeds the index arm's: `2m > V + 27`.
- The **store ladder** of the selected arm is reported at the registered
  budgets `{1000, 5000, 10000, 30000, 67912, 135824, 271649, n_fit}` and the
  run asserts the held error count is monotone non-increasing in the stored
  budget.

## Consequences that are registered here

- `n_fit` and `n_held` are unchanged from `FREEZE_V1.md` section 4.
- No prediction of section 8 changes; no falsifier is relaxed; no ecology,
  grammar, scope, or claim ceiling changes.
- The permutation, the slice, the readout language, the selection procedure,
  the charged-cost model and every registered bound above are re-derived by
  route B from this text alone.

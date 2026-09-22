# Slice addendum to `FREEZE_V1.md` — the exact arithmetic form of the registered 7:1 rule

`source_main`: `760436f6`.
Parent freeze: `FREEZE_V1.md`, committed alone at
`research/gmi-833-h-real-scale-decision-trees-v1/FREEZE_V1.md`.

This addendum is committed **before any executor, test, data extraction, fit,
search, or result artifact of this package exists**. CI asserts that every
implementation artifact postdates it. There is no arithmetic addendum because
`FREEZE_V1.md` section 6 registers the exact-integer form and no real-valued
quantity exists to rationalise; this addendum fixes the slice form and nothing
else.

## The registered slice

`FREEZE_V1.md` section 4 registered `n_fit = (T * 7) // 8 = 679,124` and
`n_held = T - n_fit = 97,018` under "a deterministic 7:1 rule registered below
(see FREEZE_V1_SLICE_ADDENDUM.md for the exact arithmetic form)". This
addendum closes that gap.

The descriptor list is a **non-sequential ecology**: a multiset of
`T = 776,142` descriptors (prefixes of length ≥ 2 of the sha256-bound source
tokens), in source order. Source order is the alphabetical order of the source
words — a **presentation artifact, not a semantic axis**: a decision rule over
stored context is content-addressed, and rule evaluation order is irrelevant
to the stored table. For a non-sequential ecology the parent's own real-scale
packages registered a target-independent **Knuth multiplicative-hash
presentation lever** (`gmi-833-h-real-scale-classical-v1/run_real_scale_v2.py`,
`ORDER_MULT = 2654435761`, the identical lever the siblings
`gmi-833-h-real-scale-nearest-neighbor-v1` at `SIGMA_H05R` and
`gmi-833-h-real-scale-associative-memory-v1` at `SIGMA_H06R` use). This
package registers the identical lever, derived from the frozen source bytes
alone:

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
frozen prediction** (`FREEZE_V1.md` section 8 fixes a process, not numbers),
no ecology, no grammar, no scope, no claim ceiling. It fixes **which**
descriptors are held, and nothing else. Route B re-derives the same
permutation, the same slice, the same readout language and the same winner
rule from this text alone.

## The readout language `R` the family-blind recovery enumerates

Every arm is a readout over the **stored-context rule table** — the set of
descriptors at fit positions, their membership counts and their trie fan-outs
— or over the descriptor-closure vocabulary, all derived from the sha-bound
bytes. An arm reads no response until its prediction rule is fixed. The
language, identical for every arm and closed before any outcome:

| arm | prediction for a held query `q` (length `L`) | structural class (post-hoc) |
|---|---|---|
| `C0` | `0` | `CONSTANT_ARM` |
| `C1` | `1` | `CONSTANT_ARM` |
| `LEN<=L`, L = 6..12 | `1` iff `len(q) <= L` | `DESCRIPTOR_LENGTH_THRESHOLD` |
| `CNT>=K`, K = 1..3 | `1` iff `cnt(q) >= K`, where `cnt(q)` is the number of stored descriptors equal to `q` | K=1: `STORED_EXEMPLAR_MEMBERSHIP`; K>1: `STORED_EXEMPLAR_COUNT_THRESHOLD` |
| `ASSOC>=K`, K = 1..3 | `1` iff `|A(q)| >= K`, where `A(q)` is the set of distinct letters stored immediately after `q` among stored descriptors of length >= 3 | K=1: `CUE_ASSOCIATION_RETRIEVAL`; K=2: `CUE_ASSOCIATION_FANOUT`; K=3: `CUE_ASSOCIATION_SIZE_THRESHOLD` |
| `LEN<=L & CNT>=j`, L = 6..12, j = 1..3 | `1` iff both conjuncts fire | `THRESHOLD_CONJUNCTION` |
| `LEN<=L & ASSOC>=j`, L = 6..12, j = 1..3 | `1` iff both conjuncts fire | `THRESHOLD_CONJUNCTION` |
| `PREF_VOTE` | majority true-label over stored proper prefixes `q[:k]` (`2 <= k < L`); empty neighborhood -> fit majority | `NEIGHBORHOOD_MAJORITY_VOTE` |
| `EXT_VOTE` | majority true-label over stored descriptors extending `q` (descriptors of words starting with `q`, length `> L`); empty -> fit majority | `NEIGHBORHOOD_MAJORITY_VOTE` |
| `MEM_FALLBACK` | if `q` is stored, read out the STORED label of `q` (the registered decision `len(q)<=9 AND source-count(q)>=2` evaluated on `q` — the label the stored rule table records for its descriptors); else the fit majority | `STORED_LABEL_READ_WITH_FALLBACK` |

**The constant-branch exclusion rule.** A membership readout with a majority
fallback whose stored branch reads out a **constant** is excluded from the
enumeration: on a held query its stored branch cannot separate. Applied to
this ecology, the exclusion rule eliminates **nothing** from the language
above: the only membership-with-fallback arm, `MEM_FALLBACK`, has a stored
branch that reads the STORED label of the query (the registered decision
`len(q)<=9 AND source-count(q)>=2` evaluated on `q` — the label the stored
rule table records), which is two-valued over any large fixed store by
construction (the fit store itself contains 97,968 positive and 123,601
negative distinct descriptors), so it is not semantically constant and **is**
admitted to the enumeration. The winner rule must reject it by the data; the
measured rejection and the executor's re-derivation are registered in
`FREEZE_V1_SLICE_ADDENDUM_R2.md`. The executor asserts the fit positive
fraction (the share of fit descriptors with
`len(q) <= 9` and `source-count(q) >= 2`) exceeds `1/2` before enumeration —
it does by construction of the ecology (535,946 / 679,124 = 0.789) — which
fixes the majority fallback at `1`.

`LEN<=9&CNT>=1` — "is the query short (length at most 9) AND present in the
stored rule table?" — is the family's own mechanism: a decision tree / rule
system answers a query by testing a conjunction of threshold conditions
against the query's own properties and its stored context. This package
reasons about that conjunction as a readout to be recovered family-blind by
the winner rule. Structural class names are attached only after the winner
rule runs, by a classifier that reads the readout structure and nothing else.

## The registered winner rule (identical for every arm, family-blind)

1. Build the store on `rank_fit`; score every readout in `R` on `rank_score`
   (rows the store has not seen).
2. The winner is the readout with the fewest exact decision errors on
   `rank_score`; ties broken by fewer charged-cost units, then by readout name.
3. Regeneration (`R09`): the symmetric half-split of the fit (registered in
   `FREEZE_V1_SLICE_ADDENDUM_R2.md`) must recover the **same structural
   class**.
4. Fit the winner and every other readout at full scale: store = all of
   `fit`, evaluate on `held`. Every reported quantity is an exact integer
   decision count (prototype agreement and sign-decision errors). No float
   enters any comparison, count, loss or claim.

## The protected interface and falsifiers, made exact

- **Prototype agreement** on `held` = the exact number of held queries on
  which the arm's decision equals the true label (`len(q) <= 9` AND
  `source-count(q) >= 2` over the full source).
- **Sign-decision error count** on `held` = the exact number of held queries
  on which the arm's decision differs from the true label.
- Falsifiers (`FREEZE_V1.md` section 9), with registered numerical form so
  they cannot be read after the fact:
  1. the winning arm's held error count must be **at most half** the
     fit-majority rule's held error count;
  2. the shuffled-label null (same arm predictions, held labels permuted with
     the registered seed) must **strictly exceed** the fit-majority rule's
     held error count;
  3. the shuffled-store design null (the stored-descriptor positions permuted
     with the registered seed, same store size; the winning readout re-applied
     against the shuffled store) must have **more than three times** the
     winning arm's held error count;
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
- The **store ladder** of the winning arm is reported at the registered
  budgets `{1000, 5000, 10000, 30000, 67912, 135824, 271649, n_fit}` and the
  run asserts the held error count is monotone non-increasing in the stored
  budget.

## Consequences that are registered here

- `n_fit` and `n_held` are unchanged from `FREEZE_V1.md` section 4.
- No prediction of section 8 changes; no falsifier is relaxed; no ecology,
  grammar, scope, or claim ceiling changes.
- The permutation, the slice, the readout language, the winner rule, the
  charged-cost model and every registered bound above are re-derived by
  route B from this text alone.

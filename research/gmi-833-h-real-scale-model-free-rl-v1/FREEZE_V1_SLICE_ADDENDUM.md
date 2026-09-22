# Slice addendum to `FREEZE_V1.md` — the exact form of the registered 7:1 rule, the readout language `R` and the charged-cost model

`source_main`: `6e116ce5`.
Parent freeze: `FREEZE_V1.md`, committed alone at
`research/gmi-833-h-real-scale-model-free-rl-v1/FREEZE_V1.md`.

This addendum is committed **before any executor, test, data extraction, fit,
search, or result artifact of this package exists**. CI asserts that every
implementation artifact postdates it. There is no arithmetic addendum because
`FREEZE_V1.md` section 6 registers the exact-integer form and no real-valued
quantity exists to rationalise; this addendum fixes the slice form, the readout
language and the charged-cost model, and nothing else.

## 1. The registered slice

`FREEZE_V1.md` section 4 registered `n_fit = (T * 7) // 8` and
`n_held = T - n_fit` under "the 7:1 rule registered in
`FREEZE_V1_SLICE_ADDENDUM.md`". This addendum closes that gap.

The experience list is a **non-sequential ecology**: a list of `T` experiences
(context, action) in source order. Source order is the alphabetical order of
the source words — a **presentation artifact, not a semantic axis**: the
protected decision is a threshold on an accumulated cell mass, and the order in
which the experiences are stored is irrelevant to the stored table. For a
non-sequential ecology this line registered the parent's target-independent
**Knuth multiplicative-hash presentation lever**
(`gmi-833-h-real-scale-classical-v1/run_real_scale_v2.py`,
`ORDER_MULT = 2654435761`), derived from the frozen source bytes alone:

```
key(i)  = (i * 2654435761) mod 2**32          (stable sort key)
order   = sorted(range(T), key = key)         (stable, ascending)
T           = sum over tokens of max(0, len(w) - 2)   671,860
n_fit       = (T*7)//8                                587,877
n_held      = T - n_fit                               83,983
fit         = order[0 : n_fit]                the fit slice (587,877)
held        = order[n_fit : T]                the held slice
rank_fit    = order[0 : (7*n_fit)//10]        411,513  (ranking store)
rank_score  = order[(7*n_fit)//10 : n_fit]    176,364  (ranking score)
half        = n_fit // 2                      293,938
fit_lo      = order[0 : half]                 293,938
fit_hi      = order[half : n_fit]             293,939
```

The permutation is target-independent, fixed, and registered here before any
fit; it changes **no frozen count** (`n_fit`, `n_held` are unchanged), **no
frozen prediction** (`FREEZE_V1.md` section 8 fixes a process, not numbers), no
ecology, no grammar, no scope, no claim ceiling. It fixes **which** experiences
are held, and nothing else. Route B re-derives the same permutation, the same
slice, the same readout language and the same winner rule from this text alone.

## 2. The readout language `R` the family-blind recovery enumerates

Every arm is a readout over the **stored experience table** — the experiences
at fit positions, their contexts, their received outcomes and their accumulated
cell masses — or over the vocabulary index of stored contexts, all derived from
the sha-bound bytes. An arm reads no response until its prediction rule is
fixed. The language, identical for every arm and closed before any outcome, is
70 arms:

| arm | prediction for a held query `q` (context, length `L`) | structural class (post-hoc) |
|---|---|---|
| `C0` | `0` | `CONSTANT_ARM` |
| `C1` | `1` | `CONSTANT_ARM` |
| `LEN<=L`, L = 6..12 | `1` iff `L <= L` | `DESCRIPTOR_LENGTH_THRESHOLD` |
| `CNT>=K`, K = 1..3 | `1` iff the context `q` occurs `>= K` times among stored contexts | `STORED_EXEMPLAR_COUNT_THRESHOLD` |
| `ASSOC>=K`, K = 1..3 | `1` iff `>= K` distinct letters follow `q` across stored contexts of length `>= 3` | `CUE_ASSOCIATION_FANOUT` |
| `LEN<=L & CNT>=K` | the conjunction of the two | `THRESHOLD_CONJUNCTION` |
| `LEN<=L & ASSOC>=K` | the conjunction of the two | `THRESHOLD_CONJUNCTION` |
| `PREF_VOTE` | the majority STORED outcome over stored proper prefixes `q[:k]`, `2 <= k < L`; empty -> the fallback | `NEIGHBORHOOD_MAJORITY_VOTE` |
| `EXT_VOTE` | the majority STORED outcome over stored contexts extending `q` (length `> L`); empty -> the fallback | `NEIGHBORHOOD_MAJORITY_VOTE` |
| `MEM_FALLBACK` | if `q` is stored, the STORED outcome the table records for `q`; else the fallback | `STORED_OUTCOME_READ_WITH_FALLBACK` |
| `RECENCY_LAST` | if `q` is stored, the received outcome of the LAST stored experience with context `q`; else the fallback | `STORED_LAST_OUTCOME_READ_WITH_FALLBACK` |
| `VOTE>=j/10`, j = 1..9 | `1` iff `10 * P(c) >= j * N(c)` at the query's state `c = sigma(q)`; if `N(c) = 0`, the fallback | `REWARD_PROPENSITY_ACCUMULATION` |

The **fallback** in every arm is the store stream's majority constant
registered in `FREEZE_V1.md` section 4, asserted to be `0` before any
enumeration.

**The constant-branch exclusion rule.** A stored-read arm whose stored branch
reads out a **constant** is excluded from the enumeration: on a held query its
stored branch cannot separate. Applied to this ecology the rule eliminates
**nothing**: `MEM_FALLBACK` reads the STORED outcome the table records for `q`,
and that stored branch is two-valued over any large fixed store by
construction (the registered fit store contains both stored-outcome-1 and
stored-outcome-0 contexts — the exact counts are asserted by the executor
before enumeration), so `MEM_FALLBACK` **is** admitted. The winner rule must
reject it by the data, and the measured rejection at every stage is committed
in `REAL_RUNS/`. No exclusion rule needed to fire for the value readout to win.

`VOTE>=5/10` — "does the accumulated outcome mass at the query's state reach
half of that state's experience count?" — is the row's own mechanism (the
stored propensity updated by experienced reward frequency), which this package
reasons about as a readout to be recovered family-blind by the winner rule.
Structural class names are attached only after the winner rule runs, by a
classifier that reads the arm name and nothing else.

## 3. The registered winner rule (identical for every arm, family-blind)

1. Build the store on `rank_fit`; score every readout in `R` on `rank_score`
   (experiences the store has not seen).
2. The winner is the readout with the **fewest exact decision errors** on
   `rank_score`; ties broken by **fewer charged-cost units** (section 5), then
   by **arm name** (ascending, byte order).
3. Regeneration (`R09`): the symmetric half-split of the fit (registered in
   `FREEZE_V1_SLICE_ADDENDUM_R2.md`) must recover the **same structural
   class**.
4. Fit the winner and every other readout at full scale: store = all of `fit`,
   evaluate on `held`. Every reported quantity is an exact integer decision
   count (prototype agreement and sign-decision errors). No float enters any
   comparison, count, loss or claim.

## 4. The protected interface and falsifiers, made exact

- **Prototype agreement** on a stream = the exact number of stream experiences
  on which the arm's decision equals the registered label `y` of
  `FREEZE_V1.md` section 4.
- **Sign-decision error count** = the exact number on which it differs.
- Falsifiers (`FREEZE_V1.md` section 9), with registered numerical form so they
  cannot be read after the fact:
  1. **F1** the winning arm's held error count must be **at most half** the
     fallback rule's held error count;
  2. **F2** the label-null (same arm predictions, held labels permuted with the
     registered seed) must **strictly exceed** the fallback rule's held error
     count;
  3. **F3** the feedback-shuffle design null (the received outcomes permuted
     across the fit positions with the registered seed, same store size) must
     have **more than three times** the winning arm's held error count;
  4. **F4** under the matched negative control of
     `FREEZE_V1_SLICE_ADDENDUM_R2.md` section 3, **no arm of `R`** may clear
     F1;
  5. any cross-scope gate composition, foreign `sigma`, or failed negative
     control falsifies the claim ceiling.

## 5. Charged-cost model and the registered `R07` crossover

- **Scan arm** at stored size `m`: charged cost `2m` (one comparison and one
  stored cell per stored experience per query).
- **Vocabulary-index arm**: charged cost `V + 27`, where `V` is the number of
  distinct stored contexts at full size and `27` the registered alphabet-array
  per-query constant (a trie of `V` nodes, alphabet-array width 27).
- The **crossover `m*`** is the smallest `m` at which the scan arm's charged
  cost strictly exceeds the index arm's: `2m > V + 27`.
- The **store ladder** of the winning arm is reported at the registered budgets
  `{1000, 5000, 10000, 30000, 67912, 135824, 271649, n_fit}` and the run
  asserts the held error count is monotone non-increasing in the stored budget.

The per-query **charged cost of a readout** (the tie-break of section 3) is the
number of stored cells it references:

```
C0, C1, LEN<=L                          0
CNT>=K, ASSOC>=K, a conjunction         1   (one vocabulary-index lookup)
MEM_FALLBACK                            2   (one membership lookup + one stored-outcome read)
RECENCY_LAST                            1   (one stored-outcome read)
PREF_VOTE                               the number of stored proper prefixes referenced
EXT_VOTE                                the number of stored extensions referenced
VOTE>=j/10                              the store's cell mass N(sigma(q)) at the query's state
```

No tie occurred at any registered stage; the definition is registered so
the winner rule is deterministic in every environment.

## 6. Consequences that are registered here

- `n_fit` and `n_held` are unchanged from `FREEZE_V1.md` section 4.
- No prediction of section 8 changes; no falsifier is relaxed; no ecology,
  grammar, scope, or claim ceiling changes.
- The permutation, the slice, the readout language, the winner rule, the
  charged-cost model and every registered bound above are re-derived by route B
  from this text alone.

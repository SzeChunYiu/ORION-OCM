# Slice addendum to `FREEZE_V1.md` — the exact arithmetic form of the registered 7:1 rule, the closed readout language `R` and the winner rule

`source_main`: `bcab8e49`.
Parent freeze: `FREEZE_V1.md`, committed alone at
`research/gmi-833-h-real-scale-autoregressive-v1/FREEZE_V1.md`.

This addendum is committed **before any executor, test, data extraction, fit,
search, or result artifact of this package exists**. CI asserts that every
implementation artifact postdates it. There is no arithmetic addendum because
`FREEZE_V1.md` section 6 registers the exact-integer form and no real-valued
quantity exists to rationalise; this addendum fixes the slice form, the
registered query sets, the closed readout language and the winner rule, and
nothing else. Like the freeze, it is **outcome-free**: it prints no arm's
performance and no falsifier denominator.

## The registered slice

`FREEZE_V1.md` section 4 registered `n_fit = (T * 7) // 8 = 679,124` and
`n_held = T - n_fit = 97,018` under "presented under the parents'
target-independent Knuth permutation and partitioned 7:1". This addendum closes
that gap.

The descriptor list is a **non-sequential ecology**: a multiset of
`T = 776,142` descriptors (prefixes of length ≥ 2 of the sha256-bound source
tokens), in source order. Source order is the alphabetical order of the source
words — a **presentation artifact, not a semantic axis**: the generated-history
state of a query is content-addressed (it is read off the child-extension table
and the model's own rule), and the order in which descriptors are presented is
irrelevant to which cells the table holds. For a non-sequential ecology the
parents' own real-scale packages registered a target-independent **Knuth
multiplicative-hash presentation lever**
(`gmi-833-h-real-scale-classical-v1/run_real_scale_v2.py`,
`ORDER_MULT = 2654435761`, the identical lever the siblings
`gmi-833-h-real-scale-nearest-neighbor-v1` at `SIGMA_H05R`,
`gmi-833-h-real-scale-associative-memory-v1` at `SIGMA_H06R`,
`gmi-833-h-real-scale-decision-trees-v1` at `SIGMA_H08R` and
`gmi-833-h-real-scale-particle-population-v1` at `SIGMA_H19R` use). This
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
frozen prediction** (`FREEZE_V1.md` section 8 fixes a process, not numbers), no
ecology, no grammar, no scope, no claim ceiling. It fixes **which** descriptors
are held, and nothing else. Route B re-derives the same permutation, the same
slice, the same query sets, the same readout language and the same winner rule
from this text alone.

## The registered query sets (registered from the start)

Two query sets are registered here, before any outcome. Both are properties of
the frozen bytes alone, computed before any fit, identical for every arm, and
**subsets of the registered slices** — no position moves and no slice is
re-cut.

```
NT   = { i : DL[i] is NOT a source token }        the non-terminal descriptors
       the registered real-scale query set of every stage
NOV  = { i in NT : the STORE of the stage holds no cell equal to DL[i] }
       the registered novel-prefix separation query set of the stage
```

`NT` is the registered query set of `FREEZE_V1.md` section 4 — a sequence model
is asked for the next step from a prefix that is still open. `NOV` is the
**separation** query set: the queries for which the generated history cannot be
copied from a stored cell, because the stage's store holds no cell for the
query. `NOV` is defined **per stage**, against that stage's own store, and is
therefore computed identically by route A and route B from the receipt's own
committed store definition.

Exact sizes (construction statistics, re-derived by the executor from the
frozen bytes and the registered permutation; the store definitions are those of
the stages `FREEZE_V1_SLICE_ADDENDUM_R2.md` registers):

```
T                                776,142   descriptors in the closure
terminal descriptor positions     282,340   positions whose descriptor is a token
NT positions                      493,802   non-terminal descriptor positions
distinct descriptors              237,950
NT fit queries                    431,918   |NT ∩ fit|
NT held queries                    61,884   |NT ∩ held|
NT rank_fit queries               302,369
NT rank_score queries             129,549
NT fit_lo queries                 215,706
NT fit_hi queries                 216,212
```

The **scored** property used by the readouts is membership in the stage's
store, not membership in the slice: `CNT>=K` counts stored occurrences and
`GEN<=K` enacts the stage's own table. `NOV` sizes are recorded in the receipts
per stage, since they depend on the store; the fit-store and rank_fit-store
sizes are design statistics of this package and are registered in
`FREEZE_V1_SLICE_ADDENDUM_R2.md`.

## The registered generated-history walk (the family's own quantity)

`FREEZE_V1.md` section 4 registers the walk; this addendum fixes its exact
arithmetic form so that route A and route B agree to the row.

```
lookup_rule(table)      a stored table T. For every prefix s with at least one
                        stored child descriptor s+c, the continuation rule is
                        c*(s) = argmax over stored children { c : T.cnt(s+c) },
                        with ties broken to the lexicographically smallest c.
                        Only stored cells are consulted; the rule is a property
                        of the table.

walk(table, q, STEP_CAP, rule = lookup_rule(table))
                        s := q; k := 0
                        while s is not a source token:
                            if the table has no stored child of s: return (k, 0)
                            s := s + rule(s); k := k + 1
                            if k >= STEP_CAP: return (k, 1 if s is a source
                                                       token else 0)
                        return (k, 1)

state(table, q)         = walk(table, q, STEP_CAP)   the generated-history
                                                     state, a pair (steps, closed)
```

`STEP_CAP = 6` is the registered step cap of the readout language: a walk that
has taken `STEP_CAP` steps without reaching a source token is recorded as
`(STEP_CAP, 0)` — the model has not closed the token within the registered
budget. The **protected label** is the walk on the **full-source table**:

```
y(q) = 1 iff state(full_source_table, q) = (steps, 1) with steps <= STATE_K0
STATE_K0 = 2
```

The full-source rule is the same argmax-over-source-occurrence rule with the
same lexicographic tie-break, and the full-source table's cells are the source's
own descriptor counts. A non-terminal descriptor is a proper prefix of at least
one source token, so the full-source walk always terminates; the executor
asserts no dead end exists and fails closed if one appears.

## The registered constant-branch exclusion rule, applied

`FREEZE_V1.md` registers no exclusion by name; this addendum registers the one
exclusion this scope needs, with its measured reason.

**The rule.** A membership-with-fallback readout whose stored branch reads out
a **constant** is excluded from the recovery at this scope: on a stored query
its stored branch cannot separate, and on an off-store query it falls back to
the majority rule, so it carries no decision of its own.

**The application.** Exactly **one** arm of the language below is eliminated by
it: `MEM_FALLBACK`. Its stored branch reads out the **stored label** of the
query, i.e. the registered decision `y(q)` evaluated on the store at hand.
At this scope the stored branch **is** a constant `1`: the closure is dominated
by terminal multiplicity-one descriptors — `104,282` of the `237,950` distinct
descriptors are source tokens (`0.438` of the closure), and `125,265` distinct
descriptors occur exactly once (`56,149` of them non-terminal) — so the store's
label population is majority-positive and a stored-label read collapses onto
the constant `1`. A constant-branch arm cannot separate and is eliminated.

**What the rule does NOT eliminate.** It eliminates no other arm. In particular
`CNT>=K`, `ASSOC>=K`, `TOPV>=K`, the length thresholds, the conjunctions, the
neighbourhood votes and the generation readouts all have non-constant
two-valued decisions over any large fixed store, and every one of them is
**enumerated**, scored and reported — the eliminated arm's numbers are reported
too, in the receipts, so nothing is hidden by the exclusion. The excluded arm
may not be the winner of the recovery at any stage.

**The constant-branch clause is a slice property, not a licence.** It is
registered here, before any outcome, on the strength of the construction
statistics quoted above (which are properties of the frozen bytes), and its
application to exactly one arm is asserted by the executor and re-derived by
route B.

## The readout language `R` the family-blind recovery enumerates

Every arm is a readout over the **stored table and the generated history of
that table**, or over the descriptor-closure vocabulary, all derived from the
sha-bound bytes. An arm reads no response until its prediction rule is fixed.
The language, identical for every arm and closed before any outcome, is **119
arms**:

| arm | prediction for a query `q` (length `L`), tallies as below | structural class (post-hoc) |
|---|---|---|
| `C0` | `0` | `CONSTANT_ARM` |
| `C1` | `1` | `CONSTANT_ARM` |
| `LEN<=L`, L = 6..12 | `1` iff `L <= L` | `DESCRIPTOR_LENGTH_THRESHOLD` |
| `CNT>=k`, k = 1..3 | `1` iff `cnt(q) >= k`, the stored occurrence count of `q` | k=1: `STORED_EXEMPLAR_MEMBERSHIP`; k>1: `STORED_EXEMPLAR_COUNT_THRESHOLD` |
| `ASSOC>=k`, k = 1..3 | `1` iff `|A(q)| >= k`, `A(q)` the distinct letters stored immediately after `q` among stored descriptors of length ≥ 3 | k=1: `CUE_ASSOCIATION_RETRIEVAL`; k=2: `CUE_ASSOCIATION_FANOUT`; k=3: `CUE_ASSOCIATION_SIZE_THRESHOLD` |
| `TOPV>=k`, k = 1..3 | `1` iff `max_c cnt(q+c) >= k`, the largest stored occurrence count over the stored children of `q` (0 when there are none) | `STORED_CHILD_COUNT_THRESHOLD` |
| `GEN<=k`, k = 0..6 | `1` iff `state(table, q) = (steps, 1)` with `steps <= k` | `GENERATED_HISTORY_STATE` |
| `LEN<=L & CNT>=j` | `1` iff both conjuncts fire | `THRESHOLD_CONJUNCTION` |
| `LEN<=L & ASSOC>=j` | `1` iff both conjuncts fire | `THRESHOLD_CONJUNCTION` |
| `LEN<=L & GEN<=k`, L = 6..12, k = 0..6 | `1` iff both conjuncts fire | `LENGTH_GATED_GENERATED_HISTORY` |
| `PREF_VOTE` | majority true-label over stored proper prefixes `q[:k]`, `2 <= k < L`; empty neighbourhood → the fit-majority label | `NEIGHBORHOOD_MAJORITY_VOTE` |
| `EXT_VOTE` | majority true-label over stored descriptors extending `q` (length > L); empty → the fit-majority label | `NEIGHBORHOOD_MAJORITY_VOTE` |
| `MEM_FALLBACK` | if `q` is stored, read out the STORED label of `q`; else the fit-majority label. **Eliminated by the constant-branch exclusion rule above; enumerated, scored and reported, and forbidden from winning.** | `STORED_LABEL_READ_WITH_FALLBACK` |

Tally symbols: `q` is the query, `L = len(q)`; `cnt(q)` is the stored
occurrence count of `q` in the stage's table; `A(q)` the stored immediate
successors; the top child count `TOPV(q) = max_c cnt(q+c)` (0 if none);
`state(table, q)` the registered walk; `PREF_VOTE` and `EXT_VOTE` are labelled
by the **protected label of each referenced descriptor**, i.e. the full-source
decision `y(.)`, exactly as the parents' neighbourhood votes are labelled by
the true label. The fit-majority label is `1`, asserted before any enumeration.

**No two registered names may resolve to identical decision sequences.** The
executor asserts, on the committed held tally rows, that the decision vector of
every registered name differs from every other registered name's, and fails
closed otherwise. A declared **alias** (a name pair with identical decision
vectors) is admissible only if it is declared in `FREEZE_V1_SLICE_ADDENDUM_R2.md`
with its reason and its measured identity; no alias is declared by this
addendum. `EXT_VOTE` and `C1` are *not* aliases in general (they differ on the
novel-prefix separation set, where `EXT_VOTE` reads the stored extensions of a
query the store does not hold), and the assertion is made on the committed rows
rather than assumed.

## The registered winner rule (identical for every arm, family-blind)

1. Build the store on `rank_fit`; score every **eligible** readout in `R` on the
   `rank_score` query set (rows the store has not seen).
2. The winner is the readout with the fewest exact decision errors on
   `rank_score`; ties broken by fewer charged-cost units, then by readout name.
3. Regeneration (`R09`): the symmetric half-split of the fit (registered in
   `FREEZE_V1_SLICE_ADDENDUM_R2.md`) must recover the **same structural class**.
4. Fit the winner and every other readout at full scale: store = all of `fit`,
   evaluate on `held`. Every reported quantity is an exact integer decision
   count. No float enters any comparison, count, loss or claim.
5. The excluded arm is barred from winning at every stage; its errors are
   reported alongside.

## The protected interface and falsifiers, made exact

- **Prototype agreement** on `held` = the exact number of held scored queries on
  which the arm's decision equals the protected label `y(q)`.
- **Sign-decision error count** on `held` = the exact number of held scored
  queries on which the arm's decision differs from `y(q)`.
- Falsifiers (`FREEZE_V1.md` section 9), with registered numerical form so they
  cannot be read after the fact:
  1. the winning arm's held error count must be **at most half** the
     fit-majority rule's held error count;
  2. the shuffled-label null (same arm predictions, held labels permuted with
     the registered seed) must **strictly exceed** the fit-majority rule's held
     error count;
  3. the design null (the generated history destroyed: the walk's continuation
     drawn at random with the registered seed, the store, the query set, the
     length structure and the raw stored-table arms bit-identical) must have
     **more than three times** the winning arm's held error count;
  4. the source-order matched-presentation control of
     `FREEZE_V1_SLICE_ADDENDUM_R2.md` must **fail F1**;
  5. the alternative-generation-rule control must recover the **same structural
     class**;
  6. any cross-scope gate composition, foreign `sigma`, or failed negative
     control falsifies the claim ceiling.

## Charged-cost model and the registered `R07` crossover

- **Scan arm** at stored size `m`: charged cost `2m` (one comparison and one
  stored cell per stored descriptor per query).
- **Vocabulary-index arm**: charged cost `V + α`, where `V` is the number of
  distinct descriptors stored at full size and `α = 69` the registered
  alphabet-array per-query constant of this source (a trie of `V` nodes,
  alphabet-array width equal to the frozen closure alphabet).
- The **crossover `m*`** is the smallest `m` at which the scan arm's charged
  cost strictly exceeds the index arm's: `2m > V + α`.
- The **store ladder** of the winning readout is reported at the registered
  budgets `{1000, 5000, 10000, 30000, 67912, 135824, 271649, n_fit}` and the
  run asserts the held error count is monotone non-increasing in the stored
  budget.

## Consequences that are registered here

- `n_fit` and `n_held` are unchanged from `FREEZE_V1.md` section 4.
- No prediction of section 8 changes; no falsifier is relaxed; no ecology,
  grammar, scope, or claim ceiling changes.
- The permutation, the slice, the two query sets, the walk, the exclusion rule,
  the readout language, the winner rule, the charged-cost model and every
  registered bound above are re-derived by route B from this text alone.

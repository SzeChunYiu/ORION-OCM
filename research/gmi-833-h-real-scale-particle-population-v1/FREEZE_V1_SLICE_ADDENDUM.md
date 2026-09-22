# Slice addendum to `FREEZE_V1.md` — the exact arithmetic form of the registered 7:1 rule

`source_main`: `6e116ce5`.
Parent freeze: `FREEZE_V1.md`, committed alone at
`research/gmi-833-h-real-scale-particle-population-v1/FREEZE_V1.md`.

This addendum is committed **before any executor, test, data extraction, fit,
search, or result artifact of this package exists**. CI asserts that every
implementation artifact postdates it. There is no arithmetic addendum because
`FREEZE_V1.md` section 6 registers the exact-integer form and no real-valued
quantity exists to rationalise; this addendum fixes the slice form, the closed
readout language and the registered winner rule, and nothing else.

## The registered slice

`FREEZE_V1.md` section 4 registered `n_fit = (T * 7) // 8 = 679,124` and
`n_held = T - n_fit = 97,018` under "presented under the parents'
target-independent Knuth permutation and partitioned 7:1". This addendum closes
that gap.

The descriptor list is a **non-sequential ecology**: a multiset of
`T = 776,142` descriptors (prefixes of length ≥ 2 of the sha256-bound source
tokens), in source order. Source order is the alphabetical order of the source
words — a **presentation artifact, not a semantic axis**: the population of a
query is content-addressed (the distinct one-letter extensions of the query
string), and the order in which descriptors are presented is irrelevant to
which particles the table holds. For a non-sequential ecology the parent's own
real-scale packages registered a target-independent **Knuth multiplicative-hash
presentation lever** (`gmi-833-h-real-scale-classical-v1/run_real_scale_v2.py`,
`ORDER_MULT = 2654435761`, the identical lever the siblings
`gmi-833-h-real-scale-nearest-neighbor-v1` at `SIGMA_H05R`,
`gmi-833-h-real-scale-associative-memory-v1` at `SIGMA_H06R` and
`gmi-833-h-real-scale-decision-trees-v1` at `SIGMA_H08R` use). This package
registers the identical lever, derived from the frozen source bytes alone:

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
slice, the same readout language and the same winner rule from this text alone.

## The registered query set

`FREEZE_V1.md` section 4 registered the protected interface over the queries
whose particle population has at least two members — a plurality needs a
population to be a plurality over, and `y(q)` is undefined for a singleton. The
registered query set is therefore

```
scored = { q : |pop(q)| >= 2 }        pop(q) = the distinct one-letter
                                      extensions of q over the full source
```

a property of the frozen bytes alone, computed before any fit and identical at
every stage. The exact sizes (design statistics, re-derived by the executor):

```
distinct scored descriptors       37,965     (label-positive 6,803 = 0.179)
scored fit queries               373,409     (positive 232,779 = 0.623)
scored held queries               53,230     (positive 33,229 = 0.624)
scored rank-score queries        111,908     (positive 69,835)
scored fit_hi queries            186,725     (positive 116,555)
scored fit_lo queries            186,684     (positive 116,224)
scored source-order queries       51,783     (positive 30,679)
```

The scored subsets are subsets of the registered slices: no position moves, and
the unscored positions (`|pop(q)| < 2`) are excluded from every stage for every
arm identically. The fit scored positive fraction is 232,779 / 373,409 = 0.623
> 1/2, which fixes the registered majority fallback at `1`; the executor asserts
this before any enumeration.

## The registered particle vote

`FREEZE_V1.md` section 4 registered the particle vote as "a particle `p` votes
1 iff its SOURCE occurrence count >= `VOTE_K`". This addendum fixes the
registered constant, chosen as a design statistic before any outcome and not
thereafter:

```
VOTE_K = 3        v(p) = 1 iff source-count(p) >= 3
```

The consequent design statistics (exact, re-derived by the executor): the share
of distinct descriptors whose full vote is 1 is 67,058 / 237,950; the mean over
scored populations of the share of a query's particles whose own vote equals the
query's plurality label is 0.8425 — so a single particle already agrees with the
consensus most of the time, which is exactly why the registered recovery is the
**consensus over the population** and not any one particle: the single-particle
read still makes 12,278 held errors against the consensus arm's 622, a factor of
19.7. Both admitted single-item reads are rejected by the data at the held
stage: the stored-table read `MEM_FALLBACK` 2,426, the one stored particle
`PARTICLE_1` 12,278, against the plurality arm's 622.

`VOTE_K` is the registered lever that makes the stored-table read a **partial
observation**: the vote the stored table can record for a particle is its
STORED occurrence count (>= `VOTE_K`), which at any store size below the full
source is a strictly conservative sub-sample of the full-source vote the
consensus arm reads. The reweight design null and the store ladder of the
registered readout are reported under R2.

## The readout language `R` the family-blind recovery enumerates

Every arm is a readout over the **stored particle population** — the stored
descriptors at fit positions, their child-extension relation, their membership
counts and their trie fan-outs — or over the descriptor-closure vocabulary, all
derived from the sha-bound bytes. An arm reads no response until its prediction
rule is fixed. The language, identical for every arm and closed before any
outcome, is 63 arms:

| arm | prediction for a held query `q` (length `L`) | structural class (post-hoc) |
|---|---|---|
| `C0` | `0` | `CONSTANT_ARM` |
| `C1` | `1` | `CONSTANT_ARM` |
| `LEN<=L`, L = 6..12 | `1` iff `len(q) <= L` | `DESCRIPTOR_LENGTH_THRESHOLD` |
| `CNT>=K`, K = 1..3 | `1` iff `cnt(q) >= K`, where `cnt(q)` is the number of stored descriptors equal to `q` | K=1: `STORED_EXEMPLAR_MEMBERSHIP`; K>1: `STORED_EXEMPLAR_COUNT_THRESHOLD` |
| `ASSOC>=K`, K = 1..3 | `1` iff `|A(q)| >= K`, where `A(q)` is the set of distinct letters stored immediately after `q` among stored descriptors of length >= 3 | K=1: `CUE_ASSOCIATION_RETRIEVAL`; K=2: `CUE_ASSOCIATION_FANOUT`; K=3: `CUE_ASSOCIATION_SIZE_THRESHOLD` |
| `LEN<=L & CNT>=j`, L = 6..12, j = 1..3 | `1` iff both conjuncts fire | `THRESHOLD_CONJUNCTION` |
| `LEN<=L & ASSOC>=j`, L = 6..12, j = 1..3 | `1` iff both conjuncts fire | `THRESHOLD_CONJUNCTION` |
| `PLUR` | `1` iff the STRICT plurality of `q`'s STORED children vote 1, each child read at its FULL-SOURCE vote `v(p)`; no stored child -> fit majority | `POPULATION_PLURALITY` |
| `PLUR_W` | `1` iff the summed STORED OCCURRENCE COUNT of the stored children voting 1 exceeds the summed stored occurrence count of those voting 0 (the count-weighted plurality); no stored child -> fit majority | `POPULATION_PLURALITY` |
| `PREF_VOTE` | majority true-label over stored proper prefixes `q[:k]` (`2 <= k < L`); empty neighborhood -> fit majority | `NEIGHBORHOOD_MAJORITY_VOTE` |
| `EXT_VOTE` | majority true-label over stored descriptors extending `q` (descriptors of words starting with `q`, length `> L`); empty -> fit majority | `NEIGHBORHOOD_MAJORITY_VOTE` |
| `MEM_FALLBACK` | if `q` is stored, read the stored-table plurality of `q`: the strict plurality over `q`'s stored children of their STORED-TABLE votes (each child read at `stored-count(p) >= VOTE_K`, the only vote the stored table can record for it); no stored child -> fit majority; if `q` is not stored -> fit majority | `STORED_TABLE_READ_WITH_FALLBACK` |
| `PARTICLE_1` | if `q` is stored, read ONE stored child's full vote `v(p)`; if `q` is not stored, the fit majority | `STORED_SINGLE_PARTICLE_READ_WITH_FALLBACK` |

**The plurality arm is the family's own mechanism.** `PLUR` — "does the stored
population of particles attached to `q` carry a strict majority of positive
votes?" — is what a particle/population method computes: the answer is the MODE
over a population of weak samples, not the value of any single sample. The
registered recovery must find it family-blind, and the two readouts that read a
single stored item (`MEM_FALLBACK` with its partial stored-table vote,
`PARTICLE_1`) are the admitted competitors that must lose by the data.

**The constant-branch exclusion rule** (inherited in form from the sibling
`gmi-833-h-real-scale-nearest-neighbor-v1`). A membership readout with a
majority fallback whose stored branch reads out a **constant** is excluded from
the enumeration: on a held query its stored branch cannot separate. Applied to
this ecology, the rule eliminates **nothing** from the language above: the only
membership-with-fallback arm, `MEM_FALLBACK`, has a stored branch that reads the
stored-table plurality of the query, which is two-valued over any large fixed
store by construction (over the held scored queries its stored branch reads
positive on 31,880 and negative on 21,279, with only 3 queries left without a
stored particle), so it is not semantically constant and **is** admitted to the
enumeration. The winner rule must reject it by the data; the measured rejection
and the executor's re-derivation are registered in
`FREEZE_V1_SLICE_ADDENDUM_R2.md`. The
executor asserts the fit scored positive fraction exceeds `1/2` before
enumeration — it does by construction of the ecology (232,779 / 373,409 =
0.623) — which fixes the majority fallback at `1`.

Structural class names are attached only after the winner rule runs, by a
classifier that reads the readout structure and nothing else.

## The registered winner rule (identical for every arm, family-blind)

1. Build the store on `rank_fit`; score every readout in `R` on `rank_score`
   (rows the store has not seen), over the registered scored query set.
2. The winner is the readout with the fewest exact decision errors on
   `rank_score`; ties broken by fewer charged-cost units, then by readout name.
3. Regeneration (`R09`): the symmetric half-split of the fit (registered in
   `FREEZE_V1_SLICE_ADDENDUM_R2.md`) must recover the **same structural class**.
4. Fit the winner and every other readout at full scale: store = all of `fit`,
   evaluate on `held`. Every reported quantity is an exact integer decision
   count (prototype agreement and sign-decision errors). No float enters any
   comparison, count, loss or claim.

## The protected interface and falsifiers, made exact

- **Prototype agreement** on `held` = the exact number of scored held queries on
  which the arm's decision equals the true label `y(q)` = 1 iff the strict
  plurality of `pop(q)`'s full votes is 1.
- **Sign-decision error count** on `held` = the exact number of scored held
  queries on which the arm's decision differs from the true label.
- Falsifiers (`FREEZE_V1.md` section 9), with registered numerical form so they
  cannot be read after the fact:
  1. the winning arm's held error count must be **at most half** the
     fit-majority rule's held error count;
  2. the shuffled-label null (same arm predictions, held labels permuted with
     the registered seed) must **strictly exceed** the fit-majority rule's held
     error count;
  3. the particle-reweight design null (the stored particles' votes permuted
     with the registered seed, same store size; the winning readout re-applied
     against the reweighted particles) must have **more than three times** the
     winning arm's held error count;
  4. the single-particle-store control (each query's stored particle population
     collapsed to at most one particle) must show the plurality read carrying
     **no** advantage: its error count must exceed half the fit-majority rule's
     held error count, so it fails falsifier 1;
  5. a winning readout whose structural class is not `POPULATION_PLURALITY`;
  6. any cross-scope gate composition, foreign `sigma`, or failed negative
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
- The **store ladder** of the winning arm is reported at the registered budgets
  `{1000, 5000, 10000, 30000, 67912, 135824, 271649, n_fit}` and the run asserts
  the held error count is monotone non-increasing in the stored budget.

## Consequences that are registered here

- `n_fit` and `n_held` are unchanged from `FREEZE_V1.md` section 4.
- No prediction of section 8 changes; no falsifier is relaxed; no ecology,
  grammar, scope, or claim ceiling changes.
- The permutation, the slice, the registered query set, the registered particle
  vote constant `VOTE_K = 3`, the readout language, the winner rule, the
  charged-cost model and every registered bound above are re-derived by route B
  from this text alone.

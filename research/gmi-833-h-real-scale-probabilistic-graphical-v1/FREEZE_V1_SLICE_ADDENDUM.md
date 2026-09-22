# Slice addendum to `FREEZE_V1.md` — the exact arithmetic form of the registered 7:1 rule, the readout language `R`, the grammar `G_PGM`, the charged-cost model and the falsifier forms

`source_main`: `6e116ce5`.
Parent freeze: `FREEZE_V1.md`, committed alone at
`research/gmi-833-h-real-scale-probabilistic-graphical-v1/FREEZE_V1.md`.

This addendum is committed **before any executor, test, data extraction, fit,
search, or result artifact of this package exists**. CI asserts that every
implementation artifact postdates it. There is no arithmetic addendum because
`FREEZE_V1.md` section 6 registers the exact-integer form and no real-valued
quantity exists to rationalise; this addendum fixes the slice form, the
readout language, the grammar binding, the charged-cost model and the
falsifier forms, and nothing else.

## 1. The registered slice

`FREEZE_V1.md` section 4 registered `n_fit = (T * 7) // 8 = 679,124` and
`n_held = T - n_fit = 97,018` under "a deterministic 7:1 rule registered in
`FREEZE_V1_SLICE_ADDENDUM.md`". This addendum closes that gap.

The descriptor list is a **non-sequential ecology**: a multiset of
`T = 776,142` descriptors (prefixes of length >= 2 of the sha256-bound source
tokens), in source order. Source order is the alphabetical order of the source
words — a **presentation artifact, not a semantic axis**: a factor-product
readout over stored evidence is content-addressed, and the order in which the
factors were built is irrelevant to the stored tables. For a non-sequential
ecology the parent's own real-scale packages registered a target-independent
**Knuth multiplicative-hash presentation lever**
(`gmi-833-h-real-scale-classical-v1`, `ORDER_MULT = 2654435761`, the identical
lever the siblings `gmi-833-h-real-scale-nearest-neighbor-v1` at `SIGMA_H05R`,
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
fit_lo      = order[0 : n_fit//2]             339,562    (R09 half)
fit_hi      = order[n_fit//2 : n_fit]         339,562    (R09 half)
```

The permutation is target-independent, fixed, and registered here before any
fit; it changes **no frozen count** (`n_fit`, `n_held` are unchanged), **no
frozen prediction** (`FREEZE_V1.md` section 8 fixes a process, not numbers),
no ecology, no grammar, no scope, no claim ceiling. It fixes **which**
descriptors are held, and nothing else. Route B re-derives the same
permutation, the same slice, the same readout language and the same winner
rule from this text alone.

## 2. The two-factor split, registered in exact arithmetic

The token list is split by a content-external, deterministic rule:

```
R1 = the tokens with len(w) % 2 == 0     (even length)
R2 = the tokens with len(w) % 2 == 1     (odd length)
```

Every token belongs to exactly one factor, so every descriptor occurrence
belongs to exactly one factor. The two stored relations are therefore
**disjoint and independent**. The exact occurrence split is measured and
re-derived by the executor:

```
R1 occurrences = 387,582        R2 occurrences = 388,560
R1 + R2 = 776,142 = T
```

The factor-local evidence of a query `q` (a descriptor) is, per factor `i`:

```
ci(q)  = the number of descriptors stored at fit positions that equal q and
         belong to factor i
fi(q)  = |Ai(q)|, where Ai(q) = { c : some token w of factor i has prefix q c }
         (the factor's continuation fan-out at q; the trie child count of q
          inside factor i's token trie)
```

Over the union the registered aggregates are `cnt(q) = c1(q) + c2(q)` and
`A(q) = A1(q) union A2(q)` with `|A(q)|` the union fan-out. **Every readout in
section 3 reads only these quantities and the query's own length.** There is
no marginalised table, no pre-computed joint, and no family-level structure.

## 3. The readout language `R` the family-blind recovery enumerates

Every arm is a readout over the stored factor graph — the descriptors at fit
positions, their per-factor occurrence counts and their per-factor
continuation fan-outs — or over the query itself, all derived from the
sha-bound bytes. An arm reads no response until its prediction rule is fixed.
The language, identical for every arm and closed before any outcome:

| arm | prediction for a held query `q` (length `L`) | structural class (post-hoc) |
|---|---|---|
| `C0` | `0` | `CONSTANT_ARM` |
| `C1` | `1` | `CONSTANT_ARM` |
| `LEN<=L`, L = 6..12 | `1` iff `L <= L` | `DESCRIPTOR_LENGTH_THRESHOLD` |
| `R1CNT>=K`, `R2CNT>=K`, K = 1..3 | `1` iff `ci(q) >= K` | `SINGLE_FACTOR_MEMBERSHIP` |
| `R1ASSOC>=K`, `R2ASSOC>=K`, K = 1..3 | `1` iff `|Ai(q)| >= K` | `SINGLE_FACTOR_ASSOCIATION` |
| `R1x&R2y` over `x` in {`R1CNT>=a`, `R1ASSOC>=a`}, `y` in {`R2CNT>=b`, `R2ASSOC>=b`}, a,b in {1,2} (16 arms) | `1` iff both conjuncts fire | `FACTOR_JOINT_CONSISTENCY` |
| `LEN<=L&R1ASSOC>=1&R2ASSOC>=1`, `LEN<=L&R1CNT>=1&R2CNT>=1`, L = 6..12 | `1` iff every conjunct fires | `FACTOR_JOINT_CONSISTENCY` |
| `PREF_VOTE` | majority true-label over stored proper prefixes `q[:k]` (`2 <= k < L`); empty neighbourhood -> fit majority | `NEIGHBORHOOD_MAJORITY_VOTE` |
| `EXT_VOTE` | majority true-label over stored descriptors extending `q` (descriptors of words starting with `q`, length `> L`); empty -> fit majority | `NEIGHBORHOOD_MAJORITY_VOTE` |
| `MEM_FALLBACK` | if `q` is stored, read out the STORED label of `q` — the registered decision `|A1(q)|>=1 AND |A2(q)|>=1` evaluated on `q`, i.e. the label the stored factor graph records for its own descriptor; else the fit majority | `STORED_LABEL_READ_WITH_FALLBACK` |

The language is closed at **54 arms**: `C0`, `C1`, 7 length arms, 12
factor-local count arms, 12 factor-local fan-out arms, 16 factor-product
joint arms, 4 length-gated joint arms, `PREF_VOTE`, `EXT_VOTE`,
`MEM_FALLBACK`. The post-hoc classifier reads the readout NAME and nothing
else: a name that conjoins an `R1...` condition with an `R2...` condition is
`FACTOR_JOINT_CONSISTENCY`; a name with a single factor condition is
`SINGLE_FACTOR_*`; a length-only name is `DESCRIPTOR_LENGTH_THRESHOLD`.

**The constant-branch exclusion rule.** A membership readout with a majority
fallback whose stored branch reads out a **constant** is excluded from the
enumeration: on a held query its stored branch cannot separate. Applied to
this ecology, the exclusion rule eliminates **nothing** from the language
above: the only membership-with-fallback arm, `MEM_FALLBACK`, has a stored
branch that reads the STORED label of the query (the registered decision
`|A1(q)|>=1 AND |A2(q)|>=1` evaluated on `q` — the label the stored factor
graph records), which is two-valued over any large fixed store by
construction (the fit store itself contains 470,352 positive and 208,772
negative descriptors), so it is not semantically constant and **is** admitted
to the enumeration. The winner rule must reject it by the data; the measured
rejection and the executor's re-derivation are registered in
`FREEZE_V1_SLICE_ADDENDUM_R2.md`. The executor asserts the fit positive
fraction (the share of fit descriptors with `|A1(q)|>=1` and `|A2(q)|>=1`)
exceeds `1/2` before enumeration — it does by construction of the ecology
(470,352 / 679,124) — which fixes the majority fallback at `1`.

The family's own mechanism that this package reasons about is
`R1ASSOC>=1&R2ASSOC>=1` — "does EVERY factor agree that the query has a stored
continuation?" — the **factor-product (message-passing) readout** of a
two-factor stored model. This package recovers it family-blind by the winner
rule. Structural class names are attached only after the winner rule runs, by
a classifier that reads the readout name and nothing else.

## 4. The registered winner rule (identical for every arm, family-blind)

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

## 5. The grammar `G_PGM`, bound by digest

`G_PGM` is the family-blind grammar of `FREEZE_V1.md` section 5, fixed here in
its exact form: the descriptor closure over the sha-bound token vocabulary
(prefixes of length >= 2), the two-factor split of section 2, the
factor-local evidence table of section 2, the readout language of section 3
and the charged-cost model of section 6. `grammar_pgm_v1.py` implements it and
exposes a stable digest over (the readout list, the presentation key, the
factor split rule); an extra readout must move that digest, and a test asserts
it does. The grammar contains no graphical-model macro, no
factor-graph-inference routine, no message-passing implementation and no
reference to any external implementation.

## 6. The charged-cost model and the registered `R07` crossover

The registered per-query charged cost of a readout is the number of stored
factor lookups it references:

```
C0 / C1 / LEN<=L                          0
R1CNT>=K, R2CNT>=K, R1ASSOC>=K,
R2ASSOC>=K, and the LEN-gated arms        1   (one factor-local lookup)
a product of one R1 condition with one
R2 condition (a joint arm)                2   (one lookup per factor)
MEM_FALLBACK                              2   (one membership lookup and one
                                               stored-label read)
PREF_VOTE / EXT_VOTE                      the number of stored descriptors
                                          referenced
```

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

No tie occurred at any measured stage; the definition is registered so the
winner rule is deterministic in every environment.

## 7. The protected interface and the falsifiers, made exact

- **Prototype agreement** on `held` = the exact number of held queries on
  which the arm's decision equals the true label (`|A1(q)|>=1 AND
  |A2(q)|>=1` over the full source).
- **Sign-decision error count** on `held` = the exact number of held queries
  on which the arm's decision differs from the true label.
- Falsifiers, with registered numerical form so they cannot be read after the
  fact:
  1. the winning arm's held error count must be **at most half** the
     fit-majority rule's held error count;
  2. the shuffled-label null (same arm predictions, held labels permuted with
     the registered seed) must **strictly exceed** the fit-majority rule's
     held error count;
  3. the one-factor design null must have **more than three times** the
     winning arm's held error count, while the arm that reads the OTHER
     (intact) factor alone must keep its uncorrupted error count exactly;
  4. the single-factor ecology control must NOT hand the win to a
     factor-product arm;
  5. the matched source-order presentation control must fire (the winning
     readout under source order must fail falsifier 1);
  6. the store ladder must be monotone non-increasing and end at the held
     error count;
  7. any cross-scope gate composition, foreign `sigma`, or failed negative
     control falsifies the claim ceiling.

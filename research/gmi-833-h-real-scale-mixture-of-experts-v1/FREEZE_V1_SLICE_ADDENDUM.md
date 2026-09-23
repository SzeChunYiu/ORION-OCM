# Slice addendum — the exact slice rule, the expert partition, the readout language, the charged-cost model and the falsifier forms

`source_main`: `3cbf841c`.
Governs: `FREEZE_V1.md` (committed before this addendum).

This addendum is committed **before any executor, test, data extraction, fit or
result artifact exists**, and CI asserts the ordering. It registers, in exact
reproducible form, the numbers the executor will assert rather than discover.

## 1. The exact slice rule

The `T = 776,142` descriptor occurrences of `FREEZE_V1.md` section 4 are
indexed canonically: token file order, then prefix length ascending. The
registered presentation key is the target-independent Knuth multiplicative hash

```
key(i) = (i * 2654435761) mod 2**32
```

and the presentation order is the descriptors sorted ascending by `key(i)`.
The arithmetic slices of that order, fixed before any fit:

```
n_fit      = (T * 7) // 8 = 679,124     >= 100,000   (R11 bar)
n_held     = T - n_fit    =  97,018     >= 20,000    (R11 bar)
rank_fit   = (7 * n_fit) // 10    = 475,386
rank_score = n_fit - rank_fit     = 203,738
fit_lo     = n_fit // 2           = 339,562
fit_hi     = n_fit - fit_lo       = 339,562
```

Every stage is a pair `(store, score)` over these slices:

| stage | store | score | queries |
|---|---|---|---|
| rank | `rank_fit` | `rank_score` | 203,738 |
| held | `fit` | `held` | 97,018 |
| primary | `fit_lo` | `fit_hi` | 339,562 |
| regen | `fit_hi` | `fit_lo` | 339,562 |

## 2. The expert partition, exactly

For a token `w` with first character `c = w[0].lower()`, the expert is

```
k = 0 if 'a' <= c <= 'f'
k = 1 if 'g' <= c <= 'm'
k = 2 if 'n' <= c <= 's'
k = 3 otherwise (including any non-alphabetical first character)
```

The full-source per-expert token and descriptor-occurrence counts, measured on
the frozen construction:

```
tokens:       [36,982, 24,211, 30,327, 12,814]        sum = N = 104,334
occurrences:  [279,312, 176,952, 227,771, 92,107]     sum = T = 776,142
```

Eighteen tokens have a non-alphabetical first character and therefore belong
to expert 3. Every descriptor occurrence belongs to exactly one expert, so the
four stored relations are disjoint.

The registered router, a function of the query descriptor alone:

```
r(q) = (sum(ord(ch) for ch in q) * 2654435761) mod 2**32 mod 4
```

The query distribution over the descriptor positions, measured:

```
over all T:   [190,040, 192,775, 190,509, 202,818]    sum = 776,142
over held:    [23,952, 24,149, 23,791, 25,126]        sum = 97,018
```

## 3. The readout language `R`, closed before any outcome

Each arm is a fixed predicate on the query descriptor `q`, the query length
`len(q)`, the store's per-expert occurrence counts `scnt_k(q)` and fan-outs
`sfan_k(q)` (0 when the expert stores nothing for `q`), the router `r(q)`, the
store's majority label `M` (two-valued, read from the committed receipt, never
hardcoded), and the store's routed predicate `spred(q) = 1 if sfan_{r(q)}(q)
>= 1 else 0`. The arms:

**Constants and lengths** (cost 0):
```
C0        : 0
C1        : 1
LEN<=L    : 1 if len(q) <= L else 0, for L = 6..12
```

**The router-selected (sparse-routing) family** — read ONLY the expert the
router selects (cost 1):
```
SEL_CNT>=t : 1 if scnt_{r(q)}(q) >= t else 0, for t = 1, 2, 3
SEL_FAN>=t : 1 if sfan_{r(q)}(q) >= t else 0, for t = 1, 2
```

**The fixed-expert family** — read exactly one expert, the same one for every
query (cost 1):
```
E0_CNT>=1, E0_CNT>=2, E0_CNT>=3, E1_CNT>=1, E2_CNT>=1, E3_CNT>=1
    : 1 if scnt_j(q) >= t else 0
E0_FAN>=1, E1_FAN>=1, E2_FAN>=1, E3_FAN>=1
    : 1 if sfan_j(q) >= t else 0
```

**The union / continuous-reweighting family** — read ALL experts (cost 2):
```
UNION_FAN>=t : 1 if any_k sfan_k(q) >= t else 0, for t = 1, 2
UNION_CNT>=t : 1 if sum_k scnt_k(q) >= t else 0, for t = 1, 2, 3
TOPK2_FAN>=1 : 1 if one of the two experts with the largest scnt_k(q)
               (ties by smaller k) has sfan >= 1 else 0
WSUM_FAN>=1  : 1 if sum_k scnt_k(q) * sfan_k(q) > 0 else 0
```

**The admitted membership arm** `MEM_FALLBACK` (cost 2). Its decision function
is registered exactly, in the same written form as its siblings:

```
if sum_k scnt_k(q) >= 1:      # the query is stored in this store
    return spred(q)            #   1 if sfan_{r(q)}(q) >= 1 else 0
else:
    return M                   #   the store's majority label (fit-majority
                               #   constant, read from the committed receipt)
```

The fallback branch is **load-bearing and reachable**: it is taken on every
query the store does not contain, and the executor asserts that at least one
registered query in every stage takes it (the measured counts are in section 8 of this addendum). Without that branch this arm
would be the same code path as `SEL_FAN>=1` under another name.

**The language is closed at 37 arms.** It is exactly the union of the five
families above. Nothing is added after any outcome. The predicate identities
registered in `FREEZE_V1.md` section 5 — the alias rule (Rule 1), the
neighbouring H08 constant-branch rule (Rule 2) and the two measured
coincidences (Rule 3) — govern how the 37 names are ranked: two committed arms
whose decision functions are identical at every registered stage and every
query are ONE readout registered under two names, the second name recorded as
an alias, and the alias is not a competitor for the winner or runner-up slot.

## 4. The winner rule

On a stage's query set, every arm makes one binary decision per query and the
error count is the number of decisions differing from the full-source label
`y(q) = 1 iff f_{r(q)}(q) >= 1`. The winner is the arm with the fewest errors;
ties are broken by charged cost, then by readout name (lexicographic). Aliases
under Rule 1 are not competitors. The majority rule is the constant arm
answering the store's majority label `M`; its error count is the fit-majority
rule's, and it is reported at every stage.

## 5. The grammar binding

`G_MOE` (freeze section 5) is implemented by the executor's readout module: the
descriptor closure over the token vocabulary, the four-expert first-letter
partition, the expert-local evidence tables, the router, and the closed
language of section 3. The module exposes a digest over the registered forms
(expert split rule, router, arm list, costs); the executor and the tests assert
the digest is stable, so a perturbed form fails rather than passing vacuously.
No family-level macro, no mixture-of-experts routine and no family name enters
the generator.

## 6. The charged-cost model and the resource crossover

The charged cost of an arm is the number of expert tables it reads: `0` for the
constants and the length arms, `1` for a router-selected or fixed-expert arm,
`2` for any arm reading two or more experts or the stored label. Let `V` be the
number of DISTINCT stored descriptors in the fit store, and `A = 27` the
alphabet width. A scan of an unknown descriptor's neighbourhood costs `2m`
lookups; a vocabulary index costs `V + A`. The crossover `m*` is the smallest
`m` with `2m > V + A`, and the crossover coordinate (R07) asserts the scan arm
strictly exceeds the index arm at `m*`. The store ladder of the winner readout
is evaluated on the registered budgets
`{1000, 5000, 10000, 30000, 67912, 135824, 271649, 679124}` and must be
monotone non-increasing in the stored budget.

## 7. The falsifier forms, registered before any outcome

- **F1**: the winner's held error count exceeds half the fit-majority rule's
  (`winner_errors * 2 > majority_errors`).
- **F2**: the label-shuffle null fails to strictly exceed the fit-majority
  rule (construction in `FREEZE_V1_SLICE_ADDENDUM_R2.md` section R2.2).
- **F3**: the design null fails to exceed three times the winner's held error
  count, or moves any arm that does not read the corrupted expert.
- **F4**: the `B'` unexcited-context control fails — a routing-free arm's
  decision sequence differs between the excited and unexcited arenas, or a
  router-selected arm does not collapse onto its matched fixed-expert
  counterpart with zero decision mismatches.
- **F5**: a non-monotone store ladder; **F6**: a crossover `m*` at which the
  scan arm does not strictly exceed the index arm; **F7**: any cross-scope gate
  composition, any foreign `sigma`, or disagreement between routes A and B.

The numerical forms live in this addendum and in
this addendum and in `FREEZE_V1_SLICE_ADDENDUM_R2.md` so they cannot be read
after the fact.

## 8. Per-stage design statistics, measured on the frozen construction

Measured on the frozen constructions before any executor exists, exact integers,
host of record billy-old, CPython 3.14.4. These are the numbers the executor
will assert rather than discover; any that does not survive the executor is
registered afterwards in a measurement addendum with its custody position
stated, never silently adjusted.

| stage | queries | label `y` positives | store majority constant `M` | fallback branch taken | `y` vs `y0` disagreement | majority-rule errors |
|---|---|---|---|---|---|---|
| rank | 203,738 | 46,192 | 0 | 46,697 | 80,398 | 46,192 |
| held | 97,018 | 22,123 | 0 | 17,150 | 38,296 | 22,123 |
| primary | 339,562 | 77,035 | 0 | 95,100 | 134,131 | 77,035 |
| regen | 339,562 | 76,828 | 0 | 94,246 | 133,573 | 76,828 |

Over the whole descriptor set: 175,986 of 776,142 positions have `y = 1`;
`y0` has 254,810 of 776,142; the two labels disagree on 306,000 of 776,142
positions (71,963 of 237,950 distinct descriptors). Per distinct descriptor,
`y = 1` for 42,484 and `y0 = 1` for 58,885.

Two facts this table fixes before the outcome:

- **the fallback branch of `MEM_FALLBACK` is taken**, in the thousands, at every
  stage (section 3), which is what makes the arm's registered decision function
  reachable rather than decorative;
- **the store majority constant is `0` at every stage**, so every stage is
  majority-negative and the constant arm `C0` is also the majority-rule arm.
  This is the fact that makes `MEM_FALLBACK` and `SEL_FAN>=1` coincide at these
  stages, and the fact that `FREEZE_V1.md` section 5 Rule 3 registers.

**The registered presentation control's frame, measured.** The `y` vs `y0`
disagreement column is the label change that the secondary reading (`arena B`)
introduces and the primary reading (`B'`) does not. It is registered here so
that the choice of `B'` as the primary form rests on a measured number and not
on a preference: a control that redefines the label moves 306,000 of 776,142
positions and therefore cannot simultaneously assert that the routing-free arms
are unchanged.


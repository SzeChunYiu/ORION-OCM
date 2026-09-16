# GMI #833 Section-E E8 recursive-library freeze

**Parent:** #833 Section E  
**Child:** #897  
**Source main:** `23e20b02166843437fc4010f96bcabf704455dab`  
**Status:** pre-implementation theorem/evidence freeze

This file freezes the language, expansion semantics, exact invention rule, lifecycle charges, training corpus, held-out tasks, search order, predicted recursive library, hostile cases, parent subtraction and claim ceiling **before** any inventor, evaluator, tests, receipt, manifest, reconciliation spec or dedicated workflow exists on this branch.

## 1. Scientific boundary

This tranche targets exactly the final three open Section-E rows:

1. grammar expansion `G_t -> G_(t+1)` from discovered reusable abstractions;
2. recursive library formation / primitive invention;
3. whether invented primitives reduce future discovery cost on frozen unseen tasks.

The result is deliberately finite and conditional. It is not universal library learning, open-ended grammar growth, P4 recovery completion, unseen-form discovery, or a theorem that abstraction always helps.

## 2. Parent subtraction

Parent mathematics and algorithms are not novelty here:

- #233 **HST-T04** owns the prefix-code/Levin allocation identity: shortening a target code by `Delta` multiplies its idealized allocation by `2^Delta`, under its stated scheduler/cost assumptions.
- #233 **HST-T05** owns the lifecycle amortization arithmetic: with useful reuse `H_eff`, per-use saving `DeltaC`, and acquisition/maintenance/revision charge `K`, benefit is positive iff `H_eff * DeltaC > K`.
- DreamCoder-style iterative library learning and program reuse are parent concepts.
- Stitch/top-down library learning owns corpus-guided synthesis of reusable abstractions for compression.
- MDL/refactoring/library-learning broadly own the idea of trading library-definition cost against corpus compression.

The repository residual is the exact #833 contract: conservative monotone grammar extension, deterministic charged invention, genuine recursive use of earlier abstractions, strict train/held-out custody, an exact finite discovery-burden comparison, an explicit harmful-transfer control, independent oracle, and fail-closed governance.

## 3. Frozen finite language

Base alphabet:

```text
G0 = (a, b, c)
```

A program is a finite nonempty sequence of currently legal symbols. Its protected semantics is its recursively **fully expanded base-token word**.

A learned macro is a fresh generation-ordered symbol `m_k` with a body of **exactly two symbols from the current grammar**. Its full expansion must be finite and nonempty in `{a,b,c}`.

A library is a generation-ordered acyclic map

```text
m_k -> (x,y)
```

where `x,y` are base symbols or earlier learned macros. A body may not reference itself, a later macro, or an unknown symbol.

Grammar growth is monotone:

```text
G_(t+1) = G_t union {m_(t+1)}.
```

Every old program remains legal and its expansion is unchanged.

## 4. GRW-1 — conservative grammar extension

For an acyclic library `L`, define `Expand_L` recursively:

- `Expand_L(a)=a`, `Expand_L(b)=b`, `Expand_L(c)=c`;
- if `m -> (x,y)`, then `Expand_L(m)=Expand_L(x) Expand_L(y)`;
- sequence expansion is concatenation of symbol expansions.

Target theorem:

1. adding an acyclic new macro does not change `Expand` for any program over the old grammar;
2. any new program's semantics equals the expansion obtained by replacing the macro with its registered body;
3. cycles or forward/unknown references fail before adoption.

Registered cycle terminal:

```text
RECURSIVE_LIBRARY_CYCLE
```

Unknown/forward reference terminal:

```text
INVALID_LIBRARY_REFERENCE
```

## 5. Frozen training corpus

The complete training corpus is fixed to **four copies** of one successful base program:

```text
TRAIN = [
  abababab,
  abababab,
  abababab,
  abababab
]
```

The exact task/program identity `abababab` is training-only and is not a held-out target.

The inventor receives **only this training corpus and the current library**. Held-out targets are not parameters of candidate generation, scoring, tie-breaking, stopping, or macro naming.

## 6. INV-1 — deterministic charged invention rule

At each generation:

1. collect every distinct contiguous pair of current grammar symbols that occurs in the current rewritten training corpus;
2. for each pair `body=(x,y)`, greedily left-to-right rewrite every non-overlapping occurrence in every training program with a hypothetical fresh symbol;
3. verify that fully expanding each rewritten program gives exactly its pre-rewrite base-token semantics;
4. compute the incremental charged objective.

Frozen charges for every new macro:

```text
C_definition = 2 symbol-units
C_maintenance = 2 symbol-units
C_revision_expected = 0 at this finite immutable scope
K = 4 symbol-units total incremental library charge
```

Let `N_before` be the current rewritten training-corpus symbol count and `N_after(body)` the count after the hypothetical rewrite. Define

```text
net_gain(body) = N_before - (N_after(body) + 4).
```

A macro may be admitted **iff `net_gain > 0` strictly**.

Among positive-gain candidates choose maximum `net_gain`; ties are broken by the lexicographic order of the candidate's **fully base-expanded body word**, then by its current-symbol body using the fixed symbol order below. Family labels, held-out targets and post-hoc task identities are never inputs.

Frozen symbol order:

```text
a < b < c < m1 < m2 < m3 < ...
```

After admission, commit the rewrite to the training corpus and continue. Stop when no candidate has strict positive gain or after 8 generations, whichever comes first. The frozen fixture predicts stopping earlier for mathematical reasons, not because of the depth cap.

## 7. REC-1 — frozen recursive invention prediction

The predicted invention trace is frozen before implementation:

### Generation 1

Current corpus symbol count: `4 * 8 = 32`.

Candidate `ab` has four non-overlapping occurrences per program. Rewriting gives four `m1` symbols per program:

```text
m1 m1 m1 m1
```

so `N_after=16`, charge `K=4`, and

```text
net_gain = 32 - (16+4) = 12 > 0.
```

Prediction:

```text
m1 -> (a,b)
Expand(m1) = ab.
```

### Generation 2

Current corpus is four copies of `m1 m1 m1 m1`, so `N_before=16`.

Pair `(m1,m1)` rewrites each program to `m2 m2`, so `N_after=8` and

```text
net_gain = 16 - (8+4) = 4 > 0.
```

Prediction:

```text
m2 -> (m1,m1)
Expand(m2) = abab.
```

This is genuine recursive invention because `m2` is defined using the earlier learned primitive `m1`, not directly as four base tokens.

### Generation 3 stopping prediction

Current corpus is four copies of `m2 m2`, so `N_before=8`.

Hypothetical `(m2,m2)` would rewrite each program to one symbol: `N_after=4`. With the same charge `K=4`:

```text
net_gain = 8 - (4+4) = 0.
```

Strict-positive admission therefore rejects it. The registered terminal is exactly two learned generations:

```text
RECURSIVE_LIBRARY_FIXED_POINT_AT_STRICT_POSITIVE_GAIN
```

A result that admits a zero-gain third macro is RED.

## 8. AMORT-1 — exact macro threshold instantiation

For this pair-macro language, every successful macro occurrence replaces two current symbols by one, hence per-use symbol saving

```text
DeltaC_use = 1.
```

For the registered incremental charge `K=4`, #233 HST-T05 specializes to

```text
beneficial iff H_eff > 4.
```

The training fixture has:

- `m1`: `H_eff=16` replacements, strictly beneficial;
- `m2`: `H_eff=8`, strictly beneficial;
- hypothetical `m3`: `H_eff=4`, exactly break-even and therefore rejected by the strict rule.

This arithmetic is parent-owned; the contribution here is its exact integration into the frozen recursive grammar-growth mechanism.

## 9. Frozen held-out tasks

These targets are fixed **before invention implementation** and are disjoint from the exact training program `abababab`.

### Reuse-positive held-outs

```text
P1 = ababab
P2 = abababc
P3 = cababab
P4 = ababababab
```

They are unseen exact target words but deliberately share reusable substructure with training. This tests conditional transfer, not arbitrary-domain generalization.

### Unrelated negative control

```text
N1 = cccc
```

No learned `ab`/`abab` macro can shorten this word. The expanded grammar may make its enumeration burden worse because the alphabet is larger. That negative must be preserved rather than averaged away.

## 10. HLD-1 — exact discovery-burden protocol

For a fixed grammar/library, search enumerates **all nonempty syntax programs** in this order:

1. increasing syntax-symbol length `1,2,3,...`;
2. lexicographic product order inside a length using the frozen grammar symbol order.

For each candidate, recursively expand to its base-token semantic word. Count every syntactic candidate, including semantic duplicates. Stop at the first candidate whose fully expanded semantics equals the held-out target.

The per-target discovery burden is exactly the number of candidates enumerated through that first hit.

Two arms:

- **baseline:** grammar `{a,b,c}` with no library;
- **expanded:** grammar `{a,b,c,m1,m2}` with the frozen invented library.

Library lifecycle overhead is charged **once across the registered positive held-out horizon**:

```text
C_library = 2 macros * (2 definition + 2 maintenance) = 8.
```

Frozen positive prediction:

```text
sum expanded_discovery(P1..P4) + 8
<
sum baseline_discovery(P1..P4).
```

This is the exact checkbox target. No per-task cherry-picking or dropping a difficult positive target is allowed.

Frozen negative-control prediction:

```text
expanded_discovery(N1) >= baseline_discovery(N1).
```

A harmful or neutral unrelated control is scientifically allowed and must remain visible.

## 11. Strict custody / no held-out leakage

The final experiment must machine-record separate canonical digests for:

- training corpus;
- positive held-out list;
- negative held-out list;
- invention rule/configuration.

The invention API may consume only the training corpus and frozen invention configuration. The experiment orchestrator must construct the library **before** passing held-outs to the evaluation function.

Required metamorphic leakage check: replacing both held-out lists with unrelated alternatives while leaving training unchanged must produce byte-identical library/invention trace.

Any held-out target in candidate generation/scoring/tie-breaking/stopping returns

```text
HELDOUT_LEAKAGE
```

rather than a positive result.

## 12. Frozen hostiles

The tranche is RED if any of these is not detected:

1. self/cyclic macro body -> `RECURSIVE_LIBRARY_CYCLE`;
2. forward or unknown macro reference -> `INVALID_LIBRARY_REFERENCE`;
3. a rewrite whose full base expansion differs from the original -> `SEMANTIC_REWRITE_MISMATCH`;
4. zero-gain candidate admitted -> `NON_STRICT_GAIN_ADMISSION`;
5. definition cost omitted -> `UNCHARGED_LIBRARY_DEFINITION`;
6. maintenance cost omitted -> `UNCHARGED_LIBRARY_MAINTENANCE`;
7. a held-out target is inserted into training or invention inputs -> `HELDOUT_LEAKAGE`;
8. held-out list/digest changed after the frozen protocol -> `HELDOUT_FREEZE_DRIFT`;
9. positive result reported without charging the total `8` library overhead -> `UNCHARGED_LIBRARY_OVERHEAD`;
10. unrelated negative control silently omitted -> `MISSING_NEGATIVE_TRANSFER_CONTROL`.

## 13. Independent exact oracle

A second implementation must not import the main inventor. It must independently:

- expand the frozen `m1,m2` library to base words;
- verify the two-generation dependency order and acyclicity;
- enumerate baseline and expanded grammar programs for P1..P4 and N1 using the frozen search order;
- recompute total positive burden with the `8` overhead;
- reproduce the sign of the positive and negative-control comparisons.

## 14. #833 reconciliation boundary

Only after dedicated PR CI is green may this tranche check exactly:

```text
- [ ] Define grammar expansion `G_t -> G_{t+1}` from discovered reusable abstractions.
- [ ] Implement recursive library formation / primitive invention.
- [ ] Test whether newly invented primitives reduce future discovery cost on unseen tasks.
```

The checked wording must state the finite registered scope, strict train/held-out separation, charged overhead, and preserved unrelated negative control.

No later Section-F or known-family recovery row is earned by this tranche.

## 15. Claim ceiling

```text
GMI_FINITE_CONSERVATIVE_RECURSIVE_LIBRARY_GROWTH_AND_HELDOUT_REUSE_BENEFIT_AT_REGISTERED_SCOPE
```

Forbidden promotions:

- `UNIVERSAL_LIBRARY_LEARNING`
- `PRIMITIVE_INVENTION_ALWAYS_HELPS`
- `OPEN_ENDED_GRAMMAR_GROWTH`
- `UNSEEN_FORM_DISCOVERY`
- `P4_RECOVERY_COMPLETE`
- `REAL_WORLD_TRANSFER_PROVED`
- `ALL_FUTURE_TASKS_CHEAPER`
- `COMPLETE_GMI`

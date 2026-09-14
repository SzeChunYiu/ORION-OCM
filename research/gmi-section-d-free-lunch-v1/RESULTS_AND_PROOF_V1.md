# Section D: conditional morphology free lunch, NFL control, and prospective phase law V1

Date: 2026-09-14. Owner: #602 Section D. Child tracker: #666.
Pre-outcome authority: `FREEZE_V1.md`, commit
`3fc4ddb2af98f738e5898a63488341c0d11f4364`.
Witness: `section_d_free_lunch_witness.py`.
Receipt: `RESULT_V1.json`.

## Executive result

The strongest version of the contributed Section-D/NFL objection is **too
strong**, but it exposes a real defect in the original target.

Two statements are simultaneously true:

1. **NFL survives.** On the exact uniform all-Boolean-function control,
   LOW_FIRST and HIGH_FIRST have identical performance distributions at every
   query budget 1..8.
2. **A strict free lunch appears as soon as registered structure carries
   decision information.** On the prospectively frozen UP/DOWN structured
   family, the best unconditioned policy scores `1/2` at one query, while the
   descriptor-conditioned policy scores `8/9`, an exact gain of **`7/18`**.

The right Section D target is therefore not a universal morphology independent
of the obligation. At registered finite candidate class `M`, it is

```text
(S_M(O), E, R, V, H) -> Pareto_M(O,E,R,V,H)
```

where `S_M(O)` is an obligation-structure descriptor sufficient for the
morphology distinctions the frozen class can make.

The witness then tests that correction prospectively. Four five-bit obligations
share the same coarse `E/R/V/H` values and hard memory budget but recover **four
different frozen morphologies**:

| world | pre-outcome structural fact | frozen / observed frontier at Q=16, memory cap 8 |
|---|---|---|
| W-A | degree-1 GF(2), support 3 | `xor_fold` |
| W-B | one minority point | `default_exceptions` |
| W-C | exact Hamming-weight step | `count_step` |
| W-D | Hamming-weight step + one defect | `count_step_plus_exceptions` |

All four predictions, every frozen horizon boundary, the remint, and both
frontier implementations passed unchanged.

Terminal:

```text
NFL_SYMMETRY_CONTROL_REPRODUCED
STRICT_FREE_LUNCH_FROM_REGISTERED_STRUCTURE_SUPPORTED
COARSE_D_MAP_FALSIFIED_AND_STRUCTURAL_REPAIR_SUPPORTED_AT_FINITE_SCOPE
PROSPECTIVE_PHASE_BOUNDARIES_CONFIRMED_AS_FROZEN
```

This is **not** `NO_FREE_LUNCH_THEOREM_FALSE`.

---

## 1. The exact theorem: information cannot hurt morphology selection

Let:

- `W` be a finite world set with distribution `mu`;
- `M` be a finite morphology set;
- `L(m,w)` be a registered scalar lifecycle loss;
- `Z=phi(W)` be any descriptor observed before morphology choice.

Define the best constant risk

```text
R0 = min_m E[L(m,W)]
```

and the best descriptor-conditioned risk

```text
RZ = min_delta E[L(delta(Z),W)]
   = sum_z P(z) min_m E[L(m,W) | Z=z].
```

### Theorem D-FL1 — conditional free lunch

```text
RZ <= R0.
```

Moreover, assuming every descriptor cell considered has positive probability,

```text
RZ = R0
```

iff there exists at least one morphology that minimizes conditional expected
loss in **every** descriptor cell. Equivalently,

```text
RZ < R0
```

iff

```text
intersection_z Argmin_m E[L(m,W)|Z=z] = empty.
```

### Proof

For every fixed morphology `m` and every descriptor value `z`,

```text
min_a E[L(a,W)|Z=z] <= E[L(m,W)|Z=z].
```

Multiply by `P(z)` and sum over `z`:

```text
RZ <= E[L(m,W)].
```

This holds for every `m`, so it also holds for the best constant morphology:

```text
RZ <= min_m E[L(m,W)] = R0.
```

For equality, take a global minimizer `m*` of `R0`. The difference

```text
R0 - RZ
= sum_z P(z) (
    E[L(m*,W)|Z=z]
    - min_m E[L(m,W)|Z=z]
  )
```

is a weighted sum of non-negative terms. With every retained cell having
positive probability, it is zero iff every term is zero, i.e. iff `m*` is a
conditional minimizer in every cell. The converse is immediate. QED.

### Executable proof pressure

The witness exhausts **531,441** integer loss tables:

```text
3 morphologies x 4 worlds, each loss in {0,1,2}
```

with two positive-mass descriptor cells. It verifies both the inequality and the
strictness iff/common-minimizer equivalence on every table. This does not replace
the proof; it is an implementation hostile for the proof statement.

Parent disposition: this theorem is a finite value-of-information / Bayesian
decision result and is **parent-owned** by the Blackwell decision-information
tradition. GMI's use of it is as a phase-law governance rule, not a novelty
claim.

---

## 2. NFL is reproduced, not dismissed

The negative control uses

```text
X = {0,...,7}
F = every Boolean function X -> {0,1}
```

uniformly, and two non-revisiting query orders:

```text
LOW_FIRST  = 0,1,2,3,4,5,6,7
HIGH_FIRST = 7,6,5,4,3,2,1,0.
```

At query budget `q`, performance is the best Boolean value observed so far.
Exact enumeration over all `256` functions gives:

| q | P(best=1), either policy |
|---:|---:|
| 1 | 1/2 |
| 2 | 3/4 |
| 3 | 7/8 |
| 4 | 15/16 |
| 5 | 31/32 |
| 6 | 63/64 |
| 7 | 127/128 |
| 8 | 255/256 |

The full distribution is identical for the two algorithms at every `q`.

This is the appropriate interpretation of NFL here: **with the structure erased
by the averaging symmetry, the algorithms cannot distinguish themselves in
expectation.**

The sharpened finite NFL parent is also respected. The structured UP/DOWN class
below is not closed under arbitrary input permutations: swapping inputs 3 and 4
in `UP_4` yields a function that is neither an UP threshold nor a DOWN threshold.
Therefore the closed-under-permutation sufficient condition for NFL equality is
absent in the structured class.

Parent disposition:

- Wolpert & Macready (1997) owns the all-problems NFL result;
- Schumacher--Vose--Whitley / Igel--Toussaint own the closed-under-permutation
  sharpening for finite uniform function classes.

The present result does not weaken them.

---

## 3. The exact structure-conditioned free lunch

Frozen structured families:

```text
UP_t(x)   = 1[x >= t],  t=0..8
DOWN_t(x) = 1[x <= t],  t=-1..7
```

with equal family prior. The descriptor is only `Z in {UP,DOWN}`.

At one query:

```text
E[LOW_FIRST | UP]   = 1/9
E[HIGH_FIRST | UP]  = 8/9
E[LOW_FIRST | DOWN] = 8/9
E[HIGH_FIRST|DOWN]  = 1/9.
```

Hence either unconditioned constant algorithm has

```text
R_const_value = 1/2,
```

while descriptor-conditioned selection has

```text
R_cond_value = 8/9.
```

The registered free-lunch gain is

```text
Delta = 8/9 - 1/2 = 7/18.
```

Nothing was fit to obtain this number. It was frozen in `FREEZE_V1.md` before
scored code existed and reproduced exactly.

The scientific reading is:

> structure is prior information. Once the world distribution is not symmetric
> under the transformations that erase that structure, a morphology/search
> policy may have a strict conditional advantage.

That is the route around NFL. It is a conditional theorem, not a universal
winner claim.

---

## 4. Why the original Section D map is still wrong

The contributed triage correctly identified a real gap: coarse ecology/resource
coordinates cannot by themselves decide morphology when obligations with the
same coarse setting demand different internal distinctions.

The prospective test makes this exact.

All four worlds share:

```text
n = 5
Q = 16
hard persistent-memory budget = 8
verifier = exhaustive truth table on all 32 inputs
developmental history = none
```

Yet their exact unique feasible Pareto frontiers are four different mechanisms.
Therefore the coarse mapping

```text
(E,R,V,H) -> M*
```

is not a function at this scope if `E` omits obligation structure.

This is a **falsification of the coarse target**, not of morphology phase laws.
The repair is to expose the structural information that the morphology decision
actually consumes.

---

## 5. Architecture-name-free structural signature

The frozen signature contains only function properties:

```text
algebraic_degree
algebraic_support_size_if_degree_le_1
minority_count
best_hamming_weight_step_residual
```

The observed held-out values are:

| world | degree | degree-1 support | minority count | best weight-step residual |
|---|---:|---:|---:|---:|
| W-A | 1 | 3 | 16 | 14 |
| W-B | 5 | — | 1 | 1 |
| W-C | 4 | — | 16 | 0 |
| W-D | 5 | — | 15 | 1 |

These four signatures are distinct and were computed before phenotype naming.
They contain no `NEURAL`, `SYMBOLIC`, `MEMORY`, `RAG`, `PROGRAM`, `BAYES`, or
other architecture-family macro.

At the frozen memory cap, the signature explains the feasible exact form:

- low algebraic degree/support -> compact XOR fold;
- tiny minority set -> default plus exact exceptions;
- zero count-step residual -> compact count step;
- small nonzero count-step residual -> count step plus local corrections.

This is a finite **morphology-sufficient structural descriptor**. It is not a
claim of a universal sufficient statistic for future morphology classes.

---

## 6. Pareto criterion, frozen before results

Every candidate is first required to be exact under exhaustive verification.
Wrong candidates are infeasible.

For exact candidates the resource vector is

```text
(persistent_cells, lifecycle_ops)
```

where

```text
lifecycle_ops
= description/install units
+ 32 exhaustive verification units
+ Q * serve operations per query.
```

Hard memory budget is applied before the frontier. Pareto dominance is ordinary
coordinatewise dominance, with at least one strict coordinate. There is no
post-hoc scalar price vector.

The witness uses two separately coded selectors:

1. all-pairs dominance census;
2. reverse-order incremental skyline insertion.

They agree on every registered world/horizon cell.

This proves implementation invariance of the frontier computation. It is **not
yet** the broader Section D requirement for replication across genuinely
different morphology-search algorithms; that box remains open.

---

## 7. Prospective held-out morphology predictions

The freeze named all four worlds and their winners before the witness existed.
All four were confirmed.

### W-A — sparse affine obligation

```text
y = x0 XOR x2 XOR x4
```

Observed structural signature: degree 1, support 3.
At memory cap 8 only the compact exact fold survives the stronger generic
parents on the Pareto frontier:

```text
{xor_fold}
```

### W-B — singleton residual

```text
y=1 iff x=10101
```

Observed minority count: 1.
Frontier:

```text
{default_exceptions}
```

### W-C — exact count step

```text
y=1 iff HammingWeight(x)>=3
```

Observed best count-step residual: 0.
Frontier:

```text
{count_step}
```

### W-D — count step plus one defect

Same as W-C except `00000` is flipped.
Observed best count-step residual: 1.
Frontier:

```text
{count_step_plus_exceptions}
```

The W-B and W-D outcomes are especially useful for Section D because generic
`default_exceptions` receives first refusal. The hybrid wins W-D only because
the structured rule shrinks the correction set from 15 minority points to one
rule-relative defect.

---

## 8. Exact horizon phase diagrams

At memory budget 64 the full table is legal. The freeze predicted the **full
Pareto set**, including generic exception storage as a stronger parent.

Common exhaustive verification adds 32 operations to every exact candidate and
therefore does not move pairwise operation crossings.

### W-A

Resource laws:

```text
xor_fold:          memory 4,  ops = 36 + 3Q
default_exceptions memory 17, ops = 49 + 2Q
full_map:          memory 32, ops = 64 + Q
```

`count_step_plus_exceptions` is dominated by `xor_fold` throughout.

Observed exactly as frozen:

```text
Q <= 13       {xor_fold}
Q = 14..15    {xor_fold, default_exceptions}
Q >= 16       {xor_fold, default_exceptions, full_map}
```

### W-B

```text
default_exceptions memory 2,  ops = 34 + 2Q
full_map           memory 32, ops = 64 + Q
```

Equality is at Q=30; the lower-memory exception store dominates at equality, so
the table enters only at Q=31:

```text
Q <= 30       {default_exceptions}
Q >= 31       {default_exceptions, full_map}
```

### W-C

```text
count_step          memory 2,  ops = 34 + 5Q
default_exceptions  memory 17, ops = 49 + 2Q
full_map            memory 32, ops = 64 + Q
```

Observed exactly as frozen:

```text
Q <= 5        {count_step}
Q = 6..15     {count_step, default_exceptions}
Q >= 16       {count_step, default_exceptions, full_map}
```

### W-D

```text
count_step_plus_exceptions memory 3,  ops = 35 + 6Q
default_exceptions          memory 16, ops = 48 + 2Q
full_map                    memory 32, ops = 64 + Q
```

Observed exactly as frozen:

```text
Q <= 3        {count_step_plus_exceptions}
Q = 4..16     {count_step_plus_exceptions, default_exceptions}
Q >= 17       {count_step_plus_exceptions, default_exceptions, full_map}
```

These are genuine phase boundaries in horizon/resource space. The strongest
competitor can delay a pairwise crossing: the table does not enter merely when
it first beats the compact rule on operations; it must also stop being dominated
by the generic exception morphology.

---

## 9. Disjoint encoding/remint

The freeze permuted bit coordinates by

```text
pi = (2,4,1,0,3).
```

For all four worlds, the following were invariant:

- algebraic degree;
- degree-1 support cardinality;
- minority count;
- best Hamming-weight-step residual;
- Q=16 / memory-8 Pareto frontier.

Thus the result is not tied to the original bit names or exception location.
This satisfies a disjoint **surface encoding** replication. It is not an
independent domain replication.

---

## 10. Parent subtraction

### NFL

Owned by Wolpert--Macready and sharpened finite-class NFL work. Our negative
control reproduces it. No novelty claim.

### Value of information

Owned by Blackwell-style decision theory. The inequality in §1 is an elementary
finite specialization. No novelty claim.

### Compact algebraic / rule representations

Ordinary symbolic, Boolean-algebra, table, and exception-store parents own the
mechanisms. GMI does not claim to invent XOR rules, lookup tables, thresholds or
residual correction lists.

### Surviving Section D residual

What remains useful is the **single governed composition**:

```text
NFL symmetry test
-> registered structural descriptor
-> exact conditional value test
-> architecture-neutral candidate mechanisms
-> complete Pareto accounting
-> prospective phase boundary
-> remint
-> stronger-parent interference on the frontier
```

That is a protocol/result about when a morphology law is scientifically
licensed, not a new optimization theorem.

---

## 11. What this establishes about "breaking NFL"

The phrase must be used carefully.

What is broken:

```text
the symmetry / closure conditions that force equal average performance
```

What is not broken:

```text
the NFL theorem itself
```

The exact free lunch is purchased by information: a structured problem class and
a descriptor that tells the machine which structure is present. In the uniform
all-function control that information disappears and the advantage collapses to
zero exactly as NFL predicts.

So the productive GMI question is no longer "does NFL forbid Section D?" It is:

> What is the coarsest prospectively observable structural descriptor that makes
> morphology choice conditionally predictable, and how much lifecycle value does
> each added distinction buy?

That is both falsifiable and recursively extensible.

---

## 12. #602 Section D disposition from this tranche

Earned at the registered finite scope:

- architecture-name-free morphology/resource descriptors: **yes**;
- Pareto criterion without post-hoc scalarization: **yes**;
- exact tiny-world phase diagrams: **yes**;
- analytic crossover surfaces: **yes**;
- next-world predictions frozen before enumeration/search: **yes**;
- predicted morphology transitions across registered structural/horizon
  boundaries: **yes**;
- disjoint surface-encoding replication: **yes**;
- symbolic/programmatic compact-rule phase: **yes**, at tiny finite scope;
- memory/retrieval phase: **yes**, W-B;
- hybrid phase: **yes**, W-D.

Not earned:

- universal/complete ecology coordinates independent of obligation structure;
- complete unbounded resource schema;
- developmental-history phase law;
- stochastic/heuristic search-algorithm replication;
- neural-like phase;
- probabilistic phase;
- search/planning phase;
- real-scale boundary uncertainty;
- extrapolation beyond the registered finite worlds.

The original coarse target should therefore be edited rather than silently
checked: `(E,R,V,H)` alone was **falsified** at finite scope and repaired by the
registered structural signature.

---

## 13. References / parent anchors

- D. H. Wolpert and W. G. Macready, “No Free Lunch Theorems for Optimization,”
  *IEEE Transactions on Evolutionary Computation* 1(1):67–82, 1997,
  doi:10.1109/4235.585893.
- C. Schumacher, M. Vose, D. Whitley, “The No Free Lunch and Problem
  Description Length,” GECCO 2001.
- C. Igel and M. Toussaint, “On classes of functions for which No Free Lunch
  results hold,” *Information Processing Letters* 86(6):317–321, 2003,
  doi:10.1016/S0020-0190(03)00222-9.
- D. Blackwell, “Equivalent comparisons of experiments,” *Annals of
  Mathematical Statistics* 24(2):265–272, 1953,
  doi:10.1214/aoms/1177729032.

Claim ceiling:

```text
FINITE_EXACT_PROSPECTIVE_SECTION_D_PHASE_LAW
PARENT_OWNED_NFL_AND_VALUE_OF_INFORMATION
NO_UNIVERSAL_MORPHOLOGY_OR_REAL_SCALE_CLAIM
```

# FREEZE — `gmi-833-ag6-universal-bases-v1`

Committed **before any implementation file exists in this package**. `git log --follow` over this
directory must show this file as the first object added. Every frame decision below — including the
capability battery, the cost definitions, the pre-registered probes and subsamples, and the rule by
which each row is allowed to close — is fixed here, before any measurement is taken.

## 0. Pins

| field | value |
|---|---|
| `source_main` | `50f833cc4bc3cadcefd44eca14fa58f73f815587` |
| repository | `SzeChunYiu/ORION-OCM` |
| issue | `833` |
| section comment | `5693520829` (section `AG`), heading level `###` |
| anchor | `### AG6 — Universality is a lower-bound null, not intelligence` |
| branch | `research/833-derive-bases` |
| claim ceiling | `GMI_AG6_THREE_UNIVERSAL_BASES_AT_REGISTERED_FINITE_SCOPE_WITH_BASIS_RELATIVE_COST` |

## 1. The exact rows this tranche may reconcile

Only these three, byte-exact from the comment body:

```
- [ ] Reconstruct at least three radically different universal low-level bases (e.g. register/counter, combinatory/rewrite, cellular/local) at bounded executable scope.
- [ ] Compare their compilation overhead, description bias, reachability geometry and developmental search burden.
- [ ] Test whether the same higher MI morphology/capability laws survive across these bases after resource normalization.
```

**No neighboring row is earned here.** In particular the fourth unchecked AG6 row,
`- [ ] Preserve `UNIVERSAL_COMPUTATION_ONLY` whenever no intelligence-specific predictive residual remains.`,
is a discipline-contract row that this tranche does not touch, and nothing in AG0, AG5 or AG7 is
touched either.

## 2. Registered scope — the one charged frame

Everything below is fixed now and may not be changed after a measurement is seen.

### 2.1 Registered semantic class

`MEALY_2x2` = every two-state binary Mealy machine: states `{0,1}`, start state `0`, input and
output alphabet `{0,1}`, transition `delta: (state,input) -> state` and output
`out: (state,input) -> {0,1}`, both given as 4-bit tables over the key order
`((0,0),(0,1),(1,0),(1,1))`. The class has exactly `2^4 * 2^4 = 256` members. Machine index
`m = 16*delta_bits_index + out_bits_index` with both indices enumerated by
`itertools.product((0,1), repeat=4)` in order — the same construction the merged parent
`gmi-833-g0-register-core-v1` uses in `exhaustive_mealy_census`.

### 2.2 Registered word set

`W` = every `{0,1}`-word of length `0..3`, enumerated shortest-first and lexicographically inside
each length. `|W| = 15`. This is the parent's `all_binary_words(3)`.

### 2.3 Task set

`T = MEALY_2x2 x W`, `|T| = 3840`. **Identical for all three bases.** A basis *realizes* machine
`m` iff, for all 15 words `w`, running that basis's compiled artifact on the basis's encoding of
`w` yields exactly the basis's encoding of `out_m(w)`, with no budget exhaustion.

### 2.4 What "universal" means here, and what it does not

`REGISTERED_UNIVERSAL(basis)` holds iff the basis realizes all 256 members of `MEALY_2x2` on all
15 words, i.e. 3840/3840 exact matches. This is **finite, registered universality at a declared
scope**. It is *not* Turing universality and is not evidence for Turing universality. Turing
universality of combinatory logic is Schönfinkel's and Curry's; of elementary cellular automata,
Cook's; of two-counter machines, Minsky's. This tranche claims none of it.

### 2.5 The three bases

| basis | signature | one-step relation |
|---|---|---|
| `REG` register/counter | `READ, INC, DECJZ, EMIT, HALT` over registers and labels | one labelled instruction fires |
| `CMB` combinatory/rewrite | generators `S`, `K`; one binary application former | `S x y z -> x z (y z)`, `K x y -> x` |
| `CEL` cellular/local | finite cell alphabet `Sigma`; one local rule `d: Sigma^3 -> Sigma` | one synchronous radius-1 update of the whole tape |

`REG` is re-derived inside this package rather than imported from the parent, so that all three
bases are charged by one accounting. Agreement with the parent's published census (256 machines,
15 words, 3840 comparisons, 0 mismatches) is itself a check.

### 2.6 Held fixed across bases

- the 3840 tasks;
- the meaning of **one step** = one application of that basis's own declared one-step relation;
- the meaning of **one unit of size** = one occurrence of a symbol of that basis's own declared
  signature in the canonical serialization of the artifact;
- the budget rule: a per-basis step cap declared before the run, with the number of tasks that hit
  the cap reported and required to be `0`;
- the capability battery `Q` of 2.7;
- the domination rule of 2.9.

### 2.7 Varies by basis — and this *is* the description bias

- the signature itself;
- the input/output encoding convention (register: input stream / output stream; combinatory:
  Church fold-lists over Church booleans; cellular: an input track and an output track on a tape);
- the artifact space and therefore what "one edit" means (2.10).

These are declared, not hidden. No claim is made that a step or a size unit means the same
physical thing in two different bases. `CROSS_BASIS_COST_UNIT_COMMENSURABLE` is forbidden.

### 2.8 Capability battery `Q` — frozen now, before any frontier is seen

Three registered target transductions on `W`:

- `IDENTITY`: target output on `w` is `w`;
- `COMPLEMENT`: target output on `w` is the bitwise complement of `w`;
- `CONST0`: target output on `w` is `0^|w|`.

`Q(m) = |{(task, w) : out_m(w) equals task's target on w}|`, an integer in `[0, 45]`. Every machine
scores at least 3 because all three targets agree on the empty word. `Q` is a property of the
machine, not of a basis, so `Q` transfers across bases by construction; that is the point of the
test, not a result of it.

### 2.9 Cost `C` and the law object

Two cost coordinates, both per basis and per machine:

- `C_size(m)` = size of the compiled artifact in that basis's own units (2.6);
- `C_steps(m)` = total steps over all 15 words.

Law object, shape taken from `research/machine-intelligence-morphogenesis-v1/PHASE_LAW_V1.md`
(capability/resource Pareto frontier): `m` is **dominated** iff there exists `m'` with
`Q(m') >= Q(m)` and `C(m') <= C(m)` and at least one inequality strict. The **frontier** is the set
of undominated machines. Reported per basis, per cost coordinate.

**Invariance class, stated now.** The frontier depends on `C` only through the within-basis
*ordering* of `C`. It is therefore invariant under every strictly increasing map applied uniformly
to all 256 machines of one basis — which is exactly the class of global resource normalizations
(unit changes, affine rescalings, division by a basis constant, monotone reparametrizations). It is
**not** invariant under machine-dependent reweighting. That is a weaker statement than
"invariant under arbitrary resource normalization" and the stronger reading is forbidden.

**Vacuity guard, fixed now.** Frontier sizes are reported before any symmetric difference is
interpreted. A frontier of size `1` or of size `256` makes a cross-basis symmetric difference
uninformative; if either occurs the comparison is reported as `VACUOUS` and the row does not close
on it.

### 2.10 Developmental search burden — the search model, fixed now

The uniform-enumeration reading ("enumerate artifacts in size order until one realizes the target")
is **not** executable across all three bases and this tranche will say so with an exact count rather
than restricting a basis to make it executable. Choosing a restricted rule schema in order to make
the fourth comparison measurable would narrow the row to close it, which is forbidden.

The search model actually measured is a **one-edit local-search landscape**, with one uniform
shape and a basis-relative slot structure that is itself the declared bias:

> An artifact is a finite list of typed slots, each with a finite admissible domain. One **edit**
> replaces the value in exactly one slot by a different admissible value of that same slot.

- `REG`: slots are the opcode, register operand and successor label(s) of each instruction.
- `CMB`: slots are the leaves of the term; the admissible domain of every leaf is `{S, K}`.
- `CEL`: slots are the entries of the local rule table; the admissible domain of every entry is
  the cell alphabet.

Per basis and per machine, measured: `neighbourhood_size`, `preserving` (neighbours that still
realize the same machine), `viable` (neighbours that realize some member of `MEALY_2x2`), and the
exact Fractions `preserving/neighbourhood_size` and `viable/neighbourhood_size`.

**Pre-registered subsample.** The one-edit census runs on `S16` = the 16 machines whose index is
`0 mod 16`, fixed here before any measurement. If the full 256 turns out affordable it is reported
as a supplement; `S16` remains the pre-registered basis of any claim.

### 2.11 Reachability geometry — the probe set, fixed now

Measured on the **corridor plus one-step fringe**: the configurations visited by the deterministic
run, together with every one-step successor of each such configuration under the basis's *full*
one-step relation (for `CMB`, contraction of any redex, not only the leftmost-outermost one).

Pre-registered probes: machines of index `0, 85, 170, 255` on the word `(0,1,0)`. Reported per
basis: corridor length, fringe size, maximum and minimum out-degree, number of normal-form /
terminal configurations, and — for `CMB` — a local-confluence census (for every corridor
configuration and every pair of distinct one-step successors, do the two successors join within the
declared join budget).

Supplementary and explicitly labelled as a lower bound when its cap is reached: the size of the
full reachable set from the probe start under the full one-step relation, node cap `50000`.

## 3. Closure rule for each row — fixed before measurement

- **r34** (three bases) closes iff all three bases are constructed in this package and each is
  `REGISTERED_UNIVERSAL` at 3840/3840 with 0 budget exhaustions, under two materially independent
  routes, and `REG` reproduces the merged parent's published census.
- **r35** (four comparisons) closes iff *all four* of compilation overhead, description bias,
  reachability geometry and developmental search burden are measured on the frame declared above
  and reported with exact arithmetic. If any one of the four is not delivered on that frame, r35
  goes to `not_closed` with the obstruction stated. Delivering three of four does not close it.
- **r36** (MI law survival) closes iff the three bases are genuinely comparable — same task set,
  exact realization, `Q` basis-independent, and the frontier test non-vacuous by 2.9 — and the
  frontier comparison is then reported with its verdict, whether the verdict is SURVIVES or FAILS.
  If comparability fails, r36 goes to `not_closed` with the incomparability stated as the result.

A negative verdict on r36 (the law does **not** survive) is a closure of the row, because the row
says *test whether*, not *show that*.

## 4. Two materially independent routes

Route A: the package executor. Route B: an oracle importing nothing from route A and nothing from
any parent module — it rebuilds `MEALY_2x2` and `W` from their definitions, and for `CMB` it
evaluates the **source lambda term directly** by capture-avoiding substitution under normal order,
bypassing bracket abstraction entirely, so that the compiler and the reduction engine are both
independently checked. Resource and geometry quantities get their own second mechanisms in route B
rather than reusing route A's traversal.

## 5. Hostiles and nulls — required before any result is reported

Every hostile must be **detected**, and each must be paired with a control proving the checker moves
the quantity that hostile perturbs. The locality hostile is mandatory: a planted radius-2 dependence
in the cellular rule must be caught by the locality checker, and the no-alarm case must be asserted
on the true rule. A null the true result beats is required, and the no-alarm case must be asserted
on the real configuration.

## 6. Bound classification — mandatory

Every stated bound carries a class: `VACUOUS` (the bound is implied by the declared range of the
quantity), `ATTAINED` (a witness meets it), `STRICT_UNATTAINED`, or `LOWER_BOUND_ONLY` (a cap was
reached). A tightness test by attainment does not detect vacuity for an upper bound; vacuity is
tested separately by comparing the bound against the quantity's declared range.

## 7. Parents (full ledger with verified DOIs in `PARENT_LEDGER.md`)

Schönfinkel 1924 and Curry 1930 own combinatory logic and the `S`/`K` basis; Turner 1979 owns
optimized bracket abstraction; Church and Rosser 1936 own confluence; von Neumann 1966, Codd 1968,
Smith 1971, Margolus 1984 and Cook 2004 own cellular automata and their universality; Hedlund 1969
owns the characterization of cellular automata as exactly the shift-commuting continuous maps;
Minsky 1967 owns register/counter machines. Inside this corpus, `gmi-833-g0-register-core-v1` owns
the register basis and its Mealy census, `gmi-833-ag5-extension-lowering-v1` owns the measured
structure-dependence of `NEIGHBOR_UPDATE`, `gmi-833-ag2-signature-free-syntax-v1` owns the
signature-below-grammar reading, `gmi-833-ag1-descent-stack-v1` owns the `F0..F9` layering, and
`gmi-833-aj12-foundation-substrate-relativity-v1` owns formalization-style relativity.

Nothing in that list is claimed novel here. The residual contribution of this tranche is the
**charged cross-basis comparison on one frame**, and the normalization-invariance statement that
makes the frontier verdict attributable to the basis rather than to the accounting.

## 8. Forbidden promotions

```
UNIVERSAL_SIMPLICITER
TURING_UNIVERSALITY_PROVED_HERE
COMBINATORY_BASIS_TURING_UNIVERSAL_PROVED_HERE
CELLULAR_BASIS_TURING_UNIVERSAL_PROVED_HERE
REGISTER_BASIS_TURING_UNIVERSAL_PROVED_HERE
BASIS_INDEPENDENT_DESCRIPTION_SIZE
CROSS_BASIS_COST_UNIT_COMMENSURABLE
PARETO_FRONTIER_INVARIANT_UNDER_ARBITRARY_RESOURCE_NORMALIZATION
SEARCH_BURDEN_BASIS_INDEPENDENT
UNIFORM_ENUMERATION_SEARCH_BURDEN_MEASURED
INTELLIGENCE_FROM_UNIVERSALITY
ALL_COMPUTATIONAL_MODELS_EMBEDDED
MI_LAW_PROVED_BASIS_INVARIANT
UNIQUE_MINIMAL_UNIVERSAL_GRAMMAR
COMPLETE_GMI
```

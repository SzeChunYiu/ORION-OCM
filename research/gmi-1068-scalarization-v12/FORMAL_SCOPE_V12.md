# Formal scope V12

Read [CORE.md](CORE.md), [THEORY_V12.md](THEORY_V12.md) and
[FREEZE_V12.md](FREEZE_V12.md). The kernel results cover T1–T6 over the
explicit scalar-law interface below. They include a concrete integer
instance. No real-number instance is constructed or silently imported.

## Scalar premises and actual instance

[ScalarLawsV12.lean](ScalarLawsV12.lean) imports only `Std`.
Its `Scalar α` class provides addition, multiplication, negation, zero,
one and the two order relations, with seventeen explicit scalar laws:

- additive associativity, commutativity, zero and additive inverses;
- multiplicative associativity, commutativity, identity and distributivity;
- order reflexivity, transitivity, antisymmetry and totality;
- strict order iff weak order and inequality;
- compatibility of weak order with addition;
- nonnegative products nonnegative and positive products positive;
- `0 < 1`.

No vector inequality, separation, order-recovery or minimization theorem
is an interface field. Derived scalar identities, cancellation, strict
translation compatibility and difference/order equivalences are proved
from these laws.

`intScalar : Scalar Int` supplies the actual built-in integer operations
and their proved laws. This witnesses a nontrivial model of the interface.
The generated contract also checks general-dimensional integer instances
using explicit `Int.le` and `Int.lt`; it does not merely name the instance.

The scalar structure is a declared mathematical premise, not a selected
utility function, an empirical calibration or a consequence of process laws.
Applying the generic proofs to real numbers requires a real-number
implementation satisfying the fields. The real specialization in THEORY
is a complete paper argument, not a kernel-checked real model.

## Finite sums and T1–T2

[FiniteSumsV12.lean](FiniteSumsV12.lean) defines `sum` recursively on
`Fin n`, for arbitrary natural n. It proves linearity, multiplication
compatibility, weak monotonicity, strict improvement at a coordinate and
splitting off any selected coordinate. No finite-sum theorem is assumed.

`dot w x = sum (fun i => w i * x i)`.
`CoordLE x y` means every coordinate of x is at most its counterpart in y.
`Nonnegative w` and `Positive w` mean all weights have the respective sign.

- T1, `dot_monotone`: nonnegative weights and `CoordLE x y` imply
  `dot w x ≤ dot w y`.
- T2, `dot_strict`: add a selected coordinate k with `x k < y k` and
  `0 < w k`; then `dot w x < dot w y`.

T2 permits zero weights elsewhere. Strictly positive weights are its
special case. The proof reduces scalar multiplication inequalities to the
proved difference/order equivalences, then uses finite-sum induction.

Every dimension is covered, including zero. For dimension zero, T1 is the
comparison of two zero sums; T2 cannot supply its required `Fin 0` coordinate.
Statements over another finite index set use a chosen enumeration; no
separate reindexing theorem is claimed in these modules.

## Explicit separator and T3–T4

[ScalarizationV12.lean](ScalarizationV12.lean) uses `magnitude a`, defined
as a when `0 ≤ a` and as `-a` otherwise.
`magnitude_bounds` proves its nonnegativity and its bound on `-a`.
It is the ordinary absolute-value construction for this ordered scalar model.

`except f k` sums all coordinates except k. For d and selected k:

```text
S = except (fun i => magnitude (d i)) k
separator d k i = if i = k then S + 1 else d k
```

`separator_positive` proves every weight positive when `0 < d k`.
`separator_formula` proves the exact score
`d k * ((S + 1) + except d k)`.
`separator_dot_positive` proves that score strictly positive.
The paper additionally states the lower bound by `d k`; that stronger
inequality is not a separate registered kernel theorem.

`dot_difference` connects this construction to differences of two scores.
`separating_weight` produces a positive weighting ranking x above y
whenever `CoordLE x y` fails.

- T3, `positive_family_recovers_order`: coordinatewise order is equivalent
  to the same weak score comparison for every strictly positive weight vector.
- T4, `incomparable_reversal`: failure of coordinatewise order in both
  directions yields two positive weightings with opposite strict rankings.

These are arbitrary-dimensional theorems. They neither privilege one weight
vector nor require division or an Archimedean assumption.
The generic magnitude and existence arguments use classical logic;
no executable extraction or search-efficiency theorem follows.
Normalization of positive real weights is outside this kernel development.

## T5: reflection alone is impossible

`no_total_scalar_reflection` concerns any relation r on a type X and any
scalar target whose weak order compares every two values.
If neither r(x,y) nor r(y,x) holds, it refutes existence of a function f
satisfying `f a ≤ f b → r a b` for all a,b.

Thus even reflection alone is impossible; the theorem does not require
preservation as an extra premise. Equal scalar values are included because
weak comparison still holds. The coordinate-specific
`coordinate_no_total_reflection` applies this result on an arbitrary
feasible-domain subtype containing an incomparable vector pair.

## T6: attained minimizers

`Minimizer D w x` includes feasibility of x and its weak score comparison
against every feasible y. `ParetoEfficient D x` includes feasibility and
excludes a feasible y weakly below x everywhere and strictly below at a
selected coordinate.

`positive_minimizer_efficient` proves the implication for every feasible
predicate D and strictly positive w. It assumes neither convexity nor
finiteness of D and does not assert existence of a minimizer.
Equivalence with a dominance-plus-unequal-vectors definition of efficiency
is explained in the paper; the kernel definition uses a strict coordinate.

## Contract, reproduction and trust

[proof_contract_v12.py](proof_contract_v12.py) fixes the three source names
in dependency order and seventeen explicitly typed registrations.
Sixteen are theorem applications, including two ordinary-integer
specializations; one is the `intScalar` data instance.
Bracketed Int labels describe specializations of existing declarations.
They do not claim additional source theorem names.

[check_lean_v12.py](check_lean_v12.py) compiles all sources and the generated
typed contract in a fresh directory with Lean4.19.0 and warnings as errors.
Every registration prints its kernel dependencies. The reviewed proofs use
only standard logical dependencies such as propositional extensionality,
classical choice and Lean's quotient principle where needed.
Explicit scalar-law parameters remain premises even when the dependency
report lists no additional logical principles.

The guard's source-valid empty/weakened/removed-instance controls separately
test that compilation alone cannot impersonate the registered statements.
No placeholder or additional unchecked axiom is supplied by these modules.

Python arithmetic, exhaustive calibration, hostile input validation and their
correspondence to Lean are separately checked, not kernel-certified here.
The unsupported-frontier example and real normalization argument have paper
proofs and exact executable controls. No convex converse, empirical learning
result, context-free preferred scalar or full GMI theory is proved.

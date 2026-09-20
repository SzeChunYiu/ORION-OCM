# V20 separating controls and excluded inferences

These are analytic controls; execution outcomes belong to independent tests.

## T4.1 — lost continuation and its repair

Use states {0,1,2}, base order 0≤1≤2, one action with d(0)=2 and
no successor from 1 or 2. For candidates {0,1}, current-value pruning retains
only 1 and loses the attainable endpoint 2. The upward goal {2} is lost.
The defect is upward preservation of definedness: 0≤1 but only 0 can act.
Greatest simulation removes (0,1), so both candidates are maximal within this
candidate set and the successful continuation is retained. This is the registered
mechanism repair, not a claim that ordinary value dominance was sufficient.
Equivalent present values can fail identically: equate 0 and 1 in the base
order while retaining their different enabled futures. Arbitrary representative
selection before checking the guard can keep the wrong history.

## T4.2 — other pruning failures

For 0<1 and the total update F(0)=1,F(1)=0, raw input-maximal pruning keeps
1 and returns only 0. Totality alone does not prevent order reversal.
For the identity update, pruning {0,1} to {1} loses the goal {0}; this goal
is not upward-closed. The valid theorem concerns upward goals only.
A missing maximal equivalence class makes a proposed representative set
noncofinal. A representative outside the attained set is not a legal solution
to the stated cardinality problem. Distinct equivalent maxima remain in Max(A)
until the explicitly declared representative operation is applied.

## T4.3 — resources and observer scope

Take a one-state V8 machine with a cost-one self-loop. Lift residual budgets
0 and 1. Their original state and constant endpoint value can be identical,
but only residual budget 1 can execute the action. Collapsing the pair before
checking simulation can erase the only successful continuation. Retaining the
lifted states and deriving G distinguishes the affordability requirement.

If x reaches a goal only by a and y reaches it only by b, bare existential
goal capability can agree while same-word simulation fails. Its greatestness
is relative to the registered observer, not to every possible notion of capability.
Similarly, state-order preservation alone cannot transport an arbitrary endpoint
Context: comparable states x≤y with O(x)=some(1) and O(y)=none (or some(0)
under 0<1) violate the required observation guard already at the empty word.

For nondeterminism, let p --a→ s where s enables both b,c. Let q have two
a-successors t,u, with t enabling only b and u only c. Both starts admit the
same finite words ε,a,ab,ac, but no q-successor can simulate s. This blocks
the deterministic proof's single-successor-for-all-suffixes step.

## T4.4 — infinite frontier boundaries

Nat with its usual order has no maximal element, despite each value being
obtainable as a finite index. Nat with an added greatest element infinity has
cofinal maximal set {infinity}, despite the chain 0<1<2<...; well-founded
ascent is therefore not necessary for a particular attained set's cofinal maxima.
An infinite antichain has no strict ascents at all, so ascent is well-founded,
yet every element is maximal and its frontier is infinite.

The disjoint union of Nat and a single isolated point m has Max={m}, but no
natural number is below m. Existence of some maximal value is weaker than
cofinality of the maximal frontier. These examples are paper-level scope controls;
finite calibration cannot establish their infinite behavior.

## T4.5 — validation boundaries

Malformed dimensions, aliases such as Boolean indices, invalid selectors and
invalid later word symbols must be rejected before a failed prefix can hide them.
Empty attained images, empty generic state/action sets, and evaluator-undefined
histories are valid mathematical cases and must not be mistaken for malformed
input. Actual partial postcomposition changes E exactly by the Option domain;
it keeps P separately even when illegal histories have defined ambient values.

# Adaptive-information and exact-helper erratum

Status: corrective engineering against the reviewed PR154 four-file snapshot.
No claim of a new learning mechanism, frozen-population result, or whole-PR repair.

## Corrected finite adaptive identity

Fix a finite number n of probe slots. Set
`H_i=(H_{i-1},P_i,Y_i)`, where H0 includes all initial information and any
independent algorithm random seed used by the policy. Require
`I(Theta;P_i | H_{i-1})=0`: choosing a probe introduces no extra target
information beyond recorded history.

Then the ordinary chain rule gives
`I(Theta;H_n | H_0)=sum_i I(Theta;Y_i | H_{i-1},P_i)`.
Indeed, expand each increment as
`I(Theta;P_i | H_{i-1}) + I(Theta;Y_i | H_{i-1},P_i)`;
the first term is zero. A conditional bound of b bits on each increment implies
at most nb additional bits. Initial target information remains outside that bound.
If H0 is independent of Theta, this is also a bound on the full transcript's
information. No unbounded or random stopping-time extension is asserted.

Ordinary conditioning on the complete generated probe sequence is different.
For fair-bit Theta, fixed P1, Y1=Theta, P2=Y1, and constant Y2, the old conditioned
left side is 0 bits, but the correct increment sum and transcript information
are 1 bit. The regression computes these exactly for the two equally likely
worlds; it is a finite counterexample/control, not a general entropy estimator.
The general corrected identity follows from the stated chain-rule proof.

## Exact numerical scope

The helper implements exact rational instances of finite mathematical statements.
It accepts built-in int, Fraction and finite built-in float. Floats mean precisely
their represented binary rationals; prior rounding and intended decimal values
cannot be reconstructed. Use `Fraction(1,10)` for the exact rational one tenth.
Thus float probabilities 0.1 and 0.9 fail exact normalization even though their
rounded floating sum is 1.0; the helper neither normalizes nor invents a tolerance.

Numeric results use Fraction. Boolean, string, Decimal, NaN and infinity are
rejected. Probability kernels/weights must be nonnegative and sum exactly to one;
successors must belong to the supplied finite state set, including zero-mass
entries. Cognitive costs must be nonnegative; finite stop and ordinary decision
costs may have either sign. State/action IDs are distinct and hashable.
Bisimulation compares action sets independent of iteration order and literal
contracts; contract equality must be deterministic. None is reserved for STOP.

The finite cognition allowance is a nonnegative built-in integer. Every cognitive
transition consumes one unit, and STOP is mandatory at zero. A STOP tie remains
STOP. This repairs arithmetic in the bounded parent; it does not establish
properness or select a Bellman solution for unlimited zero-cost cognition.

Exact helper arithmetic does not certify source cost extraction, protected
legality, demand distributions, observational adequacy, unbounded policy scope,
or lifecycle coverage. It also does not retroactively certify the unchanged
prospective selector's numerical outputs or transfer a competitive guarantee.
Fraction serialization and its runtime/storage costs remain integration work.

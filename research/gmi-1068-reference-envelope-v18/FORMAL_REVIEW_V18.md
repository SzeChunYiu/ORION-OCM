# Independent formal review — V18

The reviewer authored the paper exposition and independently reviewed the
mechanizer's six new Lean sources, four immutable dependencies, explicit typed
contract, replay checker and source-valid mutation guard. This is a source/proof
review, not an independent second paper authorship claim.

## Actual independent kernel replay

The final75-entry contract passed a fresh isolated10-source build under
Lean4.19.0 with warnings treated as errors. Generated audit SHA256:
6a474d99cd5c5b51c6c511fe9bd58e1340627edd712bb4e175b1e2883192cb09.
The proof-contract source SHA256 is
bebb46e4961b599955ef717df0371ffc289087e8a83c996a2154cd0b5031dda3.
The reviewer performed this replay, rather than relying only on the author's
reported compilation. The checker printed and inspected each registered
statement's axioms and rejected sorryAx. No unproved assumptions were added.

A separate fresh10-source build checked one helper theorem and nine additional
examples: target shortest length at L=1; exact nontarget length3 from an ε-only
base; impossibility of an absent nontarget output; actual Int Dirac evaluation;
impossibility of a zero-dimensional normalized probability; preservation of
E=False; an illegal observation despite ambient E=True; mutual-conversion
possibility for distinct Bool objects; and an actual true target indicator.
These are nonvacuous boundary specializations, not extra primary-corpus counts.

## Reviewed conclusions and assumptions

PrefixWrapperV18 uses List Bool programmes and an actual recursive prefix
parser. success_iff characterizes successful inputs in both directions;
wrapper_binding and pad_binding expose the actual operations. Prefix freedom
is derived from base prefix freedom and positive padding, not supplied as an
output assumption. The target cannot prefix a simulation word or vice versa.
The parser does not accept the empty programme, including when the base does.

ShortestCodesV18 defines minimality using actual successful evaluation and
List.length. minimum_exists uses well-ordering of natural lengths; uniqueness
compares the two witnesses. target_minimum and nontarget_minimum_iff derive
the precise1 and L+j lengths. nontarget_exists explicitly handles outputs
missing from a nonuniversal base. The actual K-shift is not an interface axiom.
No claim that this Option-machine interface is itself a universal TM is registered.

FiniteMarginsV18 derives finite Int score splits and bounds using the immutable
V12 finite sum laws. The strict separation premise is exactly that the target
advantage exceeds the worst bounded residual contribution. It does not merely
require a positive target gap. Empty dimensions remain valid for finite sum
laws; a theorem requiring a target takes z:Fin n, excluding an empty target.
The weighted scores here are integer quantities, not implicitly normalized
Real probability values. Positive common-denominator clearing is a paper
interpretation for finite rationals; it does not prove the countable Real theorem.

LowerFiniteV18 constructs a minimum by finite recursion and proves attainment,
upper/lower characterization, monotonicity and constants. Its family has type
Fin(m+1), so nonemptiness is structural. It assumes primitive Scalar laws from
V12, not the desired expectation/minimum conclusions. Scalar's actual Int
instance demonstrates consistency; no generic Real/Rat kernel instance is claimed.

ExpectationContextsV18 uses actual weight functions with nonnegativity and
normalization fields. It constructs actual immutable V15 Context values,
preserves E definitionally and separately intersects with P for active histories.
Both expectation and lower context equations expose their weighted-sum/minimum
evaluators, contextual order and every observe branch. no_empty_probability
uses0<1 to reject a normalized empty vector. The actual Int Dirac family makes
the interface inhabited; it supplies no nontrivial fractional-probability model.
The finite rational Python implementation supplies that separate interpretation.

FreeMonotonesV18 defines conversion by existence of an actual free arrow.
Reflexivity and transitivity construct the category identity/composition witnesses
using supplied Closed. target_true and target_context_value bind the indicator
to conversion; family completeness uses target=b and the identity witness.
The Bool order has the correct reversed comparison of source and destination.
The actual total target Context observes all objects under P=True. Completeness
is not claimed for hidden illegal/undefined objects, omitted targets, a single
scalar or an undeclared free-arrow partition. No tensor is constructed.

## Contract, checker and limits

The75 registrations contain explicit expected types, not merely declaration
names. In particular they bind parser/wrapper and shortest semantics, actual
context domain/evaluation/tag equations, finite margins and complete target
comparison. Each inherited module is compiled from its bound source in the
fresh temporary import path before the audit; installed stale oleans are not
used as substitutes. Version/tool/source absence is CANNOT_CHECK, distinct
from a failed source or typed AUDIT.

Read the four source-valid mutation controls: all ten source modules emptied;
nontarget_minimum_iff weakened to True; strict_separation weakened to True;
and target_family_complete weakened to True. They require AUDIT-stage failure,
so a changed source must first compile. Root's integrated driver executes
these controls; this reviewer does not count reading their source as executing them.

The paper alone supplies operational partial computability/universality,
countable Kraft, Real convergence, coding-invariant full-machine envelope,
actual environmental-measure interpretation and the general Real probability
specializations. The concrete conditional example is paper plus finite exact
calculation; the general dynamic-consistency theorem remains the cited parent's.
Those claims are deliberately not smuggled into the75 kernel registrations.
No formal defect was found in the reviewed sources or explicit contract.

The final FORMAL_SCOPE_V18.md was read against these sources; its explicit
paper/kernel and Int/fractional boundaries agree. Scope SHA256:
2befc2617f175b6eb149389b1d32277ca7c9369b2ad88c49386e83e442d5d1dc.
The successor CORE/RECONCILIATION wording also preserves20/202 originals,
two qualified replacements separately and the unchanged OPEN programme boundary.

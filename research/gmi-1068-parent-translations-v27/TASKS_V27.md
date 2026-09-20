# AA5 — tasks need declared interfaces

Primary parent: Deutsch, Constructor Theory, sections1.1–1.2. Legitimate inputs
and permitted outputs form task specifications; physical repeatability and the
composition principle are additional claims, not consequences of relation algebra.
Dependencies: actual V14 total relations and V26 closed-arrow restriction.

## AA5-A — canonical task and explicit regular inclusion

For R:X→X→Prop let Dom R={x | ∃y,R(x,y)} and Ran R={y | ∃x,R(x,y)}.
Define taskR:TotalRel(Dom R,Ran R) by R on the underlying labels.
For each x in Dom R its witness supplies y in Ran R and the required relation.
Decode a typed relation I→J to ambient pairs by existential subtype lifts.
Then decode(taskR)(x,y) iff R(x,y): the forward direction drops subtype proofs;
the reverse constructs both membership proofs from the same R(x,y).

If Ran R⊆Dom S, let inc be the actual inclusion preserving the underlying label.
Its graph is a total relation Ran R→Dom S. Form taskR;graph(inc);taskS.
The decoded relation holds exactly when ∃y,R(x,y) and S(y,z): one direction
eliminates the graph equality, and the other builds the subtype witnesses and
that equality. Its declared source is Dom R and its target is Ran S.
For every x in Dom R choose an R-successor y; regularity gives y∈Dom S and
hence an S-successor z. Thus the decoded composite's domain is exactly Dom R.
Its range is only contained in Ran S; an S-input never reached by R can contribute
an output that remains declared yet is absent from this composite's actual image.
No untyped equality with canon(R;S), whose target is the smaller exact range,
follows from equal decoded relations.

## AA5-B — raw exact-range regularity is not strong partial associativity

Take distinct a,b,c,d,e and R={(a,b)}, S={(b,c),(d,e)}, T={(c,c)}.
Ran R={b}⊆Dom S={b,d}, so R;S is regular and equals {(a,c)}.
Its exact range {c} is contained in Dom T={c}, so (R;S);T is regular.
But Ran S={c,e} is not contained in Dom T, so S;T is irregular.
Recomputing interfaces as exact ranges after each multiplication therefore admits
one association and forbids the other. Relational composition itself remains
associative whenever considered as an unrestricted relation; the failure belongs
to this inferred-interface partial definedness rule. It is not a counterexample
to ordinary category associativity or a physical falsification of constructor theory.

Repair the syntax by declaring objects I⊆X and arrows actual TotalRel(I,J).
Identity and typed composition come from V14, with declared endpoints retained.
Decode of any such arrow has domain exactly I, by totality, and range contained
in J, by typing. These facts hold for compositions too; J need not shrink.
In the example, the regular adapter R;inc;S has declared target {c,e}; it does
NOT become a typed arrow into {c} merely because its actual range is {c}.
Its later join to T still lacks the required inclusion. Hence the repaired
observer does not silently preserve the formerly accepted unequal grouping.
An explicit restriction/factorization or other checked bridge requires its own
interface data and physical assumptions. It cannot be inserted as an identity
between unequal declared objects. For genuinely matching I→J→K→L, both
bracketings are defined and equal by the ordinary total-relation category laws.

## AA5-C — possible arrows under explicit closure

Supply Poss(f) on these actual typed arrows. Assume Poss(id_I) for every I and
Poss(f) and Poss(g) imply Poss(f;g) whenever endpoints match.
V26 constructs the wide subcategory with arrows {f | Poss(f)} and inherited
identity/composition. Its inclusion preserves actual operations and same-object
raw observers. Conversely any such restricted category must retain identities
and be closed under its inherited composition; these conditions are exact.
No rule infers Poss from a relation's syntax, output alternatives or normalization.
Physical feasibility of inc and approximate indefinite repeatability stay external.

Closure is one-way. In the Bool-function monoid, {id} contains identity and is
closed, yet swap is excluded and swap;swap=id is included. Thus a possible
composite does not force possible factors. Conversely {id,swap,const0} fails
closure because const0 followed by swap is const1, which is absent.
These are actual finite composition statements, not empirical impossibility laws.

The inherited V26 resource category includes boundary balances as objects and
uses exact cost/residual equations. Forgetting balances can revive a previously
failed join; successful typed path projection still holds. Its use illustrates
why declared inputs include resource state. It does not show a depleted device
is indefinitely repeatable, derive its costs, or identify physical substrates.

## Translation limit and falsifiers

Task alternatives specify allowed outputs, not their frequencies; arbitrary
behavior outside legitimate inputs is not an additional task arrow.
Equality of decoded pairs need not imply equality of declared target interfaces.
A test that only compares pairs can miss this loss, so both endpoint lists and
actual V14 composition must be checked. Empty legitimate input is allowed;
a nonempty input with no permitted output cannot form a TotalRel Task.
The finite oracle treats raw inferred regularity and declared-interface composition
as different operations and tests both, including the five-label failure separately.

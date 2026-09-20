# Freeze V27 — source-specific parent translations

Preregistered before V27 implementation and experiments; no successful outcome is asserted by this freeze.
Package: `research/gmi-1068-parent-translations-v27`; #1068 governs, #833 supplies historical parents.
Only original **GMI2-R1-009 — translate to parent process formalisms** is eligible, conditionally.
Use the actual AJ1 PARENT_COMPARISON seven identities/order/native/additional roles as the bounded parent set.
They are categorical_process_theory, operational_probabilistic_theory, relations, stochastic_kernels,
labelled_transition_systems, coalgebra, constructor_theory. Preserve its no-unique-ontology ceiling.
Do not import AJ1's parallel-composition requirement into the later R1 sequential minimum.
This round follows the merged V26 result; preserve every other original field and the two qualified replacements.
Success would change33/189 originals to34 fulfilled/188 unresolved, with2 qualified/186 active unresolved.
Whole R1 remains OPEN and other whole-round dispositions unchanged; a seven-row ledger alone earns nothing.

## AA1 — actual relation-LTS, powerset coalgebra and finite paths

Fix a label type A. An LTS on S is R:S→A→S→Prop, not a multigraph with duplicate edge identities.
Define successors_R(s)={(a,t)|R(s,a,t)} and relationOf(alpha)(s,a,t)=alpha(s)(a,t).
Prove both actual extensional roundtrips, including empty types; retain labels and all transition triples.
Define powerMap(f,U)={(a,f(t))|(a,t)∈U} by an explicit existential and derive identity/composition laws.
Prove the exact coalgebra square powerMap(f,successors_R(s))=successors_Q(f(s)) iff BOTH:
forward: R(s,a,t) implies Q(f(s),a,f(t)); back: Q(f(s),a,u) implies some t with R(s,a,t),f(t)=u.
Prove equivalence with graph(f) bisimulation for this powerset model, not with mere trace equality.
The actual V11 generator G_R(s,t) is {a:A | R(s,a,t)}; singleton generators recover R.
Use actual V11 Path.category; bind nil/cons/append/evaluation and recursive label-list observations.
Forward maps actual generators and paths, preserving labels and endpoints. Proofs do not create extra edge IDs.
Given Forward and Back, every target Path p from f(s) to u has a source endpoint t and source Path q from s to t,
with dependent bundled equality (f(t),mapPath(q))=(u,p): lift THE SAME path, not only its trace.
No state injectivity or unique/computable/global infinite-path lifting is assumed.

## AA2 — the category of whole systems is a different level

Define an actual Set endofunctor by its type map, function map and identity/composition laws.
Systems are (carrier,step:carrier→F(carrier)); Hom is a function satisfying the actual coalgebra square.
Construct identity/composition and derive Category laws by extensionality, not an assumed category conclusion.
Construct the actual function category and faithful forgetful ProcessMap; bind carrier/function operations.
Instantiate the powerset functor and connect this Hom condition to AA1, retaining the level distinction:
whole systems and their homomorphisms are not individual transitions or within-system execution paths.
For F(X)=Bool×X use two singleton systems with different output bits and identical underlying carrier.
They are distinct structured objects. The literal unequal-Empty pair fails in their system category and
succeeds after faithful forgetting. Reuse actual V26 collapsed_empty_witness; object injectivity is a separate condition.
The tag-preserving target retains System objects and ALL carrier functions as Hom; its object-identity forgetful
map gives actual V26 raw transport. No fullness/equivalence or equivalence-invariant raw syntax is claimed.

## AA3 — actual relational and normalized-stochastic parents

Construct arbitrary Rel(A,B)=A→B→Prop, equality identity and existential composition; derive actual laws.
Include empty relations, including inhabited→empty; these need not be pointwise total.
Construct generic actual V14 TotalRel category and faithful same-object inclusion into Rel, binding operations.
Reuse actual V14/V26 finite normalized matrices, Dirac/graph/support maps and rational support collision.
Finite matrices are a declared specialization of stochastic kernels; arbitrary measurable integration is not proved.
For a supplied standard monoidal/symmetric process theory, the sequential reduct retains its actual
objects/arrows/id/composition. Standard-definition extraction is parent-owned PAPER, not tensor reconstruction.

## AA4 — classical subnormalized events and outcome-labelled tests are mandatory

Retain actual V14 Weight, including one_ne_zero, zero-sum-free addition and no zero divisors.
Add explicit mul_comm, a primitive partial order, bottom0, and monotone addition/left-right multiplication.
No matrix inequality, normalization or event-category conclusion may be an interface field.
Derive finite-sum monotonicity and rowSum(p;q)=sum_j p_ij rowSum(q_j)≤rowSum(p_i)≤1.
An Event is an actual finite matrix with row sums≤1; derive Category laws from actual matrix operations.
Identity is normalized; zero events exist for every dimension, including inhabited→empty.
Actual normalized Kernel embeds faithfully; its inverse on the normalized Event slice has identical coefficients.
A Test has a finite outcome shape, distinct outcome identities and one matrix per outcome, with normalized aggregate.
Use finite shapes generated by Fin n and Cartesian product, with explicit finite/nested sums and derived sum laws.
Prove each test component is subnormalized. Compose tests with actual outcome PAIRS and actual matrix products.
Prove aggregate(test composition)=matrix composition(aggregates), hence aggregate normalization.
Do not discard zero events, relabel equal events as one outcome or individually normalize event rows.
A supplied injective external outcome encoder is retained and paired; no adaptive test interface is inferred.
Pair closure does not supply a global Category of labelled tests: different product bracketings need explicit reassociation.
Zero-outcome tests on inhabited inputs are impossible by inherited one_ne_zero; empty inputs remain covered.
Basis preparation/effect contexts extract actual coefficients; derive classical event separation and closed scalar values.
Kernel algebra is over the stated ordered carrier; Nat demonstrates consistency only. General nonnegative Real/Rat
interpretations remain PAPER unless actually instantiated; exact Fraction and concrete rational controls are separate.
CDP general systems/events/tests and ancillary equivalence give the parent interpretation, not a quantum derivation.

## AA5 — task interfaces, regularity failure and conditional possible-arrow restriction

For ambient R:X→X→Prop define Dom R and Ran R by actual existential domain/range.
Construct taskR:TotalRel(Dom R,Ran R) retaining R and actual subtype labels; decode recovers R exactly.
Regular(R,S) means Ran R⊆Dom S. Its witness gives an explicit inclusion function and actual graph relation.
Prove decode(taskR;graph(inclusion);taskS)=R;S and its legitimate domain is exactly Dom R.
Its declared target remains Ran S; decoded range may be strictly smaller, so do not equate it untyped with canon(R;S).
Required analytical counterexample on five distinct labels: R={a→b},S={b→c,d→e},T={c→c}.
R;S and (R;S);T are regular, but S;T is not, since e is outside Dom T.
Thus recomputing exact-image interfaces does not give strong partial associativity; do not claim it does.
Repair: category objects are DECLARED interfaces I⊆X and Hom=actual TotalRel(I,J).
For any typed task I→J, decoded domain is exactly I and range is contained in J, not necessarily equal.
Composition retains declared endpoints even when its actual image shrinks. Explicit graph inclusions connect
compatible distinct interfaces; a later restriction needs its own checked bridge, not silent endpoint replacement.
Choose a possibility predicate containing identities and closed under actual typed composition, then use V26 restriction.
Neither physical feasibility of the inclusion nor approximate repeatability nor the chosen possibility laws are derived.
Possible composites need not have possible factors; retain the actual V26 battery/state-boundary lesson separately.
Task alternatives are permitted outputs, not an empirical transition distribution or behavior outside legitimate inputs.

## Exact finite calibration and deterministic ordering

All numbers below are planning algebra requiring measured reconciliation after a committed freeze; no outcomes claimed.
A. One fixed label, state counts n,m=0..2, every transition subset, every total state map.
Candidate total sum_(n,m)2^(n²+m²)m^n=1143, with0^0=1; model counts by size are1,2,16.
Order n,m ascending; relation bits lex(source,label,target), source then target masks, maps lexicographic tuples.
Reject duplicate input triples; present triples get sorted stable edge IDs, and repeated path occurrences remain.
Classify forward/back independently. For each forward map, test all valid source paths length0..3 and compatible
path pairs with total length≤3: map actual edge IDs, endpoints, labels and concatenation against independent walks.
Order lengths ascending, then lexicographic state sequences from each ascending start; primary labels are fixed.
For each true hom and each source start, enumerate all target paths length0..3 from its image and ALL source lifts.
Check exact mapped paths, not just equal words; measure actual source/target/path-pair/lift counts separately.
Named controls outside primary: dead-state→loop; nonvacuous extra successor; two-label label-swap failure
and explicit label-renaming revival; a.(b+c) versus a.b+a.c equal traces/different branching;
Bool-output singleton-system forgetting loses raw Empty failure, while retained structured tags preserve it.

B. Dimensions n,m=0..2, row-major exact entries ordered0,1/2,1. Subnormalized row counts are
r_m=binomial(m+2,2)=(1,3,6); sum_(n,m)r_m^n=59 events,2117 composable pairs,79401 triples.
Order dimensions then row-major coefficient tuples; composable pair/triple records follow corpus-index lex order.
An independent trajectory oracle sums products over intermediate states, never using production composition.
Check literal coefficients, associativity, identities, subnormal bounds, empty dimensions and normalized-slice agreement.
Composites retain arbitrary exact rational values, with no requantization to the generating grid.
Two fixed distinct outcomes0,1 are MANDATORY: q_m=binomial(2m+1,2)=(0,3,10),0^0=1;
sum q_m^n=125 tests and12271 composable test pairs. Order outcomes before row-major entries.
Check every paired-ID event, aggregate equality/normalization, zero events and complete outcome retention.
Named [1/2];[1/2]=[1/4] rejects conditional renormalization; equal-aggregate tests with different labelled
probabilities reject test erasure. Basis preparations/effects check separation, with empty-dimension cases explicit.

C. All16 relations on fixed substrate{0,1}, masks over(0,0),(0,1),(1,0),(1,1), all256 pairs/4096 triples.
Independent tuple-set composition checks exact domain/range and regular-pair inclusion/decode bridges.
For adjacent regular triples check both bracketings and inherited associativity; measure regular-case counts.
The five-label nonassociating-regularity control is separate; test declared-interface retention and explicit bridge repair.
Enumerate four total Bool functions as tuples(0,0),(0,1),(1,0),(1,1), all16 possibility subsets in mask order.
Check identity retention and all16 ordered function pairs per subset (256 checks), no inferred physical possibility.
{id,swap,const0} fails closure; {id} is closed while excluded swap;swap is included. Preserve this converse failure.
No RNG or unregistered primary enlargement. Generic theorem proofs and these finite correspondences stay distinct.

## Falsifiers, exact proof registration and source custody

Strict validation covers type aliases, dimensions, labels, duplicate outcomes/triples, all unused entries,
negative/oversized event rows, unnormalized tests, ill-typed composition and malformed later path suffixes.
Every mutation family has a valid actual baseline. Mutate actual maps/edges/destinations, event coefficients,
outcome identities, task domains/inclusion maps and coupled outputs; the supplied source structure stays fixed.
Fresh Lean4.19 isolated replay binds actual constructors, relations/matrices/sums, subtype labels and theorem types.
Four source-valid mutants: all sources empty; HomEquation↔(Forward and Back) leaf→True;
test aggregate-composition AND normalization leaf→True; actual regular-task inclusion/decode leaf→True.
Changed sources must compile before typed AUDIT rejection. Register same-target-path lifting, actual system
category laws and collapsed-Empty control independently, not merely their declaration names.
Mandatory module/coverage guards, exactly seven original parent-row identities/native/additional/status
records, actual row mutation controls, normal/-O equality and inherited receipt dereferencing are required.
Unavailable prerequisites are CANNOT_CHECK; checked-invalid is separate. Ledger schemas cannot certify prose truth.
Each result/parent row states premises, actual map/decoder, preserved operations/observer, forgotten information,
inverse/faithfulness scope, falsifier, strongest parent and PAPER/KERNEL/FINITE boundary.
All old snapshots and V16 qualified records remain immutable; derive current counts from the successor chain.

## Fifteen explicit claim boundaries

1. Only original009 is eligible; no whole-R1, unique ontology or full-GMI promotion.
2. The bounded seven-family ledger is a declared parent set, not every possible process formalism.
3. Sequential reducts forget supplied enrichment; they do not reconstruct tensor or symmetric structure.
4. Relation-LTS triples omit duplicate multigraph-edge identities; richer provenance needs a different interface.
5. Generator-labelled paths retain histories; reachability/trace quotients need not recover transitions or branching.
6. Finite same-path lifts are existential, not canonical computable selectors or an infinite-path theorem.
7. Whole-system homomorphisms and within-system execution paths are different arrow types.
8. Faithful carrier forgetting may collapse structured objects and revive raw failed joins.
9. Arbitrary Rel and TotalRel differ; empty outputs are not silently prohibited in the former.
10. Finite normalized channels are neither all subnormalized events nor all measurable stochastic kernels.
11. Labelled tests retain zero events and outcome IDs; no adaptive-test or general ancilla-equivalence theorem follows.
12. Ordered-weight algebra and concrete rational calibration do not fabricate a general Real/Rat kernel instance.
13. Inferred exact task ranges can violate strong partial associativity; declared interfaces are the explicit repair.
14. Possibility/regular-bridge feasibility/repeatability/physical resource laws remain supplied assumptions, with no converse-factor inference.
15. Classical parents own these mechanisms; integration and finite evidence imply neither originality nor general AI derivation.

## Primary ownership and input custody

Rutten Example2.1/Theorem2.5, printed9–13: https://ir.cwi.nl/pub/48/0048D.pdf
CDP §§II.E–F, pp6–7: https://arxiv.org/pdf/0908.1583
Deutsch §§1.1–1.2, pp3–6: https://arxiv.org/pdf/1210.7439
Mathlib Endofunctor.Algebra: https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Endofunctor/Algebra.html
Actual V11 paths, V14 relation/matrix/rational proofs and V26 functor/restriction bridges are reused, not reinvented.
SOURCE_PINS_V27.json binds29 Lean and12 Python sources with complete import closure, original R1 freeze/identity,
AJ1 THEORY/PARENT_LEDGER/PARENT_COMPARISON/historical RESULT, current V26 receipt/snapshot and V16 authority.
The54 exact input hashes include only real source artifacts; AJ1 has no package-local freeze.
SOURCE_PINS_V27.json SHA256: 1487da39c95784ed86fadeef497fb0a1226a3395777cf7c9db0a72fdee2b14f2.
These two preregistration files alone are committed before implementation. Both remain immutable.

## Production and test interfaces

Production modules are core_v27, lts_v27, events_v27, tests_v27 and tasks_v27; split only to keep files≤200lines.
Cache actual V11 paths, V14 kernels/relations and V26 core/functor/restriction/resource modules with class identity.
Public containers are exact tuples, dimensions/indices exact int, scalar data exact Fraction; validate all entries.
Outcome IDs are natural atoms or recursively ordered binary pairs, preserving nested pair structure and zero events.
Python Test accepts checked Event values; generic Lean Test starts from matrices and derives their component bounds.
Task endpoints retain sorted external labels, including unused declared output points, across actual V14 composition.
Fifteen unittest methods across ten modules: lts2, events2, tests1, tasks2, controls1, hostiles2, custody2,
parent_ledger1, coverage1, kernel_guard1. The four source-valid proof mutants belong to kernel_guard.
Actual measured module/key/count records are sealed before final normal/-O receipt replay; no classified totals are assumed.

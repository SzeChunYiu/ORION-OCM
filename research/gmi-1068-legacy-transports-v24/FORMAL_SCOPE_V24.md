# V24 formal scope

Only the source-keyed R3-009 transport scope is covered.
This file separates kernel mathematics from the executable legacy refinement.
It does not establish a complete theory, unique preference, or a new parent result.

## Replay and assumptions

The fresh checker compiles seven immutable V12/V15/V17/V20 sources and
thirteen new modules with Lean4.19.0, Std, and warningAsError.
The static proof contract contains138 explicit typed registrations.
Every registered declaration is checked by assignment to its exact type,
followed by an axiom inspection. No runtime type discovery is used.
Source-valid replacement tests must compile SOURCE and fail AUDIT.

Scalar theorems use the existing V12 primitive ordered commutative ring laws.
The actual Int instance is freshly replayed and its operations are bound.
No generic rational or Real instance is manufactured from finite Fraction tests.
Paper rational/real specialization requires a genuine model of those laws.
Logic is standard Lean logic; some definitions/proofs use classical choice,
propositional extensionality and quotient soundness, as printed by the audit.
No additional mathematical axiom, placeholder or unsafe proof is introduced.

All domains, admissions, orders, profiles, losses and weights are declared.
The proofs do not learn those ingredients or establish empirical meanings.
Generic predicates can be undecidable; these mathematical images are not
algorithms enumerating all histories or solving unrestricted selection.

## X1: actual partial Context and selected images

ImageTransport uses actual V15 Context and actual V20 Attained.
Image is evaluated on admission P intersect the evaluator-defined domain.
Projected retains the explicit selected-history predicate B as well.
The selected/full projected-image equality holds exactly when every active
full history has an active selected witness with the same projected value.
The theorem is slightly more general than B subset P intersect E:
it explicitly intersects B with that domain rather than trusting the premise.

terminal_sufficient requires factorization only on active histories and
coverage of their terminals by active selected histories.
injective_boundary requires injectivity only on the active domain.
It then characterizes when image equality forces every active history to
be selected. Neither theorem derives injectivity or terminal sufficiency
from endpoint equality alone.

ProfileContexts constructs the actual record containing capability,
resources, provenance, terminal and history, and proves history retention.
Its code Context evaluates to the history/code itself; an explicit decoder
postcomposes it to the profile Context. E, values, order and all outcome
tags are bound. The generic partial Context theorem also permits genuinely
partial dependent evaluators; the profile constructor accepts a declared
total profile function restricted by E.

## AF: rich histories, erasure and actual Context bridges

AFErasure maps endpoint/edge-word to endpoint/action-word using List.map.
An edge carrier may be instantiated by source/outgoing-slot pairs.
Validity and horizon belong to declared admission/domain predicates;
this file does not prove that every arbitrary edge list is a valid path.

The old-profile constructor retains capability, step length, two Boolean
presence coordinates, provenance predicate, endpoint and action-word.
Consumed provenance is initial provenance OR membership in any action's
registered tags. Its empty/cons laws and repeated-event idempotence are
kernel checked. Action labels index provenance, so repeated labels share tags.
Exact string rendering and sorted finite-set serialization are executable
refinement evidence, not equality between Lean predicates and Python strings.

AFContextBridge.fullContext is the ERASED full-history Context:
its domain is raw histories, but values are projected legacy profiles.
full_erasure_image proves that its image equals the old-profile image of
all erased active raw histories. selected_old_image uses the supplied
selected endpoint/action-word roster without choosing an edge-path decoder.

RichAFContexts.richContext explicitly evaluates to
(raw endpoint/edge-word, projected legacy profile).
Its order is equality on these full rich values, matching the identity-code
comparison in the finite adapter. Distinct raw histories remain distinct.
Actual V17 postcompose with Prod.snd and the declared old order s equals
the erased fullContext. Both image and three-way outcome transport are proved.
Projection does not reflect equality of rich histories; a repeated-label
erasure collision is kernel checked.

The exact legacy H_BFS is supplied by immutable reachable/gamma_profiles.
The Lean generic image theorem does not implement or verify that BFS.
Path-lift induction, simple-path horizon coverage, selected neighbor order,
dictionary serialization and finite edge-history enumeration are paper plus
independent actual-call calibration. No hidden legacy horizon/resource/verifier
parameter or all-walk enumeration theorem is claimed.

## X2: every candidate identity and declared prices

CandidateContexts evaluates each ID to (ID,resource vector).
Its actual preorder reverses coordinatewise resource comparison.
maximal_ids proves full maximal attained values projected to IDs equal
the declared Pareto predicate, retaining every ID at a tied resource vector.
pareto_nondominated derives the equivalent absence of an active candidate
with coordinatewise weak improvement and a strict coordinate.

The active predicate is viability AND reachability when requested.
FinitePreference uses an actual predicate filter and V20 frontier.
For a complete active roster, membership equals the full Pareto predicate.
Lists can repeat identical IDs; set-membership mathematics is unaffected.
The strict Python interface instead requires unique nonempty IDs and returns
canonical sorted results; list length is not inferred to equal set cardinality.

PriceContexts evaluates (ID,dot(weight,resource)), with reverse scalar order.
maximal_ids equals the full argmin predicate, including all ties.
Strictly positive prices imply Pareto efficiency via the actual V12 dot_strict.
No converse that every Pareto point is a supported scalar optimum is proved.
No preferred weight, tie-break or deterministic winner is inferred.

Generic scalar proofs permit dimension0 and arbitrary scalar resources.
The legacy valid-input specialization requires dimension>=1 and nonnegative
exact rational resources. This stronger concrete contract is not erased.
Empty active sets have no Pareto/argmin member.
Legacy terminal strings and strict new unused-input validation are finite
API evidence; they are not claimed as kernel parser semantics.

## X3: partial losses and one shared plan

PlanContexts uses actual partial evaluators on declared E and admission U∩P.
Values are (plan ID,loss), with the declared loss preorder.
feasible_image equates P/E/threshold feasibility to the ID projection of
the target-restricted attained image. Illegal, undefined and VALUE equations
are registered separately; no default loss fills absent evaluations.
total_specialization recovers the original total-loss source formula.

An alternate total identity Context places feasibility in admission.
identity_feasible proves equal feasible plan sets only; it does not claim
identical illegal/undefined diagnostics for the two representations.

CommonPlans fixes a shared plan universe U and uses one universal quantifier
over selected histories. Compatibility is existence of one common plan.
The empty history family yields U, so compatibility still requires U nonempty.
Mapped intersection equality requires an injective common plan map and
explicit restriction to its mapped ambient universe, including empty families.
Loss projection need not be injective and does not preserve these intersections.

## Controls and remaining refinement boundary

Kernel controls establish pairwise-but-not-joint Fin3 feasibility;
equal scalar loss images with incompatible plan IDs; the empty-index
mapped-universe failure; zero-price dominated ties; negative-price reversal;
duplicate-vector ID preservation; unattained coordinate minima;
same endpoint with distinct profiles; repeated provenance idempotence;
and noninjective edge-word erasure.

All exact constructor, domain, order, evaluator, image, feasible/common-plan,
filter and named-control operations are included in static registrations.
ProofTargets supplies the final independent selected_projection_contract,
preference_contract and plan_intersection_contract leaves in that order.
Python legacy calls, strict validation, oracle corpus, traversal correctness,
serialization and receipt coverage remain independently checked finite evidence.
SEL is a downstream source-specific interface with supplied structure.
No universal primitive or blanket historical-theorem substitution follows.

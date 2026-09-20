# V21 preregistration: execution and resource-indexed attainability

Control plane #1068; historical programme #833.
Parent: 825f7755574551eec05ebd3b424d3b155eabdfaf (V20, #1116).
This freeze precedes all V21 implementation, experiments and outcome files.
Planning arithmetic below is not observed coverage.

## U1 — actual successful finite execution

Use immutable V8 Machine.next, run and budgetMachine; construct weighted
finite-word execution Option(endpoint,Nat cost), with actual empty/cons equations.
Prove concatenation through the actual intermediate endpoint, adding costs.
Construct endpoint execution of actual budgetMachine; for every s,w,b,
success at (t,r) iff unrestricted weighted execution returns (t,c),
c<=b and r=b-c. Empty words cost zero and missing edges stay missing.
On success, complete budgeted and unrestricted V8 Responses coincide.
Budget concatenation uses residual after the prefix, never a fresh allowance.
Derive larger-budget success with the same physical endpoint and residual b'-c;
distinct residual states are not equal. Arbitrary kernel state/action types,
including empty types, are allowed; Python V8 keeps its nonempty constructor.

## U2 — actual fixed partial-context images

Use actual V15 Context over raw finite histories (start,word); a declared
selector restricts histories from x. Unrestricted admission is original P
AND selection AND physical success; budget admission also requires cost<=b.
Preserve E, ambient evaluator and value preorder; bind all observation cases.
Define actual images for selected families and all finite histories.
Prove image inclusion for nested selectors with fixed admission/evaluation,
then operational budget nesting from U1 rather than from a numeric label.
The all-finite-history image equals the union of bounded-length images;
union over all Nat budgets equals the unrestricted finite-history image.
Neither arbitrary finite lengths nor those unions supply infinite traces,
limit points, probabilities or asymptotic attainment.

## U3 — joint information, resource response and capability

Construct J={(c,v): selected physically successful h, P(h), E(h),
actual execution cost c and actual evaluated value v}.
Prove A_b={v: exists c<=b,(c,v) in J}; capability(b,G) iff such a
witness has v in the declared target G. G may be arbitrary: this is
image inclusion, not V20 upward-goal pruning.
Keep both original resource meanings: declared coordinate projection rho[A]
and indexed admission b->A_b. Bind projection to actual evaluated composition.
Neither rho nor the joint cost/value pairing is inferred from a bare image.
Construct least Nat target cost, or None for no successful finite witness.
Prove exact capability cutoff and a history attaining every finite cutoff.
This is a possibly noncomputable characterization, not a shortest-path
algorithm for arbitrary history predicates or evaluators.

## U4 — ordered accumulation and its assumptions

Declare a preorder, associative cost product, identity, and monotonicity in
both arguments; commutativity, positivity and subtraction are not implicit.
Construct actual weighted-word folds and prove ordered concatenation.
Cumulative execution checks initial spent<=capacity and every later prefix.
Prove capacity nesting with fixed physical transitions and cost assignment.
With nonnegative edge increments relative to identity, prove prefix success
iff physical success and final aggregate affordability. Bind the empty-prefix
case, including initially unaffordable states; do not assume all capacities positive.
Relate Nat cumulative accounting to U1's actual residual implementation.
Give Nat addition, vector addition, max and mixed time-add/peak-max readings.
Signed addition falsifies final-total-only admission; maximum prefix demand
revives that case. It does not change V8's Nat semantics.
No automatic unique residual or least scalar capacity exists in general.

## Eligible unchanged original records

GMI2-R3-001 — formalize contextual attainability.
GMI2-R3-002 — formalize budget restriction.
GMI2-R3-003 — prove monotonicity.
GMI2-R3-005 — derive capability projection.
GMI2-R3-006 — derive resource response.
GMI2-R3-010 — mechanize attainability lemmas.
Freshly replay original Attainability.lean's actual Attain, attain_mono,
maximal_is_attainable and impossible_means_no_target; bridge its actual image
to V15/V20 partial-context images. No needed history identity is erased.
Do not close R3-007 (barriers), R3-008 (regime changes), R3-009 (legacy transports),
or any other original record. Preserve V20's R3-004 evidence unchanged.
If all six eligible scopes earn closure:27 fulfilled/195 unresolved originals,
two existing qualified replacements separately leave193 active unresolved.
R3 whole remains stale; no other whole-round promotion or new amendment.

## Independent finite calibration

A: actual V8 n=1,2; one action; observations None,0,1; outputs0,1; costs0,1,2;
every absent/present output/cost/destination assignment. Every start, words
lengths0..4, capacities0..8. Planning:1542 machine instances,15315 physical
histories,137835 budgeted cases.
B: n=1,2; two actions; observations None,0,1; output0; costs0,1;
all absent/present cost/destination assignments; lengths0..3, capacities0..3.
Planning:5652 instances,169155 histories,676620 budgeted cases.
These corpora overlap; their sum is not a distinct-model count.
Every word cut tests weighted composition and actual residual continuation.
Independent literal traversal records cumulative prefixes and exact stopped
traces; compare actual V8.run and actual budget_lift/run, not two sum filters.
Measure successes, failures, traces, endpoint/residual and cut checks in loops.

Context corpus: n=0..3 distinct singleton-action histories; one-state machine
has action i of cost i/output0 or absent, with all physical-presence masks.
For n=0 use one unused absent action. Value size m=0..2, every preorder,
all P flags and None-or-value assignments; E is exactly the defined domain,
including defined illegal ambient evaluation. Every selector, capacities0..2,
all target subsets and every declared coordinate map rho:m->{0,1}.
Planning:8210 model/contexts,62654 selectors,187962 budget images.
Independently build J/witnesses; check restricted P, preserved E/evaluator,
all tags, inclusion/nesting, target cutoffs and finite union at maximal cost.
All-Nat union and minimum existence require proof, not this finite range.

Ordered resource-only words lengths0..3, initially identity:
Nat addition alphabet0,1,2/capacities0..6:280 planned cases;
Nat^2 addition alphabet{0,1}^2/capacities{0..3}^2:1360;
Nat max alphabet0,1,2/capacities0..2:120;
mixed time-add/peak-max alphabet{0,1}^2/capacities{0..3}x{0,1}:680;
signed addition alphabet-2,-1,0,1,2/capacities-1,0,1,2,3:780.
Test every cut and comparable capacity nesting; positive cases compare
prefix/final feasibility, signed cases compare maximum prefix demand including0.
Include positive noncommutative matrix-product control AB!=BA.
All counts must be measured; seal exact coverage only after execution.

## Countermodels, revival and malformed inputs

Two costs1,1/allowance1: resetting each segment fails; retain residual.
Signed +2,-2: final total fits but first prefix fails; retain prefix demand.
Peak costs5,5 fit capacity5; blind subtraction wrongly rejects.
Opposite cost/value pairings have equal marginals and different target cutoffs;
relabelled target changes capability with unchanged J.
Budget-dependent empty-history value b gives singleton{b}, breaking nesting;
fix the evaluator to revive it. Non-nested labelled restrictions also fail.
A length-two-only evaluator at an unchanged endpoint needs its actual loop;
retain history or sufficient observer state instead of erasing the witness.
Vector target costs(1,0),(0,1) have incomparable minima, no least vector.
Real costs1+1/n have unattained infimum1: paper proof, no finite extrapolation.
Undefined observation, absent edge, admission rejection and evaluation failure differ.
Validate later actions, unused entries, dimensions and capacities before
short-circuiting, including failed prefixes and empty selected families.
Reject duplicate set indices, Bool/integer aliases and malformed tuple shapes.
Valid empty images, checked-invalid inputs and unavailable sources stay distinct.

## Proof, review and custody

Pin Lean4.19.0; isolated SOURCE compilation, exact typed AUDIT and axiom scan.
Bind constructors/recursion/fields, not only theorem conclusions.
Source-valid mutants must compile SOURCE then fail AUDIT, including actual
residual equivalence, joint filtration and generic prefix/final theorem leaves.
Independent oracle cannot call production to compute its expected answer.
Normal/optimized integrated receipts must match bytes; exact coverage guards,
real no-alarm tests and hostile/coupled evidence mutations are mandatory.
Bind every science source/review in RESULT; successor preserves all untargeted
original fields and immutable V16 qualified authority. Use actual-target-base
CI custody and gate publication on new exact-head success.
Modular docs/code <=200 lines; raw receipts may exceed. No novelty is promised.

## Primary parents

Mohri, Semiring Frameworks and Algorithms for Shortest-Distance Problems,
intro and §§1–2: https://cs.nyu.edu/~mohri/pub/jalc.pdf
Path products are classical; aggregate distances need not have path witnesses.
Mohri, Weighted Automata Algorithms §§1.2/2:
https://www.cs.nyu.edu/~mohri/postscript/hwa.pdf
Dijkstra (1959), Problem2/Remark1: https://ir.cwi.nl/pub/9256/9256D.pdf
No endpoint-only solver is imported for arbitrary history contexts.
Fritz, Resource convertibility and ordered commutative monoids, Def3.1:
https://doi.org/10.1017/S0960129515000444
Ordered combination alone gives neither positivity nor subtraction;
noncommutative sequential costs are an explicitly adapted interpretation.
These parents own the classical mechanisms; integration is not a breakthrough.

## Immutable input SHA256 bindings
- `research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json` `4cc262d491fbcdccf2b4c8656e80dcdb06e1795344500e46ac980ca09a679574`
- `research/gmi-1068-r3-contextual-attainability-v1/FREEZE_V1.md` `e9f25acb58dc24f2bda8ae6dfeab4e78660f3e1ffc664638b74b76d7f5557209`
- `research/gmi-1068-r3-contextual-attainability-v1/THEORY_V1.md` `6298fda4b6a2f4feb63c98f103c69ffea2602ec86e58fbbfb7dcad06c4aa8c9a`
- `research/gmi-1068-r3-contextual-attainability-v1/Attainability.lean` `1c34238b76315a1420566ec41efd5088ab1ff8a4a2930cd362cec08d9608f686`
- `research/gmi-1068-continuation-v8/ContinuationV8.lean` `daca89f4bb32898b285a993ad5de777acbcbcffbf10b0c888b10dfc8accf4da4`
- `research/gmi-1068-continuation-v8/continuation_v8.py` `16f5ba400ea3475b1fc7f58a594ca283aa9d8cf2710095a56a81b9f96c146f02`
- `research/gmi-1068-partial-context-v15/PartialContextV15.lean` `332dcfb63304d5668800ea21f09795c2d92267989291ffe35d9e38ea2db0edf5`
- `research/gmi-1068-partial-context-v15/context_v15.py` `75c62203c8ae61ddce1081f9deaf463dfce6965bb160086a8e21adfe787fcd2f`
- `research/gmi-1068-context-specializations-v17/core_v17.py` `2036aee04274bfdd29cd0caa300ace47b066ac958c58043a0290105dbfae107f`
- `research/gmi-1068-frontier-simulation-v20/core_v20.py` `3f1cc388ddf559b5ae7eb45ff6f20e27affbf7ba4285fb9287039e02c35d3ac3`
- `research/gmi-1068-frontier-simulation-v20/FrontierOrderV20.lean` `ec4a10f31365a2e304dd12b599e7c0ac83e3996c31e3a6b6f7307252e8d24bf4`
- `research/gmi-1068-frontier-simulation-v20/AttainedFrontierV20.lean` `c10d3c4203fbde6c50dced422026020180f9d0514b6c44c144dffbaa1f31c890`
- `research/gmi-1068-frontier-simulation-v20/RESULT_V20.json` `bff15739317f2bf4b905099e51dda0712a66ae16c5c8e2364d20da54b69a3949`
- `research/gmi-1068-recursive-audit-v20/SCOPE_SNAPSHOT_V20.json` `fa4a12ecbac168d5cb8bbfc2a6eee95fa60e72eea4408fcd8b9267d486d130ba`
- `research/gmi-1068-recursive-audit-v20/CURRENT_ACCOUNTING_V20.json` `f1065f62509ee7dc137b27cec9971ad7b45274d854f1a6e4f4af84121ba782c5`
- `research/gmi-1068-corrected-targets-v16/RESULT_V16.json` `18bea5c6f85b4fcc91c40c53cbf63df59c38d70e9e839efc4585f6640497ad1a`
- `research/gmi-1068-amendment-governance-v16/AMENDMENT_LEDGER_V16.json` `e1cc2d2dbc10171407577889f75ac531c30cf09eab224fc3823f3931c5048618`
- `research/gmi-1068-amendment-governance-v16/RESULT_V16.json` `ed491fab2cd0b69fb4ee845b82e349c79ff0d70f0dbc1d312ee0755645437de4`

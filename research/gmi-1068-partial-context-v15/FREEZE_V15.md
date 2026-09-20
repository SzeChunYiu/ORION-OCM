# V15 freeze: partial contexts and general AJ7 separation
Control plane: #1068; #833 remains historical evidence.
Parent:459480807bfcc613696508098ed9f95c1cf00bc8, PR#1110 pending.
Preserve this preregistration ancestry; merge successful V14 main before publication.
Only eligible original atoms and exact titles:
- GMI2-R2-001: formalize context/preorder.
- GMI2-R2-004: generalize AJ7 countermodel.
Read the original R2 freeze and checklist; do not silently redefine its context.

## Assimilated parents and disclosed planning
Partial maps retain an explicit defined domain:
https://homepages.inf.ed.ac.uk/gdp/publications/Ax_FPC.pdf
Preorder antisymmetrization is classical:
https://stacks.math.columbia.edu/tag/002Z (Remark4.21.3).
Mature implementation inspected: Mathlib/Order/Antisymmetrization.lean.
This is a construction reference, not an installed Lean4.19 dependency.
V9 supplies the generic fiber criterion and no_recovery_of_collision;
V11's old registrations do not cover the new use merely by their existence.
Reward-learning ambiguity is a comparison parent, not the proof of this claim:
https://ai.stanford.edu/~ang/papers/icml00-irl.pdf

The following constructions and corpus counts were derived during planning.
29 preorders on three labelled values and 125 three-history status/value
assignments give 3625 proposed contexts. These are disclosed design counts,
not unseen empirical discoveries. No outcome-bearing V15 code precedes freeze.

## O1: partial context, admission and induced comparison
Use arbitrary ambient histories H, admission P⊆H, evaluation domain E⊆H,
a preorder on W, and an actual function ν:E→W.
Observe ILLEGAL if h∉P, UNDEFINED if h∈P but h∉E, and VALUE(ν(h)) otherwise.
Restrict to D=P∩E to recover the original partial evaluator on admitted
histories: D⊆P and ν restricted along D→E.
Evaluation outside admission, when the ambient evaluator has it, does not
turn that history into an admitted/evaluated observation.

On D define x≼νy iff ν(x)≤ν(y). Prove reflexivity and transitivity.
Define mutual comparison x~y iff x≼νy and y≼νx.
Prove it is an equivalence, comparison is independent of representatives,
and the quotient relation is reflexive, transitive and antisymmetric.
Prove quotient comparison agrees exactly with comparison before quotienting.
Do not extend undefined comparisons to false on all H and call that a preorder.
This is contextual equivalence, not behavioral/process equivalence.
Generic W can itself contain an undefined-like value; VALUE(that value) is
different from the observation constructor UNDEFINED.

## O2: general fixed-process reversal and nonrecovery
Fix the actual complete process object C:Proc, including laws and admission.
Use P=admitted(C), a fixed domain D⊆P, distinct a,b∈D, and lo,hi∈W with
lo≤hi and NOT hi≤lo. Distinct values alone do not suffice for a preorder.
Allowed is a declared predicate on actual functions D→W.
Require Allowed to contain the two indicator functions assigning lo/hi
oppositely to a and b. Construct them, prove opposite strict rankings,
and show their actual ordering functions disagree at (a,b).
An alternative sufficient condition is a separating allowed function plus
closure under swapping a and b; distinguish this from the primary assumption.

Models are actual permitted evaluators M={ν:D→W // Allowed ν}.
processObs(m)=C (the whole C, not a selector label or reduced state list).
evaluatorObs(m)=m.val and orderingObs(m)(x,y)=(m.val x≤m.val y).
Apply V9's generic collision theorem to these actual maps. Freshly register
its exact type, replay its actual source and bind its immutable hash.
Prove there is no recovery of the differing ordering from the same full C.
Do not promote semantic nonrecoverability to probabilistic independence.

Falsifiers: constant-only Allowed; evaluators factoring through a map that
identifies a,b; empty/singleton D; non-strict codomain pairs; unadmitted or
unevaluated witnesses. State which premise fails in each.
Use a real fixed finite lawful process example for the executable reversal;
retain its complete composition/law data unchanged between evaluators.
The pure context corpus below is not a claim that every arbitrary admission
subset is itself the arrow set of a composition-closed process category.

## O3: exact independent finite calibration
Enumerate all three-value preorder relations from all Boolean relation tables.
For each, enumerate all five-way status/value assignments to three histories:
ILLEGAL, UNDEFINED, VALUE0, VALUE1, VALUE2. This yields the planned3625 contexts.
Represent admission and definedness separately; compare independent algorithms
for observations, induced comparisons, equivalence classes and quotient orders.
Check every relevant reflexivity, transitivity, representative-invariance and
antisymmetry equation; count actual executions.
Retain empty domains, nonantisymmetric value preorders and equivalent values.

For every strict value pair and distinct evaluated history pair, construct
opposite evaluators and verify actual ranking reversal with the process fixed.
Include domain/admission restrictions, constant-only and observation-collapsed
allowed classes as no-reversal controls; never claim a witness outside Allowed.
Additional probes cover empty carriers/codomains, evaluation on illegal
histories, an undefined-labelled value, malformed tables, false preorder laws,
bool/float aliases, out-of-range histories/values and mismatched dimensions.
Independent oracle must not call production order, quotient or context helpers.
A weakened always-pass diagnostic must be rejected on real hostile inputs.

## Evidence and custody
Pinned Lean4.19 with exact typed registrations and axiom inspection.
General proofs must not assume quotient-order or collision conclusions.
Run real source-valid proof weakenings that compile and fail the statement audit.
Normal/optimized integrated receipts must match, with exact coverage guard.
Missing tools/inputs is CANNOT_CHECK, separate from checked-invalid evidence.
Bind original checklist, original R2 freeze, V14 snapshot, and reused V9 proof.
New exact successor contract permits only these two original dispositions,
and rejects scope laundering, wrong witnesses, unrelated status changes and
coupled receipt/manifest edits. All other original records remain unchanged.
Docs/code modular under200lines, except raw snapshots/receipts as needed.

V14 has16closed original atoms (8governance,8scientific),206unresolved.
Full success yields18closed (8governance,10scientific),204unresolved.
R2 and overall programme remain OPEN, R0 alone remains whole-EARNED.
No reverse-admission recovery closure, context-family completion, prior-free
value selection, empirical novelty or complete intelligence derivation follows.
Commit, push and merge this result only after all final-head checks succeed.

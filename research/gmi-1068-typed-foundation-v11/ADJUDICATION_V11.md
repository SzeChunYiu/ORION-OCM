# Three original requirements: independent adjudication V11

Authority: #1068, FREEZE_V11.md, original ATOMIC_CHECKLIST_V1.json and original
R1/R2 freezes. This file defines the evidence-to-requirement mapping; generated
RESULT_V11 and the successor snapshot record the actual gate outcome.
Only the following three original atoms are eligible. Whole R1/R2 stay OPEN.
Do not infer closure from this document existing or from passing finite tests.

## GMI2-R1-002 — prove typing/associativity

Original source: gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json.
R1 FREEZE_V1 requires typed sequential composition and mechanized universal
category-law consequences, separately from minimality and admission claims.

Evidence: THEORY_V11 T1 constructs endpoint-indexed concatenation and proves
associativity by structural induction over arbitrary finite paths. T2 proves
preservation/uniqueness for every fixed interpretation into a lawful category.
T3 proves the laws survive any typed congruence quotient. T4 supplies the
coverage bridge for every small lawful category through the kernel of its
path evaluator, with explicit inverse functors. The corresponding general
Lean declarations are mapped in FORMAL_SCOPE_V11.md.

Disposition upon all gates: CLOSED, CONSTRUCTIVE_FORMAL_PROOF.
This is the formal law component originally requested. Target category laws
are premises of interpretation, not laws discovered for arbitrary physical
substrates. T4 avoids narrowing the component to freely generated categories.
Admission adequacy remains subject to V5's exact closure/lifting conditions.

## GMI2-R1-003 — prove identities

Original title and owner are preserved byte-for-byte in the source checklist.
R1 FREEZE_V1 requires identity processes and their laws.

Evidence: THEORY_V11 T1 constructs nil_A at each object and proves both unit
laws for every typed path. T2 proves evaluator preservation. T3 constructs
quotient identity classes and proves their laws. T4 shows these correspond
to the identities of every lawful small category represented by the quotient.
The proof works for distinct objects, parallel edges, loops and empty graphs.

Disposition upon all gates: CLOSED, CONSTRUCTIVE_FORMAL_PROOF.
The empty formal continuation is the identity. No claim says an arbitrary
physical idle operation consumes zero resources. V9's unique-unit theorem
separately prevents confusing removal of the identity symbol with loss of
identity structure; absolute signature minimality is not earned here.

## GMI2-R2-002 — prove context not derived from process law

Original R2 FREEZE_V1 target2 explicitly asks an explicit countermodel to
unique context/value ordering determined by process law. It does not ask
for nonrecoverability in every possible restricted model class.

Evidence: V9 THEORY_V9 section3 Countermodel A and RecoverabilityV9.lean
`process_does_not_recover_context`, `actual_ranking_reversal`, and the general
`no_recovery_of_collision`/`recoverable_iff_fiber_constant` theorems.
THEORY_V11 T5 spells out their match to the original target.

The two expansions have literally identical objects, named arrows,
source/target maps, identities, composition table, full admission and all
finite typed histories. Both evaluator domains are that common history set.
Only the total evaluator changes. Actual admitted histories [a],[b] reverse
strict rank. Adding the shared fixed ambient category to the Lean process
reduct does not resolve the collision: those components are equal too.

Disposition upon all gates: CLOSED, COUNTERMODEL_TO_UNIQUE_DETERMINATION.
The precise result is no uniform decoder on any declared model class
containing both expansions. It neither rules out recovery on a restricted
class nor establishes probabilistic independence. Objectives may be supplied
externally. Permuting away fixed intervention labels changes the question.

`independent_context_v11.audit()` binds seven real source files by SHA256,
including the original checklist/freezes, V9 theory, definitions, theorem
source and receipt. Tests compare operational evaluations against the bound
V9 implementation and check actual illegal compositions. Full process
records are compared once; admission is compared for each enumerated history.
Missing/unreadable input remains distinct from invalid evidence.

The 182 typed histories through length12, 156 differing evaluations,
26 identity-only histories and 36 identity-padded ranking reversals are
explicitly disclosed pre-freeze diagnostics. Reproduction is not prediction.
General nonrecoverability follows from the actual collision proof, not from
exhausting that finite history prefix.

## Required gate and remaining debt

All three dispositions require: original-source custody, general Lean proofs
under pinned4.19.0, real valid baselines, independent executable checks in
normal and optimized Python, hostile rejection controls, measured coverage,
and independent scientific review. The generated receipt must bind the
actual proof/test files. A failure leaves the affected atom unclosed.

The source checklist's historical status fields remain untouched. A successor
snapshot may record only these three changes, preserving every other atom
record and the dependency DAG. R0's eight governance closures remain separate.

No closure here for R1 minimality, all primitive loss witnesses, arbitrary
physical admission, all parent translations, or all universal process claims.
R2-003 and R2-007 need separately frozen corrected targets. There is no
promotion to R3-R17, full process/context fixed point, all machine-intelligence
families, empirical truth, novel parent mathematics or FULL_GMI.

# V20 / T preregistration — attainable frontiers and safe continuation pruning

Control plane: #1068; historical evidence: #833.
Planning parent: 55047a2320d7b1cabebb994a52d6c12ba92d2110 (S, PR #1115).
Import merged S main ancestry before publication. This freeze precedes every T
outcome implementation, proof, test, receipt and adjudication.
Only GMI2-R3-004, "prove frontier construction conditions", is eligible for
original closure. Its original evidence kind is FORMAL_OR_FINITE and status
UNKNOWN. Original R3 FREEZE target4 is "finite Pareto/maximal frontier construction".
The original prohibition on unconditional infinite-history frontiers remains.

## T1 — construct the actual finite frontier

Use a declared preorder, not assumed antisymmetry or a total preference.
For every finite attained set A, including empty A, construct its maximal
elements Max(A)={a in A | forall b in A, a<=b implies b<=a}.
Prove inclusion, cofinality (every a in A lies below some maximal element),
and equality of downward closures. Equivalent distinct maximal values both
belong to Max(A); do not silently identify values before declaring a quotient.

Construct an executable representative selector returning one attained member
per maximal equivalence class under a~b iff a<=b and b<=a. Prove its
cofinality, pairwise incomparability of distinct representatives, and minimum
cardinality among all cofinal subsets C of A. Choices can depend on a supplied
enumeration; no canonical encoding or absolute representation minimum follows.
Register actual finite construction/equations, not only "maximal implies member".

Instantiate the construction with the actual V15 Context and admission P:
A_x={eval(h) | H_x(h) and P(h) and E(h)}, where H_x selects the histories
under consideration. A finite supplied history collection yields a finite image;
alternatively a separately proved finite image suffices. Finite length of each
history alone does not imply finitely many histories or values.
Compute the actual attained image, frontier and representative witnesses.
Keep illegal, undefined and value responses distinct on the ambient domain.

Additional general theorem: on any attained preorder A, well-founded strict
ascent R(y,x) iff x<=y and not y<=x implies a maximal element above every a.
Prove this by well-founded induction. It is sufficient, not necessary, and
does not ensure a finite frontier, termination of an arbitrary search, or an
effective reconstruction of an infinite order. No Zorn import is required.
Record infinite boundaries at paper scope: Nat has no maximal value; Nat with
a top has a cofinal maximum despite infinite ascent; an infinite antichain has
well-founded strict ascent but an infinite frontier. One isolated maximal
element beside an ascending Nat component need not be cofinal.

## T2 — necessary and sufficient preservation condition

For arbitrary preorders X,Y and an actual partial map F:X->Option Y, define
guarded monotonicity:
x<=x' and F(x)=some(y) imply exists y', F(x')=some(y') and y<=y'.
It includes preservation of definedness upward, not only order where both exist.
For a set A write F[A] for defined outputs. Prove guarded monotonicity iff
every finite A and every cofinal C subset A satisfy down(F[A])=down(F[C]).
The reverse direction must use actual two-point sets {x,x'} retaining {x'}.
Prove the sufficient direction also for arbitrary cofinal subsets, without
unnecessary finiteness. Empty cases remain valid.
Give the equivalent observation statement for existential attainment of every
upward-closed goal. It does not preserve arbitrary singleton goals, universal
safety, probabilities, multiplicities or exact history identity.
Prove guarded maps compose, preserving their actual Option domains.

Construct actual partial postcomposition of V15 contexts:
E'(h)=E(h) and F(eval(h)) is defined; P stays unchanged, and the new evaluator
returns the actual F value. Preserve admission even for illegal ambient histories
where evaluation happens to be defined. Register the changed domain, outcome
tags and attained-image equations. V17 total postcomposition's unchanged-E law
cannot be applied to a partial map.

## T3 — constructive revival through deterministic continuation simulation

Supply a state set X, action set, deterministic partial transitions d_a:X->Option X,
and a base preorder B on states. Define simulation R by R subset B and:
x R y and d_a(x)=some(u) imply exists v, d_a(y)=some(v) and u R v.
Construct the greatest such relation G. Prove it is a preorder and exactly:
for EVERY finite action word w, including empty w, run(x,w)=some(u) implies
exists v, run(y,w)=some(v) and B(u,v).
The empty word enforces containment in B. Determinism allows one successor
to match all suffixes. Register actual recursive Option runs and step laws.

This is the greatest base-order refinement for SAME action-word observations.
It is not necessarily the greatest relation preserving bare existential goal
reachability when substituting different actions is allowed.
Every action is guarded-monotone for G. Combine T1/T2 to prove that finite
cofinal pruning under G preserves downward endpoint attainability through each
finite sequence of actions, and hence existential upward endpoint goals.
Do not infer infinite-run behavior, arbitrary trace equivalence or probabilistic
semantics from this statement.

For finite machines compute G by synchronous descending refinement starting at B:
delete pairs with an unmatched enabled action or successor pair absent from the
previous relation. Prove/verify the actual implementation's stable result against
the all-word criterion. At most n² pairs can be deleted; include the final
stability check when stating an iteration count. Empty state/action sets work.
Calibrate against independent pair-BFS distinguishing words, with any rejected
pair witnessed within length n² (base-order failures may have the empty word).
A proof of the general greatest relation is distinct from certification of the
Python algorithm; state the exact kernel/finite correspondence boundary.

Bridge to the actual V8 Machine and budget_lift for supplied finite budgets.
Use lifted destinations as the partial transitions and a declared endpoint
Context/order. Costs constrain legality through the actual lift. This endpoint
observer does not promise equality of V8's full EDGE/output/cost traces.
Residual budget must not be dropped before the guarded condition is checked.
The generic core includes empty machines even though V8's existing constructor
requires nonempty states/actions; do not silently strengthen the generic theorem.

## Prospective calibration and decisive controls

Planning algebra only; no outcome counts exist at this freeze.
Enumerate all preorders on sizes0..3. All source/target partial maps give
59,403 ordered map instances and 1,563,467 raw map/(C subset A) candidates
before cofinal filtering. Check the guarded iff and actual downward outputs.
Every two-action deterministic machine on0..3 states with each base preorder
gives119,113 instances. Compare greatest relations against independent
distinguishing-word search; verify actual frontier pruning and positive controls.
Use all actual V15 contexts with history/value dimensions0..3, all strict P
flags and partial value assignments, every preorder, and every history selector.
Exercise partial postcomposition separately over declared dimensions0..2,
including empty target domains and illegal-but-evaluated histories.
All counts are recorded from mandatory independent counters after the run;
an oracle must not delegate its answers to production.

Mandatory controls:
- Lost continuation: a currently dominated history can reach a goal while its
  retained dominator cannot continue. Demonstrate capability loss with raw
  value pruning, and recover it using the derived G frontier.
- A total update reverses value order; retaining only its input maximum fails.
- Equivalent current values can have different enabled futures.
- Non-upward singleton goals can be lost even by lawful monotone pruning.
- Preorder aliases, empty A, an omitted maximal class and a representative
  outside A reject false minimality/cofinality claims.
- Collapsing unequal residual budgets can erase affordability distinctions.
- Nondeterministic branching: after a, one state offers both b,c while the
  other branches to separate b-only/c-only states. Equal finite trace languages
  do not imply forward simulation; keep this outside the deterministic theorem.
- Alternative action labels may reach the same goal despite failing same-word
  simulation; do not promote the observer-relative greatest relation.
- Malformed shapes, noncanonical Boolean/integer aliases, invalid indices and
  hidden later input errors must be rejected distinctly from empty attainability.
Failures require one-stage diagnosis and a real repair before adjudication;
do not alter the target to manufacture a positive result.

## Evidence, source ownership and original accounting

Lean4.19/Std must freshly check the finite construction/cofinality laws,
well-founded ascent theorem, guarded iff/composition, actual partial-context
domain/evaluation bridge, greatest deterministic simulation and arbitrary-word
characterization. Register exact constructor outputs and theorem types.
Finite selector/minimum-cardinality and refinement correspondence claims must
have explicit general proofs or be separately labelled finite-calibration scope;
do not disguise finite experiments as arbitrary-carrier mechanization.
Use source-valid theorem weakenings that compile before typed AUDIT rejection.
Mandatory test inventory/counters, independent primary-parent comparison and
actual-data hostile controls must yield identical normal/-O receipts.
Missing evidence/tool is exit2; checked invalidity is exit1.

Primary parents: Geilen-Basten-Theelen-Otten, Algebra of Pareto Points,
Theorem1/Corollary1, Sections5-6: https://tbasten.estue.nl/papers/pareto.pdf
Their minimization partial orders require explicit dualization and preorder
quotient handling. Doyen-Raskin, Sections3.1-3.2, simulation/antichain operators:
https://lsv.ens-paris-saclay.fr/~doyen/papers/Antichains_Algorithms_Finite_Automata.pdf
Well-founded existence is standard order theory; no new mathematics or empirical
breakthrough is claimed. The contribution is a precise executable GMI bridge and
a verified repair of unsafe pruning, with all assumptions exposed.

Preserve all222 original IDs/titles and every untouched record. Only R3-004
may close after its actual finite-frontier requirement is fulfilled.
Then original fulfilled20/unresolved202 becomes21/201; two immutable V16
qualified readings separately leave199 active unresolved. R3 keeps its inherited
whole-round stale status, and R0 remains the only whole-EARNED round.
Add only scoped R3/R4/R14/R15 repair evidence. No new amendment authority,
full GMI, universal objective, finite infinite-frontier representation or
unconditional nondeterministic trace/simulation equivalence is claimed.
Bind actual predecessor bytes against the PR base and dereference inherited
receipt inputs; reject coupled scope, source, status and accounting mutations.

| Source | SHA256 |
| --- | --- |
| research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json | 4cc262d491fbcdccf2b4c8656e80dcdb06e1795344500e46ac980ca09a679574 |
| research/gmi-1068-r3-contextual-attainability-v1/FREEZE_V1.md | e9f25acb58dc24f2bda8ae6dfeab4e78660f3e1ffc664638b74b76d7f5557209 |
| research/gmi-1068-r3-contextual-attainability-v1/THEORY_V1.md | 6298fda4b6a2f4feb63c98f103c69ffea2602ec86e58fbbfb7dcad06c4aa8c9a |
| research/gmi-1068-r3-contextual-attainability-v1/Attainability.lean | 1c34238b76315a1420566ec41efd5088ab1ff8a4a2930cd362cec08d9608f686 |
| research/gmi-1068-partial-context-v15/PartialContextV15.lean | 332dcfb63304d5668800ea21f09795c2d92267989291ffe35d9e38ea2db0edf5 |
| research/gmi-1068-partial-context-v15/context_v15.py | 75c62203c8ae61ddce1081f9deaf463dfce6965bb160086a8e21adfe787fcd2f |
| research/gmi-1068-context-specializations-v17/core_v17.py | 2036aee04274bfdd29cd0caa300ace47b066ac958c58043a0290105dbfae107f |
| research/gmi-1068-continuation-v8/continuation_v8.py | 16f5ba400ea3475b1fc7f58a594ca283aa9d8cf2710095a56a81b9f96c146f02 |
| research/gmi-1068-continuation-v8/ContinuationV8.lean | daca89f4bb32898b285a993ad5de777acbcbcffbf10b0c888b10dfc8accf4da4 |
| research/gmi-1068-arrows-only-v19/RESULT_V19.json | 287b88eaa73f304d553402fea95a1d106297f20981bfd155330a19a31fa2822b |
| research/gmi-1068-recursive-audit-v19/SCOPE_SNAPSHOT_V19.json | b1d00cd9fc7e7de1be9a76f4c17633b3d907e9b66e00171653bbc5558e15fc92 |
| research/gmi-1068-recursive-audit-v19/CURRENT_ACCOUNTING_V19.json | 11e24983450223f1d1e24cb6b3813278147205a7f179f7493d57827bb6e789b7 |
| research/gmi-1068-corrected-targets-v16/TARGET_CONTRACT_V16.json | faa8f83c0af7a2f0a042e84deb7be191b09a281c08f287c5e986397124177902 |
| research/gmi-1068-corrected-targets-v16/RESULT_V16.json | 18bea5c6f85b4fcc91c40c53cbf63df59c38d70e9e839efc4585f6640497ad1a |
| research/gmi-1068-amendment-governance-v16/AMENDMENT_LEDGER_V16.json | e1cc2d2dbc10171407577889f75ac531c30cf09eab224fc3823f3931c5048618 |
| research/gmi-1068-amendment-governance-v16/RESULT_V16.json | ed491fab2cd0b69fb4ee845b82e349c79ff0d70f0dbc1d312ee0755645437de4 |

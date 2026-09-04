# ORION Cognitive Machine failure ledger

Umbrella: ORION-V2 #194
Execution master: ORION-V2 #197
Focused P0: ORION-V2 #221
Independent review: ORION-V2 #199, #245

**Status: `APPEND_ONLY__NO_NOVELTY_OR_BREAKTHROUGH_CLAIM`.**

This ledger follows the form of the repository's root `FAILURE_LEDGER.md`. Failure history is
append-only: a repaired defect remains visible, and **a later green result may not erase how it was
obtained**. Nothing recorded here grants scientific, novelty, priority, architecture, language,
quantum or publication authority.

Scope. This ledger holds process, custody and import-authority failures of the OCM programme. The
scientific negatives of the revocation-complete-learning lane — the eleven killed or threatened
claims `RCL-F01` through `RCL-F11`, each with its disposition, strongest reason and reopen condition
— live in
`research/orion-machine/revocation_complete_learning/RCL_FAILURE_AND_PARENT_COLLAPSE_LEDGER_V0.md`
and are **referenced, not restated**, so that they have exactly one home.

## Retained failure classes

These are failure vocabularies to keep detecting, not a claim that every class currently has an open
critical defect.

- `BINDING_OVER_UNCOMMITTED_BYTES` — a content binding is computed over a working-tree or pre-commit
  draft rather than over the committed blob, and the artifact then enters version control at a
  different length. Every downstream receipt inherits the wrong digest. The failure is invisible to
  every custody instrument the repository has, because each of them compares a recorded digest
  against the bytes that *are* there and correctly reports a mismatch — while no instrument can say
  whether the bytes that *were* recorded ever existed. Distinct from
  `NONREPRODUCIBLE_FROZEN_ARTIFACT` in the root ledger: there the artifact is regenerable and the
  regeneration differs; here there is nothing to regenerate, and recovery is impossible **by
  construction rather than by loss** — the referent was never pushed, so no search of the repository,
  however exhaustive, can reach it. The tell is a `git log --all --full-history` on the path
  returning only the creating commit while the recorded length has never occurred on it. Guard:
  compute every binding from the committed blob (`git show <commit>:<path>`), never from a file on
  disk; and when a drift is found, re-bind with the superseded binding retained and the disposition
  stated, rather than silently replacing it. First observed 2026-09-03, recorded 2026-09-04
  (`RCL_FAILURE_AND_PARENT_COLLAPSE_LEDGER_V0.md`; see the concrete record below).

- `RECORDED_REPAIR_NEVER_LANDED` — a receipt records a checker defect as discovered *and repaired*,
  with the repair stated verbatim, while the module it names still carries the unrepaired value. The
  receipt is internally consistent, the repair description is correct, and the code is wrong; a
  reader auditing the receipt finds a closed defect, and a reader running the module finds a red
  suite. The two never meet, because nothing binds a `repaired` field to a landing commit. Guard: an
  entry under a `discovered_and_repaired_*` key must cite the commit that landed it, and the repaired
  value must be asserted by a test that runs in CI — a repair recorded only in prose is a plan, not a
  repair. First observed 2026-09-03, landed 2026-09-04 (see the concrete record below).

- `DANGLING_CROSS_REFERENCE` — an artifact or issue names an issue or pull-request number as the
  source of authority for something it does not itself establish, and the number resolves to an
  unrelated object. Because GitHub numbers issues and pull requests from one sequence, a number
  written before the object exists will later denote *something*, and that something reads as
  confirmation. The failure is silent in both directions: the citing artifact looks well referenced,
  and the cited object carries no sign that anything points at it. Guard: resolve every imported
  number against what it names — state, title, changed paths — and record the resolution, not the
  number. First observed 2026-09-04 (see the concrete record below).

- `IMMUTABLE_TARGET_MUTATED_BY_ITS_OWN_BINDING_TEST` — an artifact is published as a frozen,
  immutable review target *and* carries a hash-binding self-test that walks every artifact it binds.
  The two properties are incompatible: any correction to any bound artifact forces an edit to the
  frozen target, or its own test fails. Freezing and self-verification pull in opposite directions,
  and the conflict surfaces only when the first correction arrives — at which point the least-bad
  action is to edit the immutable file and disclose it. A second-order consequence follows: the
  target's recorded `base_sha` or head then names a commit that is no longer the branch head, so an
  independent reviewer following the published pointer inspects a different tree from the one under
  review. Guard: separate the frozen statement of the review question from the mutable binding table
  it refers to, so a re-bind never edits the frozen half; and when a published target does move,
  announce the move on the issue that administers it rather than leaving the reviewer to discover it.
  First observed 2026-09-04 (see the concrete record below).

- `TARGET_ARCHITECTURE_PRESUPPOSED` — a theorem candidate is phrased as "the OCM architecture
  achieves X", so its statement already contains the architecture whose existence the programme is
  supposed to establish, and every parent-subtraction outcome is read as a verdict on an
  architecture rather than on a substrate constraint. The operator directive of 2026-09-04 (#194,
  comment 5539487737) names the failure: MNI/MNSI are not target architectures, and the object of
  study is the minimal substrate plus its constraints. Guard: state every theorem candidate in the
  form "under substrate `Σ` with constraints `C`, a machine can/cannot …", and record the
  architecture-shaped residual names (`STRICT_*_RESIDUAL`) as `NOT_EARNED` rather than as open
  targets. First observed 2026-09-04 across #200–#205 as chartered; every lane restated in
  `theory/OCM_DIRECTIVE_RESCOPE_V1.md` §2.

- `PARALLELISM_CEILING_BREACHED` — a lane spawns sub-workers against a stated programme-wide
  ceiling on concurrent workers, so the ceiling's purpose (bounded, attributable, sequential
  reasoning per lane) is defeated while each worker's output still looks well-formed. The tell is
  a worktree or branch touching the lane's paths whose author is not the lane. Guard: a lane under
  a ceiling does the work sequentially itself; children's committed work is recovered and built on,
  uncommitted children's work is re-derived. First observed 2026-09-04 (this lane's previous
  attempt spawned a lane-202 checker builder and a lane-203 semantics builder against a
  three-worker ceiling; the lane-202 checker was recovered from the shared worktree at 838 lines
  and re-verified, and the lane-203 semantics was re-derived from scratch since none was committed).

- `SUPERSEDED_BINDING_MISATTRIBUTED` — a rebind replaces a carrier's `superseded_binding` with the
  immediately previous bytes but defaults its `recorded_in_commit` to the original freeze commit
  and discards the earlier superseded entry, so the custody chain is both mis-attributed (a commit
  that never held those bytes) and truncated (the original binding gone). Every hash still
  verifies, so the byte-exact tests pass; the defect is in provenance, not content. Guard: a rebind
  nests the previous entry (with the commit that actually carried it, checked by `git show`) rather
  than replacing it, and never defaults a commit field. First observed 2026-09-04 (this lane's
  README rebind cascade on PR #281; found by Cursor Bugbot; corrected before merge with the full
  chains nested and every commit verified against the blob it carried).

- `PRESENTATION_DEPENDENT_OBSTRUCTION` — an obstruction is named in a coordinate that is a
  *presentation* of the problem rather than its content, so that objects satisfying the literal
  negation of the obstruction exist and leave the underlying difficulty untouched. The lever the
  obstruction names is then satisfiable without progress, and a lane that satisfies it reports a
  reopen that reopens nothing. Two instances on 2026-09-04: lane #200's residual was recorded as
  needing "a non-rectangular natural class" when the content of Theorem D is *decomposability into
  two parent learners* — the three planted non-rectangular classes of the first pass are all
  decomposable (`I = 0`, certified), so the literal lever was already satisfied by the first pass's
  own controls; and the separation-test design named "a registered non-rectangular natural class"
  as the missing object for condition (1) when the blocker is the comparator definition, which no
  class property can change (Theorem N2, class-independent). Guard: when recording an obstruction,
  state the *invariant* it stands for and give a planted object that satisfies the literal condition
  without meeting the invariant; if none can be constructed, the coordinate is the content. Records:
  `theory/OCM_NONRECTANGULAR_CLASS_V1.md` §2, `theory/OCM_SEPARATION_TEST_REAUDIT_V2.md` §1.

## Retained concrete failure records

- **`BINDING_OVER_UNCOMMITTED_BYTES` — RCL parent-collapse ledger, 2026-09-03/04.** The binding
  recorded in commit `4655495` for
  `research/orion-machine/revocation_complete_learning/RCL_FAILURE_AND_PARENT_COLLAPSE_LEDGER_V0.md`
  is 4,751 bytes / `466e6da9…`; the bytes actually committed are 4,746 / `12ca96d8…`. The artifact
  and both receipts that bind it were created together in one all-insertions commit across 18 files.
  Three searches with stated scope agree that only `4655495` and its merge `7015cdb` ever touched the
  path — `git log --all --full-history`, an object-store scan of 6,765 objects that found the
  4,746-byte blob as its control, and the GitHub commits API for the branch, which closes the gap the
  shallow clone leaves. **The file has never existed in version control at its recorded length**, so
  there was no clean version to restore. Six reconstruction sweeps — 5-gram over 4,747 positions,
  inflection-aware anomaly scan, space-multiset over 16,108,764 multisets, structured whitespace over
  113 enumerated combinations, typographic/encoding over 33.6M candidates, and whole-word omission
  across 5,007 words — each carried a positive control that fired, and none produced the recorded
  hash. **This is birth drift, not corruption.** Disposition `DRIFT_RECORDED_NOT_BLESSED`: the
  binding was re-taken over the committed bytes with `superseded_binding` retained in every receipt
  that carries it, nothing above the custody note was altered to make hashes agree, and nothing was
  overwritten. What remains open is whether the pre-commit draft differed in substance or only in
  transport formatting; that is not determinable from any source reachable from this repository. No
  claim, disposition, strongest reason or reopen condition in the RCL ledger is changed by it.
  Record: the artifact's own section *Custody note — binding re-freeze 2026-09-04*; audit row
  `IA-04` in `research/orion-machine/OCM_SNAPSHOT_V1.json`.

- **`RECORDED_REPAIR_NEVER_LANDED` — WLL interface hierarchy, 2026-09-03/04.**
  `research/orion-machine/receipts/OCM_WLL_P0_THEOREM_BUNDLE_RECEIPT_V1.json` records, under
  `discovered_and_repaired_checker_defects`, the defect *"endpoint parity relation counted as one
  individually known target coordinate"*, its effect *"endpoint-only safe coverage overstated by one
  coordinate"*, and its repair *"correct endpoint-only guaranteed coordinates from one to zero and
  abstentions from five to six"*, with `theorem_statement_changed: false`. The repair was not in
  `research/orion-machine/reference/ocm_wll_interface_hierarchy_exact.py`, which still pinned
  `I0_ENDPOINT_ONLY` at `(answerable=1, abstentions=5)` while the registered 256-world model yields
  `(0, 6)`. The module failed its own calibration and took five CI checks down with one root cause.
  **The gate was strengthened, not relaxed**, when the recorded repair was landed in commit
  `4cb6dca`: `THEOREM_BOUNDS` now holds the Section 6 lower bounds *as bounds*; `TARGET_WIDTH` with
  an assertion that `answerable + abstentions == target_width` pins the denominator, so a bound
  cannot be satisfied vacuously by `(0, 0)`; `REGISTERED_MODEL_VALUES` retains the exact measured
  pair, so drift detection is no weaker than before; and Theorem WLL-8 monotonicity — coverage
  non-decreasing and abstention non-increasing along the refinement chain — is newly asserted on
  measured metrics. Mutation controls M1 through M5 are each caught, with the unmutated case M0 as
  the no-alarm control. No theorem, computation or claim changed. Verified under Python 3.12.13,
  matching the CI pin. Record: audit row `IA-05` in `OCM_SNAPSHOT_V1.json`.

- **`DANGLING_CROSS_REFERENCE` — draft-carrier number 226, 2026-09-04.** Issue #221 carries the
  header *"Active draft: #226"*, and the field `draft_pr: 226` appears in both
  `research/orion-machine/receipts/OCM_WLL_P0_THEOREM_BUNDLE_RECEIPT_V1.json` and
  `research/orion-machine/theory/OCM_WLL_CANDIDATE_TERMINAL_V3.json`. Pull request 226 is
  *"pra-r1: protected run under operator authorization — outcome receipt
  (CONTROL_FAILURE__SUITE_NOT_INTERPRETABLE)"*, head ref `pra-r1-outcome`, merged
  2026-09-03T00:17:48Z. It changes four files, all under
  `research/llm-machine-epistemics/results/pra-llm-r1/`, and **zero** files under
  `research/orion-machine/`. Issue #221 was created at 00:05:27Z, four minutes before pull request
  226 was opened at 00:09:48Z: the number was written before it denoted anything, and then came to
  denote a different research line. The actual carriers are pull requests #244 and #254, established
  by enumerating the changed files of all 188 pull requests of this repository in every state, which
  returns 22 and 30 paths under `research/orion-machine/` respectively and 0 for every other pull
  request. No frozen receipt was edited to correct this; the reference is recorded as dangling.
  Record: audit row `IA-01` in `OCM_SNAPSHOT_V1.json`.

- **`IMMUTABLE_TARGET_MUTATED_BY_ITS_OWN_BINDING_TEST` — RCL review packet V0, 2026-09-04.**
  `research/orion-machine/revocation_complete_learning/RCL_INDEPENDENT_REVIEW_PACKET_V0.json` is the
  frozen hostile-review target published to issue #199 and is declared immutable
  (`RCL_INDEPENDENT_REVIEW_PACKET_V1.json`: *"V0 remains immutable"*). Its own hash-binding test
  walks every entry of its `artifacts[]` array, so the ledger re-bind above forced an in-place edit
  of the frozen file. The edit was made, every non-`artifacts` key was verified byte-for-byte
  unchanged, and the change was disclosed inside the packet itself. The second-order consequence is
  the operative one: the packet's `base_sha`, `7ae42207…`, is no longer the head of the branch it
  names, which is at `d4eb281` — and issue #245 records a *"Current rebased head"* of `7015cdb`,
  which has since advanced by four commits. **An independent reviewer following either published
  pointer would inspect a different tree from the one under review.** The administrators of #199 and
  #245 have been told the target moved. Record: audit rows `IA-02` and `IA-03` in
  `OCM_SNAPSHOT_V1.json`.

- **`IMMUTABLE_TARGET_MUTATED_BY_ITS_OWN_BINDING_TEST` — second instance, spine README, 2026-09-04.**
  `research/orion-machine/README.md` is the programme spine (D01) *and* an entry in the `artifacts[]`
  arrays of `REVOCATION_COMPLETE_LEARNING_RECEIPT_V0.json` and `RCL_INDEPENDENT_REVIEW_PACKET_V0.json`,
  both walked byte-exactly by `tests/unit/test_revocation_complete_learning.py`. The operator
  directive of 2026-09-04 requires the spine's terminal block to change, so the README was edited
  (1,076 → 3,317 bytes) and the two V0 carriers were re-bound with `superseded_binding` retained and
  `rebind_reason` stated; the packet V0 edit cascaded into `RCL_INDEPENDENT_REVIEW_PACKET_V1.json`,
  which binds packet V0, and was re-bound the same way. Every non-`artifacts` key of both packets is
  unchanged. Bindings were recomputed from committed blobs (`git show <commit>:<path>`), never from
  working-tree files. This is the same conflict as the first instance — a frozen target that binds a
  mutable spine — and the same least-bad action; the structural fix (freeze the review *question*,
  bind the spine elsewhere) is still not applied and is recorded as owed. The move is announced on
  #199 and #245, which administer the targets. The pre-directive README bytes remain bound in
  `OCM_SNAPSHOT_V1.json` `content_bindings` at commit `d4eb281` as history, unedited.

- **`IMMUTABLE_TARGET_MUTATED_BY_ITS_OWN_BINDING_TEST` — third instance, spine README, lane-200
  revival, 2026-09-04.** The terminal block had to change again (residual restated; natural
  non-rectangular class line; RCL-C and separation lines). README.md (3,317 → 4,121 bytes) was re-bound
  in `REVOCATION_COMPLETE_LEARNING_RECEIPT_V0.json` and `RCL_INDEPENDENT_REVIEW_PACKET_V0.json`
  with the previous entry nested verbatim under `superseded_binding` (its own chain retained and
  its `rebound_in_commit` verified against the blob it names before nesting), then the receipt
  inside packet V0 and packet V0 inside packet V1 consequentially, one commit per link so that every
  `rebound_in_commit` names the commit that actually carries the bound bytes. All 38 bindings in the
  three carriers verified against `HEAD` from `git show`. The structural fix — freeze the review
  *question*, bind the spine elsewhere — is still not applied and is still owed; a third occurrence
  is the argument for doing it before a fourth.

- **`VACUOUS_CONTRAST` — below-frontier arm of `rcl_checks_v1.py`, 2026-09-04, on a merged
  artifact.** The V1 checker written to repair three vacuous V0 controls carried one of its own:
  `candidate_profiles` never deduplicated, so below the frontier the candidate set always had
  `2^(N−S−Q) > 1` members and the assertion "below the frontier yet every profile reconstructed
  exactly" could not fire; only the collision-pair arm carried content. **Found by Cursor Bugbot on
  PR #281** at `2f54e77`, after the module had merged in #278. Repaired in place (the module is
  bound only by its own PR receipt, regenerated with superseded bindings retained, not by a frozen
  review target): candidates are deduplicated, soundness (truth among candidates) and completeness
  (exactly `2^(N−S−Q)` distinct candidates) are asserted for every profile, and mutation `M6`
  (collapsing reconstructor) is registered and caught for that reason; 6/6 mutations. Denominators
  unchanged (28,863 reconstructions, 64 collision pairs). The lesson is the root ledger's second
  `VACUOUS_CONTRAST` instance restated: a guard against vacuity can carry a vacuous arm.

- **`VACUOUS_CONTRAST` — S4 census of the reference semantics, 2026-09-04, caught before merge.**
  The first draft of `reference/ocm_reference_semantics.py::check_S4_representation_revision`
  scored the `abstain` policy inside the exactness loop. Since `abstain` returns `None` on every
  revocation a coarse partition cannot express, `exact` was false exactly when `is_block_union`
  was false, so the biconditional "exact iff measurable" **could not fail** — the same shape as the
  three RCL controls above — and mutation `M3` was being "detected" by the unrelated coarsest-
  partition assertion rather than for its registered reason. **Found by Cursor Bugbot** on PR #279
  at `e9a0222`, reproduced, and repaired in place because the PR was unmerged and the module was
  bound only by its own PR receipt, not by a frozen review target: the two committed policies are
  evaluated separately on all 168 profiles, abstention is its own count (zero iff measurable), and
  measurability is judged by an independently written `is_block_union_b`, so `M3` now moves the
  exact-partition counts from 1/4/1/4 to 15/15/15/15 and is caught for that reason; a new test pins
  the disagreement. No theorem statement changed; Theorem S4 gained its committed-policy clause,
  which it had silently assumed. Repaired in `a855f57`, receipt regenerated in `58282c5` (both squash-merged to `main` as `e1bd52b`).

- **`VACUOUS_CONTRAST` — three RCL controls that cannot fail, 2026-09-04.** This is the repository's
  existing vocabulary from the root `FAILURE_LEDGER.md`, applied to a new instance; no class is minted
  for it. Three controls in the revocation-complete-learning lane are structurally incapable of
  reporting the condition they exist to catch:

  1. `rcl_checks_core.py::verify_storage_query_frontier` reconstructs from
     `profile_from_bits(bits[:stored] + bits[stored:], n)`. That expression is the identity on the
     full bit vector for **every** value of `stored`, and the emitted `exact` field is the literal
     `True`. The loop over `stored` varies nothing: no storage bit is ever withheld and no coordinate
     query is ever issued, so the 5,329 reconstruction checks do not test the RCL-1c storage/query
     frontier they are cited for.
  2. `rcl_checks_finish.py::verify_controls` sets `mutation_detected` by flipping one coordinate of a
     **copied** signature tuple and comparing the copy to the original. That inequality holds for
     every boolean vector — verified over all 16 four-vectors, with none making it false — so the
     control cannot detect a mutated profile, a colliding signature, or a broken `signature`.
  3. The same function builds `no_alarm` by storing `live(full, revoked)` twice under two keys and
     calling `len(set(values)) == 1` agreement. That is `x == x`, true for either value of `live()`.
     No distinct complete-updater path is exercised, so the control cannot catch a false retraction or
     a `live()` that always returns the same boolean.

  This is the exact shape the root ledger names: *"a comparator with no contrast reports `1.000`,
  which reads as strength and has no denominator to interrogate."* **Found by an automated reviewer**
  — the Cursor Bugbot check run on pull request #244 at head `d4eb281`, which reported three
  medium-severity findings — and each was then reproduced independently against the committed source
  before being recorded here. A checker's report is not a finding until the finding is confirmed.

  **Recorded, not repaired.** All three sites are hash-bound inside
  `RCL_INDEPENDENT_REVIEW_PACKET_V0.json`, the frozen review target of issues #199 and #245.
  Repairing them here would break that binding a second time, and would delete the evidence that
  checkbox **RCL-R03** of issue #245 exists to surface: *"Confirm the planted over-retraction control
  fires, the no-alarm control passes, and the mutation control fails the intended invariant."* The
  authoring side repairing a control before the independent review that is chartered to test it has
  run would convert a finding into a green result. The three control results are withdrawn to
  `CANNOT_CHECK`; no theorem statement is altered; the planted over-retraction control, which does
  compare two distinct expressions, is not implicated. Disclosed on #244 and #245. Record: audit row
  `IA-07` in `OCM_SNAPSHOT_V1.json`; deliverable row `D09` in `OCM_TASK_LEDGER_V1.json`, downgraded
  from `PRESENT` to `PARTIAL` on this finding.

  **Scope of the withdrawal, stated rather than assumed.** `RCL-1c`, *"exact storage-query frontier"*, carries the status `HAND_PROOF_COMPLETE_FINITE_CONSTRUCTION_GREEN`. The `FINITE_CONSTRUCTION_GREEN` half is produced by `verify_storage_query_frontier` and is withdrawn with it, as is `storage_query_reconstruction_checks: 5329` in both
  `REVOCATION_COMPLETE_LEARNING_RECEIPT_V0.json` and `REVOCATION_COMPLETE_LEARNING_EXACT_RESULT_V0.json` and the `frontier_points` / `all_exact` roll-ups. The `HAND_PROOF_COMPLETE` half is not implicated and is neither confirmed nor disturbed here. `RCL-0`, `RCL-1b`, `RCL-1d`, `RCL-2`, `RCL-2a` and `RCL-3` take `FINITE_ORACLE_GREEN` from other verifiers; `RCL-2b` rests on the planted over-retraction control, which compares `live(full, revoked)` against `live(emitted_one, revoked)` — two distinct expressions. A withdrawal with an unstated scope is the same defect in miniature.

- **`TERMINAL_OVERSTATES_ITS_PROCEDURE` — near miss in the #204/#205 precondition record,
  2026-09-04.** The uncommitted draft of `theory/OCM_LANES_204_205_PRECONDITION_RECORD_V1.md`
  recorded lane #202's terminal as `TRANSFORMER_EQUIVALENT_UNDER_MATCHED_RESOURCES` before any
  comparator manifest existed or anything had been compiled — the root ledger's class, applied to
  a terminal string written ahead of its procedure. Caught on resumption by reading the lane-202
  checker's own `authority` block (`transformer_equivalence_proved_here: false`) against the draft;
  corrected to `TRADEOFF_FRONTIER_ONLY` with comparator equivalence `CANNOT_CHECK` before the record
  was committed. Recorded because the string would have read as a result on the lane that consumes
  it (#204's precondition table). No artifact carried it into version control.

- **`PRESENTATION_DEPENDENT_OBSTRUCTION` — lane #200 obstruction and separation-test condition (1),
  2026-09-04.** The first pass's obstruction ("no registered class is non-rectangular") was correct as
  a statement and wrong as a lever: `reference/ocm_nonrectangular_class_exact.py` shows COUPLED_FULL,
  COUPLED_HALF and COUPLED_FORCED (648 worlds, all failing R0) each have interaction term 0 — a
  B-first product of two parent learners meets the counting bound on every one — while a planted
  pointer-chasing class shows the procedure can fire (`I = 1`, existence witness). The content of the
  obstruction is non-decomposability; restated in `theory/OCM_NONRECTANGULAR_CLASS_V1.md` §2. The
  same shape in `OCM_SEPARATION_TEST_DESIGN_V1.md` §5 item 1: the class half is now met by
  `VSW(SINGLETONS_5)` and the test is still not freezable, for a class-independent reason
  (`OCM_SEPARATION_TEST_REAUDIT_V2.md` Theorem N2). Neither first-pass record is edited; both are
  superseded by reference.

- **Near miss, no class minted — two exact-solver defects caught before any artifact, 2026-09-04.**
  (1) The first draft of the decision-tree solver in `ocm_nonrectangular_class_exact.py` pruned its
  query scan on the *world* count when the target was the coarser behaviour value, accepted a
  suboptimal tree, overstated `D_B` on MONO_CONJ_2 by one, and reported `I = 1` — a spurious natural
  non-decomposable class. Caught by re-deriving `D_B` by hand (2 membership queries identify 4
  monotone conjunctions). (2) The sequential cost was then taken as `D_first + max fibre cost`; on
  LTF_2 the simulated Z-first strategy costs 11 where the formula says 12, so the formula is not the
  cost of any strategy of the shape it names. Caught by simulating the composite strategy on every
  world. Both are retained as mutation controls (M1) and the guard is structural: every optimal
  value is established by two independently written solvers that must agree *and* by an explicit
  strategy simulated on every world; a non-decomposability claim is certified only when the
  sequential cost exceeds a *simulated* joint tree. The lesson is the root ledger's
  `TERMINAL_OVERSTATES_ITS_PROCEDURE` in miniature: an optimiser's number is not a bound until a
  strategy attaining it has been run.

### Unreturned by construction, not repaired

Issue #221's deliverable 10 — *"independent hostile review stating which candidates collapse and what
exact residual remains"* — is `NOT_OBTAINED__DISCLOSED_LIMITATION`, and so is the parallel review of
issue #245. This is **not** a pass and **not** `CANNOT_CHECK`: the check is well defined and
executable by any independent party, and it simply has not been performed. No review was simulated,
role-played or generated. Issue #221's own gate reads *"same-session theorem authorship cannot close
the independent review issue #199"*, and a generated reviewer would supply from inside the authoring
session exactly the external authority this P0 exists to withhold — which would poison a
parent-subtraction record whose entire purpose is to keep that authority external.

The cost is named rather than absorbed: `literature_priority_established: false`,
`novelty_established: false` and `clean_post_material_passes: 0` remain as the carriers record them;
every `promotion_blockers` and `blocking_obligations` list in those carriers names independent
hostile proof reconstruction, so no candidate advances past its recorded terminal; and `RCL-F10`
stays `BLOCKED` with `RCL-F11` `BLOCKED_HIGH_COLLISION`. The smallest next action is to route issues
#199 and #245 to a party outside the authoring sessions.

- **`VACUOUS_CONTRAST` ×2 and a stale self-binding — KSO M1 population receipt, 2026-09-04 (PR #295), found by
  the guards lane's adversarial replay.** (1) *Label ≡ oracle on the CONSTRAINT edge*: every `nocontra:<c>`
  atom is VALID on the dev split at v0 and v1 (the ME-X1 generator plants no negative evidence), so a
  population that drops the constraint tail from every claim label passed 100/100 populations — the
  counter could not fire. Repair landed: `check_P2_constraint_power` derives, per world, a registered
  world with one negative evidence item from a valid source against the request's target claim, asserts
  the oracle reads `nocontra` INVALID, the claim label dead, and catches the tail-drop mutant (50/50
  worlds); v0 agreement is now reported `NO_POWER__ALL_CELLS_POSITIVE` and the claim is carried on the
  v1 worlds' oracle-negative cells only. (2) *"Hub-seeded ⇒ hub positive and top"*: true of any seeded
  atom, including the least connected — an identity presented as a direction. Repair landed: direction
  (i) of KS-T06b in its discriminating form (evidence question touching hub and specifics: hub first by
  raw activation, not first by surprise, planted popularity ranker differs), counted per world with the
  receipt asserting ≥ 1; direction (ii) kept as `NOT_DISCRIMINATING`, background as `IDENTITY`. (3) *Stale
  self-binding*: the receipt's own `bindings["kso_m1_mex1_population_v1.py"]` was left behind by a later
  edit (`populate(request=)`), and `KSO_M0_FREEZE_V1.json` froze the stale receipt — the
  `REPAIR_DOCUMENTED_NOT_LANDED` / `BINDING_OVER_UNCOMMITTED_BYTES` shape. Repair landed: receipt
  regenerated at the head, freeze record rebound in the same commit, and a unit test that recomputes
  every binding in both files against the committed bytes.

## Reopening rule

This ledger reopens on any of the following, each of which produces a *passing* artifact and is
therefore invisible to a green suite:

- a content binding is shown to have been taken over bytes that never entered version control, or
  over a working-tree file rather than a committed blob;
- a receipt-recorded repair is shown to be absent from the module it names, or a `repaired` entry is
  found that cites no landing commit and is asserted by no test that runs in CI;
- an imported issue or pull-request number is shown to resolve to an object other than the one the
  citing artifact describes;
- a published review target is shown to name a commit that is no longer the head of the branch under
  review, or a file declared immutable is shown to have been edited without disclosure;
- an independent review terminal is found to have been produced by, or on behalf of, a session that
  authored the work it reviews.
- a registered control is shown to be incapable of failing — a comparison of an expression with
  itself, a loop whose parameter changes nothing, or a verdict field written as a literal.

A verdict resting on any of these is withdrawn to `CANNOT_CHECK`. It is not converted into a repaired
defect, and a later green result does not erase how the earlier one was obtained.

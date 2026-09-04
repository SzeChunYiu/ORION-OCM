# ORION-V2 Failure Ledger

This ledger begins before implementation because research-process failures are scientific evidence. Failure history is append-only: a repaired defect remains visible, and a later green result may not erase how it was obtained.

## Retained failure classes

These are **failure vocabularies to keep detecting**, not a claim that every class currently has an open critical defect.

- `COVERAGE_GAP` — a declared knowledge-taxonomy branch lacks adequate native and changed-vocabulary search.
- `REPO_COLLISION` — a proposed omission or novelty was already represented in ORION V1.
- `DONOR_RECONSTRUCTION_FAILURE` — the native parent cannot yet be reproduced faithfully.
- `FALSE_STRUCTURAL_ANALOGY` — apparent cross-domain proximity disappears when assumptions or semantics are restored.
- `DONOR_PRODUCT_TIE` — the strongest donor composition matches the candidate ORION mechanism.
- `NONIDENTIFIABLE` — the intended distinction cannot be learned under the current probe/intervention family.
- `CENSORED_ROUTE` — a required source or evaluation route was unavailable and cannot be counted as a negative search result.
- `V1_PARITY_RISK` — a proposed V2 factorization may lose a frozen V1 capability.
- `PREMATURE_IMPLEMENTATION` — code or outcome-generating execution begins before the V1 freeze gate.
- `AUTHORITY_LAUNDERING` — local research or engineering evidence is used as scientific/novelty/adoption authority.
- `SILENT_MODEL_SUBSTITUTION` (corrected below) — a model endpoint serves a different model than the one requested, with a success status and no warning, so artifacts carry an unrecorded producing-model identity. Guard: log the **served** model id on every call and assert it against a frozen pin (fail closed); where an earlier campaign lacks that record, its artifacts may be reused only as a labelled non-gating panel. First observed 2026-09-02 (E40-m5′ Stage-2b/2c: `glm-5.2` → `glm-5.3`, `glm-4.6` → `glm-5.3-flash`; the m2/m3 served model is unrecoverable — 0 hits across 1,810 artifact files).
- `DEGENERATE_PROBE_STATISTIC` — a proposed statistic lacks the shared structure it needs to rank anything, so a null result measures the statistic rather than the hypothesis. A specialization of `NONIDENTIFIABLE` for constructed proxies. Guard: establish the statistic's dynamic range on the substrate **before** using it as a truth proxy. First observed 2026-09-02 (E40-m5′ Stage-2c: replica-consensus Jaccard J = 0.028 mean, range 0.009–0.052 — independent seed-replicas of the same cell share ≈3 % of their edges).
- `MANDATE_EXPLORATION_COLLAPSE` — a binding cycle-1 prompt mandate anchors an iterative arm on its mandated first config, which it then keeps re-choosing, so the search never samples the axis the objective varies along and a feedback-following control fails. Severity tracks mandate specificity and is model-dependent. Guard: run any mandated design alongside an unmandated planted control on the same channel before reading its trajectories. First measured 2026-09-02 (E40-m5′ Stage-2d: unmandated PASS 0.9877 reaching the optimum by cycle 2; regime anchor FAIL 0.9518; exact-seed mandate FAIL 0.0233 with `frac` never leaving 0.0 across nine cycles).
- `UNGATED_CONTROL_VERDICT` (corrected below) — an analysis records control verdicts without consuming them, so it can emit a scientific verdict while a registered control is failing. Guard: `evaluate_gates()` takes the control verdicts as input and refuses every gate when one fails, with a fixture proving the refusal fires. First observed 2026-09-02 (E40-m5′ Stage-2c analysis emitted a routing terminal while its planted control failed; repaired in the Stage-2d freeze, not retrofitted to the frozen Stage-2c script).
- `NONREPRODUCIBLE_FROZEN_ARTIFACT` — a "frozen" artifact is regenerated from its committed seed through iteration over an unordered container, so per-process hash randomisation yields a different artifact from the same commitment while every seed record, sha256 and freeze receipt remains internally consistent and correct: the custody chain is honest and the artifact is still not reproducible. Guard: regenerate the frozen artifact in a fresh process under at least two `PYTHONHASHSEED` values and compare hashes, and forbid RNG draws ordered by an unordered container (the reproducible-builds practice of rebuilding in a deliberately varied environment and comparing bit-for-bit, applied to a research split). **Near miss, not a realised defect** — unlike every other class in this list, no contaminated result was produced: it was caught before any protected artifact existed. Found by regenerating the split from a second process and comparing digests, not by a review or an auditor. First observed 2026-09-02 (FG70 `ORION-FG-L5-EXACT-V1`, PR #181: three generator planters drew decision assignments while iterating `set(...)` of signature tuples; fixed at the root and guarded by a cross-`PYTHONHASHSEED` behavioural test and a source-level test).

- `FORECLOSED_FAILURE_MODE` — a world is built so that the failure its primary endpoint measures **cannot occur in it**, so a hard validity gate fails and the study cannot be rescued without degrading an arm. Distinct from `NONIDENTIFIABLE`: the effect is not merely unlearnable under the probe family, it is absent by construction. The tell is a validity gate that survives a full revival attempt while every arm reads a clean zero on a detector proven to fire on the same records. The operative variable is **not** how expensive the evidence is to obtain — in ME-F1, finding a witness is exactly what the budget buys — but whether *"do I have warrant for this?"* is ever a **judgment call for the agent**. Guard: before freezing an endpoint, establish that its failure mode has dynamic range in the world as built, and specifically that the agent's own warrant status is **not** already unambiguous to it. A tool that returns `WITNESS_FOUND` versus `INCONCLUSIVE` in plain text, with an abstention option at no extra cost, leaves a competent agent no ambiguity to exploit and no self-deception channel — so over-assertion has nothing to arise from. First observed 2026-09-03 (ME-F1 G0e: `SIMPLE_DIRECT` laundered 0 of 121 claims, then 0 of 106 **bare verdicts** after the warrant field was removed from its interface entirely; ME-X1's 492 laundered updates arose where warrant status was itself a judgment. Routed `CANNOT_CHECK`; no protected campaign dispatched).

- `UNGUARDED_DEPENDENT_CHECK` — a registered condition makes one check undecidable, and the recoverability guard is written on the check whose *semantics* name that condition but not on a different check that also consumes the erased field. The second check re-derives from absent state and reports a definite verdict, so **"I could not check this" is silently converted into a substantive finding**. The tell is a three-way oracle-versus-implementations gate failing on one (cell, check) pair with no spread, while an arm-versus-arm concordance diagnostic reads 100 % — an arm-vs-arm comparison is structurally incapable of seeing a defect in an implementation the two arms *share*. Guard: for every censoring condition, declare the **set** of checks it makes undecidable — not the one check it is named for — and assert observed-equals-declared as a generator-validity invariant; keep the three-way comparison against the oracle as the hard gate and never let arm-vs-arm concordance stand in for it. Its repair carries a second trap, `REPAIR_THAT_DELETES_ITS_OWN_EVIDENCE`: extending the check table while leaving a "exactly one censored check" count invariant in force makes the generator re-draw every episode the fix was written for, so the gate goes green because the hard cases left the split. First observed 2026-09-03 (ME-X7 V1 protected run: G0b `ORACLE_SELF_AGREEMENT` 1244/1250 and G5 `S2_REPLAY_SUPPORT` 1244/1250, the same 6 instances, all `CENSORED_UNDECIDABLE × MODE_COMPUTATIONAL × DIRECT × C_ARTIFACT_DIGEST`, symmetric between the arms; routed `CANNOT_CHECK`, no arm verdict issued, re-frozen as ME-X7 V2 with both halves of the repair. Measured counterfactual: the table extension alone drops `CENSOR_ENV` from 8 draws to 2 and removes all six).

The nine classes below were relocated on 2026-09-04 from a refused standalone-paper candidate
(`DO_NOT_OPEN`, merge `323894f`, `papers/prospectuses/SILENT_FAILURE_MODES_ADMISSION_ASSESSMENT_V1.md`),
whose disposition named this ledger and the owning lane PRs as the durable homes for the findings.
They are **process-failure vocabularies, not a scientific result and not a novelty claim**: the
unification of vacuity and coverage as one mutation framework is Kupferman, CONCUR 2006, and the
empirical census slot — roughly a fifth of formulas trivially valid on a new design's first runs —
is Beer, Ben-David, Eisner and Rodeh, FMSD 18(2):141-163, 2001, p. 141, an IBM RuleBase experience
report rather than a methodologically specified census. Records, evidence grades and search scopes:
`research/failures/2026-09-silent-failure-modes-relocation/`.

- `VACUOUS_CONTRAST` — a treatment arm and its comparator dispatch to the same code with identical
  fields, so a reported agreement is `x == x`. **Not caught by the denominator question**, which is
  the reason it needs its own vocabulary rather than folding into a counter-never-ran class: a gate
  that never ran reports `0`, which invites "out of how many?"; a comparator with no contrast reports
  `1.000`, which reads as strength and has no denominator to interrogate. The catching question
  differs in kind — *could these two arms ever have differed?* Guard: assert the arms' code paths
  diverge, and report shared-implementation comparisons as shared rather than counting them as
  independent evidence. First observed 2026-09-03 (ME-X7 parent-fidelity: 8 vacuous comparison
  *items* spanning 6 of 11 gates, 4 fully vacated and 2 partially — items, not gates; development
  artifact only, no protected artifact ever existed). Second instance in the same window, found by
  a verifier asked whether a test could fail: the cross-`PYTHONHASHSEED` guard written against
  `NONREPRODUCIBLE_FROZEN_ARTIFACT` compares a run at `0` against parametrizations `0`, `1`, `12345`,
  so the `0` case compares a process against itself and passes on the unfixed code — the guard
  against vacuity contained a vacuous parametrization.
- `STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE` — a registered clause whose verdict is fixed by the
  construction of the stimulus, in either direction, so its result is a property of the design and
  not a measurement. Distinct from `NONIDENTIFIABLE` (a distinction unlearnable under the probe
  family) and from `DEGENERATE_PROBE_STATISTIC` (a statistic with no dynamic range): here the
  clause's own pass/fail is determined before any model is run. Both directions read as results —
  an unsatisfiable clause as an empirical negative, an unfailable one as a clean pass — and neither
  has a denominator. Guard: before freezing a clause, establish that both of its verdicts are
  reachable under the frozen stimulus, and check the exchangeability of the arms as a generator
  invariant. First observed 2026-09-04 (PRA GP2a: under R3 the two arms of all 120 frozen
  `F3_P2_CANON` instances are an exact source-exchange of one another while the label flips, so
  expected accuracy of any classifier is exactly 0.5 — **implementing the clause as registered would
  have produced a permanently unpassable gate reading like an empirical negative**; and two sibling
  clauses are unfailable because the two arms render identically, one of which ran and reported
  `probe_R2_true_removal_at_chance = True`, a zero-violation pass that could never have been
  otherwise).
- `HANDICAPPED_COMPARATOR` — a comparator is isolated by an asymmetry in the harness — a procedural
  rule its prompt omits, or a budget below the one its procedure needs — rather than by the mechanism
  under test. Distinct from `DONOR_RECONSTRUCTION_FAILURE`, which is an inability to reproduce the
  parent at all: here the parent is reproduced and then disadvantaged. Guard: assert prompt and
  budget parity between arms as a precondition on the comparison, and refuse the comparison until it
  holds. First observed 2026-09-03 (ME-F1: the mechanism's prompt names a procedural switch-tool
  rule the parent's does not while both hold the same information; the lane routed `CANNOT_CHECK`
  and made parity a hard precondition before any protected dispatch). **The repair magnitudes
  nominated for this class are `CANNOT_VERIFY` and must not be quoted**; the budget instance was
  additionally attributed to the wrong arm as nominated. The class is warranted on the mechanism
  and the precondition, not on a measured inversion.
- `TERMINAL_OVERSTATES_ITS_PROCEDURE` — a terminal string or receipt sentence claims more than the
  procedure that produced it: an impossibility where the evidence supports only non-recovery by one
  fitting procedure, or a margin borrowing the authority of a null that tested a different contrast.
  Distinct from `AUTHORITY_LAUNDERING`, which imports authority from outside the result. Guard: for
  each terminal, name the procedure that would have to fail for it to be false, and check that the
  registered statistic actually covers the comparison the prose draws. First observed 2026-09-03
  (ME-X6: `UNTYPED_AGGREGATE_CANNOT_REPRESENT_THE_CONJUNCTION_AT_MATCHED_INFORMATION` falsified by
  exhibition, 56/56 on the capability half against a 28/56 control, the comparator differing from
  the mechanism only in a weight dict it cannot set to zero; H-EXT-1: a +2.1 pp parent margin decided
  by 11 tasks under a registered bare threshold, beside a 0/2000 permutation null that tests the
  gated-versus-always-on contrast and not that margin).
- `REGISTERED_SCOPE_DIVERGENCE` — a runner evaluates a narrower clause than the one registered, and
  the clause passes on the half it evaluated. Guard: bind the machine-readable registration to the
  runner and assert clause-by-clause that observed scope equals registered scope; a narrowed clause
  is `CANNOT_CHECK`, never `pass`. First observed 2026-09-03 (PRA GP2a registered under R0 *and* R3
  in the design JSON, evaluated under R0 only; the rollup recorded `pass: true` while probing R3 all
  along at 0.594 and 0.542 against a 0.80 threshold).
- `UNPINNED_SUBSTRATE_CONDITION` — the served-model pin is satisfied by every artifact and the
  experimental condition still changes underneath a frozen prompt, because the pin certifies
  *identity* and not *behaviour*. A strengthening of `SILENT_MODEL_SUBSTITUTION`, not a duplicate:
  that class's guard fired correctly and was insufficient. Guard: record and gate on the behavioural
  envelope as well as the identity — output-token distribution against the prior run, the
  content-block types actually parsed, and the fraction of calls at the cap. First observed
  2026-09-03 (E30-R12: all 119 envelopes record the frozen served id `glm-5.3`; the identical frozen
  prompt at 61,557 input tokens completed in 763 output tokens five days earlier and hit the 6,000
  cap on 116 of the re-runs, the budget consumed by a `thinking` block the arm's parser never reads;
  `EXECUTION_NOT_COMPLETED__NO_ENDPOINT_READ`, 0 of 480 evaluations produced).
- `CHECKER_STAGED_ON_THE_WRONG_SUBSTRATE` — a cross-check's argument defaults point at a development
  corpus or an absent toolchain, so the check runs against something other than the thing it
  certifies. Guard: make the staged path and the toolchain identity assertions inside the receipt
  verifier, so that creating the stale artifact flips a check to FAIL. First observed 2026-09-03
  (ME-X3: the default `--dir` holds 20 development task_ids disjoint from the protected ids —
  contamination additionally requires an explicit `--report` pinned to the protected slot, which is
  the accurate and weaker form; and a bare-name toolchain default that on this machine exits 1 with
  "no default toolchain configured". Both near-misses; the toolchain one is **fail-loud** and is
  retained for the staging error, not as a silent mode).
- `CHECK_THAT_RUNS_AND_CANNOT_FIRE` — a check executes, on the right file, for the right string, and
  is incapable of reporting the defect it exists to catch. Guard: a CI job that **proves the gate can
  fail** against a fixture of genuine violations, with the fixture asserted to carry the real-world
  form of the defect. First observed 2026-09-03 (log-wrap blindness: pdflatex wraps its transcript at
  column 79 mid-word, so `Citation .* undefined` returns a clean log — measured 0 raw matches on a
  planted key with `grep -c LaTeX` at 20 as the control, and the committed verbatim fixtures break at
  exactly 68+11 and 69+10 characters; repaired sites proven by real pdflatex runs, and the blindness
  is **site-specific to three workflow gates**, since every other checker also accepts the unwrapped
  `There were undefined references.`). The class's sharpest member is the apparatus itself: the
  meta-gate built to prove those gates could fail planted **only unwrapped fixtures**, so all eight
  registered sites read green while the deployed gates were blind to the only form the defect takes —
  measured from the historical blobs as 8 site-policy entries and zero occurrences of `wrap` at
  `fbe647c`. Repairing the pattern alone would have left the gates exactly as inert. Two further
  members are recorded at reduced strength and must be quoted at it: an assertion that matched the
  very log line saying the file was **not** found, because the failure message contains the filename
  (a genuine inversion, never on `main`, and the consequence it would have licensed was blocked one
  layer up); and a vacuous-loop mechanism — a `continue` past every non-matching case, so a filter
  matching everything skips every assertion — verified by re-execution (unguarded exit 0 under the
  mutation, guarded exit 1) with the guarded exemplar present since its first commit and **no
  realised instance found**.
- `RENDERED_SURFACE_SUBSTITUTED_FOR_THE_FACT` — a rendered, filtered or proxied summary is read as
  the fact it summarises. The failure is **bidirectional**, which is what makes it more than a
  tooling note: toward apparent strength when it stands in for a claim ("nothing changed", "the
  suite is green"), and toward apparent failure when it stands in for a status, prompting the repair
  of a healthy artifact. Guard: before acting on a summary, execute the thing it summarises, and ask
  both what would have to run for this to be false **and** what would have to run for it to be true;
  use the unfiltered binary for any command whose result drives a decision. First observed
  2026-09-03. Its realised instances are **operational** — a command proxy returning `0` on a
  non-empty file and swallowing a requested `-c` count; `pytest` piped to `tail`, so the shell
  reported the pipe's status and a red suite read as green; `gh run list` rendering in-progress runs
  as elapsed time, which read as "timed out" would have prompted weakening a suite that was never
  failing. The programme's standing rule against asserting absence from absent printed output is
  what caught the third, which is evidence the detector was already held rather than discovered.

- `REPAIR_DOCUMENTED_NOT_LANDED` (corrected below) — a repair is analysed, decided and written into a record, and the
  record reads as though it shipped, while the artifact it names is unchanged. The check ran, the
  analysis is correct and the decision is sound; the gap is between the **record and the tree**.
  Distinct from `TERMINAL_OVERSTATES_ITS_PROCEDURE`, its closest neighbour: there the gap is
  *inferential* — the prose outruns what the analysis licenses, and is settled by re-reading the
  procedure — whereas here the prose is exactly warranted by the analysis and the question is a
  `git` one, whether a commit landing the change is an ancestor of `main`. It is not a check that
  never ran, not a contrast that could not exist, and not a rendered status trusted in place of the
  thing. Guard: a record asserting a repair must name **the artifact changed and the commit that
  changed it**, and that commit must be an ancestor of `main` (`git merge-base --is-ancestor <sha>
  origin/main`, run with a control that must fail); where a repair is deliberately deferred the
  record must say **documented, not applied**, state the reason, and place a pointer where whoever
  executes the artifact will meet it — *a correction nobody reads is a sentence nobody executes*.
  Deferring a fix with the reason stated is good practice; describing a deferred fix as *corrected*
  is the failure. First observed 2026-09-04 (OCM P0, PR #254:
  `research/orion-machine/receipts/OCM_WLL_P0_THEOREM_BUNDLE_RECEIPT_V1.json`, added `4bed0ce`
  2026-09-03 10:14 +0200, records under the field name `discovered_and_repaired_checker_defects`
  the entry *"correct endpoint-only guaranteed coordinates from one to zero and abstentions from
  five to six"* with `theorem_statement_changed: false` — while the module still pinned
  `I0_ENDPOINT_ONLY: (False, 1, 5)`. At branch head `17eb66b` five of six check runs failed —
  `native-recovery`, `foundation-reference`, `stochastic-reference`, `unified-reference`,
  `reference-tests` — each on the identical five tests of
  `tests/unit/test_ocm_wll_interface_hierarchy_exact.py`, with the pinned `(False, 1, 5)` exhibited
  in all five job logs, and stayed red for ~22 hours until `4cb6dca` landed exactly what the
  receipt already described. The field name is the tell: it asserts the defect was *repaired*.)
  Second instance the same day in an unrelated lane, and the sharper one because a lane caught it
  in its own work (ORION-paper PR #111, registry follow-up): `v2-papers/PAPER_REGISTRY.json`
  classes P-A and P-B as `…PRE_OUTCOME_SAMPLE_EFFECT_DEFECT_FOUND_AND_CORRECTED_2026_09_04` while
  the protocol it names was never amended — at ORION-V2 `main` `b2f7962`,
  `research/experiments/FM80_NATURALISTIC_TRANSFER_DECISIVE_PROTOCOL_V1.md` §8 still reads "at
  least 30 per domain" and §9.1 still reads "at least **10 percentage points**", the file carrying
  the single commit `baa9356` (its 2026-08-30 freeze) and the `.json` twin no correction key. What
  shipped was a sibling document,
  `research/experiments/fm80-audit/FM80_PRE_OUTCOME_DESIGN_CORRECTION_V1.md`. **Not amending was
  the correct call on authority grounds** — selecting a repair branch is a design act belonging to
  the lane that will execute the study, and choosing the cheapest branch after seeing the analysis
  is precisely what that protocol's §12 forbids — so the defect is **not** the deferred repair, it
  is the record claiming the repair landed. The status proposed in its place is
  `DEFECT_FOUND_AND_DOCUMENTED__REPAIR_BRANCH_UNSELECTED__PROTOCOL_TEXT_UNAMENDED_WITH_BINDING_PRE_EXECUTION_POINTER_ADDED`,
  with `protocol_text_amended: false` and `repair_branch: UNSELECTED__BELONGS_TO_THE_EXECUTING_LANE`.
  The mitigation that instance names is the guard worth keeping: a binding, explicitly
  **non-amending** pre-execution pointer placed **inside the defective artifact itself**, at §8 and
  §9, so whoever opens the protocol to run it meets the warning rather than the unmarked defective
  floor. **Near miss recorded on the mitigation layer, not a realised defect:** as of ORION-V2
  `main` `b2f7962` and ORION-paper `main` `9c4a631` neither half of that mitigation has landed —
  the pointer exists only in ORION-V2 PR #264 (open, unmerged) and the registry re-statement only
  in ORION-paper PR #111 (open, `CONFLICTING`), where the `_CORRECTED` string is still live — and
  the registry's `binding_pre_execution_pointer_added_to_protocol: true` asserts the state of a
  file in a **different repository**, with nothing binding the two. It is recorded because it is
  this class's own tell reappearing at the mitigation layer, in exactly the form the guard above
  exists to catch.

- `INTERFACE_ASKS_FOR_WHAT_IT_WITHHELD` — the harness presents an arm a truncated view of its
  workspace and then asks the arm to return information only the untruncated view contains
  (verbatim context lines and line numbers for a unified diff), so the arm's output fails at the
  interface for every arm alike and the failure is scored as the arm's. Distinct from
  `HANDICAPPED_COMPARATOR` (an asymmetry between arms; here every arm is handicapped equally, so
  no paired contrast notices) and from `UNPINNED_SUBSTRATE_CONDITION` (the channel; here the
  channel answered every call and the served id held). The tell is an apply-failure rate that
  is flat across arms of very different capability, with the non-applying patches declaring
  edit positions beyond the shown prefix of a file the snapshot cut. Guard: the interface is a
  registered condition — the edit contract asks only for what the presentation showed, the
  presentation policy exempts every file the task names from truncation, and a per-envelope
  `interface_receipt` (interface id and fingerprint, files shown, mentioned files truncated) is
  gated for homogeneity ahead of any endpoint, so "every patch applied" can never be read out
  of "the model saw nothing". First observed 2026-09-04 (E30-R13 read-only attribution,
  `research/experiments/e30-r14/results/E30_R14_R13_APPLY_FAILURE_ATTRIBUTION_V1.json`: of the
  205 canonical-but-non-applying patches, **152 edit a region the 30 000-character per-file
  snapshot never showed**; 201 of the 346 failures are unrecoverable by any reader of the
  archived text because the quoted context does not occur in the file; apply-failure
  0.69–0.78 on all four arms including the parent federation. The presentation replication was
  controlled against the archived `source_snapshot_truncation` receipts, and a fabricated
  context block returned 0 anchors while a real one from the same file returned exactly 1).

### Corrections to entries above, recorded rather than applied

This ledger is append-only, so two earlier entries are corrected here rather than edited in place.

- `UNGATED_CONTROL_VERDICT` above says an analysis *"records control verdicts without consuming
  them"*. The admission assessment's re-read of the artifact corrects the mechanism: `evaluate_gates()`
  **never receives** the control verdicts; the rollup writer records them as a sibling of `analysis`.
  The corrected form is the stronger one — the function cannot decline to consume what it is never
  passed — and the class, its guard and its first-observed date are unaffected. The same re-read
  found the stale-terminal consequence to be **counterfactual**: the repository contains zero
  programmatic consumers of that rollup.
- `SILENT_MODEL_SUBSTITUTION` above names two substitutions. The probe recorded **three** across
  four requests, all at HTTP 200: `glm-5.2`→`glm-5.3`, `glm-5.1`→`glm-5.3` and
  `glm-4.6`→`glm-5.3-flash`, with `glm-5.3`→`glm-5.3` as the negative control. The corollary belongs
  with the class: a run that logs **no** served id has an *inferred*, not a verified, producing
  model, and must be labelled as such.

- `REPAIR_DOCUMENTED_NOT_LANDED` above records, of the mitigation shipped for its second instance,
  that *"neither half of that mitigation has landed"* and that the pointer and the registry
  re-statement exist *"only in ORION-V2 PR #264 (open, unmerged)"* and *"only in ORION-paper PR #111
  (open, `CONFLICTING`)"*. That was true when verified, at ORION-V2 `main` `b2f7962` and ORION-paper
  `main` `9c4a631`. **It was false by the time the entry merged.** Both PRs merged in the interval
  between verification and merge: ORION-V2 #264 at 2026-09-04T07:34:40Z (`d3981d4`) and ORION-paper
  #111 at 2026-09-04T07:39:03Z (`f9bb8e4`), against the entry's own merge at 07:42:16Z (`ffa5c34`) —
  three minutes and seven minutes ahead of it. Both merge commits are ancestors of their respective
  `main` (`git merge-base --is-ancestor`, run with a negative control — `4cb6dca`, still on the open
  PR #254 branch — correctly reported not-an-ancestor). Verified on `main`: the protocol carries the
  binding pre-execution read at §8 and §9 (`binding` ×3 case-insensitively, `pre-execution` ×2,
  `pointer` ×1, `unsatisfiab` ×2, against `percentage points` ×1 as a control proving the search
  fires) and `pre_execution_binding_reads` in the `.json` twin with `non_amending: true` and
  `selects_no_repair_branch: true`; the registry now carries `FOUND_AND_DOCUMENTED` for P-A and P-B
  with `FOUND_AND_CORRECTED` gone from both.
- **This is the class in the mirror, and it is a distinct variant that the entry must not flatten.**
  In both founding instances the record was false *when written*; here the record was true when
  written and went **stale between verification and merge**. Overstatement and staleness produce the
  same artifact — a record describing a state the tree does not have — and the same guard catches
  both, which is the point: a repair record that names no commit cannot be checked for either, while
  one that names a commit makes both detectable by a single ancestry question. The interval is not a
  process failure to be drilled out; it is why the guard is written on the commit rather than on the
  prose.
- **Strength, on the two halves separately.** The mitigation-layer near miss rested on two facts, and
  only one of them expired. The *unlanded* half is void and is withdrawn: both halves have landed.
  The **cross-repository half survives the merge unchanged and is the part worth keeping** —
  ORION-paper's registry asserts `binding_pre_execution_pointer_added_to_protocol: true` about a file
  in ORION-V2, naming no commit there and no ancestry check, so nothing binds the two. Both artifacts
  landing does not create a binding: the next edit to either desynchronises them silently and no gate
  would notice. It remains a **near miss** on the ledger's own legend — the assertion is currently
  true, and no contaminated result was produced by it — but it is a standing structural hazard, not a
  transient one.
- **Guard extended, and the extension is the operative output of this correction:** where a repair
  record asserts a state of an artifact in **another repository**, it must name that repository's
  commit and the ancestry must be checked *there*, in that repository, against that repository's
  `main`. A cross-repo assertion carrying no foreign sha is unverifiable by construction and must be
  recorded as `CANNOT_CHECK`, never as a fact.
- The **second instance's own classification is unchanged and does not soften.** It was realised, not
  a near miss: `..._PRE_OUTCOME_SAMPLE_EFFECT_DEFECT_FOUND_AND_CORRECTED_2026_09_04` stood on
  ORION-paper `main` describing a protocol that had never been amended. It is now **remediated**, and
  remediation is not retroactive absolution — this ledger's preamble holds that a repaired defect
  remains visible and that a later green result may not erase how it was obtained. Everything else in
  the entry stands as written: the FM80 protocol text is *still* unamended on `main` (§8 "at least 30
  per domain" ×1, §9.1 "**10 percentage points**" ×1), which is what the pointer was placed to make
  survivable rather than to hide; not amending remains the correct call on authority grounds; and the
  first instance is untouched, its five red checks and the pinned `(False, 1, 5)` being a realised
  defect on any reading.

Every concrete failure must preserve its source identities, affected claims and reopening conditions. No failure may be deleted merely because a later theory is more successful.

- `FREE_TEXT_CATEGORICAL_ENDPOINT` — a categorical endpoint is typed as a free string at the arm
  interface and scored by exact equality, so the registered primary measures each arm's *rendering
  habit* (whether it happens to emit the bare token) and not its decision. A strengthening of
  `HANDICAPPED_COMPARATOR` in the other direction: no arm is isolated by a prompt asymmetry, every
  arm is handicapped by the same untyped field, and the handicap is unequal only because the arms'
  prose habits differ. Guard: an endpoint with a finite admissible set crosses the interface **as**
  that set — named in the contract, enumerated in the output schema, rejected on non-membership — and
  a descriptive rendering census of every wrong row is run before any exact-match contrast is read as
  a decision-level result. First observed 2026-09-04 (FG80 R2: `representation_feature` typed
  `"string"`; 34–50 of every arm's 80 answers carried the correct id decorated — `H_X = 1`,
  `H_X is active (value 1)` — and were scored wrong; the −19-task paired deficit of the full
  machine-native arm against the simple direct control, p = 4.3e-03, becomes −3 tasks, p = 0.375,
  under a conservative normalisation that keeps every conjunction, negation and `= 0` wrong. Zero
  rendering variants in the other thirteen studies of the same suite, whose endpoints are not
  free-string categoricals. The R2 terminal and the P-F trigger verdict are **not** altered by the
  census, which is descriptive; the prospective test is `research/experiments/fg80-r3/`, frozen
  before dispatch with the ceiling row named as *no dynamic range*, never as a tie the mechanism
  earned).

## Retained concrete failure records

- `research/experiments/fg80-r3/FG80_R3_PRE_DISPATCH_RECEIPT_V1.md` — FG80 R2 rendering census (descriptive, non-gating, four controls PASS) attributing the P-F negative to `FREE_TEXT_CATEGORICAL_ENDPOINT`; R3 interface re-run frozen (seed 20260904, 400 dispatches) with dispatch deferred to the frozen channel's window. Carries the class above. Also records a pre-outcome detector repair caught by the selftest (`H_A AND H_B` was normalised to `H_A` by a `\b` that matched at the space) and the corrected census it produced.
- `research/failures/2026-08-parallel-wave3-ownership-collision/README.md`
- `research/failures/2026-08-wave4-recovery-and-ci-preterminal-defects/README.md`
- `research/failures/2026-08-wave5-epoch-and-chain-binding-defects/README.md`
- `research/failures/2026-08-parity-preflight-test-expectation-drift/README.md`
- `research/failures/2026-09-silent-failure-modes-relocation/README.md` — twenty-five relocated session records behind the nine classes above, each with its evidence grade, its corrections and the scope of any absence claim. Four are `CANNOT_VERIFY` and are recorded as such; one group (`05`) is explicitly **operational hygiene rather than a scientific failure class**, per the admission assessment §3 and §9. That group is named here rather than classed, because
  recording an operational hazard as a scientific failure class would repeat the error the refusal
  identifies — bundling unlike things because each was surprising. The hazards, with the test that
  settles each: a PR can read `state: MERGED` while its work is absent from `main`, when it was
  merged into an integration branch whose own PR had already landed
  (`git merge-base --is-ancestor <mergeCommit> origin/main`, control required); `--delete-branch`
  closes every PR stacked on the deleted branch as its base, and recovery is a new PR — the cascade
  is proven by timeline events, while the refusal to reopen rests on first-party testimony only;
  a multi-commit squash-merge makes landed work look unlanded in two mutually confirming ways, and
  the sound test is a tree-hash comparison for the path; a two-dot diff folds the other side's
  additions into the deletion column, which is where a large phantom-deletion count comes from —
  three-dot is the form that isolates a side; a pipe reports the pipe's exit status, so a red suite
  reads as green; and a command proxy can return `0` on a non-empty file, which is what authorises
  a destructive overwrite. The record states its own contamination limit: the corpus was collected while a paper was being assessed from it, which changed what lanes looked for and how they worded it — a performative-evaluation instance the programme already has a coordinate for (P-D's C09), with no model of that response, so nothing in it may be read as a prevalence or a base rate.
- `research/experiments/e40-matched/E40_M5P_STAGE2D_OUTCOME_RECEIPT.md` — E40-m5′ Stage-2d: the Stage-2c control failure is attributed to the cycle-1 mandate (D2 `PROMPT_IMPLICATED`, all controls PASS); the model channel alone is exonerated, though the m3-form arm passed under the earlier model and fails now, so the cause is an interaction whose magnitude is not estimable (the m2-era model is unrecoverable). Stage-2c stays `CHECKER_INVALID__NO_VERDICT`; the E40 line stays open.
- `research/experiments/e40-matched/E40_M5P_STAGE2C_OUTCOME_RECEIPT.md` — E40-m5′ Stage-2c: registered planted positive control FAILED (terminal quality 0.6412 vs 0.9877 in m3, 1.0 in m2), so the campaign's computed routing terminal was **not** filed; disposition `CHECKER_INVALID__NO_VERDICT` and the E40 line stays open. Carries the three classes above. Cause discrimination is frozen as Stage-2d (`E40_M5P_STAGE2D_PLANT_DISCRIMINATION_DESIGN_V1`).
- `research/experiments/me-x7/ME_X7_OUTCOME_RECEIPT.md` — ME-X7 V1: hard gate G0b failed on a lane defect (`UNGUARDED_DEPENDENT_CHECK`); routed `CANNOT_CHECK`, witness terminal `NONE`, no arm verdict, protected seed burned. Re-frozen as `research/experiments/me-x7-v2/` with the two coupled corrections its §7 prescribes, and closed there: the V2 protected run passed every hard gate with `cross_implementation_agree` 1250/1250 and `S2_REPLAY_SUPPORT` 1250/1250 **while the cell that exposed the defect was still in the split** (`CENSOR_ENV` 11 draws, 7 in `MODE_COMPUTATIONAL`) — `research/experiments/me-x7-v2/ME_X7_V2_OUTCOME_RECEIPT.md`.

- **Operational hygiene, 2026-09-04 (named, not classed, per the group-05 rule above)** — two hazards that
  each produce a *green* artifact and are settled by `scripts/pr_merge_gate.py` (`docs/MERGE_GATE.md`),
  a five-field merge gate with a distinct could-not-check exit, mutation-tested on every field:
  (a) **a pair of individually green PRs across a live freeze** — #282 (`538e017`) froze
  `research/experiments/me-f1-r3/results/ME_F1_R3_FREEZE_V1.json` binding `me-f1/mef1_arms.py` by sha256;
  #276 (`dc27ced`) changed that file 70 minutes later and merged; `main` was red on
  `test_frozen_state_if_present_matches_inputs` until #286 (`d1dfd12`) re-pinned it. No per-PR check can see a
  pair; the gate's field 5 scans the base at merge time and, replayed at `d696d74` (main before #276), refuses
  #276 naming the freeze and its owner, and passes #289 as the no-alarm control.
  (b) **a job cap presenting as `cancelled`** — measured through the jobs API on `main@b53dba5` (last 25 runs
  of every workflow), the five full-suite jobs run at p95 9.9–10.3 min under 10–12 min caps; every cancelled
  job in the sample (4 of 100) died at 10.0–10.2 min with the pytest step cancelled and no failed step, and
  #283/#288/#290 read red on it while `gh run view --log-failed` printed nothing (empty on cancellation by
  design). Two lanes nearly debugged non-existent failures. The gate's field 4 reads `cancelled` (or any
  incomplete status) as could-not-check with the advice "re-run the workflow on this head", never as a
  failure and never as a pass; the caps are resized at >= 2x the measured p95 in #292. The test that settles
  each: (a) `--replay` against the historical pair; (b) the jobs API step list for the run (a cancelled step
  with no failed step is a cap or a manual cancel, not the code).
  (c) **the FM40 stranding class, recurring (2026-09-04)** — #290 passed the gate's five fields and
  squash-merged onto `research/ocm-convergence-map-20260904` (the #289 branch, already landed) as
  `54712cc0`, which is not an ancestor of `main`; the PR was stacked and never retargeted after its base
  landed, and the gate had no base-branch field. Same mechanism as #187 (merged to the integration branch,
  never to `main`; recovered by #215, recorded in `research/failures/2026-09-silent-failure-modes-relocation/
  05-operational-tooling-and-version-control.md`): `state: MERGED` is not evidence that anything reached
  `main`. Recovered by #296 (cherry-pick reland onto `main`). The gate now carries **field 0**, checked
  first: `baseRefName == <default branch read from the API>`; any other base is refused with "retarget
  before gating", an unreadable default is could-not-check, and the report prints whether the base still
  exists and whether its tip is already an ancestor of the default. The test that settles it: the recorded
  #290 pre-merge snapshot is refused on field 0 alone while #296 and #289 pass.

Their current closure classification is machine-recorded in:

`research/closure/CRITICAL_FAILURE_DISPOSITION_WAVE06_V1.json`

That receipt may report zero **known open critical local correctness/integrity/authority defects** while protected scientific evidence remains unresolved in other gates. In particular:

- missing independent semantic evaluators are G1/G5 custody evidence;
- strongest parent comparator identity is G4 evidence;
- protected parity and naturalistic/prospective value are G1/G5 evidence;
- scientific novelty/publication/field authority is G8 external authority.

These are not silently converted into repaired defects.

## Reopening rule

The critical-failure gate reopens if current CI exposes a real correctness/integrity/authority defect, if a hostile control demonstrates fail-open behavior, if an identity/custody binding is bypassable after outcome access, or if a historical repair no longer reproduces.

It reopens equally on the three conditions the 2026-09 relocation earns, each of which is invisible
to the clauses above because each produces a *passing* artifact:

- a gate is shown to be incapable of reporting the defect it exists to catch — including a
  meta-gate whose fixtures do not carry the real-world form of that defect;
- a comparator is shown to share a code path with its treatment arm, or to be isolated by a prompt
  or budget asymmetry rather than by the mechanism under test;
- a registered clause is shown to be structurally determined — unsatisfiable or unfailable under the
  frozen stimulus — or to have been evaluated at a narrower scope than registered.

A verdict resting on any of these is withdrawn to `CANNOT_CHECK`; it is not converted into a
repaired defect, and a later green result does not erase how the earlier one was obtained.

It reopens on a fourth condition, appended 2026-09-04 for `REPAIR_DOCUMENTED_NOT_LANDED`. The three
conditions above were written to fire on a *passing* artifact; this one is invisible to all of them
because it is not a property of any artifact's verdict at all — of its two founding instances the
artifact was **failing** in one and had **never been run** in the other, and the record read
repaired in both:

- a record asserting a repair cannot name the commit that landed it, or names one that is not an
  ancestor of `main` (`git merge-base --is-ancestor <sha> origin/main`, run with a control that must
  fail — the same test this ledger already requires for a PR reading `MERGED` whose work is absent
  from `main`), or describes a deliberately deferred repair as *corrected* rather than *documented,
  not applied*.

Here the correction is to the **record**, which is amended to say what the tree holds; the
underlying analysis and the decision to defer are not thereby withdrawn, and a later commit landing
the repair does not erase the interval in which the record overstated it.

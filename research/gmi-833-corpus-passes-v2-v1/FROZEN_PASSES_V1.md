# GMI #833 corpus identification passes v2 — FROZEN pass definitions + judgment protocol V1

**Schema:** `GMI_833_CORPUS_PASSES_V2_FROZEN_PROTOCOL_V1`
**Written and committed BEFORE any detector implementation or run** (pre-registration; ledger
REMAINING_WORK_V1.md at `14276c20` is the queue authority).
**Parent:** #833 Section B identify-boxes L42, L44–L56, L58.
**Reused authorities (frozen, never re-derived here):**
census `research/gmi-833-corpus-census-v1` (source `2fffb144`, result blob `861b1ba1`, 22,553
objects); #939 adjudication freeze `research/gmi-833-corpus-audit-close-v1/FREEZE_V1.md`
(verdict taxonomy + evidence rules); #949 `research/gmi-833-depgraph-adjudication-v1`
(duplicate-group semantics: groups key on `statement.lower()`; 1,652 content-hash groups,
857 GAP-DUPID); rescore v2 `research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json`
(197 rows; support_kind 63 ANALYTIC_PROOF / 49 EXACT_FINITE_CERTIFICATE / 11
ANALYTIC_PROOF_PLUS_EXACT; 62 census-vs-observed proof-mode disagreements);
terminology crosswalk `research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md`
migration rule table (17 legacy→replacement rows) + gate token map.

## 0. Populations (frozen)

| pop | definition | N |
|---|---|---|
| P1 | census scientific_objects at frozen census SHA | 22,553 |
| P2 | THEOREM_SCORES_V2 rows (merged #948 state) | 197 |
| P3 | `research/gmi-*` packages on this branch base `14276c20` | 230 |

Repo-tree scans (P3) run at base `14276c20` and are labeled with that SHA; P1/P2 screens stay
at their frozen SHAs. No drift between the two is conflated: every flag records which
population/SHA produced it.

## 1. Tiering (frozen — realism about scale)

- **Tier M (mechanical screen):** detectors over all of P1/P2/P3. Output is a FLAG with the
  matched pattern and evidence locator. A flag is a candidate, never a verdict.
- **Tier S (stratified deep-read):** per pass, `n = min(30, flags)` flagged candidates,
  stratified by `(audit_disposition, object_class)` proportional allocation, every non-empty
  stratum >= 1, largest-remainder to exactly n, `random.Random(833212)` (seed disjoint from
  #939's 833200) over members sorted by `(source_path, source_locator, object_id)`.
  Sampling rate printed per pass in the receipt.
- **Tier A (full adjudication):** (i) every candidate whose Tier-S read returns a
  CONFIRMED-class defect; (ii) every candidate touching a GREEN-mainline claim-bearing object
  (the #939 (a) population — few, claim-bearing, highest downstream leverage).
- Everything screened but not deep-read carries status **SCREENED-NOT-ADJUDICATED** — an
  explicit gap state, distinct from clear/CONFIRMED, never silently absorbed.

## 2. Verdict vocabulary (frozen)

Tier-A verdicts reuse the #939 taxonomy verbatim: `CONFIRMED, OVERSTRONG, DUPLICATE,
COMPUTATION_ONLY, ENUMERATION_SUBSTITUTED, POST_HOC_ASSUMPTION, UNKNOWN` — plus the
pass-specific positives declared below (`DECLARED_FINITE_ONLY`, `ANALYTIC_SUPPORTED`,
`TWO_ROUTE`, `PROSPECTIVE_DEMONSTRABLE`, `REGISTERED_EXPLICIT`, `DECLARED_HORIZON`,
`RESIDUAL_STATED`), each of which is a no-defect-at-registered-scope record, never a proof
the underlying theorem is true. Detector flag classes: `TERM_DUP_CAND, ENUM_ANALYTIC_CAND,
COMP_ONLY_CAND, NO_INDEP_IMPL, POST_HOC_CAND, GRAMMAR_TARGET_CAND, COST_FORCES_CAND,
MACRO_PRIVOP_CAND, IID_STAT_CAND, FIN_HORIZON_CAND, ALT_ACCT_CAND, ENCODING_SENS_CAND,
SEARCH_SENS_CAND, PARENT_REDISC_CAND`.

## 3. Pass specs (pattern → flag rule → adjudication evidence → validation)

### PASS-L42 — duplicates under different terminology (the detector build)

- **Pattern.** Two census objects state the same substantive claim; their statements differ
  textually ONLY by tokens belonging to one crosswalk migration row (legacy term on one side,
  a sanctioned replacement on the other), or by that row's inflectional/gate-invisible forms
  (y→ies plurals, underscore-joined, hyphen/space variants). This is the duplicate class the
  content-hash (`statement.lower()`) and DUPID detectors cannot see.
- **Detector (mechanical).** `mask(s)`: lowercase statement, every token in a crosswalk
  equivalence class (legacy + replacements + inflections) replaced by a row marker `⟨Rk⟩`.
  Bucket P1 by sha256(mask); a bucket with >= 2 distinct raw-statement hashes AND >= 1
  differing token position whose two sides both belong to the SAME crosswalk row is a
  TERM_DUP_CAND group. No pairwise scanning (masked hashing is O(N)).
- **Adjudication.** Per candidate group, #939 DUPLICATE rule: textual check that the pair is
  a restatement without registered residual vs. a same-substance re-declaration with
  different registered scope. Verdicts DUPLICATE / DISTINCT / UNCERTAIN with reason + the
  unifying row id.
- **Validation (before first real run; a detector's first real run must not be its
  calibration).** (a) *Recall plant:* 20 synthetic variant pairs built by applying the
  crosswalk to real census statements — must flag >= 19/20. (b) *No-alarm plant:* 200
  real same-package statement pairs differing in NON-crosswalk tokens only — must flag 0.
  (c) *Semantics anchor:* raw-hash grouping (mask disabled) must reproduce the census's
  1,652-group count and the 1,586/66 verdict split untouched. (d) *Specificity anchor:*
  the 66 known-DISTINCT content-hash groups must yield 0 TERM_DUP flags.

### PASS-L44 — finite enumeration where an analytic proof is possible

- **Pattern.** A claim whose support is a finite enumeration/certificate, where the statement
  quantifies over a parameterizable family with algebraic structure such that an analytic
  argument is plausibly available, and the enumeration is not declared as the registered
  method. (#939: declared enumeration is fine; undeclared substitution is not.)
- **Population.** All 49 EXACT_FINITE_CERTIFICATE P2 rows (full read — Tier A direct: the
  ledger assigns this population per-object verdicts) + Tier-M screen over P1
  COMPUTER_ASSISTED_EXHAUSTIVE claim-class objects for candidates beyond P2.
- **Flag rule (mechanical pre-screen).** Row statement quantifies universally over a family
  (quantifier `forall…`) AND justification cites only enumeration/certificate artifacts AND
  no sibling P2 row of the same package carries ANALYTIC_PROOF/ANALYTIC_PROOF_PLUS_EXACT on
  the same subject file.
- **Adjudication (per object).** Read statement + citation paths. Verdict
  `ENUMERATION_SUBSTITUTED` (analytic plausibly available, undeclared) /
  `DECLARED_FINITE_ONLY` (enumeration is the registered method — e.g. census of a registered
  finite microscope with no closed-form target) / `UNKNOWN`, each with reason.

### PASS-L45 — analytic claims supported only by computation

- **Pattern.** A row typed ANALYTIC_PROOF whose support artifacts are computational only
  (no proof-bearing document), i.e. #939 COMPUTATION_ONLY.
- **Population.** All 63 ANALYTIC_PROOF P2 rows.
- **Flag rule.** citation_paths contain zero proof-bearing documents (`.md`/proof sections)
  OR justification string cites only runs/certificates/enumeration. Then Tier-A read of the
  flagged (full adjudication — population is small and claim-bearing).
- **Verdicts.** `ANALYTIC_SUPPORTED` (non-computational proof found at registered scope) /
  `COMPUTATION_ONLY` / `UNKNOWN`. The 62-row census-vs-observed disagreement table is an
  input: rows where census said ANALYTIC_DEDUCTIVE but observed support is computational are
  priority reads.

### PASS-L46 — computational claims with no independent implementation

- **Pattern.** A package's computational claims lack the two-route pattern: no independent
  second implementation (independent oracle / materially distinct executor) with an agreement
  artifact for the claimed quantities.
- **Screen (package-level, mechanical).** Package has >= 1 P1 claim-bearing object with
  computational proof mode (FINITE_EXECUTABLE_CERTIFICATE, COMPUTER_ASSISTED_EXHAUSTIVE,
  STATISTICAL_EXPERIMENT, MECHANIZED_PROOF, EMPIRICAL_EXPERIMENT). Two-route status from the
  package tree: `independent_oracle_v1.py`+`ORACLE_RESULT_V1.json` (g0-* pattern) OR two
  distinct executors of the same quantity with an agreement/cross-check artifact (the #863
  BFS-vs-Floyd–Warshall and exhaustive-vs-branch-and-bound precedents). Verdict
  `TWO_ROUTE` / `SINGLE_ROUTE` / `NO_COMPUTATION`; SINGLE_ROUTE flags its computational
  claim objects NO_INDEP_IMPL.
- **Adjudication.** Tier-S read of SINGLE_ROUTE packages (rate printed): verify the mechanical
  verdict (oracle exists but unused = SINGLE_ROUTE stands; second route hiding under another
  name = TWO_ROUTE with citation).

### PASS-L47 — assumptions introduced after observing outcomes (post-hoc)

- **Pattern.** Freeze/assumption artifact committed at/after the result it claims to precede;
  prospective-ness non-demonstrable from custody metadata (#939 evidence rule; registered
  instance INSTANCE-CONFIG-FREEZE-SEPARATION, 10–13 s gaps).
- **Screen (mechanical, git-history).** Per P3 package: first-commit time of FREEZE*/freeze
  authority file vs first-commit time of each RESULT*/receipt artifact vs config/executor
  edits between them. Flag POST_HOC_CAND when a result precedes its freeze, or freeze+result
  land in one commit, or a config edit lands within 120 s AFTER the freeze it parameterizes
  (tight-gap class of the registered instance).
- **Adjudication.** Tier-A on flags: `PROSPECTIVE_DEMONSTRABLE` (ordering clean once
  path-followups are read) / `POST_HOC_ASSUMPTION` (defect confirmed) / legit-late-change
  only with a typed POST_HOC marker (POST_FREEZE_*), per #939.

### PASS-L48-SCREEN — grammar encodes target (IDENTIFICATION ONLY; aj owns resolution)

- The L48 residual (AJ9 no-smuggling contract response) is aj-lane; this package does NOT
  touch it and does NOT tick L48. Corpus-wide identification screen only: run the A1/A2
  registered detectors (architecture-name/macros denylist + privileged/semantic-operator
  scan) over every P3 package carrying grammar/DSL/primitive definitions; flag
  GRAMMAR_TARGET_CAND where grammar token set or operator costs overlap the target family
  naming or a privileged operator appears. Output is a screened/flagged disposition table;
  verdicts stay with the owning lanes.

### PASS-L49 — cost models that structurally force the claimed winner

- **Pattern.** A claimed winner selected under a cost/scalarization model that was never
  audited for forcing (no #855-A3-style winner-reversal / zero-cost-privileged-operator /
  positive-scalarization check at package scope).
- **Screen.** P3 packages whose claim artifacts register a cost/scalarization (mechanical:
  cost model / scalarization / weighted / budget-profile tokens in freeze/RESULT files) AND
  whose winner claims cite it; flag COST_FORCES_CAND where no cost-audit artifact exists in
  the package tree. Adjudicate Tier-S: `AUDITED` (audit artifact found+read) /
  `UNAUDITED_COST_DEPENDENT` / `NOT_COST_DEPENDENT`.

### PASS-L50 — hidden architecture macros / privileged operators

- **Pattern.** Grammar/operator definitions embedding architecture names/macros, or
  operators with privileged (zero/hidden) cost — beyond the packages the A1/A2 tools already
  covered.
- **Screen.** Corpus-wide A1 denylist + A2 semantic-operator run over P3 grammar/operator
  definition files (ledger L50 wording verbatim: "corpus-wide run of the A1/A2 denylist +
  semantic-operator detectors as census dispositions"). Flags MACRO_PRIVOP_CAND with the
  matched token + file. Tier-S adjudication; lexical hits are screens, not findings (A1
  design note).

### PASS-L51 — hidden independence/iid/stationarity assumptions

- **Pattern.** Statement or justification PRESUPPOSES iid / independence / stationarity /
  ergodicity / exchangeability / time-homogeneity, but no registered assumption in the
  package carries it (statement-level presupposition vs package-level registration; the
  census per-object `assumptions` fields are empty by construction and belong to the L34
  lane — this pass flags, never retrofits).
- **Detector.** Term/structure scan (incl. `iid`, `i.i.d.`, `independent(ly) …identically`,
  `stationar*`, `ergodic*`, `exchangeab*`, `time-homogeneous`, `fixed … proposals/kernel`,
  `drift-free`, `i.i.d. kernel`) over P1 statements+justifications of computational rows;
  cross-check the package's registered assumptions docs for the same property.
  Flag IID_STAT_CAND when used-but-unregistered at package level.
- **Adjudication.** Tier-S read: `REGISTERED_EXPLICIT` / `HIDDEN_BUT_USED` (defect) /
  `NOT_PRESUPPOSED` (false positive class recorded).

### PASS-L52 — hidden finite-horizon assumptions

- **Pattern.** Universal claim whose evidence is bounded by a horizon/budget/depth/timeout
  that the statement and registered scope do not declare.
- **Detector.** P1 rows with quantifier_class in {UNIVERSAL, FINITE_EXACT} whose
  justification/citation artifacts contain horizon tokens (`budget`, `steps`, `horizon`,
  `episode`, `depth`, `timeout`, `termination`, `step limit`) while the statement +
  registered scope string do not. Declared-horizon rows (rescore scope strings like
  `budget <=7`) are the no-alarm anchor class. Flag FIN_HORIZON_CAND; Tier-S read:
  `DECLARED_HORIZON` / `HIDDEN_FINITE_HORIZON` (defect) / `NOT_HORIZON_DEPENDENT`.

### PASS-L53 — claims failing under alternative reasonable resource accounting

- **Pattern.** A selection/winner claim under one resource scalarization without an
  alternate-scalarization replica (#863 R4 pattern; #891 registered the counterexample
  class: same-semantic grammar pair reversing selection under unchanged positive weights).
- **Screen.** P3 packages with scalarization-dependent selection claims (from L49's screen)
  lacking any alternate-scalarization artifact; plus re-verification read of the registered
  #891 counterexample as the confirmed class anchor. Flag ALT_ACCT_CAND; Tier-S:
  `TESTED_STABLE`, `TESTED_SENSITIVE` (defect, like #891's registered reversal),
  `UNTESTED_SCALARIZATION_DEPENDENT` (defect-of-omission, identification output).

### PASS-L54 — claims sensitive to arbitrary encoding choices

- **Pattern.** Claim depending on a surface encoding/presentation/labeling without a remint
  / alternate-encoding control (#863 R2 verdict vocabulary: ENCODING_SENSITIVE /
  CANNOT_AUDIT_ENCODING; #875 registered slice = remint controls with independent oracle).
- **Screen.** P3 packages whose artifacts reference encodings/presentations/label
  permutations/relabeling, lacking a remint/bijection-control artifact. Flag
  ENCODING_SENS_CAND; Tier-S: `REMINT_CONTROLLED` / `ENCODING_SENSITIVE` /
  `NOT_ENCODING_DEPENDENT`.

### PASS-L55 — claims sensitive to search algorithm rather than structure

- **Pattern.** Claim produced by one search strategy without a materially distinct replica
  (#863 R3: two materially distinct strategy signatures under common objective/budget).
- **Screen.** P3 packages with search-derived claims (mechanical: search/optimization/
  enumeration executors behind claim artifacts) lacking a second-strategy artifact. Flag
  SEARCH_SENS_CAND; Tier-S: `REPLICATED_DISTINCT` / `SEARCH_ALGORITHM_SENSITIVE` /
  `NOT_SEARCH_DERIVED`.

### PASS-L56 — claims that are only rediscoveries of parent mathematics

- **Pattern.** A claim whose strongest registered parent strictly contains it and whose
  registered residual (delta) is absent or vacuous. (PARENT_LEDGERs exist; the comparison
  does not — this pass builds it.)
- **Screen.** P2 rows with non-empty strongest_parents: flag PARENT_REDISC_CAND where no
  residual/delta is stated in (`justification`, `forbidden_extrapolations`, package
  parent-subtraction sections) OR where the statement is textually contained in the parent
  statement. Tier-A on all flagged (claim-bearing; reads authoritative): `RESIDUAL_STATED`
  (delta genuine, quote it) / `DUPLICATE` (rediscovery-only, #939 sense) / `UNKNOWN`.

### PASS-L58 — applied downgrade of the confirmed OVERSTRONG (separate claim, one object)

- Target `research/gmi-capability-interactions-unified-v1/CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1.md`.
- Registered defect (#939 verdict table, verbatim): name says unified theorem for all 27
  capabilities; the universal phrasing "for any two capabilities" exceeds a pure 27x27 finite
  classification once the rules rest on unproven equalities (joint=sum / joint=max).
- Applied action: reword Section 2 universal phrasing to the registered 27x27
  finite-classification scope; attach the mandatory joint-burden caveat making the
  joint=sum / joint=max equalities definitional classifications at registered scope rather
  than proven resource accounting; align Sections 3/5/6 wording; MANIFEST.json gains the
  audit-trail note (finding → verdict → new wording → this PR). Controls re-run:
  `test_interactions.py` + `interactions_witness.py` (package's own) must pass unchanged.
  One claim only; no other object edited. Claim check re-run post-edit against the #939
  defect wording: every defect clause must be addressed by the new text.

## 4. Validation discipline (every detector)

No detector output is reported before its validation plant passes; each detector ships a
self-test asserting (i) known-positive recall (>= 19/20 or pass-declared), (ii) no-alarm on
planted clean rows (0 flags), (iii) determinism (byte-identical rerun), (iv) "could not
check" is a distinct status from "checked and fine". A detector failing validation is fixed
or dropped — never shipped with a caveat. Fixture-only validation is insufficient where real
data exists: each validation plant is built FROM census/rows, not invented strings (synthetic
variant pairs apply the real crosswalk to real statements).

## 5. Determinism + receipts

All detectors stdlib-only, iterate sorted keys, seeded sampling, rerun byte-identically.
`RECEIPTS_V1.json`: commands, base SHAs (census `2fffb144`, rescore #948 merge, branch base
`14276c20`), artifact sha256s, per-pass flag/adjudication counts re-read from written files
(script-asserted, printed, then re-read).

## 6. Claim ceiling + forbidden

Earned at most: `GMI_833_SECTION_B_IDENTIFICATION_PASSES_AT_FROZEN_POPULATIONS_SCOPE`.
Forbidden: any census-disposition overwrite; any object promotion; `GMI_THEORY_BASELINE_V1`
frozen (needs L59 + L34 + full corpus); touching aj-lane packages beyond read; ticking L48
(aj) or any box whose live evidence this package does not itself produce; claiming
SCREENED-NOT-ADJUDICATED objects clear; claiming any verdict proves a theorem true; editing
frozen RESULT/receipt JSONs (L58 edits the live theorem .md + MANIFEST note only).

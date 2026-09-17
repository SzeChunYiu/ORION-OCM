# REV-L47-CUSTODY-GAPS — prospective re-establishment freeze (W4 pattern)

Ticket: REV-L47-CUSTODY-GAPS (GMI #833). This document is committed BEFORE
any re-run of any substantive-class package executes. Its commit timestamp
precedes every re-run receipt in this package; the receipts record the
executing commit (an ancestor of this freeze's commit is impossible — the
runner executes AT a commit that contains this freeze) plus host wall-clock
timestamps of each run.

**Tree pin.** The re-runs execute exactly the corpus files at commit
`f0a2a237c9f30bbcc12d9824ca628116c44ddc80` (the tree this freeze commits
onto; every re-run receipt additionally records `git status --porcelain`
emptiness for the target package, proving the executed files equal the
committed = pinned files).

**Purpose.** 12 packages were triaged SUBSTANTIVE (TRIAGE_V1.json): the
outcome-bearing artifact, or the search implementation their freeze text
claims to predate, landed within 120 s of the freeze in the only surviving
history — prospective custody is not demonstrable from metadata. Per the
W4 pattern (REV-L47-NOVEL-INTELLIGENCE-W4 lever; #981 E9 structure), this
freeze pre-registers, per package: the claim under repair, the re-run, the
decision rule, and the non-claims. The re-run re-executes the package's own
frozen machinery under demonstrable custody; if the outcome matches the
committed artifacts, the claim is re-earned at original strength with the
prospective receipt as the new strongest evidence. The ORIGINAL landing's
commit-order gap remains a recorded, permanent custody defect (it is not
erased by this replica).

**Non-claims (all packages).** No new scientific claim beyond each
package's frozen claim ceiling is made here. A green replica re-establishes
PROSPECTIVE CUSTODY FOR THE CONTENT at the package's registered scope; it
does not retroactively cleanse the original commit ordering, does not
upgrade any claim ceiling, and does not tick any other ledger row (L46
two-route, L49 accounting, etc.). A failed replica opens a revival chain
attribution (failure stage named), never a silent narrowing.

**Custody order for this tranche.**
1. Commit A = this freeze (+ runners). Pushed; remote hosts clone at commit A.
2. Remote phase 1 = mechanical self-tests (content legs for the 6 MECHANICAL
   receipts) + the 11 single-stage re-runs below + section-d stage A
   (acquisition + training only; NO holdout execution).
3. Commit B = section-d replica stage-2 freeze (fitted coefficients + numeric
   n=17/31 predictions) — BEFORE any holdout execution.
4. Remote phase 2 = section-d stage B (holdout execution + all comparisons).
5. Commit C = receipts + verdicts + register updates.

## Decision rules, per package

### gmi-833-aj9b-k01-blind-recovery-v1 (and aj9c, aj9d, aj9e, aj9f, aj9h — same rule)

- Claim under repair: "a blind generic search recovers the frozen family's
  function" (RECOVERED terminal) with the freeze predating implementation;
  the recovery CONTENT is what this replica re-establishes.
- Re-run: `python3 check_aj9<X>.py` in the package dir (the checker re-executes
  the frozen searches, re-adjudicates against the pinned AJ9a benchmark blob,
  enforces its own no-smuggling token scans, re-verifies its original git
  custody legs against the full clone, and rewrites RESULT_V1.json from the
  live run).
- Decision rule: **CLEARED-GREEN** iff checker exit 0 AND post-run
  `git diff --quiet -- <package>` (rewritten RESULT byte-identical to the
  committed artifact). Any assertion failure ⇒ revival chain with the
  failure stage recorded.

### gmi-833-developmental-naturality-v1

- Re-run: `python3 developmental_naturality_v1.py` (cwd package).
- Decision rule: **CLEARED-GREEN** iff printed JSON equals committed
  RESULT_V1.json (parsed-object equality; byte equality also recorded) AND
  `python3 test_developmental_naturality_v1.py -v` exits 0.

### gmi-833-real-transition-protocol-v1

- Re-run: `python3 real_transition_protocol_v1.py` (cwd package).
- Decision rule: **CLEARED-GREEN** iff printed JSON equals committed
  RESULT_V1.json (qualifying_count stays 0, all hostiles rejected) AND the
  package test exits 0.

### gmi-history-morphology-discovery-v1

- Re-run: `python3 history_morphology_discovery_v1.py` (cwd package).
- Frozen decision targets (the freeze's arms/targets/controls/success rule,
  re-registered here before this re-run): first-verified ranks
  RESET [40,54], CONTINUED [5,6], SHUFFLED_HISTORY [16,20].
- Decision rule: **CLEARED-GREEN** iff printed JSON equals committed
  RESULT_V1.json AND `python3 test_history_morphology_discovery_v1.py -v`
  exits 0 (its 17-key committed-RESULT equality assertions).

### gmi-heldout-long-sequence-v1

- Re-run: `python3 heldout_long_sequence_v1.py` (cwd package).
- Decision rule: **CLEARED-GREEN** iff printed JSON equals committed
  RESULT_V1.json — in particular the held-out n={17,31,63} outcomes match
  the predictions FREEZE_V1.md registered before its executor existed —
  AND the package test exits 0.

### gmi-833-heldout-20-transitions-v1

- Re-run: `python3 heldout_transition_v1.py` (cwd package; runs both frozen
  searchers over all 65,552 semantics and the 20 frozen cases).
- Decision rule: **CLEARED-GREEN** iff printed JSON equals committed
  RESULT_V1.json (deterministic; ~10–40 s).

### gmi-section-d-uncertainty-extrapolation-v5 — two-stage replica

Stage-1 authority = this section. The registered mechanism, law forms,
interval math, fitting algorithm, holdout protocol and pass ledger
(U1–U7, X1–X10) are the v5 package's own frozen texts (FREEZE_V5.md,
FIT_AND_HOLDOUT_FREEZE_V5.md at the tree pin) — adopted verbatim by
reference, NOT modified. The replica differs ONLY in: a fresh
post-freeze random acquisition and fresh custody chain.

- Stage A (after this commit, before commit B): acquire exactly
  `N=16384` bytes via Python `secrets.token_bytes`, map
  `X_i=1 iff raw<224`, pack MSB-first, commit REPLICA_SAMPLE_V1.json
  (n, packing, threshold, packed_bits_hex, ones_count, packed_sha256).
  **One draw only. No reroll regardless of outcome** (frozen rule: a
  statistical miss is retained, epsilon is never widened).
  Then run training_measure_v5.build() (n<=5 hard block) → commit
  REPLICA_TRAIN_V1.json; fit the four affine laws from n={2,3}, validate
  zero residual at n={4,5}.
- Commit B (stage-2 freeze, BEFORE any n=17/31 execution): the four
  fitted (a,b) pairs + numeric predictions at n=17/31 for all four
  coordinates + predicted crossover horizon/winners, from the actual
  stage-A training output.
- Stage B (after commit B): execute holdouts via the v5 witness's own
  measure_holdout/crossover machinery (imported; no reimplementation),
  including disjoint remints and the hostile mutated-prediction
  comparator; evaluate U1–U7 on the FRESH sample and X-legs against
  commit-B predictions with zero tolerance.
- Decision rule: **CLEARED-GREEN** iff all U-legs except statistical
  U1/U2 hold mechanically AND (U1/U2 hold on the fresh draw — expected
  with coverage >0.999 under the registered model — or a prospective
  statistical miss is recorded honestly) AND every X-leg holds exactly.
  The X-legs are deterministic functions of frozen machinery: any X
  mismatch is a revival-chain failure (stage: mechanism-equality), never
  tolerated.

# HUMAN_GATE_PROXY_THEOREMS_V1 — named results of gmi-833-human-gate-proxy-v1

Claim ceiling: `GMI_833_HUMAN_GATE_ROWS_DISCHARGED_BY_LABELLED_MODEL_PROXY_AT_REGISTERED_ARTIFACT_SCOPE`.
Every result below is about *records and protocols*, not about the truth of the reviewed claims.
Nothing here is an external, human or independent-team outcome; the label
`HUMAN_GATE_BYPASSED__MODEL_PROXY` is the disclosure, not a promotion.

## HGP-1 — labelled-proxy discharge is decidable from committed bytes

**Scope.** The 40 rows frozen in `FREEZE_V1.md` §2, the 23 proxy records of `PROXY_RECORDS_V1.json`,
the decision rules of `FREEZE_V1.md` §4.

**Statement.** For every row `r` in the frozen set, `closed(r)` is a total function of (i) the verbatim
verdict lines under `proxies/`, (ii) the record integrity predicate (label present; brief sha256 equal to
the frozen value; every handed artifact's git blob sha equal to the frozen pin; verdict file sha256 equal
to the record; row verdicts in the record equal to the verbatim block; a model self-report present) and
(iii) the executor-decided protocol facts of HGP-2/3/4/5. Under these inputs at commit time:
**18 rows close, 22 do not.** A row never closes on a proxy that returned `NOT_SATISFIED` or
`UNDECIDABLE_FROM_ARTIFACTS`, and a two-route row (`AG8-R48`, `AC05`) closes only on two `SATISFIED`
records from two model families.

**Quantifiers.** All 40 rows; all 23 records; both routes (A regex-based, B state-machine-based)
compute the same closed set by set equality.

**Assumptions.** The harness's isolation-by-instruction (a fresh session told to read only the brief and
its artifacts) is the isolation actually obtained; the served-model strings in the harness transcripts
are correct. Neither assumption is checkable from git; both are recorded, not asserted.

**Falsifiers.** Any of hostiles H1–H7, H11, H12 passing undetected; the two routes disagreeing on the
closed set; a `NOT_SATISFIED` row appearing in `closed`.

**Strongest parents.** `research/independent-authorship-gate-v1` (P1E3: isolation by instruction,
verbatim capture); `research/m2-traversal-capital-v1/m2p3/authored/PROVENANCE.json` (served-model
recording); the #833 reconciliation schema `GMI_ISSUE_RECONCILIATION_V2`. Not claimed novel: the
record-integrity pattern (sha-pinned inputs + verbatim outputs) is the programme's standard receipt
discipline.

**Forbidden extrapolations.** `EXTERNALLY_REVIEWED`, `HUMAN_REVIEW_OBTAINED`, `THIRD_PARTY_ADJUDICATED`,
`PROXY_VERDICT_IS_TRUTH`: a `SATISFIED` proxy verdict says a model could perform the role from the
artifacts, never that the reviewed claim is true, and a `NOT_SATISFIED` verdict is the model's
objection list, never a proof of falsity.

## HGP-2 — the Z9 blind protocol ran and falsified theory clause T3 (EARNED-BY-COUNTEREXAMPLE)

**Scope.** Two batches, 24 held-out environments, 64 price points, the registered family of
`FREEZE_V1.md` §5, the theory T1–T4 stated in `BRIEF_Z9_PREDICTION_TEAM.md`.

**Statement.** With test teams (sonnet, opus), prediction teams (opus, sonnet) and adjudicators
(sonnet, opus) in six disjoint sessions, environments committed before predictions and predictions
(sha256 in the commit message) before any oracle ran, the exact oracles (route A full enumeration of
65,552 candidates; route B cell-wise per next-state table; agreeing on every cell) give:
class-set predictions **61/64**, capability predictions **35/64**, crossover predictions **14/24**
(batch 1: 28/30, 16/30, 7/12; batch 2: 33/34, 19/34, 7/12). Every miss is on `J_best_onebit`
(`J_best_stateless` matched 64/64): the exhaustive one-bit optimum is strictly better than the
carry-`x_{t-1}` machine on every environment whose target reads `x_{t-2}` (`PREV2`, `XOR2`, `AND2`,
`OR2`, `MAJ3`). Clause **T3 is false** on the family; T2 (stateless cell-wise optimum) and T1/T4
(argmin and crossover *given* the true class optima) are not contradicted. Witness:
`(L=3, PREV2/OR2, p=4/9)`: exhaustive `E_onebit = 5/36 < 7/36` (carry-previous value), `lambda* = 1/6`
not `1/9`. A seeded random class-set predictor matches every winner set **0/200** times.

**Quantifiers.** All 24 environments, all 64 price points, both oracles, both adjudicators (whose
totals equal the executor's exact re-score).

**Assumptions.** The registered family and objective; exact arithmetic; the prediction teams did not
enumerate machines (instructed; their transcripts show scratch arithmetic only).

**Falsifiers.** An oracle A/B disagreement (H10); a prediction file whose sha256 differs from its frozen
commit (H9); any adjudicator total differing from the executor's; a null predictor matching all sets.

**Strongest parents.** `gmi-833-heldout-20-transitions-v1` (the parent law `lambda* = eta·p/2` at
`L=3`, `CUR/PREV`, reproduced 20/20 by oracle A's self-test); the Z15 falsifier discipline.
Not claimed novel: the exhaustive-argmin methodology. **Residual contribution:** the first held-out
evidence that the programme's one-bit-optimum clause does not extend past a one-step window, obtained
under blind role separation. A negative is a lead: the revival target is a corrected one-bit clause
(optimise the next-state table, not only the output table — exactly what oracle B does) re-frozen and
re-tested on a third batch.

**Forbidden extrapolations.** `INDEPENDENT_TEAM_REPLICATION`, `REAL_SYSTEM_VALIDATED_BY_PROXY`,
`UNIVERSAL_MORPHOLOGY_LAW`.

## HGP-3 — the AA10 exhaustion gate is executable and fails on a planted violation

**Statement.** Over `GMI_GAP_GRAPH_V1.json` (1140 records, all `OPEN` at `source_main`) the gate
"a record may carry an exhausted status only with an `independent_hostile_review` object whose
`reviewer_kind ∈ {EXTERNALLY_REVIEWED, HUMAN_GATE_BYPASSED__MODEL_PROXY}`, `reviewer_id ≠ owner_role`,
and a 64-hex `verdict_sha256`" reports **0 exhausted, 0 violations**, and a planted `EXHAUSTED`
record without review yields **1 violation** (H8), as does a review whose `reviewer_id` equals the
owner. Two independent walks agree. **Scope:** the pinned graph only; the gate is a CI check from this
package on. **Falsifier:** H8 undetected. **Not claimed:** that any gap is exhausted.

## HGP-4 — four Lean 4 core targets for the spine type-check

**Statement.** PX-AA15 judged S1 (state-class law), S2 (CIP-1 partition), S3 (AG1-4 acyclicity),
S4 (AJ13 predicate) PRACTICAL and wrote `aa15_targets/S{1..4}_*.lean`; under Lean 4.14.0 core on
laptop-billy every file compiles with **0 errors** (sorry counts 8 / 6 / 2 / 0; committed logs).
S4 is fully proved; S3 proves the AG1-4 arrow-set counterexample (35 non-MI arrows: 0 cycles, 7 sinks;
37 arrows: a 2-cycle, 5 sinks), independently recomputed by the lane. **Scope:** statement stubs, not
proofs of S1–S3. **Falsifier:** a stub failing to compile under the pinned toolchain. **Forbidden:**
`FORMALLY_VERIFIED`.

## HGP-5 — reopen authority was granted and every demand is honoured

**Statement.** Every brief carries rule 5 ("You have authority to demand … be REOPENED"); the 23 records
contain **86 REOPEN demands from 17 proxies**, and `REOPENED_GATES_V1.json` (generated, `--check`ed in
CI) carries each verbatim with status `REOPENED_BY_PROXY_DEMAND`; deleting one is detected (H12).
**Scope:** registration of demands; this package closes none of the reopened gates. **Falsifier:** a
demand absent from the register.

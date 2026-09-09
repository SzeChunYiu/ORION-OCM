# D6' — fresh-context hostile review (D6_HOSTILE_REVIEW_V1)

**VERDICT: PASS_WITH_FINDINGS** — 0 HIGH / 2 MED / 3 LOW. All seven checks PASS.
No finding changes a verdict, the census, or the sha-chain.

- Review ID: `D6_HOSTILE_REVIEW_V1` (machine record: `D6_HOSTILE_REVIEW_V1.json`)
- Reviewed: branch `hsg/d6-hostile-review`, HEAD `5d3cfb285ebf8988ca4b999f7e301dd17755e471`
- Scope: issue #233 capsule `research/heritable-search-geometry-v1` at post-fold state
  (AMEND_1: lanes E/F/G merged via PRs 243/245/244).

## Why the verdict holds

- **Census and fold are exact.** Re-applying patches E/F/G to the pre-fold atom
  table (commit 44c5ce65) reproduces all 52 (atom,rung) rows with zero
  collisions, zero missing/extra rows, zero content mismatches, non-verdict
  payload untouched; recomputed census is exactly 22 LIFT_CONDITIONAL /
  12 PARENT_SUFFICIENT / 7 NOT_APPLICABLE / 6 LIFT_FAILS / 5 LIFT_SURVIVES.
- **Sha-chain intact.** All 7 AMEND_1 sha256s recomputed; historical pre-fold
  states recovered byte-exact from git blobs at all 8 pre-integration commits.
  Nothing UNCHECKABLE_HISTORICAL.
- **The counterexamples are real.** All 6 LIFT_FAILS rows carry minimal,
  machine-witnessed counterexamples; arithmetic hand-checked. The exact checker
  was RE-EXECUTED for this review: exit 0, `SUMMARY pass=11`, stdout
  byte-identical to `exact/run_v1.log`, 10/11 witnesses byte-identical; the
  11th differs by one 15th-digit float in the check the checker itself flags
  "float (transcendental object)".
- **Conditions are load-bearing.** All 22 LIFT_CONDITIONAL conditions name a
  checkable condition plus the failure mode when dropped (CHARGE, SEL-MEAS,
  CHAIN-BUDGET, ARCHIVE-GOV, KERNEL-UNIVERSALITY, DIODE-PRECOMMIT,
  FLUX-DRIFT/EPS-PRECOMMIT, state-shared transport, d-closure,
  family-restriction). None vacuous, none hedge.
- **Parents own what is claimed.** 12 PARENT_SUFFICIENT rows verified against
  owned statements; unverified-text markers used where due (PAC-Bayes chain,
  Blum 1967, Baez-Fong). Reviewer externally confirmed the Ay–Jost–Lê–
  Schwachhöfer extension cite: arXiv:1207.6736 = *Information geometry and
  sufficient statistics*, PTRF 162 (2015).
- **Honesty intact.** A_T10/A_T11 open with empty verdicts; no closure language
  anywhere (searched with control patterns); coverage honestly 16/18.

## Findings

**F1 (MED, C1) — H3 mirror-case prose diverges from its own witness.**
`hostiles/GEOMETRY_HOSTILES_V1.md:32` ("edge set {S→B}, d(S,A)=3 … misses
affected B" — B is affected but at d(S,B)=2 no ball r≥2 misses it) and
`ladder/R4_CONE_VS_BALL_G14_AT06.md:26` ("remove S→A … misses the affected
node A" — with S→A removed, A is not affected) each describe a construction
that does not work, and they disagree with each other. The machine witness
(checker C4 + `hostile_cone_ball.json` + atom row "under_invalidate A") is
correct: keep BOTH edges, stretch d(S,A) to 3, r=2 → ball={B}, A
affected-and-missed. Fix: rewrite both sentences to the witness construction.

**F2 (MED, C6) — per-rung coverage gaps exist but are surfaced nowhere.**
Per-atom coverage (17/17 concepts, 16/18 theorems) is literally true, but three
N/A reasons defer to lanes that currently hold zero rows ("R6 is lane G",
"R7 is not this lane" — patch G has 9 theorem rows and NO concept rows).
Unassigned cells: G05/R6+R7, G07/R7, G08/R6+R7, G11/R6, G13/R7, G14/R7,
G16/R7, G17/R6; un-rowed ladder_question halves A_T01/R2, A_T03/R2, A_T04/R3,
A_T05/R7, A_T06/R7, A_T07/R6, A_T08/R3-R4, A_T14/R3-R4, A_T16/R5; plus open
A_T10/A_T11. Mitigated: everything stays OPEN, no closure claimed. Fix: add a
per-(atom,rung) coverage matrix to the freeze amendment; reword deferrals to
"OPEN pending lane landing".

**F3 (LOW, C1) — stale first-run numbers in `R4_CONTRACTION_G09.md:49-50`.**
"δ(K)=½ ≤ δ(Q)=½ … δ(K)=1 > ½" contradicts the file's own line 9 (δ(Q)=3/4)
and the final witness (3/4, 3/4, 1.0). Stale values are conservative; the run
log carries the corrected ones. Fix: update the parentheticals to 3/4.

**F4 (LOW, C4) — A_T12/R5 misses the A5 marker either way.** Parent string
"standard modern statement, Levin-Peres-Wilson class" has neither "(verified)"
nor PARENT_STATEMENT_UNVERIFIED_TEXT; the ledger ⚠ attaches to Koopman 1931,
not LPW. Statement is standard and witness-backed (216 kernels). Fix: verify
LPW text or append the marker.

**F5 (LOW, C1) — registry-note vs landed-row label drift.**
`R5_AMORTIZATION_AT05_G16.md:50-52` says G16 R5 is "NOT_APPLICABLE as an
independent row" while patch F and the folded table land it as its own
PARENT_SUFFICIENT row. Substance identical; labels disagree. Fix: reconcile
the note with the landed row.

## Checks tally

| Check | Result |
|---|---|
| C1 verdict-artifact existence + match | PASS |
| C2 sha-chain (incl. historicals) | PASS |
| C3 condition genuineness | PASS |
| C4 parent discipline | PASS |
| C5 fold integrity + census | PASS |
| C6 NOT_APPLICABLE honesty | PASS |
| C7 open-rows honesty | PASS |

Method: /usr/bin/git + subprocess cat-file (rtk pipe/exit-code corruption
avoided); absences checked by grep-with-control + find-by-basename; every
finding pinned to file:line; clean checks asserted with a no-alarm case
(checker re-execution, blob-byte equality, full fold re-application).

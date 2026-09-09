# HSG Survival V1 — folded-ladder verdict census (D4', issue #233)

Machine companion: `HSG_SURVIVAL_V1.json` (same directory). Source: `HSG_ATOM_TABLE_V1.json`
(sha256 `739cd905631cb720595d618e3e61e7708fcbe665192d7c7cbe7438e4c30fee61`).
Every count below was recomputed from the atom table by script (52 verdict rows); no prior
count was trusted. Conditions and counterexamples are copied VERBATIM from lane verdict
fields (quote style marks verbatim text). No new mathematics, no verdict changes.

## Census

Overall (52 rows): LIFT_CONDITIONAL 22 · LIFT_SURVIVES 5 · LIFT_FAILS 6 · PARENT_SUFFICIENT 12 · NOT_APPLICABLE 7 · BLOCKED 0.

| lane | PR | rows | SURV | COND | FAIL | PARENT | N/A |
|---|---|---|---|---|---|---|---|
| E (concepts R1–R3) | #243 | 17 | 3 | 11 | 1 | 2 | 0 |
| F (R4/R5) | #245 | 26 | 1 | 4 | 5 | 9 | 7 |
| G (R6/R7) | #244 | 9 | 1 | 7 | 0 | 1 | 0 |

## Per-rung survival table

- **R1** (2 assessed: G12, G14) — 2 PARENT_SUFFICIENT. Survives unconditionally: none.
  Parents: #145 semigroup closure (G12); causal-DAG locality (G14, with xi-removal failing as sub-finding).
- **R2** (4: G04, G08, G13, G15) — SURVIVES: G08 (constitution as Cantor space). CONDITIONAL: G04
  ("inheritance as distribution over infinite H needs measurable selection of parents"), G15
  ("ratchet ordering = restatement of elitist retention"). FAILS: G13 — counterexample
  "hostiles/G13_M_overhead_FOSD.md" (net FOSD fails for M > gross gain).
- **R3** (11: G01–G03, G05–G07, G09–G11, G16, G17) — SURVIVES: G03 (kernel exists; parent
  Ionescu-Tulcea), G07 (verifier as randomized kernel, (alpha,beta) bounds). CONDITIONAL (9),
  conditions verbatim in JSON; representative: G01 "kernel state needs coordinate
  measurability; (iii) relocated not removed". FAILS: none.
- **R4** (14: G03, G09, G10, G11, G12, G14, G15, G17 + A_T01, A_T03, A_T06, A_T07) — SURVIVES: none.
  CONDITIONAL: G09 (state-shared transport only), G17 (m* shrinks iff family sup-KL shrinks),
  A_T03 (metric admitted to the observation). FAILS (4): G10, G14, G15, A_T01 — see negatives.
  PARENT: Chentsov (G03), Dobrushin coupling (G11), Pearl (A_T06), Zitzler-Thiele (A_T07). N/A (3, routing folds).
- **R5** (12: G09, G10, G12, G15, G16 + A_T02, A_T05, A_T12; N/A folds G03/G11/G14/G17) —
  SURVIVES: G15 (running-max ratchet holds verbatim along every orbit, pathwise, no
  kernel/metric assumptions). CONDITIONAL: A_T02 (reach iff outside d-closure; set→metric
  direction fails per hostile H5). FAILS: G12 (same equivalence dies: witness hostile H5).
  PARENT (5): Dobrushin nonstationary (G09), tower property (G10), renewal-reward (G16, A_T05),
  Perron-Frobenius (A_T12).
- **R6** (6 theorems: A_T04, A_T08, A_T09, A_T13, A_T14, A_T16) — SURVIVES: none at the R6 key
  (A_T15 SURVIVES is keyed rung "all"). CONDITIONAL (5): CHARGE (A_T04), SEL-MEAS (A_T08),
  CHAIN-BUDGET (A_T09), ARCHIVE-GOV (A_T13), KERNEL-UNIVERSALITY (A_T16) — full verbatim
  conditions in JSON, e.g. A_T04: "CHARGE: amendment descriptions self-delimiting and billed
  to the acting lineage's bit budget; changelog included in C_t. Without it self-extension
  mints share (unconditional lift fails)." PARENT: Wolpert-Macready (A_T14).
- **R7** (2: A_T17, A_T18) — SURVIVES: none. CONDITIONAL (2): DIODE-PRECOMMIT (A_T17 — closed
  topologies: decoupled-evaluator component, pre-committed provenance-stripping diode; open:
  two-way exchange at evaluator, post-hoc or performance-indexed interfaces), FLUX-DRIFT /
  EPS-PRECOMMIT (A_T18, both conditions carried in one row).

## Negative results ledger (every FAIL and CONDITIONAL is a result; full table in JSON)

**Prominent — lane F H3, G14/R4 LIFT_FAILS**: metric-ball cache locality is unsound in both
directions; load-bearing text verbatim: "cache-skip by metric proximity unsound in both
directions; only the cone licence (lane A iff) is sound" — witness
"hostiles/witnesses/hostile_cone_ball.json (H3: over_recompute B and under_invalidate A)".
This bounds #221 archive-geometry claims: the only surviving cache-locality licence is the
causal cone (A_T06/R4 PARENT_SUFFICIENT: "do(S=s) changes the law only on Desc(S) u {S};
outside invariant").

The other five FAILS: G10/R4 burden Lipschitz (witness H1: one edit, burden N*p vs p;
restored: "Lipschitz iff d >= c*d_B (burden pseudometric); admissibility discontinuity is
structural"); G12/R5 metric-vs-set reach (witness H5 aliasing); G13/R2 inheritance FOSD at
M>0; G15/R4 hypervolume under capacity (witness H4: capacity 1, HV 4 -> 3/2); A_T01/R4
approximate-set infimum (witness H2: d_H = eps, inf N*p -> p; fails for program costs per H1).
22 CONDITIONAL rows are bounded lifts, each with its named condition and constrained
downstream claim in the JSON ledger (28 negative-result rows total).

## Parent-absorption ledger (12 PARENT_SUFFICIENT)

Chentsov 1972 (G03/R4) owns Fisher-metric uniqueness — HSG registers the kernel family, adds
no second metric. Dobrushin 1956 (G09/R5) owns nonstationary coalescence — #145 owns the
closure object. Tower property (G10/R5); Dobrushin coupling (G11/R4, Ev sensitivity ≤ TV);
#145 closure (G12/R1, "R1 adds nothing"); renewal-reward (G16/R5 + A_T05/R5, T05 threshold =
breakeven with H_eff); Pearl-class DAG locality (A_T06/R4, the cone licence); Zitzler-Thiele
1999 (A_T07/R4, HV monotone at unlimited capacity — capacity caveat filed as G15/R4 FAIL);
Perron-Frobenius/Levin-Peres-Wilson-class (A_T12/R5, 216-kernel exact witness); Wolpert-Macready
NFL sharpenings (A_T14/R6); causal-DAG locality (G14/R1). Verbatim parent + owned-statement
text in JSON `parents_ledger`.

## Downstream hooks (statements only; citations in JSON)

- **#221**: cache locality bounded to causal cone (G14/R4 FAIL + A_T06/R4 PARENT); ratchet
  survives pathwise (G15/R5 SURVIVES) while HV under capacity fails (G15/R4); amortization =
  renewal-reward breakeven, regenerative condition named (G16/A_T05 R5); novelty ceiling
  ARCHIVE-GOV (A_T13/R6); horizon rewrite (A_T12/R5); undecidability rung-invariant (A_T15);
  NFL escape parent-owned (A_T14/R6); inflow ledger + eps-precommit (A_T18/R7); burden metrics
  need d ≥ c·d_B (G10/R4).
- **#151/#217**: surviving developmental lifts — G03/R3, G07/R3, G08/R2 SURVIVES; orbit
  prediction parent-owned (G09/R5). Bounded — G13/R2, A_T01/R4 FAIL; A_T04/R6 CHARGE;
  A_T03/R4 aliasing price; A_T08/R6 SEL-MEAS; G17/R4 + A_T09/R6 crossover bounds; G11 Ev pair.
- **#145**: contraction transfer state-shared only (G09/R4); closure algebra owned by #145
  (G12/R1, G09/R5); reach divergence (A_T02/R5 COND + G12/R5 FAIL); ergodic decomposition
  parent-owned (A_T12/R5); Blum transfer unproven for restricted families (A_T16/R6).

## Honesty: open rows and coverage asymmetries

Open ladder rows: **A_T10** (Ev estimator at R3/R4) and **A_T11** (module promotion at R5) —
no lane claimed any verdict for either; carried as open rows, not silently dropped.
Asymmetries: R1 assessed only 2 rows and R2 4; R4 is densest (14) and holds 4 of 6 FAILS;
no concept atom carries an R6/R7 verdict row (concept rows routed there were folded or
declared NOT_APPLICABLE-to-lane, so R6/R7 are theorem-only strata, and no G17/R6 row exists
despite the R5 fold naming lane G); A_T15's SURVIVES is keyed rung "all" (census bucket, not
R6); A_T18's R7 row carries two named conditions; the 7 NOT_APPLICABLE rows are routing folds
with recorded reasons, not content verdicts; 16/18 theorem atoms and 17/17 concept atoms have
verdicts.

## DISCREPANCIES

None. Recomputed census (22 CONDITIONAL / 5 SURVIVES / 6 FAILS / 12 PARENT_SUFFICIENT /
7 NOT_APPLICABLE; 52 rows) matches the freeze's own `HSG_FREEZE_V1_AMEND_1.verdict_census`
and `coverage` block exactly, including the atom-table sha256 binding
(`739cd905…4c30fee61` = `atom_table_sha256_after`).

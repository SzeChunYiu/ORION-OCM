# Hostile review V2 — the V2 exact layer, the microscope, and Stages D/E/F as executed

Status: **attack log written by the main researcher after the revival chain RV-377-001…016**, replacing the
external hostile-review pass that did not complete. Every item names the defect, the receipt that exposes it,
the fix, and what the fix cost the claim. Codex's `GMI_HOSTILE_REVIEW_V1.md` (H1–H5) attacks the synthesis;
this file attacks the executed evidence. Refs #377 §14, #373, #233.

## 1. Instrument defects found by the revival chain (all fixed, none retroactively)

| # | defect | exposed by | fix | cost to the claim |
|---|---|---|---|---|
| I1 | P4 stated as a fixed total-growth cut (1.5×) over a fixed ladder | RV-003 (linear-scan columns fail), RV-010 (indexed columns 1.64–1.71) | growth-ORDER instrument: ratio of consecutive per-doubling increments (RV-012/013) | P4 is now a per-phase order law, weaker in form but exact |
| I2 | exec coordinate conflates store BUILD with QUERY work | RV-012 (6/75 failures, all M5 exec in indexed-emulation columns) | runner records `exec_after_init`; R4 reports build/query separately | R vector needs a build coordinate; earlier κ_exec values for store rows include build |
| I3 | P5 witness onset predicted at n=16 by hand | RV-010 clause 004 (separation already at n=4) | none needed; the witness exists | the "not separated at n≤8" sub-clause was wrong; recorded as a mis-freeze |
| I4 | P2 crossover predicted for M0 at n=1 | RV-010 clause 002 | none; M0's charged desc is size-invariant (5 bits) so no crossover exists | P2 restricted to rows whose factorized desc grows with n |
| I5 | blind-recovery classifier keyed on store-primitive use | RV-006 (cells act as a store) | locality-keyed classifier (RUN3) | V1/RUN2 classes are not comparable to RUN3+ |
| I6 | raw write counts include dead scratch writes | RV-008 (7/9 hybrids) | dead-write elimination before classification (RECLASS_RUN3: 7/9 LOCAL_MEMORY, scores unchanged) | canonicalization is mandatory (Codex Stage C-v1 already required it) |
| I7 | search grammar's update expressions have depth ≤ 2 → learning rate 1 only → every multi-input gradient learner diverges | RV-015 planted check (0.0 vs 0.926 with one more level) | declared G_DEPTH = 3 (RV-016); mandatory planted existence check before any blind run | Stage F V1/RUN2/RUN4 "no dense winner" results are instrument artefacts, not evidence about the ecology |
| I8 | E_smooth2 development length too short for every registered row | RV-009 (no admissible row at 16 events) | 48 events + declared approximate-search row S2a (RV-014) | PH-REV-2 untested until RV-014 returns |
| I9 | Stage E frontier verdict counted an unobservable handover as support | caught before commit | NOT_OBSERVABLE verdict | none |
| I10 | MUL emulation rounding differed from native for negative products | caught by C2 at h=4 | signed shift-add with identical floor rule (0 disagreements on 256×256) | none |

Pattern: eight of ten defects are **frozen thresholds or instrument scopes chosen by hand before the cost
algebra was evaluated on the new range**. The revival protocol (#373) caught each one because every
prediction was numeric and frozen in a commit before its run. None of the fixes touched a result already
reported as positive.

## 2. Attacks on the positive claims

### A1 — "the rewrite basis pays ~110× on the gradient law" (P1a) is a property of the emulation macro, not of the basis
Correct as stated. The ripple-carry / shift-add macros are the frozen universal compilation; a table-driven
MUL in B2 would cost ~256 desc bits and ~10 exec per product and shrink the factor to ~5×. The claim is
therefore scoped to the frozen macro family and reads: *under any fixed gate-level compilation of fixed-point
arithmetic into a basis without native arithmetic, the gradient law's update cost carries the compilation
constant multiplicatively per parameter*. The direction (constant > 1, growing with precision) is
parent-owned (circuit complexity of multiplication); the number 110 is ours and macro-relative.

### A2 — the M5/M5L witness (P5) is a data-structure triviality
Yes at the level of data structures (list vs index). The content at the theory level is only that the
phenotype quotient Φ_E (Dev tables) is blind to it in every column while the R vector separates it outside
K_FLAT from n=4 upward — the finite instance of Codex GMI-RP7 (same semantic state, different frontier).
Nothing else is claimed. Terminal: `SUB_BAND_NON_EMPTY__PARENT_DATA_STRUCTURE_OWNED`.

### A3 — the per-phase growth-order law (RV-013, all hold) is tautological: the columns' store disciplines were declared
Partly. Each column's order follows from its cost algebra, so within one column the law is a consistency
check on the compiler. The non-tautological part is small and should be stated exactly: (i) the order is
identical across the six indexed columns and across the three scan columns although their native op sets
differ (B2 has no arithmetic; B0i has no store; U has everything), i.e. the charged compilation is
order-preserving under every basis of the frozen family (D1 as defined); (ii) the two form classes that the
signature layer distinguishes by the declared `store_discipline` coordinate are recoverable label-free from
the growth order of exec_query/upd alone, which repairs I5 at the theory level. Terminal:
`CHARGED_COMPILATION_PRESERVES_GROWTH_ORDER__DATA_STRUCTURE_PARENT_OWNED`.

### A4 — PH-REV-2 (pending RV-014) would be Codex GMI-RP3 (horizon crossover) on the r-axis
Agreed in advance. If RV-014 holds, the r* formula is RP3 with A_i = desc + H·exec_q and c_i = upd + ver +
rev/4; the parent is algorithm selection / resource-rational analysis. What is ours is only the executed
cross-basis calibration and the corrected direction (update WORK, not write locality), which is also the
Levin/OOPS accounting. No phase-law credit beyond `PARENT_INSTANTIATED_AT_SCOPE` is admissible.

### A5 — F1 positive (7/9 after canonicalization) is one seed, one budget, one grammar, one basis column, and the classifier thresholds were chosen after RUN3
The thresholds (≤ 2 live writes/event; store or ≤ 2 cells) were fixed in CLAIM_LADDER_V2 before RUN3;
the canonicalization step was frozen (RV-008) before the replay; the replay is byte-identical to RUN3
before elimination. What remains attackable: (a) one seed — the random-baseline fraction at θ is 0.0015,
so the 9 winners are search products, but a second seed is required before any rung is claimed; (b) the
E_bind16 target `((7x)>>2)&1` is a lookup problem by construction, so "memory forms win" is the
parent-predicted null (Gold/exact identification), not a discovery. Terminal for F1:
`BINDING_ECOLOGY_RECOVERS_MEMORY_FORMS__ONE_SEED__PARENT_NULL_CONSISTENT`.

### A6 — the RV-015 existence failure is our own instrument's artefact and its fix is elementary
Yes. The stability bound (step size < 2/k) is textbook. The point retained is methodological and enters
the D2/D3 design as a rule: *no blind-recovery claim, positive or negative, is admissible without a planted
existence certificate for every predicted class inside the exact search grammar.* Stage F V1/RUN2/RUN4
negatives on the smooth ecology are void, not negative.

## 3. Attacks on the framework

- **F-1 Derivation direction.** Every "morphology" in the matrix is a hand-written reference program
  (M0–M5, S2–S5). The matrix measures representation → cost under bases; it never generated a form from a
  basis. B2 is therefore earned only as "bounded compilation of parent-sufficient representations" (Codex
  GMI-V4-04 caveat), which is what CLAIM_LADDER_V2 says. Stage F is the only generative test and it is
  at E2 scope.
- **F-2 Parent cost models are assumptions.** κ compares our charged totals to documented per-row parent
  accounting (e.g. "Rete-indexed match 1+log n", "backprop 3× forward"). These are conventions, not
  measurements of parent code. κ values are therefore relative to those conventions; the cross-column
  comparisons (same program, different basis) do not depend on them and are the load-bearing numbers.
- **F-3 K_sim.** Defined as the worst charged ratio vs U over the executed cells; it grows with the scope
  (B2: 131 on R2 vs 131.5 on V1 — stable here, but not guaranteed). Prop 5.3's resolution rule uses it
  as a band, so any claim "outside K_FLAT but inside K_sim²" is scope-relative.
- **F-4 Observables are declared for two coordinates.** execution_shape and store_discipline are declared
  by the row and only cross-checked; theta_type, update_locality and feedback_dependence are measured.
  After RV-013 store_discipline is measurable from the growth order; execution_shape still is not.
- **F-5 Scale.** 4-input binding ecology, H = 8, 8-bit fixed point, one seed. Everything is a finite
  exact certificate (P2) and nothing is a statistical result.
- **F-6 The "ultimate question" is not touched by any positive result here.** No form was predicted before
  it was designed; the hole census (HOLE-A/B/C) is pre-registered and untested; Codex's
  `PHASE_HOLE_AUDIT_V2` verdict (no clean hole) stands.

## 4. What survives the attack, exactly

1. A charged, executed compilation of six reference morphologies and five learning laws into four candidate
   bases with a non-flat, coordinate-specialized overhead matrix (P1a, P1b, K_sim, class separation) —
   B2 at scope with the representation caveat.
2. Per-phase growth-order preservation across nine columns (RV-013), the M5/M5L sub-band witness (P5), and
   the per-event WORK reading of the revision axis (RV-009 diagnosis) — all parent-owned in substance,
   ours only as executed calibrations.
3. The instrument rules learned the hard way: canonicalize before classifying; certify existence inside
   the grammar before searching; state growth laws per phase and by order; freeze numeric predictions in a
   commit before every run.

## 5. Required before any B4/B5 sentence

- RV-014 positive on E_smooth2 at 48 events (PH-REV-2 instantiating RP3) in at least two numeric-native
  columns AND a second target.
- RUN6 (G_DEPTH 3) with existence certified: either dense winners at θ or the reachability terminal, then
  a second seed and a second search family (population-based) before F2 is called either way.
- A second seed for E_bind16 (F1).
- The W4 ledger depth pass (P2/P3/P5/P8 full text) so that the parent-null for each ecology is cited from
  primary sources rather than from the axis file.

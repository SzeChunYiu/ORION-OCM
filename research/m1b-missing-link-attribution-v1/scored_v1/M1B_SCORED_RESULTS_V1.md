# M1B scored run v1 — results (frozen protocol, ten arms)

Run: `run/` in this directory (43 files, sha256-verified against the run host).
Provenance: `RUN_MANIFEST_V1.json`. Machinery: PR #350 @ 82efa496 (selftest green on
the run host before launch). Freeze: `M1B_MISSING_LINK_ATTRIBUTION_FREEZE_V1.json` (#346).
No amendment was executed; no arm, metric, statistic or threshold moved.

## Verdict (frozen precedence, computed by m1b_stats.map_terminal)

**AMORTISATION_DOMINATED** — at least one attribution oracle recovers material
acquisition-side ground (LINK-attributable), and NO arm's recovery survives charging
its dev-enumeration cost (lifetime-charged recovery non-material for every arm).

Gate results: 10/10 arms, 0 censored rows, 0 leakage, 0 assay defects, seals verified,
frozen worlds byte-identical (partitions a5b0cbc1…), dev fingerprint gate passed
(70d8cad4…), CONTINUED refusal intact (refusal_rate 1.0, nothing served), all three
KOs collapsed, forced-fragment negative confirmed, no direction conflicts.

## Headline table (top rung 200k slots, 8 targets x 5 rungs = 40 rows/arm)

| arm | mean B_slots | verified | recovery vs KS oracle [95% CI] | material |
|---|---|---|---|---|
| RESET | 56 601 | 12/40 | — (anchor) | — |
| CONTINUED (refused) | 56 601 | 12/40 | +0.000 | no |
| RETR_ORACLE | 56 601 | 12/40 | +0.000 | no |
| APPL_KO / RETR_KO | 56 601 | 12/40 | +0.000 | no |
| INTG_KO | 63 039 | 17/40 | +0.853 [−0.35, +1.80] | no |
| KNOWN_STRUCTURE_ORACLE | 37 316 | 18/40 | +1.000 (denominator) | — |
| INTG_ORACLE | 16 638 | 25/40 | +2.263 [+1.83, +2.63] | yes |
| STRONG_ADAPTIVE_PARENT | 3 810 | 31/40 | +2.794 [+2.69, +2.89] | yes |
| APPL_ORACLE | 1 629 | 36/40 | +2.902 [+2.82, +2.98] | yes |

Lifetime-charged recovery: every arm ≈ −580 as recorded / ≈ −361 under the corrected
divisor (see M1B-DISC-3 below), none material → the terminal.

## Interpretation

**The missing link is APPLICABILITY; retrieval timing is worthless in isolation;
search integration is a real secondary lever.**

1. **APPL channel (which fragment helps where) dominates.** Serving only fragments
   on-path in a minimal derivation of THIS target — through the REGISTERED M.solve,
   registered timing, registered cost — turns 12/40 into 36/40 verified at ~35x lower
   burden (56 601 → 1 629 mean B). The native chain does not fail because of what a
   fragment costs or when it fires; it fails because the whole 16-fragment library is
   served blind to every target.
2. **RETR channel (when to fire) transplanted alone does exactly nothing.** RETR_ORACLE
   is byte-for-byte RESET performance (mean B identical, +0.000, 12/40, all 28 failures
   typed verification_reject). With the full library and registered cost, perfect timing
   never changes which candidates enter: the on-path fragment set is empty for the fired
   stream positions, so the oracle timing signal simply never fires on anything that
   helps. Timing cannot rescue an undiscriminated library.
3. **INTG channel (what an entry costs) is real but secondary** (+2.263 material,
   25/40): placing on-path entries at registered choice points with off-path pruned
   uncharged. Its KO shows the cost side is load-bearing: charging macros as primitive
   sequences (INTG_KO) destroys the CI (+0.853 [−0.35, +1.80], not material) yet still
   lifts successes to 17/40 — macro entry helps even at full price, but the advantage
   is not statistically secured once paid for honestly.
4. **The strongest parent nearly owns the link.** STRONG_ADAPTIVE_PARENT — a decision
   list fit on DEV data only, on frozen normal-form features, serving the SAME mined
   fragments through the registered path — recovers +2.794 [+2.69, +2.89], within the
   20% registered margin of APPL_ORACLE (+2.902), at 31/40 with zero oracle knowledge
   and its 30 069-byte store honestly charged. Under the frozen precedence this arm
   ALONE would have made the terminal PARENT_EQUIVALENT; AMORTISATION_DOMINATED ranks
   above it and is the honest headline. Practically: nearly the entire applicability
   advantage is learnable from dev data by a plain class→fragment policy.
5. **Why M1 read NO_NATIVE_EFFECT is now fully attributed.** CONTINUED refuses (no
   admitted generator at dev time) and equals RESET exactly. The mined library exists
   and is harmless; what was missing was any applicability gate. With a dev-learned
   gate the REGISTERED chain (timing + cost untouched) harvests 31/40. The oracle
   timing/cost channels were never the obstruction.

### Reading the recovery numbers — both contexts (per coordinator directive)

- **Against the frozen parent set** (this assay's own denominator): recovery_i is
  (B_RESET − B_arm)/(B_RESET − B_KNOWN_STRUCTURE_ORACLE) at matched keys, n=18 pairs
  with positive denominator. APPL_ORACLE +2.902 and STRONG_ADAPTIVE_PARENT +2.794 are
  both far above 1.0: these arms beat the KS oracle's own reduction, i.e. the frozen
  "ceiling" is undersized for the applicability channel.
- **Against the constant-offset context of PR #349** (M2 pre-freeze probes): #349's
  evidence says the KS oracle's M1 advantage is ~94% a history-free constant offset
  (enumeration-order mismatch), so recovery > 1.0 here reads as "the KS denominator
  does not measure transferable structure in this channel", NOT as "> perfect
  transfer". Both readings agree on what matters for this lane: APPLICABILITY is a
  genuine, mechanically transplanted link (the KO collapses to RESET and the KO alarm
  stays silent), and its size is only meaningful relative to RESET, not to the KS
  oracle. No arm, statistic or freeze was amended in response to #349; the attribution
  design answers it honestly by construction, and the numbers above are the answer.

### Amortisation: what exactly dominates

The dev phase spent 14 427 131 candidate-enumeration slots mining the fragment
library. Amortised over the 8 protected targets (1 803 391 slots/target), this charge
is ~13.7x RESET's per-target acquisition burden (131 978 slots/target) and ~256x
APPL_ORACLE's (7 048). Recovery that is +2.9 unamortised is ≈ −361 amortised. At THIS
assay scope the link is real, harvestable, and uneconomical: one dev epoch cannot pay
back on 8 targets. The charge is fixed and the benefit scales with serving volume —
the checker-computed break-even serving scales N* (targets needed for lifetime
recovery to cross the 20% margin, dev cost charged once): **APPL_ORACLE 316.5,
STRONG_ADAPTIVE_PARENT 330.7, INTG_ORACLE 447.7 targets** (~40–56x this run's 8).

**M1B-DISC-3 (disclosed instrumentation defect, found by this PR's own invariants
checker):** the shipped `phase_summarize` divided the dev charge by the rung count
(5) instead of the target count (8), recording 2 885 426 slots/target. Under the
corrected divisor every arm's lifetime recovery moves to ≈ −361 (CI upper ≈ −150)
— still nowhere near the 0.20 margin, so **AMORTISATION_DOMINATED stands unchanged**.
Machinery was not modified post-run; the defect is disclosed in
`RUN_MANIFEST_V1.json` and codified as the `amortisation_divisor_consistency`
invariant.

## Negatives → invariants (same PR)

`../m1b_invariants.py` codifies this run's negatives and disclosures as checkers for
every FUTURE M1B run (executed against this run: `INVARIANTS_REPORT_V1.json`, overall
KNOWN_DISCLOSED — the three disclosed states are matched to their disclosure ids and
everything else PASS; run WITHOUT `--expect-disclosed` it reports FAIL, because
disclosures must be asserted, never assumed; all five tamper classes — fake
RETR-differs, foreign divisor, new-arm horizon overcount, foreign failure vocabulary,
undisclosed-shape — were validated to FAIL on planted copies):

1. `retrieval_no_fire_no_effect` — a RETR transplant with zero on-path fires must
   equal RESET exactly (RETR_ORACLE's null here was exact; a future run where it
   differs with zero fires is an assay defect).
2. `observation_horizon_consistency` — observation-trace retrieval cost must not
   exceed the arm's acquisition slots (catches M1B-DISC-1's full-horizon overcount).
3. `typed_failure_cross_path_consistency` — M.solve-path and mirror-path arms must
   not diverge in typed-failure vocabulary for identical behaviour (M1B-DISC-2).
4. `recovery_over_unit_flag` — recovery > 1.0 vs the KS denominator must be flagged
   and annotated with the constant-offset context (#349), never silently reported.
5. `amortisation_divisor_consistency` — the lifetime dev charge must equal
   dev_enumeration_slots / distinct targets (catches M1B-DISC-3).
6. `amortisation_breakeven` — every material arm must carry its break-even serving
   scale N* (targets at which lifetime recovery crosses the 20% margin).

## Claim ceiling (frozen, restated verbatim)

Attribution of M1's NO_NATIVE_EFFECT to applicability / retrieval timing / search
integration at THIS assay scope ONLY: frozen worlds, frozen registered learner bound
as-is, ten arms, declared info advantages. Calibration-oracle arms are never headline
comparators. No economics claim, no OCM-residual claim, no open-endedness claim, and
no claim about any unfrozen family is supported by this machinery or any run it
produces.

## Next decisive experiment

**Amortisation scaling (the break-even lane):** the dev enumeration cost is fixed at
14.4M slots; STRONG_ADAPTIVE_PARENT's per-target advantage over RESET at the top rung
is ~52 791 acquisition slots/target (56 601 → 3 810 mean B, 31/40 vs 12/40 verified).
The decisive question is empirical: at what protected-target count does the
dev-learned gate's lifetime-charged recovery cross the 20% margin (checker-computed
N* = 330.7 targets for STRONG_ADAPTIVE_PARENT, 316.5 for APPL_ORACLE) — and does the
gate's precision hold or decay as targets move away from dev normal-form classes?
That experiment (fixed dev cost, growing serving volume, same frozen worlds and
learner, no new arms) converts AMORTISATION_DOMINATED from a scope statement into an
economics curve, and is the correct successor to this lane.

---

Artifacts: `run/summary.json` (deterministic summary), `run/arms/*.json` (10 arm
reports with per-row search behaviour), `run/seals/`, `run/events_*.jsonl`,
`run/ledger.json`, `run/dev_state.json`, `run/strong_parent_store.json`,
`drive_m1b_v1.sh` + `drive_m1b_v1.log` (run-host driver). Disclosures:
`RUN_MANIFEST_V1.json` §instrumentation_disclosures.

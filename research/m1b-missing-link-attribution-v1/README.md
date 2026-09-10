# M1B: missing-link attribution (machinery lane)

Frozen protocol: `research/top-tier-atomic-closure-v1/M1B_MISSING_LINK_ATTRIBUTION_FREEZE_V1.json`
(PR #346).  Umbrella: issue #323.  Question: M1 returned `NO_NATIVE_EFFECT` while
oracle headroom exists (KNOWN_STRUCTURE_ORACLE mean B 18762 vs primitive 26396) —
which link in the native chain is missing?

## The three channels

| channel | question | oracle arm | KO arm |
|---|---|---|---|
| APPLICABILITY | which fragment helps where | `APPL_ORACLE` | `APPL_KO` |
| RETRIEVAL TIMING | when to fire | `RETR_ORACLE` | `RETR_KO` |
| SEARCH INTEGRATION | what an entry costs | `INTG_ORACLE` | `INTG_KO` |

Native/parent arms: `RESET`, `CONTINUED` (registered learner as-is; refusal is
data), `STRONG_ADAPTIVE_PARENT` (decision-list applicability on frozen
normal-form partition features, own persistence outside OCM bookkeeping, serving
the SAME fragments dev mined).  `KNOWN_STRUCTURE_ORACLE` reruns the M1 arm as the
recovery-share ceiling.  Ten arms total.

## Arm semantics and declared info advantages

Oracle arms transplant exactly ONE channel; everything else stays registered
(`M.solve` for applicability arms; the research-lane mirror `adapter_solve` where
timing or cost is transplanted — parity with `M.solve` asserted by the selftest).

- `APPL_ORACLE` — serves only fragments occurring in a minimal derivation of the
  target (proper contiguous subsequences of `p*`).  Advantage: per-task
  minimal-derivation fragment set.  Timing + cost registered.
- `RETR_ORACLE` — fires exactly at choice points where the next guided candidate
  leads with an on-path fragment, never elsewhere.  Advantage: per-choice-point
  on-path knowledge.  Cost registered (1 slot per fired candidate, no prune relief).
- `INTG_ORACLE` — on-path entries placed at the solver's choice points charged
  exactly one slot; off-path guided expansions pruned UNCHARGED.  Advantage:
  zero integration overhead + per-candidate on-path knowledge.
- `APPL_KO` — the perfect set is computed per task, then fragments are physically
  removed; serves nothing.  Must collapse to primitive performance.
- `RETR_KO` — the perfect timing signal fires and is consumed per choice point
  (recorded as `retrieval_signal_events`), but serving is disabled.  Must collapse.
- `INTG_KO` — identical placement to INTG_ORACLE, but every macro is charged as
  its primitive step sequence (`len(program)` slots).  Must collapse.

## Statistics (`m1b_stats.py`)

- Primary endpoint: `recovery_i = (B_RESET − B_arm)/(B_RESET − B_KNOWN_STRUCTURE_ORACLE)`
  at matched keys (`target@budget`), bootstrap 95% CI (frozen seed 20260910),
  material iff mean ≥ 0.20 (registered margin) AND CI excludes 0.
- NULL_BAND_GATED direction tests: per-rung sign-flip bands; determinate strata
  must agree — two determinate disagreements = assay defect; all-indeterminate =
  `NULL_EFFECT_INDETERMINATE` (a legitimate null straddle, never a defect).
- Lifetime-charged recovery: dev enumeration slots amortised into the arm burden
  (drives `AMORTISATION_DOMINATED`).
- Holm family across the three attribution hypotheses.

## Terminal precedence

`ASSAY_DEFECT` > `LEAKAGE_ALARM` > `INSUFFICIENT_HISTORY` > `CANNOT_CHECK_*`
(missing arms / censored rows) > `LINK_ATTRIBUTED_{APPL|RETR|INTG|MULTIPLE|NONE}` >
`AMORTISATION_DOMINATED` > `PARENT_EQUIVALENT`.

## Negatives → invariants (checker additions shipped with the results PR)

1. FORCED_FRAGMENT_NEGATIVE — a planted fragment leak into APPL_KO serving must
   alarm; a clean KO must not (`forced_fragment_check`).
2. REFUSAL_CORRECTNESS — the learner's dev refusal is data: refused-but-served
   alarms; refused-and-not-served is intact (`refusal_correctness_check`).
3. NULL_INDETERMINACY — the null straddle is `NULL_EFFECT_INDETERMINATE`, never a
   defect; determinate conflicts are (`direction_tests`).
4. KO non-collapse — a materially recovering KO arm alarms (`ko_collapse_check`).
5. Adapter/native parity — the mirror loop with native channels reproduces
   `M.solve` through `GeneratorMethod` exactly.

## HDI-14 cost ledger (every arm; missing family = ASSAY_DEFECT, never silent 0)

`acquisition_slots`, `dev_enumeration_slots`, `obligation_slots`,
`retrieval_events`, `retrieval_cost_slots`, `max_penalty_tax_slots`,
`rejected_candidates`, `verification_calls`, `external_checker_spawns`,
`storage_bytes` (charge-what-you-carry: bytes the arm loads to build its serving
capability), `adapter_storage_bytes` (the declared info advantage is stored, hence
charged), `adaptation_events`, `interpreter_restarts`, `wall_seconds`.

## Selftest

```
python3 m1b_selftest.py --quick   # sub-second machinery gate (hostiles + 1 arm)
python3 m1b_selftest.py --full    # ten-arm toy lifecycle, real OS restarts (laptop gate)
```

Exit codes: 0 clean; 10 no-op breach; 11 fake restart; 12 tamper; 13 leakage;
14 false alarm; 15 internal; 20 forced-fragment; 21 refusal; 22 null-indeterminacy;
23 KO collapse; 24 adapter parity; 25 lifecycle defect.  Toy runs are stamped
`toy_selftest_only_NOT_SCORED_EVIDENCE` in every artifact.

## Scored run (Phase 2, gated)

Host: laptop billy only (never the Mac mini).  Entry gates: PR #345 + PR #346 +
this machinery PR all merged AND `--full` selftest green on the run host.  Fresh
clone at the merged commit; frozen worlds verified byte-identical
(`a5b0cbc1814042a7…` partitions, `62f199960eecfb08…` protected set) at every phase
entry; dev bound to the frozen M1 mined-fragment fingerprint
(`70d8cad4ce2189e…`); ladder 1000,4000,16000,64000,200000; 8 targets + obligations.
Artifacts land in `scored_v1/` with sha256-verified transfer.

## Scored run v1 — EXECUTED (2026-09-10, laptop billy @ 82efa496)

Terminal **AMORTISATION_DOMINATED** (frozen precedence).  Missing link:
APPLICABILITY (APPL_ORACLE +2.902 material, 36/40 vs RESET 12/40); SEARCH
INTEGRATION secondary (+2.263); RETRIEVAL TIMING null in isolation (+0.000,
exactly RESET).  STRONG_ADAPTIVE_PARENT recovers +2.794 of the +2.902 with zero
oracle knowledge (within the 20% margin = PARENT_EQUIVALENT shape, outranked by
the amortisation terminal).  No arm's recovery survives the 14.4M-slot dev
charge (corrected-divisor lifetime means ≈ −361).  Three instrumentation
disclosures M1B-DISC-1/2/3 (none affects the terminal) + negatives→invariants
checkers: `m1b_invariants.py` (6 invariants, tamper-validated).  Full results:
`scored_v1/M1B_SCORED_RESULTS_V1.md`; provenance `scored_v1/RUN_MANIFEST_V1.json`;
checker report `scored_v1/INVARIANTS_REPORT_V1.json`.

## Claim ceiling

Attribution at this scope ONLY.  Calibration-oracle arms are never headline
comparators.  No economics, no OCM-residual, no open-endedness, no claim about
any unfrozen family.

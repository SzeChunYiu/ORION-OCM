# FNA-6 protocol — working-state / residual-stream analogue — frozen before execution

**Issue #214 §4 FNA-6. Base `86ddd9bcedfb48de804fbb68d599f00ebd8316ba` (origin/main).**
**Evidence class E1 / L1.** One world from the production generator, one author.
No claim that a blackboard is novel (#214 says so explicitly); no architecture cosplay —
each parent arm implements the *function* (a working state serving the same obligation
stream) and is measured on identical tasks.

## The incumbent

The active-KSO working state on main is, operationally: the immutable `KnowledgeSpace`
(persistent structure; admissions produce a new space via `with_edges`), the snapshot-bound
`ExtractionIndex` (`kso/extraction_index.py`: structural adjacency, object-bound validity,
charged cold build), per-query `ExtractionRun` liveness caches (`kso/extraction_indexed.py`),
ATMS nogood records (`kso/nogoods.py`), and the impact-cone / reopening report
(`kso/revocation.py`: REOPEN / RECHECK / UNAFFECTED). This is the arm the parents are
compared against — not rebuilt, measured as production code (with counter instrumentation
that mirrors it; equality to production `gated_closure` is asserted before any scored run).

## Working-state contract (frozen)

The working state W of an architecture serving an obligation stream must guarantee:

- **W1 query-relative activation** — `serve(obligation, target)` answers exactly what the
  oracle (production `gated_closure` at stream state) answers. Zero tolerance.
- **W2 exact revocation propagation** — after an evidence revocation, no later serve uses a
  stale liveness verdict. Every wrong verdict is counted.
- **W3 concurrent-obligation isolation** — two obligations sharing objects interleave; a
  wrong answer whose derivation consulted an object resident in the *other* obligation's
  working set is an **interference event** (caught by the exact checker, never by a
  self-report).
- **W4 merge semantics** — after admissions and after the mid-stream catalogue mutation,
  serves stay exact. A wrong answer after a structural change is a **merge failure**.
- **W5 bounded working set** — peak concurrent resident objects are measured.
- **W6 whole-lifecycle charged cost** — build + serve + merge + sweep/reopen + close; every
  elementary object operation counted; no free preprocessing; the judge is never charged.

## Arms

| code | what it is | lineage |
|---|---|---|
| `P0_INCUMBENT_ACTIVE_KSO` | production active-KSO state, instrumented mirror | ATMS/TMS + self-adjusting index (de Kleer 1986; Doyle 1979; Acar 2005) |
| `P1A_BLACKBOARD_APPEND` | Hearsay-II-style panels + KSAR agenda scheduler, append-only hypotheses | Hayes-Roth 1985 (doi:10.1016/0004-3702(85)90063-9); Erman et al. 1980 |
| `P1B_BLACKBOARD_VERSIONED` | same + BB1-style control state, version-tagged hypotheses, validate-on-read recompute | Hayes-Roth 1985 / BB1 (Hayes-Roth 1993) |
| `P2_SOAR_WM` | WME working memory with goal-id scoping, elaboration productions, preference resolution, i-support retraction cascade | Soar manual §4 (Laird 2019) |
| `P2_MUTANT_NO_GOAL_BINDING` | interference probe: P2 without goal scoping | labelled MUTANT, never reported as a result |
| `P3_ACTR_STRICT_BUFFERS` | goal/retrieval/imaginal buffers, strict capacity 1, declarative memory | ACT-R 7 manual (Anderson et al. 2019?) — see SOURCE_LEDGER |
| `P3R_ACTR_REVALIDATE` | pre-registered revival lever for P3: retrieval-time validity check, charged | VanLehn 1988-style retraction-on-mismatch |
| `P4_FULL_RESCAN` | no working state; every serve rescans the field | null-cost baseline |
| `LOC_RANDOM_NULL` | random same-cardinality touched sets | locality null |

`P1B` and `P3R` are the pre-registered revival levers for `P1A` and `P3` respectively;
they are charged for everything they do.

## World and stream

Production `ocm.kso.checks.random_space`, `n_atoms=480, n_edges=1280, n_evidence=24`,
salt-seeded (own salts, same generator and scale as the established #216 MSC world — not a
benchmark authored for this study). Stream: obligations O_A/O_B (salt-chosen seeds), 24
serves each (target polarity balanced SUPPORTED / NOT at the state where the serve runs),
alternating O_A, O_B, …; one update event after every 4 serves (6 admissions of 3–7 edges,
6 evidence revocations chosen to flip at least one liveness); one **catalogue drift** at the
midpoint (after serve 23): one salt-chosen edge retracted AND one salt-chosen atom's warrant
replaced by certified-zero. Every arm replays the identical frozen sequence; the oracle is
production `gated_closure` at stream state and is never charged.

## Metrics

Per arm: `decisions_exact`/48; `interference_events`; `stale_revocation_decisions`;
`merge_failures`; per-phase op counts (`build_ops`, `serve_ops`, `merge_ops`, `sweep_ops`,
`drift_ops`); `working_set_peak`; `persistent_bytes` at close; locality = mean fraction of
update-touched objects inside the production `impact_cone` of the change (null =
`LOC_RANDOM_NULL`, 20 draws; locality supported iff mean ≥ 0.90 and ≥ 2× null mean).

## Sufficiency and terminals (frozen decision rule)

An arm is **SUFFICIENT** iff `decisions_exact == 48` AND `interference_events == 0` AND
`stale_revocation_decisions == 0` AND `merge_failures == 0` — exactness has zero tolerance.
Let `cost(arm)` = total charged ops.

- ≥1 parent arm (P1A/P1B/P2/P3/P3R/P4) SUFFICIENT and `cost ≤ 2.0 × cost(P0)` → overall
  terminal `PARENT_SUFFICIENT_FOR_working_state` (parents named).
- else P0 SUFFICIENT (expected) → `NON_NEURAL_FUNCTIONAL_RECONSTRUCTION_SUPPORTED_working_state`,
  with the explicit note that the reconstruction pre-exists on main and this study measures
  parity, it does not build it.
- else `NO_FUNCTIONAL_PARITY_working_state`.
- per-arm cost terminals: an arm SUFFICIENT but `cost > 10 × cost(P0)` → that arm is
  additionally marked `STATE_SEARCH_COST_DOMINATES`.

Outcomes, population, stream, salts and thresholds are never tuned. Negative OCM-mechanism
results are engineered iteratively (attribute one stage → apply the pre-registered lever →
re-run the SAME frozen stream → record under `engineering_chain`) until positive or a
structural obstruction is proven. `PARENT_SUFFICIENT` is a success terminal.

## Mandatory harness validation (before any scored number)

1. Static-world no-alarm: on an update-free stream every arm reproduces the oracle 48/48 and
   the exact checker reports zero events (proves the checker does not cry wolf).
2. Instrumented incumbent closure == production `gated_closure` on the scored population
   (asserted at run start; disagreement ⇒ `CANNOT_CHECK_HARNESS_DISAGREES`).
3. The planted `P2_MUTANT_NO_GOAL_BINDING` must be *detected* by the checker on the scored
   stream (proves the interference detector has teeth); it is never reported as a result.
   If the mutant is not detected, the run records `MUTANT_NOT_EXPRESSED_ON_STREAM` for that
   probe and the detector's teeth are instead proven by the test-suite fixture (a stream
   constructed so crosstalk is forced); no scored claim rests on an unexpressed mutant.

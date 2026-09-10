# M1 native-acquisition machinery (build lane)

Status: **scored run V1 EXECUTED on laptop billy 2026-09-10 — terminal NO_NATIVE_EFFECT
(clean assay; see `scored_v1/M1_SCORED_RESULTS_V1.json`).** Governing design:
`research/top-tier-atomic-closure-v1/M1_NATIVE_ACQUISITION_PROTOCOL_FREEZE_V1.json`
(read from the in-flight `m1-native-acquisition-freeze` branch at build time; not
committed into this PR). The registered learner `src/ocm/learning/methods.py` is
bound AS-IS — imported and driven, never copied or modified. No new cognitive core,
no learned router (#71 respected).

## Files

| file | role |
|---|---|
| `m1_partitions.py` | entry gate (d): frozen semantic partition emitter |
| `m1_runner.py` | 8-step lifecycle runner, six checkpoint-clone arms, CHECKER_C, sealed logs, deterministic summarize + terminal mapping |
| `m1_selftest.py` | entry gate (c): hostile selftest (sub-second toy mode; `--full` adds all six arms + carrier-removal mechanism check) |

## Entry-gate status at PR time

| gate | status |
|---|---|
| (a) DEV_CAL_V2_PROTOCOL_FREEZE_V1 merged | CLOSED — merged (PR #337), on origin/main at run HEAD 86dd3701 |
| (b) calibration fixture (`calibration_reference.py`, 12 tests + controls) | CLOSED — merged (PR #340); parent-parity correction in flight as PR #342 at run time (noted, not depended on) |
| (c) this machinery passes its hostile selftest | CLOSED — re-run on the run host pre-run: quick exit 0 in 1.11 s; `--full` exit 0 in 2.72 s, all hostiles fired |
| (d) frozen semantic partitions emitted with member digests | CLOSED — full emission (grammar length 8, frozen seed) on laptop billy: 18 partitions, 144 x 4 streams, 0 shared normal forms, `M1_PARTITIONS_V1.json` sha256 a5b0cbc1814042a7b4ddcfbc8658e63c4b352fade22cfdcd91c1968bea13921e |

A scored run on laptop billy requires ALL of (a)-(d). All four closed before the run.

## Scored run V1 (2026-09-10, laptop billy)

`scored_v1/` holds the complete run package (scp'd from the run host, sha256-verified
both sides; `HOST_RECEIPT.json` carries the phase timestamps, python 3.11.14, git
HEAD, artifact manifest and the raw log; `M1_SCORED_RESULTS_V1.json` is the distilled
verdict). Parameters: dev slots 200000; ladder 1000/4000/16000/64000/200000; 8
protected acquisition targets + 136 obligations per arm.

- **Terminal: NO_NATIVE_EFFECT** under the frozen precedence — clean assay (no
  leakage, no assay defect, zero censoring, all seals verified, real OS-process
  restarts with pid evidence on every arm, external CHECKER_C verdicts on every
  verified row).
- The registered learner REFUSED generator deployment at dev time
  (`validate_generator` no-slowdown rule; consistent with #189/#191). NOT relaxed
  in-run: CONTINUED therefore served no generator (refusal_rate 1.0) and equals
  RESET on all 40 common target@budget rows (mean B 26396 both).
- ORDINARY_ADAPTIVE_PARENT serving the same 16 fragments WITHOUT the admission
  gate is a net negative (mean B 30207, 11/40): the no-slowdown refusal was correct
  in the registered sense. KNOWN_STRUCTURE_ORACLE (calibration only): 18/40 at
  mean B 18762 — headroom above baseline exists but was not captured natively.
- Obligations: 136/136 externally verified per arm at the top rung.
- Claim discipline: mechanism scope only; NO economics, NO OCM-residual, NO
  open-endedness. The successor distinguishing immutable correctness from
  average-efficiency non-inferiority is a NEW registration, not an in-run change.

## Arms (exactly what each receives)

Every arm runs in a FRESH process against its OWN CLONE of the checkpointed runtime
ledger (`ocm_clones/<ARM>/`), so one arm's revocation cannot contaminate another.

- **RESET** — empty runtime root; no learned history; baseline primitive search.
- **LIBRARY_ONLY** — the checkpoint clone replays the admitted solved objects
  (proof atoms, via `M.admit_solution` at dev time); learning/search-control state
  frozen: the generator atom exists on disk but is never served. Carrier note: in
  this learner the library (proof atoms) and search control (generator procedure
  atom) are separable KSO objects.
- **CONTINUED** — full persistent native learner: `M.load_generator`
  (support-sensitive reload) serves the admitted fragments through `M.solve`.
- **CONTINUED_WITH_LEARNING_STATE_REMOVED** — solved content preserved; the
  generator's holdout validation evidence is revoked through the registered
  `runtime.revoke`; the report records SURGICAL (generator warrant dead, proofs
  live) or JOINT — never claims surgical independence it did not verify. When the
  learner itself refused deployment, the report says NO_ADMITTED_GENERATOR instead.
- **ORDINARY_ADAPTIVE_PARENT** (outside OCM bookkeeping) — receives EXACTLY: the
  identical developmental solved traces, the identical mined fragments
  (`M.learn_generator` output) persisted as plain JSON with a fingerprint check,
  and the identical search mechanics `M.solve` — but WITHOUT the OCM bookkeeping:
  no `validate_generator` no-slowdown admission gate (it serves fragments even
  where the learner refuses), no evidence supports, no revocation, no
  support-sensitive reload, no KSO atoms.
- **KNOWN_STRUCTURE_ORACLE** — CALIBRATION ONLY, never a headline comparator.
  Declared information advantage: the target's structural class (true minimum
  primitive length); enumeration is pruned to that length with honest slot
  accounting for every enumerated word.

Refusals are per-arm rows (learner's registered `REFUSED_TO_DEPLOY_LEARNED_METHOD`
from the no-slowdown rule; NO_ADMITTED_GENERATOR), never presented as cheaper
learning: refused rows are excluded from successes and reported as refusal-rate.

## Restart evidence format

`checkpoint.json` records `pre_restart_pid`, interpreter path, python version,
`boot_token`, `kso_state_hash`, and the dev-phase seal digest. `acquire` refuses to
run when `pre_restart_pid == os.getpid()` (ASSAY_DEFECT: SAME_PROCESS_FAKE_RESTART).
`restart-and-acquire` spawns a fresh interpreter and stores a receipt
`{parent_pid, child_pid, child_returncode}`; the arm report embeds
`{pid, pre_restart_pid, pid_changed}` — pid change is asserted, and CHECKER_C rows
carry the checker's own pid and `methods.py` sha256 digest.

## How the scored run composes phases (laptop billy)

```bash
python3 m1_partitions.py --out <run>/partitions.json            # gate (d) emission
python3 m1_runner.py --run-dir <run> --phase dev --slots 200000
python3 m1_runner.py --run-dir <run> --phase checkpoint          # process exits after this
for arm in RESET LIBRARY_ONLY CONTINUED CONTINUED_WITH_LEARNING_STATE_REMOVED ORDINARY_ADAPTIVE_PARENT KNOWN_STRUCTURE_ORACLE; do
  python3 m1_runner.py --run-dir <run> --phase restart-and-acquire --arm $arm --slots-ladder ...
done
python3 m1_runner.py --run-dir <run> --phase summarize           # verifies seals, maps terminal
```

Endpoints emitted per arm: paired B(M,T,q) rows (slots + candidates_checked per
target per budget level, success-vs-budget curve data when a ladder is given),
obligation rows, refusal-rate, censoring; cost ledger = wall seconds per phase,
interpreter restarts, candidate enumerations, verification calls (count-only; the
physical vector lands with the scored run). Terminal precedence: ASSAY_DEFECT >
LEAKAGE_ALARM > INSUFFICIENT_HISTORY > NATIVE_ACQUISITION_DEMONSTRATED /
NO_NATIVE_EFFECT / PARENT_EQUIVALENT / CANNOT_CHECK_<reason>. Claim ceiling:
mechanism claim at this scope only.

## Hostile selftest

Quick mode (sub-second gate): (i) no-op solver fails the positive control,
(ii) same-process fake restart rejected, (iii) sealed-log tamper fails closed,
(iv) answer-in-history plant trips LEAKAGE_ALARM, (v) clean toy run zero alarms +
real restart evidenced. `--full` adds the carrier-removal mechanism check. Distinct
exit codes: 0 clean; 10 no-op breach; 11 fake restart undetected; 12 tamper
undetected; 13 leakage undetected; 14 false alarm; 15 internal.

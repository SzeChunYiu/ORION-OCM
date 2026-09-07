# Native proof/runtime claim review — 2026-09-07

**Decision: no remaining claim or semantic-acceptance blocker for this exposed F0 integration result.**
This is a read-only review of existing bytes, with no new search, Lean execution,
OCM replay invocation, source edit or native qualification run.

## Bound evidence

Linux run root: `/home/billy/orion-director-work/20260907/proof-runtime-commissioning-20260907/`.
All relative raw paths below resolve under that root.

- `result.json`: `c1d93fa010515a97f8746bd53252253c8b7d46a95c1c8e78222a023d0ae2f5da`.
- `freeze.json`: `f71f9053b8dd2270c9a41bcb4e4415f26cc5ee03d1c49b04ae035f5e0f2d5b8f`.
- Runtime manifest: `93aa17a738a8511bbb8996eff91e81da0ec5868db50d0f81ab26809e38661894`.
- Result is `PROOF_RUNTIME_LIFECYCLE_COMMISSIONING_PASS`, with all 24 declared phases present and passing.
- Independently rehashed all 192 recorded source files and all copied source/input bindings: unchanged.
- Reviewed lifecycle source remains `50288e74802c1cb889c6be4b238a7fcd6497eaa24d5f7d8fc21fecec18c3af3f`;
  replay remains `83e94a0dd46b60d57dd808fc02c9d0280b916113fc999cef0b4f220565e214a5`.

The separate custody reviewer owns the exhaustive native runtime/artifact inventory audit.
This note independently reads critical worker, kernel, phase and ledger records;
it does not substitute a second full runtime-tree audit or an archive-seal audit.

## Actual construction, checking and admission

`phases/02-solve_B.json` and `phases/15-solve_C.json` contain actual OCM traces:
grounding, representation, navigation, extraction, indexed composition, checker PASS,
checked ANSWER, then authenticated admission. Each considers the one registered operator.
The stored OCM ledger has two query/checker-result sequences and two checked-proof batches;
the issuer journal contains REGISTERED followed by two PREPARED/COMMITTED pairs.

| Route | Checked run | Run evidence |
|---|---|---|
| B | `a6fcc05f50714090ba2014e983a14092` | `ev:ocm:a74ccba238ed3c65` |
| C | `e8094210b07b4ec988ca79b6dd5f2991` | `ev:ocm:278ae6a9a35f42cb` |

Each session has one separate worker process and one fresh checker sequence:
Lean version, Foundation compilation, fixed Target compilation and Candidate compilation.
All eight recorded Lean processes return 0 with empty stderr and complete raw output.
Version output identifies Lean 4.33.1, commit `819816b2e0a3bf405af45ae5c7af2491d8f5bee6`.
Both candidate outputs explicitly report that `OCMMechanicalProof.constructed` uses no axioms.
Both checker results name the same independently fixed `F0Target.statement` and target SHA
`0694094c1851d5fb72827f4af8a5de0e7d5fd14b646ad9926319f573206273ce`.

The worker output, returned OCM candidate, requested checker proposal and staged candidate
agree. Both generated Lean files prove `constructed : F0Target.statement := @proposed`.
The identical compiled hash is `bc04bf105235ce21741db927fec31549b17dbd02eaba800971748cfafd147c23`.
These are separate checked executions of the same argument, not independent mathematical discoveries.

Both searches record 24 applications, 37 generated terms and 10 introductions.
Their proof terms apply supplied hypotheses directly. Constant 0 (Eq) appears once in a
type annotation; imported proof-lemma usage is empty. This supports the existing
`PARENT_SUFFICIENT` apparatus interpretation, not learned lemma or method consumption.
OCM's logical `verification_calls=2` per solve is not two native kernel sequences per solve.

## A/B/C/S lifecycle

A is instruction/request provenance `ev:ocm:218dbf458738a6c7`;
S is shared checker/environment evidence `ev:ocm:210d3bd6cb9f235b`.
A is supplied registration provenance, not evidence that OCM discovered a new method.
Actual proof/claim objects carry `{B,S}` and `{C,S}` separately, yielding `S ∧ (B ∨ C)`.

| Raw phases | Observed consequence |
|---|---|
| 08–10 | Withdraw B: OPEN, including cold restart; reinstate B: LIVE |
| 11–12 | Withdraw A: proof LIVE, applicability false; restore A: applicability true |
| 16, 18 | Two authenticated routes; withdrawing B leaves C-supported LIVE |
| 19–20 | Both B/C withdrawn: OPEN; reinstatement restores LIVE |
| 21–22 | Withdraw shared S: OPEN; restore S: LIVE |

Withdrawal changes liveness; stored support expressions and authenticated historical routes
remain visible for audit. OPEN does not assert theorem falsity. Reinstatement uses the existing
evidence, without another native check or replacement checked-run evidence.

Cold phases 06, 09 and 23 have distinct host PIDs 3172845, 3172860 and 3174377;
all return 0 with empty stderr, matched child PIDs and recorded cleanup.
Each reports no session, no host operators, no executable operators, bound imports and read-only state.
Their LIVE/OPEN/LIVE results are authenticated data restoration and status evaluation;
they do not demonstrate new solving or learning after restart.

## Costs and allowed claims

Driver wall is 42.449141277 s through final freeze. The separate raw GNU-time record
`../proof-runtime-native-process-cost.txt` reports 42.54 s wall, 31.22 s user,
6.98 s system, 90,676 KiB maximum RSS and exit 0 for the recorded standalone command.
This RSS is not a simultaneous aggregate of all processes. Nested phase/session/checker
times overlap; adding them to outer wall would double count. Runtime preparation and
unknown original archive download cost remain separate. This is not full lifetime economics.

The actual second solve has more KSO atoms and navigation work (36 → 144); neither that
observation nor a one-operator index supports an active-subspace scaling or speedup claim.
The result provides checked persistent support and revision inside actual OCM.
It does not establish useful acquisition, transfer, FLT reconstruction, general proof-search
competence, superiority to adaptive symbolic parents, language-model parity or OCM novelty.

The closed proposer/checker use their fixed mechanical process contracts. Parent and cold
readers use pinned `-I -S -B` Python with explicit bound imports, but host/filesystem/journal
custody remains trusted. This is not whole-OCM or arbitrary-plugin no-neural qualification.
Reviewed README, CONTRACT and QUALIFICATION prose preserves these distinctions.

# G1.2 remaining subtraction + G1.3 controller-growth

**Terminal:** `COMPACT_VESSEL_PARTIAL`

This capsule finishes the G1.2 coordinates that #187 left open (compensating
composition, resource change, epistemic-invariant failure, necessity class)
and the G1.3 controller-growth series. It does not reopen the G1.1 freeze.

Parent freeze: [`research/g1-vessel-freeze-v1`](../g1-vessel-freeze-v1/CORE.md)
(`COMPACT_VESSEL_PARTIAL`). Duplicate-core deletion remains `NOT_EARNED`
(G1.1.6). #187 already showed M0 `OCMRuntime` and `work.Operator` are required
by current tests.

No production code was deleted. Subtraction is stub / monkeypatch, as in #187.

[Counts](COUNTS.json) · [Result](RESULT.json)

## G1.3 inventory (attribution series, not a git timeline)

Non-comment nloc, same definition as the freeze. Domain slices use the live
modules named in #165. Shared production Π is the freeze Π bucket (3588 nloc).
`dialogue/planner.py` is freeze-PRIOR but is counted here as domain-specific
controller.

| After adding | production Π | domain controller | cumulative controller | authored F/O nloc | learned F/O state bytes | Π Δ | F/O Δ |
|---|---:|---:|---:|---:|---:|---:|---:|
| language (`src/ocm/language` + `learning/language`) | 3588 | 170 | 3758 | 3203 | 0 | +170 | +3203 |
| math (`src/ocm/science` + `learning/methods.py`) | 3588 | 170 | 3758 | 4210 | 10917 | 0 | +1007 |
| procedural (`src/ocm/work` + `operators`) | 3588 | 170 | 3758 | 5096 | 10917 | 0 | +886 |

Language F/PRIOR inside the slice: field-bridge F 315 nloc, PRIOR 2888 nloc.
Math: lifecycle F 82 nloc, PRIOR 925 nloc. Procedural: O 886 nloc.

G2/G3 run artifacts are absent on this branch. Learned competence is therefore
measured from the experiment modules plus a live G2 `admit_macro`:

- G2 experiment 528 nloc / 23690 bytes (imported mechanism, not production Π)
- G3 experiment 557 nloc / 24387 bytes
- planner.py 170 nloc / 12280 bytes (authored language Π)
- one admitted `("inc","inc")` macro: 10917 ledger bytes; `solve.py` stays 536 nloc

`CONTROLLER_GROWTH_DOMINATES` is not issued: math and procedural additions grow
authored F/O, not production Π. `STATE_SIZE_DOMINATES` is not issued: one
admitted macro is smaller than planner.py source.

### Competence in F/O state

**PARTIAL_AT_POLYNOMIAL_SCOPE.** The G2 admit writes operator state into the
ledger without growing `solve.py`. Language competence remains authored
`planner.py`. Procedural competence remains authored `work` / `operators`
source. New competence does **not** predominantly appear in learned/imported
state across all three domains.

Architecture rule empirical status stays
`INTELLIGENCE_IN_F_AND_O = PARTIAL_AT_POLYNOMIAL_SCOPE` and
`Π remains small = PARTIAL`.

## Hostile (G1.3.3 / G1.3.4)

`hostile_pi_lookup` in `study.py` is a 7-nloc coefficient→program table
(`HOSTILE_PI_COEFFICIENT_TABLE_V1`). It solves the eight registered polynomial
identities in the table.

The G2 mechanism arm (`build_search_index` / `solve_from_index`) solves the
same tasks by enumeration. The marker and function name are absent from:

- `research/g2-macro-operator-v1/experiment.py`
- `src/ocm/learning/methods.py`
- `src/ocm/runtime/solve.py`

## G1.2 subtraction

Three restore-after probes. Production files stay in the tree.

### sqlite ledger vs jsonl — resource

Stub `SQLiteLedgerStore = None`. JSONL `LedgerStore` still appends and
verifies (capability unchanged). Live n=32: hash chains match; JSONL dir 7916
bytes vs SQLite/WAL dir 465376 bytes (WAL preallocation at this N);
JSONL `head` 0.273 ms vs SQLite 0.113 ms.

G5 physical denominator at N=2048 (cited, not re-run): JSONL cumulative rewrite
529,399,134 bytes vs SQLite parent 4,697,488 bytes; write amplification 1022×.
Terminal there: `DATABASE_PARENT_SUFFICIENT`.

### warrant interval — epistemic

`WarrantProfile.partial([{0}]).liveness({0})` is `UNKNOWN`.
`mutant_unknown_as_dead` returns `DEAD`. UNKNOWN count 1 → 0.
Certified LIVE/DEAD are unchanged. Witness:
`tests/m1/test_mutants.py::test_unknown_treated_as_live_and_as_dead_mutants`.

### work.Operator — algebraic, with compensating composition

Stub `work.contracts.Operator = None` and reload `work.envs`:
`TypeError: 'NoneType' object is not callable`. M9 construction fails
(algebraic/API necessity, as #187). Production code is not deleted.

Compensating composition: wrap `ent.classify_urgency` as `OperatorSpec`.
The wrapped backend still maps `{facts: {outage: True}}` → `urgency=high`
after the class is stubbed. M9 Skill/TaskContract tests are **not** preserved.
G1.1.6 remains not earned as deletion.

## Necessity (G1.2/006)

| Removed | Algebraic | Resource | Epistemic | Witness |
|---|---|---|---|---|
| sqlite vs jsonl | no | yes | no | n=32 dir/head delta; G5 N=2048 rewrite 529e6 vs 4.7e6 |
| warrant interval | no | no | yes | UNKNOWN disappears under boolean collapse |
| `work.Operator` | yes | no | no | M9 construction `TypeError`; OperatorSpec wrap recovers classify |

## G1.2 / G1.3 boxes

| id | status |
|---|---|
| G1.2/001 remove one at a time | `EARNED_AS_PROBES` |
| G1.2/002 compensating compositions | `EARNED_AS_MEASUREMENT` |
| G1.2/003 capability loss | `EARNED` (sqlite none; Operator M9 construction) |
| G1.2/004 resource change | `EARNED` |
| G1.2/005 epistemic-invariant failure | `EARNED` |
| G1.2/006 distinguish algebraic/resource/epistemic | `EARNED` |
| G1.2/007 PARENT_SUFFICIENT | `PRESERVED` |
| G1.2/008 do not call “minimal” from deletion | `OBEYED` |
| G1.3.1 controller growth across domains | `EARNED_AS_ATTRIBUTION_SERIES` |
| G1.3.2 competence in learned F/O state | `PARTIAL_AT_POLYNOMIAL_SCOPE` |
| G1.3.3 hostile Π table | `EARNED` |
| G1.3.4 hostile absent from mechanism | `EARNED` |
| G1.3.5 prior-information count | `EARNED_UPSTREAM` (freeze) |

## Terminal

`COMPACT_VESSEL_PARTIAL` is reaffirmed, not strengthened.

Not issued: `MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE`,
`CURRENT_KSO_PARENT_SUFFICIENT`, `CONTROLLER_GROWTH_DOMINATES`,
`STATE_SIZE_DOMINATES`, `DOMAIN_CORE_FORK_REQUIRED`.

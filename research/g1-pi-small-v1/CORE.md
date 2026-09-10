# G1 architecture box — Π remains small and domain-general (v1)

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) §2:

> Π remains small and domain-general.

Also measures the paired box that intelligence accumulates in F and O, not in
an ever-growing hard-coded controller, at the same microworld.

**Capsule terminal:** `PI_REMAINS_SMALL_AT_MICRO_SCOPE` ([`RESULT.json`](RESULT.json)).

**Programme-level terminal:** `COMPACT_VESSEL_PARTIAL` (not closed here).

## Predecessors (cited, not overwritten)

| capsule | terminal |
|---|---|
| [`research/g1-controller-growth-v1`](../g1-controller-growth-v1/CORE.md) | `COMPACT_VESSEL_PARTIAL` |
| [`research/g1-fo-competence-v2`](../g1-fo-competence-v2/CORE.md) | `COMPETENCE_IN_FO_STATE_AT_MICRO_SCOPE` |
| [`research/g1-duplicate-cores-v1`](../g1-duplicate-cores-v1/CORE.md) | `SINGLE_CORE_AT_SCOPE` (measurement, not deletion) |

G1.1.6 deletion is not this task.

## Measurement

Production controller nloc and SHA-256, before and after admitting competence:

| file | freeze role | why counted as controller |
|---|---|---|
| `src/ocm/runtime/solve.py` | Π | canonical domain-general Π_exec |
| `src/ocm/runtime/ocm_runtime.py` | Π | shared Admit_C executive for both domains |
| `src/ocm/dialogue/planner.py` | PRIOR | G1.3 domain-control; must not fork |

The freeze Π bucket (21 files, 3588 nloc at freeze) is snapshotted as supporting
inventory. Competence is the G2 `("inc","inc")` macro plus the L1 Adj–Noun
construction, admitted into one ledger-backed `OCMRuntime`.

## Pass / fail

- If those Π files grow: `PI_GREW_AT_SCOPE` (negative, first-class).
- If nloc is constant, files are byte-identical, F/O ledger bytes grow, and the
  same Π serves language construction + polynomial procedure with no
  domain-forked planner: `PI_REMAINS_SMALL_AT_MICRO_SCOPE`.

That micro-scope terminal is **not** programme-wide “Π remains small”. Hostile
coefficient tables remain in predecessor capsules; authored `work` / `operators`
remain. Architecture rule `PI_SMALL_DOMAIN_GENERAL` stays `PARTIAL` at
programme scope.

## Not claimed

`MINIMUM_SELF_EXTENDING_VESSEL`. Three-domain predominance. G1.1.6 deletion.
Unscoped `PI_REMAINS_SMALL`. Production `src/` edits.

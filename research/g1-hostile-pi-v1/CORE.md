# G1 remaining: hostile Π / authored work operator (v1)

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) §2:

> Π remains small and domain-general.

Predecessor [`research/g1-pi-small-v1`](../g1-pi-small-v1/CORE.md) earned
`PI_REMAINS_SMALL_AT_MICRO_SCOPE` and left the programme terminal
`COMPACT_VESSEL_PARTIAL`. The honest remainder named there is **hostile Π /
authored work operators**: a domain-specific hard-coded Π that would trivially
solve a task.

This capsule plants that hostile, requires it absent from the mechanism arm
(G1.3.3 / G1.3.4 already state this; this run measures it on a work task),
and asks whether domain-general Π plus F/O admission still works without it.

**Capsule terminal:** see [`RESULT.json`](RESULT.json). Legal terminals are
`PARENT_SUFFICIENT`, `PI_GREW`, `HOSTILE_PI_REQUIRED`.

`PARENT_SUFFICIENT` is not programme failure. It means the parent Operator /
Skill / Admit_C path solved the planted work tasks without the hostile lookup.
Programme-wide `PI_SMALL_DOMAIN_GENERAL` stays `PARTIAL` because authored work
backends remain as prior information (G1.3.5). Nothing here ticks G1.1.6
deletion or issues `MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED`.

## Predecessors (cited, not overwritten)

| capsule | terminal |
|---|---|
| [`research/g1-pi-small-v1`](../g1-pi-small-v1/CORE.md) | `PI_REMAINS_SMALL_AT_MICRO_SCOPE` |
| [`research/g1-fo-competence-v2`](../g1-fo-competence-v2/CORE.md) | `COMPETENCE_IN_FO_STATE_AT_MICRO_SCOPE` |
| [`research/g1-controller-growth-v1`](../g1-controller-growth-v1/CORE.md) | `COMPACT_VESSEL_PARTIAL` |

Parents already planted `HOSTILE_PI_COEFFICIENT_TABLE_V1` on polynomial
identities. This remainder is a **work-operator** hostile, not a second
coefficient table.

## Hostile (G1.3.3)

`hostile_work_pi_lookup` in `experiment.py` (`HOSTILE_PI_WORK_OPERATOR_V1`) is
a domain-specific rule: planted enterprise case → `escalate` iff outage else
`reply_faq`. It solves the checker’s expected action without gather / classify
/ policy / verify.

## Mechanism arm (G1.3.4)

The hostile marker and function name must be absent from production Π, the
generic `work.Operator` / `run_skill` path, and the G2 admit module. The
mechanism:

1. Binds the parent role skeleton (`gather → classify → check_policy →
   act_smallest → verify → document`) to production `enterprise_operators`.
2. Executes `run_skill` on the planted tasks. The hostile function is not
   called.
3. Admits that skill as a ledger procedure atom and admits the G2
   `("inc","inc")` macro into the same `OCMRuntime` (F/O).
4. Measures `solve.py`, `ocm_runtime.py`, and `planner.py` nloc before and
   after. Growth is `PI_GREW`.

Polynomial primitives, if touched, are pinned at methods.py blob
`50323a33418b8ef8bb6500ddeba4b9d1f795e9e3`.

## Pass / fail

- Hostile solves every planted task, is absent from the mechanism arm, F/O
  grows, controller files stay byte-identical, `run_skill` succeeds with zero
  hostile calls: `PARENT_SUFFICIENT`.
- Measured Π files grow: `PI_GREW`.
- Mechanism cannot solve the planted work tasks without the hostile:
  `HOSTILE_PI_REQUIRED`.

## Not claimed

`MINIMUM_SELF_EXTENDING_VESSEL`. Programme-wide `PI_REMAINS_SMALL`. G1.1.6
deletion. Production `src/` edits. Three-domain predominance.

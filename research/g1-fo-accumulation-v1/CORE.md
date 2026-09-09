# G1 architecture box — intelligence accumulates in F and O (v1)

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) §2:

> Machine intelligence accumulates primarily in F and O, not in an
> ever-growing hard-coded controller.

**Capsule terminal:** see [`RESULT.json`](RESULT.json) after the local run.
Expected positive: `FO_ACCUMULATION_AT_MICRO_SCOPE`. Honest negatives:
`CONTROLLER_GREW_AT_SCOPE`, `NO_FO_BYTE_GROWTH_AT_SCOPE`,
`FO_ACCUMULATION_INCOMPLETE_AT_SCOPE`.

**Programme-level terminal:** `COMPACT_VESSEL_PARTIAL` (not closed here).

## Predecessors (cited, not overwritten)

| capsule | cited when |
|---|---|
| [`research/g1-fo-competence-v2`](../g1-fo-competence-v2/CORE.md) | tracked on this tree (`COMPETENCE_IN_FO_STATE_AT_MICRO_SCOPE`) |
| [`research/g1-pi-small-v1`](../g1-pi-small-v1/CORE.md) | if that RESULT is git-tracked |
| [`research/g1-controller-growth-v1`](../g1-controller-growth-v1/CORE.md) | tracked (`COMPACT_VESSEL_PARTIAL`) |
| [`research/g1-duplicate-cores-v1`](../g1-duplicate-cores-v1/CORE.md) | tracked (`SINGLE_CORE_AT_SCOPE`; measurement, not deletion) |

This capsule does not rewrite those `RESULT.json` files. It does not claim
the paired box “Π remains small and domain-general” as a programme close
(that is `g1-pi-small-v1` if present). Freeze architecture rule
`INTELLIGENCE_IN_F_AND_O` stays design-earned at freeze; this run is the
empirical micro-scope accumulation measurement.

## Measurement

Admit one G2 `("inc","inc")` macro **and** one L1 Adj–Noun construction into
a single ledger-backed `OCMRuntime`. Count:

| quantity | meaning |
|---|---|
| Π nloc | non-blank, non-comment lines of `solve.py`, `ocm_runtime.py`, `planner.py`, plus the freeze Π bucket |
| ledger F/O bytes | on-disk ledger directory size after each admit |

Authored freeze F and O source nloc are snapshotted as a control: they must
not grow either. Growth is supposed to be instance state, not new authored
field/operator modules.

## Pass / fail

- If measured Π nloc is constant **and** ledger F/O bytes grow (G2 slice
  and L1 slice both positive): `FO_ACCUMULATION_AT_MICRO_SCOPE`.
- If Π nloc grows: `CONTROLLER_GREW_AT_SCOPE`.
- If Π is constant but ledger bytes do not grow: `NO_FO_BYTE_GROWTH_AT_SCOPE`.
- If admits do not both land as live procedure atoms: `FO_ACCUMULATION_INCOMPLETE_AT_SCOPE`.

Micro-scope only. Procedural `work` / `operators` remain authored. Not
three-domain predominance.

## Not claimed

`MINIMUM_SELF_EXTENDING_VESSEL`. Unscoped `INTELLIGENCE_IN_F_AND_O` as a
programme close. `PI_REMAINS_SMALL`. G1.1.6 deletion. Production `src/`
edits.

# Publication after-execution receipts v1

Harvest of [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) §15
**after-execution** boxes that can be earned from this repository without a
second machine. Does **not** close [#144](https://github.com/SzeChunYiu/ORION-OCM/issues/144).
Does **not** invent E4, a fresh host, independent authorship, or an independent
scorer.

v1/v2 publication-constitution freeze files stay on disk unchanged. Their
terminals remain `PUBLICATION_CONSTITUTION_FROZEN_WITH_GAPS`. This capsule
does not overwrite `research/publication-constitution-v1/` or
`research/publication-constitution-v2/` `RESULT.json` (none is written here).

## Question

Which §15 after-execution boxes already have in-tree receipts (RESULT.json,
CI-retained prototype traces, SHA-256 manifests, CORE/result correspondence),
and which still require a second machine / disjoint replication / independent
scorer?

## Earned from this checkout

| box | harvested from |
|---|---|
| retain raw traces | G3.2 `failure_attempts_v1`; native-generation diagnostic/timeout raw `result.json` archives (not G2.4/G3.1 confirmatory CI artifacts) |
| retain failures | G3.2 retained failed attempts; H1 v2 negative terminal; L1 v3 `NO_CROSS_FAMILY_TRANSFER` |
| retain crashes/timeouts | native-generation timeout/error/watchdog captures; G3.4 timeout-only diagnosis row |
| machine-readable receipts | capsule `RESULT.json` / constitution `PROTOCOL.json` / CINV audit |
| raw cost vectors | G3.2 `accounting`; G5.2 scaling walls/bytes; G2.4 restart and P1 `slots` / enumeration attempts |
| immutable figure tables | G5.2 `scaling` / `SUMMARY.json` / `results/scaling_raw.json` |
| exclusions with reasons | G3.2 `prior_exposed_length6_n` + salt note; L1 v3 held-out family exclusion |
| checksum manifest | this harvest SHA-256 plus verified in-tree `SHA256SUMS` (p0, diagnostic raw, timeout archive) |
| claim/result correspondence review | mechanical CORE.md ↔ RESULT.json/PROTOCOL.json terminal/claim check (author-side, not an independent reviewer) |

## Still `CANNOT_CHECK`

| box | conversion |
|---|---|
| fresh-host rerun | `CANNOT_CHECK_NO_SECOND_MACHINE` — this checkout is not a second host; do not relabel same-head CI as E4 |
| disjoint replication | `CANNOT_CHECK_NO_E4_DISJOINT_REPLICATION` — same-head harvest is not E4 |
| independent scorer/checker | `CANNOT_CHECK_NO_INDEPENDENT_SCORER` — in-ecology oracles are not an independent scorer |
| red-team reviewer simulation | `CANNOT_CHECK_NO_INDEPENDENT_RED_TEAM` |
| §16 independently authored families | `CANNOT_CHECK_NO_INDEPENDENT_AUTHORSHIP` — need a **human independent author** to donate world/task families; internal generators remain audit-only |

G2.4 / G3.1 confirmatory raw traces remain **absent on this head**
(`MISSING_ON_THIS_HEAD_CI_ARTIFACT`). Later capsules and prototype archives
are not a substitute G2.4 trace dump.

## Terminal

```text
PUBLICATION_AFTER_EXEC_RECEIPTS_PRESENT_WITH_GAPS
```

# GMI lifecycle meter exact calibration v1

Status: **EXECUTABLE SYNTHETIC METER / B2 PARTIAL CLOSURE**

Date: 2026-09-12.

Purpose: close the first, exact-accounting half of closure blocker B2 before any hardware/software-counter claim.

## 1. Burden vector

For a registered execution trace define

\[
B=(B_{build},B_{storage},B_{serve},B_{update},B_{verify},B_{history},B_{search}).
\]

No scalar total is reported without a registered price vector. The exact meter records every component separately.

## 2. Hostile trace family

The runner generates all 32 combinations of five binary ecology factors:

```text
structured reusable law vs unstructured records
low vs high query reuse
local vs global updates
no retention vs retained historical access
rare vs frequent updates
```

Each world expands into an explicit event trace: build, query, update, verify, retention storage and history query events.

## 3. Realization families

Four plain structural realizations are metered:

```text
table / indexed records
shared fitted state
shared core + explicit residual state
per-query search over source records
```

The runner computes the burden in two independently written ways:

1. event-by-event accumulation;
2. closed-form count identities from the trace parameters.

The two routes must match componentwise.

## 4. Exact meter theorem

For any trace whose event contributions are additive in the registered burden coordinates, the event accumulator and the corresponding closed-form event counts are identical by finite additivity. The hostile suite is valuable because it checks that the implementation did not omit retention, verification, search or update events when switching realization family.

## 5. Executed receipt

`run_gmi_lifecycle_meter_exact_v1.py` checks:

```text
32 worlds
4 realization families per world
7 burden coordinates
896 componentwise equalities
```

Result: zero mismatches.

Receipt: `GMI_LIFECYCLE_METER_EXACT_RECEIPT_V1.json`.

## 6. What this closes and what it does not

Closed at synthetic registered scope:

```text
explicit event taxonomy
componentwise meter conservation
retention/search/verification are not silently free
32-hostile-trace exact accounting C1 pilot
```

Still OPEN-BLOCKING for B2:

```text
independent implementation audit
real wall-clock / memory / energy / communication counters
compiler/runtime overhead
cache effects and concurrency
hardware-dependent pricing
hidden data/search/tool costs outside the trace contract
```

The exact meter is a prerequisite for frontier evidence, not frontier evidence itself.

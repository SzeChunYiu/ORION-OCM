# Physical resource metering + B19 real sequences

Issue [#602](https://github.com/SzeChunYiu/ORION-OCM/issues/602) leftovers after
[#805](https://github.com/SzeChunYiu/ORION-OCM/pull/805):

- Section N physical CPU/GPU/wall/IO counters
- Section N energy counters where feasible
- B19 "Test under real task sequences"

## Relation to #805

`research/gmi-resource-lifecycle-ledger-v1/` remains the derivation-only
fourteen-coordinate ledger and still reports `physical_metering: OPEN` /
`energy_metering: OPEN` in its own JSON. This package is a **sibling**, not a
rewrite: it supplies an executable measurement bridge and honest status tags.

## Run

```bash
python3 physical_resource_metering_v1.py --host-tag local
python3 continual_real_sequence_b19_v1.py
python3 -m unittest -v test_physical_resource_metering_v1.py test_continual_real_sequence_b19_v1.py
./run_hosts.sh
```

## Claim ceilings

| Artifact | Ceiling |
|---|---|
| Physical harness | `PHYSICAL_COUNTERS_CLOSED_AT_SCOPE` for wall/CPU; IO/GPU tagged AVAILABLE or UNAVAILABLE (never silently zero); energy CLOSED only with calibrated RAPL |
| Energy on Darwin / no RAPL | remains OPEN — joules are not inferred from operation counts |
| B19 witness | `REAL_SEQUENCE_WITNESS_AT_PLANTED_SCOPE` on two planted sequential classification sequences |

## Falsifiers

See `PHYSICAL_METERING_CONTRACT_V1.json`.

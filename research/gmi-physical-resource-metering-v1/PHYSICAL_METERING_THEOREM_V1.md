# Physical metering theorem note v1

## Contract

At a prospectively registered scope, a physical measurement reports wall and
process CPU deltas from `time.perf_counter` and `resource.getrusage`. IO and
GPU coordinates are AVAILABLE only when the host exposes an attributable probe;
otherwise they are UNAVAILABLE or UNCALIBRATED and must not be coerced to zero.
Energy is AVAILABLE only from a calibrated counter (readable
`intel-rapl` `energy_uj`); otherwise energy remains OPEN. Operation counts from
the #805 lifecycle ledger are never relabeled as joules.

## Sibling conservation

The fourteen-coordinate derivation ledger stays untouched. This package reads
its OPEN physical/energy markers as evidence that the measurement bridge is
still required, then closes physical counters at harness scope without rewriting
that ledger file.

## B19 real-sequence lemma

On two planted sequential classification sequences with hard finite stores, the
registered cheap-capacity price vector selects `expand` on both sequences, and
the dear-capacity / cheap-store vector selects `modularize` on both. The winner
is therefore stable across concrete task geometries at fixed prices and moves
when prices change — the executable content of "test under real task sequences"
at planted scope.

## Scope

Microworld / planted only. No ImageNet continual-learning transfer claim. No
universal energy accounting on hosts without calibrated probes.

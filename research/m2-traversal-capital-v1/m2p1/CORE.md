# M2-P1 hidden-family developmental study — CORE (read first)

Lane `LANE_M2_TRAVERSAL_CAPITAL_OPUS`. Owner #165, hardening parent #323.
Successor to the M2 negatives ([../RESULT.md](../RESULT.md)), under the design
registered in [../HIDDEN_FAMILY_DESIGN.md](../HIDDEN_FAMILY_DESIGN.md) **before** any
scored result was read.

## The question

Does developmental history make **new** verified cognition cheaper to acquire — as
opposed to replaying stored answers?

## What was changed: nothing in OCM

`src/ocm/learning/methods.py` is imported and driven **AS-IS**. `learn_generator`,
`validate_generator`, `solve` and `verify_solution` are the registered units. No new
cognitive core, no learned router (#71), no admission loosening, no threshold tuning
(#323 §11). **The ecology changed, not the machine.**

## Result in one line

History-mined structure cuts the work to acquire new externally verified targets by
**20–62 %** across six independent worlds on two hosts — and the registered admission
gate refuses it in **6 of 6**, for a reason that is provably structural.

## Findings

| # | terminal | where |
|---|---|---|
| M2-P1a | `DEVELOPMENTAL_SEARCH_PRIOR_DEMONSTRATED` | [RESULT.md](RESULT.md#m2-p1a) |
| M2-P1b | `ADMISSION_VETO_IS_STRUCTURAL` | [RESULT.md](RESULT.md#m2-p1b) |
| M2-P1c | development-depth dose-response | [RESULT.md](RESULT.md#m2-p1c) |

## Claim ceiling (registered before the run)

> history-induced search-prior transfer, on an authored ecology whose family structure
> is measured not to be surface-derivable.

**Not** general developmental intelligence. Fresh-*host* replication is met (billy-old
+ LUNARC); fresh-world replication is met across six independently seeded worlds with
different hidden motif sets; **replication on an ecology authored by someone else
remains unmet**, so #323's success certificate is not claimed closed.

## Raw records

`records/` — per-world `dev_state.json`, `ATTRIBUTION.json`, `ECOLOGY_HEADER.json`,
and `M2P1_GATE_V1.json`. Emitters are the `m2p1_*.py` scripts beside this file;
`m2p1_world.sbatch` is the LUNARC array.

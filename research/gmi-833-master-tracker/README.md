# GMI #833 Master Tracker

Single coordination point for **Issue #833 — GMI Ultimate Theory Review & Architecture-Prior-Free Derivation Programme**.

**Scope ledger:** `BOX_LEDGER_V1.json` (485 boxes: 259 main-body A–M + 95 addenda AA–AD + 131 Z-gates). Owned sections: see `SECTION_OWNERSHIP_V1.json`.

## Working rules (per addenda AA/AD)

- `expressible != admissible != derivable != reachable != selected != recovered != predicted != replicated != real-scale validated`.
- Closure states: OPEN / LOCALLY_CLOSED / HOSTILE_CLOSED / REPLICATED_CLOSED / REAL_SCALE_CLOSED. Never bare "closed" scientifically.
- Every tranche emits: FORMALIZATION.md (all theorems+proofs), executable reconstruction, house-pattern test vs committed RECEIPT, `OPEN_GAPS_<T>.json` (AA ledgers + OPEN_GAP records), `PARENTS_<T>.md`.
- Vocabulary per AB: no `obligation` in paper prose (task/behavioral specification/requirement); no bare `prior-free` (architecture-prior-free within ledger `L`), no family names as grammar primitives.
- Recursion: every closed gap asks what the repair newly assumed; emit new-gap records. Stop only at the declared evidence ceiling, never at box count. A negative is intermediate — revive it (attribute → lever → re-test).

## Fleet (round 1+2, parallel lanes)

| Section | Boxes | Owner | PR |
|---|---|---|---|
| A/C/D/AA | 15+24+18+41 | other lane (research/gmi-theory-foundations-v1, PR #835) | #835 |
| E/F | 23+16 | tranche-ef-grammar | — |
| G | 23 | tranche-g-ecology | — |
| H | 45 | tranche-h-knownforms | — |
| I/J | 16+15 | tranche-ij-learnlaw | — |
| K/L | 17+15 | tranche-kl-capdev | — |
| M | 11 | tranche-m-cognition | — |
| B | 21 | tranche-b-audit | — |
| AB/AC | 37+9 | tranche-ab-ac-lit | — |
| Z1–Z18 | 131 | master-tracker + z-gate tranches (round 3) | — |

## Merge policy

- Poll each PR head's CI to `conclusion=success` BEFORE merging (no required-checks protection; `--auto` ignored; only `conclusion=success` is green).
- Merge per result as soon as it lands; never let findings sit on a local branch.
- `GMI_GAP_GRAPH` stays fail-closed: a CRITICAL descendant keeps #833 OPEN.

## Recurring Z-gate layer (round 3)

Z1 master principle, Z2 minimal prior, Z4 universality classes, Z5 scaling, Z6 discriminations, Z7 impossibility, Z8 hostile worlds, Z9 blind protocol, Z10 real domains, Z11 benchmark, Z13 W4, Z15 falsifiers, Z16 groundbreaking, Z18 hostile review — several depend on tranche receipts; recruit after round-2 merges.

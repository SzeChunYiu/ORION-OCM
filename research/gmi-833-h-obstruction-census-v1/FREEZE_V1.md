# Section H obstruction census V1 — pre-outcome freeze

Freeze commit: the git commit whose tree first contains this file; its hash is
recorded in the child issue and later custody manifest without rewriting this
pre-outcome tree.

Source base: `b30237c229b2c3fd4016de19c5fa9c155c0a7484` (`origin/main` at freeze preparation)

Issue source: `SzeChunYiu/ORION-OCM#833`, body SHA-256
`cf30a2a76e4f961f96bd8a76cdd9d5e68b79f776e5feffe8d94da353f9b3f8a1`.

## Question frozen before implementation

For the complete 43-row named-family registry in Section H, which registered
finite hallmark contracts are not recoverable by one common family-name-free
Boolean expression grammar under one fixed ecology and budget, and is each
failure an expressivity, resource, or identifiability obstruction?

This is deliberately narrower than universal family non-recoverability.  Each
registry entry is a finite operational hallmark contract, not a definition of
the full historical family.  A recovered hallmark never closes a family row.
An obstructed hallmark proves only that the registered family contract cannot
be recovered in the frozen grammar/ecology/budget scope.

## Frozen grammar, ecology, and search

- Interface: eight Boolean coordinates `x0..x7`.
- Grammar leaves: `0`, `1`, `x0`, `x1`, `x2`, `x3`.
- Grammar operators: unary `NOT`; binary commutative `XOR` and `AND`.
- Cost: every leaf and operator node costs one; budget `B=3`.
- Protected semantics: all 256 points of `{0,1}^8`.
- Observation ecology: the eight points spanning `x0,x1,x2` while fixing
  `x3=x4=x5=x6=x7=0`.
- Search: enumerate the complete semantic quotient through cost three, retain
  candidates matching all observed rows, then minimize exact node cost without
  an extra tie-breaker.
- Lower-bound oracle: independently enumerate semantic layers through cost
  five for registered resource witnesses.

Coordinates have only interface meanings: `x3` is an unexcited context probe;
`x4` a history/state probe; `x5` a stochastic-source probe; `x6` an update or
feedback probe; and `x7` an external/peer/tool-result probe.  These are external
channels, not architecture names or family macros.

## Frozen theorem obligations

1. **EXPRESSIVITY.** Every grammar denotation is invariant in `x4..x7` by
   structural induction.  A registered target that changes when one of those
   coordinates alone changes is absent at every budget, not merely unobserved
   in a finite search.
2. **RESOURCE.** `x0 XOR x1 XOR x2` and `x0 AND x1 AND x2` have minimum grammar
   cost five.  Therefore neither is recoverable at `B=3`, while a cost-five
   witness proves this is a budget obstruction rather than an expressivity one.
3. **IDENTIFIABILITY.** `x3` and constant zero agree on every frozen ecology
   row, have equal minimum cost one, and disagree on the protected interface.
   Thus the protected target is not identified by the complete set of
   cost-minimal observational fits.
4. **POSITIVE CONTROL.** `x0`, `NOT x0`, `x0 XOR x1`, and `x0 AND x1` must be
   recovered uniquely at respective minimum costs 1, 2, 3, and 3.
5. **COMPLETE CENSUS.** Exactly the 43 named Section H rows appear once in the
   frozen registry.  Every row receives one machine-derived disposition and a
   theorem witness; no named family checkbox is changed.
6. **REMINT.** Permuting candidate identifiers and enumeration order preserves
   semantic quotient, minimum costs, obstruction classes, and the 43-row
   census.
7. **INDEPENDENT ORACLE.** A source-separated direct truth-table oracle, which
   imports no primary implementation, agrees on target semantics, observed
   projections, minimum costs, and dispositions.

## Frozen predicted terminal

`REGISTERED_43_FAMILY_HALLMARK_CENSUS_COMPLETE__UNIVERSAL_NONRECOVERABILITY_FORBIDDEN`

Predicted census: 7 recovered controls, 6 identifiability-obstructed contracts,
9 resource-obstructed contracts, and 21 expressivity-obstructed contracts.

## Preflight disposition

The already-checked shared-grammar row remains supported on `main` by merged
PRs #931–#937 and #951 at their declared finite scope.  Open PR #960 is an
independent bounded corroboration and explicitly leaves its four named family
rows open because the real-scale gate is open.  Issues #431 and #434 remain
open.  No named family row is eligible here: this package neither supplies a
real-scale test nor a complete ten-gate family ledger.

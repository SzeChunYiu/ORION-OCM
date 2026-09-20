# Section-H family tranche A freeze

## Scope and ownership

This package covers exactly eight rows not covered by the symbolic/SSM/retrieval
package: nearest-neighbor/exemplar memory (H05), associative memory (H06),
decision trees/rule systems (H08), program synthesis/program induction (H10),
library-learning/program-reuse systems (H11), search/frontier algorithms
(H12), planning systems (H13), and dynamic programming/control (H14).
Symbolic logic (H09), retrieval-augmented (H07), and state-space models (H28)
are explicitly excluded because a separate abandoned-but-valuable package owns
them. This package also claims no neural rows.

The claim ceiling is a registered finite derivation at one neutral Boolean scope
per row. It closes no issue checkbox without R11 real-scale evidence. The
following rows are replacements for the excluded rows only when a later
reconciliation explicitly names them: H18 probabilistic graphical models, H19
particle/population inference, H31 latent-variable generative systems, H32
flow-like transport systems, H34 energy-based systems, H36 cellular/local-field
computation, H37 distributed/collective intelligence, H38 tool-using/solver-routing
intelligence, H40 continual-learning systems, and H41 meta-learning systems.
No replacement row is claimed by this package.

## Frozen common grammar

Before implementation, the common grammar `G_HA` is fixed. Leaves are constants
`0`, `1` and generic input coordinates `x0` through `x7`. Operators are `NOT`,
`XOR`, and `AND`; cost is one node per leaf or operator. Expressions are
exhaustively enumerated and semantically quotiented over the registered finite
point set. The generator and selector receive no family name, row name, or
family-specific candidate menu. Structural family names are attached only by
the post-hoc mapping in `POSTHOC_MAPPING_V1.json`.

The ecology for every finite scope is the complete binary cube `{0,1}^8`, so
all channels are excited. Search is complete over the frozen budget `B=5`.
The primary protected contract is the exact target truth table. The matched
negative is evaluated under the same grammar and budget and must be rejected as
the positive class by the post-hoc classifier.

## Frozen property predictions

The predictions are made from generic behavioral properties, before any checker
or outcome exists. Each row's property is a generic contract, not a historical
architecture definition.

| row | generic property prediction | target contract | matched negative |
|---|---|---|---|
| H05 nearest-neighbor/exemplar | output depends on an addressable reference-context coordinate | `x3` | `0` |
| H06 associative memory | output depends on a cue-context coordinate | `x3` | `1` |
| H08 decision trees/rules | output requires three simultaneous threshold conditions | `x0 AND x1 AND x2` | `x0 XOR x1 XOR x2` |
| H10 program synthesis/induction | output satisfies three simultaneous behavioral constraints | `x0 AND x1 AND x2` | `x0 XOR x1 XOR x2` |
| H11 library/program reuse | output depends on a reusable-library context coordinate | `x3` | `0` |
| H12 search/frontier | frontier acceptance requires three simultaneous conditions | `x0 AND x1 AND x2` | `x0 XOR x1 XOR x2` |
| H13 planning | plan acceptance requires three simultaneous conditions | `x0 AND x1 AND x2` | `x0 XOR x1 XOR x2` |
| H14 dynamic programming/control | output depends on a persistent history/state coordinate | `x4` | `0` |

The duplicate contract assignments are intentional matched scopes: the selector
must recover the same structure without being told which row will be named
post-hoc. For H05/H06/H11, the coordinate is varied over the full ecology; for
H14, `x4` is interpreted as the registered history probe only after recovery.

## Eleven requirements and current prediction

R01 property prediction, R02 shared grammar, R03 semantic no-family-macro audit,
R04 family-blind recovery, R05 matched negative control, R06 exact lower bound,
R07 two price regimes with a winner crossover, R08 held-out frozen contract,
R09 alternate encoding, R10 source-separated independent search, and R11
sha256-bound real-scale evaluation are each tracked at the same scope. The
finite derivation is predicted to satisfy R01-R10. R11 is frozen as
`OPEN_REAL_SCALE_PENDING`: no finite result licenses real scale, and no issue
row may be marked closed without it.

## Falsifiers and forbidden promotions

Any family-name or row-name dependency in generation or recovery, a grammar
digest change, a matched negative control recovered as the positive class, an alternate-encoding class
change, disagreement between routes, a lower-bound mismatch, or a crossover
that does not reverse the winner falsifies the corresponding coordinate. The
checker must fail loudly on malformed or missing receipts.

Forbidden promotions are `CROSS_SCOPE_GATE_COMPOSITION`,
`FINITE_EVIDENCE_IMPLIES_REAL_SCALE`, `NAMED_FAMILY_ROW_CLOSED`,
`SECTION_H_COMPLETE`, `UNIVERSAL_GRAMMAR_NEUTRALITY`, and
`INDEPENDENT_TEAM_REPLICATION`.

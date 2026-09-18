# FREEZE — `gmi-833-ah4-organization-ladder-v1`

Committed **before** any executor, oracle, test, receipt or workflow file of this package.

## Custody

| field | value |
|---|---|
| `source_main` | `5e57d4292266bccf435136e1f7d72caa32e920a0` |
| issue | `SzeChunYiu/ORION-OCM#833` |
| section | AH4 (four rows) |
| comment | `5693590252` |
| claim ceiling | `AH4_ORGANIZATION_LADDER_INVARIANTS_AND_LEVEL_STRUCTURE_AT_REGISTERED_FINITE_SCOPE` |

## The exact rows this tranche may reconcile

Byte-exact from comment `5693590252` at `source_main`, all under the anchor
`### AH4 — Hierarchy of organization / “periodic table” of MI`:

```
- [ ] Define measurable invariants for each transition `L_i -> L_(i+1)`.
- [ ] Construct nearest negative systems that remain at `L_i`.
- [ ] Determine whether any levels collapse or require additional intermediate layers.
- [ ] Do not define intelligence by membership in a level until capability/development evidence warrants it.
```

**No neighboring row is earned here.** AH0, AH1, AH3, AH5, AH6 and AH7 are untouched, as is
every AG and AJ row.

## What is frozen

### 1. The ladder, verbatim from the issue

`L0` elementary substrate/process events · `L1` stable local motifs / reusable transition
patterns · `L2` state-bearing modules / bounded computational organizations · `L3` interacting
modules / composed machines · `L4` adaptive organizations whose internal state/update changes
from experience · `L5` developmental organizations that alter representation/operators/search
law · `L6` self-modeling/self-modifying organizations under verification/governance ·
`L7` populations/collectives/cultural inheritance / multi-instance development ·
`L8` grammar/theory expansion and new effective units.

The issue calls this hierarchy provisional. This tranche treats it as a hypothesis to be
measured, not a result to be confirmed.

### 2. The eight invariants, named and fixed before any run

One per transition. Each is an exactly computable predicate on a registered system, with a
declared clause decomposition so that a partial pass can be detected.

| transition | name | passes when |
|---|---|---|
| `L0 -> L1` | `I1_MOTIF_REUSE` | the same local step map is instantiated at two or more distinct sites |
| `L1 -> L2` | `I2_HISTORY_DEPENDENCE` | clause (a) the system holds a persistent state cell; clause (b) its external word behaviour is not equal to that of any cell-free system at the same interface |
| `L2 -> L3` | `I3_IRREDUCIBLE_COMPOSITION` | the composite's external word behaviour is realized by no single module of the base budget |
| `L3 -> L4` | `I4_EXPERIENCE_CONDITIONED_UPDATE` | two histories share a current state and input yet give different successors |
| `L4 -> L5` | `I5_OPERATOR_INVENTORY_GROWTH` | the set of available operators strictly grows during development |
| `L5 -> L6` | `I6_EXTERNALLY_ADMITTED_SELF_CHANGE` | the active step map is replaced by a transition whose guard consumes a value the internal state does not determine |
| `L6 -> L7` | `I7_CROSS_INSTANCE_ACQUISITION` | a distinction reaches one instance only through a registered transfer channel, and lies outside that instance's own reachable set |
| `L7 -> L8` | `I8_NEW_EFFECTIVE_UNIT` | the operator inventory gains a unit that leaves expressive power unchanged while changing description length or search distance |

`I8` is worded that way deliberately: the merged `gmi-833-developmental-reuse-v1` result is that
a macro library adds zero expressive power. A level-8 claim resting on new expressive power
would contradict a merged parent, so the invariant is stated on description and search geometry
instead.

### 3. The registered universe

- **Base.** The AJ4 organization set at the registered binary budget: four cell-free and 256
  one-cell systems, 260 in total, over binary input and output. Rebuilt here, not imported.
- **Word behaviour.** Decided by reachable product exploration; the length-bounded response
  signature is the independent cross-check, never the authority.
- **Composites.** All ordered pairs of class representatives wired in series.
- **Witness families.** Two, both fixed here: a **cumulative** family `C0 … C8`, each extending
  the previous, which shows every level is attainable; and a **minimal** family `M0 … M8`, each
  the smallest system exhibiting only its own level's described feature. The invariant matrix
  is measured over the minimal family; the cumulative family is the attainability control.

### 4. The gates, fixed before any run

`GREEN` requires: every invariant decidable with no error terminal on every registered system;
each of the eight invariants exhibiting at least one passing and one failing system (otherwise
the invariant is recorded as `NOT_SEPARATING_AT_SCOPE`, which is a result, not a failure); the
nearest-negative search returning a minimum edit distance for every transition where one
exists; route A and route B agreeing on every published quantity; every declared hostile
detected with a clean control; the randomized null not reproducing the measured matrix; and the
no-alarm case asserted.

### 5. Falsifiers, fixed before any run

- If every system that passes `I_i` also passes `I_{i+1}` over the whole registered universe,
  that transition **collapses** at this scope and is published as `COLLAPSED`, not as a level.
- If some system satisfies a proper non-empty subset of an invariant's clauses, an intermediate
  layer is indicated and must be named rather than absorbed into either neighbour.
- If the measured invariant matrix over the minimal family is not lower-triangular, the ladder
  is **not** a total order at this scope and must be published as a partial order.
- If no configuration can trip the level-membership prohibition, that row is vacuous and stays
  unchecked.
- If a randomized assignment of levels reproduces the measured matrix, the invariants do not
  identify the levels and the ladder claim is withdrawn.

## Forbidden promotions

`PERIODIC_TABLE_OF_MI_COMPLETE`, `LEVEL_MEMBERSHIP_IS_INTELLIGENCE`,
`LADDER_IS_TOTAL_ORDER`, `ALL_ORGANIZATION_LEVELS_ENUMERATED`,
`HIGHER_LEVEL_IMPLIES_HIGHER_CAPABILITY`, `UNBOUNDED_LEVEL_HIERARCHY_PROVED`,
`COMPLETE_GMI`.

## What is not claimed novel

Mealy machine theory, product-construction equivalence, the Moore length bound, sequential
circuit state minimization, macro libraries and their expressive neutrality, externally
attested update, and inheritance between instances are all parent mathematics, pinned in
`PARENT_LEDGER.md`. The residual contribution is the eight named invariants, their exhaustive
measurement over one registered universe, the nearest-negative construction, the resulting
level-structure verdict, and a prohibition checker with a configuration that trips it.

# FREEZE — `gmi-833-ah7-data-varied-choice-v1`

Committed **before** any executor, oracle, test, receipt or workflow file of this package.

## Custody

| field | value |
|---|---|
| `source_main` | `5e57d4292266bccf435136e1f7d72caa32e920a0` |
| issue | `SzeChunYiu/ORION-OCM#833` |
| section | AH7 (one row) |
| comment | `5693590252` |
| claim ceiling | `AH7_DATA_AXIS_MOVES_THE_PREFERRED_FORM_WITH_SPACE_REQUIREMENT_AND_PRICING_HELD_FIXED` |

## The exact row this tranche may reconcile

Byte-exact from comment `5693590252` at `source_main`, under the AH7 anchor, which is pinned
byte-exact in `MANIFEST_V1.json` rather than repeated here:

```
- [ ] Demonstrate same possible MI space with different data producing different selected morphologies.
```

**No neighboring row is earned here.** AH7's two already-checked rows are untouched — in
particular the requirements-and-pricing row, which the merged niche-repricing package pinned in
`MANIFEST_V1.json` already owns, is not re-earned. Every AG, AJ and AF row is out of scope.

## What is frozen

### 1. What is held fixed, and how that is proved

Four inputs are identical for every dataset in this tranche, and the receipt publishes a
fingerprint over all four so that "held fixed" is checkable rather than asserted:

- the **possibility space** `M(S)`: the AJ4 organization set at the registered binary budget,
  four cell-free plus 256 one-cell systems, rebuilt here rather than imported;
- the **raw pricing** `R`: the four-coordinate vector
  `(state_cells, table_rows, flip_transitions, unit_outputs)`, read off the description, with
  **no scalarization** at any point;
- the **requirement** `V`: be consistent with every observed pair, then be non-dominated in
  `R`;
- the **horizon** `H`: observations are drawn from words of length at most three.

### 2. What varies, and only that

The **data** `D`: a finite set of observed `(input word, output word)` pairs.
Registered family, fixed here: five target behaviours — identity, negation, constant zero,
delay by one, running parity — crossed with four coverages — the two length-one words, all
words of length at most two, the eight length-three words, and all fourteen. Twenty datasets.

### 3. The choice map

`Chosen(D) = { m in M(S) : m agrees with every pair in D, and no other agreeing member
dominates m in R }`, where domination is `<=` on all four coordinates and `<` on at least one.
Exact integer comparison only.

### 4. The gates

`GREEN` requires: the fixed-input fingerprint identical across all twenty datasets; at least
one pair of datasets **with the same target behaviour** whose chosen sets differ, so the move is
attributable to data rather than to the requirement; at least one pair whose chosen sets are
disjoint; the choice map invariant under reordering of a dataset's pairs; monotone narrowing
under dataset extension; route A and route B agreeing on every published quantity; every
declared hostile detected with a clean control; and the no-alarm case asserted.

### 5. Falsifiers

- If every registered dataset yields the same chosen set, the data axis does not move the
  preferred form at this scope and the row is not earned.
- If chosen sets differ only across different target behaviours and never across coverages of
  one behaviour, then what moved is the requirement, not the data, and the row is not earned.
- If extending a dataset ever **adds** a member to the chosen set of consistent systems, the
  consistency filter is not monotone and the construction is wrong.
- If reordering a dataset's pairs changes the chosen set, the map is not a function of the data
  and every number here is void.
- If a randomized dataset family of the same size almost always yields one chosen set, the data
  axis is not informative and that must be published as the finding.

## Forbidden promotions

`DATA_CREATES_THE_POSSIBILITY_SPACE`, `MORE_DATA_IS_ALWAYS_BETTER`,
`DATA_AXIS_DOMINATES_REQUIREMENTS_OR_PRICING`, `UNIQUE_PREFERRED_FORM_PER_DATASET`,
`LEARNING_THEORY_DERIVED`, `COMPLETE_GMI`.

## What is not claimed novel

Version-space narrowing under consistency constraints, Pareto non-domination, Mealy machines
and the observation that a hypothesis class is prior to the data that filters it are all parent
mathematics, pinned in `PARENT_LEDGER.md`. The sibling result — that requirements and pricing
move the preferred form — is owned by the merged niche-repricing and objective-provenance
packages pinned in `MANIFEST_V1.json`, and is not re-earned here. The residual contribution is
the data axis alone, with the other three inputs held fixed and the fixing made checkable.

# Section D V4 — Developmental History as a Finite Phase Axis

Pre-outcome authority: `FREEZE_V4.md` at commit `06828d7dbf2cf86072efc3ec59db6216e5bf3bd7`.

Executable authority: `section_d_history_witness.py` -> `RESULT_V4.json`.

## Result

Every frozen prediction passes.

At the registered held-out point, the **present** obligation, relation, query ecology, verifier, memory cap, future migration law, horizon, and scalar occupied memory are identical. The only changed coordinate is the semantic installed state inherited from development:

```text
H_key:   four-cell key-oriented index is already installed
H_value: four-cell value-oriented index is already installed.
```

The future ecology contains 3 forward and 5 reverse lookups per block. Its serving costs are:

```text
key_index   3*1 + 5*4 = 23 ops/block
value_index 3*4 + 5*1 = 17 ops/block.
```

So, absent switching cost, the **current ecology favors value indexing by six operations per block**.

Nevertheless at the prospectively frozen one-block horizon:

```text
H_key:
  stay key       = verification 8 + serving 23     = 31
  migrate value  = verification 8 + migration 8 + serving 17 = 33
  unique Pareto winner = key_index

H_value:
  stay value     = verification 8 + serving 17     = 25
  migrate key    = verification 8 + migration 8 + serving 23 = 39
  unique Pareto winner = value_index.
```

Both feasible candidates retain four persistent cells. The winner therefore changes when **only inherited semantic installed state changes**, even though current scalar occupancy remains four cells in both histories.

At two blocks the six-op/block serving advantage accumulates to 12, exceeds the eight-op migration cost, and `H_key` crosses to `value_index`. `H_value` selects `value_index` at every checked horizon. This is finite hysteresis, not permanent lock-in.

## Exact switching-cost theorem

Let exact morphologies A and B have equal persistent coordinates and common verification cost. Suppose present future serving favors B by

```text
D_h = C_A(h) - C_B(h) > 0
```

over horizon `h`, and converting inherited A to B costs `K>=0` future operations.

From inherited A:

```text
L(A | H_A) = C_A(h)
L(B | H_A) = K + C_B(h).
```

Subtract:

```text
L(B | H_A) - L(A | H_A)
= K - (C_A(h)-C_B(h))
= K - D_h.
```

Therefore:

```text
D_h < K  => A uniquely wins
D_h = K  => A and B tie
D_h > K  => B uniquely wins.
```

From inherited B:

```text
L(A | H_B) - L(B | H_B)
= K + D_h > 0
```

whenever `D_h>0`; B therefore wins immediately.

The witness checks the prospectively frozen finite grid

```text
base B cost c = 1..5
advantage D    = 1..8
conversion K   = 0..12
horizon m      = 1..8
```

for `5*8*13*8 = 4160` tuples. All pass. Among inherited-A cases the exact outcome counts are:

```text
A retained : 720
tie        : 135
B selected : 3305.
```

These counts are only a finite theorem sanity check; the proof above is algebraic and parent-owned by switching-cost/amortization reasoning.

## Why this is not sunk-cost accounting

Past build cost is never charged. At the decision boundary both histories already contain a valid four-cell exact index, and each starts with identical scalar occupied memory.

Only **future work** enters the lifecycle coordinate:

- future exact verification;
- future serving;
- an actual future reindex operation if the installed semantic state is changed.

The reindex cost is not a symbolic surcharge. The witness executes both orientation transformations for every one of the 24 possible four-pair bijections. Each transformation performs four reads and four writes and produces an exact opposite-direction index, for eight future operations in every world.

The freeze supplies the same fixed four-cell transient reconfiguration workspace to all candidates. The original child-issue sketch mentioned an in-place implementation; the committed freeze deliberately replaces that implementation detail with an explicit common workspace so no unregistered peak-memory assumption is needed. The Section D Pareto vector remains the V1 contract `(persistent_cells, lifecycle_ops)`.

## Exhaustive validity

The mechanism family is tested on **all 24 bijections** between four opaque key tokens and four opaque value tokens, not only the held-out relation.

For each bijection, every mechanism is checked on all eight distinct obligations: four forward and four reverse lookups.

Thus each candidate receives 192 exact world-query checks:

```text
key_index    192/192
value_index  192/192
dual_index   192/192
pair_list    192/192.
```

`dual_index` and `pair_list` are exact but each requires eight persistent cells, so both are removed by the prospectively frozen cap of four **before** Pareto comparison.

## Negative controls

### Zero migration cost

Set `K=0` while leaving the 3-forward/5-reverse present ecology unchanged.

Observed for both inherited histories and every checked `m=1..8`:

```text
unique winner = value_index.
```

The history effect therefore disappears exactly when the registered physical mechanism that carries history dependence—future conversion cost—is removed.

### Cold start

With no installed orientation and equal build cost eight for either single index, the current serving advantage determines the choice:

```text
m=1..8 -> value_index.
```

This rejects a hidden label bonus for the historically named candidate.

### Mirrored ecology

Mirror the query mix to 5 forward / 3 reverse. The serving costs exchange:

```text
key_index   = 17
value_index = 23.
```

The phase law mirrors too:

```text
H_key:   key_index for all m=1..8
H_value: value_index at m=1, then key_index at m=2..8.
```

Thus neither orientation label is privileged.

### Opaque-token remint

Keys and values are independently renamed into disjoint lexical namespaces. Exact answers, 23-vs-17 block costs, controls, and the held-out history collision are unchanged.

### Independent exact frontier implementation

All-pairs dominance and a reverse-order incremental skyline agree on every registered history/control/horizon cell.

## What “developmental history” means here

The witness does not claim that an inaccessible narrative of past events has causal force. The physically sufficient history variable is the **semantic state left installed by prior development**.

Two systems can therefore have the same scalar present resource occupancy and face the same current environment while still differ in the cost of reaching alternative future morphologies. In this finite grammar, omitting that installed semantic state from the phase descriptor loses decision-relevant information.

That is the narrow Section D result:

```text
same present O,E,R,V and scalar occupancy
+ different inherited semantic installed state
=> different unique finite-horizon Pareto morphology.
```

## Strongest-parent subtraction

This result is not novel path-dependence theory.

- W. Brian Arthur, *Competing Technologies, Increasing Returns, and Lock-In by Historical Events* (Economic Journal 99(394), 1989, DOI `10.2307/2234208`) is a canonical parent for historical path dependence and lock-in under increasing returns.
- Stuart Russell & Eric Wefald, *Principles of Metareasoning* (Artificial Intelligence 49, 1991, DOI `10.1016/0004-3702(91)90015-C`) is a parent for selecting computational actions by resource-bounded downstream value.
- Marius Lindauer & Frank Hutter, *Warmstarting of Model-Based Algorithm Configuration* (AAAI 2018, DOI `10.1609/aaai.v32i1.11532`) directly parents the idea that previously accumulated computational state can change future configuration cost.
- Classical database indexing, switching-cost, hysteresis, installed-base, warm-start, and amortization theory own the concrete mechanism.

The GMI residual is only the **prospective cross-morphology governance protocol**: freeze semantic history as a coordinate, compare neutral exact mechanisms under common physical accounting, require a zero-cost erasure control, require a finite crossover, remint names, and keep the parent theory parent-owned.

## Box disposition

This evidence is sufficient, at the registered finite scope, for exactly:

```text
[x] Demonstrate developmental history as a phase axis.
```

It does **not** close:

- a complete or unbounded developmental-history coordinate schema;
- a complete ecology/resource coordinate schema;
- empirical or real-scale phase-boundary uncertainty;
- extrapolation outside this finite relation/query/index grammar;
- universal hysteresis, permanent lock-in, or universal morphology selection.

## Claim ceiling

```text
FINITE_EXACT_PROSPECTIVE_DEVELOPMENTAL_HISTORY_PHASE_LAW
PARENT_OWNED_SWITCHING_COST_PATH_DEPENDENCE_WARMSTART
NO_UNIVERSAL_HYSTERESIS_OR_REAL_SCALE_CLAIM
```

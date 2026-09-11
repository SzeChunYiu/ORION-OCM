# Developmental-state factorization v1

Status: **exact scaling calibration + parent subtraction.**

## Question

If a minimal exact developmental quotient can be exponentially large, why are local units / modular morphologies useful at all?

The answer can be purely **factorization/resource** rather than fundamental expressivity.

## Exact product fixture

`developmental_quotient_scaling.py` constructs `n` independent local adaptive units. Each local unit has three future-distinguishable states:

```text
0  teachable-unlearned: query -> 0; teach1 -> learned
1  stubborn-unlearned: query -> 0; teach1 -> unchanged
2  learned:             query -> 1; teach1 -> unchanged
```

Legal events address one unit at a time:

```text
query_i
teach1_i
```

Every tuple in `{0,1,2}^n` is distinguishable by some future query/teaching sequence. Therefore exact deterministic developmental minimization yields

\[
|S_{min}|=3^n.
\]

A flat transition table has

\[
2n\,3^n
\]

state-event entries.

Executed finite rows:

| n | minimal developmental states | flat transition entries |
|---:|---:|---:|
| 1 | 3 | 6 |
| 2 | 9 | 36 |
| 3 | 27 | 162 |
| 4 | 81 | 648 |
| 5 | 243 | 2430 |

Yet the natural factorized realization stores:

```text
n local state cells
one shared local state alphabet of size 3
one shared local rule table: 3 states x 2 event types = 6 entries
```

and one teaching event changes exactly one state cell.

Thus global exact developmental-state complexity is exponential while description/update locality is compact.

## Parent theory owns the generic principle

This is not a new machine-intelligence law.

Factored MDPs represent large state spaces using state variables and compact dynamic-Bayesian-network transition structure. Guestrin, Koller, Parr & Venkataraman explicitly note that factorization can give exponential reductions in representation size while exact solution can still be difficult:

- Guestrin et al., *Efficient Solution Algorithms for Factored MDPs*, JAIR 19 (2003), DOI `10.1613/jair.1000`, https://arxiv.org/abs/1106.1822
- Boutilier, Dearden & Goldszmidt, *Stochastic Dynamic Programming with Factored Representations*, Artificial Intelligence 121 (2000), DOI `10.1016/S0004-3702(00)00033-3`

Dynamic Bayesian networks, graphical models, circuits and ordinary compact programs make the same broad point: an exponentially large extensional state/function table can possess a compact intensional factorization.

Therefore:

```text
FACTORIZATION_MAKES_EXPONENTIAL_STATE_COMPACT
```

is parent-owned.

## What this says about “basic cognitive units”

The local unit in this fixture is useful because it exposes conditional independence and local update structure. It is **not** proven fundamental:

- one can merge all units into the global transducer;
- one can split a local transition into smaller primitives;
- an ordinary indexed program represents the same factorization compactly;
- a different coordinate system could expose a different factorization.

The scientifically meaningful question is therefore not:

> Is the local cell the atom of intelligence?

but:

> Which factorization makes future cognition/development cheap under a declared ecology and physical/resource model?

## Candidate factorization-quality object

For a registered morphology factorization `F`, retain a vector rather than inventing one scalar:

\[
Q_F=(D,X,U,C,S,V,P)
\]

where provisionally:

- `D` — description/storage cost of the factorization;
- `X` — execution/inference work;
- `U` — update locality/work, e.g. state/parameter fraction touched;
- `C` — communication/coupling cost between factors;
- `S` — search/learning cost to acquire the factorization itself;
- `V` — verification cost/locality;
- `P` — plasticity/retention consequences under repeated updates.

Every coordinate has mature parent literature. The tuple is an accounting surface, not a novelty claim.

## Stronger residual

Track B could still contribute if morphology structure predicts a useful factorization-quality frontier across different paradigms before outcomes.

For example, prospectively test whether independently measurable quantities such as

```text
interaction graph width / coupling
update support size
credit-assignment path length
reusable-substructure compression
verification locality
```

predict later acquisition/update burden in programmatic, probabilistic, neural and OCM systems.

The strong parent control must include each paradigm's own specialized complexity predictor.

## Important negative possibility

It may turn out that there is **no cross-paradigm factorization law substantially better than the product of family-specific parent theories**.

Then the correct conclusion is:

```text
FACTORIZATION_IS_GENERAL_BUT_NO_NEW_GMI_INVARIANT_FOUND
```

not another rebranding of graphical models/modularity.

## Terminal

```text
DEVELOPMENTAL_QUOTIENT_EXPONENTIAL__FACTORIZATION_COMPACT
FACTORED_STATE_PARENT_SUFFICIENT_FOR_GENERIC_COMPACTNESS
FACTORISATION_QUALITY_PHASE_LAW_REMAINS_OPEN
```

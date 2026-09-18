# Finite reachability-fraction theorems v1

## Definitions

Let `U=M(G0-fin-v1,(2,2))` be the 576-presentation universe of #966 and let
`U/~I` be its 21-class protected quotient for `I=((),(0,),(1,);T=6)`. The
registered start is the one-cell, one-register `HALT` presentation.

At current carrier `(n,r)`, `REWRITE` replaces one cell by an arbitrary typed
instruction in the complete `q(n,r)=1+3rn+rn^2` alphabet. `GROW_CODE` appends a
`HALT` cell and `GROW_REGISTER` declares one additional zero-initialized
register. Each law is the reflexive-transitive closure of its frozen operator
set under its carrier ceiling.

## REACH-1 — exact reachable presentation characterization

**Theorem.** For each law in the frozen registry, the reachable presentations
are exactly all well-typed presentations in its rectangular carrier ceiling:

```text
REWRITE_11        : M(1,1)
CODE_GROWTH_R1    : M(2,1)
REGISTER_GROWTH_N1: M(1,2)
JOINT_GROWTH_22   : M(2,2).
```

**Proof.** Every registered primitive preserves well-typing and its law's
ceiling, so no path can leave the displayed set. Conversely, take any target
inside a displayed set. Starting at `(1,1)`, apply the registered carrier-growth
operators until the target `(n,r)` is reached; these operations preserve
existing cells and initialize each new code cell to `HALT`. Then visit each of
the `n` table cells once and use `REWRITE` to install its target instruction.
The complete typed alphabet at `(n,r)` contains every target instruction, so
the resulting presentation is exactly the target. Thus inclusion holds in both
directions. QED.

The cardinalities follow independently from #966's finite product formula:
`5`, `126`, `14`, and `576`.

## REACH-2 — exact quotient fractions

**Theorem.** Projecting the four reachable presentation sets through the fixed
protected quotient yields respectively `4`, `18`, `4`, and `21` classes.
Therefore their exact reachable quotient fractions are `4/21`, `6/7`, `4/21`,
and `1`.

**Proof.** The primary route enumerates the finite successor graph from the
registered start and forms the image of the total protected-observation map.
The source-separated oracle instead directly constructs each product set and
executes every program using a separately written interpreter. Both routes
produce the same reachable presentation count, class count, and SHA-256 of the
complete sorted semantic-key set for each law. Since #966/#984 pins the full
denominator to exactly 21 classes, reduction of the four exact ratios gives
the stated fractions. QED.

Presentation mass is not a substitute: for example, `CODE_GROWTH_R1` reaches
`126/576=7/32` presentations but `18/21=6/7` quotient classes.

## REMINT-1 — surface-name invariance

**Theorem.** Every bijection of the five operation surface tokens preserves all
four reachable quotient fractions when decoded by its matching inverse.

**Proof.** A certified remint round-trips to the identical typed instruction
table. The successor primitives, carrier bounds, start, protected execution,
and quotient depend on typed operations rather than token spelling. Hence every
presentation's membership in each reach set and every observation key are
unchanged. Exhaustive replay checks all `5! * 576 * 4 = 276,480` membership
instances. A mismatched `INC/READ` inverse changes protected behavior and is
rejected, so the test is not vacuous. QED.

## Boundary

The registry is complete only by prospective declaration for this finite
tranche. `JOINT_GROWTH_22` reaching all 21 classes does not imply universal
reachability: changing the law, budget, grammar, interface, horizon, or start
can change both numerator and denominator. No result here quantifies over all
possible developmental/search laws, stochastic/adaptive dynamics, or
unbounded programs. #874 and #877 remain the authorities for selection from a
reachable set and deterministic finite-prefix search, respectively.

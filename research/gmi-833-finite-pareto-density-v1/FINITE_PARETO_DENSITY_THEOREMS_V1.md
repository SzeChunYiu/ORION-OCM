# Finite Pareto-density theorems v1

## Registered objects

For a program `P` in the pinned `G0-fin-v1` cumulative budget, let `o(P)` be
its complete protected observation table on `(), (0,), (1,)` at step cap 6 and
let `r(P)=(code_cells,register_cells)`. A morphology is the pair
`q(P)=(o(P),r(P))`; source syntax and presentation multiplicity are absent.

The preregistered external behavior vector is

```text
u(q) = (number of HALTED probes,
        number of nonempty probes whose complete output equals their input,
        number of probes with nonempty output).
```

All three coordinates of `u` are maximized. Both coordinates of `r` are
separately minimized. This benchmark is an evaluation prior disclosed before
the census; it is not asserted to be canonical or ecology-neutral.

For morphologies `x,y`, define `x ≻ y` exactly when every behavior coordinate
of `x` is at least the corresponding coordinate of `y`, every resource
coordinate of `x` is at most the corresponding coordinate of `y`, and at
least one of those five comparisons is strict. The frontier `PF(Q)` is the set
of elements not strictly dominated by another member of `Q`. Its registered
density is the exact rational `|PF(Q)|/|Q|`.

## PARETO-1 — finite maximality and exact density

**Theorem.** Every nonempty finite morphology set `Q` has a nonempty uniquely
determined frontier. The frontier is an antichain under `≻`, every nonfrontier
element is dominated by some frontier element, and the density is a positive
reduced rational in `(0,1]`.

**Proof.** Coordinatewise weak comparison is transitive. If `x ≻ y` and
`y ≻ z`, all five comparisons remain weak in the required orientations and a
strict comparison on either link remains strict between `x` and `z`; hence
`≻` is transitive. It is irreflexive because no coordinate is strictly better
than itself. Starting from any member of finite nonempty `Q`, repeatedly move
to a strict dominator when one exists. Irreflexivity and transitivity prevent
revisiting a point, so finiteness forces termination at a maximal point. Thus
the frontier is nonempty and every nonfrontier point lies below a frontier
point. Two frontier elements cannot dominate one another, so it is an
antichain. The definition selects exactly all maximal elements, hence the set
is unique. Finally, `1 <= |PF(Q)| <= |Q|`; reducing the integer ratio gives the
claimed exact rational. QED.

The primary implementation replays irreflexivity, every ordered triple for
transitivity, the antichain condition, and maximal coverage. A separately
written all-pairs oracle negates resource coordinates, maximizes all five
integer coordinates, and reproduces every maximal objective/resource vector.

## QUOTIENT-DENSITY-1 — multiplicity invariance and hostile

**Theorem.** If a presentation multiset changes only by adding or removing
presentations whose semantic/resource morphologies already occur, its
morphology-set frontier and density are unchanged. In contrast, the fraction
of presentations lying on the frontier is not invariant to such changes.

**Proof.** The registered estimator first takes the set image under `q`.
Changing only positive fiber multiplicities leaves that image set unchanged.
Dominance, frontier, cardinalities, and their ratio are functions of that set,
so all remain unchanged. For non-invariance of presentation weighting, take a
frontier morphology `f` strictly dominating `d`. The two-presentation density
is `1/2`. Duplicating `f` changes it to `2/3`; duplicating `d` changes it to
`1/3`. The quotient remains `{f,d}` with density `1/2` in every case. QED.

This is why the census reports presentation-weighted values only as explicitly
unregistered diagnostics.

## REMINT-PARETO-1 — certified surface-remint invariance

**Theorem.** Every certified bijective operation-token remint with its matching
inverse decoder preserves the registered morphology set, frontier, and
density.

**Proof.** By #966 DESC-1, certified remint/decode changes neither the complete
protected observation table nor the raw resource vector. Therefore `q` is
pointwise unchanged. The three behavior coordinates factor through the
observation table and the two cost coordinates are the raw resource vector, so
the objective/resource points are unchanged. Applying QUOTIENT-DENSITY-1 gives
frontier and density equality. QED.

All `5!` remints are replayed on all 576 registered `(2,2)` presentations,
for 69,120 exact morphology-point checks.

## Boundary

The theorem is finite but the measured numbers are additionally conditional on
the frozen grammar, cumulative budget, protected interface, step cap, and
external objective vector. No result here defines a universal density,
chooses a scalar winner, measures reachability, performs clustering, maps a
known family, validates an UNKNOWN class, or addresses unbounded spaces.

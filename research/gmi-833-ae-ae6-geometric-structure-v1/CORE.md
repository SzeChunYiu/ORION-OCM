# gmi-833-ae-ae6-geometric-structure-v1

Section AE6 of issue #833 asks for the phrase `data lie on a manifold` to be
replaced by a checked hierarchy, for learnable distributions that break a
smooth-manifold assumption, for low-dimensional structure that is useless for
the task, and for three derivations that say when an architecture class earns
its keep. This package does all of that on one finite ambient space, in exact
rational arithmetic, with two independent computational routes.

The ambient space is the Boolean cube `{0,1}^4` with Hamming distance, so every
geometric word here is an exact combinatorial predicate. All quantities are
`int` or `fractions.Fraction`; no float appears in any claim, receipt field,
test assertion or hostile.

## The hierarchy (row 1)

Six exact predicates on the support, evaluated on the registered 8-source
roster, with a **strictness table over all 30 ordered pairs**: **23** pairs
carry a registered witness in the first class and not the second, and the
remaining **7** are reported as not separated, each with its reason.

The sharpest row-1 result is that the frozen `union of at most 3 cosets`
predicate is almost content-free at this scope. Over **all 65519** supports of
affine dimension at least 1, exactly **65503** satisfy it and only **16** do
not — and those 16 are precisely the supports of size **15**, each with a
coordinate-permutation stabilizer of order 4, 6 or 24. Because the
non-geometric class demands a *trivial* stabilizer, **no** support can be both
algorithmic and outside the union class: five of the seven non-separations are
that one census, and one of them is proved impossible rather than merely
unwitnessed. A second non-separation is a proved containment: a block product
with at most 2 values per block has affine dimension at most **2**, over all
**100** such supports.

## A learnable distribution that is not a manifold (row 2)

`S_NONMANIFOLD_LEARNABLE` is a dimension-2 coset and a dimension-1 coset meeting
in one point. Three independent exact certificates say it is not a manifold at
this scope: the Hamming-1 degree sequence is `[1, 2, 2, 2, 3]` and so not
constant; the maximal cosets inside it have two distinct dimensions `{1, 2}`;
and the two registered pieces have different dimensions and intersect. A
2-coordinate local rule attains exact accuracy **1** on it at integer cost
**13** bits.

## Low dimension is neither statistically nor causally sufficient (row 3)

The register's own gloss — support inside a GF(2) coset of dimension 1, exact
mutual information `0` bits, exact interventional effect `0` — is met exactly by
`S_LOWDIM_USELESS`. The *added* clause of prediction `AE6-P3`, that a
full-dimension coordinate also determines the target, is **unsatisfiable**, and
that prediction is reported `REFUTED` with a machine-checked certificate: over
all **480** (support, target) pairs at dimension 1, **0** satisfy the
conjunction, and over **34112** cases at support size at most 4 the identity
`exact zero mutual information with a deterministic target iff the target is
constant` has **0** violations.

Row 3 is then closed on the repaired composite witness. Its support factorizes
exactly as a dimension-**1** GF(2) factor on block `{x0,x1}` times a
full-dimension factor on block `{x2,x3}`. The maximally low-dimensional factor
has exact mutual information **0** bits with the target and exact interventional
effect **0**, while the best rule reading that factor alone scores **1/2** — the
base rate — and a single coordinate of the full-dimension factor scores **1**
with interventional effect **1**. Dimension is therefore neither statistically
nor causally sufficient for task relevance.

## Three derivations, each with a matched failure (rows 4-6)

| row | condition | named class, integer cost | comparator at the same budget | matched failure | exact drop |
|---|---|---|---|---|---|
| locality | some 2-subset of coordinates determines the target | `M_local[2]`, 13 bits, accuracy `1` | `7/8` | conjunction of all four coordinates: `15/16` vs `1` | `1/16` |
| symmetry | source and target invariant under the registered group | `M_shared[SymN]`, 12 bits, accuracy `1` | `13/16` | a single coordinate as target: `11/16` vs `1` | `5/16` |
| compositionality | the target factorizes through the registered blocks | `M_modular`, 14 bits, accuracy `1` | `5/8` | the weight threshold: `7/8` vs `1` | `1/8` |

The symmetry cost reduction is exactly the orbit-count reduction: the unshared
class costs **23** bits with **16** orbits, the shared class **12** bits with
**5**, a saving of **11** bits and **11** orbits.

No condition is `UNFALSIFIED_CONDITION`: each one is falsified by a registered
world on which the named class is strictly worse.

One structural finding sits inside row 6. At the modular budget of 14 bits the
monolithic class holds exactly **17** functions and **every one of them is
already modular**, because a one-term description is a conjunction of literals
and a conjunction factorizes across the blocks. The monolithic comparator
therefore *provably cannot* produce the compositional matched failure; the
failure is delivered against `M_shared[SymN]`, which costs 12 bits and attains
`1` on a target no one-bit block summary pair can reach. The containment is
sharp: it breaks at one more term.

## Bounds, hostiles, null

**10** bound records, each with `range_lo` and `range_hi` derived from the
definition of the bounded quantity, a computed `vacuous` flag, a separate
`attained_by`, and a `violated_by` witness from an explicitly relaxed class.
None is vacuous and none is `UNFALSIFIED_BOUND`. The registered description code
is Kraft-compliant with exact sum `1372503309540478908673/2361183241434822606848`;
dropping the self-delimiting term-count field pushes it to
`90031258052692244737/73786976294838206464`, above 1.

**5** hostiles, each asserted potent before it is asserted detected: a rank cap
that scores a dimension-4 support as dimension 2; a dropped mass-invariance
clause that scores a non-invariant source as invariant; a leaked block split
that turns `3/4` into `1`; an inflated monolithic budget that turns `5/8` into
`1`; and a moved support point that turns cycle rank `1` into `2`.

**Null.** The row-3 detector is run on **200** randomized tasks over random
block geometry drawn by a registered integer generator. It fires on **3** of
200; all three are listed individually with their exact values and all three are
genuine instances of the same phenomenon, so the rate is a reproducibility rate,
not a false-alarm rate. It does **not** fire on the clean registered witnesses.
The magnitude is bounded above by `1 - base rate <= 1/2` by definition and the
planted witness attains that definitional maximum `1/2`, so a
strictly-exceeds-the-largest-null comparison is structurally impossible for this
quantity; that is stated rather than engineered around, and the exact firing
rate is the primary comparison.

## Scope

The claim ceiling is recorded verbatim in `MANIFEST_V1.json` and
`RESULT_V1.json`. Everything above is claimed only at the registered finite
scope: `n = 4`, the two registered blocks, the union rank cap 3, the
per-block support cap 2, the full 30-element subgroup lattice of the
coordinate-permutation group, and the registered integer description code.
Nothing here licenses an asymptotic statement, a statement about real datasets,
or any claim that a geometric property implies task relevance. The prospective
real-dataset row is **not** closed; its instrument requirement is stated in
`RESULT_V1.json` and in the reconciliation file.

## Reproduce

```bash
python3 -I -B research/gmi-833-ae-ae6-geometric-structure-v1/test_ae6_geometric_structure_v1.py -v
python3 -I -O -B research/gmi-833-ae-ae6-geometric-structure-v1/test_ae6_geometric_structure_v1.py -v
python3 -I -B research/gmi-833-ae-ae6-geometric-structure-v1/ae6_geometric_structure_v1.py
python3 -I -B research/gmi-833-ae-ae6-geometric-structure-v1/independent_geometry_oracle_v1.py
```

The executor writes `RESULT_V1.json` to stdout, byte-identical in both modes.

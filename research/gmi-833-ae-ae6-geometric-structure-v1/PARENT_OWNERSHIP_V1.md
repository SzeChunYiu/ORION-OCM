# AE6 parent ownership

Nothing in this package is claimed novel against the parent literature. This
file names the parents, says what each owns, and states the narrow residual this
tranche contributes.

## Parents

**Manifold hypothesis and intrinsic dimension.**
Tenenbaum, de Silva and Langford (2000), *Science* 290(5500):2319-2323,
doi:10.1126/science.290.5500.2319.
Roweis and Saul (2000), *Science* 290(5500):2323-2326,
doi:10.1126/science.290.5500.2323.
Fefferman, Mitter and Narayanan (2016), *Journal of the AMS* 29(4):983-1049,
doi:10.1090/jams/852.
Pope, Zhu, Abdelkader, Goldblum and Goldstein (2021), ICLR, arXiv:2104.08894.
These own the idea that data support may be concentrated near a low-dimensional
set, the algorithms that estimate it, the testability question, and the
measurement of intrinsic dimension for real image data.

**Union of manifolds and stratification.**
Vidal (2011), *IEEE Signal Processing Magazine* 28(2):52-68,
doi:10.1109/MSP.2010.939739.
Brown, Caterini, Ross, Cresswell and Loaiza-Ganem (2023), ICLR,
arXiv:2207.02862.
These own the move from one manifold to a union of pieces of possibly differing
dimension, and the argument that real supports are better described that way.

**Invariance, equivariance and weight sharing.**
LeCun, Bottou, Bengio and Haffner (1998), *Proceedings of the IEEE*
86(11):2278-2324, doi:10.1109/5.726791.
Cohen and Welling (2016), ICML, arXiv:1602.07576.
Bronstein, Bruna, Cohen and Velickovic (2021), arXiv:2104.13478.
Elesedy and Zaidi (2021), ICML, arXiv:2102.10333.
These own locality and weight sharing as design principles, the group-theoretic
generalization of them, and — in Elesedy and Zaidi — the exact statement that
orbit averaging onto the invariant subspace strictly reduces risk for an
invariant target, with the reduction equal to the norm of the predictor's
non-invariant component.

**Compositionality and depth separations.**
Poggio, Mhaskar, Rosasco, Miranda and Liao (2017), *International Journal of
Automation and Computing* 14(5):503-519, doi:10.1007/s11633-017-1054-2.
Telgarsky (2016), COLT, arXiv:1602.04485.
These own the claim that hierarchically composed targets are cheaper for
compositional models than for flat ones, and the depth separations that make it
precise.

**Boolean analysis.**
O'Donnell (2014), *Analysis of Boolean Functions*, Cambridge University Press,
doi:10.1017/CBO9781139814782.
This owns the exact combinatorial substrate: juntas, the GF(2) expansion, the
affine geometry of the cube.

## What is NOT claimed novel

- That data support can be low-dimensional, stratified, symmetric or
  compositional, and that each of those suggests a different architecture class.
- That equivariance helps when the target is invariant. Elesedy and Zaidi own
  the exact generalization benefit; the projection argument here is theirs.
- That locality and weight sharing are good design principles when the target is
  local or invariant.
- That compositional targets favour compositional models.
- Any statement about real datasets, about asymptotics, or about which structure
  class is common in practice.

## The residual

Four narrow contributions, all at the registered finite scope and all
machine-checked by two independent routes:

1. **An exhaustive count that prices the frozen union predicate.** Over all
   65519 supports of affine dimension at least 1 on `{0,1}^4`, exactly 65503
   satisfy `union of at most 3 cosets contained in the support`, and the 16 that
   do not are exactly the size-15 supports, each with a nontrivial stabilizer.
   The literature says union-of-manifolds descriptions are weak without
   regularity conditions; this gives the exact number at one scope, and turns
   one class non-separation from `unwitnessed` into `impossible`.

2. **A two-part row-3 object with an impossibility proof between the parts.**
   The conjunction of `support inside a dimension-1 coset`, `exact zero mutual
   information` and `a full-dimension coordinate determines the target` is
   unsatisfiable for two independent reasons, checked exhaustively; the repaired
   composite witness realizes every clause with the dimension-1 object taken as
   the GF(2) *factor* of the support. The prediction that asserted the
   conjunction is reported `REFUTED` rather than edited.

3. **The cost side of the symmetry statement made exact and integer.** Elesedy
   and Zaidi price the accuracy benefit of orbit averaging under the invariance
   hypothesis. The residual here is the identity `cost reduction = orbit count
   reduction = 11 bits` under a named Kraft-compliant integer code, together
   with the matched failure that prices the hypothesis being false at exactly
   `5/16` of accuracy at the same budget. Pricing the hypothesis being wrong is
   what the parent does not do.

4. **A containment certificate that disciplines the compositional comparison.**
   At the modular budget of 14 bits the monolithic branch of the registered code
   holds exactly 17 functions and every one is already modular, so that
   comparator provably cannot exhibit a compositional failure. The failure is
   therefore stated against a comparator that is not contained in the class.
   This is a statement about the registered code, not about model families in
   general, and it is the kind of check the depth-separation literature leaves
   to the reader.

## Absorption

The symmetry derivation absorbs its strongest parent rather than working around
it. Orbit averaging is implemented exactly as the restriction to functions
constant on orbits, which is the invariant-subspace projection Elesedy and Zaidi
analyse; the positive half of AE6-6 reproduces their conclusion at this scope,
and the tranche's own organ is bolted on beside it — the integer cost identity
and the matched failure. Where the parent already owns the function, the parent
is cited and not re-proved.

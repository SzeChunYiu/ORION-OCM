# From a finite ecology to scalar computation

**Constructive finite result, with an explicit affine-domain boundary.**
Read [CORE](CORE.md) for status and [ECOLOGY_LAWS](ECOLOGY_LAWS.md) for
the general orbit and resource laws. This is an additional executable bridge;
the earlier architecture selection theorem did not run this inference.

## RE-1 — infer the law before naming a mechanism

Supply a complete rational table T:{0,1}^n→Q^m. Define b=T(0) and
w_i=T(e_i)−b. Test every row against b+Σ_i w_i x_i. The test succeeds
iff T is the restriction of an affine map. If it succeeds, the extension
F:Q^n→Q^m is unique **among affine maps**: its value at0 fixes b and its
values at the coordinate basis fix every column. Conversely those values
alone do not justify extension beyond the observed domain; the complete
cube test establishes the finite obligation and nothing about unseen real
inputs without the affine premise. Two-bit parity fails this particular
compiler while remaining a perfectly realizable Boolean task.

The inferred nonzero incidence is a property of this exact task, not an
unverified locality assumption. Zero entries are set to zero in the compiled
family. Distinct nonzero entries are allowed independent values until the
inferred symmetry equations force sharing. This family contains the target;
it need not be the smallest syntactic representation of this single table.

## RE-2 — exhaustive, template-blind symmetry inference

Enumerate all n!m! pairs of coordinate permutations (p,q). Accept exactly
those with W[q(r),p(c)]=W[r,c] and b[q(r)]=b[r]. This is equivalent to
F(Px)=QF(x), by coefficient comparison. The same property holds on the
whole Boolean cube iff these coefficient equations hold, because0 and
every e_i belong to the cube. Accepted pairs form a finite group: identity,
composition and inverses preserve the same equation. Completeness follows
because each admissible coordinate permutation pair was inspected.

This covers coordinate permutation symmetries at the declared interface,
not every nonlinear, continuous or physical symmetry. In particular it
does not infer human language meaning or a deployment distribution.

The code receives the table and dimensions only. It receives no historical
architecture name, symmetry group, locality template, weight-tying pattern
or hand-picked competing implementation. The authored test-table builders
are separate from the inference routine. Their authors know existing
architectures, so this is operational template blindness, not zero knowledge.

## RE-3 — predict, compile and execute

For the accepted group, the independent predictor partitions coefficient
positions, including the constant input, into simultaneous-action orbits.
An orbit containing a forbidden entry is forced entirely to zero. Otherwise
all its entries share one free coefficient. Burnside's formula on the
invariant surviving incidence yields the dimension

    d = (1/|G|) Σ_g |Fix(g) ∩ surviving_incidence|.

Next the compiler constructs **general rational homogeneous linear
equations** for support and equivariance and uses row reduction. It contains
no convolution, neuron, attention, graph-layer or Bayesian opcode. Each
resulting basis vector has disjoint0/1 support. Scalar multiply/add
instructions implement the basis combination, including multiplication by
the constant1 for the affine offset. RE-1's coefficients instantiate a
realization of every supplied table row.

The independent group oracle checks the complete basis, including its
dimension and every generated instruction. A separate direct matrix
evaluator checks outputs and trace length. Missing basis vectors, altered
coefficients, altered programs and forged active-entry counts fail.
These are exact rational checks, not a proof-assistant formalization.

## RE-4 — full declared charges and limits

Table inference visits2^n rows and evaluates mn coefficients per row.
The symmetry search visits n!m! pairs and m(n+1) coefficient slots per pair.
Its receipt reports these visits and the actual rational arithmetic count.
Constraint construction emits one m(n+1)-entry equation per coefficient per
accepted generator, plus zero-support equations. RREF reports initial dense
matrix entries and performed scalar operations; the group oracle separately
reports generator products. Thus factorial discovery and verification are
visible, not free consequences of expressivity.

The emitted implementation with a active entries performs exactly a scalar
multiplications, a additions, a parameter reads, a input reads and m output
initializations per call. Its d independent rational coefficients quantify
linear coordinate dimension. This is neither an information-theoretic
lower bound for arbitrary real encodings nor the cheapest scalar program:
sharing intermediate sums, zero specialization and other algebraic rewrites
can improve runtime. Code/index storage and rational bit lengths are not
measured as physical bytes. The receipt is a scalar-operation accounting
contract, not a hardware energy or latency profile.

## Registered scope

[The raw registration](orbit_raw_registration.json) was committed before
execution. Four authored finite tasks predict dimensions3,2,8,1. The
[obligation registration](orbit_registration.json) separately tests seven
supplied-action cases, including four parameter/action holdouts and one
noninvariant support case. None is a held-out historical architecture family.

The independent risk check averages exact rational losses over noise uniform
on the positive/negative coordinate axes. Its covariance is I/D, so the
projection risk identity applies without stochastic measurement. The result
is an algebraic witness for the law; it is not a neural training experiment.

## Inherited mechanism

Parameter sharing from discrete group actions is established prior work:
[Ravanbakhsh, Schneider and Póczos, ICML2017](https://proceedings.mlr.press/v70/ravanbakhsh17a/ravanbakhsh17a.pdf).
The present finite compiler applies coefficient equality and independent
group enumeration to explicit GMI obligations. The table inference should
not be confused with learning equivariance from noisy samples, studied by
[Yeh et al., AISTATS2022](https://proceedings.mlr.press/v151/yeh22b/yeh22b.pdf).
This unit claims a tested integration and explicit scope, not invention of
equivariance or a new intelligence family.

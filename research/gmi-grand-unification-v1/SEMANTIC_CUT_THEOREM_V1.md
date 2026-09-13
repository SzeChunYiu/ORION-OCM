# Grand GMI Semantic Cut Theorem V1

Status: **EXACT THEOREM AT FINITE ONE-WAY CUT SCOPE; STOCHASTIC DATA-PROCESSING EXTENSION EXACT**  
Date: 2026-09-12  
Parent main: `1292e35dc6d1050602bc4af14eba6dbb2bde8ddf`

## 0. Target

The channel atlas currently contains CL-1 ... CL-7 as separate capability laws. A grand theory should not leave them as unrelated formulas. The invariant object is the obligation induced at an arbitrary causal cut.

A cut separates an upstream part of a physical/intelligent process from a downstream part. The downstream part may also possess side information. The cut may be temporal (memory), spatial (communication), developmental (weights from training to deployment), inter-agent, inter-generational, or between an external store and a controller.

The theorem below is architecture-free. It says exactly how many distinguishable cut symbols are necessary for an arbitrary finite set-valued obligation.

## 1. Exact finite cut problem

Let

- `X` be the finite set of upstream semantic possibilities at cut `C`;
- `Y` be finite downstream side information;
- `A` be finite downstream actions;
- `X_y subseteq X` be possibilities compatible with downstream side information `y`;
- `Gamma(x,y) subseteq A`, nonempty, be the actions satisfying the obligation for `(x,y)`.

A zero-error one-way cut protocol is

`c : X -> Z`, `d : Z x Y -> A`

such that `d(c(x),y) in Gamma(x,y)` for every compatible `(x,y)`.

No probability distribution over ecologies is required.

## 2. Semantic conflict hypergraph

Define the cut hypergraph `H_C=(X,E_C)` by declaring a finite set `B subseteq X` to be a hyperedge whenever there is some `y` such that

1. `B subseteq X_y`, and
2. `intersection_{x in B} Gamma(x,y) = emptyset`.

It is enough to retain inclusion-minimal hyperedges, but the theorem is unchanged if every infeasible set is included.

A coloring of a hypergraph is valid when no hyperedge is monochromatic. Let `chi(H_C)` be its chromatic number.

## 3. Theorem — exact semantic cut cardinality

**Theorem SC-1.** The minimum number of cut symbols in any zero-error one-way protocol is exactly

`|Z|_min = chi(H_C)`.

Therefore the minimum fixed-length binary cut width is

`b_C^0 = ceil(log2 chi(H_C))`.

### Proof

Necessity. Suppose `c` is a valid protocol. If a hyperedge `B` were monochromatic with color `z`, then for its witnessing side information `y`, the decoder would have to choose one action `d(z,y)` lying in every `Gamma(x,y)` for `x in B`. Their intersection is empty, contradiction. Hence `c` is a valid hypergraph coloring and `|Z| >= chi(H_C)`.

Sufficiency. Let `c` be any valid coloring with `chi(H_C)` colors. Fix a color `z` and side information `y`, and let `B_{z,y}={x in X_y : c(x)=z}`. If `intersection_{x in B_{z,y}} Gamma(x,y)` were empty, then `B_{z,y}` would itself contain an infeasible hyperedge and would be monochromatic, contradicting validity. Thus the intersection is nonempty. Pick any action in it and define `d(z,y)` to be that action. This gives a zero-error protocol. QED.

## 4. Why a hypergraph is necessary

Pairwise conflict is not sufficient for general obligations.

Let `A={0,1,2}` and three upstream possibilities have acceptable action sets

`{0,1}`, `{1,2}`, `{0,2}`.

Every pair has a common acceptable action, so the pairwise conflict graph has no edge and chromatic number 1. But the intersection of all three sets is empty, so one cut symbol is impossible. The semantic conflict hypergraph has a single 3-vertex hyperedge and chromatic number 2, which is exact.

The committed checker verifies this counterexample.

This is the same structural reason that GMI control compatibility is generally a closed-cover/hypergraph problem rather than an ordinary quotient relation.

## 5. Graph specializations

If every inclusion-minimal infeasible set has cardinality two, the hypergraph reduces to a graph and SC-1 becomes an ordinary coloring theorem.

For an exact function obligation `a=f(x,y)`, two upstream states conflict exactly when there exists a compatible `y` for which their required outputs differ. This is the characteristic/confusability graph used in zero-error functional source coding with side information.

Thus Witsenhausen-style zero-error side-information bounds are a special case of SC-1, not a separate GMI primitive.

## 6. Stochastic/lossy cut theorem and the common decoder

**Correction, 2026-09-13:** the earlier version combined separately optimized
ecology risks into an allegedly attainable profile. That lower envelope need
not be jointly attainable. SC-1 and the single-ecology SC-2 remain valid; the
multi-ecology spectrum is corrected below. See `COMMON_DECODER_CORRECTION_V1.md`.

Let `E,X,Y,Z,A` be nonempty finite sets, `mu_e(x,y)` a probability law inside
ecology `e`, `K(z|x)` a stochastic cut channel, and `ell_e(a;x,y)` a bounded
loss. The declared joint law is `p_e(x,y,z)=mu_e(x,y)K(z|x)`.
A **single** decoder `d(a|z,y)` is used in all ecologies; it cannot condition on
an unobserved `e`. Its risk vector has coordinates

`R_e(K,d) = sum_{x,y,z,a} mu_e(x,y) K(z|x) d(a|z,y) ell_e(a;x,y)`.

**Theorem SC-2 (fixed ecology).** When optimizing one ecology coordinate with
all decoder kernels allowed, an optimal decoder can be chosen deterministic.
Write `L_e(z,y,a)=sum_x mu_e(x,y)K(z|x)ell_e(a;x,y)`. Then

`R_e^*(K)=min_d R_e(K,d)=sum_{z,y} min_a L_e(z,y,a)`.

Proof: each decoder row is a probability vector, so each row's linear loss is
minimized at an action attaining its smallest coefficient. Summing these
independent minima proves the formula. This unnormalized formula also covers
zero-probability cells without undefined conditional expectations. QED.

The vector `b(K)=(R_e^*(K))_e` is an **oracle lower envelope**, not generally a
machine's response profile. It optimizes `d` separately for each `e`.

**Theorem SC-3 (attainable risk set).** For the full randomized common-decoder
class define `Rset(K)={ (R_e(K,d))_e : d(a|z,y) is one decoder }`.
It is the convex hull of the risk vectors of deterministic common decoders,
hence a compact polytope. For deterministic-only or resource-restricted
decoders use the actual registered set instead of its convex hull.

Proof: the decoder set is a finite product of probability simplexes; its
vertices are deterministic tables. The risk map is linear. More explicitly,
give table `f:Z x Y -> A` weight `w_f=product_{z,y}d(f(z,y)|z,y)`.
These nonnegative weights sum to one and reconstruct every decoder row and
therefore its entire risk vector. Conversely any mixture of deterministic
tables defines an allowed decoder with the corresponding risk vector. QED.

**Theorem SC-4 (when the oracle envelope is attainable).** For the full decoder
class, `b(K) in Rset(K)` iff, for every `(z,y)`,

`intersection_{e in E} argmin_a L_e(z,y,a)`

is nonempty. An ecology with zero cell probability has every action in its
argmin and imposes no restriction. When the intersections exist a
deterministic common decoder attains the envelope.

Proof: subtract each cell minimum from its action losses. Every residual is
nonnegative. Equality of an ecology's total risk to its optimum forces every
positive-probability decoder action to minimize that ecology's coefficient
in every cell. A decoder attaining all minima therefore has support in each
stated intersection. Conversely choose one action from each intersection. QED.

**Hostile witness.** Let `X,Y,Z` be singletons, `E=A={0,1}`, and loss be
`1[a != e]`. The oracle envelope is `(0,0)`. Common deterministic profiles are
`(0,1)` and `(1,0)`; randomized profiles are `(p,1-p)`, `0<=p<=1`.
No decoder attains `(0,0)`. The randomized robust optimum is `1/2`, whereas
the deterministic robust optimum is `1`. This is the erased-signal viability
counterexample of GG31's accompanying witness, now applied to the cut spectrum.

No prior over ecologies is introduced: `mu_e` remains within-ecology
stochasticity, and the risk vector retains all ecology coordinates.

## 7. Data processing preserves jointly attainable risks

Suppose `K_2(z2|x)=sum_z1 K_1(z1|x)G(z2|z1)` with the **same** stochastic
garbling `G` in every ecology and the same side-information joint law above.
For each common decoder `d2`, define

`d1(a|z1,y)=sum_z2 G(z2|z1)d2(a|z2,y)`.

**Theorem SC-5 (common-decoder emulation).** If the registered decoder class
under `K_1` permits this composed kernel for every allowed `d2`, then

`R_e(K_1,d1)=R_e(K_2,d2)` simultaneously for every `e`.

Consequently `Rset(K_2) subseteq Rset(K_1)` for the full randomized classes.
Any declared scalar criterion on these risk vectors, including worst-case
risk, has an infimum under `K_1` no larger than under `K_2`.

Proof: substitute the expression for `d1` into the finite sum defining risk
and interchange the `z1,z2` sums. The coefficient of `d2(a|z2,y)` becomes
`K_2(z2|x)`. The same `d1` proves equality in all coordinates. QED.

The pointwise Bayes inequality `R_e^*(K_1)<=R_e^*(K_2)` follows and remains
valid. It does not assert simultaneous attainability of those minima.
With deterministic-only decoders, a stochastic garbling may require forbidden
randomness: risk-set inclusion is then not automatic. Deterministic garbling
preserves deterministic decoders. A marginal channel comparison also does not
permit changing its correlation with side information unnoticed.

This is Blackwell's emulation argument applied to a jointly attainable risk
set. It is a **risk** statement: simulating `G`, realizing the better channel,
or randomizing can consume resources. Resource-frontier dominance requires a
separate lawful resource transport/inequality, not just the risk identity.

## 8. Semantic cut spectrum

For each physical cut `C`, register jointly lawful channel/decoder pairs
`(K,d)` and a resource vector `rho_C(K,d)` containing every channel, decoding,
randomization and simulation cost assigned to this region. The stochastic
cut spectrum is

`Kappa_G(C) = Pareto{ ( (R_e(K,d))_e, rho_C(K,d) ) : (K,d) admissible }`.

The underlying attainable set remains primary: an arbitrary noncompact
channel/resource class can have an empty Pareto frontier despite containing
legal pairs. Frontier existence is a separate attainment obligation (GG49/50).

If tolerance `epsilon` is supplied, first restrict pairs to the registered
risk constraint, for example `R_e(K,d)<=epsilon_e` for every ecology, and
then take their resource frontier. Any costs assigned to another region must
remain in the full-system resource profile and must not be counted twice.
An oracle envelope may bound this spectrum from outside; it cannot replace
an attainable profile unless SC-4 (or another joint realization proof) applies.

At exact zero-error finite deterministic one-way scope, the cardinality
coordinate still contains SC-1: `min log2|Z|=log2 chi(H_C)`, up to fixed-length
rounding. Common zero-error action compatibility is already built into SC-1.
Memory, communication, development-to-deployment information and retrieval
are scoped projections/compositions of this corrected spectrum.

## 9. Recovery of the current channel atlas

The seven registered laws are specializations of the cut theorem plus their physical/channel constraints:

| atlas law | cut-theorem specialization |
|---|---|
| CL-1 development | source uncertainty left unresolved by the development cut |
| CL-2 query hint | downstream side information reduces posterior/conflict classes |
| CL-3 noisy development | garbled cut; SC-2 and data processing with repeated BSC observations |
| CL-4 bounded state | cut alphabet/resource constrained; optimized encoding becomes finite rate-distortion/covering |
| CL-5 public structure | source support/semantic classes shrink before the cut |
| CL-6 verifier search | downstream action becomes a proposal set plus exact verification effect |
| CL-7 external store | additional downstream side-information cut |

RV-377-135 ... 138 are compositions of the same cut operations rather than new primitives.

The atlas' exact formulas remain the quantitative corollaries for its frozen world family. This theorem supplies the common reason they exist.

## 10. Parent subtraction

The theorem is a GMI synthesis/specialization, not a claim that hypergraph coloring, functional compression, or Blackwell informativeness were invented here. Direct parents include Witsenhausen zero-error side information, characteristic-graph/conditional-graph-entropy functional compression, Blackwell comparison of experiments, and classical compatible-cover theory for incompletely specified machines.

GMI's residual contribution is the architecture-neutral binding of these tools to an obligation-relative causal cut, the use of hypergraphs for genuinely set-valued obligations, the pointwise ecology profile, and the integration of all cuts into morphology/resource prediction.

## 11. Executable hostile check

`grand_gmi_checks_v1.py` exhausts 117,649 finite set-valued task families with `|X|=3, |Y|=2, |A|=3` and independently computes (i) minimum protocol message count and (ii) semantic-hypergraph chromatic number. Every family agrees. It also freezes the graph-only three-way counterexample and exact stochastic garbling checks.

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

## 6. Stochastic/lossy cut theorem

For a fixed ecology coordinate `e`, let `mu_e(x,y)` be its within-ecology source law, `K(z|x)` a stochastic cut channel, and `ell_e(a;x,y)` a bounded loss. Define

`p_e(x,y,z)=mu_e(x,y) K(z|x)`.

**Theorem SC-2.** For linear expected loss, the optimal decoder after `K` is deterministic at each `(z,y)` and the exact Bayes risk is

`R_e^*(K) = sum_{z,y} p_e(z,y) min_a E_e[ell_e(a;X,y) | z,y]`.

This is not a prior over ecologies. `mu_e` is stochasticity inside one declared ecology coordinate. Across an ecology set `E`, GMI keeps the pointwise risk profile

`R(K) = (R_e^*(K))_{e in E}`.

## 7. Data-processing theorem

If `K_2 = G o K_1` for any downstream garbling channel `G`, then

`R_e^*(K_1) <= R_e^*(K_2)`

for every ecology coordinate `e` and every declared loss problem.

Proof: after observing `K_1`, the downstream process can simulate `G` and then run the optimal `K_2` decoder. Therefore `K_1` can imitate every strategy available after `K_2`; optimizing cannot be worse. QED.

This is the cut form of Blackwell/data-processing monotonicity. Because the inequality holds coordinatewise, no distribution over the ecology set is needed.

## 8. Semantic cut spectrum

A grand GMI problem does not have one information number. It has a family indexed by physical/causal cuts and tolerance:

`Kappa_G(C,epsilon) = Pareto{ (R(K), rho_cut(K)) : K physically/admissibly crosses C }`.

At exact zero-error finite scope, the cardinality coordinate contains SC-1 as

`min log2|Z| = log2 chi(H_C)`

(up to fixed-length integer rounding).

Different familiar quantities are projections/specializations of this spectrum: memory capacity, communication bandwidth, training-to-deployment information, retrieval bandwidth, inter-agent messages, and genomic/inter-generational information.

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

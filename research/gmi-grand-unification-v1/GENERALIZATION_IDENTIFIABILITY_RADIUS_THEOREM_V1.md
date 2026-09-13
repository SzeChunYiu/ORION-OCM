# Grand GMI Generalization Identifiability Radius Theorem V1

Status: **INFIMUM IDENTITY + ATTAINMENT-AWARE PREDICTION GATE + EXACT WITNESSES**
Date: 2026-09-13

## 0. Generalization is an identifiability problem before it is an architecture problem

Let `E` be a nonempty admitted ecology/world class and `Y` a nonempty output space with nonnegative declared loss. A frozen training/probe process exposes an observation signature

\[
D:E\to\mathcal D.
\]

The protected held-out obligation asks for a target response

\[
T:E\to\mathcal Y,
\]

where `Y` carries a declared loss/distance `d_Y`.

The information-theoretic predictor class consists of all set-theoretic mappings

\[
g:\mathcal D\to\mathcal Y.
\]

Existence in this unrestricted class does not establish measurability, continuity, computability, or physical/developmental realizability. Those restrictions require their own selector or realization theorem. Fiberwise choices below use the usual axiom of choice when there are infinitely many fibers.

Grand GMI asks first what is identifiable from `(E,D,T)` before discussing neural, symbolic, retrieval, program or other realizations.

---

## 1. Observation fibers

For an observed signature `z`, define the compatible ecology fiber

\[
F_z=\{e\in E:D(e)=z\}.
\]

Every machine receiving only `z` must emit the same prediction for every world in `F_z`. Therefore the target values inside one fiber are the irreducible ambiguity left by the declared training/probe process.

Define the fiber radius

\[
r(z)=\inf_{y\in\mathcal Y}\sup_{e\in F_z}d_Y(y,T(e)).
\]

and the global generalization radius

\[
\boxed{R_{gen}(E,D,T)=\sup_{z\in D(E)}r(z).}
\]

If the output space `Y` is finite, the infimum is a minimum. Finiteness of the world or observation space alone does not imply attainment. Radii are interpreted in `[0,+infinity]`.

---

## 2. Minimax generalization theorem

**GIR-1 — Generalization Radius Theorem.**

\[
\boxed{
\inf_{g:\mathcal D\to\mathcal Y}
\sup_{e\in E}d_Y(g(D(e)),T(e))
=
R_{gen}(E,D,T).
}
\]

**Proof.** Any predictor chooses one output `g(z)` independently for each observation fiber. Its worst-case error on fiber `F_z` is at least `r(z)`, so its global error is at least `R_gen`. If `R_gen=+infinity`, this already proves the identity. Otherwise fix one `eta>0`, uniformly across all fibers, and choose `g_eta(z)` with fiber error less than `r(z)+eta`. The assembled predictor has global error at most `R_gen+eta`. Taking the infimum over predictors and then letting `eta` decrease to zero proves the value identity. QED.

The last step proves equality of infima; it does not construct a predictor with error exactly `R_gen`. If every fiber radius is attained, choosing those centers does attain `R_gen`. Section 7 gives the exact feasibility criterion, which can hold even when some smaller fiber radii are not attained.

No probability distribution over worlds is required.

---

## 3. Exact extrapolation criterion

If `d_Y` is a metric and predictions live in the same target space, `r(z)=0` exactly when `T` is constant on `F_z`.

Therefore:

**GIR-2 — Exact Generalization Identifiability Theorem.** Exact protected extrapolation from `D` is possible for every admitted world iff

\[
\boxed{
D(e)=D(e')\implies T(e)=T(e')
\quad\forall e,e'\in E.
}
\]

Equivalently, target response factors through the observation signature:

\[
\boxed{T=g\circ D}
\]

for some `g`.

This is the finite/deterministic form of the principle that a held-out distinction cannot be inferred unless the declared ecology plus observations make it identifiable.

---

## 4. No-free-extrapolation corollary

Suppose two admitted worlds satisfy

\[
D(e)=D(e')
\]

but require different protected held-out responses.

Then no learner—neural, symbolic, Bayesian, programmatic or otherwise—can be correct on both worlds using only the declared observation boundary.

More generally, if

\[
d_Y(T(e),T(e'))>2\varepsilon,
\]

then by the triangle inequality no single prediction can lie within `epsilon` of both targets. Hence any `epsilon`-accurate learner requires additional ecology restriction, observation, side information or assumption.

**GIR-3 — No-Free-Extrapolation Boundary.** Architecture cannot repair target non-identifiability at the declared information boundary.

This is stronger and more local than an average No-Free-Lunch claim: it gives a direct counterexample inside one declared ecology whenever a target-distinct pair remains observation-equivalent.

---

## 5. Structure and additional data shrink the radius

### Ecology restriction

If `E' subseteq E`, every compatible fiber only loses worlds. Thus

\[
\boxed{R_{gen}(E',D,T)\le R_{gen}(E,D,T).}
\]

### Observation refinement

Suppose `D_2` refines `D_1`: there exists `h` with

\[
D_1=h\circ D_2.
\]

Every `D_2` fiber is contained in a `D_1` fiber, so

\[
\boxed{R_{gen}(E,D_2,T)\le R_{gen}(E,D_1,T).}
\]

**GIR-4 — Generalization Monotonicity.** More valid structural constraints on the admitted ecology or more informative protected observations can only improve the minimax identifiability radius.

This gives precise meaning to an inductive bias without requiring a probability prior: symmetry, smoothness, compositional grammar, causal structure, conservation laws and other assumptions help exactly insofar as they remove target-disagreeing worlds from observation fibers.

---

## 6. Structural assumptions are scientific declarations, not free information

Grand GMI therefore separates three objects:

1. **observed evidence** `D(e)`;
2. **admitted ecology/model class** `E`;
3. **realization/search bias** used to find a predictor inside the resulting constraints.

Restricting `E` can make extrapolation possible, but that restriction is a substantive assumption about the world. It must be declared, justified and exposed to falsification. Calling the same restriction a network architecture, regularizer, kernel, prior, grammar or physical symmetry does not make it assumption-free.

**GIR-5 — Inductive-Structure Typing.** Every successful extrapolation beyond observed distinctions is licensed by some declared constraint that reduces the compatible target fiber, whether that constraint is explicit in the ecology or implicit in the development/realization class.

The theorem does not say every such constraint is arbitrary. Physical law and experimentally established structure can supply justified restrictions. It says they cannot be omitted from the accounting.

---

## 7. Prospective novelty criterion

For a proposed held-out domain or behavior, freeze before observation:

- admitted ecology `E`;
- protected evidence/probes `D`;
- target `T`;
- tolerance `epsilon`.

For finite `epsilon>=0`, define the set of feasible predictions on each fiber:

\[
A_\varepsilon(z)
=\left\{y\in\mathcal Y:\sup_{e\in F_z}d_Y(y,T(e))\le\varepsilon\right\}.
\]

For a metric this is the intersection, inside `Y`, of the closed `epsilon`-balls around all compatible targets. A predictor with error at most `epsilon` exists in the unrestricted class **iff** `A_epsilon(z)` is nonempty for every `z in D(E)`. Necessity follows by evaluating that predictor on each fiber; sufficiency follows by choosing a point from each feasible set.

Compute or bound `R_gen`, while retaining the distinction between a value and a feasible prediction:

- If `R_gen < epsilon`, the uniform-slack argument in GIR-1 supplies a predictor satisfying the tolerance.
- If `R_gen = epsilon`, the radius alone does not decide feasibility. Prove that every `A_epsilon(z)` is nonempty; attainment of every fiber radius is one sufficient condition.
- If `R_gen > epsilon`, no predictor can satisfy the all-world obligation at this frozen boundary. Additional structure or information, or a changed declared risk criterion, is required. A prior alone does not change the same worst-case obligation over `E`.

A certified upper bound strictly below `epsilon` suffices; an upper bound equal to `epsilon` needs the same feasibility evidence. A lower bound above `epsilon` rules out feasibility, but a lower bound below `epsilon` does not license a prediction. For a prediction conditional on one observed signature `z`, apply the criterion only to that fiber. For any particular proposed output, check its membership in `A_epsilon(z)`; existence of some adequate output does not certify every output.

**GIR-6 — Prospective Prediction Gate.** A frozen all-world prediction is licensed at tolerance `epsilon` exactly when feasible centers exist on every relevant observation fiber, with a selector in the registered predictor class. For the unrestricted set-theoretic class, this is exactly the nonempty-feasible-set criterion above. Restricted measurable, computable or physical classes need additional evidence that their selector is available.

### Attainment sufficient conditions

For a nonempty compact metric output space `Y`, the fiber objective `y -> sup_e d_Y(y,T(e))` is lower semicontinuous and attains its minimum. The same conclusion holds for a general loss when its fiber objective is lower semicontinuous on a nonempty compact output space and has a finite value somewhere. Compactness establishes fiberwise centers; it does not automatically supply a measurable selector as the observation varies.

### Exact boundary counterexample

Let `E={e_-,e_+}`, let both worlds have the same observation, take `Y=R minus {0}` with absolute distance, and let their targets be `-1,+1`. Every legal prediction satisfies

\[
\max\{|y+1|,|y-1|\}=1+|y|>1,
\qquad
\inf_{y\ne0}(1+|y|)=1.
\]

Thus `R_gen=epsilon=1` but `A_1(z)` is empty. The sequence `y_n=1/n` approaches the value and never attains it. At every strictly larger tolerance, a sufficiently small nonzero output is feasible. Restoring the missing point `0`, for example by using the compact output interval `[-1,1]`, makes the boundary feasible.

Fiberwise optimality is sufficient but stronger than necessary: keep `Y=R minus {0}` and use two fibers with target sets `{-1,+1}` and `{-1,+3}`. Their radii are `1` (unattained) and `2` (attained at `1`). Outputs `1/2` and `1` have global error `2=R_gen`, despite nonattainment on the first fiber.

This creates a hard guard against retrospectively explaining an unseen machine/domain after its outcome is already known.

---

## 8. Relation to known GMI layers

The radius theorem connects existing objects:

\[
\boxed{
\text{ecology + evidence}
\to
\text{compatible world fiber}
\to
R_{gen}
\to
\text{required extra information/structure}
\to
(\eta_\Omega,\kappa,\tau,\rho)
\to
\text{realization morphology}.
}
\]

Examples:

- compositional language reduces held-out radius by factorizing unseen combinations into observed block values;
- symmetry reduces radius by identifying transformed cases under a declared invariant ecology;
- causal constraints remove worlds that fit observations but disagree interventionally;
- retrieval adds evidence and refines fibers;
- active experimentation selects probes specifically to reduce the relevant fiber;
- neural feature learning is one development mechanism that may discover a useful restriction/representation, but neurality alone supplies no universal extrapolation guarantee.

---

## 9. Exhaustive finite microscope

`grand_gmi_generalization_radius_checks_v1.py` uses:

- four admitted worlds;
- every binary observation map `D:E->{0,1}`: **16** maps;
- every ternary target map `T:E->{0,1,2}`: **81** maps;
- absolute-error target metric;
- every predictor from the used observation symbols to `{0,1,2}`.

Across all **1,296** `(D,T)` problems:

- direct exhaustive predictor search equals the fiber-radius theorem in **1,296/1,296** cases;
- **132** cases have radius `0` and therefore exact identifiable generalization;
- **1,164** cases have minimax radius `1`.

Observation-refinement assault:

- every binary coarse observation map crossed with every ternary fine map that truly refines it gives **462** refinement pairs;
- crossed with all 81 target maps: **37,422** exact refinement/target cases;
- `R_gen(fine) <= R_gen(coarse)` in **37,422/37,422** cases;
- strict improvement occurs in **6,120** cases.

Aggregate terminal:

`GRAND_GMI_GENERALIZATION_RADIUS_TRANCHE_ALL_GREEN`.

---

## 10. Parent subtraction

Statistical learning theory, version spaces, identifiability, minimax prediction and No-Free-Lunch results are established parent theory. Wolpert/Schaffer-style results emphasize that unrestricted data-only induction does not privilege one learner without assumptions; standard learning theory makes learnability depend on a restricted function/model class.

Grand GMI does not claim those facts as inventions.

The residual contribution is the architecture-free placement of held-out prediction inside the same semantic/process/resource stack used for control, planning and morphology:

\[
\text{protected obligation response}
\to
\text{observation fibers}
\to
\text{exact minimax target radius}
\to
\text{licensed prediction or explicit non-identifiability}.
\]

This also supplies an operational preregistration criterion for genuinely prospective Grand-GMI predictions.

The infimum/attainment distinction is standard optimization theory; see Boyd and Vandenberghe, [*Convex Optimization*, section 4.1.1](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf). Measurable policy selection is a separate obligation, as illustrated by Yu and Bertsekas, [*A Mixed Value and Policy Iteration Method for Stochastic Control with Universally Measurable Policies*](https://arxiv.org/abs/1308.3814). The correction here applies these existing boundaries to GIR-1 and GIR-6; it claims no new parent theorem.

---

## 11. Scope and falsifiers

The theorem is an inf-sup identity for the unrestricted predictor class under the nonempty-space and nonnegative-loss assumptions above. The original microscope is finite and deterministic. `grand_gmi_generalization_attainment_checks_v1.py` adds exact rational witnesses for finite target sets in a real output space with finitely many points removed; these boundary witnesses do not prove an arbitrary measurable-selection theorem. Stochastic observations require a separately declared risk criterion and measurable/statistical typing.

Direct falsifiers:

1. a finite `(D,T)` problem where exhaustive minimax prediction differs from the fiber radius;
2. a target-distinct pair with identical evidence for which an exact predictor is correct on both without extra information;
3. an observation refinement or ecology restriction that increases the minimax radius;
4. a prospective prediction licensed when a required feasible-center set is empty, including an unattained `R_gen=epsilon` boundary;
5. promotion of set-theoretic existence to a restricted predictor class without the required selector/realization evidence;
6. a mismatch in the frozen exact receipts.

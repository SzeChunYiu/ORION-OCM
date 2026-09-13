# Grand GMI Generalization Identifiability Radius Theorem V1

Status: **THEOREM + EXHAUSTIVE FINITE WITNESSES**  
Date: 2026-09-12

## 0. Generalization is an identifiability problem before it is an architecture problem

Let `E` be the admitted ecology/world class. A frozen training/probe process exposes an observation signature

\[
D:E\to\mathcal D.
\]

The protected held-out obligation asks for a target response

\[
T:E\to\mathcal Y,
\]

where `Y` carries a declared loss/distance `d_Y`.

A learner or machine may implement any mapping

\[
g:\mathcal D\to\mathcal Y.
\]

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

In finite spaces the infimum is a minimum.

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

**Proof.** Any predictor chooses one output `g(z)` independently for each observation fiber. Its worst-case error on fiber `F_z` is at least the smallest possible radius `r(z)`. Hence global error is at least `sup_z r(z)`. Conversely, choose on each fiber a center attaining `r(z)` (or an arbitrarily close center if only the infimum exists). Combining those fiberwise choices defines a predictor achieving the supremum of the fiber radii. QED.

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

Compute or bound `R_gen`.

- If `R_gen <= epsilon`, the target is identified to the declared tolerance by the theory/evidence package; a prospective prediction is licensed without choosing a probability prior over the remaining worlds.
- If `R_gen > epsilon`, a specific prediction requires additional declared structure, information or prior; the current package does not identify it.

**GIR-6 — Prospective Prediction Gate.** Grand GMI should call a held-out prediction theory-determined only when the compatible ecology fiber has sufficiently small target radius at the time of freeze.

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

---

## 11. Scope and falsifiers

The theorem is general as an inf-sup identity whenever fiber centers are interpreted with infima; the frozen microscope is finite and deterministic. Stochastic observations can be handled by replacing the deterministic signature with an information experiment and a declared risk criterion, but require separate measurable/statistical typing.

Direct falsifiers:

1. a finite `(D,T)` problem where exhaustive minimax prediction differs from the fiber radius;
2. a target-distinct pair with identical evidence for which an exact predictor is correct on both without extra information;
3. an observation refinement or ecology restriction that increases the minimax radius;
4. a prospective prediction claimed theory-determined despite frozen `R_gen>epsilon` and no added assumption/information;
5. a mismatch in the frozen exact receipt.
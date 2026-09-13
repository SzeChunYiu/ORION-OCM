# Grand GMI Robust Decision Precision Theorem V1

Status: **THEOREM + SHARP EXACT FINITE WITNESSES**  
Date: 2026-09-12

## 0. The missing quantitative link

Approximate semantic geometry says how response distinctions change with tolerance. It does not by itself say **how accurately values/losses must be represented before a decision is guaranteed adequate**.

This tranche supplies that link without placing a probability prior over the ecology.

Let `E` be an admitted ecology set, `A` a finite action set and

\[
L_e(a)\in\mathbb R
\]

be the loss of action `a` in environment `e`. Define the robust action score

\[
R(a)=\sup_{e\in E}L_e(a),
\qquad
R^*=\min_a R(a).
\]

Let an approximate machine carry estimated losses `Lhat` with certified uniform error

\[
\boxed{\sup_{e,a}|\widehat L_e(a)-L_e(a)|\le\delta.}
\]

No distribution over `E` is used.

---

## 1. Robust-score Lipschitz theorem

For every action,

\[
R(a)-\delta\le \widehat R(a)\le R(a)+\delta,
\qquad
\widehat R(a)=\sup_e\widehat L_e(a).
\]

Therefore

\[
\boxed{|\widehat R(a)-R(a)|\le\delta.}
\]

**RDP-1 — Robust Score Stability.** The max-over-ecology robust score is 1-Lipschitz under coordinatewise sup-norm perturbation of the loss field.

The statement extends unchanged from finite `E` to any ecology on which the two suprema are well-defined and the same uniform error bound holds.

---

## 2. Approximate robust decision theorem

Let

\[
\hat a\in\arg\min_a \widehat R(a),
\qquad
a^*\in\arg\min_a R(a).
\]

Then

\[
R(\hat a)
\le \widehat R(\hat a)+\delta
\le \widehat R(a^*)+\delta
\le R(a^*)+2\delta.
\]

Hence

\[
\boxed{R(\hat a)-R^*\le2\delta.}
\]

**RDP-2 — Prior-Free Decision Precision Theorem.** Any minimizer of a uniformly `delta`-accurate robust loss field is guaranteed to be `2 delta`-optimal in true worst-case loss.

This is a pointwise/worst-case statement. Probability enters only if a separate observation model is used to certify the error bound.

---

## 3. Exact action-stability margin

Assume the true robust optimum is unique and define its robust margin

\[
\Delta
=
\min_{a\ne a^*}\left[R(a)-R(a^*)\right] >0.
\]

For any competitor `a`,

\[
\widehat R(a)-\widehat R(a^*)
\ge \Delta-2\delta.
\]

Therefore:

**RDP-3 — Exact Decision Stability.** If

\[
\boxed{\Delta>2\delta,}
\]

then the approximate robust problem has the same unique optimal action `a*`.

This turns decision margin into an architecture-neutral precision requirement.

---

## 4. The factor two is sharp

The constant `2` cannot be improved without additional structure.

Take two actions with true robust scores

\[
R(a_0)=0,
\qquad
R(a_1)=\Delta.
\]

A legal perturbation can shift the optimal score upward by `delta` and the competitor downward by `delta`:

\[
\widehat R(a_0)=\delta,
\qquad
\widehat R(a_1)=\Delta-\delta.
\]

If `Delta < 2 delta`, the wrong action becomes strictly preferred. At `Delta=2 delta`, a tie can be forced.

**RDP-4 — Sharpness.** No universal guarantee based only on the sup-norm loss error can replace `2 delta` by a smaller constant.

Thus the stability boundary is a real phase boundary, not proof slack.

---

## 5. Obligation tolerance determines sufficient precision

Suppose the declared obligation accepts any action whose robust regret is at most `epsilon`:

\[
R(a)-R^*\le\varepsilon.
\]

RDP-2 immediately gives:

**RDP-5 — Tolerance-to-Precision Law.** A certified loss representation with

\[
\boxed{\delta\le\varepsilon/2}
\]

is sufficient for the approximate robust minimizer to satisfy the obligation.

Because RDP-4 is sharp, this `epsilon/2` threshold cannot be universally relaxed when no further structure is declared.

This is the missing bridge from approximate semantic tolerance to required internal numerical/statistical precision.

---

## 6. Precision as a morphology/resource gate

Let candidate realization family `j` have a certified worst-case loss-representation error `delta_j` and resource vector `rho_j`. Under tolerance `epsilon`, define the guaranteed-admissible family set

\[
\mathcal J_\varepsilon
=
\{j:2\delta_j\le\varepsilon\}.
\]

Then physical/developmental family selection proceeds only among admissible candidates:

\[
\operatorname{Pareto}\{\rho_j:j\in\mathcal J_\varepsilon\}.
\]

For exact action identity with known margin `Delta`, the corresponding gate is `2 delta_j < Delta`.

**RDP-6 — Precision Morphology Gate.** Increasing demanded decision accuracy can force a phase change from a cheap low-precision realization to a more expensive high-precision realization even when both implement the same nominal algorithmic form.

Conversely, large robust margins license lower precision without changing the protected action.

Examples of the resource coordinate supplying `delta_j` include numerical precision, quantization, sensor accuracy, model approximation, value-function approximation and finite-sample estimation—provided the claimed error certificate is valid for the declared ecology.

---

## 7. Information quality and garbling

A physical observation channel may be used to construct `Lhat` or directly select an action. If channel `Z'` is a garbling of a more informative channel `Z`, every downstream policy available under `Z'` can be simulated from `Z` by applying the garbling first. Thus the attainable robust decision/resource set under `Z` contains the corresponding simulated set from `Z'`, before charging any extra physical cost of the better channel.

This is the operational data-processing principle already present in Grand GMI's semantic-cut theory and in Blackwell-style comparison of experiments. It is not a new theorem claimed here.

The role of this tranche is different: once an information/estimation process certifies a uniform decision-relevant error `delta`, RDP-1..6 say exactly what that precision buys.

---

## 8. Exact hostile microscope

`grand_gmi_decision_precision_checks_v1.py` exhausts a finite perturbation universe:

- 3 actions;
- 2 ecology coordinates;
- every true integer loss field in `{0,1,2,3}^6`: **4,096** fields;
- every coordinate perturbation in `{-1,0,+1}^6`: **729** perturbations per field;
- `delta=1`;
- total **2,985,984** field/perturbation cases.

Every case satisfies:

1. robust-score error at most `1`;
2. every approximate minimizer has true robust regret at most `2`.

For all **107,163** cases where the true optimum is unique and has margin strictly greater than `2`, the approximate optimum remains the same unique action.

The exhaustive universe also contains:

- **613,659** wrong-or-tied approximate decisions when the unique true margin is below `2`, demonstrating the unstable region;
- **94,974** forced-tie cases at exact margin `2`;
- observed maximum approximate-decision regret exactly `2`, establishing sharpness inside the finite microscope.

Aggregate terminal:

`GRAND_GMI_ROBUST_DECISION_PRECISION_TRANCHE_ALL_GREEN`.

---

## 9. Parent subtraction

Wald/minimax statistical decision theory, robust optimization, perturbation analysis and Blackwell comparison of experiments own the generic max-loss and information-order machinery. Contemporary work also develops prior-free Blackwell-style experiment comparisons under worst-case criteria.

Grand GMI does not claim those parent results as inventions.

The residual synthesis is the architecture-neutral chain

\[
\boxed{
\text{obligation tolerance / action margin}
\to
\text{required loss precision}
\to
\text{information / numerical / estimation resource}
\to
\text{admissible realization families}
\to
\text{physical morphology frontier}.
}
\]

This makes precision a derived machine-intelligence morphology variable rather than an implementation detail.

---

## 10. Scope and falsifiers

RDP-1..5 require only a valid uniform loss-error certificate and well-defined robust suprema. RDP-6 additionally assumes the registered candidate precision/resource profiles are valid.

No universal sample count follows from these theorems. Sample complexity depends on the declared observation/noise model used to obtain `delta`. No universal scalar precision metric is privileged across all tasks.

Direct falsifiers are:

1. a legal perturbation with robust-score error exceeding `delta`;
2. an approximate robust minimizer with true regret greater than `2 delta`;
3. a unique true optimum with `Delta>2 delta` that is not preserved;
4. a universal counterexample showing a constant below `2` suffices under only the stated assumptions;
5. a mismatch in the frozen exhaustive receipt.
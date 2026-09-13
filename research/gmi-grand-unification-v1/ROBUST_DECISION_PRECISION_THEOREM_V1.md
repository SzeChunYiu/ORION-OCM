# Grand GMI Robust Decision Precision Theorem V1

Status: **FINITE-REGRET THEOREM WITH EXPLICIT SCORE DOMAIN + SHARP EXACT WITNESSES**
Date: 2026-09-13

## 0. The missing quantitative link

Approximate semantic geometry says how response distinctions change with tolerance. It does not by itself say **how accurately values/losses must be represented before a decision is guaranteed adequate**.

This tranche supplies that link without placing a probability prior over the ecology.

Let `E` be a nonempty admitted ecology set, `A` a nonempty finite action set and

\[
L_e(a)\in\mathbb R
\]

be the loss of action `a` in environment `e`. Define the robust action score

\[
R(a)=\sup_{e\in E}L_e(a),
\qquad
R^*=\min_a R(a).
\]

For the main finite-score statement, require `R(a)` to be finite for every action. Real pointwise losses alone do not imply finite robust suprema on an infinite ecology. Let an approximate machine carry real estimated losses `Lhat` with a certified uniform error bound for a finite `delta>=0`:

\[
\boxed{\sup_{e,a}|\widehat L_e(a)-L_e(a)|\le\delta.}
\]

The uniform bound then makes every estimated robust score finite as well. Both action minima exist because the action set is nonempty and finite; no ecology supremum needs to be attained. No distribution over `E` is used.

For example, `E={1,2,...}` and `L_n(a)=Lhat_n(a)=n` satisfy uniform error zero while every robust score is `+infinity`. Neither an absolute score difference nor regret relative to an infinite optimum is defined. This problem is outside the finite-regret theorem. Section 2 states the useful extension when some, but not all, actions have infinite scores.

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

The absolute-difference statement extends to any nonempty ecology with finite robust scores and the same finite uniform error bound. It does not require maximizing environments. If an action instead has score `+infinity`, the preceding order inequalities remain meaningful in the extended reals, but `|infinity-infinity|` must not be formed.

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

### Extension allowing unusable infinite-score actions

With nonempty `E`, real pointwise losses and finite uniform error, `R(a)=+infinity` iff `Rhat(a)=+infinity`. If at least one action has finite robust score, the minima over the finite action set are finite, and every selected minimizer has finite score. Applying the proof to `a*` and `hat a` therefore still yields finite regret at most `2 delta`, even if other actions have infinite scores. RDP-1's absolute-difference form applies only to the finite-score actions. If all actions have infinite score, the order inequalities hold but there is no finite-regret certificate.

### Selection accuracy is separate from representation accuracy

The bound assumes the machine actually selects an estimated minimizer. A family that only represents accurate losses has not yet established this. More generally, if its selected action satisfies

\[
\widehat R(\hat a)\le\min_a\widehat R(a)+\alpha,
\qquad 0\le\alpha<\infty,
\]

the same chain gives `R(hat a)-R* <= 2 delta + alpha`. For exact minimization `alpha=0`. Any physical cost or developmental requirement for performing that selection belongs in the registered realization evidence.

---

## 3. Exact action-stability margin

Assume the true robust optimum is unique. If there are competing actions, define its robust margin

\[
\Delta
=
\min_{a\ne a^*}\left[R(a)-R(a^*)\right] >0.
\]

For a singleton action set, use the convention `Delta=+infinity`; the only action is necessarily selected and has zero regret. In the extension above, a competitor with score `+infinity` has gap `+infinity` relative to the finite optimum and cannot be an estimated minimizer. No difference of two infinite scores is needed.

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

This turns decision margin into an architecture-neutral precision requirement. For `alpha`-suboptimal estimated selection, `Delta>2 delta+alpha` is sufficient to force selection of `a*`.

---

## 4. The factor two is sharp

The constant `2` cannot be improved without additional structure.

For `delta>0`, take two actions with true robust scores

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

If `0 < Delta < 2 delta`, the wrong action becomes strictly preferred. At `Delta=2 delta`, a tie can be forced.

At equality, either approximate minimizer may be selected; choosing the competitor gives regret exactly `2 delta`. The regret bound includes equality, while preservation of the unique optimal action needs the strict margin. When `delta=0`, the scores and their minimizer sets agree exactly and all selected minimizers have zero regret.

**RDP-4 — Sharpness.** No universal guarantee based only on the sup-norm loss error can replace `2 delta` by a smaller constant.

Thus the stability boundary is a real phase boundary, not proof slack.

---

## 5. Obligation tolerance determines sufficient precision

Suppose the declared obligation accepts any action whose robust regret is at most a finite `epsilon>=0`:

\[
R(a)-R^*\le\varepsilon.
\]

RDP-2 immediately gives:

**RDP-5 — Tolerance-to-Precision Law.** A certified loss representation with

\[
\boxed{\delta\le\varepsilon/2}
\]

is sufficient for the approximate robust minimizer to satisfy the obligation.

For a certified `alpha`-suboptimal selector, the sufficient gate becomes `2 delta+alpha<=epsilon`.

Because RDP-4 is sharp, this `epsilon/2` threshold cannot be universally relaxed when no further structure is declared.

This is the missing bridge from approximate semantic tolerance to required internal numerical/statistical precision.

---

## 6. Precision as a morphology/resource gate

Let candidate realization family `j` have a certified finite worst-case loss-representation error `delta_j`, resource vector `rho_j`, and a certified procedure that selects an estimated minimizer. Under finite tolerance `epsilon>=0`, define the guaranteed-admissible family set

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

If selection is only certified within `alpha_j` of the estimated optimum, replace `2 delta_j` in these sufficient gates by `2 delta_j+alpha_j`. These sets collect families guaranteed adequate by the stated error bounds. A family outside them may still be adequate under a sharper direct certificate; failure of a sufficient precision bound is not proof of inadequacy.

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

The additive `grand_gmi_decision_finite_scores_checks_v1.py` checks score-domain rejection, finite-optimum problems with unusable infinite-score actions, singleton selection, exact equality ties, strict margins, and selection slack. Its boundary receipt is separate from the unchanged finite exhaustive receipt.

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

RDP-1's absolute-difference form requires finite robust scores and finite nonnegative precision. RDP-2 and its finite-regret corollaries require a nonempty finite action set, nonempty ecology, real pointwise losses, finite uniform precision, and at least one finite robust score; the main statement imposes the simpler condition that all scores are finite. RDP-3 additionally requires a unique finite optimum, with the singleton convention above. RDP-6 also requires valid precision/resource profiles and a selection procedure with the asserted optimization accuracy. Measurable policies, infinite action sets and physical optimization costs need their own hypotheses and evidence.

No universal sample count follows from these theorems. Sample complexity depends on the declared observation/noise model used to obtain `delta`. No universal scalar precision metric is privileged across all tasks.

Direct falsifiers are:

1. a legal perturbation with robust-score error exceeding `delta`;
2. an approximate robust minimizer with true regret greater than `2 delta`;
3. a unique true optimum with `Delta>2 delta` that is not preserved;
4. a universal counterexample showing a constant below `2` suffices under only the stated assumptions;
5. a claimed finite-regret certificate that subtracts infinite scores or lacks an adequate estimated-action selector;
6. a mismatch in the frozen exhaustive or additive boundary receipt.

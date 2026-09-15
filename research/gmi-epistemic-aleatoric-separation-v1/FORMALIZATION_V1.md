# Exact epistemic / aleatoric separation — formalization V1

Issue #750; parent ledger #602 Section M. Pre-implementation authority: `FREEZE_V1.md`, commit `f134569e8a9789cee5b3fde78d2ec330e5355d2a`, committed before the executor, tests, receipt, or scored result existed on the branch.

## 1. Claim boundary and parent subtraction

Claim ceiling:

```text
EXACT_EPISTEMIC_ALEATORIC_SEPARATION_FOR_REGISTERED_FINITE_LATENT_MODELS
```

The mathematics is parent-owned. The central identity is the ordinary law of total variance. The uncertainty-language parent is the standard distinction between uncertainty attributed to stochastic outcome variation conditional on a model/state and uncertainty attributed to ignorance over the model/state. Hüllermeier & Waegeman (2021) explicitly emphasize that epistemic and aleatoric uncertainty are conceptually distinct and may require distributional or set-based representations; Kendall & Gal (2017) likewise distinguish observation noise from model uncertainty in Bayesian predictive modeling.

This capsule contributes only a strict exact contract at a finite registered scope: rational probability tables, a proof that the variance split is exact under the registered latent semantics, a proof that the split is **not identifiable from the predictive marginal alone**, and fail-closed software that refuses to manufacture the split when the latent semantics are absent.

Evidence classes:

- EA-1–EA-5: P1 finite mathematical statements;
- exact rational implementation and 108-model census: P2 executable evidence;
- no P4 empirical calibration claim is made.

Forbidden implications include universal uncertainty decomposition, posterior correctness, capability/morphology uncertainty calibration, or a claim that an observed source of variation is metaphysically irreducible.

---

## 2. Registered finite latent semantics

Let `Theta` be a finite nonempty set. A registered latent model consists of exact rational weights

```text
pi(theta) >= 0,   sum_theta pi(theta)=1,
```

and, for each `theta`, a finite probability kernel over rational outcomes `Y`:

```text
K_theta(y) >= 0,   sum_y K_theta(y)=1.
```

Define, for each positive-weight latent state,

```text
m(theta) = sum_y K_theta(y) y,
v(theta) = sum_y K_theta(y) [y-m(theta)]^2.
```

The registered predictive marginal is

```text
P_Y(y) = sum_theta pi(theta) K_theta(y),
```

and its mean is

```text
mu = sum_theta pi(theta) m(theta) = sum_y P_Y(y) y.
```

Define the registered components

```text
A      = sum_theta pi(theta) v(theta),
E_mean = sum_theta pi(theta) [m(theta)-mu]^2,
T      = sum_y P_Y(y) [y-mu]^2.
```

`A` is the **aleatoric variance component relative to the registered conditioning semantics**. `E_mean` is the **epistemic variance of the conditional predictive mean**. The qualifier is essential: the same predictive marginal can admit different latent decompositions.

No independence assumption is needed. `Theta` is the conditioning variable itself; the result is an algebraic identity for the registered joint distribution.

---

## 3. EA-1 — exact finite law of total variance [P1]

### Theorem

For every valid registered finite latent model,

```text
T = A + E_mean.
```

Moreover `A>=0`, `E_mean>=0`, and therefore each component is at most `T`.

### Proof

Using the joint weights `pi(theta)K_theta(y)`, write

```text
T = sum_theta pi(theta) sum_y K_theta(y) [y-mu]^2.
```

For each `theta`, add and subtract its conditional mean:

```text
y-mu = [y-m(theta)] + [m(theta)-mu].
```

Squaring gives

```text
[y-mu]^2
= [y-m(theta)]^2
+ 2[y-m(theta)][m(theta)-mu]
+ [m(theta)-mu]^2.
```

Now take the `K_theta`-weighted sum over `y`. The cross term vanishes exactly because

```text
sum_y K_theta(y)[y-m(theta)]
= m(theta)-m(theta)
= 0.
```

The remaining first term is `v(theta)` and the third term is constant in `y`, so its kernel-weighted sum is `[m(theta)-mu]^2`. Weighting by `pi(theta)` and summing over `theta` yields

```text
T
= sum_theta pi(theta)v(theta)
+ sum_theta pi(theta)[m(theta)-mu]^2
= A + E_mean.
```

Every summand in `A` and `E_mean` is a nonnegative probability weight times a square, so both components are nonnegative. Since their sum is `T`, each is bounded above by `T`. QED.

The executable implementation computes `T` independently from the induced predictive marginal rather than setting it to `A+E_mean`; the test census then checks exact equality.

---

## 4. EA-2 — the split is not identifiable from the predictive marginal [P1 impossibility]

Consider these two registered latent models.

### Model A: PURE_ALEATORIC

There is one latent state `q` with weight one, and

```text
K_q(-1)=1/2,
K_q(+1)=1/2.
```

Hence

```text
P_Y(-1)=P_Y(+1)=1/2,
mu=0,
T=1,
A=1,
E_mean=0.
```

### Model B: PURE_EPISTEMIC_MEAN

There are two latent states `minus, plus` with weights `1/2,1/2`, and deterministic kernels

```text
K_minus(-1)=1,
K_plus(+1)=1.
```

Hence the predictive marginal is **identical**:

```text
P_Y(-1)=P_Y(+1)=1/2,
mu=0,
T=1,
```

but now

```text
A=0,
E_mean=1.
```

### Theorem EA-2

There is no function of the predictive marginal distribution alone that returns the registered pair `(A,E_mean)` correctly for every model in this finite latent class.

### Proof

Assume for contradiction that a function `F(P_Y)` returns the unique correct pair for every model. The two models above have exactly the same `P_Y`, so `F` must return the same value on both. But correctness would require

```text
F(P_Y)=(1,0)
```

for Model A and

```text
F(P_Y)=(0,1)
```

for Model B, a contradiction. QED.

### Corollaries

Since support, interval width, predictive variance, and any other statistic computed solely from `P_Y` are functions of the marginal, none can uniquely recover the registered decomposition over this model class.

The result is stronger than saying “variance is insufficient”: even the **entire predictive distribution** is insufficient absent latent/conditioning semantics.

This is why the executor returns

```text
CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS
```

for a marginal-only object.

---

## 5. EA-3 — exact pure and mixed controls [P1/P2]

The frozen mixed model is

```text
pi(L)=pi(R)=1/2,
K_L(-1)=K_L(0)=1/2,
K_R(0)=K_R(+1)=1/2.
```

Its conditional means are

```text
m(L)=-1/2,
m(R)=+1/2.
```

Each conditional variance is `1/4`, hence

```text
A = (1/2)(1/4)+(1/2)(1/4)=1/4.
```

The predictive mean is zero, hence

```text
E_mean
= (1/2)(-1/2)^2 + (1/2)(1/2)^2
= 1/4.
```

The marginal is

```text
P_Y(-1)=1/4,
P_Y(0)=1/2,
P_Y(+1)=1/4,
```

so direct marginal calculation gives

```text
T=1/2=A+E_mean.
```

The two limiting controls are exact:

- point-mass latent distribution + a nondegenerate kernel gives `E_mean=0` while `A>0`;
- multiple positive latent states + deterministic kernels with distinct means gives `A=0` while `E_mean>0`.

These demonstrate that neither term is merely a numerical artifact of the other.

---

## 6. EA-4 — zero mean-epistemic variance is not zero model uncertainty [P1]

Consider

```text
pi(a)=pi(b)=1/2,
K_a(0)=1,
K_b(-1)=K_b(+1)=1/2.
```

Both conditional means equal zero. Therefore

```text
E_mean=Var_pi(m(theta))=0.
```

Yet `K_a` and `K_b` are different probability distributions. Thus the latent/model state changes the predictive law even though it does not change its conditional mean.

### Theorem EA-4

`E_mean=0` does not imply that all positive-weight conditional predictive kernels are identical, and therefore does not imply absence of all epistemic/model uncertainty about the predictive distribution.

The exact control above is a witness. QED.

The executable field

```text
positive_weight_kernels_identical
```

is deliberately only a diagnostic. It is **not** an additional variance component and is not inserted into `T=A+E_mean`. Its purpose is to make the nearest false generalization machine-visible.

Broader epistemic uncertainty may concern variance, tails, multimodality, structural alternatives, latent representation, or other functionals not captured by a scalar conditional mean.

---

## 7. EA-5 — semantic relativity under latent refinement/coarsening [P1]

EA-2 gives a constructive refinement/coarsening example. The one-state stochastic representation and the two-state deterministic representation induce exactly the same observable predictive law, yet move all predictive variance from `A` to `E_mean`.

Therefore the labels “aleatoric” and “epistemic” in this capsule are not properties of the marginal distribution in isolation. They are properties of a **registered joint/conditional semantics**: what is treated as known conditioning state and what remains stochastic within that state.

This matches the broader uncertainty literature's warning that the conceptual distinction depends on the learner/modeling context. Hüllermeier & Waegeman discuss both distributional and set-based epistemic representations and emphasize ignorance versus randomness; Kendall & Gal operationalize the distinction as model uncertainty versus observation noise in a Bayesian deep-learning setting. The present theorem is narrower and exact: it does not inherit claims about any particular model family.

### Consequence

A claim such as “aleatoric uncertainty is intrinsically irreducible” is **not established here**. A later refinement of the conditioning information may reclassify variance. The only exact claim is relative to the frozen finite latent contract.

---

## 8. Exact census and invariances [P2]

The hostile suite independently generates a complete small rational family with:

- two registered latent states;
- latent weights `(0,1)`, `(1/2,1/2)`, or `(1,0)`;
- outcomes `{-1,0,+1}`;
- every kernel whose probabilities are integer multiples of `1/2` summing to one.

There are six such kernels and therefore

```text
3 * 6 * 6 = 108
```

models in the census.

For each model the test independently reconstructs the predictive marginal by direct joint accumulation, computes marginal mean and variance without calling the production marginal helper, and checks

```text
T_direct = T_reported = A + E_mean,
A>=0,
E_mean>=0,
A<=T,
E_mean<=T.
```

The suite also proves by execution that latent-label permutations leave every reported numerical quantity and the marginal unchanged. A zero-weight latent state is inert, including for the positive-weight kernel-identity diagnostic.

---

## 9. Fail-closed representation contract

The scored implementation admits only exact `Fraction` outcomes and probabilities. It rejects malformed or non-normalized tables, duplicate labels, duplicate kernel outcomes, empty models/kernels, negative probabilities, and floating-point scored inputs.

A `MarginalOnly` object is a valid exact predictive distribution but lacks the semantics required for the EA split. It therefore returns only

```text
CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS.
```

This is not a software inconvenience; EA-2 proves that fabricating a unique decomposition from that object would be mathematically unjustified.

---

## 10. Epistemic, aleatoric, and set-valued uncertainty across #602

At the scope of #750:

- `A` represents conditional outcome variability under the registered latent semantics;
- `E_mean` represents uncertainty of the conditional predictive **mean** across registered latent/model alternatives;
- confidence sets such as those in #657 and propagated sets such as those in #748 are epistemic/set-valued objects but need not carry a probability distribution over their members;
- therefore a variance decomposition is undefined for such a set unless an additional registered weighting/kernel semantics is supplied.

This distinction is intentionally compatible with #748: a set-valued developmental relation is not silently treated as an aleatoric transition distribution. It remains a set of admissible transitions unless a stochastic kernel is separately registered.

Accordingly, #750 can close the #602 row “Distinguish epistemic uncertainty from aleatoric uncertainty” at an exact registered finite-latent scope, while leaving both “Calibrate capability-prediction uncertainty” and “Calibrate morphology-phase uncertainty” open.

---

## 11. Falsifiers and nearest counterexamples

The registered claim fails if any valid finite model violates the exact variance identity, if the EA-2 marginals differ, if marginal-only input receives a numerical split, or if relabeling latent states changes a result.

The nearest counterexamples to overbroad readings are already inside the capsule:

1. **Marginal-identifiability overclaim:** EA-2 refutes it with identical marginals and opposite splits.
2. **`E_mean=0` means no epistemic uncertainty:** EA-4 refutes it with same conditional means and different kernels.
3. **Aleatoric is absolutely irreducible:** EA-5 shows the split changes under a different latent refinement while the predictive marginal stays fixed.
4. **Set-valued uncertainty is a probability distribution:** #748-style admissible sets have no weights unless a kernel is separately registered.

A real application can also fail the premises because its posterior/latent semantics are misspecified or uncalibrated. This capsule does not prove those premises from data.

---

## 12. Verification disposition

`test_epistemic_aleatoric_v1.py` contains 23 exact/adversarial tests. The dedicated workflow runs them under normal Python and `python -O`, verifies that freeze commit `f134569e8a9789cee5b3fde78d2ec330e5355d2a` is an ancestor and changed only `FREEZE_V1.md`, verifies that implementation/result artifacts were absent from the freeze commit, and reproduces `RESULT_V1.json` byte-for-byte.

The deterministic receipt must preserve the frozen exact values:

```text
PURE_ALEATORIC:      A=1,   E_mean=0,   T=1
PURE_EPISTEMIC_MEAN: A=0,   E_mean=1,   T=1
MIXED:               A=1/4, E_mean=1/4, T=1/2
SAME_MEAN_DIFFERENT_KERNELS:
                     E_mean=0, kernels_identical=false
NO_LATENT_SEMANTICS: CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS
```

Passing these controls establishes the scoped exact contract only. It is not evidence that a particular real-world latent model is the correct one.
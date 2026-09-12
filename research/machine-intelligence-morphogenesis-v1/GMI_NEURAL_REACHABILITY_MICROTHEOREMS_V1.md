# GMI Neural Reachability Microtheorems v1

Status: **FORMAL NONLINEAR DEVELOPMENT CALIBRATION / EXACT TOY REGIME**

Status date: 2026-09-12.

Purpose:

> Prove, in the smallest nonlinear example, that representational capacity does not imply developmental reachability, and that activation/update geometry must enter GMI's developmental-potential law.

---

# 1. One-parameter ReLU task

Consider one training obligation

\[
x=1,\qquad y=1
\]

and model

\[
f_w(x)=\max(0,wx).
\]

Use squared loss

\[
L(w)=\frac12(f_w(1)-1)^2.
\]

The target is exactly representable at `w=1`.

## Theorem NR-1 — dead-ReLU developmental trap

For every initialization

\[
w_0<0,
\]

standard gradient descent using the ordinary derivative on the negative ReLU branch has

\[
\frac{dL}{dw}=0,
\]

so

\[
w_t=w_0
\]

for every step `t` and

\[
L(w_t)=\frac12.
\]

Thus the globally representable exact solution is unreachable from the entire negative half-line under this development rule.

### Proof

For `w<0`, `f_w(1)=0` and the ReLU derivative is zero. Chain rule gives zero loss gradient. QED.

### GMI consequence

A representational-capacity theorem that ignores initialization/activation gradient geometry can falsely predict finite developmental burden when the actual burden under the registered optimizer is infinite.

---

# 2. Active ReLU branch

For `w>0`,

\[
L(w)=\frac12(w-1)^2,
\qquad
\frac{dL}{dw}=w-1.
\]

Gradient descent with step `eta` satisfies

\[
w_{t+1}-1=(1-\eta)(w_t-1).
\]

## Theorem NR-2 — active-region convergence

For

\[
0<\eta<2,
\]

and a trajectory that remains on the positive branch, error contracts geometrically with factor

\[
|1-\eta|.
\]

At `eta=1`, any positive initialization reaches the exact solution in one step.

---

# 3. Leaky activation removes the exact dead half-line

Let

\[
f_w(1)=
\begin{cases}
w,&w\ge0\\
\alpha w,&w<0
\end{cases}
\]

with fixed `alpha in (0,1)`.

For `w<0`,

\[
L(w)=\frac12(\alpha w-1)^2
\]

and

\[
\frac{dL}{dw}=\alpha(\alpha w-1).
\]

Gradient descent obeys

\[
w_{t+1}=(1-\eta\alpha^2)w_t+\eta\alpha.
\]

## Theorem NR-3 — negative-region leaky recurrence crosses toward the active region

If

\[
0<\eta\alpha^2<1,
\]

then while `w_t<0` the recurrence moves toward the positive fixed point `1/alpha`. Starting from any finite `w_0<0`, it crosses zero after finitely many steps.

### Proof

The affine recurrence has contraction coefficient `a=1-eta alpha^2` in `(0,1)` and fixed point

\[
w^*=\frac{\eta\alpha}{1-a}=\frac1\alpha>0.
\]

Hence

\[
w_t-w^*=a^t(w_0-w^*)
\]

converges monotonically to a positive value; therefore it cannot remain negative forever. QED.

### Interpretation

A seemingly small change to the primitive activation law changes developmental reachability even though both model classes can represent the same positive solution.

---

# 4. Reachability is a property of the full development protocol

The example proves that the relevant object is

\[
(\text{representation},\text{initialization},\text{update rule},\text{activation geometry},\text{budget}),
\]

not architecture/capacity alone.

Define, for target-adequacy set `A`, the optimizer-relative basin

\[
\mathcal B_A(U)=\{\theta_0:\exists t<\infty,\;U^t(\theta_0)\in A\}.
\]

## Corollary NR-3.1

For the ReLU example under ordinary gradient descent,

\[
(-\infty,0)\cap\mathcal B_A=\varnothing
\]

for exact target adequacy, while for the leaky system under the theorem conditions every finite negative initialization can leave the negative branch.

This is an exact microscopic **developmental accessibility** distinction.

---

# 5. Why this does not solve neural reachability

The theorem is intentionally tiny. Real networks introduce:

```text
many interacting active/dead regions
saddles and spurious minima
stochastic gradients
normalization/residual pathways
feature creation and representation drift
width/depth redundancy
optimizer state and momentum
batch/data ordering
```

Parent theory also shows that deep linear networks can have benign local-minimum structure under conditions where nonlinear networks need not. Therefore simple linear reachability laws cannot be promoted wholesale to nonlinear neural systems.

---

# 6. Gap update

`GKF-02 neural reachability` now contains:

```text
quadratic convex spectral law                 CLOSED
one-parameter nonlinear activation trap      CLOSED
activation-law counterfactual                CLOSED
full nonlinear network accessibility         OPEN-BLOCKING
```

A future pre-outcome estimator should predict quantities such as:

```text
fraction/probability of initialization in productive basins
local gradient signal density
activation saturation/deadness
conditioning along active subspaces
feature-learning movement required
escape/recovery mechanisms
```

and must reduce to the exact laws above on the registered base cases.

---

# 7. Claim ceiling

This proves that GMI must model developmental accessibility separately from representational capacity. It does not claim a general closed-form theory of neural optimization.

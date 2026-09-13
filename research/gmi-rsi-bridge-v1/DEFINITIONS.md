# Definitions and claim grammar

## 1. State and authority

Keep the existing Machine Epistemics machine object

\[
M_t=(F_t,O_t,\Pi_t,C),
\]

but separate the externally governed constitution from the state the machine may propose to change.  For this bridge write

\[
X_t=(M_t,D_t,A_t;C),
\]

where:

- `D_t` is the **development operator**: the persistent mechanisms that diagnose failure/opportunity, generate/search candidate changes, construct challengers, orchestrate evaluation, migrate state, and produce successors;
- `A_t` is the registered archive/lineage sufficient to bind ancestors, interventions, descendants and evaluation receipts;
- `C` is external adoption/invariant authority.  A candidate may model `C`; it does not self-authorize changing `C` inside this claim family.

The load-bearing separation remains:

```text
machine state ≠ self-model ≠ authority to admit a state change
```

## 2. Modification surface Σ

Every assay preregisters a finite **modification surface** `Σ`.  Example members are field state, learned methods, controller policy, prompts, source code, tools, weights, data generator, self-model, causal model, evaluator proxy, and `D` itself.  The claim must state which are mutable.  An unregistered mutable surface is a causal confound.

The self boundary is therefore parameterized, not smuggled in through prose.

## 3. Levels

- **R0 — refinement:** output/episode refinement; no required persistent developmental state change.
- **R1 — persistent adaptation:** verified experience changes persistent state reused later.
- **R2 — self-modification:** the machine originates a persistent intervention on its registered self surface, but the improvement-generating mechanism `D` may remain fixed.
- **R3 — recursive evolvability:** an earned intervention changes `D`, descendants actually execute the changed `D`, and a matched frozen-`D` counterfactual shows positive held-out descendant meta-gain under frozen/shadow evaluation and matched resource budgets.
- **R4 — heritable recursive development:** R3 plus the changed `D` state persists into at least one later registered descendant.
- **R5 — general/open-ended RSI:** reserved for a separately justified generality/open-endedness claim.  No finite number of tasks, domains, generations, or benchmark gains earns R5 in this bridge.

Repeated calls to a fixed optimizer do **not** become R3 merely because the calls are nested or numerous.

## 4. Meta-evolvability

Apply the G6 evolvability triad to `D` itself:

\[
\kappa_D(z)=\frac{|\mathrm{Closure}_{H_D}(z)|}{|V_D|},
\]

\[
\Omega_D(\epsilon)=\frac{H(Z_D)}{B^D_{id}(\epsilon)},
\]

\[
\chi_D(e)=2^{H(R_D\mid e)}.
\]

These are definitions/measurement targets, not present empirical measurements for ORION.  Existing G6 raw-trace gaps remain inherited `CANNOT_CHECK` obligations.

A schematic meta-evolvability cost lower bound is

\[
C_{meta}\ge B^D_{id}+B^D_{search}(\kappa_D,\chi_D)+C^D_{verify}+C^D_{migrate}+C^D_{maintain}.
\]

## 5. Descendant metaproductivity

Current task performance and capacity to generate strong future descendants are distinct observables.

The primary GMI object remains a full resource/performance profile over a registered horizon and held-out ecology.  If and only if a utility scalarization is preregistered, a secondary scalar may be reported:

\[
\mu_k(X;B,E)=\frac{U(\mathrm{best\ validated\ descendant}_{1:k};E)-U(M_0;E)}{B}.
\]

The causal bridge quantity is

\[
\Delta_{meta}=\mu_k(X_{mutable-D})-\mu_k(X_{frozen-D}),
\]

with same root, same ecology, matched compute/data/evaluator/human budgets and a frozen/shadow evaluation boundary.

`experiment.py` uses a deliberately simple registered scalar only to test protocol logic; it is not promoted to a universal GMI utility theorem.

## 6. RSI is not acceleration

Define per-generation quality increments `δ_t=q_{t+1}-q_t`.  Recursive acceleration would require an additional condition such as increasing increments over a registered interval.  R3/R4 require positive matched descendant meta-gain, not increasing `δ_t`.

Therefore

\[
\mathrm{R3}\centernot\Rightarrow \mathrm{recursive\ acceleration}
\]

without additional assumptions.  The synthetic assay includes a constructive counterexample.

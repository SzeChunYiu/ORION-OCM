# Grand GMI Empirical Resource Identification Theorem V1

Status: **THEOREM / ROBUST FAMILY-SELECTION BRIDGE UNDER MEASUREMENT UNCERTAINTY**  
Date: 2026-09-12

## 1. Gap closed

The existing Grand-GMI family-selection and end-to-end derivation layers can select neural, non-neural or hybrid realization families once valid resource profiles are supplied. Their exact witnesses intentionally use synthetic resource tables. The remaining gap is therefore empirical:

> When measured substrate costs are uncertain, when is a neural/non-neural family verdict actually supported by evidence rather than by a hand-entered point estimate?

This layer replaces exact resource points by certified resource sets and requires a verdict to survive every resource vector still compatible with the evidence.

## 2. Evidence-bounded resource profiles

For an admissible morphology `m`, let the unknown true registered resource profile be

\[
\rho(m)=(\rho_1(m),\ldots,\rho_d(m)).
\]

An evidence process supplies a certified uncertainty set

\[
U(m)\subseteq \mathbb R^d
\]

such that the declared evidence statement is

\[
\Pr[\rho(m)\in U(m)\text{ for every registered }m]\ge 1-\delta.
\]

The set may be obtained from repeated measurement, calibration intervals, proved physical lower/upper bounds, validated simulators, or combinations of those sources. Grand GMI does not prescribe a statistical estimator; it consumes the estimator's explicitly declared coverage guarantee.

For axis-aligned bounds we write

\[
U(m)=\prod_i[\ell_i(m),u_i(m)].
\]

The morphology remains subject to the existing adequacy, cut, transformation, substrate-legality and developmental-reachability conditions. Resource evidence does not replace those conditions.

## 3. ERI-1 — robust domination theorem

Let `a` and `b` be admissible morphologies with interval uncertainty sets. If

\[
\forall i,\quad u_i(a)\le \ell_i(b)
\]

and the inequality is strict in at least one coordinate, then every resource vector compatible with the evidence satisfies

\[
\rho(a)\prec \rho(b).
\]

Hence `b` cannot lie on the true Pareto frontier on the event that all declared intervals cover their true profiles.

### Proof

For every coordinate,

\[
\rho_i(a)\le u_i(a)\le \ell_i(b)\le \rho_i(b).
\]

At least one coordinate is strict, so `a` strictly Pareto-dominates `b`. QED.

This is a sufficient certificate. Failure of the inequalities does **not** prove coexistence; it means the current interval evidence is insufficient to certify domination.

## 4. ERI-2 — robust family exclusion theorem

Let `F_A` and `F_B` be registered realization families. Suppose every admissible `b in F_B` is robustly dominated by at least one admissible `a in F_A` under ERI-1. Then, with the simultaneous coverage guarantee of the uncertainty sets, no `F_B` realization can lie on the true global Pareto frontier.

Therefore a family verdict can be evidence-certified without knowing the exact resource profile of every candidate.

A neural verdict is robustly derived only if all non-neural frontier competitors are excluded by such evidence or by independent feasibility/reachability impossibility proofs. The same rule applies symmetrically to non-neural and hybrid verdicts.

## 5. ERI-3 — abstention under overlap

If the current uncertainty sets admit two compatible worlds `W_1` and `W_2` in which different families are Pareto-selected, then the evidence does not identify the selected family.

The only valid Grand-GMI family verdict at that scope is

`UNDECIDED_FROM_CURRENT_RESOURCE_EVIDENCE`.

### Exact two-world witness

Let neural `N` and program `P` have one resource coordinate with

- `U(N)=[2,4]`,
- `U(P)=[3,5]`.

World `W_1`: `rho(N)=2`, `rho(P)=5`, so neural wins.  
World `W_2`: `rho(N)=4`, `rho(P)=3`, so program wins.

Both worlds satisfy the same evidence intervals. Therefore selecting either family would add information not contained in the evidence.

This is the empirical analogue of semantic non-identifiability.

## 6. ERI-4 — confidence transport theorem

If the joint evidence event

\[
E=\{\rho(m)\in U(m)\text{ for all registered candidates}\}
\]

has probability at least `1-delta`, and a family verdict follows deterministically from ERI-1/ERI-2 whenever `E` holds, then the family verdict is correct with probability at least `1-delta` under the declared measurement model.

Grand GMI therefore transports a calibrated evidence guarantee into a calibrated morphology-selection guarantee; it does not create confidence from uncalibrated measurements.

When only marginal intervals are available with failure probabilities `delta_j`, the union bound gives the conservative simultaneous guarantee

\[
\Pr(E)\ge 1-\sum_j\delta_j.
\]

Sharper dependence-aware guarantees may be used when proved.

## 7. ERI-5 — evidence refinement monotonicity

Suppose new evidence replaces every uncertainty set `U(m)` by a subset `U'(m) subseteq U(m)` while retaining valid coverage semantics. Any previously proved robust domination relation remains valid.

### Proof

Shrinking the winner's admissible upper envelope cannot make its worst case larger; shrinking the loser's admissible lower envelope can move it either way for arbitrary non-box sets, so the monotonicity statement is exact for retained domination only when the new sets are subsets and the old universal comparison `x <= y` held for every `x in U(a), y in U(b)`. That universal statement continues to hold for subsets. QED.

New evidence may therefore sharpen `UNDECIDED` into a family verdict. A previously certified verdict can be overturned only if the new evidence invalidates an old coverage/model assumption rather than merely refining a valid uncertainty set.

## 8. ERI-6 — measured-feasibility exclusion

Resource constraints often enter as hard budgets rather than objectives. Let a registered budget require

\[
\rho_j(m)\le B_j.
\]

If the certified lower bound satisfies

\[
\ell_j(m)>B_j,
\]

then `m` is empirically excluded from the feasible set. If instead

\[
u_j(m)\le B_j,
\]

that resource coordinate is certified feasible. Overlap across the budget boundary is unresolved and must not be rounded into feasibility.

This converts measurement evidence into the admissible morphology set before Pareto selection.

## 9. Exact finite witnesses

The accompanying checker freezes four cases.

### A. Robust neural selection

- `N`: energy `[2,2.2]`, memory `[3,3.1]`.
- `P`: energy `[4.6,5.1]`, memory `[3.8,4.2]`.

`N` robustly dominates `P` in both coordinates.

### B. Correct abstention

- `N`: cost `[2,4]`.
- `P`: cost `[3,5]`.

Neither robustly dominates the other, and compatible worlds reverse the winner. Verdict: `UNDECIDED`.

### C. Robust non-neural selection on another substrate

- `N`: energy `[5,5.4]`, memory `[4,4.2]`.
- `P`: energy `[2,2.2]`, memory `[2.5,2.8]`.

`P` robustly dominates `N`; semantics need not change.

### D. Constraint-induced neural selection

- `N`: memory `[3,3.2]`.
- `T`: memory `[9,11]`.
- budget `memory <= 5`.

`N` is certified feasible and `T` certified infeasible. A family verdict may therefore follow from measured feasibility even without direct Pareto domination.

## 10. What this closes

The Grand-GMI derivation chain is now evidence-typed:

\[
\text{obligation/ecology}
\to S^*
\to \kappa,\tau
\to \text{operational morphology}
\to \text{candidate realization families}
\to \text{measured/proved resource uncertainty sets}
\to \text{robust feasible/frontier set}
\to \text{neural/non-neural/hybrid/undecided verdict}.
\]

This removes the logical need to treat synthetic point costs as if they were measurements.

## 11. Boundary

This theorem does **not** supply measurements of present CPUs, GPUs, neuromorphic hardware, biological tissue, analog devices or quantum machines. It supplies the rule by which such measurements become valid Grand-GMI selection evidence.

It also does not make an underdetermined experiment decisive. If intervals overlap in a way that permits opposite family verdicts, the formal result is abstention and the next scientific action is better measurement, stronger substrate bounds, a narrower candidate class, or a more discriminating registered obligation/resource coordinate.

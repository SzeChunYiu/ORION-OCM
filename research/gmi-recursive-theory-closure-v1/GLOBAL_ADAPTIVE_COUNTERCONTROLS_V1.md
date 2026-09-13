# Global adaptive countercontrols

The following original finite controls are reproduced without mathematical
changes from the [preserved PR567 source](../gmi-main566567-audit-v1/raw/main/GLOBAL_ADAPTIVE_COMPOSITION_THEOREM_V1.md).
Their corresponding statistical hypotheses are in the
[active theorem](GLOBAL_ADAPTIVE_COMPOSITION_THEOREM_V1.md).

### C1. Private-history validity is insufficient

Let a hidden fair bit `Z` be visible to the scheduler but absent from each row's private history. Define

- `L_1 = 2` if `Z=1`, else `0`;
- `L_2 = 2` if `Z=0`, else `0`.

Each factor has unconditional expectation one. If the scheduler chooses row 1 when `Z=1` and row 2 when `Z=0`, the selected factor is always two. Local/unconditional validity did not survive adaptive selection. Under the global filtration containing `Z`, the selected factor visibly violates `E[L|F_0] <= 1`.

### C2. Retroactive reweighting is not self-financing

Let `E_1,E_2` independently equal `2` on heads and `0` on tails. Each has mean one. Choosing `max(E_1,E_2)` after seeing both gives expectation `2*(3/4)=3/2`. Predictable weights are essential.

### C3. Dynamic names cannot reset alpha

If each freshly named row runs an independent level-`alpha` failure event and receives a fresh full budget, familywise failure after `m` births is

\[
1-(1-\alpha)^m\to1.
\]

GAC-4 prevents this by requiring one globally summable budget.

### C4. Dependence does not imply static-row stationarity

A row whose Bernoulli success probability alternates between `1/4` and `3/4` as a function of global history has no single fixed conditional law `P_j`. A confidence sequence proved for one stationary `P_j` cannot be applied merely because the row name is unchanged.


# R4 — A_T01: does d(A_t, A_{t+1}) ≈ 0 preserve the subset-infimum?

Row: A_T01 (T01 optional-inheritance monotonicity, PROVED at R0 by lane A), rung R4
ladder question: "approximate sets: does d(A_t,A_{t+1})=0-ish preserve it? NO expected".

## Verdict (first sentence)

LIFT_FAILS — metric closeness of the strategy sets does not preserve the subset-infimum
inequality: there is a minimal hostile with Hausdorff distance ε arbitrarily small between
A and A' where `inf_A C = N·p` but `inf_{A'} C = p`, witnessed in
`hostiles/witnesses/hostile_approx_sets.json`.

## Minimal counterexample (hostile H2)

Strategy space = programs over a one-token alphabet; registered metric d = edit distance;
C(·,τ) = expected price to a C-admissible verified solution for fixed task τ (the frozen
scalarization). A = {a} with a inadmissible (C(a) = N·p, horizon-priced). A' = A ∪ {a'}
with a' at edit distance 1 from a and C(a') = p. The Hausdorff distance
d_H(A, A') = 1 (an ε-scaled edit metric makes it any ε > 0 — the metric is a registered
parameter, scale it), yet the infimum drops from N·p to p. Note A ⊂ A' here already breaks
nothing (T01 survives verbatim); the FAIL is the CONVERSE direction people read into R4:
knowing only d_H(A,A') ≈ 0 without the inclusion. The infimum is upper-semicontinuous in
d_H ONLY under a Lipschitz cost — i.e. exactly the condition that fails in H1 (G10).

## The surviving conditional (named, OCM-checkable)

LIFT_CONDITIONAL: if the frozen cost functional C is L-Lipschitz on the metric closure of
A ∪ A', then `|inf_A C − inf_{A'} C| ≤ L·d_H(A,A')` (elementary; parent: Lipschitz
continuity of infima over sets, standard). At OCM scope program costs are not Lipschitz
under any edit metric (hostile H1's discontinuity), so the conditional does not repair
practice — it names what would have to hold.

## Assumption passes (A3)

- Remove viii-M=0: irrelevant at R4 (overhead already makes T01 conditional at R0);
  verdict per rung unchanged — FAIL for the approximate-set reading.
- Remove vii-frozen-scalarization: hostile is scalar; vector versions fail coordinatewise.

## Honesty note

T01's own P1 statement is untouched and survives verbatim at R4 (sets are sets). What
FAILS is the metric-relaxation of its hypothesis. This row therefore files FAIL for the
ladder question only, not for the parent theorem.

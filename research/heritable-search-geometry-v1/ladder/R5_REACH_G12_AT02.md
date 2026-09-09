# R5 — G12 / A_T02: metric reach vs set reach — does the iff hold?

Rows: G12 (Reach_B closure), A_T02 (T02 reach expansion by irreducible primitive; #145
owns ⟨O⟩ closure). R5 ladder question: "does metric reach expand iff set-reach expands"
(expected FAIL or CONDITIONAL).

## Verdict (first sentence)

LIFT_FAILS — the "iff" is false: set-reach expansion does NOT imply metric-reach
expansion; a minimal three-state witness (aliasing pseudometric d with d(s1,s2) = 0 for
distinct states) has ⟨O ∪ {p}⟩ reach a strictly larger SET while the d-diameter and
d-closure of the reachable set are unchanged, witnessed in
`hostiles/witnesses/hostile_reach_iff.json`; the converse direction survives trivially,
which leaves a one-directional monotonicity (the CONDITIONAL).

## Minimal counterexample (hostile H5)

𝓢 = {s0, s1, s2}; O generates only s0 ↦ s1; the registered metric d has d(s0,s1) = 1,
d(s1,s2) = 0 (distinct-but-aliased states — legal pseudometric, the same aliasing as
T03), d(s0,s2) = 1. New primitive p: s1 ↦ s2, admissible within budget B. Then:

- Set reach: Reach(O) = {s0, s1} ⊊ Reach(O ∪ {p}) = {s0, s1, s2} — strict (T02's
  witness condition met, expansion genuine at R1).
- Metric reach: d-diameter of Reach stays 1; d-closure of Reach unchanged (s2 was
  already in the d-closure of {s1} at distance 0); every metric functional of the
  reachable set is a function of the set + d, hence unchanged.

Direction two (metric ⇒ set): if Reach sets are equal, EVERY metric functional of them
is equal — so metric-reach expansion implies set-reach expansion automatically (for
functionals of the reachable set; recorded so nobody hunts a counterexample that cannot
exist). The iff therefore fails exactly in the set ⇒ metric direction.

## The surviving conditional (named, OCM-checkable)

LIFT_CONDITIONAL: metric reach expands along with set reach iff the newly reachable
state lies OUTSIDE the d-closure of the previously reachable set (the "d-closure
witness" — checkable by computing d(s_new, Reach(O)) > 0, or closure membership at
finite scope). With a genuine METRIC (d(s,s') = 0 ⟹ s = s') this condition is still
violated by accumulation-point reaches (reach a limit point of the old set): the finite
witness uses the aliasing pseudometric as the sharpest instance, and the closure
condition is the exact repair.

## Assumption pass (A3)

- Remove vii-frozen-price-vector: the hostile is metric-only; budget-free. Unaffected.

## Registry note

G12 R5 = LIFT_FAILS (hostile H5); G12 R4 (metric reach balls vs closure sets) folds into
this same file: balls-vs-sets is the same aliasing/closure mismatch, NOT_APPLICABLE as a
separate R4 row (no independent R4 content beyond H1/H3 mechanisms — reason recorded).
A_T02 R5 = LIFT_CONDITIONAL under the d-closure-witness condition.

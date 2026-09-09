# R6 remaining atoms — T09, T13, T14, T16

## A_T09 @ R6 — vacuity crossover m* under a chained/moving prior

**Verdict: LIFT_CONDITIONAL** (stated as conditional; the bound is NOT
re-derived). **PARENT_STATEMENT_UNVERIFIED_TEXT** for the exact chained
PAC-Bayes bound form (parent: PAC-Bayes chain bounds, ⚠ — exact constants and
whether the chain term is a KL sum or a union term not verified against
source).

- Frozen-scope fact (given, not re-derived): the PAC-Bayes vacuity crossover
  is m* = 104 at the frozen scope.
- Conditional statement: IF each prior-amendment step k = 1..L contributes a
  complexity term of order KL(P_k || P_{k-1}) (or an ε/2^k union split) to the
  bound, THEN m* scales at least linearly in the number of live amendments L,
  up to log factors: m*(L) ≳ 104 · (1 + c·L) in the regime where per-step
  divergences are Θ(1). The crossover therefore SHRINKS only in the opposite
  regime: a moving prior that tracks the posterior reduces the residual
  KL(P || Q_L) by more than the accumulated chain cost Σ_k KL(P_k || P_{k-1}).
- Sharp form: m*(L) < m*(0) ⟺ KL gain from tracking > chain cost. Both sides
  are process quantities at R6, so the crossover is governed, not structural.
- Condition named: CHAIN-BUDGET — the ledger of prior amendments is finite and
  charged (same CHARGE discipline as T04). Without it L is unbounded and the
  chained bound is vacuous for all m.

## A_T13 @ R6 — novelty-prefix discipline vs self-extending archive

**Verdict: LIFT_CONDITIONAL.** No formal parent claimed (novelty-search
practice is context, not a theorem source).

- Archive A_t is grown by the process's own actions and is monotone (entries
  are never deleted under frozen constitutions). Hence for every fixed point
  x, novelty ρ(x, A_t) is non-increasing in t: the discipline's target moves
  monotonically away from every point the process could have prepared.
- Two surviving statements: (i) per frozen C_t, novelty ordering is a well-
  defined prefix discipline — the R1-style statement holds frame-by-frame;
  (ii) across frames, the discipline is evanescent: any fixed threshold τ is
  eventually unreachable as |A_t| → ∞ unless the space dilates.
- **Novelty farming** (the lift's failure mode): the process can add cheap
  near-duplicates of a region it intends to visit later, filling A_t so that
  its own future actions are the novelty frontier. The archive is then an
  instrument of the very process it is meant to grade. This is the exact
  self-reference R6 introduces, and it converts the discipline from an
  external constraint into a negotiated one.
- Condition named: ARCHIVE-GOV — archive growth passes the same governed-
  amendment gate as the code (each entry billed, expiry or threshold schedule
  τ(|A_t|) fixed in C_t). Under ARCHIVE-GOV the moving-target effect is
  bounded per frame by the amendment budget; monotone evanescence persists
  but at a governed rate.

## A_T14 @ R6 — NFL kernel-averaging analogue under Dobrushin-contractive families

**Verdict: PARENT_SUFFICIENT.** Wolpert–Macready (NFL averaging) together with
the sharpened NFL form (a problem distribution admits uniform algorithm
averaging iff it is closed under permutation, c.u.p. — the "NFL sharpenings"
parent) owns the conclusion: any non-c.u.p. instance distribution breaks the
averaging identity, and a distribution concentrated on a structured kernel
family is exactly such a distribution. The Dobrushin observation is an
instance of the parent's criterion, not a lift of it.

- Why the family is non-c.u.p.: Dobrushin contraction δ(K) is invariant under
  simultaneous row-column permutation of K, but the NFL permutation group acts
  on the problem/objective space, and contractivity that matters for search is
  a joint property of (K, f) — kernel aligned to landscape. Permuting f
  destroys the alignment without moving δ, so the support of the joint
  distribution is not closed under the group; by the sharpened parent, uniform
  averaging fails and algorithms are separated on this family.
- Consequently no HSG-specific theorem is needed or claimed: the analogue is
  true because the parent says non-c.u.p. ⇒ separation. Any stronger claim
  (e.g. quantitative separation by δ) would require new proof and is not
  asserted here.

## A_T16 @ R6 — no asymptotically optimal kernel sequence under self-modification

**Verdict: LIFT_CONDITIONAL**, **PARENT_STATEMENT_UNVERIFIED_TEXT** for the
exact Blum speedup statement (parent ⚠: Blum 1967 speedup theorem — recalled
form: there exist computable tasks such that for every program computing the
task and every total computable regulation factor r, another program computes
it and is faster by more than r on all but finitely many inputs; exact form
not verified against source).

- Condition named: KERNEL-UNIVERSALITY — the governed amendment grammar is
  Turing-complete over kernels (every partial computable kernel is reachable
  by a finite chain of amendments from some constitution).
- Under KERNEL-UNIVERSALITY the lift goes through by translation: candidate
  "optimal kernel sequence" = candidate optimal program for the task family;
  Blum's witness modification is realizable as an amendment chain, so for
  every self-modifying sequence there is another achieving unbounded speedup
  on infinitely many tasks. No asymptotically optimal kernel sequence exists;
  R6 meta-dynamics cannot converge to a terminal kernel.
- Without KERNEL-UNIVERSALITY (e.g. amendments restricted to a
  Dobrushin-contractive family with δ ≤ 1 − γ), the Blum witness may be
  outside the reachable set and the transfer is unproven — the failure is the
  grammar's, not Blum's.

# A_T15 @ all rungs — rung-invariance of semantic undecidability

**Verdict: LIFT_SURVIVES.** The T15 semantic undecidability is invariant under
every computable rung-lifting operator: no rung change — fixed code → governed
amendment (R6) → coupled open families (R7) — removes it. The proof is a Rice
reduction that composes with any rung operator.

## Parent invoked

Rice 1951 (Rice–Shapiro framework): every nontrivial extensional (semantic)
property of partial computable functions is undecidable. Used in the standard
index-set form: S_P = {e : φ_e has property P} is not computable for any
nontrivial semantic P. Context parent (not load-bearing): Schmidhuber Gödel
machines confront the same wall via the proof-search bottleneck.

## Statement

For every rung r, every computable rung-lift operator L_r → r+1 (an operator
mapping rung-r states to rung-(r+1) states — e.g. freezing a kernel-valued
process into a new constitution, opening a family to task inflow), and every
nontrivial semantic property P of the lifted process's computed function:

  DECIDE(L(state) satisfies P) is undecidable.

## Proof sketch (halting reduction through the lift)

1. **Encodings are computable at every rung.** Each rung state s = (C, Σ, K,
   …) has a computable Gödel encoding; a rung-r process computes a partial
   function φ_{enc(s)} (its input–output behavior over tasks). This holds at
   R6/R7 by construction: constitutions, kernel laws and exchange schedules
   are finite data.
2. **The lift is computable.** L is a computable map on encodings (governed
   amendment is itself a program; opening a boundary is a wiring change).
   Hence enc(L(s)) is computable from enc(s), and φ_{enc(L(s))} is a partial
   computable function whose index we can compute from s.
3. **Reduction.** Suppose a decider D existed for "the lifted process has P"
   at any rung. Fix nontrivial P; pick indices a, b with P(φ_a) true,
   P(φ_b) false. Given w, effectively build rung state s_w that runs machine
   w and then emulates φ_a, else emulates φ_b (possible because rung states
   encode programs — KERNEL-UNIVERSALITY is not required for this direction:
   emulation is one-shot, not a chain). Apply D to L(s_w). Then:
   D(L(s_w)) = true  ⟺  w halts.
   D decides halting. Contradiction; no such D at any rung.
4. **Uniformity.** The reduction is uniform in L: any claimed "escape rung"
   operator supplies its own decider's contradiction. The only rung changes
   that could evade step 2 are uncomputable lifts (oracle amendments), which
   are outside the governed framework by definition — and merely relocate the
   undecidability to the lift's own source.

## Consequence for the ladder

The ladder cannot terminate in a rung whose goals are decidable: improvement
predicates ("does this amendment make search better?") are semantic and
nontrivial, hence rung-invariantly undecidable. Governance (R6) and boundary
control (R7) can restrict which undecidable questions are *asked*, never make
them decidable. This is the load-bearing reason every higher rung's gates are
procedural (charged budgets, pre-commitment) rather than semantic.

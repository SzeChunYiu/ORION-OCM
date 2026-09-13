# GMI theory map — TM-1–8

Status: **SYNTHESIS LEDGER; NO NOVELTY CLAIM**
Date: 2026-09-13

Ledger item 13: one explicit specialization/difference table against the named
parent theories. Every row states what GMI **inherits**, what it **restricts**,
and what it **does not claim**. A row is evidence-backed or it is marked thin.

The governing rule is the closure unit's own literature boundary: new GMI content
must lie in system-level interfaces, cross-layer consequences, resource accounting
or a preregistered prediction — **not in relabelling parent results**.

## TM-1. Bayesian inference

**Inherited:** conditioning, belief states as sufficient statistics under a
declared model (POMDP parent, CA §8).
**Restricted:** GMI is **prior-free by construction** — the master's `E` is an
admitted ecology *class*, explicitly "not a probability prior". `GG-S8` requires
that "optional Bayesian, welfare, minimax, bargaining or refinement selectors
must be declared when they add an ordering not fixed by the agent obligations".
**Difference:** a prior is an *admitted declared selector*, never a foundation.
Worst-case/robust obligations are the default; Bayesian averaging is one admitted
specialization.
**Not claimed:** any improvement on Bayesian decision theory.

## TM-2. Information theory

**Inherited:** channel/cut framing, data-processing reasoning (GG30).
**Restricted:** the information layer is **zero-error and combinatorial**, not
entropic. `κ` is final-message alphabet width, not Shannon entropy.
**Difference, with a proved witness:** "a noisy channel whose supports overlap
for both hidden states may carry Shannon information but still has zero
zero-error semantic value for exact survival. Grand GMI therefore does not
identify semantic information with mutual information in general." GG44 fixes
the identity-channel capacity, and the 14-vertex `G13 join K1` witness gives
exact classical alphabet 5 against unassisted quantum dimension 4.
**Not claimed:** a new coding theorem or capacity result.

## TM-3. Statistical learning (PAC / VC / Rademacher)

**Inherited:** finite-class uniform convergence; ERM as a specialization
(GEI-2, LMT-3 with `n >= (2/ε²)·log(2|H|/δ)`).
**Restricted:** GEI-5 — "no particular complexity measure is fundamental to
GMI". Whatever valid complexity theorem applies becomes capability *evidence*
and may influence morphology selection; none is constitutive.
**Difference:** generalization evidence is one coordinate of a resource-indexed
selection problem, not the selection criterion.
**Not claimed:** tightness for modern neural classes; GEI says so explicitly.

## TM-4. MDL / PAC-Bayes

**Inherited:** description-length and compression intuitions appear only
informally.
**Status: THIN.** Two sector documents mention these at all. There is no
registered MDL or PAC-Bayes specialization theorem.
**Declared gap:** a compression-based complexity coordinate is admissible under
GEI-5's typing rule but has not been instantiated. This row is an open item.
**Not claimed:** any MDL or PAC-Bayes specialization, bound or comparison. The
row records absence of work, not a result about it.

## TM-5. Reinforcement learning

**Inherited:** Bellman recursion, POMDP belief-state sufficiency, proper-policy
and stochastic-shortest-path distinctions (Bertsekas).
**Restricted:** CA-2 gives an *exact robust* Bellman recursion, verified against
an independent history-tree recursion over all `5⁸ = 390,625` kernels with zero
mismatches; CA-6 refuses to promote support-set recursion to expected-risk
stochastic acquisition without the appropriate stochastic parent.
**Difference:** no discounted scalar reward is assumed; obligations are
set-valued and resources are vector-ordered. Deliberation itself is charged
(VOC-3), which standard MDP formulations leave free.
**Not claimed:** sample-efficient RL, function approximation guarantees, or
infinite-horizon control performance.

## TM-6. Causal inference

**Inherited:** structural causal models, `do(·)` semantics, the back-door
criterion, do-calculus (Pearl; Spirtes–Glymour–Scheines; Bareinboim–Pearl).
**Restricted:** CAU-1 — observationally identical registers can differ under
intervention (`1/2` against `1`), so a purely observational stream never
determines the interventional target. CAU-3 restores identifiability only by
supplying a premise, and A4 charges the probes that establish it.
**Difference:** identifiability is **purchased**, and the purchase enters the
resource ledger. GG32 additionally proves obligation non-identifiability:
opposite constitutions live on identical dynamics.
**Not claimed:** graph discovery, transportability, or identifiability of
arbitrary queries.

## TM-7. Active learning / experimental design

**Inherited:** value-of-information reasoning, controlled/active sensing,
Equivalence Class and Decision Region Determination.
**Restricted:** "prior-free active experiment selection" — the criterion is
worst-case over an admitted ecology class, not expected gain under a prior.
VOC-3 derives the stopping rule (continue iff value of computation strictly
exceeds its charge) rather than assuming it; VOC-4 refutes the myopic rule; CA-4
shows information can be replaced by control.
**Difference:** the *deliberation* is charged alongside the experiment.
**Not claimed:** optimality under stochastic or Bayesian metalevel models.

## TM-8. Neural computation

**Inherited:** universal approximation, threshold-unit realizations.
**Restricted:** GDA7 — "universal approximation supplies neural realizability
under parent hypotheses, not neural necessity". GDA6 — content-addressed
selection derives comparison/routing structure but "does not uniquely derive
Transformer syntax".
**Difference:** GDA1–GDA5 exhibit, with exact witnesses, non-neural realizations
of every derived structure — FSM state against recurrent state, stencil/automaton
against convolution, multiplexer against gating, reduction against set
aggregation. Neither family is exempt from unseen-ecology evidence (GEI §12).
**Not claimed:** that neural systems generalize worse, or that any architecture
is selected merely by being representable.

## Cross-cutting rule

`REPRESENTABLE` and `SELECTED` are distinct closure states and must never be
conflated. Every row above supplies realizability or restriction; none supplies
selection. Selection additionally requires a complete admitted feasible family,
a resource order and a development law.

## Falsifier for this map

A row is falsified by exhibiting a registered GMI result that contradicts its
"restricted" clause, or by showing that a "difference" is in fact a theorem of
the parent under the same hypotheses. TM-4 is falsified by exhibiting a
registered MDL/PAC-Bayes specialization, which would move it out of THIN.

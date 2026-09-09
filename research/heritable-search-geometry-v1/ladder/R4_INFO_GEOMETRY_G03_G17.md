# R4 — G03 / G17: information geometry of kernel and prior families; KL vs Fisher balls; the m* crossover

Rows: G03 (proposal kernel Q_t), G17 (bias/prior family, T09-B lane D), A_T09 R4
ladder question ("prior-family geometry at R4 — KL balls vs Fisher balls — does the
vacuity crossover m* shrink under a tighter family?").

## Verdict (first sentence)

PARENT_SUFFICIENT — Chentsov (1972, "Statistical Decision Rules and Optimal Inference",
AMS translation 1982; verified) owns the geometry: the Fisher information metric is, up
to scale, the unique Riemannian metric on a statistical family invariant under Markov
morphisms; KL(p‖q) = ½ d_F(p,q)² + O(d³) is the standard second-order identification, so
KL balls and Fisher balls COINCIDE infinitesimally and diverge at finite radius; the
effect on the vacuity crossover m* is a property of the family's dimension/KL mass, not
of the metric choice.

## Exact owned statements (parent, verified)

1. Chentsov's theorem: on the probability simplex, any Riemannian metric invariant under
   Markov embeddings is a positive multiple of the Fisher metric (finite case, Chentsov
   1972; generalized to arbitrary measurable spaces by Ay–Jost–Lê–Schwachhöfer 2012,
   arXiv:1207.6736). Consequence for HSG: for the registered kernel/prior family
   {Q_ρ}, the metric that Markov-morphism-invariance leaves us is Fisher — there is no
   second natural Riemannian candidate to shop for (this is a CONSTRAINT result, not a
   blessing of "curvature" vocabulary).
2. Local KL–Fisher identity (standard, Chentsov/Amari surveys): in Fisher coordinates
   θ around p, KL(p‖q(θ)) = ½ (θ−θ_p)^T I(p) (θ−θ_p) + O(‖θ−θ_p‖³). Hence for small
   radius ε: the KL ball {q : KL(p‖q) ≤ ½ε²} contains the Fisher ball of radius ε−o(ε)
   and sits inside the Fisher ball of radius ε+o(ε). At finite radius they separate
   (KL balls are not ellipsoids); no inequality of the form KL-ball = Fisher-ball exists
   beyond second order.

## The m* crossover (lane D interface, conditional)

Lane D's T09-B derives a PAC-Bayes-type bound whose complexity penalty is the KL term
KL(Q_ρ ‖ Q_0) (prior-to-moved-prior) and finds it vacuous at OCM scope, with crossover
sample/task count m*. Geometry does NOT shrink m* by metric choice (Chentsov: Fisher is
forced; and locally KL = ½ d_F², so re-expressing the penalty changes nothing at second
order). m* shrinks iff the FAMILY shrinks: LIFT_CONDITIONAL, named condition
"registered-family dimension drop": if the family is restricted so that
sup KL(Q_ρ ‖ Q_0) over admissible ρ drops from K to K' < K (e.g. restricting to an
s-dimensional exponential family with smaller parameter range), the crossover moves from
m* to m*' satisfying m*' ∝ K' by the parent bound's algebra — metric re-description buys
nothing, family restriction buys proportionally. OCM-checkable: compute sup-KL over the
registered family (the checker does this exactly on a finite two-point family,
`witness_info_geometry.json`).

## Assumption passes (A3)

- Remove vi-fixed-ecology / xiii-iid-Q: the geometry of the family is ecology-free; the
  crossover conditional is stated for the frozen lane-D bound and inherits ITS ecology
  assumptions — recorded, not re-derived here.

## Residual claimed by HSG

The interface statement "metric choice cannot shrink m*, only family restriction can"
(two-line argument from Chentsov + the parent bound's algebra); everything else is
parent-owned.

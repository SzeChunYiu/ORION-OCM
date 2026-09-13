# Common-decoder correction — recursive theory audit, iteration CD-1

Date: 2026-09-13. Reviewed predecessor: `5622ac45d0261e8fe0a92f4209b1bb782ce43732`.

## Falsified predecessor claim

`SEMANTIC_CUT_THEOREM_V1.md` §§6–8 formed `R(K)=(min_d R_e(K,d))_e`
and inserted it into an attainable cut frontier. The minimizer was permitted
to change with an unobserved ecology. That exchanges `for every e, there exists d`
with `there exists d, for every e`.

The two-ecology, no-observation witness has opposed binary correct actions.
Its oracle envelope is `(0,0)` but every real randomized risk vector is
`(p,1-p)`. The envelope is impossible and the robust risk is at least `1/2`.
This refutes the predecessor's joint-attainment interpretation; it does not
refute its fixed-ecology Bayes calculation or zero-error hypergraph theorem.

## Repaired result and dependency review

The corrected cut theorem proves three finite results explicitly:

1. The full randomized common-decoder risk set is the convex hull of the
   deterministic risk profiles, using a constructive mixture over decoder tables.
2. The oracle envelope is attainable exactly when every observation cell has
   an action minimizing every ecology's unnormalized conditional loss there.
   Cells impossible in one ecology impose no constraint from that ecology.
3. One hidden-ecology-independent garbling composed with a common decoder
   reproduces its **entire** risk vector. The decoder class must allow this
   composition; physical resource dominance needs an additional cost theorem.

The spectrum now ranges over admissible channel/decoder pairs, with the
registered tolerance applied to each pair and costs assigned explicitly.

The zero-error SC-1/GG1 and causal-semantic GG30 remain valid: they already
require a common acceptable action for all compatible hidden states. For a
randomized protocol to satisfy a finite zero-error obligation, each positive
support action must satisfy it in every compatible state; choosing a support
action gives a deterministic decoder. The erased-signal viability witness
already refused a common perfect action and is consistent with this repair.
`ROBUST_DECISION_PRECISION_THEOREM_V1.md` §7 uses common-policy emulation and
already distinguishes resource charges; it needs no theorem change.

## Exact checks and historical custody

`grand_gmi_common_decoder_checks_v1.py` emits
`GRAND_GMI_COMMON_DECODER_RECEIPT_V1.json` with:

- 2,304 finite channel/loss problems; exhaustive deterministic search agrees
  with the common-argmin condition; 644 oracle envelopes are unattainable;
- 6,561 exact joint-risk emulation identities using two ecology coordinates,
  correlated side information, zero-probability cells and stochastic decoders;
- 81 constructive convex-mixture identities over 16 deterministic tables;
- the hidden-ecology counterexample and a counterexample to unconditional
  deterministic-decoder inclusion under stochastic garbling.

Every calculation uses exact rational arithmetic. The proof establishes the
finite theorem; these checks are bounded witnesses and regression protection.
No randomized continuum is claimed exhaustively enumerated.

The historical `GRAND_GMI_SEMANTIC_CUT_RECEIPT_V1.json` and the earlier
checker are unchanged. The historical
`GRAND_GMI_SEMANTIC_CUT_TRANCHE_ALL_GREEN` terminal only certifies its recorded
117,649 zero-error families, BSC checks and computation witnesses. It did
not test multi-ecology joint attainment and cannot clear the falsified claim.

Current correction terminal:
`GRAND_GMI_COMMON_DECODER_CORRECTION_GREEN_AT_FINITE_SCOPE`.
This closes this mathematical error at the stated scope. Empirical GMI
completion, independent physical evidence and other theory audit lanes remain
separate obligations.

## Primary-source boundary

The emulation proof is classical comparison-of-experiments mathematics, not
a novel GMI information theorem. Parent reference: David Blackwell,
[Equivalent Comparisons of Experiments (1953)](https://doi.org/10.1214/aoms/1177729032),
Annals of Mathematical Statistics 24(2), 265–272. The publisher's full text
did not expose readable article content during this audit; the finite proof
above is supplied independently, rather than relying on an unread passage.

[Brooks, Frankel and Kamenica, Comparisons of Signals (March 2024)](https://benjaminbrooks.net/downloads/bfk_comparisons.pdf)
was read for the side-information boundary: joint dependence with another
signal matters, so a marginal experiment ordering cannot silently preserve
an unspecified side-information coupling. Our theorem fixes the joint law
`mu_e(x,y)K(z|x)` and the same garbling at every ecology.

[Rosenthal, Blackwell without Priors, §3 (arXiv:2510.08709v1)](https://arxiv.org/html/2510.08709v1)
was checked as a scope contrast. It observes an entire signal distribution;
that is a different information boundary from one draw of `(z,y)` here. Its
linear-transformation criterion is not substituted for a stochastic garbling
or used to establish this repair.

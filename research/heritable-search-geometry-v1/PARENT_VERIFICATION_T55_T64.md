# Parent-Verification T55–T64 (D10 follow-up, issue #233)

Independent verification of the parent-theorem claims behind PR #250
(`hsg/v3-d10-donor-theorems` @ 5a620b0). Machine-readable record:
`PARENT_VERIFICATION_T55_T64_V1.json`.

## Census

| Verdict | Count | Theorems |
|---|---|---|
| CONFIRMED | 2 | T57 (Weitzman), T62 (Candes-Recht) |
| PARTIAL | 2 | T58 (Golovin-Krause + Sviridenko), T64 (Russell-Wefald + Hay et al.) |
| WORDING_IMPRECISE | 1 | T60 (Jamieson-Talwalkar) |
| WRONG_ATTRIBUTION | 0 | (T64's Hay mis-attribution folded into PARTIAL) |
| UNVERIFIABLE | 0 | — |

T55/T56/T59/T61/T63 carry no external parent claims (P1 elementary or verified
elsewhere) and are out of scope here.

## Per-claim verdicts

| Thm | Parent(s) as cited | Verdict | Key correction |
|---|---|---|---|
| T57 | Weitzman 1979, Econometrica 47(3), doi:10.2307/1910412 | CONFIRMED | Reservation rule (z_d solves E[(X_d−z_d)^+]=c_d; decreasing-z order; stop when best observed exceeds every unopened z) matches the paper per publisher abstract + JSTOR body snippet. |
| T58 | Golovin-Krause 2011 JAIR 42; Sviridenko 2004 ORL 32(1) | PARTIAL | GK confirmed incl. live JAIR URL (view/10731; PR's 404 was a wrong URL); min-cost cover exact form is α(ln(Q/η)+1) / α(ln(Q/δη)+1), δ=min p(φ) — "O(log(1/p*))" is shorthand. Sviridenko enumerates TRIPLES (all |U|=3 sets + all 1/2-sets), not "pairs". |
| T60 | Jamieson-Talwalkar 2016, "Hyperband Applications", ICML | WORDING_IMPRECISE | Title is "…and Hyperparameter Optimization"; venue AISTATS 2016 (PMLR 51:240-248), not ICML. Proven: B > z_SH suffices (Thm 1); comparison is vs the UNIFORM ALLOCATION baseline — matching lower bound is a stated conjecture, not a theorem. (K/Δ²)log K is the stochastic KKS form; SH origin [15] Karnin-Koren-Somekh uncited in PR. |
| T62 | Candes-Recht 2009 FoCM 9, doi:10.1007/s10208-009-9045-5 | CONFIRMED | Publisher abstract verbatim: m ≥ C n^1.2 r log n (= n^6/5), uniform random sampling, nuclear-norm program, high-probability exact recovery; n^1.25 variant for all ranks. Nuance: abstract quantifies "most n×n matrices of rank r" (incoherence in body theorems). |
| T64 | Russell-Wefald 1991 AIJ 49; Hay et al. 2012 arXiv:1207.5879 | PARTIAL | R-W confirmed (utility-of-computation formula, computations as actions). Hay et al.: no later title "Bounded rational metareasonation" exists (garbled — delete); ZERO Pandora/Weitzman content in the full text; actual results are Thm 7/9 (myopic⇒optimal continuation/stop on transition-closed subsets), Thm 10 (≤ λ(1−λ)/c − 3 ≤ 1/4c − 3 computations, one-armed Bernoulli), compute-forever + non-indexability counterexamples. |

## Corrections spelled out

1. **T58 / Sviridenko** — PR says "partial enumeration over pairs". Source
   algorithm: phase 1 enumerates all feasible sets of cardinality **one or
   two**; phase 2 enumerates **all** U ⊆ I with **|U| = 3**, greedily
   completing each. Theorem 1: "The worst-case performance guarantee of the
   above greedy algorithm … is equal to 1 − e^−1" (O(n^5) evaluations).
2. **T58 / Golovin-Krause cover bound** — exact Thm 5.8 form:
   c_avg(π) ≤ α·c_avg(π*_avg)·(ln(Q/η)+1) (self-certifying) or
   α·(ln(Q/(δη))+1) in general, δ = min_φ p(φ). "log(1/p*)-competitive" holds
   only when Q/η is constant (GBS case: OPT·(ln(1/min_h p_H(h))+1)).
3. **T60 / title+venue** — "Non-stochastic Best Arm Identification and
   Hyperparameter Optimization", AISTATS 2016, JMLR W&CP 41, PMLR 51:240–248.
   Not ICML; "Hyperband Applications" is not the title; Hyperband (Li et al.)
   is not referenced by the PR.
4. **T60 / guarantee strength** — Thm 1 is a sufficiency bound (budget
   B > z_SH ⇒ best arm returned; doubling ⇒ 2z_SH); Thms 2–4 compare to
   uniform allocation ("outperforms … in favorable conditions, and performs
   comparably (up to log factors) otherwise"). "Within logarithmic factors of
   the non-stochastic lower bound" overstates: the lower bound is conjectured
   ("We conjecture that a matching lower bound to Theorem 1 …").
5. **T64 / Hay et al.** — registry cite "selecting computations under limited
   resources" and the "(later titled 'Bounded rational metareasonation…')"
   parenthetical are both wrong; the sole title is "Selecting Computations:
   Theory and Applications" (UAI 2012, pp. 346–355). "Their analysis includes
   Pandora-like settings" must be removed: no Pandora content in the paper.

## Notes

- All evidence quotes were retrieved from primary or publisher pages
  (JSTOR/Econometric Society, JAIR PDF, PMLR PDF, Springer FoCM metadata,
  AIJ CMU scan, arXiv:1207.5879 full text); none are reconstructed.
- JAIR "404" in PR #250 diagnosed: doi-form URL fetch failure, not a dead
  source — canonical article page and PDF (10731/25633) are live.

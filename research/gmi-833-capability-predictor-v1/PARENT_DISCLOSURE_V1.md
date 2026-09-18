# Parent ownership, assimilation, and the named residual

Assimilation-first: every parent below is absorbed and used, not routed around.
Nothing in this section is claimed as novel by this tranche.

## 1. External literature (parent-owned mathematics)

| owner | what it owns | identifier |
|---|---|---|
| Manski, *Partial Identification of Probability Distributions* (2003) and the identified-set literature | the identified set `I_q(C) = q[C]`, point identification iff singleton image, and the discipline of reporting sets rather than forcing points | ISBN 978-0-387-00454-9 |
| Chow, "An optimum character recognition system using decision functions" (1957) | the reject option as a decision terminal | DOI `10.1109/TEC.1957.5222035` |
| El-Yaniv & Wiener, "On the foundations of noise-free selective classification" (2010), JMLR 11:1605-1641 | selective prediction, coverage/risk trade-off | JMLR v11 |
| Boole / Fréchet union bound | `P(union of bad events) <= sum of their probabilities`, hence dependence-safe composition with no independence premise | classical |
| Rice, *The Algorithm Selection Problem* (1976) | predicting performance of a computational method from features of the problem and the method | DOI `10.1016/S0065-2458(08)60520-3` |
| Wolpert & Macready, *No Free Lunch Theorems for Optimization* (1997) | no algorithmic advantage without restriction/structure in the problem distribution; why a predictor must be relative to disclosed priors | DOI `10.1109/4235.585893` |
| Gulwani, Polozov & Singh, *Program Synthesis* (2017) | search-language-constrained program spaces; why reachability under a registered grammar differs from expressibility | DOI `10.1561/2500000010` |
| Standard multiobjective/Pareto optimisation | supremum over a superset cannot decrease; budget monotonicity | classical |
| Myhill-Nerode / bisimulation / predictive-state families | exact protected-response quotient and state minimality | classical |
| Leike & Hutter, *Bad Universal Priors and Notions of Optimality* (2015), PMLR 40:1244-1259 | even "universal" agent constructions depend materially on representation choice | PMLR v40 |

## 2. Repository parents (merged, pinned)

| package | issue/PR | what it owns that this tranche uses verbatim |
|---|---|---|
| `research/gmi-833-foundation-v1` | #837 | behavioral specification `B = (I, Acc)`; realization contract `M = (X, x0, Q, U, Chi, rho)`; developmental law `Delta` and `Reach_Delta(M_0, B)`; the 14-coordinate lifecycle resource contract inherited from #805; `forall_fin[U]` notation; the evidence/maturity ladder and the monotone forbidden-extrapolation rule |
| `research/gmi-833-morphcap-v1` | #848 | the external capability contract `c = (T, mu, u, V, b, tau)`; `C_c(M) = E_{t~mu}[u(trace_M(t))]`; the refusal to fabricate a value when no admissible execution exists; CAP-2A admissible-class monotonicity and CAP-2B resource monotonicity; the CAP-2 impossibility region; CAP-3's observational-aliasing ceiling and its positive information twin |
| `research/gmi-833-global-uncertainty-v1` | #851 | U-1's five disjoint typed constructors; U-2A `Q[R[S]] = (Q o R)[S]`; U-2B `P(theta_k in C_k) >= max(0, 1 - alpha - sum beta_i)` and the explicit refusal of the independence product; U-3A missing-relation = complete relation = `UNKNOWN`; U-3B empty upstream is not laundered; U-4A exact query identification; U-4B confidence image preservation; U-5's marginal non-identifiability |
| `research/gmi-833-capability-abstention-v1` | #913 / PR #916 | ABSTAIN-1 itself: a point iff a singleton image, the complete identified set otherwise, the forced-point counterexample theorem, and the four machine-distinct terminals |
| `research/gmi-833-capability-bounds-interactions-v1` | #906 / PR #907 | BOUND-1 floors vs ceilings; INT-1 mixed-difference interaction; BUDGET-1's exact iff for mandatory shared-charge harm (`R >= Q` and `R - M < Q`) |
| `research/gmi-833-global-vs-reachable-morphology-v1` | #874 | the separation of the globally optimal candidate from the developmentally reachable one |
| `research/gmi-833-finite-search-budget-morphology-v1` | #877 | the registered finite deterministic complete search trace with strictly positive exact evaluation costs and its cost-feasible prefix |
| `research/gmi-833-axiom-core-v1` | #854 | the registered finite axiom core |

## 3. Historical non-authority (pre-#833, mined not cited as evidence)

| package | ledger | what was mined | why it is not authority |
|---|---|---|---|
| `research/gmi-capability-predictor-v1` | #602 F4 | the architecture-name-free 8-field descriptor and the brand-label rejection rule | specification-only at claim ceiling G1, under the superseded #602 ledger; no #833 freeze, no #833 parent pins |
| `research/gmi-capability-predictor-dev-v1` | #602 F4 | the signed-margin monotone-envelope predictor and its `CANNOT_IDENTIFY` default | claim ceiling G2, development-worlds only, pre-#833 uncertainty vocabulary |
| `research/gmi-capability-calibration-v2` | #766 (successor to the #764 negative) | the determinate-frame-before-sample discipline, and the #764 assay defect as a warning | finite-population empirical calibration under the #602 ledger; this tranche makes no empirical calibration claim at all |

None of these three is pinned as a parent authority and none of their receipts is
read as evidence for any claim here.

## 4. What is NOT claimed novel

- identified sets, point identification by singleton image, and abstention;
- the reject option and selective prediction;
- Boole's inequality and dependence-safe union bounds;
- supremum monotonicity over nested feasible classes;
- the capability contract, the resource ledger, the developmental law, the search
  trace, or any of the typed uncertainty constructors;
- the observation that expressivity, resources, reachability, search and evidence
  can each limit an achieved capability. Each of those five is separately and
  already owned by the parent packages above.

## 5. The named residual of this tranche

1. **A single exact total function** `F(M,E,R,H,D,U)` that composes the parents into
   one emission, with the candidacy/contract split made explicit: `M, H, D, Seen(B)`
   decide candidacy, `E, R` decide the contract verdict, and a resource-inadmissible
   candidate is carried as `UNSATISFIED` inside the image instead of being deleted
   from the survivor set. That split is what makes soundness hold unconditionally in
   the stated form; deleting the infeasible candidate falsifies it.
2. **A prospective failure-mode taxonomy** obtained by reading one mode off each
   registered cut plus the two typed non-answers, frozen before the census, and
   proved to be a partition with a unique-binding-cut lemma and an explicitly
   censused order-dependence boundary.
3. **A total-attachment contract** in which the uncertainty object is produced by the
   same constructor as the value, enforced by a call-graph `ast` check rather than by
   convention, with the U-2B composed budget computed over the candidacy relation
   chain and the independence product refused.
4. **Two materially independent routes** and exact censuses over a frozen universe
   generator, so that the whole composition is certified rather than asserted.

The residual is the composition and its exactness, not any parent theorem.

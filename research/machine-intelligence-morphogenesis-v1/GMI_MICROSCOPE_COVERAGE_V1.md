# Section R measured: 11 of 14 tiny-world types have a microscope

Date: 2026-09-15. Addresses checklist section **R** (exact tiny-world microscopes).
Witness: `gmi_microscope/microscope_coverage_audit.py`. Receipt: `microscopes/results/STAGE_MICROSCOPE_COVERAGE_V1.json`.

Section R asks for exact tiny-world microscopes across fourteen domains, plus two rules: every microscope
**fully enumerable with a certificate**, and every positive microscope **paired with a minimal negative
twin**. The corpus has **41 witnesses**, so the question is what exists before anything new is built.

## 1  Assigned by hand, deliberately

World types are mapped to witnesses by **explicit assignment**, not by pattern matching over names. Three
audits in this corpus have now produced wrong numbers because a pattern found a common unrelated word —
`state` matching *stated*, `production` matching *reproduction*, `^rev\w*$` matching *revival*. Where the set
is small enough to assign by hand, it is assigned by hand, and every row is checkable by a reader.

A gate asserts every hand-assigned witness actually exists, so the assignment cannot rot silently.

## 2  Coverage

| world type | witnesses |
|---|---|
| architecture derivation | `neural_architecture`, `linear_family`, `gated_recurrence`, `state_space` |
| learning-law | `update_law`, `credit_assignment` |
| memory differentiation | `memory_regime`, `residual_memory`, `exemplar_parametric`, `consolidation` |
| concept-formation | `concept_formation` |
| planning | `planning_stop`, `replanning`, `subgoal`, `simulation_worth` |
| social / theory-of-mind | `social_cognition`, `social_strategic` |
| teaching | `pedagogy` |
| culture | `teaching_culture` |
| capability-ceiling | `species_algebra` |
| development / evolvability | `hierarchy`, `hierarchy_overhead`, `lesion`, `interference` |
| reachability / search-bias | `search_frontier`, `goal_formation` |
| **causal** | **none** |
| **multi-species ecology** | **none** |
| **domain-collision** | **none** |

**11 of 14 covered; three have no witness at all.**

**The multi-species gap is a cross-check, not a coincidence.** Section G box 16 found independently that every
competition result in the corpus is a **two-body contest** — and the order effect it measured (36 of 168
ordered pairs where invading and resisting disagree) is why pairwise data cannot settle a multi-species
outcome. Two separate analyses, arriving at the same missing world. A pin fails if this world ever gains a
witness without that finding being revisited.

## 3  R's two rules

**Minimal negative twin: 11 of 19 audited families carry one**, under **nine different names with no shared
token** — which is exactly why the B1 audit could not find them by pattern and had to adjudicate by hand. A
pin asserts this count agrees with the B1 receipt; two independent paths to the same number, and a divergence
is a defect in one of them.

**Fully enumerable with a certificate: one worked instance.** `real_regime_finite_state` certifies a
**10 000-state lower bound** with **49 995 000 executed pair tests**, against an enumeration of **10^83010**
machines — impossible, not merely slow.

But the receipt records `upper_bound_replicates = false`, and that is the honest half: the **lower** bound has
a demonstrated certificate method, the **upper** bound does not. Exhibiting a construction is easy;
certifying it everywhere is not. So R's certificate rule is demonstrated for one side of one microscope, and
open for the other.

## 4  Scope, and what presence does not mean

**Presence of a witness is not conformance.** That a world type has a microscope says nothing about whether
that microscope is *exact*, *fully enumerable*, or *twinned* — those are R's two rules, measured separately
above, and the twin rule stands at 11 of 19 rather than 19 of 19.

So the honest reading of "11 of 14" is: eleven world types have *something*, three have *nothing*, and the
quality bar R sets is met by a minority even among the eleven.

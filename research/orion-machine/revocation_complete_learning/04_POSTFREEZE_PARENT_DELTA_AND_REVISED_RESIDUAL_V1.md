# RCL post-freeze parent delta and revised residual V1

**Date:** 2026-09-03  
**Umbrella:** ORION-V2 #194  
**Execution:** ORION-V2 #197  
**Review:** ORION-V2 #245  
**PR:** ORION-V2 #244  
**Frozen V0 authoring commit:** `46554955cb8d4f27d520c91be65442334a638252`  
**Status:** `MATERIAL_PARENT_ADDITION__STATIC_CWC_CONTRACTED__RCL_DUAL_CERTIFICATE_BARRIER_ADDED`

This is an additive post-freeze delta. It does not modify the hash-bound V0 packet. The independent review must consider this file and its V1 review packet before returning a terminal.

## 1. Material parent addition: complete reasons

Darwiche and Hirth's *On The Reasons Behind Decisions* defines sufficient, necessary, and complete reasons for Boolean-classifier decisions and uses complete reasons to evaluate counterfactual statements. Darwiche and Ji subsequently study computing complete reasons and their prime implicants/implicates; prime implicants are sufficient reasons and prime implicates are necessary/contrastive reasons.

### Contraction

The static object previously called Counterfactual Warrant Completeness is, for a fixed monotone decision and fixed intervention semantics, a specialization of a complete reason / prime-implicant representation. The following are therefore not RCL novelty claims:

- representing all minimal sufficient warrants;
- distinguishing one sound sufficient reason from the complete family of reasons;
- evaluating fixed-classifier counterfactual feature deletions from a complete reason;
- the possibility of exponentially many sufficient reasons;
- computational hardness of enumerating or optimizing explanations.

The V0 elementary antichain theorems remain correct calibration results but lose any plausible standalone novelty route.

Primary sources:

- Adnan Darwiche and Auguste Hirth, *On The Reasons Behind Decisions*, arXiv:2002.09284.
- Adnan Darwiche and Chunxi Ji, *On the Computation of Necessary and Sufficient Explanations*, arXiv:2203.10451.
- Niku Gorji and Sasha Rubin, *Sufficient reasons for classifier decisions in the presence of constraints*, arXiv:2105.06001.

## 2. Material parent addition: provenance-guided learning under rule-induced shift

Lamaakal's 2026 preprint *Provenance Guided Incremental Learning Under Evolving Concept Definitions* studies explicit revisions to target-defining rules. Its framework compiles old/new rules into a typed delta, traces changed components through historical provenance, certifies stable records, restricts reevaluation to a candidate region, uses selective supervision for ambiguous cases, repairs the predictor incrementally, and stores recurring versions.

### Contraction

The following are no longer defensible as an RCL novelty bundle:

- explicit rule-definition change as distinct from statistical concept drift;
- provenance-guided localization of affected historical supervision;
- stable/candidate partitioning with stability certificates;
- selective relabeling plus incremental predictor repair;
- retaining knowledge certified stable under a known rule delta;
- versioned memory for recurring concept definitions.

Primary source:

- Ismail Lamaakal, *Provenance Guided Incremental Learning Under Evolving Concept Definitions*, arXiv:2608.23893v1, posted 2026-08-24.

Load-bearing limitation: the V1 review must read the complete paper and verify the theorem/algorithm details. This authoring delta relies only on the canonical abstract and available paper metadata for the contraction above.

## 3. Material parent addition: knowledge compilation and dynamic conditioning

Complete reasons and provenance formulas can be compiled to tractable circuit languages so repeated conditioning and satisfiability/model queries become efficient. This makes knowledge compilation a first-right-of-refusal parent for any RCL claim that shifts work from future revocation time into an offline warrant representation.

Known lower-bound work shows that natural formula/query classes can require exponential SDD/DNNF/OBDD representations; width parameters characterize important tractable regimes. Recent d-DNNF systems also support dynamic contexts through conditioning without explicit graph modification.

### Contraction

The V0 exact frontier `stored bits + coordinate queries >= number of hidden warrant bits` is an elementary special case of offline compilation versus online query trade-offs. It is not by itself a new complexity frontier.

Primary sources:

- Paul Beame and Vincent Liew, *New Limits for Knowledge Compilation and Applications to Exact Model Counting*, arXiv:1506.02639.
- Antoine Amarilli, Mikaël Monet, and Pierre Senellart, *Connecting Width and Structure in Knowledge Compilation*, LIPIcs ICDT 2018, DOI 10.4230/LIPIcs.ICDT.2018.6.
- Randal E. Bryant, Yong Kiam Tan, and Marijn J. H. Heule, *Certifying Projected Knowledge Compilation*, LIPIcs SAT 2025, DOI 10.4230/LIPIcs.SAT.2025.8.
- Jean-Marie Lagniez and Emmanuel Lonca, *decdnnf_rs: A Framework for Querying d-DNNF*, LIPIcs SAT 2026, DOI 10.4230/LIPIcs.SAT.2026.38.

## 4. Revised residual

The residual is no longer “store all warrants” or “repair from a known rule delta.” It is **prospective, jointly learned, independently certifiable revision competence**:

> Before future evidence/checker/rule/scope/authority interventions are known, learn reusable operator semantics and a warrant representation from independently checked experience. After an admitted intervention is revealed, decide exact retention, exact retraction, or explicit abstention while charging offline acquisition, compiled-state size, future proof/data queries, repair work, state recourse, collateral skill loss, false authority, and verifier/prover cost.

The strongest parent comparator now receives:

1. computational traces and the same proof-query interface;
2. an exact monotone-DNF/hidden-hypergraph learner;
3. complete-reason / prime-implicant computation;
4. knowledge compilation with the same offline time and storage budget;
5. provenance-guided rule-delta repair and versioned concept memory;
6. exact/ticketed/system-aware unlearning;
7. TMS/ATMS/self-adjusting computation;
8. proof-carrying execution and certifying compilation;
9. authority-path and source-to-forget-set resolvers;
10. a recurrent/looped Transformer implementation with identical access.

## 5. New theorem candidate: dual-certificate barrier

The next theorem is not a new architecture. It is a conditional complexity barrier for proof-carrying learning:

- safe retention has an existential surviving-warrant certificate;
- safe retraction asserts that no valid warrant survives;
- for a general NP-complete warrant-existence relation, polynomial-size polynomial-time checkable noninteractive certificates for exact safe retraction on every instance would put the complementary coNP-complete language in NP and hence imply `NP = coNP`;
- tractable compiled representations can avoid repeated hard online search, but may require exponential offline size on unrestricted classes.

This is proved in `05_DUAL_CERTIFICATE_BARRIER_V1.md`. The complexity implication is standard; possible novelty lies only in a stronger joint learning/compilation/revision theorem and its exact ORION consequence.

## 6. Revised breakthrough target: RCL-C

A publishable residual must establish more than the conditional barrier.

`RCL-C — Prospectively Learned Dual-Certificate Revision Frontier`

For a natural family of compositional operators and warrant relations:

1. prove a constructive learner jointly identifies operator semantics and a tractable revocation representation from checked traces without receiving future interventions;
2. prove held-out/reminted composition and useful retention after intervention;
3. provide positive retention certificates and independently checkable retraction/extinction certificates, or a principled abstention route;
4. characterize offline acquisition/compilation, stored bits, online proof/data queries, update time, recourse, collateral loss, false authority, and abstention;
5. prove a lower bound or impossibility for the strongest parent product at the same information and resources;
6. identify tractable structural regimes, such as bounded width, and hard regimes where compiled state or online proof must blow up;
7. contract architecture language if a recurrent Transformer realizes the same frontier.

## 7. Current terminal

```text
STATIC_CWC = PARENT_SUFFICIENT_COMPLETE_REASON
KNOWN_RULE_DELTA_PROVENANCE_REPAIR = PARENT_OWNED / STRONG_NEAR_PARENT
OFFLINE_COMPLETE_WARRANT_COMPILATION = KNOWLEDGE_COMPILATION_PARENT
RCL_0_THROUGH_RCL_6 = CORRECT_CALIBRATION_CANDIDATES_NOT_NOVELTY
RCL_DUAL_CERTIFICATE_BARRIER = HAND_PROVED_CONDITIONAL_THEOREM
RCL_C_JOINT_FRONTIER = OPEN
EXTERNAL_NOVELTY = NOT_ESTABLISHED
ARCHITECTURE_SEPARATION = NOT_SUPPORTED
```

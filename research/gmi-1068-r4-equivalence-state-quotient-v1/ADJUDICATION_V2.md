# R4-S1 post-merge adjudication

R4 V1 remains historical evidence. This successor records why its claim cannot be consumed unchanged by later rounds.

## R4-A1 — process-illegal and context-undefined were collapsed

R2 and R3 distinguish process admissibility from a partial context evaluator. R4 V1 used a total response table, so it could not express the difference between:
- a continuation absent from the process structure; and
- a legal continuation on which the context is undefined.

**Repair:** R4-S1 uses the disjoint response cases `ILLEGAL`, `UNDEFINED`, and `VALUE(o)`. A finite hostile proves that merging the first two changes the quotient.

## R4-A2 — equivalence was not enough for congruence

Equality of response signatures proves an equivalence relation. It does not by itself prove that appending a process fragment preserves equivalence.

**Repair:** the successor theorem requires an explicit registered-test precomposition map and a compatibility equation. Lean proves congruence only under that hypothesis.

## R4-A3 — parent map was too coarse

R4 V1 listed several parent theories but did not state exact specialization assumptions or counterexample boundaries.

**Repair:** `PARENT_MAP_V2.json` separates deterministic all-continuation Myhill-Nerode, deterministic output-respecting bisimulation, predictive quotients, predictive-state coordinates, causal states, classical parameter sufficiency, and Blackwell/Le Cam experiment comparison. No universal identification is retained.

## R4-A4 — representation lower bound was not exhaustively stress-tested

The separation lemma was mechanized, but the finite executable fixture did not enumerate competing representation partitions.

**Repair:** all Bell(6)=203 partitions are checked. Exactly two are sufficient; the minimum uses five representation values and has one coarsest sufficient partition up to relabeling.

## R4-A5 — nondeterministic trace/bisimulation boundary needed an executable witness

**Repair:** a finite system with `a.(b+c)` versus `a.b + a.c` has the same finite traces through the complete registered depth but is not bisimilar under the exact greatest fixed-point check.

## R4-A6 — classical and predictive sufficiency were being discussed without both directions

**Repair:** two finite countermodels are executable:
- parameter-sufficient but not future-predictive-sufficient;
- future-predictive-sufficient but not parameter-sufficient.

## R4-A7 — relabel invariance needs an actual transformed presentation

**Repair:** the successor constructs a bijective renamed table and separately mutates one transported response. The first preserves quotient block structure; the second does not.

## Reverse-dependency consequence

R5 and R6 may consume only the corrected R4-S1 semantics when they claim quotient preservation, representation minimality, or presentation invariance. Any result depending only on the weaker fact "there exists a registered context-relative quotient" may survive, but that dependency must be stated explicitly in its successor receipt.

## Claim ceiling

`GRAND_GMI_V2_R4_S1_CONTEXTUAL_RESPONSE_EQUIVALENCE_AND_CONDITIONAL_CONGRUENCE_AT_REGISTERED_FINITE_SCOPE`

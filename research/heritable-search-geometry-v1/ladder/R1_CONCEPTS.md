# HSG Lane E — R1 (set-level) lifts of concept atoms

Scope: atoms lifted from R0 point-object to R1 set-of-objects. Lane E owns R1 only
where the ladder question names R1 (G01, G08, G12, G14). Parents cited exactly as
permitted; none read from HST files (out of lane scope).

## G01 Σ_t — R1: state space as a set — LIFT_SURVIVES
- Definition. 𝓢 = 𝓛 × 𝓠 × 𝓗 × 𝓔 × 𝓡 × 𝓥 × 𝒞, the set of all tuples
  (L,Q,H,E,R,V,C). R1 replaces "the current state Σ_t" with "a state space".
- No assumption needed. Set formation is assumption-free; (i) decidability,
  (ii) finiteness, (iii) measurability are all R2/R3 concerns.
- Verdict: LIFT_SURVIVES. The set exists for any component sets; nothing to
  break. Measurability of 𝓢 is deferred to R2 (product σ-algebra, see
  R2_CONCEPTS.md).

## G08 C constitution — R1: set of constitutions — LIFT_SURVIVES
- Definition. 𝒞 = 2^Rules, the set of all constitutions as subsets of a rule
  set. With Rules countable, 𝒞 ≅ Cantor space {0,1}^Rules (compact, metrizable).
- R1 content: constitution is a *variable object* — the search may move between
  constitutions — not a fixed background constant.
- Verdict: LIFT_SURVIVES. Set formation is free; the countable-Rules case
  already carries the standard topology used at R2.
- Note: ladder for G08 stops at R2 (assumption-v removal is lane G's).

## G12 Reach_B(O) closure — R1: reachability as set closure — PARENT_SUFFICIENT
Parent #145 (transformation-semigroup closure) owns the statement: for any set O
and any semigroup S of transformations, the S-closure of O is the orbit
⋃_{n≥0} {s_n∘…∘s_1(O) : s_i ∈ S}, and orbit properties (monotone growth,
idempotence of closure, closure = generated sub-semigroup applied to O) follow
from semigroup algebra alone. Reach_B(O) is exactly this orbit with S = maps of
burden ≤ B per application. Every R1 property of Reach_B(O) — monotonicity in B,
Reach_B(O) ⊆ Reach_{B'}(O) for B ≤ B', closure under composition — is the
parent's statement re-instantiated. The R1 lift adds no new content.
- Verdict: PARENT_SUFFICIENT (parent statement taken from lane charter; not
  re-verified against HST files — reading them is out of lane scope).
- Cross-ref: assumption-xi-style completeness issues do not arise at R1; they
  enter when cones/metrics are imposed (G14).

## G14 dependency cone — R1: set-locality — PARENT_SUFFICIENT
Parent (causal DAG intervention locality, standard) owns the statement: in a DAG
with node set N and edge set Etext, intervening on A ⊆ N changes the joint law
only on the descendants of A; effects of an intervention factor through the
induced subgraph on the ancestral closure of A. The dependency cone of an update
= its parent set in the DAG; "cone-local reasoning is sound" = the parent's
intervention-locality statement verbatim, CONDITIONAL on the DAG being complete
and correct (all dependencies present as edges).
- Verdict: PARENT_SUFFICIENT — the R1 set-locality reading adds nothing beyond
  the DAG-intervention parent; R4+ metric/dynamic readings (other lanes) may.
- Sub-finding: removing cone-completeness (xi) breaks the parent's own
  precondition → unsound local reasoning; minimal counterexample in
  hostiles/G14_cone_completeness.md (recorded here because the fail belongs to
  the parent's precondition, not to a lift this lane introduces).

Lane E — verdicts R1: G01 SURVIVES, G08 SURVIVES, G12 PARENT_SUFFICIENT,
G14 PARENT_SUFFICIENT.

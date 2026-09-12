# Grand GMI Causal-Semantic and Viability Theorem V1

Status: **THEOREM + EXACT FINITE WITNESSES**  
Date: 2026-09-12

## 1. Meaning is obligation-relative causal relevance

Let a physical state be written `(x,z)` where `z` is some candidate physical detail. Call `z` **Omega-null** at the declared boundary when, for every admitted intervention on `z`, every admitted continuation/context, and every legal downstream action process, the protected obligation-response profile is unchanged.

Equivalently, all states that differ only in `z` lie in the same obligation-relative response class.

**GG29 — causal semantic nullity theorem.** If `z` is Omega-null and observing/manipulating it introduces no undeclared side channel, randomness source or resource change, then the projection forgetting `z` is response-sufficient. No GMI semantic/capability statement can require retaining `z`.

Thus information becomes semantic only when a physical distinction can causally change an obligation-relevant future under some admitted continuation.

## 2. Semantic information is not one universal scalar

For a channel `C`, the most general Grand-GMI notion of information is the change it induces in the attainable obligation/resource profile:

\[
\Delta_\Omega(C)=\mathcal A_{\Omega}(C)-\mathcal A_{\Omega}(\varnothing),
\]

understood as a partial-order/profile difference, not necessarily a real number.

At finite zero-error cut scope, layer 1 gives a canonical scalar specialization. If `H_0` is the semantic conflict hypergraph without side information and `H_C` the residual conflict hypergraph after the channel,

\[
I^{0}_\Omega(C)=\log_2\chi(H_0)-\log_2\chi(H_C).
\]

More useful side information removes conflicts, so `I^0_Omega(C) >= 0`.

**GG30 — semantic-information data processing.** Any garbling of a side-information channel can only preserve or increase the residual zero-error conflict chromatic number; it cannot increase zero-error semantic information.

The exact checker enumerates all nine nonempty-support binary side-information channels and all four deterministic binary garblings: 36/36 satisfy the monotonicity.

## 3. Viability induces an endogenous obligation

Let a system boundary include a declared constitution/viability set `V` of physical states. For horizon `T`, define

\[
\Omega_V(\tau)=1
\]

iff the protected trajectory satisfies the declared viability condition (for example remains in `V`, returns to `V`, or meets a declared continuation threshold).

Then `Omega_V` is an ordinary GMI obligation. All semantic-state, cut, transformation, resource, morphology and developmental theorems apply without introducing an external reward function.

**GG31 — viability-lift theorem.** A declared constitution predicate induces a well-typed endogenous GMI obligation.

This covers a major class of autonomous systems: self-maintenance, fault recovery, homeostatic control and population continuation can be written as viability obligations when the relevant constitution is declared.

## 4. Exact signal/viability witness

World bit `h in {0,1}` names which action preserves viability. With a perfect observation `s=h`, policy `a=s` attains the robust profile `(1,1)`. If the observation is erased to a constant, no deterministic action policy attains `(1,1)`.

The same bit therefore has exactly one bit of zero-error semantic value for this obligation:

\[
\chi(H_0)=2,\qquad \chi(H_{perfect})=1.
\]

A noisy channel whose supports overlap for both hidden states may carry Shannon information but still has zero zero-error semantic value for exact survival. Grand GMI therefore does not identify semantic information with mutual information in general.

## 5. Physics alone does not choose arbitrary goals

Consider fixed dynamics `x_{t+1}=a_t` with actions `{0,1}`. Constitution `V_0={0}` makes action `0` viability-preserving; constitution `V_1={1}` makes action `1` viability-preserving. The physical transition law is identical.

**GG32 — obligation non-identifiability theorem.** A physical process theory alone does not determine a unique nontrivial obligation or value ordering. Opposite constitutions can live on identical dynamics and induce opposite optimal actions.

This is the grand-theory version of the earlier obligation deletion countermodel. It prevents the programme from smuggling morality, preference or task choice out of bare physics.

## 6. Semantic quotient witness

For physical states `(h,z)` with hidden hazard bit `h` and irrelevant micro-detail `z`, let viability outcome under action `a` be `1[a=h]`. The complete action-response signature depends only on `h`, never on `z`. Across all 16 binary response tables that are functions only of `(h,a)`, the two `z` variants of every `h` are exactly response-equivalent.

Thus the semantic quotient removes physical detail that cannot matter to the obligation while retaining the hazard distinction that can.

## 7. Relation to biological/evolutionary semantics

If a population-level lifted process declares persistence/reproduction/constitution predicates, those predicates induce viability obligations on the lifted morphology/population state. Layer 2 then applies recursively.

This does **not** assert one universal biological fitness scalar, nor that every organism optimizes survival at every timescale. It states a conditional reduction: once a continuation/constitution criterion is part of the system boundary, its causal semantic information is derived exactly by the same GMI machinery.

## 8. Grand-GMI consequence

The theory now separates three things that are often conflated:

1. **physical information** — distinctions present in the substrate;
2. **semantic information** — distinctions causally relevant to a declared obligation;
3. **value/obligation origin** — externally declared for engineered tasks, or conditionally induced by a declared constitution/viability predicate for autonomous systems.

No architecture, probability prior, utility scalar or neural representation is fundamental to this separation.
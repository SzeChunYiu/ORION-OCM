# EB-F0 Definitions (frozen by FREEZE_V1.json)

Owner: #296. Outcome-neutral: these objects do not decide whether intelligence
is individual, collective, species-level or cultural.

Framework is EXPLICITLY_NON_FINAL (RGC). Stronger mathematics, counterexamples
or evidence supersede via append-only freeze amendment.

## 1. World state

At simulation time `t`:

```text
W_t = (E_t, μ_t, Γ_t, H_t ; P, C)
```

- `E_t` ecological state (space/network, resources, hazards, niche, shock).
- `μ_t` finite population measure over extant cells and their states.
  Not a pre-labelled species list.
- `Γ_t` time-varying interaction/communication/assembly hypergraph.
- `H_t` append-only world/lineage/cultural event history.
- `P` immutable world physics and update law.
- `C` immutable external OCM constitution/checker, outside every genome
  and write set.

An extant cell `i` has bounded state

```text
x_i(t) = (g_i, F_i, O_i, Π_i, h_i, r_i, q_i, ℓ_i)
```

`C` is not copied into `x_i`. No species, group, culture or collective is
primitive. Those are observer-side coarse-grainings induced from genealogy,
interaction, reproduction and cognition.

## 2. Dynamics as independently ablatable kernels

```text
K_world      ecology/resource transition
K_senseact   legal sensing/action and resource effects
K_learn      within-lifetime cognitive update
K_social     horizontal/oblique information or method transfer
K_assemble   formation/fission/fusion of interaction groups
K_birthdeath survival/reproduction/death
K_mut        architectural/genetic variation
K_inherit    vertical inheritance of permitted state/methods
```

Composed kernel: `Law(W_{t+1} | W_t)`. Deterministic worlds are degenerate
kernels. Every kernel declares randomness source, **read set**, writable state,
resource cost and information channel. Ablating one kernel must not rewrite
unrelated physics.

The read set is not optional bookkeeping. The section 3 obligation is that
protected assay state is not an *ancestor* of any birth/death or
resource-transition decision, and ancestry is reachability over both halves of
the edge relation. A declaration carrying writes alone has no incoming edges,
so every ancestor set collapses to the sink itself and the check returns PASS
for every world including a leaking one. See
`WORLD_STATE_AND_DYNAMICS_V1_AMEND_1.json` for the read sets and for `K_assay`,
the observer-side kernel that writes the protected names, and
`NONINTERFERENCE_CHECK_SPEC_V1.json` for the decidable form of the predicate.
An unresolved read or write set yields `CANNOT_CHECK`, never `PASS`.

## 3. Endogenous selection

Birth/death/reproduction arise from `P` and resource accounting only.
Realized reproductive contribution `w_i` is an **observer statistic**, not
an intelligence reward.

Primary law: protected assay state is not an ancestor of any
birth/death/resource-transition decision in the write/causal graph.
Failure of this condition invalidates spontaneous/general cognition claims
for that run. `ASSAY_SELECTED_CONTROL` is a separately frozen treatment.

## 4. Transmission channels

```text
I_gen     architectural/genetic inheritance
I_epi     permitted vertical epistemic/method inheritance
I_C       C-verified admitted inheritance
I_h       horizontal peer transfer
I_o       oblique/non-parent transfer
I_pub     persistent public/cultural artifacts
```

Every transferred object `z` records source, target, transform, warrant,
scope, verification, bytes, communication/retrieval/maintenance cost, and
later causal use. Transfer may return `CANNOT_TRANSLATE` / `CANNOT_VERIFY`.
No monotonicity of social learning without the optional-use/zero-hidden-cost
assumptions (BIO-T4; HST-T01 / G13 overhead hostile).

## 5. No privileged unit of intelligence

Let `L` range over observer-side candidate coarse-grainings (individual,
temporary group, persistent group, lineage, communication community,
cultural pool, or another data-supported partition). The name list is not
exhaustive and is not a theorem.

For each `L` define `φ_L : microstate/history -> macrostate_L` and test:

1. predictive sufficiency
2. causal autonomy/residual under resource-matched interventions
3. heredity/persistence of the candidate macro-unit

Output is a correspondence/Pareto set, possibly empty or incomparable.
There is no frozen `L*`.

## 6. Multilevel selection

Where a nested partition is justified, use the Price identity (parent:
Price 1970/1972) to separate within-unit and between-unit change.
A `MajorTransition` claim requires higher-level reproduction, heritable
variation, differential persistence, division of labour/interdependence and
conflict mediation — not merely a graph community.

## 7. Evolvability

Parent: HST-T10. For state `a` in ecology `e`, legal descendant kernel
`K_t(da'|a,e,H_t)` and protected useful-descendant set `U_t(e,a)`:

```text
Ev_t(a,e) = K_t(U_t(e,a) | a,e,H_t)
τ_U       = first hitting time of U
```

Never equate fitness with evolvability. Ev ↔ hitting-time identities hold
only under explicit kernel assumptions (BIO-T11).

## 8. Cultural accumulation

Observer-side `H^cult_t` is the reconstructible graph of socially
transmissible objects and events, separate from `C`. Cumulative culture
requires repeated innovation + transmission + retention + causally useful
modification across generations. Byte growth is not sufficient (BIO-T13).

## 9. Protected assays and future-domain bridge

Assay families are distributions over obligations, not one IQ scalar.
For target domain `T` after evolution is frozen:

```text
ΔB_T(H) = B_T(RESET) - B_T(CONTINUED(H))
```

full burden vector. The biosphere **never proves** language, mathematics or
science capability. Evidence chain:

```text
history H
 -> protected ecological phenotype
 -> freeze H
 -> fresh T (language / formal maths / coding / science)
 -> CONTINUED(H) vs RESET vs strongest matched parent
 -> inherited-object / channel knockouts
 -> ΔB_T and retention/negative transfer
```

## 10. Resource-matched organization residual

For any candidate `L`, compare at matched total compute, memory, sensory
information, action opportunities and external knowledge:

```text
observed_gain = resource_pooling_gain
              + communication/organization residual
              + specialization/composition residual
              - coordination/maintenance cost
```

No class is privileged.

## 11. Generator-support ceiling

Search cannot discover responses to opportunities the world representation
cannot express. Every open-endedness/evolvability claim carries generator/VM
support as an assumption (BIO-T3).

## 12. Open-endedness claim ceiling

Finite deterministic state spaces eventually recur (BIO-T2 / HST-T12).
Finite stochastic spaces do not license unbounded novelty from a long
trajectory (HST-T13). Report horizon-scoped novelty/evolvability plus
recurrence ceilings. Unbounded open-endedness is outside finite-run scope.

## 13. What this package deliberately does not define

- a privileged unit of intelligence `L*`
- fitness as an intelligence/language/math score
- a universal best inheritance/social-learning mode
- OPEN_ENDED / AGI / general intelligence as a biosphere terminal

# Causal identifiability boundary — CAU-1–5

Status: **THEOREM AT DECLARED FINITE SCOPE + EXACT RATIONAL WITNESSES**
Date: 2026-09-13

Ledger item 8. The statistical mechanism is **not** claimed novel: observational
non-identifiability, the back-door criterion and do-calculus are established
(Pearl 2009; Spirtes–Glymour–Scheines 2000; Bareinboim–Pearl 2016). The GMI
contribution is the explicit interface: when an *observational* evidence stream
admitted by `I` does and does not determine an obligation `O` stated over
interventional quantities, with all probe costs charged by `R`.

## Parents (cite, do not rewrite)

| Parent | Disposition |
|---|---|
| `CAUSAL_SEMANTIC_VIABILITY_THEOREM_V1.md` GG29/GG30 | ADOPT Ω-nullity and `Δ_Ω(C)`. Meaning is obligation-relative causal relevance; this capsule adds *when observation fixes it*. |
| master §1.7 | ADOPT "semantic information only insofar as interventions can change an obligation-relevant attainable profile". |
| `research/g6-intervention-lab-v1/` | ADOPT paid probe transcripts as the cost model. REJECT reuse of its synthetic plant; its ceiling is a bounded plant, not a boundary theorem. |
| `research/g2-strategy-identifiability-v1/` | ADOPT the exact finite microscope discipline. REJECT extending its locked G4.4 box; that capsule states preconditions, not a general boundary. |
| `MINIMAL_AXIOM_FREEZE_V1.md` A1/A2/A4 | ADOPT nonanticipation, scoped quantification and charged composition. |

## 1. Register

A finite causal register is `M = (V, pa, F, P_U)`: finite variables `V`, parent
map `pa`, deterministic structural maps `F = {f_v}` and a product law `P_U` over
exogenous noise. `M` induces the observational law `P_M` and, for any assignment
`do(X = x)`, the interventional law `P_M^{do(X=x)}` obtained by replacing `f_X`
with the constant `x` and leaving every other map and `P_U` unchanged.

An **evidence stream** is the sequence of quantities `I` actually admits. A
*purely observational* stream admits only draws from `P_M`.

## 2. CAU-1 — observational equivalence does not determine interventional law

> **CAU-1.** There exist finite registers `M0, M1` with `P_{M0} = P_{M1}` on
> every observable variable, yet `P_{M0}^{do(X=1)}(Y=1) ≠ P_{M1}^{do(X=1)}(Y=1)`.
> Consequently no learner restricted to a purely observational stream can
> determine the interventional target, whatever its sample size or compute.

Proof. Exhibit the confounded/unconfounded pair of §6 and apply the two-world
argument of LMT-5: the learner-visible histories have identical law, so its
terminal output has identical law, and it cannot be correct in both worlds. The
witness is exact and rational; no asymptotics are used. QED.

This is a statement about the *stream*, not about sample size. A1 is what makes
it bite: the choice at each step is `F_{t-1}`-measurable, and `F_t` never
contains an interventional draw that `I` did not admit.

## 3. CAU-2 — what observation does fix

Observation fixes the law `P_M` and hence every functional of it, including the
Markov equivalence class of compatible graphs. It therefore fixes the
interventional target **only when** that target is constant on the equivalence
class. Reporting an interventional number from observational data alone is a
scope violation of A2 unless CAU-3's premises are discharged.

`Δ_Ω` and `I⁰_Ω` of GG29/GG30 are defined through admitted interventions, so
they inherit exactly this boundary: a channel's semantic information is not
estimable from passive observation without the same premises.

## 4. CAU-3 — sufficient premises, and their charge

> **CAU-3 (back-door).** If `Z` satisfies the back-door criterion for `(X, Y)`
> in `M` — no member of `Z` is a descendant of `X`, and `Z` blocks every
> back-door path — then
> `P^{do(X=x)}(Y) = Σ_z P(Y | X=x, Z=z) P(Z=z)`,
> every term of which is observational.
>
> **CAU-3b (randomization).** If `I` admits an exogenous randomized assignment
> of `X` independent of `U`, then `P(Y | X=x)` under that regime equals
> `P^{do(X=x)}(Y)` directly.

Both are premises, not conclusions. Under A4 the probes that establish them are
charged: a randomized assignment consumes admitted interventions from `Θ` and
their cost enters `R`. Identifiability is therefore **purchased**, never free,
and the purchase is what CAU-1 proves cannot be skipped.

## 5. CAU-4 — interventions are admitted operations

`do(·)` is meaningful only for assignments `I` actually admits. An intervention
outside `Θ` is not a cheaper route to the same claim; it is a different declared
problem under A2. Composing an identified effect with downstream components
requires GAC-5's discharged interfaces: an identified `P^{do}` is a *local*
guarantee and does not compose by itself.

## 6. Exact witnesses

**W1 — confounded vs unconfounded.** `U ~ Bernoulli(1/2)`.
*World 0:* `X = U`, `Y = U`. *World 1:* `X = U`, `Y = X`.
Both give the same observational law: `P(X=1,Y=1) = P(X=0,Y=0) = 1/2`.
Under `do(X=1)`: world 0 leaves `Y = U`, so `P(Y=1) = 1/2`; world 1 gives
`P(Y=1) = 1`. Identical observation, different intervention: **1/2 ≠ 1**.

**W2 — back-door recovery.** With `Z = U` observed, the back-door adjustment
returns `1/2` in world 0 and `1` in world 1, matching the truth in each. The
premise, not more data, is what restores identifiability.

**W3 — adjusting on a descendant is not safe.** A third register: `X ~ Bernoulli(1/2)`
exogenous, `Y = X`, and `Z = Y`, so `Z` is a descendant of `X` and violates the
back-door criterion. The truth is `P(Y=1 | do(X=1)) = 1`, but the adjustment
formula applied to `Z` returns
`Σ_z P(Y=1 | X=1, Z=z) P(Z=z) = P(Y=1) = 1/2`.
Exactly `1/2 ≠ 1`, so "adjust for everything observed" is refused: the criterion's
exclusion of descendants is load-bearing, not decorative.

Note on W1's learner bound: the frozen check that `max_q min(1-q, q) = 1/2` is an
arithmetic witness of the two-world bound, not a proof of CAU-1. The proof is the
identical-visible-law argument of §2.

## 7. Failure taxonomy

| Failure | Symptom | Repair |
|---|---|---|
| unmeasured confounding | two registers match observationally, differ under `do` | admit an intervention or a valid adjustment set |
| bad control | adjustment set contains a descendant/collider | re-derive the set from the graph |
| regime shift | assignment law changes between evidence and deployment | re-declare `E`; transport premise |
| cost denial | identifiability asserted without charging probes | charge under A4 |

## 8. Falsifiers and boundaries

CAU-1 is falsified by a purely observational learner that determines the
interventional target in both W1 worlds. CAU-3 is falsified by a register
satisfying the back-door premises whose adjustment formula disagrees with its
own interventional law.

This capsule does **not** establish: graph discovery from data, identifiability
of arbitrary queries, transportability across environments, correctness of any
physical randomizer, finite-sample rates, or that an identified effect is
obligation-optimal. Those remain separate obligations.

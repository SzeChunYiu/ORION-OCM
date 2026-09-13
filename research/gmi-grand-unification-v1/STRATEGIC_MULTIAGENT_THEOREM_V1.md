# Grand GMI Strategic Multi-Agent Theorem V1

Status: **FORMAL REDUCTION + FINITE EXACT SECTOR**  
Date: 2026-09-13  
Base: `main@6ed341cd6809e381db470947d3c1f004efc61c57`

## 0. Purpose

Grand GMI already reduces cooperative distributed machines to one product-state process with internal semantic cuts. A genuinely global theory must also cover systems whose components have **different or conflicting obligations**. This document shows that strategic interaction requires no new architectural primitive: it is the same causal-process theory with an indexed family of obligations and unilateral-intervention probes.

The theorem does **not** claim that physics selects one universal game-theoretic solution concept. Where obligations conflict, equilibrium existence and equilibrium selection depend on declared strategy classes and any optional scalarization/preferences.

**Identifier scope.** The historical section IDs `GG42`–`GG45` below also occur
in `QUANTUM_PROCESS_INSTANTIATION_THEOREM_V1.md`. Cite the source-qualified
form `strategic:GG42` (versus `quantum:GG42`), or the distinct `GG-S*` IDs in
`CLAIM_LEDGER_STRATEGIC_V1.md`. Existing IDs and receipts are retained; these
are separate claims, not alternate names for one theorem.

## 1. Strategic GMI problem

A finite strategic GMI problem is

\[
\mathfrak G_{strat}=(\mathbf P,\mathcal E,\{\Omega_i\}_{i=1}^n,\Theta,\rho,\mathcal D,\epsilon),
\]

where the master objects retain their existing meanings and `Omega_i` is the obligation of agent `i`. A joint machine induces a joint strategy/kernel `sigma=(sigma_1,...,sigma_n)` and a protected trace law.

For each agent `i`, ecology coordinate `e`, and admitted unilateral deviation `d_i`, define the deviation-regret coordinate

\[
r_{i,e,d_i}(\sigma)
= L_{i,e}(\sigma)-L_{i,e}(d_i,\sigma_{-i}),
\]

with losses minimized. No distribution over ecologies is required.

The complete strategic signature is the vector

\[
\mathcal R(\sigma)=\big(r_{i,e,d_i}(\sigma)\big)_{i,e,d_i}
\]

together with ordinary Grand-GMI capability/resource coordinates.

## 2. GG40 — equilibrium is simultaneous local obligation satisfaction

Fix a strategy class `K`. Define the local strategic obligation for agent `i` at opponents' strategy `sigma_-i` as

\[
\Gamma_i(\sigma_{-i})
=\{\sigma_i: L_i(\sigma_i,\sigma_{-i})\le L_i(d_i,\sigma_{-i})\ \forall d_i\in K_i\}.
\]

Then

\[
\sigma_i\in\Gamma_i(\sigma_{-i})\ \forall i
\]

if and only if `sigma` is a Nash equilibrium for the declared scalar loss game/strategy class.

Thus Nash equilibrium is not a new intelligence primitive. It is a fixed point of simultaneously satisfied local control obligations under unilateral-intervention probes.

**Parent boundary.** Existence results for finite mixed Nash equilibria are classical game theory; Grand GMI claims the reduction/typing, not invention of Nash's theorem.

## 3. GG41 — strategic semantic-state refinement

For agent `i`, histories `h,h'` are strategically semantically equivalent only when every obligation-relevant future response agrees under:

- every admitted ecology,
- every admitted own continuation,
- every admitted strategy/intervention of the other agents,
- every registered tolerance/resource context.

Adding opponent interventions can therefore only **refine** the single-agent/passive semantic quotient. There is a canonical surjection from the strategically finer quotient to every quotient obtained by deleting strategic probes.

This is exactly the semantic-state refinement theorem applied to a larger probe family.

## 4. GG42 — strategic semantic cuts

Inter-agent communication defines internal causal interfaces. At a classical
deterministic **one-way** interface `c:X -> Z`, `d:Z x Y -> A`, the SC-1
hypergraph bound applies to the complete encoded message. A pairwise clique
bound applies when the required actions conflict pairwise under the declared
side information; general set-valued obligations use the full hypergraph.

Negotiation and other interactive protocols may first reveal receiver
information to the sender. Their later messages can depend on that feedback,
so a one-way hypergraph on the original sender input cannot be reused without
checking the information pattern. Re-register the actual later cut and its
remaining obligation, or prove a bound for the whole interactive class. The
INDEX witness in `COMPOSITIONAL_DISTRIBUTED_GMI_THEOREM_V1.md` §2 gives four
bits one-way versus three bits with feedback for the same final obligation.

Therefore coordination, signaling, negotiation messages, shared blackboards, market prices, and opponent-model summaries are all instances of the same obligation-relative cut requirement.

No separate "communication intelligence" primitive is required.

## 5. GG43 — prior-free strategic frontier

For a finite registered strategic problem, the set

\[
\mathcal A_{strat}
=\{(\mathcal R(\sigma),Q(\sigma),\rho(\sigma)): \sigma\in K\}
\]

is exactly enumerable, with an exactly computable nondominated subset, under
the following effective finite assumptions: `K` is a finite register with a
terminating enumeration; all admitted ecology and unilateral-deviation
coordinates form finite registers; loss, capability and resource coordinates
are effectively evaluable; and every equality/order comparison needed for
regret, hard gates and dominance has a total exact decision procedure. Exact
rational coordinates suffice. Any larger number representation must supply
the required procedures. These are the exact-arithmetic conditions of the
finite operational theorem, not consequences of the cardinality of `K`.
The coordinatewise nondominated subset is the **strategic GMI frontier**.

To compute it, evaluate each registered strategy profile and deviation, form
the finite regret vectors, then compare every pair of profiles. This terminates
under the stated assumptions. An infinite enumerable strategy family does
not inherit this finite exhaustion algorithm.

A zero-regret equilibrium, when it exists, is a special point satisfying

\[
r_{i,e,d_i}(\sigma)\le 0\quad\forall i,e,d_i.
\]

When no such point exists, the theory does not manufacture an equilibrium by silently introducing a prior or utility aggregation. It returns the nondominated regret/resource frontier.

**Exact-comparison boundary.** One player with two actions of losses `0,x_P`
and constant capability/resource coordinates is already sufficient: let
`x_P=2^{-t}` if program `P` first halts at step
`t>=1`, and zero otherwise. The real `x_P` is uniformly computable to arbitrary
precision, but action 1 has zero regret exactly when `x_P=0`. A total exact
zero-regret classifier over these representations would decide nonhalting.
Finite strategy count alone therefore does not make exact equilibrium or
frontier membership decidable. This is the same arithmetic boundary as
`../machine-intelligence-morphogenesis-v1/GMI_OPERATIONAL_COMPLETENESS_THEOREM_V1.md`
§7, not an additional failure of finite rational game theory. See
`INTERACTIVE_CUT_SCOPE_CORRECTION_V1.md` for its strategic specialization.

## 6. GG44 — ecology-robust equilibrium need not exist

Let two ecologies induce opposite dominant actions for both players:

- `e0`: each player uniquely prefers action `0` regardless of the other player;
- `e1`: each player uniquely prefers action `1` regardless of the other player.

The unique equilibrium is `(0,0)` in `e0` and `(1,1)` in `e1`. Their intersection is empty.

Hence a requirement that one joint action be an exact equilibrium in **every** admitted ecology can be inconsistent. This is the strategic analogue of the prior-free no-universal-optimum boundary.

Any Bayesian expected-game selector, weighted social welfare, lexicographic rule, minimax rule, or equilibrium refinement is therefore an **optional selector** unless its ordering is itself part of the declared obligation.

## 7. GG45 — cooperative teams are a special case, not the general case

The layer-4 team-centralization theorem is recovered when the agents share one joint obligation and are judged only by external team traces/resources. Conflicting obligations require retaining the per-agent regret coordinates above; collapsing them to one team scalar can erase genuine strategic distinctions.

Thus:

\[
\text{cooperative distributed GMI}\subset\text{strategic multi-agent GMI}.
\]

## 8. Exact finite evidence

`grand_gmi_strategic_checks_v1.py` performs deterministic exhaustive checks:

1. all `3^8 = 6,561` two-player `2x2` loss games with loss entries in `{0,1,2}`: profiles satisfying both local best-response obligations are exactly the pure Nash profiles;
2. the corpus includes games with no pure equilibrium, so existence is not silently assumed;
3. `196,608` strategic semantic-refinement checks verify that adding opponent/probe coordinates only refines semantic partitions;
4. an explicit two-ecology dominant-action construction has disjoint exact-equilibrium sets;
5. a one-bit signaling coordination witness is checked against the semantic-cut lower bound.

## 9. Claim ceiling

This theorem establishes a Grand-GMI reduction of finite strategic interaction, adversarial behavior and conflicting local objectives. It does not establish:

- one universal equilibrium-selection rule;
- universal mixed-equilibrium existence under vector-valued prior-free ecology obligations;
- human social preference or moral values from physics;
- bargaining/fairness axioms without declaring them;
- computationally efficient equilibrium finding for unrestricted games.

Those boundaries are necessary consequences of the architecture-free programme, not omissions to be hidden.

# GMI Candidate-Domain Reduction Theorems v2

Status: **HOSTILE PARENT-REDUCTION HARDENING / NOVELTY PRUNING**

Status date: 2026-09-12.

Purpose:

> Prove when unusual classical carriers fail to establish a new structural/resource domain because a strong program/distributed parent can reproduce the same semantics and asymptotic lifecycle law when granted the same primitive substrate capabilities.

The comparison must be fair: a candidate does not earn domain status merely because its parent is artificially denied the parallelism, locality, memory or actuator primitives the candidate receives.

---

# 1. Finite local-field/cellular systems reduce to distributed local programs

Consider a synchronous system on graph `G=(V,E)` of bounded degree. Each node has state in finite set `S`. At every round, node `v` updates by a fixed finite rule

\[
s_v(t+1)=F\big(s_v(t),(s_u(t))_{u\in N(v)}\big).
\]

## Theorem CR-1 — round-preserving distributed-program simulation

A distributed message-passing program running one process per node can simulate one cellular/local-field round with:

```text
O(1) local program-state overhead per node (for fixed finite S,F)
O(1) messages per incident edge per round
one distributed synchronization/update round per candidate round
```

up to fixed encoding constants.

### Proof

Each node sends its finite state encoding to neighbors, applies the finite transition table `F`, and writes the next finite state. Since degree, state alphabet and rule are fixed, encoding and local computation overhead are bounded by constants. QED.

### Consequence

A finite-state cellular/local-field carrier is not a distinct H1/H2 domain from a distributed-program parent when both receive the same topology and local communication substrate.

Its locality, regeneration and damage-tolerance laws can still define an important **kingdom/mechanism class**.

### Escape condition

A stronger domain claim requires a primitive not preserved by this reduction, for example a physical field operation whose relevant time/energy/precision law cannot be matched by the registered distributed-program substrate.

---

# 2. Explicit finite constructor ecologies reduce to distributed programs with the same construction primitive

Let each active module carry one of finitely many constructor states. A local constructor rule maps available neighboring/material state to a finite set of construction actions, including creating/activating another module.

## Theorem CR-2 — construction-round simulation under matched actuators

Suppose the program parent is granted the same construction actuator primitive and the same parallel set of active module locations. Then every synchronous constructor round can be simulated by a distributed program round with fixed per-module rule-interpreter overhead.

Thus any parallel replication schedule available to the constructor system is also available to the matched program realization.

### Important correction

A comparison of

```text
self-replicating constructor: O(log N) parallel growth rounds
single centralized builder:   Omega(N) build rounds
```

is **not** a domain separation if the parent was unfairly restricted to one builder while the candidate received exponentially growing parallel builders.

A distributed program using the same replicated construction ports can issue the same local construction actions in the same asymptotic number of rounds.

### Consequence

Constructive closure remains a necessary developmental-state variable, but explicit finite constructor rules do not establish H1/H2 domain novelty under matched physical construction primitives.

### Remaining possible niche

Only genuinely different primitive physics/material self-assembly whose lifecycle law is unavailable to the parent substrate can escape this reduction; that would need to be tested as a substrate/physical-computation distinction, not inferred from the word `constructor`.

---

# 3. Hyperdimensional/vector-symbolic algebra reduces to ordinary vector programs asymptotically

Consider dimension `d` hypervectors with primitive operations such as componentwise binding, bundling/addition, fixed permutation and similarity.

## Theorem CR-3 — array-program upper bound

On a classical random-access/vector machine, the standard componentwise implementations satisfy:

```text
binding:        O(d)
bundling:       O(d) per added vector
permutation:    O(d) materialized, or O(1) metadata + indexed access when permutation is implicit
similarity:     O(d)
```

with `O(d)` stored state per hypervector.

Therefore the usual finite-dimensional HDC/VSA algebra has a direct ordinary coefficient/array-program realization with the same linear-in-d asymptotic state and operation complexity.

### Consequence

HDC/VSA is not a new H2/H3 classical computational domain merely because its algebra is unusual. Its scientific value lies in robustness/capacity/learning laws, hardware mapping and compositional convenience.

An H1 constant-factor/energy distinction remains substrate-dependent.

---

# 4. Finite population-hereditary systems reduce to explicit population programs

Let a population contain `N` individuals, each with finite genotype/state. One generation applies computable fitness evaluation, selection, mutation/recombination and replacement rules.

## Theorem CR-4 — generation-preserving population simulation

An ordinary program storing the explicit population can simulate one generation by applying the same finite/computable operators to the `N` individuals, with burden proportional to the candidate's own explicit fitness/update work up to representation overhead.

If the candidate evaluates individuals in parallel, the fair parent comparison must permit matched parallel processors before claiming wall-clock separation.

### Consequence

Hereditary population state can be an indispensable developmental state and a useful search kingdom, but finite classical evolutionary dynamics do not by themselves establish a new H2/H3 domain.

A domain-level claim would require an irreducible physical/population primitive with a lifecycle law outside the matched computational parent.

---

# 5. Event/partial-order, quotient/invariant and finite relational systems

Previous hardening already established:

```text
event/partial-order state:
    finite symbolic relational representation gives the same compression over interleaving enumeration

quotient/invariant state:
    direct instance of GMI semantic quotient theory

finite relational/local-global constraints:
    strong graph/CSP/linear-algebra parents reproduce registered exact laws
```

These remain mechanisms/kingdoms unless a new parent-relative resource lower bound is found.

---

# 6. General matched-primitive reduction principle

## Theorem schema CR-G

Let candidate system `C` have:

1. finite/effectively encodable local state;
2. computable local transition/operator rules;
3. explicit primitive communication/actuation operations `P`;
4. a registered parallel schedule.

If parent program family `D` is granted the same primitive operations `P`, topology and parallel schedule, then an interpreter for the fixed candidate rule set can simulate `C` with fixed local interpretation overhead plus the same asymptotic primitive-operation count.

Therefore any claimed resource separation must identify a primitive whose lifecycle semantics are **not** preserved under the parent registration.

This prevents hidden substrate denial from masquerading as cognitive-domain novelty.

---

# 7. Revised status of classical candidate domains

At current hardened scope:

```text
relational local/global        mechanism/kingdom; strong symbolic reduction
constructive closure           developmental-state mechanism; matched-actuator reduction
local field/cellular           distributed/dynamical kingdom under matched topology
hyperdimensional/VSA           algebraic kingdom; ordinary vector-program reduction
population/hereditary          search/development kingdom; explicit population reduction
event partial order            symbolic concurrency kingdom
quotient/invariant             core semantic-quotient mechanism
energy/relaxation              dynamical/search kingdom unless physical substrate law separates
reaction-network               dynamical/physical kingdom unless native chemistry gives unmatched lifecycle law
```

No new H2/H3 ordinary-classical domain is established by these candidates.

---

# 8. What remains genuinely promising

The domain programme should now focus less on renaming classical algorithms and more on possible **primitive-resource separations**:

```text
nonclassical information carriers (quantum calibration)
physical/analog fields with rigorously measured precision-energy-time laws
in-situ molecular/chemical computation where sensing/computation/actuation cannot be fairly digitized at matched burden
unknown carriers recovered by neutral grammar whose primitive law cannot be compiled within the frozen overhead class
```

Even here, substrate repricing alone is not sufficient; the candidate must change a registered achievable capability/resource frontier.

---

# 9. Claim ceiling

These reductions deliberately make the novelty bar harder. They do not say the reduced paradigms are unimportant. They say:

> A useful mechanism, architecture family, or kingdom is not automatically a new domain when a matched parent reproduces its semantic and asymptotic primitive-operation law.

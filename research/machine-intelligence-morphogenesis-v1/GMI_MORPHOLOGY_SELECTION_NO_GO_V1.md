# GMI Morphology Selection No-Go v1

Status: **FORMAL IDENTIFIABILITY BOUND — PARENT-OWNED DECISION/RESOURCE LOGIC**

Refs: `GMI_REALIZATION_DEMAND_SIGNATURE_V0.md`, `GMI_DEVELOPMENTAL_REALIZATION_PRINCIPLE_V1.md`, `GMI_CROSS_PARADIGM_REALIZATION_NORMAL_FORM_V1.md`.

## 1. Question

Can the obligation-side demand signature alone determine which form of machine intelligence should emerge?

That is, can there be a universal rule

\[
f(\Xi(\Omega))=M^*
\]

that names the optimal morphology using only obligation properties?

In general, no.

The reason is simple but load-bearing: optimality also depends on the available realizations' response/cost functions, the physical/resource price regime, and the bounded process used to discover/build them.

---

# 2. Fixed obligation, opposite winners

Fix one semantic obligation `Omega` and therefore one exact demand signature

\[
\Xi(\Omega)=\xi.
\]

Let two exact semantically adequate realizations be `M_A` and `M_B`.

Suppose at resource regime `r_1` their complete scalarized lifetime costs are

```text
C(M_A | Omega, r_1) = 5
C(M_B | Omega, r_1) = 10.
```

Then `M_A` is preferred.

At another legal resource/hardware regime `r_2`, keep the semantic obligation and demand signature unchanged but let

```text
C(M_A | Omega, r_2) = 20
C(M_B | Omega, r_2) = 8.
```

Then `M_B` is preferred.

Therefore no function of `Xi(Omega)` alone can identify the winner across both regimes.

This is not deep new mathematics. It is a direct consequence of ordinary decision/resource dependence.

---

# 3. GMI-MS1 — demand-only non-identifiability

**Statement.**

Without a fixed realization candidate class and fixed realization-response/resource semantics, the obligation-side signature `Xi(Omega)` is insufficient to determine a unique optimal morphology.

A valid morphology selection object must include at least:

```text
Omega / Xi(Omega)
available realization family M_set
realization response/burden functions
resource/price regime
semantic admissibility constraints
```

and, for what is actually discovered rather than normatively best:

```text
morphogenetic proposal/search process Gamma
morphogenesis budget/history
```

---

# 4. Corrected normative phase law

The normative lifetime frontier is therefore a relation of the form

\[
\mathcal F
=
\mathcal F(\Omega,\mathcal M_{avail},\rho,\pi),
\]

where:

- `Omega` / `Xi` describes the obligation;
- `M_avail` is the available realization class;
- `rho` supplies complete realization resource semantics;
- `pi` is any prospectively declared resource price/constraint regime when scalar choice is required.

Prefer Pareto frontiers before scalar prices.

The theory should predict **realization properties/frontier transitions**, not an architecture label in isolation.

---

# 5. Corrected observed morphogenesis law

The morphology actually obtained by a bounded developmental process depends additionally on search/discovery:

\[
M_{found}
\sim
\Gamma(
  \mathcal F,
  H_{dev},
  B_{discover},
  L_{morph},
  Q_{morph}
).
\]

In words:

```text
normatively attractive morphology
!=
morphology reachable/discoverable under a bounded search
```

unless the search process is proven complete for that registered candidate space.

AutoML/NAS/evolution/program search are direct parents for this distinction.

---

# 6. Hardware is part of realization economics, not semantics

The same semantic machine may rank differently on different substrates.

Examples:

```text
dense matrix accelerator
CPU with branch-heavy symbolic search
memory-constrained edge device
high-latency verifier/service
high communication-cost distributed system
```

Hardware can affect:

```text
training/build cost
serving latency/energy
memory bandwidth
parallelism
communication
update/retraining cost
```

It does not by itself change which semantic distinctions the obligation requires.

Thus:

```text
semantic quotient
!=
physical realization frontier.
```

---

# 7. Available-family dependence

Even under a fixed price regime, the best morphology depends on what realization families are legally/technically available.

If the candidate class excludes the globally best implementation, the optimal member of the restricted class is only a conditional optimum.

Therefore all claims must name the comparator/candidate class.

Forbidden wording:

```text
THE optimal form of intelligence
```

unless the candidate class is complete under a justified formal scope.

Preferred wording:

```text
Pareto-optimal among the registered realization class
```

or

```text
frontier within the registered morphology family set.
```

---

# 8. Relation to algorithm selection

Rice-style algorithm selection already formalizes instance/problem features plus an algorithm portfolio and performance model.

GMI must not rename that as a universal morphology law.

The Track-B residual is only stronger if the same semantic/demand coordinates:

```text
1. retain their meaning across materially different realization families;
2. predict realization properties before architecture labels;
3. survive family-held-out tests;
4. remain useful after strongest family-native predictors receive first refusal;
5. extend from fixed portfolio selection to developmental/morphogenetic acquisition economics.
```

Otherwise terminal:

```text
ALGORITHM_SELECTION_PARENT_SUFFICIENT.
```

---

# 9. Relation to resource rationality / rate distortion

Resource-rational and information-theoretic bounded-rationality theories already optimize task utility/distortion under information/computation costs and can derive efficiency frontiers/hierarchies under their assumptions.

GMI adopts those results where the mapping is faithful.

The remaining problem is not “resources matter”.

It is whether a common obligation/realization semantics can connect those optimality principles to:

```text
learning/update laws
persistent developmental state
morphology discovery cost
retention/plasticity
heterogeneous verification
cross-paradigm phase prediction
```

without changing definitions per family.

---

# 10. Exact finite hostile

`gmi_morphology_selection_no_go.py` freezes one semantic obligation and two semantically admissible realization labels `A` and `B`.

It demonstrates three independent non-identifiability mechanisms:

## Resource-price reversal

Same obligation and raw burden vectors, different nonnegative price vectors:

```text
price regime p1 -> A wins
price regime p2 -> B wins.
```

## Hardware/response reversal

Same obligation and same price vector, but the legal physical realization costs of A/B change:

```text
hardware h1 -> A wins
hardware h2 -> B wins.
```

## Search reachability failure

Normative optimum `C` exists in the registered candidate class but a bounded proposal sequence cannot reach it before budget exhaustion:

```text
normative winner = C
found winner = B.
```

These are calibration hostiles, not machine-intelligence discoveries.

---

# 11. Revised phase-law target

The scientifically meaningful target is therefore not

\[
M^*=f(\Xi).
\]

It is closer to

\[
\mathcal F_\Omega
=
Pareto\{B(M\mid\Omega):M\in\mathcal M_{avail},\; M\text{ semantically admissible}\}
\]

plus a bounded discovery law

\[
P(M_{found}\mid \Gamma,H,B_{discover},\Omega).
\]

A prospective GMI phase result would show that compact architecture-neutral coordinates of `Omega` plus registered realization-response coordinates predict movement of this frontier across **multiple family classes**.

---

# 12. Consequence for “neural networks are one form”

GMI should not predict “neural” from task words.

A neural realization may move toward the frontier when its measured response properties fit the obligation and resource regime, for example:

```text
training cost can be amortized over a long reuse horizon
available feedback supports efficient distributed parameter updates
approximation/distortion is admissible
hardware makes dense numerical computation cheap
drift/retraining/interference costs remain acceptable
```

If these conditions do not hold, other exact/programmatic/probabilistic/memory/hybrid realizations may dominate.

This is a conditional phase hypothesis, not a theorem that neural networks are globally optimal.

---

# 13. Current terminal

```text
DEMAND_ONLY_MORPHOLOGY_SELECTION_REJECTED
REALIZATION_RESPONSE_AND_SEARCH_REQUIRED
```

This narrows the Track-B ultimate question to a stronger form:

> Is there a compact architecture-neutral demand/response law that predicts *frontier movement* across machine-intelligence forms once semantic adequacy, available realizations, resources and bounded discovery are all explicit?

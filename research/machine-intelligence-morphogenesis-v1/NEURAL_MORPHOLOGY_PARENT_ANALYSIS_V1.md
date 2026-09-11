# Neural Morphology Parent Analysis v1

Status: **parent reconstruction + Track-B hypothesis source**. This file does not argue that neural networks are inferior or that OCM should replace them.

Question:

> Why has neural morphology dominated so many recent machine-intelligence tasks, and what does that imply for a general morphogenesis theory?

The answer must be decomposed into mechanisms and resource regimes rather than attributed to “universal approximation.”

---

## 1. What universal approximation/computability does NOT explain

Classical universal-approximation results and recurrent-network computational-universality constructions show broad representational power. They do not by themselves explain:

```text
learnability from finite data
optimization speed
sample efficiency
transfer
continual plasticity
lifetime maintenance
hardware efficiency
why one architecture is selected over another
```

Therefore `NEURAL_IS_UNIVERSAL` is not a Track-B morphology explanation.

---

## 2. Candidate mechanisms behind neural success

### N1 — differentiable credit assignment

Backpropagation gives structured credit signals through composed differentiable computations. This can make adaptation of very large parameter sets feasible when a useful loss/gradient exists.

Track-B interpretation:

```text
morphology advantage may come from the update law U,
not merely the forward architecture G.
```

A general basis must therefore represent **learning laws**, not only computations.

Strong parent: Backprop as Functor already formalizes gradient-style learning compositionally under explicit assumptions.

### N2 — distributed representation / shared feature learning

Multitask-representation theory gives conditions under which a shared representation learned across related tasks improves learning relative to independent task learning. Neural systems are a highly scalable implementation of this pattern.

Track-B consequence:

```text
related-task structure is an ecology coordinate;
representation-learning benefit is conditional, not universal.
```

### N3 — amortization

Large training cost can be converted into repeated cheap inference.

A minimal economic criterion is:

\[
H(C_{scratch}-C_{infer}) > C_{train}+C_{maint}+C_{update}
\]

where `H` is the effective reuse horizon.

Neural morphology is especially attractive when the same statistical competence is consumed at huge scale.

This is conceptually similar to OCM/library amortization and therefore cannot be claimed as OCM novelty.

### N4 — empirical scaling

Neural language-model loss has exhibited systematic empirical scaling with model size, data and compute over large ranges. Compute-optimal work further shows that even within the same broad morphology, architecture scale and data scale must be allocated jointly.

Track-B consequence:

```text
morphology phase laws need internal scaling laws;
a morphology is not one point but a family with its own resource-optimal curve.
```

### N5 — hardware/software co-design

Dense linear algebra maps unusually well to GPUs/TPUs/tensor accelerators. The original TPU evaluation reported large speed/energy advantages on deployed neural inference workloads relative to contemporaneous CPU/GPU baselines.

Track-B consequence:

```text
R (physical resource regime) is part of morphology selection.
```

Comparing neural tensor computation to pointer-heavy symbolic execution on hardware optimized for tensors is not architecture-neutral science.

### N6 — learned plasticity / learning-to-learn

MAML, learned optimizers and differentiable plasticity show that neural parameters can encode not only solutions but update behavior and fast adaptation.

Therefore:

```text
parametric != static
neural != non-developmental
```

and “OCM is developmental while NN is not” is rejected.

---

## 3. Known neural limitations relevant to a phase law

### L1 — continual plasticity loss

The 2024 Nature study on deep continual learning shows standard deep-learning procedures can gradually lose plasticity over long task sequences and that diversity-injecting methods such as continual backprop can mitigate this.

Track-B interpretation:

- morphology limits can arise from the update law rather than representational reach;
- `plasticity` and `retention` are separate variables;
- long-lifetime comparisons may reverse short-horizon comparisons.

### L2 — stability / forgetting

Continual-learning literature already treats the stability-plasticity problem as a core challenge. Track B must not attribute every long-lived neural failure to “opaque parameters”; matched modern continual parents are required.

### L3 — exact revision / provenance

Standard dense parametric learning does not inherently supply exact source-level revocation, local dependency reopening or formal warrant. This is a potential ecology pressure favoring explicit or hybrid morphology, but it is **not** a theorem that neural systems cannot implement these functions through additional structures.

Strongest parent product must receive first refusal.

### L4 — sparse/noisy feedback and credit assignment

Backprop advantage depends on a usable differentiable training signal. In environments where useful feedback is sparse, expensive, non-differentiable or delayed, search, probabilistic inference, model-based control, program synthesis or hybrids may have different frontiers.

### L5 — retraining / adaptation economics

A huge reuse horizon favors large amortized models; rapid environment change, expensive retraining or frequent exact revision may shorten that horizon and alter the phase boundary.

---

## 4. Neural dominance is an empirical region, not a universal law

The current Track-B hypothesis is:

\[
M_{neural}\in Frontier(E)
\]

for large important regions `E`, not

\[
M_{neural}=\text{the unique fundamental form of intelligence}.
\]

Likewise, the theory must allow a result in which neural or neural-hybrid systems dominate most practically relevant regions.

That would be a valid Track-B finding.

---

## 5. Required neural parent arms for future phase studies

Do not use one toy MLP as “the neural morphology.” Depending on the ecology, first refusal should include:

```text
plain gradient-trained network
continual-learning / plasticity-preserving network
meta-learned / fast-adaptation network
memory/retrieval-augmented network
modular / mixture architecture where appropriate
neural-program / tool hybrid
```

All must receive matched information, tools and verifier access.

---

## 6. Falsifiable neural-region predictions

### P-N1

Increasing related statistical task volume and reuse horizon should expand the region where learned parametric representation amortizes better than reset explicit search, after training cost is charged.

### P-N2

Increasing exact-revision frequency should reduce the advantage of monolithic retraining relative to explicit/local or hybrid mechanisms unless a neural parent implements comparably local revision.

### P-N3

Increasing continual task horizon without plasticity-preserving machinery should expose declining neural developmental productivity before an equivalent from-scratch network; modern plasticity parents are required as controls.

### P-N4

Changing hardware prices/accelerators should move measured morphology boundaries even if algorithms are unchanged.

### P-N5

A hybrid may dominate where statistical representation and exact compositional verification are both material, but only if the effect survives a strongest ordinary neural+tool/solver parent product.

---

## 7. Primary sources currently bound to these claims

- Cybenko, 1989 — universal approximation for sigmoidal networks.
- Siegelmann & Sontag, 1995 — computational power of recurrent sigmoidal nets under their construction.
- Rumelhart, Hinton & Williams, 1986 — backpropagation representation learning.
- Maurer, Pontil & Romera-Paredes, 2016 — regimes where multitask representation learning is beneficial.
- Finn et al., 2017 — MAML.
- Andrychowicz et al., 2016; Wichrowska et al., 2017 — learned optimizers.
- Miconi, Stanley & Clune, 2018 — differentiable plasticity / meta-learning.
- Kaplan et al., 2020 — empirical neural-language-model scaling laws.
- Hoffmann et al., 2022 — compute-optimal model/data scaling.
- Dohare et al., 2024 — loss of plasticity in deep continual learning and continual-backprop mitigation.
- Jouppi et al., 2017 — TPU hardware co-design / neural inference performance.

The literature ledger must keep reading depth and source verification separate from this synthesis.

---

## 8. Claim ceiling

Allowed:

```text
NEURAL_MORPHOLOGY_PHASE_HYPOTHESES_REGISTERED
```

Not allowed from this analysis:

```text
WHY_NEURAL_NETWORKS_WIN_PROVEN
NEURAL_NETWORKS_NOT_GENERAL
OCM_SUPERIOR_TO_NEURAL
NEURAL_PHASE_BOUNDARY_ESTABLISHED
```

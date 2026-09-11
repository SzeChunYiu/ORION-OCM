# Parent Expansion v3 — meta-RL, developmental program encodings, clone theory

Status: **third parent-hardening pass**. This supplements the earlier ledgers and remains intentionally short of saturation.

---

## A. Neural systems can contain learned learning algorithms

### Duan et al. — RL²: Fast Reinforcement Learning via Slow Reinforcement Learning (2016)

Primary source: https://arxiv.org/abs/1611.02779

The method represents a fast RL algorithm as recurrent-network dynamics. The RNN weights are learned slowly across a task distribution, while activations carry the fast learner's state on a new MDP.

**Track-B consequence:** a neural morphology can encode a *learning algorithm itself* in its dynamics. Any contrast of “neural parameters versus a genuinely developmental machine” is scientifically invalid unless adaptive/meta-neural parents receive first refusal.

Disposition:

```text
ADOPT_META_RL_PARENT
REJECT_STATIC_NEURAL_STRAWMAN
```

### Wang et al. — Learning to reinforcement learn (2016)

Primary source: https://arxiv.org/abs/1611.05763

A recurrent network is trained by one RL algorithm, while its recurrent dynamics implement a second learned RL procedure shaped by structure in the training domain.

**Track-B consequence:** separation between morphology and learning law is essential; the learning law may itself be represented in recurrent state/weights rather than being an external explicit algorithm.

Disposition: `ADOPT_LEARNED_ALGORITHM_PARENT`.

### Rakelly et al. — PEARL (ICML 2019)

Primary source: https://proceedings.mlr.press/v97/rakelly19a.html

PEARL separates task inference from control using probabilistic latent context and off-policy meta-RL, enabling rapid adaptation from small new-task experience and structured uncertainty-aware exploration in the studied benchmarks.

**Track-B consequence:** neural + probabilistic hybrid morphology is already a mature parent pattern; “hybrid statistical + belief-state adaptation” is not by itself a new form.

Disposition: `ADOPT_NEURAL_PROBABILISTIC_META_RL_PARENT`.

---

## B. Program graphs can develop/self-modify their own morphology

### Harding, Miller & Banzhaf — Self-Modifying Cartesian Genetic Programming

Primary source family: chapter in *Cartesian Genetic Programming*, Springer (2011), pp. 101–124.

SMCGP adds self-modifying nodes whose execution transforms the phenotype, producing a sequence of phenotypes from one genotype.

### Miller — Cartesian genetic programming: its status and future (2020)

Primary review: https://doi.org/10.1007/s10710-019-09360-6

The review covers self-modifying CGP, recurrent CGP, iterative CGP, differentiable CGP, modules and developmental ANN encodings. It explicitly describes SMCGP as a developmental process in which active self-modification operations transform one phenotype into the next.

**Direct threat to Track B:**

```text
rewritable program graph
+ self-modification
+ developmental phenotype sequence
```

is already parent-owned territory.

Therefore `B2_REWRITABLE_TYPED_PROGRAM_GRAPH` survives only if Track B establishes something above generic self-modifying GP/program morphology, such as:

- cross-paradigm bounded developmental compilation;
- prospective ecology -> morphology phase law;
- blind recovery under a neutral basis;
- a resource/developmental theorem not inherited from generic program evolution.

Disposition:

```text
STRONG_PARENT_FOR_B2
SELF_MODIFYING_PROGRAM_MORPHOLOGY_PARENT_OWNED
```

---

## C. Boolean basis/minimality is mature clone theory

### Post — Two-Valued Iterative Systems of Mathematical Logic (1941)

Post gave a complete classification of clones of Boolean functions under composition/projections. Modern presentations call this **Post's lattice**.

Key consequence for our exact calibration:

- Boolean functions closed under composition/projections form clones;
- Post classified the Boolean clone lattice;
- functional-completeness criteria and standard Sheffer functions such as NAND/NOR are mature mathematics.

Thus Stage A and Stage C-v0 are **not** new minimal-basis theory. They are instrumentation checks.

Track-B implication:

Before any finite primitive/minimality claim ask whether it is already a known problem in:

```text
clone theory / universal algebra
transformation semigroup generator theory
functional completeness
circuit basis complexity
```

Allowed calibration terminal remains:

```text
ADAPTIVE_BOOLEAN_BASIS_CENSUS_EXACT__PARENT_MATHEMATICS_DOMINATES
```

**Upward residual:** the novel question, if any, must involve *developmental update behavior + resource semantics + cross-paradigm morphogenesis*, not the Boolean closure facts themselves.

---

# Updated parent-subtraction consequence

After this pass, the following are explicitly **not** Track-B novelty:

```text
neural systems learning how to learn
recurrent networks implementing learned RL algorithms
probabilistic latent task inference in meta-RL
self-modifying/developmental program graphs
evolving sequences of neural/program phenotypes
Boolean functional completeness/minimal connective bases
```

The surviving candidate research question moves upward again:

> Can one parent-subtracted, resource-bounded developmental framework predict and recover **which whole morphology/update organization** is favored by a new ecology, across neural, symbolic, probabilistic and programmatic parents?

Current coverage status:

```text
PARENT_COVERAGE_PARTIAL__META_RL_SELF_MODIFYING_PROGRAMS_CLONE_THEORY_ADDED_V3
```

Remaining before saturation still includes proof-level Levin/Blum reconstruction, broader process/interaction formalisms, artificial chemistries/developmental encodings, meta-learning theory beyond the registered parents, and fresh 2025–2026 architecture-discovery literature.

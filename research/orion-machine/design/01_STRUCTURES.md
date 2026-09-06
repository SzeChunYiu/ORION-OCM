# 01 — Structures: what the machine is made of, chosen against alternatives

Criteria used in every table (the same four, in this order):
**R** exact retraction (revoking a part removes exactly its contribution, nothing else);
**P** parent absorption (the strongest published parent re-implements faithfully on it);
**C** cost (population, query, revision) on the registered instance sets;
**K** checkability (a planted violation is caught by an exact checker with a no-alarm case).
"Best" is the row that wins on R and K without losing P, at acceptable C. Nothing below is chosen
without a rejected row and its reason.

## S1. The knowledge space: warranted typed hypergraph `[MACHINE: kso_math_v1.check_warrant_semiring, KnowledgeSpace.validate]`

`𝒦 = (A, H, τ, L, Σ)` — atoms `A`; hyperedges `h = (tails(h) ⊆ A, heads(h) ⊆ A, w(h) ≥ 0)`;
`τ: H → T`; labels `L: A ∪ H → 𝓛`; genome `Σ` (S1–S7 predicates on `𝒦`).

| candidate | R | P | C | K | verdict |
|---|---|---|---|---|---|
| **directed typed hypergraph** (chosen) | ✔ conjunctive tails make "all premises needed" exact | ✔ ATMS nodes/justifications, AND/OR graphs, hyperpath search | population O(\|A\|+\|H\|); query see 04 | ✔ `validate` + planted dangling/negative-weight | **chosen** |
| plain typed graph (pairwise edges) | ✘ a rule with two premises needs an auxiliary node whose revocation semantics is invented | partial (KG, spreading activation) | lower | ✔ | rejected: conjunction not representable exactly |
| simplicial / cell complex (v1 atlas gluing) | ✘ gluing is symmetric; warrant flows directionally | ✘ no ATMS parent on complexes | higher | partial | rejected as the substrate; **kept as constraints** (gluing conditions, 07) |
| factor graph / probabilistic graphical model | ✘ marginalisation is not retraction; a revoked factor changes every marginal | ✔ BP | high | ✘ no exact no-alarm case | rejected |

## S2. Warrant: ATMS label = antichain of environments `[PROVED: KS-T01] [PARENT: de Kleer 1986]`

`𝓛 = Antichain(𝒫(Assumptions))`; `l₁ ⊕ l₂ = min(l₁ ∪ l₂)`; `l₁ ⊗ l₂ = min{e₁ ∪ e₂}`;
`0 = ∅`; `1 = {∅}`; `live(l, R) ⇔ ∃ e ∈ l : e ∩ R = ∅`. The RCL profile of #203 **is** this label.

| candidate | R | P | C | K | verdict |
|---|---|---|---|---|---|
| **ATMS label** (chosen) | ✔ revocation set `R` kills exactly the environments meeting it; reinstatement is exact | ✔ de Kleer; RCL profile = label (#203) | \|l\| ≤ 2^{assumptions} in theory; n=4 exhaustive, sparse in practice | ✔ exhaustive n=3 semiring checker, planted merge mutant | **chosen** |
| JTMS single justification (Doyle 1979) | partial: IN/OUT relabelling is a search, not an algebra; multiple supports lost | ✔ | lower | partial | rejected: composition law not associative on supports |
| probability / Dempster–Shafer mass | ✘ retraction ≠ conditioning; a revoked premise leaves residual mass | ✔ | high | ✘ | rejected |
| Boolean provenance semiring (Green–Karvounarakis–Tannen 2007) | ✔ same algebra | ✔ | same | ✔ | equivalent; **absorbed as the parent of the semiring view** (08) |

## S3. Edge types: the atlas vocabulary plus four structural relations `[MACHINE: kso_m0_freeze_checks_v1 (vocabulary bound to ContextMapKind)]`

`T = ContextMapKind ∪ {DEPENDENCE, SUPPORT, COMPOSITION, CONSTRAINT}` where `ContextMapKind =
{RESTRICTION, EMBEDDING, SCALE_CHANGE, BOUNDARY_CHANGE, REPRESENTATION_TRANSPORT, DECISION_TRANSPORT}`
(`src/orion_v2/epistemic_atlas.py`). Unregistered types are rejected at admission.

| candidate | R | P | C | K | verdict |
|---|---|---|---|---|---|
| **fixed registered vocabulary** (chosen) | ✔ typed navigation `W_Q` is per-type, so a revoked type is a pruned block | ✔ typed KGs; atlas is v1's own vocabulary | O(1) per edge | ✔ planted unregistered type rejected | **chosen**; extension only by Jump (M4) |
| untyped edges | ✘ navigation cannot condition on relation; hubs dominate | ✔ spreading activation | lowest | ✘ | rejected (ME-X6 V3: typing is a *coverage prior*, so absent typing is a lost prior, 02 §A15) |
| learned/latent types | ✘ retraction of a type has no exact meaning | ✔ (embeddings) | high | ✘ | rejected for the substrate; admissible as a Jump *proposal* source (M4) |

## S4. Navigation state: restart walk with frozen denominators `[PROVED: KS-T03, KS-T04, KS-T05]`

`W_Q[a,b] = Σ_{h: a∈tails(h), b∈heads(h)} η_Q(τ(h)) · w(h) · g_R(h) · g_R(b) / d(a)`, `d(a)` frozen at `R=∅`;
`ρ = α s_Q + (1−α) W_Qᵀ ρ`; unique fixed point; `α` is a registered parameter (04 §P).

| candidate | R | P | C | K | verdict |
|---|---|---|---|---|---|
| **frozen-denominator gated walk** (chosen) | ✔ pruning ≡ gating with original denominators (KS-T04); a revoked atom's share leaves, nothing is redistributed | ✔ RWR / PPR (Tong–Faloutsos–Pan 2006; Page et al.) | exact rational O(n³) small; iterative O(k(n+m)) | ✔ renormalising mutant caught (16/50 worlds) | **chosen** |
| renormalised PPR (row-stochastic after pruning) | ✘ revocation *raises* unrelated atoms (must-differ control fired) | ✔ | same | ✔ but wrong law | rejected: violates R |
| Hopfield / energy relaxation | ✘ attractors are global; no per-atom retraction | ✔ | high | ✘ | rejected |
| attention over embeddings | ✘ no label gate, no exact zero | ✔ (transformers) | high | ✘ | rejected for the solver; admissible as a *codec* (M5) |

## S5. Atom: decomposed knowledge structure with its own label `[MACHINE: kso_m1_mex1_population_v1 (label ≡ oracle, planted merge)]`

An atom is the smallest unit that can be independently warranted or revoked: a claim, a definition,
a procedure step, a constraint, a representation. Its label is its own; a composite never merges
labels (planted `⊕`-merge caught 50/50).

| candidate | R | P | C | K | verdict |
|---|---|---|---|---|---|
| **atom = independently revocable structure** (chosen) | ✔ | ✔ ATMS node, `ATOMIC_CLAIM_INVENTORY.json` schema (v1) | population by decomposition, 04 §populate | ✔ | **chosen** |
| sentence / paragraph | ✘ one revocation drags unrelated claims | ✔ (RAG chunks) | low | ✘ | rejected for the store; a *render* unit only |
| embedding vector | ✘ no label, no exact identity | ✔ | low | ✘ | rejected; codec-side only |

## S6. Procedure: warranted hyperpath `[SPEC → M2]`

A procedure is a hyperpath `π = (h₁..h_k)` in the enabled sub-hypergraph from seeds to a target,
with `L(π) = ⊗ᵢ L(hᵢ) ⊗ ⊗_{a∈π} L(a)`. Its cost is the budget it consumed (04 §NavigationBudget).

| candidate | R | P | C | K | verdict |
|---|---|---|---|---|---|
| **hyperpath with `⊗` label** (chosen) | ✔ revoke any part ⇒ `live` fails for the whole | ✔ hyperpath search (Gallo et al. 1993), AND/OR planning | O(\|π\|) to label | ✔ planted component revocation kills composite (compose checker) | **chosen** |
| program tree / DSL (DreamCoder) | partial: library revocation not tracked | ✔ | high | partial | rejected as the *store*; **the parent for M3 consolidation** (08) |
| option / skill (RL) | ✘ reward-derived; feedback cannot warrant | ✔ | high | ✘ | rejected |

## S7. Genome: `Σ = {S1..S7}` as predicates on `𝒦` `[MACHINE: kso_m0_freeze_checks_v1 (seven planted violations, digest unchanged by population)]`

The constraints that no operation may write: revocation-completeness (S1), label soundness (S2),
exact-share retraction (S3), coarsest authority-preserving partition (S4, Theorem S4), signature
invariance under self-revision (S5), channel warrant typing (S6), obstruction honesty (S7).
Alternative considered: constraints as *soft* penalties — rejected: a penalty can be traded away by
growth, which is the cancer case (03 §τ4).

## S8. Boundary: codec with the E30-R14 contract `[SPEC → M5]`

`codec: text → (s_Q, request atoms)` and `render: (subgraph, warrant, outcome) → text`; a codec has
no write access to `L`, `H`, `Σ`. Two codecs are required by the translator-invariance gate.
Alternative: LLM as store+solver (today's default) — rejected by the programme's premise
(#284 unbundling); it becomes the strongest-parent comparator instead (08).

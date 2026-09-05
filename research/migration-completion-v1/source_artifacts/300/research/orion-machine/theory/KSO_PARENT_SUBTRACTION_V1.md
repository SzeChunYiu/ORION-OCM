# KSO parent subtraction V1 — strongest known mathematics first

Status: **M0 research dependency map; no novelty or superiority claim.**  
Umbrella: #194 · execution master: #197 · prototype: #284 · stacked implementation branch: `research/ocm-kso-math-v1-20260904`.

The KSO is not allowed to win by renaming a graph, a truth-maintenance system, PageRank, a program algebra, a sheaf, or graph rewriting. This file assigns first right of refusal to the strongest parent object for each mechanism and states what, if anything, remains as an OCM coupling question.

## Expert cells used for this subtraction

- **X-KS1 higher-order networks / stochastic processes** — hypergraphs, Markov chains, local diffusion.
- **X-KS2 compositional mathematics / programming languages** — monoidal categories, operads, Kleene algebra, typed procedures.
- **X-KS3 epistemics / provenance** — ATMS, provenance semirings, proof-carrying computation.
- **X-KS4 local-to-global / representation** — presheaves, sheaves, lumpability, quotient dynamics.
- **X-KS5 dynamic structure** — Petri nets, algebraic graph transformation, DPO rewriting, concurrency.
- **X-KS6 learning / self-extension** — program induction, library learning, meta-learning, self-rewrite.
- **X-KS7 decision / experimentation** — value of information, Bayesian experimental design.
- **X-KS8 hostile parent referee** — assumes the faithful product of all rows below and attempts to absorb the KSO completely.

## Parent table

| KSO mechanic | strongest parent / primary source | what the parent already owns | adopted KSO rule | residual status |
|---|---|---|---|---|
| Minimal sufficient warrant sets and exact retraction | de Kleer, **An assumption-based TMS**, *Artificial Intelligence* 28(2), 1986, DOI `10.1016/0004-3702(86)90080-9` | assumption-set labels, simultaneous alternatives, retraction/context switching | KSO node/edge warrant is an ATMS-style antichain; do not rename it | `PARENT_OWNED` |
| Compositional provenance annotations | Green, Karvounarakis & Tannen, **Provenance Semirings**, PODS 2007, DOI `10.1145/1265530.1265535` | semiring propagation of annotations/provenance through composition | use an idempotent antichain semiring for alternative/conjunctive warrant | algebra parent-owned; KSO binds it to live cognitive dynamics |
| Higher-order relations and random walks | Chitra & Raphael, **Random Walks on Hypergraphs with Edge-Dependent Vertex Weights**, ICML 2019, PMLR 97 | hypergraph random walks, Laplacian, mixing, conditions where hypergraph walk collapses to graph walk | KSO substrate is a typed directed hypergraph; higher-order relation is not encoded as unrelated pairwise edges | `PARENT_OWNED` for walk mathematics |
| Seeded/local graph navigation | Andersen, Chung & Lang, **Local Graph Partitioning using PageRank Vectors**, FOCS 2006, DOI `10.1109/FOCS.2006.44` and classical personalized PageRank | restart-biased local diffusion from seeds | query atoms define restart distribution; M0 uses a substochastic restart operator | `PARENT_OWNED` |
| Nontrivial typed local diffusion | Bodnar et al., **Neural Sheaf Diffusion**, NeurIPS 2022 | sheaf-valued diffusion, heterogeneous local transport, control of oversmoothing/heterophily | richer learned transports may replace scalar KSO edge weights only after scalar M0 is calibrated | `PARENT_OWNED`; optional successor |
| Local-to-global consistency | Robinson, **Sheaves are the canonical data structure for sensor integration**, *Information Fusion* 36, 2017, DOI `10.1016/j.inffus.2016.12.002`; Hansen & Ghrist, **Toward a spectral theory of cellular sheaves**, 2019, DOI `10.1007/s41468-019-00038-7` | restriction maps, consistency/global-section questions, sheaf Laplacian/cohomological obstructions | keep the existing ORION atlas presheaf-like; a global claim needs a separate gluing witness | `PARENT_OWNED` |
| Procedure/control algebra | Kozen, **Kleene algebra with tests**, TOPLAS 19(3), 1997, DOI `10.1145/256167.256195` | equational algebra for sequencing, choice, tests and iteration of programs | procedure language should reuse KAT-like laws rather than inventing control-flow algebra | `PARENT_OWNED` |
| Wiring/composition of multi-input operators | Fong & Spivak, **An Invitation to Applied Category Theory**, 2019, Ch. 6; hypergraph categories / operads | typed wiring diagrams, substitution, compositional network semantics | KSO hyperedges/operators use typed ports; composition is a wiring operation with separate warrant/resource decoration | `PARENT_OWNED` |
| Concurrent enable/fire semantics | classical Petri-net theory; Reisig, **Petri Nets: An Introduction** | conjunctive preconditions, firing, resources/concurrency | navigation and execution are distinct: navigation may traverse a relation; an executable hyperedge fires only when all preconditions are live/enabled | `PARENT_OWNED` |
| Extracting a compact connected clue subgraph | prize-collecting Steiner tree / network design; Goemans–Williamson family | connected prize-cost optimization and approximation | M2 extraction is a prize-collecting connected-subgraph problem; exact only on bounded domains | `PARENT_OWNED`; do not claim extraction algorithm novelty |
| Safe representation quotient of navigation | Kemeny–Snell lumpability | necessary/sufficient equality of block-transition probabilities for a Markov quotient | KSO compression must satisfy navigation lumpability **and separately** warrant measurability | dynamic quotient parent-owned; conjunction with warrant is integration |
| Structural graph self-modification | Lack & Sobociński, **Adhesive and quasiadhesive categories**, RAIRO 39(3), 2005, DOI `10.1051/ita:2005028`; DPO graph transformation | well-behaved pushout-based graph rewrite; typed/attributed graphical structures | Jump is a governed typed rewrite with protected interface, correspondence, impact/reopen set and rollback | rewrite mathematics parent-owned |
| Proof-bearing executable admission | Necula, **Proof-Carrying Code**, POPL 1997, DOI `10.1145/263699.263712` | producer supplies proof; host checks against a declared policy before execution | executable learned operators require a checkable certificate at the authority boundary | `PARENT_OWNED` |
| Procedure/library induction and consolidation | DreamCoder (Ellis et al., 2021) and LILO (Grand et al., arXiv:2310.19791) | program search, abstraction/library learning, compression/reuse, language-assisted library documentation | KSO consolidation may compress repeated procedure subgraphs; this is not itself novel | `PARENT_OWNED`; must outperform/match faithful library learner to claim residual |
| Formal-math search with symbolic checking | AlphaGeometry, *Nature* 625 (2024), DOI `10.1038/s41586-023-06747-5`; AlphaGeometry2, JMLR 26 (2025) | learned guidance plus symbolic deduction; auxiliary construction search; machine-checkable math | M6 must compare against strong neuro-symbolic theorem-proving/search parents; proof checker is not KSO novelty | `PARENT_OWNED` for solver pattern |
| Self-rewriting based on proof of utility | Schmidhuber, **Gödel Machines**, arXiv `cs/0309048` / 2007 chapter | self-referential proof-based code rewrite under encoded utility axioms | KSO J6/J7 self-revision cannot be advertised as new merely because it rewrites itself | `PARENT_OWNED`; ORION adds external authority/reopen obligations only if irreducible |
| Choosing the universally “best” learner/search policy | Wolpert & Macready, **No Free Lunch Theorems for Optimization**, IEEE TEC 1(1), 1997, DOI `10.1109/4235.585893` | no algorithm dominates uniformly over all problems under the theorem's symmetry assumptions | OCM must discover **context-relative** policies; “globally best intelligence form” is not a valid unconditional target | universal-best claim killed |
| Information-seeking action | Howard, **Information Value Theory**, IEEE TSSC 2(1), 1966, DOI `10.1109/TSSC.1966.300074`; Rainforth et al., **Modern Bayesian Experimental Design**, *Statistical Science* 39(1), 2024, DOI `10.1214/23-STS915` | value of information / decision-aware experiment selection | acquisition should optimize downstream decision value minus cost/risk, not raw entropy reduction | `PARENT_OWNED` |

## Strongest faithful parent product

The hostile comparator for KSO is therefore not a plain knowledge graph. It is at least:

```text
typed hypergraph
+ restart/local hypergraph navigation
+ optional learned sheaf transports
+ ATMS / provenance labels
+ KAT / typed operator composition
+ Petri-style conjunctive firing
+ connected-subgraph extraction
+ Markov-lumpable representation compression
+ DPO graph rewriting
+ proof-carrying admission / external verifier
+ DreamCoder/LILO-style library learning
+ active experiment selection
+ the same memory, tools, proof assistant, resources and codec access
```

A KSO theorem that disappears against this product is `PARENT_SUFFICIENT`, not a KSO residual.

## What may remain genuinely ORION-specific enough to investigate

The remaining research question is the **coupling**, not any row in isolation:

1. a cognitive diffusion whose path contribution is *warrant-gated* so revocation removes the exact original contribution rather than redistributing it;
2. one state transition contract connecting `learn → navigate → compose → verify → revoke/reopen → rewrite` while preserving authority and resource accounting;
3. a structural-obstruction gate that permits a graph/representation/operator rewrite only after lower-level mechanisms are witnessed insufficient;
4. lifecycle-safe consolidation: a macro-skill remains reusable only while the warrant and representation conditions of its source subgraph remain live;
5. a whole-system frontier against the faithful parent product above.

These are **residual candidates**, not novelty claims. M0 establishes only a coherent finite mathematical core and hostile checkers.

## Source boundary

Primary/theorem-bearing sources used above were checked on 2026-09-04. Current novelty is **not established**. This is a parent map, not a literature-saturation terminal; three clean post-material-addition passes are still required by #197 before any priority claim.

## Executable rows — the parents #194 named, each *run* on one registered witness (checker F7, `../reference/kso_m0_freeze_checks_v1.py`; results `../results/KSO_M0_FREEZE_RESULTS_V1.json`)

Witness `W`: seed `s → a`; `a → b` (b's label `{{0}}`), `a → z`; `b → c`, `z → c`; `c → d`;
revocation `R = {0}`. The question for each parent is the same: after `R`, does `b` stop reacting,
and does `z` — which never depended on `b` — keep exactly its share?

| parent (primary source) | owns activation | owns retraction | what it does on `W` after `R = {0}` | label-gated activation with exact-share retraction |
|---|---|---|---|---|
| spreading activation — Collins & Loftus, *Psychological Review* 82(6), 1975, DOI `10.1037/0033-295X.82.6.407` | yes | no | `b` keeps positive activation (no labels to gate on) | no |
| semantic networks / marker passing — Quillian, in Minsky (ed.) *Semantic Information Processing*, 1968 | yes (markers) | no | marker reaches `b` and everything `b` feeds | no |
| ACT-R declarative activation — Anderson, *Rules of the Mind*, 1993; Anderson et al., *Psychological Review* 111(4), 2004, DOI `10.1037/0033-295X.111.4.1036` | yes (`A_i = B_i + Σ_j W_j S_ji`) | no | `b` receives spreading strength from its source regardless of warrant | no |
| Hopfield associative memory — *PNAS* 79(8), 1982, DOI `10.1073/pnas.79.8.2554` | yes (recall) | no | the "revoked" pattern remains a stable fixed point of the unchanged weights | no |
| case-based reasoning retrieval — Kolodner, *Case-Based Reasoning*, 1993; Aamodt & Plaza, *AI Communications* 7(1), 1994, DOI `10.3233/AIC-1994-7104` | yes (similarity ranking) | yes (delete the case) | deleting case `b` **raises** `z`'s share (survivors renormalised) | no — retraction redistributes |
| knowledge-graph retrieval / random walk with restart — Tong, Faloutsos & Pan, ICDM 2006, DOI `10.1109/ICDM.2006.70`; personalised PageRank (Andersen, Chung & Lang, FOCS 2006) | yes | yes (delete the node) | deleting `b` and renormalising rows **raises** unrelated `z` (`navigation_matrix_bad_renormalize`) | no — retraction redistributes |
| JTMS dependency-directed retraction — Doyle, *Artificial Intelligence* 12(3), 1979, DOI `10.1016/0004-3702(79)90008-0` | no | yes (IN/OUT) | IN/OUT status equals the KSO live set exactly; there is no activation quantity to take a share from | no — no activation |
| ATMS labels — de Kleer, *Artificial Intelligence* 28(2), 1986 | no | yes (environments) | labels are the KSO profiles verbatim; no dynamics | no — no activation |
| **product**: (JTMS/ATMS gate) ∘ (spreading activation with pre-revocation denominators) | yes | yes | **equals the KSO law entry-wise on `W`** | yes — as a product of two parents |

**Finding (shown, not assumed).** 0 of 8 single parents owns label-gated activation with
exact-share retraction; each owns activation or retraction, and the two that own both (CBR, KG/RWR)
retract by deletion-and-renormalisation, which is precisely the planted defect of KS-T04. The KSO
law is reproduced exactly by the product of a truth-maintenance gate and spreading activation over
frozen denominators. **Consequence for the residual ledger:** the coupling is a design choice
(*which* normalisation survives revocation), not a mechanism no parent has; it enters the table as
`PARENT_PRODUCT_OWNED`, and any KSO claim about retraction dynamics has this product as its
first-right-of-refusal comparator. M1 (`../results/KSO_M1_POPULATION_RECEIPT_V1.json`) shows the
product and the KSO agreeing on 400 planted revocations over 50 ME-X1 worlds while the renormalising
parents differ on 16 of them.

| KSO mechanic | strongest parent | adopted rule | residual status |
|---|---|---|---|
| label-gated activation with exact-share retraction (#194's "OCM delta") | JTMS/ATMS gate ∘ PPR with frozen denominators | adopt the product; the only choice is the denominator convention | `PARENT_PRODUCT_OWNED` |

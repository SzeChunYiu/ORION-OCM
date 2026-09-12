# GMI Neural / LLM / Transformer Microfeature Calculus v1

Status: **THEORY HARDENING / MICRO-MECHANISM FORMALIZATION — NO UNIVERSAL NUMERIC LAW CLAIMED**

Status date: 2026-09-12.

Refs:

- `GMI_CROSS_PARADIGM_REALIZATION_NORMAL_FORM_V1.md`
- `GMI_NEURAL_MACHINE_INTELLIGENCE_DERIVATION_V1.md`
- `GMI_NEURAL_EXPLANATION_COMPLETENESS_AUDIT_V1.md`
- `GMI_MACHINE_LEARNING_PHENOMENA_ATLAS_V1.md`
- `GMI_PREDICTIVE_RESIDUAL_QUOTIENT_THEORY_V1.md`
- `GMI_CAUSAL_MECHANISM_PHASE_THEORY_V1.md`

Purpose:

> Make essentially every architectural, training, inference and systems-level feature of modern neural networks / LLMs / Transformers land in a typed GMI mechanism with an intervention, resource effect, invariance class and falsifier.

This is not a claim that GMI already predicts the exact numerical benefit of every feature. It is a closure calculus: every feature must have a lawful location and every claimed advantage must become a causal response law rather than an architecture slogan.

---

# 1. Microfeature as a typed intervention

Use the realization normal form

\[
M=(F,\Theta,K,U,\Gamma,\kappa,\rho_M).
\]

A **microfeature** `f` is not identified by a source-code name. It is a registered transformation of one or more realization components while preserving a declared obligation and legal information set.

Assign every feature one or more primary types:

```text
C  compiler / interface / tokenization / semantic interpretation
S  state representation / coordinates / embeddings
R  routing / dependency selection / composition
T  local transform / nonlinear computation
N  normalization / gauge / conditioning
U  update / credit / optimizer / development schedule
H  history / memory / cache / persistence
V  verifier / authority / admission / abstention
G  morphogenesis / factor split-merge / architecture change
P  physical implementation / precision / IO / parallelism
D  decision / decoding / sampling / action selection
```

For ecology `e`, define the registered effect vector of replacing matched realization `M` by `M[f]`:

\[
\Delta_f(e,M)=
(\Delta L_{sem},
 \Delta L_{gen},
 \Delta L_{rob},
 \Delta L_{cal},
 \Delta B_{train},
 \Delta B_{serve},
 \Delta B_{mem},
 \Delta B_{comm},
 \Delta B_{update},
 \Delta B_{verify},
 \Delta B_{search}).
\]

A GMI explanation of `f` is not accepted until it supplies:

1. feature type(s);
2. exact semantic invariances and non-invariances;
3. a directional prediction for at least one component of `Delta_f` under a controlled ecology/context intervention;
4. matched negative twin;
5. hidden-cost accounting rule;
6. implementation-equivalence class;
7. kill condition.

This turns “why does feature X help?” into a registered mechanism-response problem.

---

# 2. Canonical decoder Transformer in GMI form

Let tokenized prefix state at position `i` be

\[
r_i^{(0)}=E(\tau_i)+p_i,
\]

where `E` is the token embedding and `p_i` a positional mechanism.

For a pre-normalized decoder block `l`, write

\[
u^{(l)}=r^{(l)}+A_l(N_l(r^{(l)})),
\]

\[
r^{(l+1)}=u^{(l)}+G_l(N'_l(u^{(l)})).
\]

For attention head `h`,

\[
Q_h=XW_h^Q,\quad K_h=XW_h^K,\quad V_h=XW_h^V,
\]

\[
s_h=\frac{Q_hK_h^\top}{\sqrt{d_h}}+M_{legal}+B_{pos},
\]

\[
\alpha_h=\operatorname{softmax}(s_h/T_a),
\]

\[
A_h(X)=\alpha_hV_h.
\]

Multi-head output is a composition of head outputs followed by an output map. A gated feed-forward block can be represented schematically by

\[
G(X)=W_2\left(\phi(W_gX)\odot W_1X\right).
\]

Final logits and token distribution are

\[
z_i=W_U N_f(r_i^{(L)}),
\qquad
p(x_{i+1}\mid x_{\le i})=\operatorname{softmax}(z_i/T_d).
\]

This entire structure is one concrete `K` with mutable state `Theta`; training defines `U`; any architecture-changing process belongs to `Gamma`; tokenizer/input-output interpretation belongs to `kappa`; training/serving/cache/communication/precision costs belong to `rho_M` and `P`.

---

# 3. Exact and conditional microfeature propositions

## TM-1 — positional distinguishability theorem

Suppose two legal histories `h,h'` differ only by a permutation `g`, and the obligation distinguishes them:

\[
q_O(h)\ne q_O(g\cdot h).
\]

Any exact realization whose complete internal representation is invariant under `g` and has no side channel cannot satisfy `O` on both histories.

Therefore sequence order information is necessary whenever order changes a protected semantic consequence.

This predicts a need for *some* positional/order mechanism, not RoPE, sinusoidal embeddings or any named implementation.

Negative twin: a permutation-invariant obligation.

Kill: an exact side-channel-free realization merges obligation-distinct permutations.

## TM-2 — dynamic-routing union-cost theorem

Let `E(x)` be the set of dependency edges required for exact evaluation on input `x`.

Any fixed sparse routing graph safe for all registered inputs must contain

\[
E_*\supseteq\bigcup_x E(x).
\]

Therefore its edge-materialization burden is at least proportional to

\[
\left|\bigcup_x E(x)\right|,
\]

whereas an exact input-dependent router needs only `|E(x)|` edges on input `x`.

Ideal average structural opportunity:

\[
\Delta B_{route}
\propto
\left|\bigcup_x E(x)\right|
-\mathbb E_x|E(x)|.
\]

This is a precise regime in which attention-like dynamic routing can beat one fixed sparse graph. Dense attention may still lose if routing discovery cost dominates.

## TM-3 — softmax as entropy-regularized routing

For score vector `s` and temperature `T>0`,

\[
\operatorname{softmax}(s/T)
=\arg\max_{p\in\Delta}
\left[p^\top s+T H(p)\right].
\]

Thus softmax attention is an entropy-regularized routing policy. Lower `T` favors concentrated routing; higher `T` favors diffuse routing.

This does not imply a universal optimal temperature; it locates temperature as a routing-entropy tradeoff.

## TM-4 — causal-mask legality theorem

If the registered autoregressive obligation requires action/output at position `i` to be measurable with respect to legal information `x_{<i}`, then any execution path using protected future information violates the information constitution even if final benchmark loss improves.

A causal mask is one implementation of the legal dependency restriction.

Negative twin: bidirectional encoding where future tokens are legally observable.

## TM-5 — exact KV-cache materialization proposition

For a fixed deterministic decoder model and immutable prefix, previously computed key/value states are derived serving state. Reusing them is semantics-preserving relative to recomputing them exactly.

Therefore KV caching is an A2-style authority/serving separation:

```text
authoritative state: model parameters + legal prefix
serving materialization: cached K/V tensors
```

The cache is disposable unless the external obligation gives it persistence/lineage meaning.

Prediction: its benefit rises with prefix reuse and autoregressive continuation length, but memory burden rises with cached sequence length, layers and KV-head count.

## TM-6 — implementation-equivalent exact-attention proposition

Two attention implementations that return exactly the same mathematical attention result under the same numeric semantics belong to one semantic mechanism class even if their memory traffic differs.

Consequently IO-aware exact algorithms such as tiled attention are primarily `P/rho` innovations, not new cognitive semantics.

A theory that calls them different intelligence forms commits an implementation-label error.

## TM-7 — KV-sharing tradeoff proposition

Let `H_q` be query-head count and `H_{kv}` the number of independently materialized key/value heads.

Ignoring other constants, autoregressive KV-cache state scales linearly with `H_{kv}` rather than `H_q`.

Thus MQA/GQA-like sharing can reduce memory-bandwidth burden by reducing `H_{kv}`.

However, if two query groups require functionally distinct K/V maps for exact registered behavior and no compensating transform exists elsewhere, forcing them to share can destroy exact adequacy.

Prediction: optimal grouping is a capability-vs-cache/communication frontier controlled by dependency heterogeneity and serving prices, not a universally best head ratio.

## TM-8 — finite-context information no-go

Suppose two histories have identical final `W` tokens but require different protected outputs:

\[
h_{[-W:]}=h'_{[-W:]},\qquad q_O(h)\ne q_O(h').
\]

Any stateless `W`-window model with no external/recurrent memory must merge the two histories and cannot be exact.

Therefore context length, recurrence, retrieval and persistent memory are substitutable ways of carrying required history distinctions, with different burdens.

## TM-9 — next-token optimum and predictive quotient

Under ideal population cross-entropy and sufficient model capacity, the optimum recovers the true conditional next-token distribution. Histories with different continuation distributions are therefore distinguishable in the exact predictive quotient.

Transfer to another target `O` is exact in principle only when

\[
q_O=g\circ q_P,
\]

or when additional residual state resolves the remaining aliases.

This separates “next-token prediction is powerful” from the false statement “next-token prediction contains every target distinction.”

## TM-10 — parameter-sharing symmetry principle

Tying parameters imposes an equality constraint among transformations. This reduces description/state burden but removes degrees of freedom.

It is favored when the protected obligation is invariant/equivariant under the same sharing relation; it becomes a bias cost when the target requires symmetry breaking.

This covers convolutional sharing, recurrent sharing, tied embeddings and many repeated-block constructions under one mechanism.

## TM-11 — approximate serving compilation principle

Quantization, pruning, distillation and approximate caching define a serving compiler

\[
C_{serve}:Z_{auth}\to Z_{serve}
\]

with semantic distortion `epsilon_C` and burden reduction `Delta rho`.

They are admissible when the registered obligation tolerates the induced distortion and lifecycle savings dominate compilation/update burden.

No precision format is universally optimal independently of `O` and `P`.

## TM-12 — residual-target adaptation principle

If a pretrained substrate already resolves most target distinctions and target adaptation has low effective residual dimension/rank, a localized adapter/LoRA-like update can dominate full retraining.

The strong GMI prediction is not “LoRA works,” but:

\[
B_{adapt}^*\ \text{should increase with target residual complexity}
\]

under matched information and protected performance.

---

# 4. Feature atlas — input representation and interface

## Tokenizer / segmentation (`C,S,P`)

A tokenizer is an input compiler

\[
T:\text{surface stream}\to\text{symbol sequence}.
\]

It changes:

```text
sequence length
vocabulary/state-table size
frequency distribution
lexical fragmentation
surface remint sensitivity
serving/training token burden
```

Exact semantic claims must be invariant to semantically equivalent retokenizations or explicitly charge tokenizer-specific information.

Open law: predict optimal vocabulary/segmentation from corpus morphology + hardware + target semantics without architecture identity.

## Vocabulary size (`C,S,P`)

Larger vocabulary may shorten sequences but enlarges embedding/output state and can reduce sharing across subword structure. It is a materialization/factorization tradeoff, not a semantic primitive.

## Embeddings (`S,C`)

Embedding tables compile discrete symbols into continuous coordinates. Their scientific role is measured by what target distinctions/neighborhoods become cheaper to compute, not whether individual dimensions are interpretable.

## Positional mechanisms (`S,R`)

Sinusoidal, learned absolute position, RoPE, ALiBi-like biases and other schemes are alternative encodings of order/relative geometry. TM-1 supplies the necessity condition; comparative superiority is a response law over extrapolation, relative-distance structure and resource burden.

## Segment/type/modality embeddings (`S,C`)

These expose external distinctions such as speaker, modality or segment membership. They help only when those distinctions alter protected semantics or learning geometry.

---

# 5. Feature atlas — attention and routing

## Q/K/V factorization (`R,T`)

Separating query, key and value maps factorizes:

```text
what is being sought
what locations advertise
what payload is transmitted
```

This is a routing/content decomposition, not a claim that Q/K/V coordinates are uniquely identifiable.

## Dot-product similarity and `1/sqrt(d)` scaling (`R,N`)

Dot products provide a cheap compatibility score. Dimension-dependent scaling controls score magnitude and softmax saturation under common initialization assumptions. The causal claim is conditioning of routing entropy/gradients, not semantic necessity of the exact constant.

## Multi-head attention (`R,A1`)

Heads are parallel routing factors. Multiple heads are useful when distinct dependency relations cannot be represented cheaply by one shared routing channel. Head count is therefore factorization granularity; redundant heads are allowed and common.

## MHA / GQA / MQA (`R,H,P`)

These vary sharing of K/V materialization across query channels. TM-7 defines the exact tradeoff class.

## Causal / padding / block / local masks (`R,C`)

Masks encode legal or assumed dependency structure. Causal masks can be constitutional; local/block masks are usually resource priors that are valid only if omitted dependencies are unnecessary or recoverable through layers/other state.

## Sparse/sliding-window attention (`R,P`)

Trades routing coverage for lower compute/memory. Strong prediction: advantage tracks true dependency sparsity/locality and hardware price, not context length alone.

## Cross-attention (`R,C`)

Implements routing between separately represented streams/states. Its value depends on whether preserving source/target state separation lowers burden relative to early fusion.

## Attention temperature / logit scaling (`R,D`)

TM-3: controls concentration vs routing entropy.

## Attention dropout (`R,U`)

Stochastic edge removal changes development regularization/robustness, not inference semantics when disabled at serve time.

---

# 6. Feature atlas — local transforms / MLPs

## Position-wise MLP (`T,S`)

After routing mixes information across positions, a local MLP transforms each residual coordinate independently across positions. It supplies nonlinear feature construction/capacity without additional token-token routing.

## ReLU / GELU / SiLU (`T,U`)

Alternative nonlinear response geometries. The theory must predict training/representation/resource response; no activation name is fundamental.

## GLU / SwiGLU-like gates (`T,R`)

Multiplicative gating gives content-conditioned local transformation. It can be interpreted as micro-routing among feature transformations. Claimed benefit must survive matched parameter/FLOP controls.

## Width / expansion ratio (`S,T,P`)

Controls local representational workspace and compute. Optimal width is a capacity/search/resource frontier, not a universal constant.

---

# 7. Feature atlas — residual stream and normalization

## Residual connection (`S,U`)

For `y=x+f(x)`, the Jacobian is

\[
J_y=I+J_f.
\]

Thus gradient/signal transport contains an identity contribution. This helps explain trainability of deep compositions in appropriate regimes but is not a universal guarantee against instability.

GMI interpretation: incremental refinement of a shared state rather than destructive replacement at every sublayer.

## Residual stream (`S,H`)

The persistent vector stream is fast serving/development state through which many mechanisms communicate. Feature superposition and interference are response properties of this shared state.

## LayerNorm (`N,U`)

Normalizes centered scale statistics, creating approximate shift/scale gauge invariances and conditioning effects.

## RMSNorm (`N,U,P`)

Removes explicit recentering and normalizes root-mean-square scale. It is a cheaper gauge/conditioning choice where recentering is unnecessary.

## Pre-norm vs post-norm (`N,U`)

Changes the Jacobian composition through depth and therefore optimization stability. It is an update-geometry choice, not just formatting.

## epsilon constants / clipping (`N,U`)

Numerical-stability mechanisms whose optimum depends on precision and activation statistics.

---

# 8. Feature atlas — output and decoding

## Unembedding / tied input-output embeddings (`C,S`)

The output map compiles residual state into token logits. Tying it to input embeddings imposes a symmetry/share constraint (TM-10) reducing parameters while restricting the map.

## Softmax output (`D`)

Maps scores to a normalized categorical distribution. Probability calibration is a distinct obligation from argmax correctness.

## Temperature / top-k / top-p (`D`)

Decision policies over a learned distribution. They alter diversity/risk/entropy without changing stored knowledge in the base model.

## Beam search (`D,P`)

Allocates more inference search to sequence decoding. It is a test-time search policy with compute-quality tradeoff.

## Self-consistency / best-of-N (`D,V,P`)

Samples multiple proposals and aggregates/selects them. Improvement must be charged for all proposals and any judge/verifier.

## Speculative decoding (`D,V,H,P`)

Cheap draft proposals are conditionally accepted/checked against a stronger target distribution. This is a serving-time proposal/admission mechanism and an implementation cousin of verifier-gated computation, not by itself a new knowledge architecture.

---

# 9. Feature atlas — autoregressive objective and training protocol

## Autoregressive factorization (`C,D`)

For any sequence distribution with legal ordering,

\[
p(x_{1:n})=\prod_{t=1}^{n}p(x_t\mid x_{<t}).
\]

The chain rule is exact; the architectural/training choice is to model these conditionals efficiently.

## Cross-entropy next-token loss (`U,C`)

A proper scoring-rule development signal for conditional distributions. Population optimum recovers the true conditional under capacity/optimization assumptions. Finite-data, proxy-alignment and distribution-shift gaps remain response terms.

## Teacher forcing (`U,C`)

Training receives the true prefix rather than model-generated prefixes. This changes the development distribution and can create exposure mismatch in free-running generation.

## Data mixture (`U,C`)

The corpus distribution determines which predictive distinctions and priors are rewarded. Mixture weights are development-context choices and must be charged/registered when explaining capabilities.

## Sequence packing / batching (`P,U`)

Primarily physical/development efficiency mechanisms; may alter gradient noise/order but not target semantics when implemented exactly.

## Adam/AdamW (`U`)

Preconditioned stochastic update law. Benefits belong to optimizer response geometry; weight decay adds explicit trajectory/selection pressure.

## learning-rate warmup / decay (`U`)

Time-dependent control of development step geometry. Strong claims require schedule interventions, not folklore.

## gradient clipping (`U,N`)

Bounds update magnitude to stabilize training in regimes with heavy-tailed/unstable gradients, at possible bias cost.

## dropout / stochastic depth (`U,S`)

Development-time stochastic subrealization sampling/regularization. Must be distinguished from deterministic serving morphology.

---

# 10. Feature atlas — adaptation/alignment

## SFT / instruction tuning (`U,C`)

Changes policy mapping from latent capabilities to instruction-conditioned behavior. It may expose/reorganize capability without creating all underlying knowledge from scratch.

## reward model + RLHF (`U,V`)

Adds an external preference proxy and policy optimization. Preference reward is not automatically a truth/admissibility verifier.

## DPO-like preference optimization (`U,V`)

A different optimization realization for preference data. GMI compares information legality, training burden, policy shift and protected outcomes rather than assigning semantic privilege to the algorithm name.

## rejection sampling / verifier fine-tuning (`V,U`)

Proposal filtering can improve admitted development data if the judge correlates with the real obligation; judge error and selection bias must be charged.

## LoRA / adapters / prompt tuning (`U,S`)

Localized residual adaptation. TM-12 supplies the strongest theory prediction.

## model editing / unlearning (`U,H,V`)

Local update obligations must be scored by collateral dependency cone, retained competence, exact removal/admission semantics and downstream serving burden.

---

# 11. Feature atlas — memory, retrieval and tools

## KV cache (`H,P`)

TM-5: disposable serving materialization of prefix computation.

## retrieval / RAG (`H,R,C`)

Separates mutable/external state from parametric predictive state. Whether retrieval is authoritative, merely advisory, versioned or verified is an additional mechanism distinction.

## external database / knowledge graph (`H,C,V`)

Can preserve explicit identity, provenance, recency or relational structure more cheaply than weights in certain regimes. Query/communication burden is charged.

## recurrent/state-space memory (`H,S,T`)

Compresses history into evolving finite/structured state. TM-8 provides the exact necessity test for insufficient state/window.

## tool calls / APIs (`R,V,P`)

The model delegates sub-obligations to external realizations. Tool result authority, latency, failure probability and verifier status are separate dimensions.

## scratchpads / chain-of-thought state (`H,D`)

Additional test-time working state can externalize intermediate computation. It is not necessarily faithful explanation; utility is measured by causal intervention on working-state availability/content.

---

# 12. Feature atlas — serving and systems

## FlashAttention / tiling (`P`)

TM-6: exact implementation-equivalent reduction of memory traffic/IO burden.

## KV quantization / compression (`P,H`)

Approximate serving compiler for cache state; capability-vs-memory-bandwidth frontier.

## weight quantization (`P,S`)

TM-11 serving compilation.

## mixed precision (`P,U`)

Changes numerical resource cost and update noise/stability. Exactness claims require accounting for numeric semantics.

## activation checkpointing / recomputation (`P,H`)

Trades training compute for memory while preserving mathematical gradients up to numeric effects.

## data / tensor / pipeline / sequence / expert parallelism (`P,R`)

Alternative placement/communication realizations of the same abstract computation. Their frontier position depends on hardware topology, bandwidth, latency and synchronization price.

## continuous batching (`P,D`)

Serving scheduler that increases utilization by dynamically grouping requests; normally no cognitive semantic change.

## load balancing in MoE (`P,R,U`)

Controls congestion/expert collapse and hence both learning and communication burden.

---

# 13. Small-feature closure table

The following often-discussed details all have typed homes:

| Feature | GMI primary type | Primary causal question |
|---|---|---|
| tokenizer | C/P | sequence-length vs vocabulary/alias burden |
| embedding dimension | S/P | representational workspace vs cost |
| positional encoding | S/R | order distinctions and extrapolation geometry |
| RoPE | S/R | relative-position geometry under long-context regime |
| causal mask | C/R | legal information dependency |
| head count | R | routing factorization granularity |
| Q/K/V dimension | R/S | compatibility/payload capacity vs cost |
| MQA/GQA | R/H/P | KV diversity vs cache bandwidth |
| attention scale | N/R | score saturation / routing entropy |
| softmax | R/D | entropy-regularized competition |
| attention dropout | U/R | routing regularization |
| MLP ratio | T/S/P | local workspace vs compute |
| GELU/SiLU | T/U | nonlinear/update geometry |
| SwiGLU | T/R | conditional local gating |
| residual connection | S/U | incremental state + identity gradient path |
| LayerNorm/RMSNorm | N/U/P | gauge/conditioning vs cost |
| pre/post norm | N/U | deep Jacobian/update stability |
| weight tying | S/C | symmetry sharing vs expressivity |
| context length | H/P | history information vs compute/memory |
| KV cache | H/P | serving reuse vs memory |
| FlashAttention | P | exact IO compilation |
| quantization | P/S | approximation tolerance vs hardware cost |
| speculative decoding | D/V/P | proposal/accept serving economics |
| beam / top-p / temp | D | decision-search/risk/diversity |
| AdamW | U | preconditioned development and selection |
| warmup / decay | U | time-dependent reachability |
| gradient clipping | U/N | stability vs update bias |
| checkpointing | P/H | memory-compute trade |
| LoRA/adapters | U/S | target residual complexity |
| MoE router | R/G/P | conditional heterogeneity vs communication |
| RAG | H/R | residual mutable knowledge vs retrieval cost |
| tool use | R/V | delegated sub-obligation and authority |
| RLHF/DPO | U/V | preference-policy selection, not truth by default |
| CoT/scratchpad | H/D | test-time working-state burden |

This list is deliberately extensible: a newly invented feature is admitted by typing it and registering its effect vector, not by creating a new theory namespace.

---

# 14. Recursive microfeature hardening protocol

For each feature `f`, recursively run:

```text
MF0 DEFINE
    exact mathematical/algorithmic transformation

MF1 TYPE
    which GMI components change?

MF2 SEMANTIC INVARIANCE
    what obligation changes are impossible / irrelevant?

MF3 RESOURCE LAW
    which lifecycle costs can move?

MF4 MECHANISM HYPOTHESIS
    what intermediate variable mediates benefit?

MF5 COLLISION / NEGATIVE TWIN
    construct same superficial feature with mechanism absent, or mechanism present with different implementation

MF6 CONTROLLED ABLATION
    matched intervention on the feature

MF7 CONTEXT INTERACTION
    vary demand and hardware/resource prices independently

MF8 IMPLEMENTATION EQUIVALENCE
    reproduce mechanism through a different encoding

MF9 FAMILY-HELD-OUT PREDICTION
    fit law on some architecture families, test another

MF10 PARENT REDUCTION
    test whether a simpler known mechanism explains the effect

MF11 CLAIM
    formal / parent theorem / empirical law / programme / open
```

No feature is “explained” merely because it is assigned a type.

---

# 15. Highest-priority remaining microfeature gaps

The calculus closes the *location* of the following gaps but not yet their universal quantitative response laws:

```text
G-T01 tokenizer granularity law across languages/code/modalities
G-T02 optimal positional geometry / length extrapolation law
G-T03 head factorization and redundancy law
G-T04 exact regime map for MHA <-> GQA <-> MQA
G-T05 softmax temperature / entropy law under learned routing
G-T06 MLP expansion/gating law
G-T07 normalization choice and pre/post-norm phase map
G-T08 residual-stream superposition/interference law
G-T09 context-window vs recurrence vs retrieval substitution frontier
G-T10 in-context algorithm formation law beyond toy settings
G-T11 chain-of-thought working-memory faithfulness vs utility law
G-T12 hallucination as predictive-residual / verifier / calibration decomposition
G-T13 data-mixture -> capability/quotient coverage law
G-T14 instruction tuning -> latent-capability exposure vs new acquisition split
G-T15 preference optimization -> policy shift / truth divergence law
G-T16 tool/RAG authority/provenance semantics
G-T17 KV/cache/attention serving frontier across hardware
G-T18 quantization/distillation robustness frontier
G-T19 distributed parallelism communication phase diagram
G-T20 MoE specialization/routing-collapse causal law
```

These are now explicit experimental targets rather than hidden explanatory holes.

---

# 16. Claim boundary

This file supports the statement:

> Modern neural-network, LLM and Transformer components can be decomposed into a small typed set of GMI mechanism classes, and many exact necessity/invariance/resource statements can already be proved at finite scope.

It does **not** support:

```text
all quantitative deep-learning behavior is solved;
all Transformer details are optimal;
all LLM abilities are explained causally;
attention/Transformers are uniquely implied by GMI;
new-form intelligence is established.
```

The research target is stronger and falsifiable:

> after reminting away implementation labels, the typed mechanism descriptors should predict which microfeatures become useful or dominated under held-out obligation and resource interventions.

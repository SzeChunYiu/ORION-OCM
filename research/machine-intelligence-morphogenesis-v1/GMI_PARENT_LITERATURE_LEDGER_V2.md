# GMI Parent Literature Ledger V2 — current-literature first refusal (16 areas)

Status: **first-refusal ledger, 2026-09-12; every listed work verified to exist by a search result (arXiv/publisher/proceedings page, alphaXiv id, or Consensus record). No full-text depth is claimed here; depth upgrades belong in `LITERATURE_LEDGER_V2.md` / `PARENT_LEDGER_V2.json`.** Mirror: `GMI_PARENT_LITERATURE_LEDGER_V2.json` (generated from the same source). Refs: `GMI_THEORY_CORE_V3_EXECUTED.md` (L1–L7, §1b–5d), `GMI_PREDICTED_MACHINE_INTELLIGENCE_FORMS_V1.md` (F1–F6), `REVIVAL_LEDGER.jsonl` (RV-377-029..043), `NOVELTY_RESIDUAL_V2.md`.

Scope rule: this ledger covers the sixteen *current-literature* areas (2022–2026 plus canonical classics) that the earlier ledgers (P0–P9A families: universality, induction, AIXI, OOPS/PowerPlay, AutoML-Zero, meta-learning, PPL, categorical learning, cognitive architectures, RASP/grokking) do not cover, or cover only at the classic layer. Works already absorbed at full-text depth in `PARENT_LEDGER_V2.json` (e.g., Chan 2022, Schlag 2021, AutoML-Zero, DreamCoder, EWC, Hooker 2020) are cited only where the first-refusal line needs them.

Threat scale: **LOW** — parent is the form or a tool, does not explain or reduce a GMI law/form; **MEDIUM** — parent explains part of the claim or supplies the frame, GMI keeps a scoped residual; **HIGH** — parent already states, proves or measures the mechanism/phase law at the claim's own layer, GMI residual is at most scope or a coordinate.

Verification legend: `WS` WebSearch results contained the work's own page; `AX` alphaXiv returned it with its arXiv id; `CS` Consensus returned the record. Direct fetches of arxiv.org / publisher pages were blocked by the egress proxy during this pass, so every entry is *found-in-search-results*, not *page-read*.

Counts: **127 works, 127 verified, 0 to_verify**; threat histogram: HIGH 56, MEDIUM 65, LOW 6.

## Contents
- 1. Transformer/attention theory: expressivity, positional encodings, length generalization, circuits/induction heads, in-context learning theory
- 2. Optimization and generalization: implicit bias, edge of stability, NTK vs feature learning, double descent, grokking, scaling laws, emergence-metric critiques
- 3. Causal representation learning and identifiability
- 4. Continual learning, model editing, unlearning, plasticity loss
- 5. External memory / RAG / retrieval-augmented and memory-augmented models
- 6. Mixture-of-experts and conditional computation
- 7. State-space models and linear attention / recurrence
- 8. Program synthesis and neuro-symbolic systems
- 9. Automated theorem proving and verifier-gated generation (LLM + proof checkers, generate-and-verify, speculative decoding as verification)
- 10. Neural architecture search and morphology search
- 11. Quality-diversity, MAP-Elites, novelty search, POET/open-ended evolution, artificial life
- 12. Predictive state representations, causal states/epsilon-machines, information bottleneck, sufficient statistics
- 13. Incremental/self-adjusting computation, versioned databases, persistent data structures, build systems (for the versioned-local-compilation and lineage forms)
- 14. Active learning / Bayesian experimental design / causal experimental design (for the interventional learner form F4)
- 15. Compilers/JIT/tracing and cache/memoization theory (for the self-compiling form F6 and compile-amortization laws)
- 16. No-free-lunch theorems and Goodhart/proxy-gaming literature
- Strongest reduction threats ranked (top 10) · Parents the executed records already answered

## 1. Transformer/attention theory: expressivity, positional encodings, length generalization, circuits/induction heads, in-context learning theory

**1.1 Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin (2017). Attention Is All You Need.** — NeurIPS 2017. <https://arxiv.org/abs/1706.03762> · verified: WS

- Establishes: Defines the attention form as softmax-normalized similarity-weighted retrieval over a context store, composed with position encodings and feed-forward blocks; no recurrence.
- First refusal: **LOW** → RV-377-034 (attention family derived at D1 as similarity-weighted retrieval; NORMALIZE primitive, gap G9). The parent is the form itself; GMI claims only the basis-dependence of its cost and its domination by hard kNN at scope, which the parent does not address.

**1.2 Elhage, Nanda, Olsson, Henighan, Joseph, Mann, Askell, Bai, Chen, Conerly, DasSarma, Drain, Ganguli, Hatfield-Dodds, Hernandez, Jones, Kernion, Lovitt, Ndousse, Amodei, Brown, Clark, Kaplan, McCandlish, Olah (2021). A Mathematical Framework for Transformer Circuits.** — Transformer Circuits Thread (Anthropic). <https://transformer-circuits.pub/2021/framework/index.html> · verified: WS

- Establishes: Rewrites attention-only transformers as sums of readable paths (QK/OV circuits), showing that trained weights are compositions of interpretable sub-programs (skip-trigram and induction circuits).
- First refusal: **MEDIUM** → L1 (realization is compilation) and section 1b Step 1 (a trained network is a compiled program). The 'trained network = compiled composition of circuits' view is the mechanistic-interpretability standard; L1 adds only the cost signature and the cross-basis identity of development tables.

**1.3 Olsson, Elhage, Nanda, Joseph, DasSarma, Henighan, Mann, Askell, Bai, Chen, Conerly, Drain, Ganguli, Hatfield-Dodds, Hernandez, Johnston, Jones, Kernion, Lovitt, Ndousse, Amodei, Brown, Clark, Kaplan, McCandlish, Olah (2022). In-context Learning and Induction Heads.** — Transformer Circuits Thread; arXiv:2209.11895. <https://arxiv.org/abs/2209.11895> · verified: WS

- Establishes: Induction heads form abruptly during training (a phase change) and their formation coincides with the appearance of in-context learning across model sizes.
- First refusal: **HIGH** → L5 (reachability order inert -> memory -> context-conditioned memory before any in-weights learner; RV-377-023 plateau). A parent already documents the developmental phase transition that produces the in-context form, with a mechanism; GMI's L5 ordering at 10^5 evaluations is a coarse instance unless it predicts the order across bases.

**1.4 Zhou, Bradley, Littwin, Razin, Saremi, Susskind, Bengio, Nakkiran (2023). What Algorithms can Transformers Learn? A Study in Length Generalization. [Follow-on: Huang, Yang, Bhattamishra, Sarrof, Krebs, Zhou, Nakkiran, Hahn (2025). A Formal Framework for Understanding Length Generalization in Transformers, ICLR 2025, arXiv:2410.02140.]** — ICLR 2024; arXiv:2310.16028. <https://arxiv.org/abs/2310.16028> · verified: WS

- Establishes: RASP-L conjecture: transformers length-generalize on a task iff it has a short RASP-L program valid for all lengths; the 2025 follow-on proves limit-transformer bounds via C-RASP.
- First refusal: **MEDIUM** → L3 gates 1-2 (existence in the generator's grammar; admissibility on the unseen split, RV-377-014/017). A grammar-level existence/admissibility criterion for the transformer family already exists with proofs; GMI's four gates would have to reproduce the RASP-L/C-RASP boundary to add anything for this family.

**1.5 Merrill, Sabharwal (2023). The Parallelism Tradeoff: Limitations of Log-Precision Transformers.** — TACL 11; arXiv:2207.00729. <https://arxiv.org/abs/2207.00729> · verified: WS

- Establishes: Log-precision transformers are simulable by uniform TC^0 circuits; any equally parallelizable architecture inherits the same limits (cannot solve linear equalities or CFG membership if L != P).
- First refusal: **HIGH** → L6 (instrument parameters, FRAC_BITS, decide which forms exist; RV-377-029/031 precision gating; gap G5). Precision-bounded expressivity is a theorem-level parent; 'precision decides existence of the probabilistic/policy-gradient rows' is an instance of precision-limited expressivity, not a new law.

**1.6 Garg, Tsipras, Liang, Valiant (2022). What Can Transformers Learn In-Context? A Case Study of Simple Function Classes.** — NeurIPS 2022; arXiv:2208.01066. <https://arxiv.org/abs/2208.01066> · verified: WS

- Establishes: Transformers trained from scratch in-context learn linear, sparse-linear, two-layer-NN and decision-tree function classes at the level of task-specific estimators, under distribution shift.
- First refusal: **MEDIUM** → L5 / RV-377-023 (task diversity creates the selection gradient toward context-conditioned memory forms) and 1b Step 5 (forward pass as proposal geometry). The parent shows SGD on a diversity ecology reaches an in-context learner that matches least squares; GMI's executed 'diversity creates the gradient' is Chan 2022 plus Garg 2022 at toy scale.

**1.7 von Oswald, Niklasson, Randazzo, Sacramento, Mordvintsev, Zhmoginov, Vladymyrov (2023). Transformers learn in-context by gradient descent.** — ICML 2023; arXiv:2212.07677. <https://arxiv.org/abs/2212.07677> · verified: WS

- Establishes: A weight construction shows one linear self-attention layer implements a gradient-descent step on a regression loss; trained transformers converge to this mesa-optimizer.
- First refusal: **HIGH** → L1 (the same update law compiled into a different basis at bounded cost) and 1b Step 1 / GMI-TN2 (an ML algorithm = update law U + query law Q). Cross-basis compilation of the gradient law into attention weights, in a real system, is exactly L1's 'compilation with a cost signature' claim; the executed six-basis C2 result is a toy version of what this parent already demonstrates.

**1.8 Reddy (2024). The mechanistic basis of data dependence and abrupt learning in an in-context classification task.** — ICLR 2024 (oral); arXiv:2312.03002. <https://arxiv.org/abs/2312.03002> · verified: WS

- Establishes: A minimal attention network shows the induction head emerges abruptly through a three-way interaction and competes with in-weights learning; burstiness and class count decide ICL vs IWL.
- First refusal: **HIGH** → L5 and L2 ecology axes (task diversity, seen/unseen split) — the in-context vs in-weights occupant as a function of ecology coordinates. A parent already provides the mechanistic phase diagram of context-conditioned vs in-weights forms as a function of ecology coordinates, with a minimal model; L5's ordering result is a coarse instance.

## 2. Optimization and generalization: implicit bias, edge of stability, NTK vs feature learning, double descent, grokking, scaling laws, emergence-metric critiques

**2.1 Soudry, Hoffer, Nacson, Gunasekar, Srebro (2018). The Implicit Bias of Gradient Descent on Separable Data.** — JMLR 19; arXiv:1710.10345. <https://arxiv.org/abs/1710.10345> · verified: WS

- Establishes: Gradient descent on separable data converges (slowly) to the max-margin direction: the optimizer, not the loss, selects the solution.
- First refusal: **MEDIUM** → L2/L3 (the search process Gamma selects the occupant among admissible realizations) and 1b Step 2. Gamma has a parent-owned selection law (max-margin) that GMI's 'rho-cheapest admissible' phrasing does not capture; the executed frontier assumes Gamma is neutral among admissible forms.

**2.2 Cohen, Kaur, Li, Kolter, Talwalkar (2021). Gradient Descent on Neural Networks Typically Occurs at the Edge of Stability. [Follow-on: Liu, Zhang, Du, Zhao (2025). A Minimalist Example of Edge-of-Stability and Progressive Sharpening, NeurIPS 2025, arXiv:2503.02809.]** — ICLR 2021; arXiv:2103.00065. <https://arxiv.org/abs/2103.00065> · verified: WS

- Establishes: Full-batch GD drives sharpness to 2/eta and then hovers there; loss is non-monotone at short scales while decreasing over long scales (progressive sharpening then self-stabilization, proved in a two-layer example in 2025).
- First refusal: **MEDIUM** → RV-377-015 / L3 existence clause (a stable step is expressible: learning rate below 2 over the active inputs) and 1b Step 2(b). GMI's stability clause is the classical 2/lambda_max condition; the parent shows real training self-organizes to that boundary, so the executed 'stable step' gate is the linear special case of a known dynamic.

**2.3 Jacot, Gabriel, Hongler (2018). Neural Tangent Kernel: Convergence and Generalization in Neural Networks.** — NeurIPS 2018; arXiv:1806.07572. <https://arxiv.org/abs/1806.07572> · verified: WS

- Establishes: In the infinite-width limit training follows kernel gradient descent with a fixed NTK; the network behaves as a kernel machine (lazy regime), with feature learning requiring different scalings.
- First refusal: **HIGH** → RV-377-025 / L4b (generalizing memory vs gradient occupant is basis-dependent) and RV-377-034 (attention as kernel smoothing dominated by hard kNN). The NTK identifies the gradient row with a kernel-memory row in the lazy regime, collapsing GMI's memory-vs-gradient distinction at large width unless feature learning is charged; L4b must survive this identification.

**2.4 Belkin, Hsu, Ma, Mandal (2019). Reconciling modern machine-learning practice and the classical bias-variance trade-off.** — PNAS 116(32). <https://doi.org/10.1073/pnas.1903070116> · verified: WS

- Establishes: Test risk is non-monotone in capacity (double descent): it peaks at the interpolation threshold and decreases again in the over-parameterized regime.
- First refusal: **MEDIUM** → Protocol rule 17 / RV-377-041b (frontier size rule R-top vs R-best when admissibility is non-monotone in size). The non-monotonicity of admissibility in size that forced rule 17 is the double-descent phenomenon; GMI's rule is an instrument convention around a parent-owned curve.

**2.5 Varma, Shah, Kenton, Kramar, Kumar (2023). Explaining grokking through circuit efficiency. [Model capacity follow-on: arXiv:2605.09724 (2026).]** — arXiv:2309.02390. <https://arxiv.org/abs/2309.02390> · verified: WS

- Establishes: Grokking is a competition between a memorizing circuit and a more efficient but slower-to-learn generalizing circuit; a critical dataset size makes them equally efficient, predicting ungrokking and semi-grokking (confirmed).
- First refusal: **HIGH** → L4 cost crossovers and L5 acquisition order (memorizing plateau before the generalizing form; RV-377-025 Hamming-memory vs gradient occupant). A parent already states an efficiency-competition phase law between memorizing and generalizing realizations with a critical crossover and confirmed novel predictions in a real neural system — the same shape as L4/L5 at executed toy scope.

**2.6 Hoffmann, Borgeaud, Mensch, Buchatskaya, Cai, Rutherford, de Las Casas, Hendricks, Welbl, Clark, Hennigan, Noland, Millican, van den Driessche, Damoc, Guy, Osindero, Simonyan, Elsen, Rae, Vinyals, Sifre (2022). Training Compute-Optimal Large Language Models.** — NeurIPS 2022; arXiv:2203.15556. <https://arxiv.org/abs/2203.15556> · verified: WS

- Establishes: Fits loss = E + A/N^alpha + B/D^beta over 400 models; compute-optimal training scales parameters and tokens equally (Chinchilla), overturning Kaplan-style allocations.
- First refusal: **MEDIUM** → Section 3 (cost per intelligence) and gap G1/G1b (a measured price vector); L4 as a cost law. GMI's 'capability per kilo-cost' table is a toy analogue of a frontier the parent measured at scale with real prices; GMI adds revision and retention axes the parent lacks, but its cost law has no scale evidence.

**2.7 Schaeffer, Miranda, Koyejo (2023). Are Emergent Abilities of Large Language Models a Mirage?** — NeurIPS 2023 (outstanding paper); arXiv:2304.15004. <https://arxiv.org/abs/2304.15004> · verified: WS

- Establishes: Apparent emergent abilities arise from nonlinear/discontinuous metrics applied to smoothly improving per-token performance; continuous metrics remove the discontinuity.
- First refusal: **HIGH** → L3 admissibility gate (capability >= theta), section 2 plateaus, and every 'occupant flip' read from a thresholded capability; rule 16 reliability curves. GMI's admissibility gate is a discontinuous metric on a continuous capability; every executed occupant flip that is really a threshold crossing is exposed to this critique and needs a continuous-metric replication.

**2.8 Michaud, Liu, Girard, Tegmark (2023). The Quantization Model of Neural Scaling.** — NeurIPS 2023; arXiv:2303.13506. <https://arxiv.org/abs/2303.13506> · verified: WS

- Establishes: Capabilities are discrete quanta learned in order of use frequency; a power law in frequencies yields power-law loss scaling and sudden per-skill emergence.
- First refusal: **MEDIUM** → L5 and section 2 ('what is found is decided before what is cheapest'; the climbing order inert -> memory -> context -> dense). Gives a parent account of acquisition order (use frequency) that could reproduce GMI's climbing order without the cost/reachability machinery; GMI must show the order is cost-driven, not frequency-driven.

## 3. Causal representation learning and identifiability

**3.1 Schoelkopf, Locatello, Bauer, Ke, Kalchbrenner, Goyal, Bengio (2021). Toward Causal Representation Learning.** — Proceedings of the IEEE 109(5); arXiv:2102.11107. <https://arxiv.org/abs/2102.11107> · verified: WS

- Establishes: Frames CRL: recover high-level causal variables and mechanisms from low-level observations; independent-causal-mechanism and sparse-mechanism-shift principles; links to transfer and robustness.
- First refusal: **MEDIUM** → F1 RQM (target distinctions aliased under prediction) and the PRQ residual-quotient theory (5d). The 'residual inside predictive fibers' is CRL's non-identifiability of latents from observational data; the parent owns the framing, GMI owns only the finite counting bound.

**3.2 Locatello, Bauer, Lucic, Raetsch, Gelly, Schoelkopf, Bachem (2019). Challenging Common Assumptions in the Unsupervised Learning of Disentangled Representations.** — ICML 2019 (best paper); arXiv:1811.12359. <https://arxiv.org/abs/1811.12359> · verified: WS

- Establishes: Theorem: unsupervised disentanglement is impossible without inductive biases on model and data; 12,000 trained models confirm that disentangled models cannot be identified without supervision.
- First refusal: **HIGH** → Worlds W0/W1 and F1.1-F1.2 (a pure predictor cannot recover residual identities); PRQ-1/PRQ-2 and MN1-a/b (5d). The impossibility theorem is the parent form of GMI's predictive-sufficiency no-go; PRQ-1/2 is a pigeonhole restatement that the theory core itself scores as a tautology check.

**3.3 Khemakhem, Kingma, Monti, Hyvaerinen (2020). Variational Autoencoders and Nonlinear ICA: A Unifying Framework.** — AISTATS 2020; arXiv:1907.04809. <https://arxiv.org/abs/1907.04809> · verified: WS

- Establishes: iVAE: with an auxiliary observed variable and a conditionally factorial prior, deep latent-variable models become identifiable up to simple transformations.
- First refusal: **MEDIUM** → F1.3 (composition rule reconstructing target state from predictor plus residual) and F4.4 (evidence update refining target state). Shows that side information is what makes the residual recoverable — the parent form of 'developmental side-information' (MN2); GMI must show its residual bound is not the iVAE identifiability condition in disguise.

**3.4 Lachapelle, Rodriguez Lopez, Sharma, Everett, Le Priol, Lacoste, Lacoste-Julien (2022). Disentanglement via Mechanism Sparsity Regularization: A New Principle for Nonlinear ICA.** — CLeaR 2022; arXiv:2107.10098. <https://arxiv.org/abs/2107.10098> · verified: WS

- Establishes: Identifiability up to permutation when latent mechanisms are sparse in past latents/auxiliary variables, including unknown-target interventions.
- First refusal: **MEDIUM** → F2.2 (sparse dependency-aligned residual factors) and A1 factorization (RV-377-037). Sparsity of mechanisms as an identifiability principle is parent-owned; GMI's sparse residual factors are an engineering restatement without an identifiability result.

**3.5 Brehmer, De Haan, Lippe, Cohen (2022). Weakly supervised causal representation learning.** — NeurIPS 2022; arXiv:2203.16437. <https://arxiv.org/abs/2203.16437> · verified: CS

- Establishes: Paired pre/post-intervention samples (no labels) suffice to identify latent causal variables and structure; implicit latent causal models avoid explicit graph search.
- First refusal: **MEDIUM** → F4 IQL (interventions split observational aliases) and world W4. Weakly supervised interventional pairs already deliver identification; IQL must show that choosing which intervention to run by target ambiguity adds anything beyond identifiability-by-interventions.

**3.6 Ahuja, Mahajan, Wang, Bengio (2023). Interventional Causal Representation Learning.** — ICML 2023 (PMLR 202); arXiv:2209.11924. <https://proceedings.mlr.press/v202/ahuja23a.html> · verified: WS

- Establishes: Perfect do-interventions identify latent factors up to permutation and scaling via support geometry; imperfect interventions give block-affine identification.
- First refusal: **HIGH** → F4.1-F4.3 (interventions remove target ambiguity) and the W4/W9 twins. A parent theorem already says which interventions remove which aliases; IQL's 'target-quotient information value' must add predictive power over this class or trigger its own kill condition.

**3.7 von Kuegelgen, Besserve, Wendong, Gresele, Kekic, Bareinboim, Blei, Schoelkopf (2023). Nonparametric Identifiability of Causal Representations from Unknown Interventions.** — NeurIPS 2023; arXiv:2306.00542. <https://arxiv.org/abs/2306.00542> · verified: WS

- Establishes: With nonparametric mixing and causal model, one perfect intervention per node (two for general n) identifies latents and graph up to ambiguities shown to be irresolvable from interventional data.
- First refusal: **HIGH** → F4.5 (stop when remaining ambiguity is below need) and F1.4 (residual capacity); the irresolvable-ambiguity classes are the parent's lower bound. The parent both gives the sufficient intervention set and proves which ambiguities no intervention resolves — the two halves of IQL's stop rule.

**3.8 Varici, Acarturk, Shanmugam, Kumar, Tajer (2025). Score-based Causal Representation Learning: Linear and General Transformations.** — JMLR 26(112); arXiv:2402.00849. <https://jmlr.org/papers/v26/24-0194.html> · verified: WS

- Establishes: Score-function variations across interventional environments give identifiability and achievability: one stochastic hard intervention per node (linear mixing), two (general mixing), with algorithms.
- First refusal: **MEDIUM** → F4.6 (reuse of intervention structure across ecologies) and the MLX experiment rows for F1/F4. Achievability (an algorithm attaining the identifiability bound) is what GMI's F4 microscope would have to beat; the parent already supplies the constructive baseline.

## 4. Continual learning, model editing, unlearning, plasticity loss

**4.1 Bourtoule, Chandrasekaran, Choquette-Choo, Jia, Travers, Zhang, Lie, Papernot (2021). Machine Unlearning.** — IEEE S&P 2021; arXiv:1912.03817. <https://arxiv.org/abs/1912.03817> · verified: WS

- Establishes: SISA: shard, isolate, slice, aggregate — bounds the influence of a data point so unlearning retrains only the affected shard/slice; cost proportional to the affected partition.
- First refusal: **HIGH** → A1/A3 (factorized served state, dependency-tracked repair; RV-377-037: A1/A3 change cost only), L4e, and the section 5.3 E5 reduction attack that names SISA. SISA is the exact parent for 'revision cost proportional to the affected cone' with retraining as repair; the E5 compilation of the VLC row into SISA is still pending and could end the VLC novelty claim.

**4.2 Meng, Bau, Andonian, Belinkov (2022). Locating and Editing Factual Associations in GPT (ROME); Meng, Sen Sharma, Andonian, Belinkov, Bau (2023). Mass-Editing Memory in a Transformer (MEMIT).** — NeurIPS 2022 (arXiv:2202.05262); ICLR 2023 (arXiv:2210.07229). <https://arxiv.org/abs/2202.05262> · verified: WS

- Establishes: Causal tracing locates factual associations in mid-layer MLPs; rank-one (ROME) and mass (MEMIT) updates edit thousands of facts directly in weights.
- First refusal: **MEDIUM** → A3 dependency-tracked local repair, VLC ability A2 (zero collateral regression), F2.4 local residual rebuild. The parent achieves local repair without a dependency cone but pays collateral damage (Gupta 2024), which is GMI's exposure term; the executed cone result is exact only at scope.

**4.3 Mitchell, Lin, Bosselut, Manning, Finn (2022). Memory-Based Model Editing at Scale (SERAC).** — ICML 2022 (PMLR 162); arXiv:2206.06520. <https://proceedings.mlr.press/v162/mitchell22a.html> · verified: WS

- Establishes: Semi-parametric editing: edits are stored in an explicit memory, a scope classifier decides whether an input is in an edit's scope, and a counterfactual model serves in-scope inputs.
- First refusal: **HIGH** → F1 RQM (broad predictor + separately mutable residual + composition rule) and F2.3 (authoritative residual separated from serving state). SERAC is an existing RQM: F1.1-F1.3 are realized by base model, edit memory and scope classifier; only the capacity law F1.4-F1.6 remains for GMI to own.

**4.4 Hartvigsen, Sankaranarayanan, Palangi, Kim, Ghassemi (2023). Aging with GRACE: Lifelong Model Editing with Discrete Key-Value Adaptors.** — NeurIPS 2023; arXiv:2211.11031. <https://arxiv.org/abs/2211.11031> · verified: WS

- Establishes: A discrete, local codebook of edits in a layer's latent space supports thousands of sequential edits from streaming errors with minimal impact on unrelated inputs, without changing weights.
- First refusal: **HIGH** → F1/F2 (residual as a codebook adaptor), VLC A2 (no collateral regression), MN1 residual capacity. A working lifelong residual store with locality guarantees; the residual-capacity law GMI predicts (bits per predictive class) would have to be measured against GRACE's codebook growth.

**4.5 Cohen, Biran, Yoran, Globerson, Geva (2024). Evaluating the Ripple Effects of Knowledge Editing in Language Models.** — TACL 12; arXiv:2307.12976. <https://arxiv.org/abs/2307.12976> · verified: WS

- Establishes: An edit implies further facts that must change (ripple effects); proposes evaluation criteria for logical propagation and shows current editors fail them.
- First refusal: **MEDIUM** → A3 dependency cone / update geometry Delta_U (RV-377-036) and VLC A2/A3 (blast radius = cone). The parent names the dependency-cone problem for real models but has no dependency-tracked repair; GMI's executed cone is exact only at scope and untested on any real editor.

**4.6 Gupta, Rao, Anumanchipalli (2024). Model Editing at Scale leads to Gradual and Catastrophic Forgetting.** — Findings of ACL 2024; arXiv:2401.07453. <https://arxiv.org/abs/2401.07453> · verified: WS

- Establishes: Sequential ROME/MEMIT edits cause gradual then abrupt forgetting of earlier edits and downstream ability.
- First refusal: **MEDIUM** → Retention price lambda_R and the exposure term (gap G4: collateral regression priced by lambda); RV-377-032 A2. Quantifies collateral regression as a function of edit count in a real system — GMI's retention term with a measured, nonlinear shape the exact layer does not reproduce.

**4.7 Dohare, Hernandez-Garcia, Lan, Rahman, Mahmood, Sutton (2024). Loss of plasticity in deep continual learning.** — Nature 632, 768-774. <https://doi.org/10.1038/s41586-024-07711-7> · verified: WS+CS

- Establishes: Standard deep learning loses the ability to learn under continual training (ImageNet, RL); plasticity is maintained only by injecting a random non-gradient component (continual backpropagation) or L2.
- First refusal: **HIGH** → L4a revision axis (the r >= 1 occupant is the cheapest-update admissible form with fixed per-event work) and 1b Step 3; RV-377-040/041 stochastic component. Real-system evidence that the gradient realization is not admissible at high revision count without stochastic reinjection contradicts L4a's constant per-event update cost, and echoes RV-041's low-reliability stochastic occupant.

**4.8 Lyle, Zheng, Khetarpal, van Hasselt, Pascanu, Martens, Dabney (2024). Disentangling the Causes of Plasticity Loss in Neural Networks.** — arXiv:2402.18762. <https://arxiv.org/abs/2402.18762> · verified: WS

- Establishes: Plasticity loss decomposes into several independent mechanisms; no single intervention suffices, but layer normalization plus weight decay is robust across nonstationarities.
- First refusal: **MEDIUM** → L6 (instrument parameters) and the RV-377-037 mechanism-factorial method (witness-changing vs cost-changing mechanisms). A parent factorial decomposition of mechanisms in a real continual learner; GMI's factorial is exact at scope but has no real-system analogue, and plasticity is an unmodelled coordinate of theta.

## 5. External memory / RAG / retrieval-augmented and memory-augmented models

**5.1 Graves, Wayne, Danihelka (2014). Neural Turing Machines.** — arXiv:1410.5401. <https://arxiv.org/abs/1410.5401> · verified: WS

- Establishes: Couples a controller network to an external memory via differentiable attention; learns copy, sort and associative recall from examples.
- First refusal: **LOW** → L1 (memory forms M1/M5 as compiled rows) and the F1 parent list (memory-augmented networks). The parent is the memory-augmented form; GMI's claim concerns which ecology makes it the occupant, which the parent does not address.

**5.2 Lewis, Perez, Piktus, Petroni, Karpukhin, Goyal, Kuettler, Lewis, Yih, Rocktaeschel, Riedel, Kiela (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.** — NeurIPS 2020; arXiv:2005.11401. <https://arxiv.org/abs/2005.11401> · verified: WS

- Establishes: Joint model of a parametric generator and a non-parametric dense retriever over a document index; the index can be swapped without retraining.
- First refusal: **MEDIUM** → F1 RQM parent first-refusal list and L4b (generalizing memory vs gradient at r >= 1). RAG is a broad predictor plus a mutable store; F1's only residual claim is that the store's size/necessity tracks measured residual burden, which is untested.

**5.3 Khandelwal, Levy, Jurafsky, Zettlemoyer, Lewis (2020). Generalization through Memorization: Nearest Neighbor Language Models.** — ICLR 2020; arXiv:1911.00172. <https://arxiv.org/abs/1911.00172> · verified: WS

- Establishes: Interpolating a pretrained LM with kNN over a datastore of contexts lowers perplexity (15.79 on WikiText-103) with no training; memory beats retraining for rare patterns and domain shift.
- First refusal: **HIGH** → RV-377-025 / L4b (memory wins in local-transducer bases at r >= 1) and RV-377-034 (hard kNN dominates soft attention). A real-system executed instance of 'a memory form is admissible and cheaper than retraining at revision' — the L4b occupant switch in a real basis — is parent-owned.

**5.4 Borgeaud, Mensch, Hoffmann, Cai, Rutherford, Millican, van den Driessche, Lespiau, Damoc, Clark, de Las Casas, Guy, Menick, Ring, Hennigan, Huang, Maggiore, Jones, Cassirer, Brock, Paganini, Irving, Vinyals, Osindero, Simonyan, Rae, Elsen, Sifre (2022). Improving language models by retrieving from trillions of tokens (RETRO).** — ICML 2022; arXiv:2112.04426. <https://arxiv.org/abs/2112.04426> · verified: WS

- Establishes: Chunked cross-attention over a 2T-token retrieval database matches GPT-3-class performance with 25x fewer parameters; pretrained models can be RETROfitted.
- First refusal: **MEDIUM** → Section 3 cost per intelligence and L4 (description cost traded against query/store cost). A measured capability-per-parameter trade between compiled (weights) and stored (index) realizations at scale; GMI's toy table has the same shape without scale evidence.

**5.5 Wu, Rabe, Hutchins, Szegedy (2022). Memorizing Transformers.** — ICLR 2022 (spotlight); arXiv:2203.08913. <https://arxiv.org/abs/2203.08913> · verified: WS

- Establishes: Approximate kNN lookup into a non-differentiable memory of past (key, value) pairs improves language modeling up to 262K tokens and lets the model use newly defined theorems at test time.
- First refusal: **MEDIUM** → L5 (context-conditioned memory forms) and F1.6 (avoid full predictor replacement when residual updates are sparse). Test-time use of newly defined objects without retraining is the F1.6 ability in a real system; GMI's residual law would have to predict the memory-size/return curve the parent measured.

**5.6 Asai, Wu, Wang, Sil, Hajishirzi (2024). Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection.** — ICLR 2024 (oral); arXiv:2310.11511. <https://arxiv.org/abs/2310.11511> · verified: WS

- Establishes: On-demand retrieval plus reflection tokens with which the model critiques its own retrieval and generation; improves factuality without an external verifier.
- First refusal: **MEDIUM** → F3.7 (abstain or serve the incumbent while unresolved) and A4 verify-before-swap with a weak, non-independent verifier (twin W8). Shows what self-verification buys and where it fails; F3.3's insistence on an independent verifier is the difference GMI must measure, and W8 is the parent's regime.

**5.7 Das, Chaudhury, Nelson, Melnyk, Swaminathan, Dai, Lozano, Kollias, Chenthamarakshan, Navratil, Dan, Chen (2024). Larimar: Large Language Models with Episodic Memory Control.** — ICML 2024; arXiv:2403.11901. <https://arxiv.org/abs/2403.11901> · verified: WS

- Establishes: A brain-inspired episodic memory controller gives one-shot knowledge updates and selective forgetting without retraining, 8-10x faster than editing baselines.
- First refusal: **HIGH** → F1/F2 (authoritative residual memory separate from serving weights) and A2 authority/serving separation. An RQM/VRQM-shaped real system with one-shot revisions and selective forgetting already exists; F2's residual claim reduces to whether versioning concentrates in this memory under retention pressure.

**5.8 Behrouz, Zhong, Mirrokni (2025). Titans: Learning to Memorize at Test Time.** — NeurIPS 2025; arXiv:2501.00663. <https://arxiv.org/abs/2501.00663> · verified: WS

- Establishes: A neural long-term memory module updates its own weights at test time by a surprise-driven gradient rule with adaptive forgetting, combined with attention for short-term context.
- First refusal: **MEDIUM** → L5 (context-conditioned memory vs in-weights learner) and L4a (test-time gradient writes to a memory module as the cheapest-update form). Blurs GMI's memory/gradient dichotomy: the occupant is a gradient-updated memory; L4b's basis-dependent split must accommodate hybrid rows before the executed table can be called a law.

## 6. Mixture-of-experts and conditional computation

**6.1 Jacobs, Jordan, Nowlan, Hinton (1991). Adaptive Mixtures of Local Experts.** — Neural Computation 3(1), 79-87. <https://doi.org/10.1162/neco.1991.3.1.79> · verified: WS

- Establishes: A gating network and local expert networks trained competitively so that experts specialize on sub-regions of the input.
- First refusal: **LOW** → F5 LMHM parent list (MoE) and L2 (conditional realization). Static experts of one family; F5's residual (development-time change of a factor's realization family) is not addressed.

**6.2 Shazeer, Mirhoseini, Maziarz, Davis, Le, Hinton, Dean (2017). Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer.** — ICLR 2017; arXiv:1701.06538. <https://arxiv.org/abs/1701.06538> · verified: WS

- Establishes: Sparse gating over thousands of experts gives >1000x capacity at near-constant compute; load-balancing losses make conditional computation trainable at scale.
- First refusal: **MEDIUM** → F5.6/F5.8 and RV-377-043 (heterogeneous mesh); section 5.3 E5 reduction into sparse MoE. Sparse conditional computation is the parent GMI must compile the LMHM row into; the executed mesh differs only in per-factor family change, which the E5 attack has not yet tested.

**6.3 Fedus, Zoph, Shazeer (2022). Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity.** — JMLR 23; arXiv:2101.03961. <https://arxiv.org/abs/2101.03961> · verified: CS

- Establishes: Top-1 routing with constant per-token compute; 7x pretraining speedup at equal FLOPs; identifies routing instabilities and remedies.
- First refusal: **MEDIUM** → RV-377-033 CP ability B2 (update cost independent of the number of inactive phenotypes). Per-token compute independent of inactive experts is MoE's defining property; CP's B2 is a parent product and only the compile/interpret crossover H* is GMI's.

**6.4 Clark, de las Casas, Guy, Mensch, Paganini, Hoffmann, Damoc, Hechtman, Cai, Borgeaud, van den Driessche, Rutherford, Hennigan, Johnson, Millican, Cassirer, Jones, Buchatskaya, Budden, Sifre, Osindero, Vinyals, Rae, Elsen, Kavukcuoglu, Simonyan (2022). Unified Scaling Laws for Routed Language Models.** — ICML 2022 (oral); arXiv:2202.01169. <https://arxiv.org/abs/2202.01169> · verified: WS

- Establishes: Performance of routed models scales as a bilinear law in parameter count and expert count; defines an effective parameter count and compares three routing techniques quantitatively.
- First refusal: **HIGH** → L4 and section 3 (cost laws as crossovers on two independent cost axes); L4b basis-dependence. A measured two-axis cost law with crossovers for conditional computation already exists at scale; GMI's H*/r*/lambda* crossovers are toy analogues with no scale evidence.

**6.5 Krajewski, Ludziejewski, Adamczewski, Pioro, Krutul, Antoniak, Ciebiera, Krol, Odrzygozdz, Sankowski, Cygan, Jaszczur (2024). Scaling Laws for Fine-Grained Mixture of Experts. [Companion: Abnar et al. (2025). Parameters vs FLOPs: Scaling Laws for Optimal Sparsity for MoE Language Models, ICML 2025, arXiv:2501.12370.]** — ICML 2024; arXiv:2402.07871. <https://arxiv.org/abs/2402.07871> · verified: WS

- Establishes: Expert granularity is a scaling variable; optimal granularity and optimal sparsity depend on the compute budget, and mirroring the dense FFN size is almost never optimal.
- First refusal: **MEDIUM** → L4d (materialization keeps realizations factorized) and RV-377-036 (fine vs coarse occupant by query geometry); F5.7. Optimal granularity as a function of budget is a parent-owned fine-vs-coarse occupant law; GMI's version adds query/update geometry but has no scale calibration.

**6.6 Dai, Deng, Zhao, Xu, Gao, Chen, Li, Zeng, Yu, Wu, Xie, Li, Huang, Luo, Ruan, Sui, Liang (2024). DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models.** — arXiv:2401.06066. <https://arxiv.org/abs/2401.06066> · verified: CS

- Establishes: Fine expert segmentation plus shared always-on experts increases specialization and reduces redundancy; matches dense models at 40% of the compute.
- First refusal: **MEDIUM** → F5.1 (semantic/dependency-aligned factor graph) and RV-377-043 shared-query exposure coupling (shared experts as shared factors). Shared plus routed experts is an engineering instance of shared-factor coupling; GMI's slope-30 coupling term is exact at scope and unmeasured in any MoE.

**6.7 Pfeiffer, Ruder, Vulic, Ponti (2023). Modular Deep Learning.** — TMLR; arXiv:2302.11529. <https://arxiv.org/abs/2302.11529> · verified: WS

- Establishes: Unifies modular architectures along computation function, routing function, aggregation function and training setting; modules as autonomous parameter-efficient units composed by learned or fixed routing.
- First refusal: **HIGH** → F5 in full (parent list: modular neural networks) and F5.4 (local Gamma). The survey's taxonomy already spans heterogeneous modules, learned routing and module-local training; F5's residual is only development-time family change under a measured local demand, which no executed record yet shows in a real modular system.

**6.8 Ostapenko, Su, Ponti, Charlin, Le Roux, Caccia, Sordoni (2024). Towards Modular LLMs by Building and Reusing a Library of LoRAs.** — ICML 2024 (PMLR 235); arXiv:2405.11157. <https://proceedings.mlr.press/v235/ostapenko24a.html> · verified: WS

- Establishes: Builds a library of adapters by model-based clustering and routes to them zero-shot (Arrow) from adapter parameters alone, generalizing to unseen tasks.
- First refusal: **MEDIUM** → F5.5 (unaffected factors remain authoritative during local morphogenesis) and F2.8 (heterogeneous residual realization families). Adapter libraries with zero-shot routing realize factor-local addition without global rebuild; F5 must show family change (not just adapter addition) is what the local demand predicts.

## 7. State-space models and linear attention / recurrence

**7.1 Gu, Goel, Re (2022). Efficiently Modeling Long Sequences with Structured State Spaces (S4).** — ICLR 2022 (oral); arXiv:2111.00396. <https://arxiv.org/abs/2111.00396> · verified: WS

- Establishes: A structured parameterization of state-space models computes long-range convolutions efficiently; state of the art on Long Range Arena with 60x faster generation than transformers.
- First refusal: **MEDIUM** → L1 basis families (uniform/compressed-program vs local-transducer bases) and RV-377-025 basis dependence. A compressed-state basis with a different cost signature for the same sequence tasks; L1's 'bases differ by finite bands' has a parent instance whose bands are measured.

**7.2 Gu, Dao (2023). Mamba: Linear-Time Sequence Modeling with Selective State Spaces.** — arXiv:2312.00752. <https://arxiv.org/abs/2312.00752> · verified: WS

- Establishes: Input-dependent (selective) SSM parameters give content-based reasoning in linear time; a hardware-aware scan makes the recurrence efficient without attention or MLP blocks.
- First refusal: **MEDIUM** → L4b (r >= 1 occupant is basis-dependent) and RV-377-035 (a price vector flips the occupant within the admissible set; hardware-aware design). Hardware-aware selection of a compressed-state form is RV-035's mechanism in practice; GMI's version is a frozen price column, the parent's is a measured kernel.

**7.3 Dao, Gu (2024). Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality.** — ICML 2024 (PMLR 235); arXiv:2405.21060. <https://arxiv.org/abs/2405.21060> · verified: WS

- Establishes: Proves a duality between SSMs and attention variants via structured semiseparable matrices, giving Mamba-2 with 2-8x faster core layers at equal quality.
- First refusal: **HIGH** → L1 (two bases realizing the same form with identical development tables and different cost signatures; Codex T13/T16 flattening). An algebraic duality between two bases with explicit cost accounting is exactly L1's 'compilation with a cost signature', parent-owned in the real family; GMI's executed six-basis C2 identity is a toy instance.

**7.4 Merrill, Petty, Sabharwal (2024). The Illusion of State in State-Space Models.** — ICML 2024; arXiv:2404.08819. <https://arxiv.org/abs/2404.08819> · verified: WS

- Establishes: Linear/diagonal SSMs cannot express computation outside TC^0 and so cannot track state (e.g., permutation composition) any better than transformers.
- First refusal: **MEDIUM** → L3 existence gate and L6 (which forms exist in a generator's grammar is decided by architecture and precision). Existence-gate results for a whole family are parent theorems; GMI's exact-layer existence gate (RV-015/029/031) has no general-case theorem of this kind.

**7.5 Jelassi, Brandfonbrener, Kakade, Malach (2024). Repeat After Me: Transformers are Better than State Space Models at Copying.** — ICML 2024; arXiv:2402.01032. <https://arxiv.org/abs/2402.01032> · verified: WS+AX

- Establishes: Theory and experiments: fixed-size-state models cannot copy strings longer than their state allows, while a two-layer transformer copies strings exponential in the number of heads.
- First refusal: **HIGH** → RV-377-025 / L4b (memory forms vs compressed forms) and L3 admissibility of compressed-state forms on retrieval ecologies. A theorem-level admissibility boundary between store-based and compressed-state realizations on a retrieval ecology — the exact shape of GMI's admissibility gate — is parent-owned.

**7.6 Arora, Eyuboglu, Zhang, Timalsina, Alberti, Zou, Rudra, Re (2024). Simple linear attention language models balance the recall-throughput tradeoff (Based).** — ICML 2024 (PMLR 235); arXiv:2402.18668. <https://arxiv.org/abs/2402.18668> · verified: WS+AX

- Establishes: Recall quality vs decoding throughput forms a Pareto frontier indexed by recurrent state size; Based (linear + sliding-window attention) moves along it with IO-aware kernels.
- First refusal: **HIGH** → L4 / section 3 (capability-per-cost frontier over state size) and RV-377-036 (query geometry decides the occupant). An explicit measured Pareto frontier 'recall (capability) vs state size (cost)' in real systems; GMI's frontier tables are exact-scope analogues with no scale evidence.

**7.7 Yang, Wang, Zhang, Shen, Kim (2024). Parallelizing Linear Transformers with the Delta Rule over Sequence Length (DeltaNet). [Follow-ons: Gated DeltaNet (arXiv:2412.06464); Gated DeltaNet-2 (arXiv:2605.22791, 2026).]** — NeurIPS 2024; arXiv:2406.06484. <https://arxiv.org/abs/2406.06484> · verified: WS+AX

- Establishes: A hardware-efficient algorithm trains linear transformers whose memory is updated by the delta (error-correcting) rule, improving associative recall over additive linear attention.
- First refusal: **MEDIUM** → L4a revision axis (the update law as an online error-correcting memory write) and RV-377-025 (Hamming-averaging memory admissibility). The memory-write rule is itself a design axis with measured recall consequences; GMI's memory rows fix one write rule and so cannot see this axis.

**7.8 (2026). The Impossibility Triangle of Long-Context Modeling.** — arXiv:2605.05066 (abstract-level only). <https://www.alphaxiv.org/abs/2605.05066> · verified: AX

- Establishes: Claims a proven trilemma: no sequence model simultaneously has length-independent per-step compute, bounded state size, and exact recall.
- First refusal: **HIGH** → L3/L4 admissibility-cost trade between memory and compressed forms; MN5 overcompression no-go (RV-377-036). If the theorem holds as stated, MN5's overcompression no-go is a corollary for real sequence models; GMI's executed version is exact at scope only. Verified by abstract; full statement to be read before citing as load-bearing.

## 8. Program synthesis and neuro-symbolic systems

**8.1 Gulwani, Polozov, Singh (2017). Program Synthesis.** — Foundations and Trends in Programming Languages 4(1-2). <https://doi.org/10.1561/2500000010> · verified: WS

- Establishes: Surveys synthesis as search over a program space guided by a specification: enumerative, deductive, constraint-based and statistical strategies, with cost of search as the central quantity.
- First refusal: **MEDIUM** → 1b Step 3 (program search pays Theta(|G| m) per event) and L4 (search forms occupy only r = 0 or where nothing else is admissible). The per-event cost of search as a function of grammar size is the parent's central accounting; GMI's search-row costs are one point in that space.

**8.2 Ellis, Wong, Nye, Sable-Meyer, Morales, Hewitt, Cary, Solar-Lezama, Tenenbaum (2021). DreamCoder: Growing generalizable, interpretable knowledge with wake-sleep Bayesian program learning.** — PLDI 2021; arXiv:2006.08381. <https://arxiv.org/abs/2006.08381> · verified: AX

- Establishes: Wake/abstraction/dreaming cycles grow a library of concepts and train a neural recognition model that amortizes search; solves domains from list processing to physics laws.
- First refusal: **HIGH** → F6 SCDI (developmental state = library; compiled serving = recognition network), L4f compile amortization, gap G12 (grammar-over-grammars). A real self-compiling developmental system (already ledger P5.DREAMCODER_OBJECTIVE): library growth is developmental state and the recognition net is a compiled serving form; F6's residual is only the price-driven recompile policy.

**8.3 Li, Choi, Chung, Kushman, Schrittwieser, Leblond, Eccles, Keeling, Gimeno, Dal Lago, Hubert, Choy, de Masson d'Autume, Babuschkin, Chen, Huang, Welbl, Gowal, Cherepanov, Molloy, Mankowitz, Sutherland Robson, Kohli, de Freitas, Kavukcuoglu, Vinyals (2022). Competition-Level Code Generation with AlphaCode.** — Science 378; arXiv:2203.07814. <https://arxiv.org/abs/2203.07814> · verified: AX

- Establishes: Generates millions of candidate programs, filters by example tests and clusters by behaviour to select submissions; top-54% on Codeforces.
- First refusal: **HIGH** → F3 VGSC (cheap high-entropy proposal + verifier filter) and RV-377-042 p_a coordinate. Generate-and-filter with a verifier at scale is parent-owned; VGSC's residual is only the serving/compilation lifecycle after admission.

**8.4 Bowers, Olausson, Wong, Grand, Tenenbaum, Ellis, Solar-Lezama (2023). Top-Down Synthesis for Library Learning (Stitch).** — POPL 2023; arXiv:2211.16605. <https://arxiv.org/abs/2211.16605> · verified: AX

- Establishes: Corpus-guided top-down synthesis of library abstractions with branch-and-bound; 3-4 orders of magnitude faster and less memory than DreamCoder's compression.
- First refusal: **MEDIUM** → L4f compile amortization H* (compression cost vs reuse) and F6.6 (compiler burden charged to lifetime cost). Shows the compile cost term in H* is itself movable by orders of magnitude; GMI's per-basis H* is only as stable as the compiler it charges.

**8.5 Grand, Wong, Bowers, Olausson, Liu, Tenenbaum, Andreas (2024). LILO: Learning Interpretable Libraries by Compressing and Documenting Code.** — ICLR 2024; arXiv:2310.19791. <https://arxiv.org/abs/2310.19791> · verified: WS

- Establishes: LLM synthesis plus Stitch compression plus auto-documentation grows interpretable libraries that improve later synthesis.
- First refusal: **MEDIUM** → F6.2/F6.5 (multiple serving morphologies from one developmental library) and F1 (broad predictor + symbolic residual). A neural predictor with a symbolic, separately mutable library is an RQM/SCDI hybrid in practice; GMI's forms are property vectors these systems already satisfy.

**8.6 Romera-Paredes, Barekatain, Novikov, Balog, Kumar, Dupont, Ruiz, Ellenberg, Wang, Fawzi, Kohli, Fawzi (2024). Mathematical discoveries from program search with large language models (FunSearch).** — Nature 625, 468-475. <https://doi.org/10.1038/s41586-023-06924-6> · verified: WS

- Establishes: An evolutionary loop pairing an LLM proposer with a systematic evaluator discovers new cap-set constructions and bin-packing heuristics.
- First refusal: **MEDIUM** → F3 (proposal + verifier) and L5 (reachability of new forms by search with a learned proposer). Search with a learned proposer reaches genuinely new artefacts; GMI's E3-lite neutral search has no proposer of this strength and its reachability negatives may be proposer artefacts.

**8.7 Trinh, Wu, Le, He, Luong (2024). Solving olympiad geometry without human demonstrations (AlphaGeometry).** — Nature 625, 476-482. <https://doi.org/10.1038/s41586-023-06747-5> · verified: WS

- Establishes: A language model trained on synthetic proofs proposes auxiliary constructions while a symbolic deduction engine verifies; solves 25/30 IMO geometry problems.
- First refusal: **HIGH** → F3.1-F3.3 (cheap high-entropy proposer + independent verifier) and F5.6 (heterogeneous families: neural + symbolic). A heterogeneous neural-proposer/symbolic-verifier mesh is a working parent of both F3 and F5; the property vectors are realized, and only the phase response to prices is GMI's to show.

**8.8 Novikov, Vu, Eisenberger, Dupont, Huang, Wagner, Shirobokov, Kozlovskii, Ruiz, Mehrabian, Kumar, See, Chen, Sun, Rocktaeschel, Hutter, Balog, Le, Kohli, Fawzi, Fawzi (2025). AlphaEvolve: A coding agent for scientific and algorithmic discovery.** — arXiv:2506.13131. <https://arxiv.org/abs/2506.13131> · verified: WS

- Establishes: An evolutionary coding agent with LLM ensembles and automated evaluators improved data-center scheduling, matrix-multiplication algorithms and the training of its own underlying LLM.
- First refusal: **HIGH** → L5 (search reaches new forms), section 7 / Q5 (a self-improving generator) and F3. A propose-verify-compile loop applied to its own substrate is the strongest existing instance of the self-improving generator GMI lists as a kill target for Q5.

## 9. Automated theorem proving and verifier-gated generation (LLM + proof checkers, generate-and-verify, speculative decoding as verification)

**9.1 Lample, Lacroix, Lachaux, Rodriguez, Hayat, Lavril, Ebner, Martinet (2022). HyperTree Proof Search for Neural Theorem Proving. [Predecessor: Polu, Sutskever (2020). Generative Language Modeling for Automated Theorem Proving (GPT-f), arXiv:2009.03393.]** — NeurIPS 2022; arXiv:2205.11491. <https://arxiv.org/abs/2205.11491> · verified: WS

- Establishes: An online-trained transformer prover with hypertree search learns from its own verified proof searches: Metamath 65.4% -> 82.6%, miniF2F-curriculum 31% -> 42%.
- First refusal: **HIGH** → F3.5 (accepted candidates enter authoritative developmental state) and gap G11 (developmental capital K1: does verified experience lower the next acquisition's burden). Verified candidates feeding back into development, with measured gains, is F3.5 and K1 realized in a real system; GMI's K1 evidence is a single OCM capsule.

**9.2 Xin, Ren, Song, Shao, Zhao, Wang, Liu, Zhang, Li, Huang, Yang, Su, Zhang, Wu, Li, Ruan, Ma, Guo, Zhang (2024). DeepSeek-Prover-V1.5: Harnessing Proof Assistant Feedback for Reinforcement Learning and Monte-Carlo Tree Search.** — arXiv:2408.08152. <https://arxiv.org/abs/2408.08152> · verified: WS

- Establishes: RL from Lean feedback plus RMaxTS (intrinsic-reward MCTS) for whole-proof generation: miniF2F 63.5%, ProofNet 25.3%.
- First refusal: **MEDIUM** → F3.4 (failed candidates are charged and retained by policy) and RV-377-042 p_a (generator quality) coordinate. The parent's intrinsic-reward exploration is a policy for what to do with failed candidates that GMI's VGSC row does not model; p_a is treated as fixed rather than learned.

**9.3 AlphaProof team, Google DeepMind (2025). Olympiad-level formal mathematical reasoning with reinforcement learning.** — Nature (published November 2025). <https://doi.org/10.1038/s41586-025-09833-y> · verified: WS

- Establishes: An AlphaZero-style agent trained on millions of auto-formalized problems finds Lean proofs; test-time RL on problem variants yields IMO-2024 silver-medal performance with kernel-checked proofs.
- First refusal: **HIGH** → F3 whole lifecycle (propose -> Lean verify -> learn), F6 (test-time RL = recompiling for a task at serving time), and E3 math lane (GMI_E3_PARENT_STACK M-P4). The strongest real system realizing F3 plus test-time adaptation; GMI's E3 must beat it under a matched contract, and its 'test-time RL' is a per-task recompilation F6 predicts but has not measured.

**9.4 Leviathan, Kalman, Matias (2023). Fast Inference from Transformers via Speculative Decoding.** — ICML 2023 (PMLR 202); arXiv:2211.17192. <https://arxiv.org/abs/2211.17192> · verified: WS

- Establishes: A cheap draft model proposes tokens that the target model verifies in parallel with an acceptance rule preserving the exact output distribution; 2-3x speedup governed by acceptance rate and cost ratio.
- First refusal: **HIGH** → F3 (names speculative decoding as a parent) and RV-377-042 three-region diagram (p_a* = (c_g + c_v)/c_exact). The parent's expected-speedup formula in acceptance rate alpha and cost ratio c is a closed-form phase law of the same type as p_a*; RV-042 executes the same structure with an added retention term.

**9.5 Brown, Juravsky, Ehrlich, Clark, Le, Re, Mirhoseini (2024). Large Language Monkeys: Scaling Inference Compute with Repeated Sampling.** — arXiv:2407.21787. <https://arxiv.org/abs/2407.21787> · verified: WS

- Establishes: Coverage (any correct sample) scales log-linearly with samples over four orders of magnitude; with automatic verifiers (code, proofs) coverage converts directly to performance, without them it does not.
- First refusal: **HIGH** → RV-377-042 p_a (generator quality) and F3.1 (high-entropy cheap proposal); twin W8 (weak verifier). A measured inference-time scaling law for proposal coverage and the verifier dependence of its value; RV-042's 'unverified speculation inadmissible below p_a = 1' is the parent's no-verifier case.

**9.6 Snell, Lee, Xu, Kumar (2024). Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters.** — ICLR 2025; arXiv:2408.03314. <https://arxiv.org/abs/2408.03314> · verified: WS

- Establishes: Compute-optimal allocation between revision and PRM-guided search depends on prompt difficulty; a smaller model with optimal test-time compute beats a 14x larger model on easy/medium prompts.
- First refusal: **HIGH** → L4 cost laws and section 3 (serving compute vs training compute crossover); F3's regime prediction. A compute-optimal frontier between two forms (bigger model vs verified search) measured in real systems is the shape of every GMI occupancy law, with real prices.

**9.7 Setlur, Rajaraman, Levine, Kumar (2025). Scaling Test-Time Compute Without Verification or RL is Suboptimal.** — arXiv:2502.12118. <https://arxiv.org/abs/2502.12118> · verified: WS

- Establishes: Proves verifier-based methods (RL or search) scale asymptotically better than verifier-free distillation of search traces at fixed compute, with the gap widening in test-time budget.
- First refusal: **HIGH** → F3.2/F3.3 (proposal state cannot become authoritative without an independent verifier) and RV-377-042 (unverified speculation inadmissible once the generator is fallible). A theoretical separation between verifier-gated and verifier-free forms as a function of budget is exactly RV-042's phase claim, at general scope.

**9.8 (2026). Adaptive Generate-Rank-Verify: Inference-Time Search with Costly Verification.** — arXiv:2605.17609 (abstract-level only). <https://arxiv.org/abs/2605.17609> · verified: WS

- Establishes: Formulates inference-time search with a priced verifier and adapts how many candidates to rank and verify to the verification cost.
- First refusal: **MEDIUM** → RV-377-042 (priced verification c_v; VGSC region where lambda x exposure > c_v). Directly prices the verifier in the search policy, the coordinate RV-042 freezes; to be read in full before the VGSC E5 attack.

## 10. Neural architecture search and morphology search

**10.1 Zoph, Le (2017). Neural Architecture Search with Reinforcement Learning.** — ICLR 2017; arXiv:1611.01578. <https://arxiv.org/abs/1611.01578> · verified: WS

- Establishes: An RNN controller trained by RL emits architectures; matches hand-designed CIFAR-10/PTB models at 800-GPU cost.
- First refusal: **LOW** → L2 Gamma (search family) and PHASE_LAW_PARENT_ATLAS section 3; L5 reachability at budget. Establishes that architecture is searchable at a price; GMI's claims are about which architecture the ecology selects, which NAS does not predict.

**10.2 Liu, Simonyan, Yang (2019). DARTS: Differentiable Architecture Search.** — ICLR 2019; arXiv:1806.09055. <https://arxiv.org/abs/1806.09055> · verified: WS

- Establishes: Continuous relaxation of the architecture space makes architecture search a bilevel gradient problem, orders of magnitude cheaper than RL/evolution.
- First refusal: **MEDIUM** → L5 discoverability gate and gap G6 (the dense learner needs 3-4 coordinated depth-3 writes and is not assembled at 10^5). Shows a Gamma under which the dense learner is trivially reachable; G6's negative is a property of GMI's discrete search family, not of the form.

**10.3 Elsken, Metzen, Hutter (2019). Neural Architecture Search: A Survey.** — JMLR 20(55); arXiv:1808.05377. <https://arxiv.org/abs/1808.05377> · verified: WS

- Establishes: Decomposes NAS into search space, search strategy and performance-estimation strategy.
- First refusal: **MEDIUM** → L2 theta = (Omega, rho, Gamma) decomposition and L3 gates. The three-way decomposition (space/strategy/estimation) is the parent of GMI's (existence/discoverability/cost) split; GMI adds only the ecology and price axes.

**10.4 Mellor, Turner, Storkey, Crowley (2021). Neural Architecture Search without Training.** — ICML 2021 (PMLR 139); arXiv:2006.04647. <https://arxiv.org/abs/2006.04647> · verified: WS

- Establishes: Overlap of activation patterns in untrained networks predicts trained accuracy, enabling NAS in seconds on one GPU.
- First refusal: **MEDIUM** → L3 existence/admissibility certified before development (planted-learner certification 0.93; L5 'existence is certified separately'). Pre-development certification of admissibility is a parent practice (zero-cost proxies); GMI's planted-learner certificate is one such proxy without the parent's validation across spaces.

**10.5 Gaier, Ha (2019). Weight Agnostic Neural Networks.** — NeurIPS 2019; arXiv:1906.04358. <https://arxiv.org/abs/1906.04358> · verified: WS

- Establishes: Topology search finds networks that solve RL tasks and reach well above chance on MNIST with a single shared random weight — the architecture alone encodes the solution.
- First refusal: **HIGH** → L5 (neutral search reaches inert transducers first: RV-377-016/023, 3/3 seeds) and L1 (a form without an update law). Neutral topology search finding inert forms that solve tasks without any learning law is the executed 'inert transducer first' result at real scale; the parent owns it.

**10.6 Gupta, Savarese, Ganguli, Fei-Fei (2021). Embodied intelligence via learning and evolution.** — Nature Communications 12; arXiv:2102.02202. <https://doi.org/10.1038/s41467-021-25874-z> · verified: WS

- Establishes: DERL evolves morphologies that learn control in environments of varying complexity; complex environments select morphologies that learn faster (a morphological Baldwin effect).
- First refusal: **HIGH** → L2 (the ecology selects the form through Gamma) and L5 (reached morphology depends on environment complexity); F5 local morphogenesis. An executed large-scale ecology -> morphology -> learnability law with a Baldwin-effect prediction; it is the embodied version of L2/L5 with real substrates, and GMI has no comparable evidence.

**10.7 White, Safari, Sukthanker, Ru, Elsken, Zela, Dey, Hutter (2023). Neural Architecture Search: Insights from 1000 Papers.** — arXiv:2301.08727. <https://arxiv.org/abs/2301.08727> · verified: AX

- Establishes: Comprehensive taxonomy of NAS including one-shot, zero-cost proxies, benchmarks and reproducibility guidance.
- First refusal: **LOW** → PHASE_LAW_PARENT_ATLAS section 3; gaps G6/G12 (reachability of search and algebraic forms by neutral search). Reference map of search families; GMI's reachability negatives should be checked against families in this taxonomy before being called results about Gamma.

## 11. Quality-diversity, MAP-Elites, novelty search, POET/open-ended evolution, artificial life

**11.1 Lehman, Stanley (2011). Abandoning Objectives: Evolution Through the Search for Novelty Alone.** — Evolutionary Computation 19(2). <https://doi.org/10.1162/EVCO_a_00025> · verified: CS

- Establishes: Rewarding behavioural novelty instead of the objective solves deceptive tasks (maze, biped) that objective-based search cannot, and drives increasing complexity.
- First refusal: **HIGH** → L5 (a search reaches the class along whose fitness there is a monotone path; no monotone path from the memory plateau to the dense learner, RV-377-023/028). GMI's reachability negatives are deception results; the parent's remedy (objective-free search) is an untested element of Gamma, so the negatives may be artefacts of a fitness-driven family.

**11.2 Mouret, Clune (2015). Illuminating search spaces by mapping elites.** — arXiv:1504.04909. <https://arxiv.org/abs/1504.04909> · verified: WS

- Establishes: MAP-Elites keeps the best solution per cell of a behaviour-descriptor space, returning a map of elites rather than a single optimum.
- First refusal: **MEDIUM** → Section 2 reachability table and F5 heterogeneous mesh (per-cell occupant); the (H, r, lambda) frontier tables as an archive. GMI's frontier tables are a MAP-Elites archive over demand coordinates with hand-enumerated rows; the parent already supplies the search that fills such an archive.

**11.3 Cully, Clune, Tarapore, Mouret (2015). Robots that can adapt like animals.** — Nature 521, 503-507; arXiv:1407.3501. <https://doi.org/10.1038/nature14422> · verified: WS

- Establishes: A pre-computed behaviour-performance map (MAP-Elites) plus Bayesian optimization at damage time lets a robot adapt in under two minutes.
- First refusal: **MEDIUM** → F6 SCDI (a precomputed repertoire of serving forms recompiled/selected at context change) and F5 local adaptation. A developmental repertoire compiled offline and selected online by a priced trial process is F6's cache/recompile policy in a real robot.

**11.4 Wang, Lehman, Clune, Stanley (2019). Paired Open-Ended Trailblazer (POET): Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions.** — GECCO 2019; arXiv:1901.01753. <https://arxiv.org/abs/1901.01753> · verified: WS

- Establishes: Co-evolves environments and agents with transfer between pairs; stepping stones reach environments unsolvable by direct optimization.
- First refusal: **HIGH** → L2/L5 (changing the ecology, not the budget, moves the plateau: RV-377-023 +0.28 vs RV-018/028) and Q5 (self-improving generator). POET already shows that ecology change rather than budget is what escapes plateaus — the executed RV-023 lesson — and supplies the generator of ecologies GMI treats as fixed.

**11.5 Hughes, Dennis, Parker-Holder, Behbahani, Mavalankar, Shi, Schaul, Rocktaeschel (2024). Open-Endedness is Essential for Artificial Superhuman Intelligence.** — ICML 2024; arXiv:2406.04268. <https://arxiv.org/abs/2406.04268> · verified: AX

- Establishes: Defines open-endedness formally as producing artefacts that are both novel and learnable from an observer's viewpoint.
- First refusal: **MEDIUM** → The C0-C3 novel-form admission rule and L5 'predict a new form' (novelty relative to an observer). The observer-relative novelty definition is the parent of GMI's admission ladder; GMI's C3 replication rung is the learnability half of the parent definition.

**11.6 Zhang, Lehman, Stanley, Clune (2024). OMNI: Open-endedness via Models of human Notions of Interestingness. [Follow-on: Faldor, Zhang, Cully, Clune (2024). OMNI-EPIC, arXiv:2405.15568.]** — ICLR 2024; arXiv:2306.01711. <https://arxiv.org/abs/2306.01711> · verified: WS

- Establishes: Uses foundation models as models of interestingness to choose which learnable tasks to pursue next in open-ended learning.
- First refusal: **LOW** → L2 ecology selection (which Omega the generator faces next). Task selection by a learned interestingness model is outside GMI's fixed-ecology frame; a threat only if GMI's E3-lite adopts a learned task generator.

**11.7 Kumar, Lu, Kirsch, Tang, Stanley, Isola, Ha (2024). Automating the Search for Artificial Life with Foundation Models (ASAL).** — arXiv:2412.17799. <https://arxiv.org/abs/2412.17799> · verified: AX

- Establishes: Vision-language foundation models search ALife substrates (Lenia, Boids, cellular automata) for target, open-ended and novel simulations.
- First refusal: **MEDIUM** → E3-lite neutral search over a primitive grammar and gap G10 (novelty measured against parent products). Supplies a novelty/open-endedness metric and a search that GMI's C1 neutral-recovery rung could reuse; without it GMI's novelty scoring is hand-made.

**11.8 Zhang, Hu, Lu, Lange, Clune (2025). Darwin Goedel Machine: Open-Ended Evolution of Self-Improving Agents.** — ICLR 2026; arXiv:2505.22954. <https://arxiv.org/abs/2505.22954> · verified: WS

- Establishes: Coding agents modify their own code, are validated on benchmarks, and are kept in an open-ended archive; self-improvements compound (SWE-bench 20% -> 50%).
- First refusal: **HIGH** → Q5 (self-improving generator), F3.5 (accepted self-modifications enter authoritative state after verification), L5. A working self-modifying verifier-gated loop over its own Gamma — the composite of F3 and Q5 GMI lists as a kill target for its generator-improvement claim.

## 12. Predictive state representations, causal states/epsilon-machines, information bottleneck, sufficient statistics

**12.1 Littman, Sutton, Singh (2001). Predictive Representations of State.** — NeurIPS 14. <https://proceedings.neurips.cc/paper/2001/hash/1e4d36177d71bbb3558e43af9577d70e-Abstract.html> · verified: WS+CS

- Establishes: State as a vector of multi-step action-conditional predictions; every system has a linear PSR with no more tests than its minimal POMDP has states.
- First refusal: **MEDIUM** → L1 (the only representation-independent object is the task-relative semantic developmental state S_Omega) and F1's broad predictive quotient S_P; GMI_PARENT_IMPORTS section 2. The predictive quotient is parent-defined and bounded; GMI's S_Omega adds task relativity but has no analogue of the PSR dimension bound.

**12.2 Shalizi, Crutchfield (2001). Computational Mechanics: Pattern and Prediction, Structure and Simplicity.** — Journal of Statistical Physics 104. <https://doi.org/10.1023/A:1010388907793> · verified: CS

- Establishes: Causal states (histories with equal conditional futures) give the unique minimal optimal predictor (epsilon-machine), with optimality and uniqueness theorems.
- First refusal: **HIGH** → L1's uniqueness claim for S_Omega and the PRQ residual (target quotient vs causal-state quotient); GENERAL_INTELLIGENCE_THEORY_PARENT_ATLAS T7. Uniqueness and minimality of the predictive quotient is a parent theorem; GMI's representation-independent state is that theorem plus a task index, and the residual bound is the fiber-size count over causal states.

**12.3 Barnett, Crutchfield (2015). Computational Mechanics of Input-Output Processes: Structured Transformations and the epsilon-Transducer.** — Journal of Statistical Physics 161. <https://doi.org/10.1007/s10955-015-1327-5> · verified: CS

- Establishes: Extends causal states to channels: the epsilon-transducer is the minimal optimal model of a structured input-output mapping.
- First refusal: **MEDIUM** → L1 (finite-state transducer flattening, Codex T13/T16) and S_Omega for input-output obligations. The minimal transducer for an obligation with inputs is parent-owned; GMI's flattening theorem is a finite special case.

**12.4 Tishby, Pereira, Bialek (1999). The Information Bottleneck Method.** — Allerton 1999; arXiv:physics/0004057. <https://arxiv.org/abs/physics/0004057> · verified: WS

- Establishes: Compress X into T preserving information about Y: a rate-distortion trade with the relevance variable defining distortion.
- First refusal: **MEDIUM** → MN5 overcompression no-go and RV-377-036 (fine vs coarse occupant); GMI_REALIZATION_PARENT_ASSUMPTION_MAP section 1 rule. Any GMI result that is a compression-vs-relevance trade after variable mapping is IB by the programme's own disposition rule; RV-036's fine-vs-coarse cells need that check.

**12.5 Still (2009). Information-theoretic approach to interactive learning.** — EPL 85, 28005; arXiv:0709.1948. <https://arxiv.org/abs/0709.1948> · verified: WS

- Establishes: Derives optimal models and action policies for an interactive learner from one objective: maximal predictive power at minimal complexity, yielding curiosity-like exploration.
- First refusal: **HIGH** → F4 IQL (intervention choice by target ambiguity rather than surprise) and its kill condition. An existing derivation of intervention policy from a predictive-quotient/complexity objective is the class IQL's kill criterion names; IQL must show target-quotient value beats predictive-information value.

**12.6 Lamb, Islam, Efroni, Didolkar, Misra, Foster, Molu, Chari, Krishnamurthy, Langford (2022). Guaranteed Discovery of Control-Endogenous Latent States with Multi-Step Inverse Models (AC-State).** — TMLR 2023; arXiv:2207.08229. <https://arxiv.org/abs/2207.08229> · verified: WS

- Establishes: A multi-step inverse model with an information bottleneck provably recovers the minimal control-endogenous state, discarding predictive but uncontrollable distractors.
- First refusal: **HIGH** → F1 (S_O differs from S_P: the task-relative quotient discards predictive distinctions) and L1 task-relativity of S_Omega; worlds W1/W4. A guaranteed, constructive discovery of a task-relative quotient that is not the predictive quotient is the constructive form of GMI's S_Omega != S_P claim.

**12.7 Shai, Marzen, Teixeira, Gietelink Oldenziel, Riechers (2024). Transformers represent belief state geometry in their residual stream.** — NeurIPS 2024; arXiv:2405.15943. <https://arxiv.org/abs/2405.15943> · verified: WS+CS

- Establishes: Transformers trained on HMM outputs linearly encode the mixed-state (belief) geometry of optimal prediction, including fractal geometries, and carry information about the entire future.
- First refusal: **HIGH** → 1b Step 5 (forward pass as proposal geometry) and Codex NPI-1...15 (quotient transfer iff q_O = g o q_pred). Real-system evidence that a trained substrate realizes the computational-mechanics predictive quotient; GMI's NPI theorems have a parent-executed instance at real scale.

**12.8 Piotrowski, Riechers, Filan, Shai (2025). Constrained belief updates explain geometric structures in transformer representations.** — arXiv:2502.01954. <https://arxiv.org/abs/2502.01954> · verified: WS+CS

- Establishes: Attention implements a constrained (parallelized, partial) Bayesian belief update; attention patterns, OV vectors and embeddings are predicted analytically from the architecture's constraints.
- First refusal: **MEDIUM** → L6 (architectural constraints decide which quotient is realized) and RV-377-034 (attention as kernel smoothing). Shows the realized quotient is the optimal one deformed by architectural constraints — a parent version of 'instrument parameters are part of theta' at real scale.

## 13. Incremental/self-adjusting computation, versioned databases, persistent data structures, build systems (for the versioned-local-compilation and lineage forms)

**13.1 Acar, Blelloch, Harper (2002/2006). Adaptive functional programming.** — POPL 2002; ACM TOPLAS 28(6) 2006. <https://doi.org/10.1145/1186632.1186634> · verified: CS

- Establishes: Dynamic dependence graphs plus change propagation make any purely functional program adaptive; update time is bounded by the trace distance between runs (e.g., logarithmic for adaptive quicksort).
- First refusal: **HIGH** → A3 dependency-tracked incremental repair (RV-377-037: A3 changes cost only; update work 669 -> 387) and VLC ability A4 (revision cost proportional to the cone); section 5.3 names self-adjusting computation. The cost law 'update cost proportional to the affected trace' is a parent theorem with a general bound; GMI's executed cone result is an instance, and the E5 compilation into this parent is pending.

**13.2 Hammer, Khoo, Hicks, Foster (2014). Adapton: Composable, Demand-Driven Incremental Computation.** — PLDI 2014. <https://doi.org/10.1145/2594291.2594324> · verified: WS

- Establishes: Demand-driven (lazy) incremental computation: only demanded outputs are recomputed, handling interleaved updates and demands and composable sub-computations.
- First refusal: **HIGH** → RV-377-033 CP ability B2 (lazy recompilation makes update cost independent of inactive phenotypes). CP's B2 is Adapton's core property; the only GMI addition is the per-basis compile/interpret crossover H*.

**13.3 Driscoll, Sarnak, Sleator, Tarjan (1989). Making data structures persistent.** — Journal of Computer and System Sciences 38(1) (STOC 1986). <https://doi.org/10.1016/0022-0000(89)90034-2> · verified: CS

- Establishes: General transformations (fat nodes, node copying) make linked structures partially or fully persistent with O(1) amortized space per update and logarithmic access to any version.
- First refusal: **HIGH** → RV-377-038 (persistence depth as a demand coordinate; encoding tournament SNAP vs LOG; H*(depth)); F2.6 residual lineage; MLX-42 (copy-on-write and persistent root remain). The snapshot vs log vs node-copying space/time trade is parent-owned with worst-case bounds; RV-038's H*(depth) crossover is an instance of that analysis, and the two untested encodings are the parent's own.

**13.4 Okasaki (1998). Purely Functional Data Structures.** — Cambridge University Press (book). <https://doi.org/10.1017/CBO9780511530104> · verified: WS+CS

- Establishes: Persistent (purely functional) structures with amortized bounds made valid under persistence via lazy evaluation; catenable lists, deques, heaps.
- First refusal: **MEDIUM** → RV-377-038 encoding tournament and L4 amortization under lineage demand (beta_lin). That amortized bounds break under persistence unless laziness is used is a cost law about lineage that GMI's per-record H* does not state.

**13.5 Mokhov, Mitchell, Peyton Jones (2018/2020). Build Systems a la Carte.** — ICFP 2018 (PACMPL 2); JFP 30 (2020). <https://doi.org/10.1145/3236774> · verified: WS

- Establishes: Build systems decompose into a scheduler and a rebuilder (dirty bit, verifying traces, constructive traces, deep constructive traces); minimality, early cutoff and correctness are analysed per design point.
- First refusal: **HIGH** → A3/A4 (verifying traces = verify-before-swap; early cutoff = cone pruning), F2.4 dependency-tracked residual rebuild, F6.4 cache/recompile policy. The rebuilder taxonomy already spans GMI's verify-before-swap vs dirty-bit distinction as named design points with correctness and minimality proofs; RV-032/037 executed two of these points.

**13.6 Budiu, Chajed, McSherry, Ryzhyk, Tannen (2023). DBSP: Automatic Incremental View Maintenance for Rich Query Languages.** — PVLDB 16(7) (VLDB 2023); VLDB Journal 2025; arXiv:2203.16684. <https://arxiv.org/abs/2203.16684> · verified: WS

- Establishes: An algebra of stream operators in which every program has a mechanically derived incremental version; covers SQL and Datalog including recursion.
- First refusal: **HIGH** → A3 incremental repair as a general operator and materialized views as the parent of CP/VLC compiled serving state. A general theorem that incremental versions exist for every program of a rich language is the general-case form of GMI's per-row cone rebuild.

**13.7 Konat, Steindorfer, Erdweg, Visser (2018). Scalable Incremental Building with Dynamic Task Dependencies (PIE).** — ASE 2018. <https://doi.org/10.1145/3238147.3238196> · verified: CS

- Establishes: An incremental build algorithm whose cost scales with the number of affected tasks, not project size, while discovering dynamic dependencies during the build.
- First refusal: **MEDIUM** → VLC ability A4 (revision cost proportional to the cone, not the whole realization). Cost-proportional-to-affected-set with dynamic dependencies is an engineering parent of A4; GMI has not shown its cone rule survives dynamically discovered dependencies.

**13.8 Huang, Xu, Liu, Elmore, Parameswaran (2017). OrpheusDB: Bolt-on Versioning for Relational Databases.** — PVLDB 10(10); arXiv:1703.02475. <https://arxiv.org/abs/1703.02475> · verified: WS

- Establishes: Adds dataset versioning to a relational database; LyreSplit partitioning trades storage against version-retrieval latency with provable bounds.
- First refusal: **MEDIUM** → RV-377-038 (history encodings: description vs replay crossover) and F2 parent list (RAG with versioned stores; transactional databases + LLM). The storage-vs-retrieval crossover for versioned data is already a parent optimization with bounds; RV-038's H*(depth) is a two-encoding special case.

## 14. Active learning / Bayesian experimental design / causal experimental design (for the interventional learner form F4)

**14.1 Lindley (1956). On a Measure of the Information Provided by an Experiment.** — Annals of Mathematical Statistics 27(4). <https://doi.org/10.1214/aoms/1177728069> · verified: CS

- Establishes: Expected information gain (expected reduction in Shannon entropy of the parameter) as the criterion for choosing experiments.
- First refusal: **HIGH** → F4.3 (IG_O(j) = A_t - E[A_{t+1} | do(j)]) and the F4 kill condition. IQL's information value is Lindley's expected information gain applied to a target functional; it is parent-owned unless target-quotient EIG differs measurably from parameter EIG, which is exactly its own kill condition.

**14.2 Foster, Ivanova, Malik, Rainforth (2021). Deep Adaptive Design: Amortizing Sequential Bayesian Experimental Design.** — ICML 2021 (PMLR 139); arXiv:2103.02438. <https://arxiv.org/abs/2103.02438> · verified: WS

- Establishes: A policy network trained offline on a lower bound of sequential EIG chooses designs in real time, non-myopically, across many deployments.
- First refusal: **HIGH** → F4.6 (learned reuse of intervention policies across structurally related ecologies). F4.6 is DAD's amortization; any IQL microscope that trains a policy is a DAD instance unless the objective differs.

**14.3 Rainforth, Foster, Ivanova, Bickford Smith (2024). Modern Bayesian Experimental Design.** — Statistical Science 39(1); arXiv:2302.14545. <https://arxiv.org/abs/2302.14545> · verified: WS

- Establishes: Reviews EIG estimation, sequential and amortized design, implicit models and the computational advances that made them practical.
- First refusal: **MEDIUM** → F4 as a whole (parent first-refusal list: Bayesian experimental design). Maps the design space F4 sits in; GMI's F4 property vector has no coordinate outside this map except the target-quotient functional.

**14.4 Eberhardt, Glymour, Scheines (2005). On the Number of Experiments Sufficient and in the Worst Case Necessary to Identify All Causal Relations Among N Variables.** — UAI 2005; arXiv:1207.1389. <https://arxiv.org/abs/1207.1389> · verified: WS

- Establishes: log2(N) + 1 multi-variable experiments suffice and are worst-case necessary to identify all causal relations among N variables (N - 1 for single-variable experiments).
- First refusal: **HIGH** → F4.5 (stop rule) and the planned RV-044 'closed-form count on the factored target'. RV-044's planned closed-form intervention count has a classical parent bound; unless GMI's count differs from the log2(N)+1 family it is a parent product.

**14.5 Toth, Lorch, Knoll, Krause, Schoelkopf, Bauer, von Kuegelgen (2022). Active Bayesian Causal Inference.** — NeurIPS 2022; arXiv:2206.02063. <https://arxiv.org/abs/2206.02063> · verified: WS+CS

- Establishes: Designs experiments maximally informative about the target causal query (not the full graph), jointly inferring a posterior over models and queries; more data-efficient than graph-focused baselines.
- First refusal: **HIGH** → F4.3 (intervention choice sensitive to target-quotient ambiguity, not whole-model uncertainty). Query-targeted EIG is precisely 'target quotient refinement rather than uncertainty reduction in a chosen model'; the IQL kill condition names this parent class.

**14.6 Zhang, Cammarata, Squires, Sapsis, Uhler (2023). Active learning for optimal intervention design in causal models.** — Nature Machine Intelligence 5, 1066-1075. <https://doi.org/10.1038/s42256-023-00719-0> · verified: CS

- Establishes: A causally informed, closed-form acquisition function with information-theoretic bounds selects interventions that move a system to a target state; applied to Perturb-CITE-seq.
- First refusal: **MEDIUM** → F4 (priced interventions toward a target) and F4.5 (stop when intervention cost dominates). Closed-form acquisition with guarantees for goal-directed intervention design is a parent baseline the F4 microscope must include as a comparison arm.

**14.7 Annadani, Tigas, Bauer, Foster (2024). Amortized Active Causal Induction with Deep Reinforcement Learning (CAASL).** — NeurIPS 2024; arXiv:2405.16718. <https://arxiv.org/abs/2405.16718> · verified: WS

- Establishes: An RL-trained transformer policy proposes interventions from history alone, without likelihoods, and transfers to shifted and real settings.
- First refusal: **MEDIUM** → F4.6 (reuse across ecologies) and F4.2 (legal intervention generator). Amortized, likelihood-free intervention policies already transfer across ecologies; F4.6 is realized, leaving only the target-quotient objective to GMI.

**14.8 Zhang, Chen, Huan (2025). Goal-Oriented Sequential Bayesian Experimental Design for Causal Learning (GO-CBED).** — arXiv:2507.07359. <https://arxiv.org/abs/2507.07359> · verified: WS+CS

- Establishes: Non-myopic, goal-oriented causal BED maximizing EIG on user-specified causal quantities with a transformer policy and normalizing-flow posteriors; outperforms graph-focused baselines under small budgets.
- First refusal: **HIGH** → F4.3 and F4.6 together (target-quantity EIG with amortized non-myopic policy). Goal-oriented EIG with amortization is F4 as a whole; the F4 discriminator must show that a quotient-defined target differs from a user-specified causal quantity in what it predicts.

## 15. Compilers/JIT/tracing and cache/memoization theory (for the self-compiling form F6 and compile-amortization laws)

**15.1 Futamura (1971; reprinted 1999). Partial Evaluation of Computation Process — An Approach to a Compiler-Compiler.** — Higher-Order and Symbolic Computation 12, 381-391 (orig. Systems, Computers, Controls 1971). <https://doi.org/10.1023/A:1010095604496> · verified: WS

- Establishes: Partially evaluating an interpreter with respect to a source program yields a compiled program; iterating yields a compiler and a compiler generator (the three projections).
- First refusal: **HIGH** → L4f compile amortization (interpretation minus lookup cost per query; source -> phenotype), F6.2 (compilers from developmental state), RV-377-033 H*. The interpreter/compiler relation and its cost accounting is parent-owned; GMI's compiled polyphenism is a Futamura projection with a reuse threshold added.

**15.2 Michie (1968). 'Memo' Functions and Machine Learning.** — Nature 218, 19-22. <https://doi.org/10.1038/218019a0> · verified: CS

- Establishes: Memoization as rote learning: a program improves its own efficiency during execution by caching results, framed explicitly as machine learning.
- First refusal: **MEDIUM** → L4d (monolithic compiled table vs recompute; lookup-native basis B2), F6.4 cache policy, section 3 (memory forms cheapest per capability). The identification of table lookup with learning, and its cost trade against recomputation, is the 1968 parent of GMI's memory rows; only the basis-dependence of the trade is GMI's.

**15.3 Karlin, Manasse, Rudolph, Sleator (1988). Competitive snoopy caching.** — Algorithmica 3, 79-119 (FOCS 1986). <https://doi.org/10.1007/BF01762111> · verified: WS

- Establishes: Introduces competitive analysis for online rent-or-buy (ski-rental) decisions: an online rule within a factor 2 of the optimal offline cost without knowing the future.
- First refusal: **HIGH** → L4e/L4f thresholds lambda*, H* and the RV-377-033/042 crossovers ('wins iff reuse exceeds the cost ratio'). Every GMI crossover H* = fixed cost / per-use saving is the ski-rental break-even, and the online version (H unknown) has a parent-owned competitive answer GMI does not yet have.

**15.4 Sleator, Tarjan (1985). Amortized efficiency of list update and paging rules.** — Communications of the ACM 28(2). <https://doi.org/10.1145/2786.2793> · verified: CS

- Establishes: Amortized analysis of move-to-front and LRU; LRU is competitive against Belady's offline MIN by a factor depending on cache size, and no online rule does better.
- First refusal: **MEDIUM** → F6.4 (cache/recompile policy responds to reuse and invalidation) and L4 amortized cost accounting. Amortized and competitive accounting for caches is the parent of every GMI 'reuse horizon' argument; GMI's H is an offline quantity the parent shows need not be known.

**15.5 Gal, Eich, Shaver, Anderson, Mandelin, Haghighat, Kaplan, Hoare, Zbarsky, Orendorff, Ruderman, Smith, Reitmaier, Bebenita, Chang, Franz (2009). Trace-based just-in-time type specialization for dynamic languages (TraceMonkey).** — PLDI 2009. <https://doi.org/10.1145/1542476.1542528> · verified: WS

- Establishes: Records hot loop traces at run time, compiles them specialized to the observed types with guards, and falls back to the interpreter when a guard fails.
- First refusal: **HIGH** → F6 (compile serving forms from observed use; guards = verification of assumptions; fallback = incumbent serving F3.7) and RV-377-033 lazy recompilation. A tracing JIT is a self-compiling developmental system with verified specialization and invalidation; F6's property vector F6.1-F6.4 is realized in every modern JavaScript engine.

**15.6 Hoelzle, Chambers, Ungar (1991). Optimizing Dynamically-Typed Object-Oriented Languages With Polymorphic Inline Caches.** — ECOOP 1991 (LNCS 512). <https://doi.org/10.1007/BFb0057013> · verified: WS

- Establishes: Per-call-site caches of lookup results that also record receiver types, which the compiler uses as type feedback when recompiling.
- First refusal: **MEDIUM** → F6.4 and F5.3 (factor-local response measurements and resource receipts as the demand signature for local recompilation). Local caches doubling as measured demand signatures for recompilation is the parent of F5.3/F5.8; GMI's local demand signature has no run-time collection mechanism.

**15.7 Darwiche, Marquis (2002). A Knowledge Compilation Map.** — JAIR 17, 229-264; arXiv:1106.1819. <https://arxiv.org/abs/1106.1819> · verified: WS

- Establishes: Organizes target compilation languages by succinctness and by which queries/transformations they support in polynomial time: compile once, answer many, at a succinctness price.
- First refusal: **HIGH** → RV-377-033 CP (knowledge compilation named as parent), L4d/L4f (interpretation vs lookup; description vs query cost), RV-377-036 (query class decides the occupant). 'The query class decides which compiled form is worth its succinctness price' is the map's organizing principle; RV-036's Delta_Q result is an instance.

**15.8 Chen, Moreau, Jiang, Zheng, Yan, Cowan, Shen, Wang, Hu, Ceze, Guestrin, Krishnamurthy (2018). TVM: An Automated End-to-End Optimizing Compiler for Deep Learning.** — OSDI 2018; arXiv:1802.04799. <https://arxiv.org/abs/1802.04799> · verified: WS

- Establishes: Graph- and operator-level optimizations with a learned cost model map one model to many hardware back-ends.
- First refusal: **MEDIUM** → F6.2 (substrate-specific serving realizations), gap G1b (measured price vector), RV-377-035 (price vector flips the occupant). Learned hardware cost models and per-substrate compilation are the parent of F6.2 and of GMI's missing measured price vector; GMI's HW column is frozen by hand.

## 16. No-free-lunch theorems and Goodhart/proxy-gaming literature

**16.1 Goldblum, Finzi, Rowan, Wilson (2023). The No Free Lunch Theorem, Kolmogorov Complexity, and the Role of Inductive Biases in Machine Learning.** — arXiv:2304.05366. <https://arxiv.org/abs/2304.05366> · verified: WS

- Establishes: Real-world problems are overwhelmingly low-Kolmogorov-complexity while uniformly sampled datasets are not; neural networks share the low-complexity preference, so NFL does not bind in practice.
- First refusal: **MEDIUM** → L2 (form = cheapest admissible on Omega) and the NFL silence region (off permutation-closed classes; Codex RP16; P0.NFL). Gives the modern statement of why structured ecologies escape NFL — the premise of any phase law — and attributes the escape to a shared simplicity bias GMI's ecology axes do not encode.

**16.2 Manheim, Garrabrant (2018). Categorizing Variants of Goodhart's Law.** — arXiv:1803.04585. <https://arxiv.org/abs/1803.04585> · verified: AX

- Establishes: Four failure modes of optimizing a proxy: regressional, extremal, causal and adversarial Goodhart.
- First refusal: **MEDIUM** → GMI_BIOSPHERE_NO_FREE_LUNCH_AND_GOODHART_GATES_V1 and L3 admissibility as a proxy metric (capability >= theta); rule 16. Provides the taxonomy GMI's Goodhart gates need; extremal Goodhart is the executed pattern of clause-writing errors from one-column calibrations (RV-035/037/038).

**16.3 Gao, Schulman, Hilton (2023). Scaling Laws for Reward Model Overoptimization. [Follow-on: Rafailov et al. (2024). Scaling Laws for Reward Model Overoptimization in Direct Alignment Algorithms, NeurIPS 2024.]** — ICML 2023 (PMLR 202); arXiv:2210.10760. <https://arxiv.org/abs/2210.10760> · verified: WS

- Establishes: Gold reward as a function of optimization against a proxy follows distinct functional forms in KL distance for RL and best-of-n, with coefficients scaling smoothly in proxy size.
- First refusal: **HIGH** → Retention price lambda and exposure (serving wrong answers), and any GMI selection on a proxy fitness (L5 fitness path as a proxy for capability). A measured law for how optimizing a proxy diverges from the true objective with optimization pressure; GMI's frontier selection on scored capability has no such term and RV-041's low-reliability occupant is a proxy-optimization artefact candidate.

**16.4 Skalse, Howe, Krasheninnikov, Krueger (2022). Defining and Characterizing Reward Hacking.** — NeurIPS 2022; arXiv:2209.13085. <https://arxiv.org/abs/2209.13085> · verified: WS

- Establishes: Formal definition of hackable proxies; for finite policy sets only trivial proxies are unhackable, because reward linearity makes unhackability very strong.
- First refusal: **MEDIUM** → L2 ('form = rho-cheapest admissible' with admissibility measured by a proxy) and the E3/E5 protected-capability protocol. Any admissibility proxy GMI freezes is hackable by the search unless it is essentially the true obligation; the protected-world firewall (G4) is the only defence and is only partially satisfied.

**16.5 Karwowski, Hayman, Bai, Kiendlhofer, Griffin, Skalse (2024). Goodhart's Law in Reinforcement Learning.** — ICLR 2024; arXiv:2310.09144. <https://arxiv.org/abs/2310.09144> · verified: AX

- Establishes: Geometric explanation of Goodharting in RL and an early-stopping rule that provably avoids it.
- First refusal: **MEDIUM** → RV-377-040/041 (stochastic admissibility as a seed lottery) and L5 fitness-path selection. Provides a principled stopping rule against proxy overoptimization that GMI's search families lack; the executed 'stochastic form wins at low reliability' may be Goodharting of the admissibility proxy.

**16.6 Kwa, Thomas, Garriga-Alonso (2024). Catastrophic Goodhart: regularizing RLHF with KL divergence does not mitigate heavy-tailed reward misspecification.** — NeurIPS 2024; arXiv:2407.14503. <https://arxiv.org/abs/2407.14503> · verified: WS

- Establishes: With heavy-tailed reward error, policies achieve arbitrarily high proxy reward with no utility gain despite KL regularization; light-tailed error is benign.
- First refusal: **MEDIUM** → L4e lambda* thresholds (bounded loss per wrong served answer) and the lifecycle exposure accounting (gap G4). GMI's lambda-linear exposure accounting assumes bounded per-answer loss; heavy-tailed exposure breaks every lambda* threshold and the parent shows regularization does not rescue it.

**16.7 Lehman, Clune, Misevic, et al. (2020). The Surprising Creativity of Digital Evolution: A Collection of Anecdotes from the Evolutionary Computation and Artificial Life Research Communities.** — Artificial Life 26(2); arXiv:1803.03453. <https://arxiv.org/abs/1803.03453> · verified: WS

- Establishes: Catalogue of evolved systems exploiting bugs, simulator defects and specification gaps rather than solving the intended task.
- First refusal: **MEDIUM** → L7 negative controls and L6 (four instrument defects found by C2 failures: RV-377-021/026/029/031); L5 neutral search. The parent already documents that search finds instrument defects before solutions; GMI's defect-closure rules 12-17 are process responses to a parent-catalogued phenomenon.

**16.8 Pan, Bhatia, Steinhardt (2022). The Effects of Reward Misspecification: Mapping and Mitigating Misaligned Models.** — ICLR 2022; arXiv:2201.03544. <https://arxiv.org/abs/2201.03544> · verified: WS

- Establishes: More capable agents exploit misspecified rewards more; capability thresholds produce phase transitions in true reward, motivating anomaly detection of aberrant policies.
- First refusal: **MEDIUM** → L3 admissibility vs capability scaling and the E3 gates (protected worlds). Phase transitions in proxy gaming as capability grows are a parent-owned phase law that GMI's ecology-driven transitions must be distinguished from at real scale.

## Strongest reduction threats ranked (top 10 across areas)

| rank | parent(s) | area | GMI claim threatened | threat | why |
|---|---|---|---|---|---|
| 1 | Karlin, Manasse, Rudolph, Sleator (1988) competitive snoopy caching / ski-rental; Sleator & Tarjan (1985) | 15 | L4e/L4f thresholds lambda*, H* and every executed crossover (RV-377-032/033/038/042) | HIGH | Every GMI crossover is a rent-or-buy break-even; the parent owns both the offline break-even and the online competitive rule for unknown reuse horizons, which GMI has not formulated. |
| 2 | Acar, Blelloch, Harper (2002/2006) self-adjusting computation; Mokhov, Mitchell, Peyton Jones (2018/2020) build systems; Budiu et al. (2023) DBSP | 13 | A1/A3/A4 mechanisms, VLC (RV-377-032/037), F2.4 | HIGH | Dependency-tracked repair with cost bounded by trace distance, verifying/constructive-trace rebuilders and mechanical incrementalization are general theorems; the executed cone results are instances and the E5 compilation into these parents is pending. |
| 3 | Varma, Shah, Kenton, Kramar, Kumar (2023) circuit efficiency | 2 | L4 cost crossovers and L5 acquisition order (memorizing before generalizing; RV-377-025) | HIGH | An efficiency-competition phase law between memorizing and generalizing realizations, with a critical crossover and confirmed novel predictions, already exists in real neural networks. |
| 4 | Lindley (1956) EIG; Toth et al. (2022) ABCI; Foster et al. (2021) DAD; Zhang, Chen, Huan (2025) GO-CBED; Eberhardt et al. (2005) | 14 | F4 IQL in full (F4.3, F4.5, F4.6; planned RV-044 closed-form count) | HIGH | Target-quantity EIG, amortized non-myopic policies and worst-case experiment counts are all parent-owned; F4's only residual is the target-quotient functional, which is its own kill condition. |
| 5 | Mitchell et al. (2022) SERAC; Hartvigsen et al. (2023) GRACE; Das et al. (2024) Larimar; Khandelwal et al. (2020) kNN-LM | 4 | F1 RQM / F2 VRQM property vectors F1.1-F1.3, F2.3; RV-377-025 memory occupant | HIGH | Broad predictor plus separately mutable residual store with scoped composition already exists in several real systems; only the residual-capacity law F1.4-F1.6 is unclaimed, and F1 is already scored IMPLEMENTATION_EQUIVALENT at the exact layer (5d). |
| 6 | Dao & Gu (2024) structured state-space duality; von Oswald et al. (2023) transformers learn in-context by GD | 7 | L1 (realization is compilation with a cost signature; identical development tables across bases) | HIGH | Proven dualities and constructions that compile one form (attention, gradient step) into another basis with explicit cost accounting realize L1 in the real families; the six-basis C2 identity is a toy instance. |
| 7 | Leviathan et al. (2023) speculative decoding; Brown et al. (2024) coverage scaling; Snell et al. (2024); Setlur et al. (2025) | 9 | F3 VGSC phase law and RV-377-042 (p_a*, three occupants, unverified speculation inadmissible) | HIGH | A closed-form speedup law in acceptance rate and cost ratio, a measured coverage scaling law, a compute-optimal frontier and a verifier-vs-no-verifier separation theorem together cover RV-042's diagram at general scope. |
| 8 | Jelassi et al. (2024) copying; Arora et al. (2024) recall-throughput; Impossibility Triangle (2026); Merrill et al. (2024) | 7 | L3/L4 admissibility-cost trade between memory and compressed forms (RV-377-025/036; MN5) | HIGH | Theorem-level admissibility boundaries and measured Pareto frontiers between store-based and compressed-state realizations exist for real sequence models; MN5's overcompression no-go is a corollary if the 2026 trilemma holds. |
| 9 | Dohare et al. (2024) loss of plasticity | 4 | L4a (r >= 1 occupant is the cheapest-update admissible form with constant per-event work); RV-377-040/041 | HIGH | Real-system evidence that the gradient realization loses admissibility with revision count unless a stochastic non-gradient component is added; plasticity is an unmodelled coordinate of theta and echoes the executed low-reliability stochastic occupant. |
| 10 | Schaeffer, Miranda, Koyejo (2023) emergence mirage | 2 | L3 thresholded admissibility (capability >= theta) and every occupant flip read from it | HIGH | GMI's gate is a discontinuous metric on a continuous capability; without a continuous-metric replication every executed flip is exposed to the metric-artefact critique. |

Near misses (HIGH entries not in the top 10, grouped):

- Futamura (1971/1999) and Darwiche & Marquis (2002): L4f compile amortization and RV-377-033/036 (interpretation vs lookup; query class decides the compiled form).
- Ahuja et al. (2023) and von Kuegelgen et al. (2023): F4 sufficiency and irresolvable-ambiguity bounds; Still (2009) and Lamb et al. (2022): F1/L1 task-relative quotient vs predictive quotient.
- Olsson et al. (2022) and Reddy (2024): L5 ordering and the in-context vs in-weights phase diagram; Gaier & Ha (2019) and Gupta et al. (2021): L5 inert-first and ecology -> morphology.
- Clark et al. (2022) and Hoffmann et al. (2022): L4/section 3 cost laws measured at scale with real prices.
- Bourtoule et al. (2021) SISA; Driscoll et al. (1989) persistence: RV-377-037 and RV-377-038 encodings.
- DreamCoder (2021), AlphaEvolve (2025), Darwin Goedel Machine (2025), AlphaProof (2025): F6 and the self-improving generator Q5.

Reading of the ranking: the three strongest threats are structural rather than empirical — competitive/online analysis (rank 1) owns the *form* of every GMI crossover, incremental-computation theory (rank 2) owns the *mechanism* of the VLC family, and circuit-efficiency grokking (rank 3) owns the *phase law* of memorizing-vs-generalizing occupancy in real networks. Ranks 4–5 are the two predicted forms (F4, F1/F2) whose property vectors are already realized by named systems; ranks 6–8 are cross-basis compilation and the memory/compressed frontier in the sequence-model literature; ranks 9–10 are real-system facts (plasticity loss, metric-induced emergence) that undercut assumptions of L4a and L3 respectively.

## Parents the executed records already answered

Where an executed RV record tests the parent's mechanism at the exact layer. 'What remains' records what the parent still owns after the record.

### RV-377-032 and RV-377-037 (VLC frontier; A1/A3/A4 factorial)

- Parents: Bourtoule et al. 2021 SISA; Acar et al. 2002/2006; Mokhov et al. 2018/2020 (verifying vs constructive traces); Konat et al. 2018; Meng et al. 2022/2023 ROME/MEMIT; Cohen et al. 2024 ripple effects
- What the record tests: Verify-before-swap (A4) is the sole witness-changing mechanism (wrong served 60 -> 0, abstentions 0 -> 96) while factorization (A1) and dependency-tracked repair (A3) change only cost (update work 101 469 -> 669 -> 387), with interactions independent of lambda; per-basis lambda* = {92, 142, 4 036}.
- What remains parent-owned / open: No parent states the witness/cost mechanism split; but the E5 compilation of the VLC row into SISA / self-adjusting computation / verifying-trace rebuilders at <= 2x cost has not been executed, so novelty stays PENDING_REDUCTION.

### RV-377-033 (Cognitive Polyphenism E1)

- Parents: Hammer et al. 2014 Adapton (laziness); Futamura 1971/1999; Darwiche & Marquis 2002; Fedus et al. 2022 Switch (compute independent of inactive experts)
- What the record tests: Lazy recompilation gives update work 2.6x below eager with one of three regimes active; compiled polyphenism enters the frontier only beyond H* ~ 1 410 reuses per rebuild in the store-native basis.
- What remains parent-owned / open: B2 and the compile/interpret crossover are parent products (Adapton, Futamura, KC map); the only GMI-owned statement is the per-basis H* table.

### RV-377-034 (attention family at D1)

- Parents: Vaswani et al. 2017; Khandelwal et al. 2020 kNN-LM; Jacot et al. 2018 NTK (kernel regime); Piotrowski et al. 2025
- What the record tests: Similarity-weighted retrieval with a fixed linear kernel has a closed-form admissibility region, is dominated by hard nearest-neighbour averaging everywhere, and is cheaper only where NORMALIZE/SCORE are native (4-7%).
- What remains parent-owned / open: The kernel-smoothing reading of attention and the NTK identification of gradient with kernel memory mean the executed dominance is expected from the parents; a temperature axis (declared) is needed before any claim.

### RV-377-035 (hardware-priced column)

- Parents: Clark et al. 2022 (two cost axes); Chen et al. 2018 TVM (learned cost models); Hooker 2020 hardware lottery (ledger P9A); Hoffmann et al. 2022
- What the record tests: A price vector flips the occupant on 168/168 admissible cells and 0/56 inadmissible cells: price acts only inside the admissible set (L3 before L4).
- What remains parent-owned / open: Parents measure price effects at scale; the executed qualifier 'only within the admissible set' is GMI's, but the price column is frozen by hand (G1b measured vector still open).

### RV-377-036 (query vs update geometry, MN5)

- Parents: Darwiche & Marquis 2002 (query class decides compiled form); Arora et al. 2024 recall-throughput; Tishby et al. 1999 IB; Krajewski et al. 2024 granularity
- What the record tests: Query scope and update cone select the occupant independently; the coarse monolith wins only native-lookup x global-query x zero-update cells; no scalar dependency coordinate reproduces the table.
- What remains parent-owned / open: The parents own the query-class principle and the recall/state-size frontier; GMI owns only the executed independence of the two geometries at scope.

### RV-377-038 (persistence / lineage encodings)

- Parents: Driscoll et al. 1989; Okasaki 1998; Huang et al. 2017 OrpheusDB
- What the record tests: Persistence demand (legal historical queries) makes single-version forms inadmissible; snapshot vs undo-log encodings flip with depth through H*(depth) = description surplus / replay gap in all six columns.
- What remains parent-owned / open: Two of the parent's four encodings (copy-on-write, persistent root) are untested (MLX-42); the parent's worst-case bounds subsume the executed crossover.

### RV-377-042 (Verifier-Gated Speculative Compiler)

- Parents: Leviathan et al. 2023 speculative decoding; Brown et al. 2024 coverage; Setlur et al. 2025; Li et al. 2022 AlphaCode; Lample et al. 2022 HTPS
- What the record tests: Three occupants along generator quality p_a with p_a* = (c_g + c_v)/c_exact; unverified speculation inadmissible below p_a = 1; VGSC serves 0 wrong answers; reuse crossover H* ~ 120 in scan-store columns and none in B2.
- What remains parent-owned / open: The acceptance-rate/cost-ratio law and the verifier-vs-verifier-free separation are parent-owned at general scope; GMI adds the retention term lambda and the basis-dependence of H*, both at scope only. C1 neutral recovery open.

### RV-377-043 (Locally Morphogenetic Heterogeneous Mesh)

- Parents: Shazeer et al. 2017; Pfeiffer et al. 2023 modular deep learning; Ostapenko et al. 2024; Dai et al. 2024 DeepSeekMoE (shared experts); Mouret & Clune 2015 MAP-Elites (per-cell occupant)
- What the record tests: Per-factor family fixed by the factor's own (exposure, overhead) coordinates; frontier meshes nested in exposure order; greedy factor-local flips reach the frontier mesh 108/108; non-additivity = shared-query exposure x lambda (slope 30, column-invariant).
- What remains parent-owned / open: The parents own heterogeneous modules, routing and shared factors; GMI owns the executed local-threshold law and the coupling slope at scope. The E5 compilation into sparse MoE is untested.

### RV-377-040 / 041 / 041b (stochastic admissibility, reliability q)

- Parents: Dohare et al. 2024 (random non-gradient component); Karwowski et al. 2024 (early stopping vs Goodhart); Gao et al. 2023 overoptimization; Lehman & Stanley 2011 novelty
- What the record tests: Admissibility of a stochastic form is a distribution over seeds (5% admissible); at low declared reliability the stochastic search form is the frontier occupant on 56/56 cells in four columns.
- What remains parent-owned / open: The parents suggest the low-reliability occupant may be proxy overoptimization (Goodhart) of the admissibility metric; gap G14 (charge failed draws) is open.

### RV-377-029 / 031 (precision and accumulator semantics)

- Parents: Merrill & Sabharwal 2023 (log-precision TC^0 bound); Merrill et al. 2024 (SSMs in TC^0)
- What the record tests: FRAC_BITS = 4 makes Bayesian averaging over > 16 hypotheses underflow; the probabilistic row is admissible only at full observation and never the occupant at 8 bits; a wide-accumulator macro restored C2.
- What remains parent-owned / open: Precision-limited existence is a parent theorem class; the executed instances are instrument facts (L6), not laws.

### RV-377-023 (earlier record cited by L5: diversity -> context-conditioned memory)

- Parents: Chan et al. 2022 (ledger P4-LB); Garg et al. 2022; Olsson et al. 2022; Reddy 2024; Wang et al. 2019 POET (ecology change moves the plateau)
- What the record tests: Sign-flip task diversity moves the neutral-search plateau by +0.28 and produces the context-conditioned class before any in-weights learner (3/3 seeds), whereas a 10x budget alone did not.
- What remains parent-owned / open: Parents own the mechanism, the phase diagram and the ecology-over-budget lesson; GMI's contribution is the label-free exact-layer replication only.

### RV-377-025 (memory vs gradient occupant is basis-dependent)

- Parents: Khandelwal et al. 2020 kNN-LM; Jacot et al. 2018 NTK; Jelassi et al. 2024; Varma et al. 2023
- What the record tests: At r >= 1 the generalizing memory wins in local-transducer bases and the gradient row in uniform/compressed-program bases (1 569/1 586 cells); Hamming-averaging admissible iff local curvature a <= 7/16.
- What remains parent-owned / open: The memory-vs-parametric occupant switch and its admissibility boundary are parent-owned in real families; the closed-form curvature bound is GMI's at scope.

## Consequence for the novelty residual

1. No executed GMI law is without a parent that states its *shape* (crossover, admissibility boundary, mechanism split) in some real family; what the executed records add is the per-basis/per-column instantiation and the separation results (price only inside the admissible set; witness vs cost mechanisms; two geometries; reliability index).
2. Of the six predicted forms, F1/F2 (SERAC, GRACE, Larimar, kNN-LM), F3 (speculative decoding, AlphaCode, HTPS, AlphaProof), F4 (ABCI, DAD, GO-CBED), F5 (modular deep learning, LoRA libraries) and F6 (tracing JITs, DreamCoder, Cully 2015) each have a named parent system realizing most of the frozen property vector; the C2 parent-non-reduction rung is therefore the binding rung for every form, and the E5 compilation attack should be run against the parents named here before any C1 neutral-recovery run.
3. Three parent facts should enter the theory core as new coordinates or caveats before the next freeze: plasticity loss (L4a's constant per-event update cost is false at high revision count in real learners), metric-induced emergence (L3's thresholded admissibility needs a continuous-metric twin), and heavy-tailed exposure (L4e's lambda-linear accounting needs a tail condition).

Generated by `build_parent_literature_ledger_v2.py` (scratchpad); 127 works / 127 verified.

"""Builder for GMI_TRANSFORMER_MICROFEATURE_REGISTRY_V1.json and its rendered markdown.

The registry is a machine-readable microfeature atlas for the neural / LLM / Transformer layer of the GMI programme.
Every entry carries the seven fields section 1 of GMI_NEURAL_LLM_TRANSFORMER_MICROFEATURE_CALCULUS_V1.md requires
for a feature explanation to be ACCEPTED, plus the theorem/receipt/experiment/claim-level bookkeeping the programme uses.

A typed location is NOT evidence. `evidence_status` is the only load-bearing epistemic field, and it is assigned by the
rule in `EVIDENCE_RULE` below. PROVED_AT_SCOPE is used only where an executed X-TMT check in
GMI_TRANSFORMER_MICROFEATURE_EXACT_RECEIPT_V1.json covers the statement made about THAT feature -- and every X-TMT check
is a MATHEMATICAL IMPLEMENTATION CHECK on a finite enumerated scope, never evidence about a trained neural network.

Run: python3 -m gmi_microscope.registry
"""
from __future__ import annotations

import json
import os

from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
JSON_PATH = os.path.join(ROOT, "GMI_TRANSFORMER_MICROFEATURE_REGISTRY_V1.json")
MD_PATH = os.path.join(ROOT, "GMI_TRANSFORMER_MICROFEATURE_REGISTRY_V1.md")
RECEIPT_PATH = os.path.join(ROOT, "GMI_TRANSFORMER_MICROFEATURE_EXACT_RECEIPT_V1.json")

TYPE_ALPHABET = {
    "C": "compiler / interface / tokenization / semantic interpretation",
    "S": "state representation / coordinates / embeddings",
    "R": "routing / dependency selection / composition",
    "T": "local transform / nonlinear computation",
    "N": "normalization / gauge / conditioning",
    "U": "update / credit / optimizer / development schedule",
    "H": "history / memory / cache / persistence",
    "V": "verifier / authority / admission / abstention",
    "G": "morphogenesis / factor split-merge / architecture change",
    "P": "physical implementation / precision / IO / parallelism",
    "D": "decision / decoding / sampling / action selection",
}

DELTA_F = ["ΔL_sem", "ΔL_gen", "ΔL_rob", "ΔL_cal", "ΔB_train", "ΔB_serve", "ΔB_mem", "ΔB_comm", "ΔB_update", "ΔB_verify", "ΔB_search"]

CLAIM_LEVELS = ["PROVED_AT_SCOPE", "PARENT_THEOREM_UNDER_ASSUMPTIONS", "EMPIRICALLY_SUPPORTED_AT_TIER_X", "REGISTERED_FOR_EXPERIMENT",
                "REDUCED_TO_PARENT", "FALSIFIED_AND_REPLACED", "OPEN_BLOCKING", "OPEN_NONBLOCKING", "OUT_OF_SCOPE"]

# EMPIRICALLY_SUPPORTED_AT_TIER_X is a schema with a tier slot. Only the tiers declared here may instantiate it.
TIERS = {
    "S": "synthetic exact microscope at laptop scope, freeze-before-run, exactly reproducible (a REVIVAL_LEDGER_TF record). "
         "This is NOT evidence about a trained neural network; it is a measured quantity in a declared synthetic ecology.",
}

EVIDENCE_RULE = {
    "PROVED_AT_SCOPE": "an executed X-TMT check in GMI_TRANSFORMER_MICROFEATURE_EXACT_RECEIPT_V1.json states and verifies, on a finite "
                       "enumerated scope, the claim this entry makes about this feature. The check is a mathematical implementation check.",
    "PARENT_THEOREM_UNDER_ASSUMPTIONS": "a published theorem (cited in parent_literature) settles the entry's claim under assumptions "
                                        "stated in the entry, but no X-TMT check in this programme covers it.",
    "EMPIRICALLY_SUPPORTED_AT_TIER_S": "a frozen-before-run microscope in this repository measured the entry's claim and it held; the tier "
                                       "is synthetic-exact, not neural.",
    "REGISTERED_FOR_EXPERIMENT": "a B2.x row of GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md and/or an MLX row of "
                                 "GMI_ML_THEORY_EXPERIMENT_MATRIX_V1.md registers the response law; not yet executed.",
    "OPEN_NONBLOCKING": "the feature has a lawful typed location and a kill condition, but no theorem, no receipt check and no registered "
                        "row decides its response law; nothing else in the programme is blocked by it.",
}

FEATURES = []


def F(fid, name, exact_definition, gmi_type, gmi_type_note, preserved, not_preserved, mechanism_hypothesis,
      components, direction, negative_twin, impl_alt, parents, formal_theorem, experiment, kill, status,
      hidden_cost_rule, section):
    """Append one registry entry. `parents` is a list of (citation, owns) or (citation, owns, 'verified')."""
    pl = []
    for p in parents:
        e = {"citation": p[0], "owns": p[1]}
        if len(p) < 3 or p[2] != "verified":
            e["citation_status"] = "to_verify"
        else:
            e["citation_status"] = "verified_in_GMI_PARENT_LITERATURE_LEDGER_V2"
        pl.append(e)
    FEATURES.append({
        "id": fid, "name": name, "exact_definition": exact_definition,
        "gmi_type": list(gmi_type), "gmi_type_note": gmi_type_note,
        "semantic_invariance": {"preserved": preserved, "not_preserved": not_preserved},
        "mechanism_hypothesis": mechanism_hypothesis,
        "resource_effect": {"components": components, "direction": direction},
        "negative_twin": negative_twin,
        "implementation_equivalent_alternative": impl_alt,
        "parent_literature": pl,
        "formal_theorem": formal_theorem,
        "experiment": experiment,
        "kill_condition": kill,
        "evidence_status": status,
        "hidden_cost_rule": hidden_cost_rule,
        "calculus_section": section,
    })


def TH(tmt, check):
    return {"tmt": tmt, "receipt_check": check, "receipt": "GMI_TRANSFORMER_MICROFEATURE_EXACT_RECEIPT_V1.json",
            "check_kind": "MATH_IMPLEMENTATION_CHECK__NOT_EMPIRICAL_NEURAL_EVIDENCE"}


# verified citations reused from GMI_PARENT_LITERATURE_LEDGER_V2.json (area id in the comment)
V_VASWANI = ("Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin (2017). Attention Is All You Need, NeurIPS 2017", None, "verified")
V_ELHAGE = ("Elhage, Nanda, Olsson, Henighan, Joseph, Mann, Askell, Bai, Chen, et al. (2021). A Mathematical Framework for Transformer Circuits, Transformer Circuits Thread", None, "verified")
V_OLSSON = ("Olsson, Elhage, Nanda, Joseph, DasSarma, Henighan, et al. (2022). In-context Learning and Induction Heads, Transformer Circuits Thread / arXiv:2209.11895", None, "verified")
V_ZHOU_LEN = ("Zhou, Bradley, Littwin, Razin, Saremi, Susskind, Bengio, Nakkiran (2023). What Algorithms can Transformers Learn? A Study in Length Generalization, ICLR 2024", None, "verified")
V_MERRILL_PAR = ("Merrill, Sabharwal (2023). The Parallelism Tradeoff: Limitations of Log-Precision Transformers, TACL 11", None, "verified")
V_GARG = ("Garg, Tsipras, Liang, Valiant (2022). What Can Transformers Learn In-Context? A Case Study of Simple Function Classes, NeurIPS 2022", None, "verified")
V_VONOSWALD = ("von Oswald, Niklasson, Randazzo, Sacramento, Mordvintsev, Zhmoginov, Vladymyrov (2023). Transformers learn in-context by gradient descent, ICML 2023", None, "verified")
V_REDDY = ("Reddy (2024). The mechanistic basis of data dependence and abrupt learning in an in-context classification task, ICLR 2024", None, "verified")
V_SOUDRY = ("Soudry, Hoffer, Nacson, Gunasekar, Srebro (2018). The Implicit Bias of Gradient Descent on Separable Data, JMLR 19", None, "verified")
V_COHEN_EOS = ("Cohen, Kaur, Li, Kolter, Talwalkar (2021). Gradient Descent on Neural Networks Typically Occurs at the Edge of Stability, ICLR 2021", None, "verified")
V_JACOT = ("Jacot, Gabriel, Hongler (2018). Neural Tangent Kernel: Convergence and Generalization in Neural Networks, NeurIPS 2018", None, "verified")
V_BELKIN = ("Belkin, Hsu, Ma, Mandal (2019). Reconciling modern machine-learning practice and the classical bias-variance trade-off, PNAS 116(32)", None, "verified")
V_VARMA = ("Varma, Shah, Kenton, Kramar, Kumar (2023). Explaining grokking through circuit efficiency, arXiv:2309.02390", None, "verified")
V_HOFFMANN = ("Hoffmann, Borgeaud, Mensch, Buchatskaya, Cai, Rutherford, et al. (2022). Training Compute-Optimal Large Language Models, NeurIPS 2022", None, "verified")
V_SCHAEFFER = ("Schaeffer, Miranda, Koyejo (2023). Are Emergent Abilities of Large Language Models a Mirage?, NeurIPS 2023", None, "verified")
V_MICHAUD = ("Michaud, Liu, Girard, Tegmark (2023). The Quantization Model of Neural Scaling, NeurIPS 2023", None, "verified")
V_BOURTOULE = ("Bourtoule, Chandrasekaran, Choquette-Choo, Jia, Travers, Zhang, Lie, Papernot (2021). Machine Unlearning, IEEE S&P 2021", None, "verified")
V_MENG = ("Meng, Bau, Andonian, Belinkov (2022). Locating and Editing Factual Associations in GPT (ROME), NeurIPS 2022; Meng et al. (2023). Mass-Editing Memory in a Transformer (MEMIT), ICLR 2023", None, "verified")
V_MITCHELL = ("Mitchell, Lin, Bosselut, Manning, Finn (2022). Memory-Based Model Editing at Scale (SERAC), ICML 2022", None, "verified")
V_GRACE = ("Hartvigsen, Sankaranarayanan, Palangi, Kim, Ghassemi (2023). Aging with GRACE: Lifelong Model Editing with Discrete Key-Value Adaptors, NeurIPS 2023", None, "verified")
V_RIPPLE = ("Cohen, Biran, Yoran, Globerson, Geva (2024). Evaluating the Ripple Effects of Knowledge Editing in Language Models, TACL 12", None, "verified")
V_GUPTA_EDIT = ("Gupta, Rao, Anumanchipalli (2024). Model Editing at Scale leads to Gradual and Catastrophic Forgetting, Findings of ACL 2024", None, "verified")
V_DOHARE = ("Dohare, Hernandez-Garcia, Lan, Rahman, Mahmood, Sutton (2024). Loss of plasticity in deep continual learning, Nature 632", None, "verified")
V_LYLE = ("Lyle, Zheng, Khetarpal, van Hasselt, Pascanu, Martens, Dabney (2024). Disentangling the Causes of Plasticity Loss in Neural Networks, arXiv:2402.18762", None, "verified")
V_NTM = ("Graves, Wayne, Danihelka (2014). Neural Turing Machines, arXiv:1410.5401", None, "verified")
V_RAG = ("Lewis, Perez, Piktus, Petroni, Karpukhin, Goyal, et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks, NeurIPS 2020", None, "verified")
V_KNNLM = ("Khandelwal, Levy, Jurafsky, Zettlemoyer, Lewis (2020). Generalization through Memorization: Nearest Neighbor Language Models, ICLR 2020", None, "verified")
V_RETRO = ("Borgeaud, Mensch, Hoffmann, Cai, Rutherford, Millican, et al. (2022). Improving language models by retrieving from trillions of tokens (RETRO), ICML 2022", None, "verified")
V_MEMTRANS = ("Wu, Rabe, Hutchins, Szegedy (2022). Memorizing Transformers, ICLR 2022", None, "verified")
V_SELFRAG = ("Asai, Wu, Wang, Sil, Hajishirzi (2024). Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection, ICLR 2024", None, "verified")
V_LARIMAR = ("Das, Chaudhury, Nelson, Melnyk, Swaminathan, et al. (2024). Larimar: Large Language Models with Episodic Memory Control, ICML 2024", None, "verified")
V_TITANS = ("Behrouz, Zhong, Mirrokni (2025). Titans: Learning to Memorize at Test Time, NeurIPS 2025", None, "verified")
V_JACOBS = ("Jacobs, Jordan, Nowlan, Hinton (1991). Adaptive Mixtures of Local Experts, Neural Computation 3(1)", None, "verified")
V_SHAZEER_MOE = ("Shazeer, Mirhoseini, Maziarz, Davis, Le, Hinton, Dean (2017). Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer, ICLR 2017", None, "verified")
V_SWITCH = ("Fedus, Zoph, Shazeer (2022). Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity, JMLR 23", None, "verified")
V_CLARK_ROUTED = ("Clark, de las Casas, Guy, Mensch, Paganini, Hoffmann, et al. (2022). Unified Scaling Laws for Routed Language Models, ICML 2022", None, "verified")
V_KRAJEWSKI = ("Krajewski, Ludziejewski, Adamczewski, Pioro, Krutul, et al. (2024). Scaling Laws for Fine-Grained Mixture of Experts, ICML 2024", None, "verified")
V_DEEPSEEKMOE = ("Dai, Deng, Zhao, Xu, Gao, Chen, Li, Zeng, Yu, et al. (2024). DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models, arXiv:2401.06066", None, "verified")
V_MODULAR = ("Pfeiffer, Ruder, Vulic, Ponti (2023). Modular Deep Learning, TMLR", None, "verified")
V_LORALIB = ("Ostapenko, Su, Ponti, Charlin, Le Roux, Caccia, Sordoni (2024). Towards Modular LLMs by Building and Reusing a Library of LoRAs, ICML 2024", None, "verified")
V_S4 = ("Gu, Goel, Re (2022). Efficiently Modeling Long Sequences with Structured State Spaces (S4), ICLR 2022", None, "verified")
V_MAMBA = ("Gu, Dao (2023). Mamba: Linear-Time Sequence Modeling with Selective State Spaces, arXiv:2312.00752", None, "verified")
V_SSD = ("Dao, Gu (2024). Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality, ICML 2024", None, "verified")
V_ILLUSION = ("Merrill, Petty, Sabharwal (2024). The Illusion of State in State-Space Models, ICML 2024", None, "verified")
V_JELASSI = ("Jelassi, Brandfonbrener, Kakade, Malach (2024). Repeat After Me: Transformers are Better than State Space Models at Copying, ICML 2024", None, "verified")
V_BASED = ("Arora, Eyuboglu, Zhang, Timalsina, Alberti, Zou, Rudra, Re (2024). Simple linear attention language models balance the recall-throughput tradeoff (Based), ICML 2024", None, "verified")
V_DELTANET = ("Yang, Wang, Zhang, Shen, Kim (2024). Parallelizing Linear Transformers with the Delta Rule over Sequence Length (DeltaNet), NeurIPS 2024", None, "verified")
V_SPEC = ("Leviathan, Kalman, Matias (2023). Fast Inference from Transformers via Speculative Decoding, ICML 2023", None, "verified")
V_MONKEYS = ("Brown, Juravsky, Ehrlich, Clark, Le, Re, Mirhoseini (2024). Large Language Monkeys: Scaling Inference Compute with Repeated Sampling, arXiv:2407.21787", None, "verified")
V_SNELL = ("Snell, Lee, Xu, Kumar (2024). Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters, ICLR 2025", None, "verified")
V_SETLUR = ("Setlur, Rajaraman, Levine, Kumar (2025). Scaling Test-Time Compute Without Verification or RL is Suboptimal, arXiv:2502.12118", None, "verified")
V_HTPS = ("Lample, Lacroix, Lachaux, Rodriguez, Hayat, Lavril, Ebner, Martinet (2022). HyperTree Proof Search for Neural Theorem Proving, NeurIPS 2022", None, "verified")
V_PROVER = ("Xin, Ren, Song, Shao, Zhao, Wang, et al. (2024). DeepSeek-Prover-V1.5: Harnessing Proof Assistant Feedback for Reinforcement Learning and Monte-Carlo Tree Search, arXiv:2408.08152", None, "verified")
V_IB = ("Tishby, Pereira, Bialek (1999). The Information Bottleneck Method, Allerton 1999", None, "verified")
V_SHALIZI = ("Shalizi, Crutchfield (2001). Computational Mechanics: Pattern and Prediction, Structure and Simplicity, Journal of Statistical Physics 104", None, "verified")
V_PSR = ("Littman, Sutton, Singh (2001). Predictive Representations of State, NeurIPS 14", None, "verified")
V_SHAI = ("Shai, Marzen, Teixeira, Gietelink Oldenziel, Riechers (2024). Transformers represent belief state geometry in their residual stream, NeurIPS 2024", None, "verified")
V_PIOTROWSKI = ("Piotrowski, Riechers, Filan, Shai (2025). Constrained belief updates explain geometric structures in transformer representations, arXiv:2502.01954", None, "verified")
V_MICHIE = ("Michie (1968). 'Memo' Functions and Machine Learning, Nature 218", None, "verified")
V_FUTAMURA = ("Futamura (1971/1999). Partial Evaluation of Computation Process - An Approach to a Compiler-Compiler, Higher-Order and Symbolic Computation 12", None, "verified")
V_SNOOPY = ("Karlin, Manasse, Rudolph, Sleator (1988). Competitive snoopy caching, Algorithmica 3", None, "verified")
V_SLEATOR = ("Sleator, Tarjan (1985). Amortized efficiency of list update and paging rules, CACM 28(2)", None, "verified")
V_PIC = ("Hoelzle, Chambers, Ungar (1991). Optimizing Dynamically-Typed Object-Oriented Languages With Polymorphic Inline Caches, ECOOP 1991", None, "verified")
V_KCMAP = ("Darwiche, Marquis (2002). A Knowledge Compilation Map, JAIR 17", None, "verified")
V_TVM = ("Chen, Moreau, Jiang, Zheng, Yan, Cowan, et al. (2018). TVM: An Automated End-to-End Optimizing Compiler for Deep Learning, OSDI 2018", None, "verified")
V_ADAPTON = ("Hammer, Khoo, Hicks, Foster (2014). Adapton: Composable, Demand-Driven Incremental Computation, PLDI 2014", None, "verified")
V_PERSIST = ("Driscoll, Sarnak, Sleator, Tarjan (1989). Making data structures persistent, JCSS 38(1)", None, "verified")
V_BUILD = ("Mokhov, Mitchell, Peyton Jones (2018/2020). Build Systems a la Carte, ICFP 2018 / JFP 30", None, "verified")
V_NFL = ("Goldblum, Finzi, Rowan, Wilson (2023). The No Free Lunch Theorem, Kolmogorov Complexity, and the Role of Inductive Biases in Machine Learning, arXiv:2304.05366", None, "verified")
V_GOODHART = ("Manheim, Garrabrant (2018). Categorizing Variants of Goodhart's Law, arXiv:1803.04585", None, "verified")
V_GAO = ("Gao, Schulman, Hilton (2023). Scaling Laws for Reward Model Overoptimization, ICML 2023", None, "verified")
V_SKALSE = ("Skalse, Howe, Krasheninnikov, Krueger (2022). Defining and Characterizing Reward Hacking, NeurIPS 2022", None, "verified")
V_KARWOWSKI = ("Karwowski, Hayman, Bai, Kiendlhofer, Griffin, Skalse (2024). Goodhart's Law in Reinforcement Learning, ICLR 2024", None, "verified")
V_KWA = ("Kwa, Thomas, Garriga-Alonso (2024). Catastrophic Goodhart: regularizing RLHF with KL divergence does not mitigate heavy-tailed reward misspecification, NeurIPS 2024", None, "verified")
V_PAN = ("Pan, Bhatia, Steinhardt (2022). The Effects of Reward Misspecification: Mapping and Mitigating Misaligned Models, ICLR 2022", None, "verified")
V_LOCATELLO = ("Locatello, Bauer, Lucic, Raetsch, Gelly, Schoelkopf, Bachem (2019). Challenging Common Assumptions in the Unsupervised Learning of Disentangled Representations, ICML 2019", None, "verified")
V_SCHOLKOPF = ("Schoelkopf, Locatello, Bauer, Ke, Kalchbrenner, Goyal, Bengio (2021). Toward Causal Representation Learning, Proceedings of the IEEE 109(5)", None, "verified")
V_DARTS = ("Liu, Simonyan, Yang (2019). DARTS: Differentiable Architecture Search, ICLR 2019", None, "verified")
V_NASSURVEY = ("Elsken, Metzen, Hutter (2019). Neural Architecture Search: A Survey, JMLR 20(55)", None, "verified")
V_WANN = ("Gaier, Ha (2019). Weight Agnostic Neural Networks, NeurIPS 2019", None, "verified")


def cv(V, owns):
    """Reuse a verified ledger citation with an entry-specific 'owns' clause."""
    return (V[0], owns, "verified")


def tv(citation, owns):
    """A citation NOT in the verified ledger: marked to_verify."""
    return (citation, owns)


# ======================================================================================================================
# A. Interface and input representation (calculus section 4)
# ======================================================================================================================

F("TF-001", "Tokenization / segmentation",
  "An input compiler T mapping a surface byte/character stream u to a symbol sequence tau_1..tau_n over a finite vocabulary "
  "Sigma, with |T(u)| = n(u) the token count. Subword schemes (BPE-style merges, unigram-LM segmentation) define T by a learned "
  "merge/score table fitted to a corpus; the induced map is generally many-to-one on surface forms and one-to-many on meanings.",
  "CSP", "C because T fixes what counts as an atomic symbol for every downstream mechanism; S because it determines the state-table "
  "index set; P because n(u) multiplies every per-token training and serving cost.",
  "Meaning of the surface stream u: any exact claim about u must be invariant under retokenization T -> T' that preserves u.",
  "Per-token arithmetic: character-level counting, digit arithmetic, rhyme/phonology and byte-level edit distance are NOT invariant "
  "because tokens partition the surface differently; token-level probabilities are not comparable across tokenizers.",
  "T controls the length n(u) of the dependency chain the router must span AND the fragmentation of a semantic unit across positions; "
  "a unit split over k tokens requires k-step composition that a single-token encoding gets for free.",
  ["ΔB_serve", "ΔB_train", "ΔB_mem", "ΔL_sem", "ΔL_rob"],
  "Coarser segmentation lowers ΔB_serve and ΔB_train through smaller n(u) and raises ΔB_mem through the embedding/unembedding tables; "
  "ΔL_sem moves in either direction depending on whether the obligation's distinctions align with the merge boundaries.",
  "Same model, same corpus, same token budget, but a tokenizer whose merges are drawn from a DIFFERENT corpus's statistics with the "
  "identical vocabulary size and the identical mean n(u): the size/length mechanism is held, the alignment mechanism is removed.",
  "Byte-level or character-level input with a learned pooling/downsampling layer reproduces the sequence-shortening mechanism without "
  "a fixed merge table; a fixed hash n-gram vocabulary reproduces the table-size mechanism without learned merges.",
  [tv("Sennrich, Haddow, Birch (2016). Neural Machine Translation of Rare Words with Subword Units, ACL 2016", "the BPE merge construction"),
   tv("Kudo, Richardson (2018). SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing, EMNLP 2018 (demo)", "the unigram-LM alternative and the lossless detokenization requirement"),
   cv(V_NFL, "the statement that no segmentation is best across all corpora without an inductive-bias assumption")],
  None, "B2.1 tokenizer granularity (factorial: surface morphology complexity x vocabulary size x sequence-length price x embedding memory price)",
  "A single vocabulary size/segmentation wins on sample efficiency AND serve tokens AND memory across corpora with materially different "
  "surface morphology, at matched model and token budget. That would falsify the no-universal-tokenizer claim of gap G-T01.",
  "REGISTERED_FOR_EXPERIMENT",
  "Meter tokens, not characters or documents: report n(u) per corpus alongside every loss, or a tokenizer change silently rebuys the "
  "compute budget. Charge the embedding+unembedding parameter count to ΔB_mem separately from the body.",
  "4. Feature atlas - input representation and interface / Tokenizer / segmentation (C,S,P)")

F("TF-002", "Vocabulary size",
  "The cardinality |Sigma| = V of the token alphabet. It fixes the embedding matrix E in R^{V x d}, the unembedding W_U in R^{V x d}, "
  "the softmax partition over V logits, and (through the segmentation that produced it) the expected sequence length E[n(u)], which for "
  "subword schemes falls roughly as V grows with diminishing returns.",
  "CSP", "C/S because V is the size of the discrete state table the compiler exposes; P because 2Vd parameters and a V-way softmax are "
  "charged at every step of training and serving.",
  "The set of surface strings representable: any lossless tokenizer covers the same surface language at any V.",
  "The parameter/compute SPLIT between the body and the vocabulary heads, and the effective sample count per token type: rare types get "
  "fewer updates as V grows.",
  "V trades sequence length (a routing-depth and serve-cost term) against vocabulary-head materialization (a memory term) and against "
  "per-type sample efficiency; the optimum is where the marginal length saving equals the marginal table cost at the registered prices.",
  ["ΔB_mem", "ΔB_serve", "ΔB_train", "ΔL_gen"],
  "Larger V raises ΔB_mem (2Vd) and the per-step softmax cost, lowers ΔB_serve through shorter sequences, and degrades ΔL_gen for rare "
  "types through fewer updates each.",
  "Hold V fixed and randomly REASSIGN which merges are in the vocabulary (same V, same table size, same softmax width, worse alignment "
  "to corpus statistics): the materialization cost is identical and the frequency-matching mechanism is destroyed.",
  "A factorized or hierarchical (two-level) softmax with the same V reproduces the alphabet size while changing the materialization cost; "
  "adaptive-span embeddings reproduce the frequency-matching mechanism without changing V.",
  [tv("Sennrich, Haddow, Birch (2016). Neural Machine Translation of Rare Words with Subword Units, ACL 2016", "the vocabulary-size/sequence-length tradeoff as a tunable"),
   cv(V_HOFFMANN, "the compute-optimal allocation frame in which vocabulary parameters compete with body parameters for a fixed budget")],
  None, "B2.1 tokenizer granularity (vocabulary-size axis)",
  "The optimal V is shown to be independent of the embedding/serving price vector at matched corpus and model size.",
  "REGISTERED_FOR_EXPERIMENT",
  "Charge 2Vd parameters to ΔB_mem and the V-way softmax to ΔB_serve EXPLICITLY; a 'parameter count' that excludes the vocabulary heads "
  "makes a large-V model look cheaper than it is.",
  "4. Feature atlas - input representation and interface / Vocabulary size (C,S,P)")

F("TF-003", "Token embeddings",
  "A lookup E: Sigma -> R^d, tau |-> E[tau], realized as a V x d matrix read by one-hot indexing, supplying the initial residual "
  "coordinate r_i^{(0)} = E(tau_i) + p_i. It is a free-parameter table, not a computed function of the symbol.",
  "SC", "S because it is the coordinate system in which every later mechanism reads the input; C because it is the interface between a "
  "discrete alphabet and a continuous state.",
  "The discrete identity of each token: E is injective as long as no two rows coincide, so no token distinction is destroyed at layer 0.",
  "Any claim that individual embedding dimensions carry interpretable meaning; E is defined only up to an invertible map absorbed by the "
  "first weight matrix, so per-coordinate semantics is not preserved under that gauge.",
  "The embedding geometry determines which token distinctions are CHEAP for downstream linear routing: distinctions aligned with large "
  "singular directions of E are separable by one linear read, others require depth.",
  ["ΔB_mem", "ΔL_gen", "ΔB_train"],
  "ΔB_mem rises linearly in Vd; ΔL_gen improves when the embedding geometry shares structure across related types and degrades when the "
  "table memorizes each type independently.",
  "Replace E by a FROZEN random matrix with the same shape and the same row norms: the coordinate-supply and materialization mechanisms "
  "are held, the learned-geometry mechanism is removed.",
  "A learned linear map applied to a fixed one-hot or hashed sparse code computes the same function class; factorized embeddings "
  "E = AB with A in R^{V x k}, B in R^{k x d} reproduce the lookup with a rank constraint.",
  [cv(V_VASWANI, "the embedding-plus-position construction used here"),
   cv(V_LOCATELLO, "the impossibility of identifying individual latent coordinates without supervision or inductive bias, which is why per-dimension interpretation is NOT a preserved invariance"),
   cv(V_ELHAGE, "the residual-stream reading in which the embedding is the layer-0 write")],
  None, "MLX-41 probe vs causal-use separation (whether an embedding direction a probe finds is the one the model uses)",
  "A causal intervention shows that per-coordinate embedding semantics is preserved under an arbitrary invertible reparameterization "
  "absorbed into W^Q/W^K/W^V, which would contradict the gauge non-invariance stated here.",
  "REGISTERED_FOR_EXPERIMENT",
  "Charge Vd parameters to ΔB_mem; when embeddings are tied to the unembedding (TF-033) charge the table ONCE and say so, or the same "
  "memory is double-counted or double-discounted across comparisons.",
  "4. Feature atlas - input representation and interface / Embeddings (S,C)")

F("TF-004", "Embedding dimension / model width d",
  "The width d of the residual stream r^{(l)} in R^{n x d}. It fixes the rank ceiling of every per-position linear read (at most d "
  "independent linear features can be read without interference), the parameter count of every block (Theta(d^2) per projection), and "
  "the per-token FLOPs (Theta(d^2) per linear layer).",
  "SP", "S because d is the dimension of the shared workspace all mechanisms read and write; P because every cost in the block scales "
  "as d^2.",
  "The function class is monotone in d: a width-d model is realizable inside a width-d' model for d' >= d by zero-padding.",
  "Interference-free superposition: once the number of features a layer must carry exceeds d, some pairs must share directions, so "
  "'each feature has its own direction' is not preserved.",
  "d is the capacity of the shared state through which all mechanisms communicate; raising d reduces read interference between "
  "concurrently carried features at quadratic cost.",
  ["ΔB_mem", "ΔB_train", "ΔB_serve", "ΔL_sem"],
  "All three burden components rise as Theta(d^2) per layer; ΔL_sem improves only while feature interference, not data or optimization, "
  "is the binding constraint.",
  "Hold d fixed and hold total parameters fixed but SPLIT the residual stream into two non-communicating width-d/2 streams: the "
  "parameter and FLOP budget is matched and the shared-workspace mechanism is removed.",
  "Depth-for-width substitution at matched parameters, or a low-rank bottleneck inside each block with a wide residual stream, "
  "reproduces the capacity change with a different cost signature.",
  [cv(V_HOFFMANN, "the empirical compute-optimal frontier over width/depth/data at fixed budget"),
   cv(V_ELHAGE, "the residual stream as a shared bandwidth-limited communication channel"),
   cv(V_MICHAUD, "the quantization/discrete-capability view of what added capacity buys")],
  None, "B2.7 MLP width/gating (width axis) and MLX-31 model/data/compute scaling surface",
  "A width that is optimal independently of the registered memory and compute prices, or a demonstration that feature interference "
  "never binds at any d for a fixed obligation.",
  "REGISTERED_FOR_EXPERIMENT",
  "Report d together with depth L and the token budget; 'parameters' alone hides that the same count buys different interference "
  "profiles at different (d, L) splits.",
  "13. Small-feature closure table / embedding dimension (S/P)")

F("TF-005", "Learned absolute positional embeddings",
  "A free table P in R^{n_max x d} added at layer 0: r_i^{(0)} = E(tau_i) + P[i]. Each position index i < n_max owns an independently "
  "learned vector; positions i >= n_max have no defined encoding.",
  "SR", "S because it writes order information into the residual coordinate; R because downstream attention scores read it to select by "
  "position.",
  "Order distinctions WITHIN the trained range [0, n_max): any permutation-sensitive obligation on such positions can be satisfied.",
  "Extrapolation beyond n_max, and translation equivariance: P[i] and P[i+k] are unrelated by construction, so a relation defined by "
  "relative offset must be relearned at every absolute position.",
  "Absolute position is supplied as content in the residual stream, so the router reads order through the same linear machinery it uses "
  "for token content; this makes order cheap to condition on and expensive to generalize across offsets.",
  ["ΔL_sem", "ΔL_gen", "ΔB_mem"],
  "ΔL_sem improves on order-sensitive obligations (TMT-1 necessity); ΔL_gen degrades sharply outside [0, n_max); ΔB_mem rises by "
  "n_max x d.",
  "Bag-of-tokens: the identical model with P set to zero, so no order information reaches any layer. TMT-1 / X-TMT1 predicts exact "
  "failure on the order-sensitive obligations and NO change on the permutation-invariant one.",
  "Sinusoidal positions (TF-006), rotary positions (TF-007), a relative bias (TF-008), or a causal-mask-plus-depth construction that "
  "reconstructs position from prefix counting all supply the necessary order information.",
  [cv(V_VASWANI, "learned and sinusoidal absolute positions as interchangeable at the reported scale"),
   cv(V_ZHOU_LEN, "the length-generalization failure mode of position encodings"),
   tv("Devlin, Chang, Lee, Toutanova (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding, NAACL 2019", "learned absolute position tables at scale")],
  TH("TMT-1", "X-TMT1"),
  "B2.2 positional necessity and geometry (arm: absolute)",
  "An exact side-channel-free realization with a fully permutation-invariant internal state satisfies an order-sensitive obligation. "
  "X-TMT1 enumerates the collisions that make this impossible at its scope.",
  "PROVED_AT_SCOPE",
  "Charge n_max x d to ΔB_mem, and charge the cost of ANY position-extension procedure (retraining, interpolation) to ΔB_update rather "
  "than reporting only the extended context length.",
  "4. Feature atlas - input representation and interface / Positional mechanisms (S,R)")

F("TF-006", "Sinusoidal absolute positional encoding",
  "A FIXED (unlearned) map p_i[2k] = sin(i / 10000^{2k/d}), p_i[2k+1] = cos(i / 10000^{2k/d}), added to the token embedding. Because "
  "each frequency band is a rotation, p_{i+delta} is a fixed linear function of p_i for every offset delta, which is the property the "
  "learned table lacks.",
  "SR", "S/R for the same reason as TF-005, with the difference that the encoding is a closed-form function of i rather than a table.",
  "Order distinctions at ANY index i, including i >= n_train, since the formula is defined for all i; and the linear-shift relation "
  "between p_i and p_{i+delta}.",
  "Useful behaviour outside the trained index range: the encoding is defined everywhere but the attention scores that consume it were "
  "only ever fit on the trained range, so defined is not the same as calibrated.",
  "The multi-band rotation makes relative offset LINEARLY decodable from the pair (p_i, p_j), so an attention head can implement an "
  "offset-selective read with one bilinear form rather than memorizing an n_max x n_max table.",
  ["ΔL_sem", "ΔL_gen", "ΔB_mem"],
  "ΔB_mem falls to zero (no table); ΔL_sem equals the learned table's within-range on order-sensitive obligations; ΔL_gen beyond range "
  "is better defined but not thereby better.",
  "Random FIXED position vectors: a non-learned table of i.i.d. vectors with matched norm and zero memory cost. This keeps 'fixed, "
  "unlearned, order-distinguishing' and removes the multi-band-rotation structure.",
  "Rotary embeddings (TF-007) apply the same rotation idea multiplicatively inside the QK bilinear form instead of additively at "
  "layer 0; a learned table initialized to the sinusoid and frozen is a third realization.",
  [cv(V_VASWANI, "the sinusoidal construction and the claim that it and learned tables performed comparably at that scale"),
   cv(V_ZHOU_LEN, "the finding that defined-everywhere is not sufficient for length generalization")],
  TH("TMT-1", "X-TMT1"),
  "B2.2 positional necessity and geometry (arms: absolute / relative / rotary-like) and the long-extrapolation task",
  "Sinusoidal encoding extrapolates to indices far outside the trained range with no degradation at matched training, which would make "
  "the 'defined but not calibrated' distinction vacuous.",
  "REGISTERED_FOR_EXPERIMENT",
  "Zero memory cost is real, but charge the extra attention capacity spent reconstructing relative offset from two absolute codes "
  "rather than reading it directly (TF-008).",
  "4. Feature atlas - input representation and interface / Positional mechanisms (S,R)")

F("TF-007", "RoPE / rotary position embedding",
  "Position enters MULTIPLICATIVELY inside the score: partition the head dimension into d_h/2 planes, rotate q_i and k_j in plane m by "
  "angles i*theta_m and j*theta_m, so that <R(i)q, R(j)k> = <q, R(j-i)k> depends on (j-i) only. No vector is added to the residual "
  "stream and no position table is stored.",
  "SR", "R primarily: position modifies the ROUTING bilinear form rather than the carried state; S secondarily because the rotation is "
  "applied to the state coordinates Q and K.",
  "Exact relative-offset dependence of the attention score: the score is invariant under a common shift i -> i+c, j -> j+c.",
  "Absolute position: a mechanism that must condition on 'this is token 0' cannot read it from the rotated score alone; and the "
  "attention magnitude at large |j-i| is not preserved under a change of the base frequency (theta_m rescaling).",
  "Making the score a function of j-i by construction removes the need to LEARN translation equivariance, so the routing relation "
  "transfers across absolute positions and (subject to frequency calibration) across lengths.",
  ["ΔL_gen", "ΔL_sem", "ΔB_mem", "ΔB_serve"],
  "ΔB_mem falls (no table); ΔL_gen on relative-distance obligations improves; ΔB_serve rises slightly (two extra multiply-adds per "
  "head-dimension pair per token).",
  "Apply the SAME per-plane rotations with angles drawn from a fixed random permutation of positions rather than from i: identical "
  "arithmetic cost, identical parameter count, and the (j-i) structure destroyed.",
  "An additive relative bias b(j-i) (TF-008) supplies relative-offset dependence additively; a complex-valued attention with "
  "position-dependent phase is the same rotation written differently.",
  [tv("Su, Lu, Pan, Murtadha, Wen, Liu (2021/2024). RoFormer: Enhanced Transformer with Rotary Position Embedding, Neurocomputing 568", "the rotary construction and the relative-offset identity"),
   cv(V_ZHOU_LEN, "length generalization as a property of the position mechanism plus the task, not the mechanism alone"),
   cv(V_VASWANI, "the additive-position baseline that rotary replaces")],
  TH("TMT-1", "X-TMT1"),
  "B2.2 positional necessity and geometry (rotary-like arm; relative-distance and long-extrapolation tasks)",
  "A controlled comparison at matched parameters and compute shows rotary has NO advantage on relative-distance obligations and no "
  "disadvantage on absolute-position obligations, i.e. the geometry is not the mediator.",
  "REGISTERED_FOR_EXPERIMENT",
  "Rotary looks free because it adds no parameters. Charge its per-token rotation FLOPs to ΔB_serve, and charge any base-frequency "
  "rescaling used to reach a longer context to ΔB_update (it is a re-calibration, not a free extension).",
  "13. Small-feature closure table / RoPE (S/R)")

F("TF-008", "Relative position bias (ALiBi / T5-style buckets)",
  "An additive term in the score: s_{ij} = q_i . k_j / sqrt(d_h) + B[bucket(j-i)] (learned scalar per bucket per head, T5-style) or "
  "s_{ij} = q_i . k_j / sqrt(d_h) - m_h (i - j) (a fixed per-head linear penalty in distance, ALiBi-style). B or m_h is read from the "
  "OFFSET only.",
  "SR", "R because the bias enters the routing score directly; S only in the weak sense that the bias table is state the model carries.",
  "Translation invariance of the routing preference: the bias contributed to (i, j) equals that contributed to (i+c, j+c).",
  "The identity of the far context: a monotone distance penalty makes distant tokens uniformly cheaper to ignore, so obligations "
  "requiring a specific distant token are NOT preserved under increasing penalty slope.",
  "The bias is a learned or fixed PRIOR over dependency distance added before the softmax, so it shifts routing entropy toward near "
  "tokens without removing any edge from the legal set.",
  ["ΔL_gen", "ΔL_sem", "ΔB_mem", "ΔB_serve"],
  "ΔB_mem is a few scalars per head; ΔL_gen on longer-than-trained inputs improves where the true dependency structure is "
  "distance-decaying and degrades where it is not.",
  "Replace bucket(j-i) by bucket(hash(i,j)) with the same number of buckets and the same learned scalars: identical parameters and "
  "arithmetic, and the distance structure removed.",
  "Rotary (TF-007) obtains relative dependence multiplicatively; a sliding-window mask (TF-019) is the hard-threshold limit of a "
  "distance penalty; a learned per-head decay applied to the value stream is a third realization.",
  [tv("Raffel, Shazeer, Roberts, Lee, Narang, Matena, Zhou, Li, Liu (2020). Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer (T5), JMLR 21", "the bucketed learned relative bias"),
   tv("Press, Smith, Lewis (2022). Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation (ALiBi), ICLR 2022", "the fixed linear distance penalty and its extrapolation claim"),
   tv("Shaw, Uszkoreit, Vaswani (2018). Self-Attention with Relative Position Representations, NAACL 2018", "the original relative-position formulation")],
  TH("TMT-1", "X-TMT1"),
  "B2.2 positional necessity and geometry (relative arm) and MLX-07 dependency variability x attention/dynamic routing",
  "An obligation whose true dependency structure is distance-INDEPENDENT is served at least as well by a monotone distance penalty as "
  "by no bias at matched training, which would show the bias is not acting through the distance prior.",
  "REGISTERED_FOR_EXPERIMENT",
  "A distance penalty buys extrapolation by suppressing far attention. Meter the far-dependency obligations separately, or the "
  "extrapolation gain is bought from a task distribution that never needed the far edges.",
  "13. Small-feature closure table / positional encoding (S/R)")

F("TF-009", "Segment / type / modality embeddings",
  "An additional additive code r_i^{(0)} += S[seg(i)] where seg: positions -> a small finite set of externally supplied labels "
  "(sentence A/B, speaker, turn role, image-patch vs text token, document id). The label comes from the interface, not from the "
  "token content.",
  "SC", "C because the label is an interface-level declaration about the input; S because it is written into the residual coordinate.",
  "Every distinction present in the token stream itself: adding a segment code does not remove information.",
  "Invariance to the labeling convention: two inputs identical as token streams but differently segmented become distinguishable, so "
  "claims about the token stream alone do not transfer.",
  "The segment code makes an externally known boundary LINEARLY available at layer 0, so mechanisms that must condition on it "
  "(attend only within my turn; treat these tokens as image) need no depth to infer it from content.",
  ["ΔL_sem", "ΔL_gen", "ΔB_mem"],
  "ΔL_sem improves exactly when the segment distinction alters the protected output; ΔB_mem rises by |segments| x d, which is "
  "negligible; ΔL_gen can degrade if the model becomes dependent on a labeling that shifts at serve time.",
  "Randomly PERMUTE the segment labels while keeping the same number of distinct labels and the same code norms: the extra state and "
  "its cost are held and the correspondence to the real boundary is destroyed.",
  "An explicit boundary TOKEN inserted in the stream, or a block mask (TF-015) that encodes the same partition structurally, supplies "
  "the same distinction without a separate embedding table.",
  [tv("Devlin, Chang, Lee, Toutanova (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding, NAACL 2019", "the segment-embedding construction"),
   cv(V_VASWANI, "the additive layer-0 code convention these embeddings follow"),
   cv(V_SCHOLKOPF, "the framing in which an externally supplied variable is useful only if it is causally relevant to the target")],
  None, "B2.16 instruction/preference separation (segment/role labels as the carrier of instruction structure) and MLX-17 multimodal alias breaking",
  "A segment distinction that provably does not change the protected output nonetheless improves protected performance at matched "
  "training, which would show the effect runs through optimization geometry rather than the declared distinction.",
  "REGISTERED_FOR_EXPERIMENT",
  "The label is free at inference but NOT free upstream: charge the annotation/segmentation pipeline that produces seg(i) to "
  "ΔB_train, and record that serve-time behaviour now depends on a label that can be absent or wrong in deployment.",
  "4. Feature atlas - input representation and interface / Segment/type/modality embeddings (S,C)")


# ======================================================================================================================
# B. Attention and routing (calculus section 5)
# ======================================================================================================================

F("TF-010", "Q/K/V factorization",
  "Three independent learned linear maps of the same residual state: Q = XW^Q, K = XW^K, V = XW^V, with the score depending on (Q, K) "
  "and the transported payload on V alone. The factorization separates 'what position i is looking for' from 'what position j "
  "advertises' from 'what position j sends'.",
  "RT", "R because W^Q and W^K define the dependency-selection bilinear form X W^Q (W^K)^T X^T; T because W^V is a local transform "
  "applied to the transported content.",
  "The set of realizable attention maps up to the reparameterization (W^Q, W^K) -> (W^Q A, W^K A^{-T}): only the product "
  "W^Q (W^K)^T is identified, and W^V is identified only up to the output map W^O.",
  "Any claim that Q, K or V coordinates are individually recoverable or individually meaningful; the gauge above destroys that.",
  "Splitting selection from payload lets one head route by a LOW-rank criterion (rank <= d_h through the QK product) while sending a "
  "payload of independent content, so selection cost and payload capacity are decoupled.",
  ["ΔB_serve", "ΔB_mem", "ΔL_sem"],
  "ΔB_serve and ΔB_mem rise as 3 d d_h H for the projections; ΔL_sem improves when the obligation's routing criterion and its payload "
  "are genuinely different functions of the state.",
  "Tie W^V = W^K (payload equals advertisement): identical parameter count minus one matrix, identical routing arithmetic, and the "
  "selection/payload separation removed.",
  "A single bilinear form with an explicitly low-rank factorization, or a kernel/linear-attention feature map phi with score "
  "phi(q).phi(k), realizes the same selection mechanism with different cost; hard kNN retrieval over K realizes its hard limit.",
  [cv(V_VASWANI, "the Q/K/V construction itself"),
   cv(V_ELHAGE, "the QK/OV circuit decomposition, which is precisely the statement that only the products are identified"),
   cv(V_BASED, "linear-attention feature maps as an alternative realization of the same selection mechanism")],
  TH("TMT-3", "X-TMT3"),
  "B2.3 fixed vs dynamic routing (dynamic-score-select arm) and MLX-07 dependency variability x attention/dynamic routing",
  "An obligation whose required edge sets E(x) vary strongly with x is served as cheaply by ONE fixed sparse graph as by score-based "
  "selection, at matched primitives. X-TMT3 fixes the union lower bound that makes this a decidable comparison.",
  "REGISTERED_FOR_EXPERIMENT",
  "Score-based selection is not free: charge the n^2 d_h score computation to ΔB_serve and the discovery/search cost of the routing "
  "criterion to ΔB_search, separately from the payload transport.",
  "5. Feature atlas - attention and routing / Q/K/V factorization (R,T)")

F("TF-011", "Head dimension d_h",
  "The per-head width: Q_h, K_h in R^{n x d_h}, V_h in R^{n x d_v}. It bounds the RANK of the per-head selection form "
  "(rank(W_h^Q (W_h^K)^T) <= d_h) and the dimension of the per-head payload. Conventionally d_h = d/H, so head count and head width "
  "trade at fixed total projection cost.",
  "RS", "R because d_h caps the complexity of the routing criterion one head can express; S because d_v caps the payload that head "
  "can carry.",
  "The total projection FLOPs and parameters when H d_h is held fixed: the (H, d_h) split is free at that level of accounting.",
  "The per-head expressible selection: a criterion of intrinsic rank r cannot be realized by a head with d_h < r, so the split is NOT "
  "semantically free.",
  "d_h sets how many independent comparison directions one routing channel can combine; obligations whose selection criterion is "
  "high-rank need wide heads, obligations with many independent low-rank criteria need many narrow heads.",
  ["ΔL_sem", "ΔB_serve", "ΔB_mem"],
  "At fixed H d_h, ΔB_serve and ΔB_mem are unchanged and ΔL_sem moves with the match between d_h and the intrinsic rank of the "
  "required criteria.",
  "Hold H and d_h but PROJECT each head's Q and K through a fixed random rank-1 matrix before scoring: identical arithmetic cost, "
  "selection rank forced to 1.",
  "A single wide head with a block-diagonal QK form is arithmetically the same as H narrow heads; a low-rank adapter on a wide head "
  "reproduces a narrow head's rank constraint.",
  [cv(V_VASWANI, "the d_h = d/H convention and the multi-head decomposition"),
   cv(V_ELHAGE, "the per-head low-rank QK circuit and its rank ceiling"),
   tv("Bhojanapalli, Yun, Rawat, Reddi, Kumar (2020). Low-Rank Bottleneck in Multi-head Attention Models, ICML 2020", "the explicit statement that d_h caps attention-matrix rank")],
  None, "B2.4 head factorization (vary the number of independent dependency relations at matched compute/parameters)",
  "Optimal d_h at fixed H d_h is shown to follow sequence length alone, independently of the rank/multiplicity of the required "
  "dependency relations.",
  "REGISTERED_FOR_EXPERIMENT",
  "Reporting only H or only d is insufficient: report the pair, because two models with identical parameter counts can have "
  "incomparable selection-rank budgets.",
  "13. Small-feature closure table / Q/K/V dimension (R/S)")

F("TF-012", "Score scaling 1 / sqrt(d_h)",
  "The score is s_{ij} = (q_i . k_j) / sqrt(d_h) rather than q_i . k_j. Under the assumption that q and k coordinates are independent "
  "with zero mean and unit variance, Var(q.k) = d_h, so dividing by sqrt(d_h) makes the score variance O(1) independently of head width.",
  "NR", "N because it is a conditioning/gauge constant on the routing scores; R because those scores are the routing logits.",
  "The ARGMAX of the attention scores and hence the hard-routing limit: dividing every score by the same positive constant leaves the "
  "ordering unchanged.",
  "The softmax distribution, and hence the gradient magnitudes through the softmax: a positive rescaling is exactly a temperature "
  "change (TF-013), so routing entropy is NOT preserved.",
  "The constant keeps pre-softmax scores in the regime where softmax is neither uniform nor saturated at the initialization scale, so "
  "gradients through the attention weights are non-vanishing at the start of training.",
  ["ΔB_train", "ΔL_sem"],
  "ΔB_train falls (fewer steps to escape a saturated or uniform routing regime); ΔL_sem is unchanged at the argmax level and moves only "
  "through what training reaches.",
  "Scale by 1/d_h or by 1 instead: identical arithmetic cost, identical function class (the model can absorb any constant into W^Q), "
  "and the initialization-scale conditioning removed. The twin isolates conditioning from expressivity.",
  "Normalizing q and k to unit norm and using a learned scalar (QK-norm) achieves the same score-scale control; initializing W^Q with "
  "variance 1/d_h absorbs the constant exactly.",
  [cv(V_VASWANI, "the 1/sqrt(d_k) constant and the variance argument for it"),
   cv(V_COHEN_EOS, "the general finding that trainability depends on the curvature/scale regime the run occupies, not only on the function class"),
   tv("Henry, Dachapally, Pawar, Chen (2020). Query-Key Normalization for Transformers, Findings of EMNLP 2020", "the alternative realization that normalizes q and k instead of rescaling the score")],
  TH("TMT-4", "X-TMT4"),
  "B2.6 softmax entropy/temperature (the scaling constant is the T axis at initialization)",
  "Training succeeds equally from any score scale at matched steps and matched schedule, which would show the constant is not acting "
  "through score conditioning.",
  "REGISTERED_FOR_EXPERIMENT",
  "The constant is arithmetically free but buys an optimization regime. Charge any scale search to ΔB_search, and never report it as a "
  "semantic improvement: X-TMT4 shows a positive rescaling is exactly a temperature move.",
  "5. Feature atlas - attention and routing / Dot-product similarity and 1/sqrt(d) scaling (R,N)")

F("TF-013", "Attention temperature T_a",
  "alpha = softmax(s / T_a) with T_a > 0. By TMT-4, softmax(s/T) = argmax_{p in Delta} [p.s + T H(p)], so T_a is exactly the weight on "
  "the entropy term of an entropy-regularized routing policy: T_a -> 0 gives hard argmax routing, T_a -> infinity gives uniform routing.",
  "RD", "R because it parameterizes the routing distribution; D in the weak sense that at T_a -> 0 routing becomes a hard selection "
  "decision.",
  "The score vector s itself and hence the routing PREFERENCE ORDER at every temperature.",
  "The mixture actually transported: the value output alpha V changes continuously with T_a, so no downstream quantity computed from "
  "alpha is temperature-invariant.",
  "T_a controls how much routing mass leaks to non-maximal sources. Low T_a suits obligations with an unambiguous required source; "
  "high T_a suits obligations where the answer is an average over several sources or where the score estimate is noisy.",
  ["ΔL_sem", "ΔL_cal", "ΔL_rob", "ΔB_train"],
  "Lower T_a sharpens routing, improving ΔL_sem on unambiguous-source obligations and degrading ΔL_rob under score noise; higher T_a "
  "does the reverse. ΔB_serve is unchanged.",
  "Replace softmax(s/T_a) by a FIXED random distribution with the same entropy: the routing entropy is matched exactly and the "
  "score-dependence is removed, so any benefit attributed to 'the right amount of spread' is separated from 'spread on the right edges'.",
  "A sparsemax or top-k-then-renormalize routing rule reaches comparable concentration through a different variational objective; a "
  "learned per-head scalar on the scores is the same parameter under a different name.",
  [cv(V_VASWANI, "softmax attention with a fixed scale, the T_a = 1 special case"),
   tv("Martins, Astudillo (2016). From Softmax to Sparsemax: A Sparse Model of Attention and Multi-Label Classification, ICML 2016", "the alternative variational routing rule with exactly sparse solutions"),
   cv(V_IB, "the general trade of a score/relevance term against an entropy/compression term, of which TMT-4 is the finite-simplex instance")],
  TH("TMT-4", "X-TMT4"),
  "B2.6 softmax entropy/temperature (routing tasks with controlled ambiguity)",
  "A single T_a is optimal across routing tasks whose source ambiguity is deliberately varied, which would falsify the "
  "entropy-vs-score trade reading of TMT-4 as the operative mechanism.",
  "PROVED_AT_SCOPE",
  "Temperature is free arithmetically, so it is the classic hidden knob: any comparison must FIX T_a across arms or report the search "
  "over it as ΔB_search. A tuned T_a compared against an untuned baseline is not a controlled comparison.",
  "5. Feature atlas - attention and routing / Attention temperature / logit scaling (R,D)")

F("TF-014", "Causal mask",
  "s_{ij} <- -infinity for j > i before the softmax, so alpha_{ij} = 0 for j > i and output i is a function of x_{<=i} only. It "
  "implements the requirement that Y_i be F_i-measurable, where F_i is the legal information set at step i.",
  "CR", "C because it is an information-constitution declaration about what is legal to read; R because it is imposed on the routing "
  "score. It is NOT primarily a regularizer.",
  "Exactly the legal-information property: the output at every position i is unchanged by any modification of tokens at positions > i.",
  "The value of bidirectional context: an obligation that legally MAY read the whole sequence is strictly harder under the mask, so "
  "encoder-style performance is not preserved.",
  "The mask removes an entire class of execution paths from the computation graph, making illegal information physically unavailable "
  "rather than merely unused; this converts a trust property into a structural one.",
  ["ΔL_sem", "ΔB_train", "ΔB_serve"],
  "ΔL_sem on autoregressive obligations is decided by legality, not accuracy; ΔB_train falls because all n positions can be trained in "
  "parallel from one forward pass; ΔB_serve falls because the prefix computation is reusable (TF-047).",
  "Bidirectional (unmasked) attention on the same model and data: X-TMT5 shows, in exact arithmetic, that outputs at positions < n-1 "
  "are UNCHANGED under a perturbation of the last token when the mask is present and CHANGE when it is absent.",
  "Training a separate model per prefix length, or a recurrent/state-space update that structurally cannot see the future (TF-045), "
  "enforces the same legality with different cost.",
  [cv(V_VASWANI, "the masked decoder construction"),
   cv(V_ELHAGE, "the decoder-only causal circuit analysis"),
   cv(V_SHALIZI, "the causal-state formulation in which the legal past is the conditioning sigma-field")],
  TH("TMT-5", "X-TMT5"),
  "B2.2 / B2.3 use the masked decoder throughout; MLX-16 prediction-only causal alias registers the legality-vs-accuracy separation",
  "A system that reads protected future information is judged adequate because its benchmark loss is lower. TMT-5 states this is a "
  "constitution violation regardless of the benchmark number; X-TMT5 exhibits the exact dependence that the mask removes.",
  "PROVED_AT_SCOPE",
  "A masked model gets parallel training and prefix reuse for free; an unmasked one does not. Never compare their compute without "
  "charging the unmasked model for re-running the prefix, and never compare their scores without stating the legality difference.",
  "5. Feature atlas - attention and routing / Causal / padding / block / local masks (R,C)")

F("TF-015", "Padding / block / document masking",
  "s_{ij} <- -infinity on a declared index set: padding masks zero out positions beyond a sequence's true length inside a rectangular "
  "batch; document/block masks forbid attention across concatenated-document boundaries; block masks restrict attention to a declared "
  "partition of positions.",
  "CR", "C because the forbidden set is an interface-level declaration about what the input MEANS (this padding is not data; these two "
  "documents are unrelated); R because it is enforced on the routing scores.",
  "The per-sequence result: a padding-masked batch returns exactly what per-sequence evaluation would return, so batching is "
  "semantics-preserving.",
  "Cross-document information flow: a document mask makes a genuine cross-document dependency unreachable, so an obligation that needs "
  "it is NOT preserved.",
  "The mask asserts an independence the interface knows and the content does not display; enforcing it prevents the model from "
  "learning spurious dependence on batch-packing artifacts (position of a document inside a packed sequence).",
  ["ΔL_sem", "ΔL_rob", "ΔB_train", "ΔB_serve"],
  "ΔB_train and ΔB_serve fall through packing (TF-056) which the mask makes safe; ΔL_rob improves by removing packing-order artifacts; "
  "ΔL_sem degrades only if a real cross-document dependency was masked away.",
  "Pack documents identically but DO NOT mask across boundaries: the throughput mechanism is held exactly and the declared independence "
  "is removed, isolating the throughput gain from the contamination cost.",
  "Per-sequence (unpacked) batching with padding waste enforces the same independence at higher cost; resetting position indices at "
  "each document boundary enforces part of it structurally.",
  [cv(V_VASWANI, "the masked-score mechanism that block and padding masks reuse"),
   tv("Raffel, Shazeer, Roberts, Lee, Narang, Matena, Zhou, Li, Liu (2020). Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer (T5), JMLR 21", "sequence packing with boundary handling at scale"),
   cv(V_ELHAGE, "the reading in which a masked edge is an absent circuit path rather than a small weight")],
  TH("TMT-5", "X-TMT5"),
  "B2.1 (packing interacts with tokenizer length) and B2.20 parallelism/precision repricing (packing is a throughput mechanism)",
  "Removing document masks while packing leaves protected performance and robustness unchanged at matched throughput, which would "
  "show the declared independence is not doing work.",
  "REGISTERED_FOR_EXPERIMENT",
  "Packing without masking buys throughput by leaking context. Meter cross-boundary attention mass explicitly; a throughput number "
  "reported without it is not comparable to an unpacked baseline.",
  "5. Feature atlas - attention and routing / Causal / padding / block / local masks (R,C)")

F("TF-016", "Number of heads H",
  "The count of parallel attention channels per layer, each with its own (W_h^Q, W_h^K, W_h^V) and its own softmax over sources. The "
  "layer output is W^O [A_1(X); ...; A_H(X)]. H is the granularity at which the layer can route by SEVERAL different criteria at once.",
  "R", "R alone: H is routing-factorization granularity. It changes neither the carried state's dimension (when H d_h = d) nor the "
  "local transform.",
  "Total projection parameters and FLOPs when H d_h = d is held: the layer's cost is invariant to the split.",
  "The number of simultaneously expressible, independently normalized routing criteria: one head must commit to a single softmax over "
  "sources, so K distinct simultaneous dependency relations need K heads (or depth).",
  "Heads are parallel routing factors. When an obligation requires several distinct relations at the same position (syntactic "
  "antecedent AND topical source AND positional predecessor), a single normalized channel must average them; separate heads need not.",
  ["ΔL_sem", "ΔB_serve", "ΔB_mem"],
  "At fixed H d_h all burdens are flat and ΔL_sem tracks the multiplicity of required relations; head REDUNDANCY is expected and is "
  "not by itself a defect.",
  "H heads that all share one (W^Q, W^K) pair but keep separate W^V: the parallel-channel count and cost are identical and the "
  "distinct-criteria mechanism is removed, so any gain attributed to 'more heads' separates from 'more criteria'.",
  "A single head applied at several depths in sequence realizes multiple criteria serially; a block-diagonal wide head is "
  "arithmetically identical to H narrow heads.",
  [cv(V_VASWANI, "multi-head attention and the H d_h = d convention"),
   cv(V_ELHAGE, "the per-head circuit decomposition and the observation that heads specialize"),
   tv("Michel, Levy, Neubig (2019). Are Sixteen Heads Really Better than One?, NeurIPS 2019", "the empirical head-redundancy finding that the 'granularity, not necessity' reading predicts")],
  None, "B2.4 head factorization (vary the number of independent dependency relations at matched compute/parameters)",
  "Optimal H is shown to follow sequence length or parameter count alone, with no dependence on the multiplicity of required "
  "dependency relations, at matched compute.",
  "REGISTERED_FOR_EXPERIMENT",
  "Head count changes nothing in the FLOP budget at fixed H d_h, so it is a free-looking knob. Charge the search over H to ΔB_search "
  "and report the (H, d_h) pair, never H alone.",
  "13. Small-feature closure table / head count (R)")

F("TF-017", "Multi-head attention (the composed mechanism)",
  "The full sublayer A(X) = W^O concat_h [ softmax((XW_h^Q)(XW_h^K)^T / sqrt(d_h) + M + B) X W_h^V ], i.e. H independently normalized "
  "content-addressed reads of the same sequence, concatenated and mixed by one output map W^O.",
  "RT", "R because it is the token-to-token dependency-selection stage; T because W^V and W^O are local transforms on the routed "
  "payload.",
  "Permutation equivariance in the SOURCE index when no position mechanism and no mask are present: attention alone cannot distinguish "
  "order, which is exactly why TF-005..TF-008 are required (TMT-1).",
  "Sparsity or interpretability of the resulting attention pattern: the map from weights to attention pattern is many-to-one, so "
  "'the head attends to X' is not an invariant of the mechanism.",
  "Content-addressed dynamic routing: the set of edges materialized on input x is chosen by x, so the layer pays for E(x) rather than "
  "for a fixed graph that must cover the union over all x (TMT-3).",
  ["ΔB_serve", "ΔB_mem", "ΔL_sem", "ΔB_search"],
  "ΔB_serve rises as Theta(n^2 d) for the scores and ΔB_mem as Theta(n^2) for the materialized weights (unless tiled, TF-073); "
  "ΔL_sem improves exactly where dynamic dependency selection is required.",
  "Replace the softmax weights by a FIXED (input-independent) attention pattern of the same sparsity, learned once: identical payload "
  "transport and cost, dynamic selection removed. TMT-3 predicts the loss is governed by |union_x E(x)| - E_x|E(x)|.",
  "Hard kNN retrieval over the key store, gated linear attention, or a state-space scan (TF-045) implement content-dependent mixing "
  "with different cost signatures; MoE routing (TF-083) is the same selection idea over experts instead of positions.",
  [cv(V_VASWANI, "the mechanism as specified"),
   cv(V_ELHAGE, "the circuit-level reading of what a head computes"),
   cv(V_OLSSON, "induction heads as an instance of learned content-addressed routing"),
   cv(V_MERRILL_PAR, "the expressivity ceiling of log-precision transformers, which bounds what this mechanism can compute at fixed depth")],
  TH("TMT-3", "X-TMT3"),
  "B2.3 fixed vs dynamic routing (all four arms) and MLX-07 dependency variability x attention/dynamic routing",
  "On an obligation family with a LARGE union-minus-mean edge gap, a fixed sparse graph matches dynamic attention at matched "
  "primitives and matched budget. That is the measurable content of TMT-3 and is the target of RV-377-056.",
  "REGISTERED_FOR_EXPERIMENT",
  "The n^2 score matrix is the cost. Meter it at ΔB_serve and ΔB_mem even when a tiled implementation never materializes it "
  "(TF-073 changes the IO, not the arithmetic), and meter routing DISCOVERY separately at ΔB_search.",
  "5. Feature atlas - attention and routing / Multi-head attention (R,A1)")

F("TF-018", "MHA / GQA / MQA key-value head sharing",
  "Let H_q be the query-head count and H_kv <= H_q the number of independently materialized key/value head pairs, with query heads "
  "partitioned into H_kv groups sharing one (K, V). MHA is H_kv = H_q, MQA is H_kv = 1, GQA is intermediate. By TMT-13 the "
  "autoregressive cache holds Theta(2 L n d H_kv) elements.",
  "RHP", "R because grouping constrains which routing channels may differ in what they retrieve; H because the shared K/V is the cached "
  "serving state; P because the cache size drives serving memory bandwidth.",
  "The query-side routing criteria: each of the H_q heads keeps its own W^Q, so per-head selection directions are not forced to "
  "coincide.",
  "Per-head key/value maps: two query groups that require functionally distinct K or V maps for exact behaviour cannot both be served "
  "by a shared pair unless a compensating transform exists elsewhere.",
  "Cache size and the memory traffic per decoded token scale with H_kv, not H_q, so sharing buys serving bandwidth by spending "
  "key/value diversity. The optimum is set by how heterogeneous the required K/V maps actually are.",
  ["ΔB_mem", "ΔB_comm", "ΔB_serve", "ΔL_sem"],
  "ΔB_mem and ΔB_comm fall linearly in H_kv (X-TMT13 verifies the element count exactly: MHA = 4x GQA-4 = 8x MQA at H = 8); ΔL_sem "
  "degrades when required K/V heterogeneity exceeds H_kv.",
  "Keep H_kv = H_q (full MHA) but TIE the K/V parameters to a shared value by construction while still storing H_q copies: the memory "
  "cost of MHA is paid and the diversity is removed, separating 'fewer bytes' from 'fewer distinct maps'.",
  "Low-rank joint compression of K and V (a latent KV) reaches the same bandwidth with a different diversity constraint; cross-layer "
  "KV sharing reduces the L factor instead of the H_kv factor.",
  [tv("Shazeer (2019). Fast Transformer Decoding: One Write-Head is All You Need, arXiv:1911.02150", "the multi-query construction and its bandwidth argument"),
   tv("Ainslie, Lee-Thorp, de Jong, Zemlyanskiy, Lebron, Sanghai (2023). GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints, EMNLP 2023", "the grouped interpolation and uptraining procedure"),
   cv(V_VASWANI, "the MHA endpoint of the family")],
  TH("TMT-13", "X-TMT13"),
  "B2.5 MHA -> GQA -> MQA (factorial: KV relation heterogeneity x sequence length x memory bandwidth price x cache capacity)",
  "A single H_q : H_kv ratio is optimal across obligations whose K/V heterogeneity and serving price vectors are deliberately varied, "
  "which would falsify the frontier reading of TMT-7/TMT-13 and close gap G-T04 the wrong way.",
  "PROVED_AT_SCOPE",
  "Cache bytes are the point: report 2 L n d H_kv explicitly per arm. A quality comparison at equal PARAMETERS between MHA and MQA "
  "hides that they occupy different serving-memory budgets.",
  "5. Feature atlas - attention and routing / MHA / GQA / MQA (R,H,P)")

F("TF-019", "Sparse / local / sliding-window attention",
  "Restrict the legal source set for position i to S(i) subsetneq {0..i}: a sliding window S(i) = {i-W+1..i}, a strided/block pattern, "
  "or a window plus a few global tokens. Cost falls from Theta(n^2) to Theta(n |S|), and the model becomes a |S|-window machine at "
  "each layer (with an effective receptive field that grows with depth).",
  "RP", "R because it is a FIXED routing prior; P because the whole point is the compute/memory reduction.",
  "Dependencies inside the window at every layer, and dependencies outside it that are RECOVERABLE by composition through depth "
  "(a depth-L window-W stack reaches back L(W-1) positions).",
  "Single-layer long-range dependence, and any dependency that neither fits in the window nor survives the lossy composition through "
  "intermediate positions.",
  "A window is a hard distance prior: it is exactly right when the true dependency structure is local or recoverable, and it is "
  "TMT-3's fixed graph E_* when it is not, in which case exactness requires E_* to cover the union over all inputs.",
  ["ΔB_serve", "ΔB_mem", "ΔL_sem", "ΔL_gen"],
  "ΔB_serve and ΔB_mem fall from Theta(n^2) to Theta(nW); ΔL_sem degrades exactly on obligations with required edges outside the "
  "window that depth cannot recover.",
  "A RANDOM sparse pattern with the identical edge count and identical cost: the compute saving is held exactly and the locality prior "
  "is removed. TMT-3 predicts the difference is governed by how well the pattern covers union_x E(x).",
  "A distance bias with a steep slope (TF-008) is the soft version; a state-space recurrence (TF-045) compresses rather than truncates "
  "the far past; retrieval (TF-046) re-admits specific far tokens.",
  [tv("Child, Gray, Radford, Sutskever (2019). Generating Long Sequences with Sparse Transformers, arXiv:1904.10509", "strided/block sparse attention patterns"),
   tv("Beltagy, Peters, Cohan (2020). Longformer: The Long-Document Transformer, arXiv:2004.05150", "sliding window plus global tokens"),
   tv("Zaheer, Guruganesh, Dubey, Ainslie, Alberti, Ontanon, Pham, Ravula, Wang, Yang, Ahmed (2020). Big Bird: Transformers for Longer Sequences, NeurIPS 2020", "the window+global+random construction and its coverage argument"),
   cv(V_JELASSI, "the measured failure of compressed/limited-state models on copying, the clearest case of a required edge the prior omits")],
  TH("TMT-3", "X-TMT3"),
  "B2.3 fixed vs dynamic routing (fixed-sparse arm) and B2.11 context vs recurrence vs retrieval",
  "A fixed window matches dense attention on an obligation family constructed to have high dependency variability and a large "
  "union-minus-mean gap, at matched cost. RV-377-056 measures exactly this gap.",
  "REGISTERED_FOR_EXPERIMENT",
  "The compute saving is visible and the coverage loss is not. Meter the fraction of required edges OUTSIDE the pattern per input, "
  "not just the FLOP reduction; a long context served by a narrow window is not the same object as a long context served densely.",
  "5. Feature atlas - attention and routing / Sparse/sliding-window attention (R,P)")

F("TF-020", "Cross-attention",
  "Attention whose queries come from one stream and whose keys/values come from another: Q = X_tgt W^Q, K = X_src W^K, V = X_src W^V, "
  "with X_src produced by a separately maintained encoder or memory. The two streams keep distinct state and distinct update rules.",
  "RC", "R because it is routing between two state collections; C because keeping the streams separate is an interface decision about "
  "what the source MEANS relative to the target.",
  "The source representation: cross-attention reads X_src without modifying it, so the source stream's semantics is preserved under "
  "any number of target-side reads.",
  "Symmetry: the target can condition on the source but not conversely, so a claim proved for early fusion (one concatenated stream) "
  "does not transfer.",
  "Maintaining separate state lets the source be encoded ONCE and read many times (and cached, versioned or replaced) instead of being "
  "re-encoded jointly with every target; the saving is the reuse factor.",
  ["ΔB_serve", "ΔB_mem", "ΔL_sem", "ΔB_update"],
  "ΔB_serve falls when one encoded source serves many targets and rises otherwise; ΔB_update falls because the source can be updated "
  "without retraining the target path; ΔL_sem degrades when the obligation needs early, deep interaction between the streams.",
  "Early fusion: concatenate the source and target into ONE stream with full self-attention at matched total length and parameters. "
  "The routing capacity is the same or greater; only the state separation and its reuse are removed.",
  "A prefix (the source tokens placed in the same stream ahead of the target) reproduces the conditioning without separate state; a "
  "retrieval store (TF-046) is cross-attention with an external, mutable source.",
  [cv(V_VASWANI, "the encoder-decoder cross-attention construction"),
   cv(V_RETRO, "chunked cross-attention over a retrieved corpus as a large-scale realization"),
   tv("Bahdanau, Cho, Bengio (2015). Neural Machine Translation by Jointly Learning to Align and Translate, ICLR 2015", "the original source-target alignment mechanism")],
  None, "B2.11 context vs recurrence vs retrieval (source-separation arm) and B2.17 RAG/tool authority",
  "Early fusion matches separate-stream cross-attention at matched cost on a task family where the source is reused many times per "
  "encode, which would remove the reuse mechanism as the explanation.",
  "REGISTERED_FOR_EXPERIMENT",
  "Cross-attention looks cheap because the source encode is amortized. Report the reuse factor (target queries per source encode); at "
  "reuse 1 it is strictly more expensive than early fusion.",
  "5. Feature atlas - attention and routing / Cross-attention (R,C)")

F("TF-021", "Attention dropout",
  "During training only, each attention weight is zeroed independently with probability p and the survivors are rescaled by 1/(1-p): "
  "alpha' = alpha . Bernoulli(1-p) / (1-p). At evaluation the identity is used, so the SERVING function is unchanged by the mechanism.",
  "UR", "U because it is a development-time stochastic regularizer acting on the update distribution; R because the object it perturbs "
  "is the routing distribution.",
  "The serving-time computation exactly: with dropout disabled at evaluation, the deployed function is the undropped one.",
  "The training trajectory and the learned weights: two runs differing only in p reach different parameters, so nothing about the "
  "learned solution is preserved.",
  "Randomly removing routing edges during development prevents any single edge from being necessary, pushing the layer toward "
  "redundant routing that degrades gracefully when a source is absent or noisy at serve time.",
  ["ΔL_gen", "ΔL_rob", "ΔB_train"],
  "ΔL_gen and ΔL_rob improve in the regime where the model would otherwise fit routing to spurious single edges; ΔB_train rises "
  "(slower convergence) and ΔB_serve is exactly unchanged.",
  "Add ZERO-MEAN NOISE of the same variance to the attention logits instead of dropping edges: the stochastic-perturbation magnitude "
  "is matched and the edge-removal structure is removed.",
  "DropConnect on W^Q/W^K, head dropout (dropping whole channels), or label smoothing reach related regularization through different "
  "perturbation structure; an explicit entropy penalty on alpha is the deterministic analogue.",
  [tv("Srivastava, Hinton, Krizhevsky, Sutskever, Salakhutdinov (2014). Dropout: A Simple Way to Prevent Neural Networks from Overfitting, JMLR 15", "the dropout mechanism and the inverted-scaling convention"),
   cv(V_VASWANI, "the placement of dropout on attention weights and residual branches in the Transformer"),
   cv(V_LYLE, "the finding that regularizers act on optimization state, not only on the function class")],
  None, "B2.9 normalization / B2.8 residual connection factorials include the regularization axis; MLX-10 optimizer implicit bias",
  "Attention dropout improves protected performance in a regime with no overfitting and no serve-time source noise, which would "
  "rule out the redundancy mechanism.",
  "REGISTERED_FOR_EXPERIMENT",
  "Dropout is free at serve time and costs training steps. Charge the extra steps to ΔB_train and charge the search over p to "
  "ΔB_search; a tuned-p arm against an untuned baseline is not controlled.",
  "5. Feature atlas - attention and routing / Attention dropout (R,U)")


# ======================================================================================================================
# C. Local transforms / MLP (calculus section 6)
# ======================================================================================================================

F("TF-022", "Position-wise MLP",
  "G(x) = W_2 phi(W_1 x + b_1) + b_2 applied INDEPENDENTLY and identically at every position, with W_1 in R^{d_ff x d}, "
  "W_2 in R^{d x d_ff}. It mixes across the feature axis only; it moves no information between positions.",
  "TS", "T because it is the layer's nonlinear local computation; S because it reads from and writes to the residual coordinate.",
  "The position axis: applying any permutation to the sequence and then G equals applying G and then the permutation, so the MLP "
  "cannot introduce or destroy order information.",
  "Linearity of the block, hence superposition of features: phi makes the map non-additive, so 'the response to x + y is the sum of "
  "responses' is not preserved.",
  "After routing has gathered the relevant content into one position's residual coordinate, the MLP performs the nonlinear feature "
  "CONSTRUCTION on that coordinate; capacity added here buys per-position computation without adding token-token edges.",
  ["ΔB_serve", "ΔB_train", "ΔB_mem", "ΔL_sem"],
  "All burdens rise as Theta(2 d d_ff) per token per layer (the dominant parameter and FLOP term in most decoders); ΔL_sem improves "
  "where the obligation needs per-position nonlinear composition rather than more routing.",
  "Replace G by a LINEAR map W_2 W_1 of the same rank and the same FLOP count (via an explicit d_ff-dimensional bottleneck): the "
  "parameter and compute budget are matched and the nonlinearity is removed.",
  "A depthwise/position-wise convolution of kernel 1 is the same operator; a per-position key-value memory lookup (the "
  "'MLP as memory' reading) realizes the same map with an explicitly retrievable parameterization.",
  [cv(V_VASWANI, "the position-wise feed-forward sublayer as specified"),
   tv("Geva, Schuster, Berant, Levy (2021). Transformer Feed-Forward Layers Are Key-Value Memories, EMNLP 2021", "the key-value-memory reading of the MLP, i.e. the implementation-equivalent alternative"),
   cv(V_ELHAGE, "the residual-stream decomposition in which MLP and attention write to the same shared state")],
  None, "B2.7 MLP width/gating (arms: linear / simple nonlinearity / gated local transform, routing need held fixed)",
  "An obligation requiring per-position nonlinear composition is served equally by a rank-matched LINEAR block at matched compute, "
  "which would show the nonlinearity is not the mediator.",
  "REGISTERED_FOR_EXPERIMENT",
  "The MLP is usually the majority of both parameters and FLOPs. Report d_ff alongside d; a 'model size' that quotes only d "
  "understates serving cost by the expansion ratio.",
  "6. Feature atlas - local transforms / MLPs / Position-wise MLP (T,S)")

F("TF-023", "MLP width / expansion ratio",
  "The ratio rho = d_ff / d (conventionally 4 for an ungated MLP; near 8/3 for gated variants at matched parameters). It sets the "
  "dimension of the intermediate workspace phi(W_1 x) and hence the number of independent nonlinear features one block can construct "
  "before projecting back to d.",
  "STP", "S because d_ff is a (transient) state dimension; T because it bounds the local transform's capacity; P because the block's "
  "cost is 2 rho d^2 per token.",
  "The residual stream dimension d and therefore the interface to every other mechanism: rho changes the block's internals only.",
  "The number of simultaneously constructible local features: at small rho the block must reuse intermediate units across unrelated "
  "features, so per-feature independence is not preserved.",
  "rho is the local-workspace-versus-compute frontier: widening buys more independent nonlinear features per block at linear cost in "
  "FLOPs, and is dominated by adding depth once feature construction is no longer the binding constraint.",
  ["ΔB_serve", "ΔB_train", "ΔB_mem", "ΔL_sem"],
  "All three burdens rise linearly in rho; ΔL_sem improves only while local-feature capacity binds.",
  "Hold rho and hold FLOPs but make W_1 BLOCK-DIAGONAL with the same number of nonzeros arranged so the intermediate units cannot mix "
  "input coordinates freely: workspace size is nominally matched and its usable capacity is cut.",
  "Two stacked narrower MLPs with the same total FLOPs, or a mixture-of-experts MLP (TF-083) that raises capacity without raising "
  "per-token FLOPs, reach comparable capacity by different means.",
  [cv(V_VASWANI, "the rho = 4 convention"),
   cv(V_HOFFMANN, "the compute-optimal-allocation frame in which rho competes with depth and data"),
   cv(V_MICHAUD, "the discrete-capability reading of what additional capacity buys")],
  None, "B2.7 MLP width/gating (vary local feature-composition complexity with routing need fixed)",
  "A single rho is optimal across obligations whose local feature-composition complexity is deliberately varied at fixed routing "
  "demand, which would close gap G-T06 against the frontier reading.",
  "REGISTERED_FOR_EXPERIMENT",
  "Expansion ratio is where 'parameter-matched' comparisons usually break: a gated block at rho = 4 has 1.5x the parameters of an "
  "ungated one. Match PARAMETERS and FLOPs explicitly, and say which was matched.",
  "6. Feature atlas - local transforms / MLPs / Width / expansion ratio (S,T,P)")

F("TF-024", "Activation function (ReLU / GELU / SiLU)",
  "The elementwise nonlinearity phi in the MLP: ReLU(x) = max(0, x); GELU(x) = x Phi(x) with Phi the standard normal CDF; "
  "SiLU/Swish(x) = x sigma(x). All three are monotone, unbounded above, bounded below, and agree asymptotically; they differ in "
  "smoothness at 0 and in whether small negative inputs pass a small signal.",
  "TU", "T because phi is the local nonlinearity; U because its derivative shape is what the optimizer sees (ReLU has a dead region "
  "with exactly zero gradient; GELU and SiLU do not).",
  "Universal-approximation capacity: an MLP with any of these activations is dense in continuous functions on compacta, so the "
  "expressible function class is not distinguished by the choice at sufficient width.",
  "The optimization trajectory and the induced feature geometry: the dead-unit behaviour of ReLU and the smooth small-negative "
  "response of GELU/SiLU give different gradient flows from the same initialization.",
  "The activation's derivative profile determines how many units receive gradient early in training and how sharply the response "
  "bends; the claimed advantage of smooth activations is fewer permanently dead units, not greater expressivity.",
  ["ΔB_train", "ΔL_gen", "ΔB_serve"],
  "ΔB_serve differs slightly (GELU/SiLU need an exp or erf, ReLU a compare); ΔB_train and ΔL_gen move through the trajectory, not the "
  "class.",
  "A PIECEWISE-LINEAR approximation of GELU with the same values at a fixed grid and the same serving cost: the response shape is "
  "matched and the exact smoothness is removed, isolating 'shape' from 'smoothness'.",
  "A hard-sigmoid gated unit, a learned-parameter activation (PReLU), or a low-order polynomial approximation at matched response "
  "range all reproduce the response geometry at different serving cost.",
  [tv("Nair, Hinton (2010). Rectified Linear Units Improve Restricted Boltzmann Machines, ICML 2010", "the ReLU form and the dead-unit behaviour"),
   tv("Hendrycks, Gimpel (2016). Gaussian Error Linear Units (GELUs), arXiv:1606.08415", "the GELU form"),
   tv("Elfwing, Uchibe, Doya (2018). Sigmoid-Weighted Linear Units for Neural Network Function Approximation in Reinforcement Learning, Neural Networks 107", "the SiLU form"),
   cv(V_LYLE, "the identification of dead/saturated units as a cause of plasticity loss, which is the mechanism this entry names")],
  None, "B2.7 MLP width/gating (activation arm) and MLX-10 optimizer implicit bias",
  "Matched-shape activations with and without a dead region train identically at matched width and schedule, which would remove the "
  "gradient-profile mechanism and leave the choice arbitrary.",
  "REGISTERED_FOR_EXPERIMENT",
  "Activation choice changes serving cost (transcendental vs compare) and can change the numerically safe precision. Charge both, and "
  "never report an activation swap as a semantic capability change.",
  "6. Feature atlas - local transforms / MLPs / ReLU / GELU / SiLU (T,U)")

F("TF-025", "GLU / SwiGLU gating",
  "A multiplicative local gate: G(x) = W_2 ( phi(W_g x) (elementwise product) W_1 x ), with three matrices instead of two. SwiGLU "
  "takes phi = SiLU. At matched parameter count d_ff is reduced by about 2/3 relative to an ungated block.",
  "TR", "T because it is still a per-position transform; R because the elementwise product is content-conditioned selection AMONG "
  "local features - micro-routing inside the block.",
  "Position independence and the residual interface: the gate mixes nothing across positions.",
  "Additivity in the input: the product of two linear reads is quadratic in x, so the block's response is not a sum of independent "
  "feature responses.",
  "Gating lets the value carried by one feature be switched on or off by ANOTHER feature computed from the same coordinate, so a "
  "conditional local computation needs one block rather than a depth-2 construction.",
  ["ΔB_serve", "ΔB_mem", "ΔL_sem", "ΔB_train"],
  "At matched parameters the burdens are flat by construction (d_ff shrinks); at matched d_ff all three rise by 50 percent; ΔL_sem "
  "improves where conditional local transformation is required.",
  "Replace the gate phi(W_g x) by a LEARNED CONSTANT vector g (same shape, same multiply, no input dependence): the extra parameters "
  "and the elementwise multiply are kept and the content-conditioning is removed.",
  "A depth-2 ungated MLP can approximate the product; a bilinear layer without the phi is the ungated GLU; a per-feature attention "
  "gate computes the same conditional selection through the routing path instead.",
  [tv("Dauphin, Fan, Auli, Grangier (2017). Language Modeling with Gated Convolutional Networks, ICML 2017", "the GLU construction"),
   tv("Shazeer (2020). GLU Variants Improve Transformer, arXiv:2002.05202", "the SwiGLU variant and the matched-parameter d_ff adjustment"),
   cv(V_SHAZEER_MOE, "conditional computation as the general mechanism class of which gating is the dense, fine-grained case")],
  None, "B2.7 MLP width/gating (gated local transform arm, matched parameter/FLOP controls)",
  "A gated block shows no advantage over an ungated block on obligations requiring conditional local computation once parameters AND "
  "FLOPs are matched, which would close gap G-T06 against the gating reading.",
  "REGISTERED_FOR_EXPERIMENT",
  "Gating is the canonical place where 'matched parameters' and 'matched FLOPs' disagree. State which was held; a gated block compared "
  "at equal d_ff has 1.5x the compute of its baseline.",
  "6. Feature atlas - local transforms / MLPs / GLU / SwiGLU-like gates (T,R)")


# ======================================================================================================================
# D. Residual stream, normalization, initialization, regularization (calculus section 7)
# ======================================================================================================================

F("TF-026", "Residual connection",
  "y = x + f(x) around every sublayer, so the Jacobian is J_y = I + J_f and a depth-L stack has end-to-end Jacobian "
  "prod_l (I + J_{f_l}). The sublayer computes an INCREMENT to a carried state rather than replacing it.",
  "SU", "S because the identity path makes the residual stream a persistent carried coordinate; U because the identity term is what "
  "the backward pass propagates.",
  "The ability of the block to act as the identity: setting f = 0 leaves the state untouched, so a residual stack can always represent "
  "a shallower one exactly.",
  "Boundedness of the end-to-end Jacobian: prod_l (I + J_{f_l}) can still blow up or collapse when the J_{f_l} are large or aligned, "
  "so 'residuals guarantee trainability' is false.",
  "The explicit identity term in every layer's Jacobian gives a gradient path that does not pass through any learned matrix, so "
  "signal reaches early layers at depth where a plain product prod_l J_{f_l} would have vanished.",
  ["ΔB_train", "ΔL_sem", "ΔB_mem"],
  "ΔB_train falls sharply with depth (trainable deep stacks); ΔB_mem rises slightly (the skip tensor must be kept live); ΔL_sem "
  "improves only through what becomes trainable.",
  "The identical stack WITHOUT the skip (y = f(x)) at the same depth, width and initialization. X-TMT9 computes both end-to-end "
  "Jacobians in exact rational arithmetic: the residual product stays near I while the plain product contracts.",
  "A gated/highway skip y = g(x) x + (1-g(x)) f(x), a fixed-scale skip y = alpha x + f(x), or a dense (DenseNet-style) concatenation "
  "supply an identity-carrying path with different scaling behaviour.",
  [tv("He, Zhang, Ren, Sun (2016). Deep Residual Learning for Image Recognition, CVPR 2016", "the residual construction and the depth-trainability claim"),
   cv(V_ELHAGE, "the residual stream as a shared additive communication channel that every sublayer reads and writes"),
   cv(V_COHEN_EOS, "the curvature-regime account of why an identity path is not by itself a stability guarantee")],
  TH("TMT-9", "X-TMT9"),
  "B2.8 residual connection (vary depth and perturbation magnitude; shallow-regime negative control)",
  "A deep stack without skips trains as well as one with skips at matched depth, width and schedule, or a residual stack is shown "
  "stable for arbitrary J_f - either would break the Jacobian-identity reading. X-TMT9 fixes the algebra at its scope.",
  "PROVED_AT_SCOPE",
  "Skips are nearly free in FLOPs and not free in activation memory. Charge the retained skip tensors to ΔB_mem, and do not credit "
  "residuals with capability gains that are really depth gains they made reachable.",
  "7. Feature atlas - residual stream and normalization / Residual connection (S,U)")

F("TF-027", "Residual stream (as shared state)",
  "The sequence of vectors r^{(0)}, ..., r^{(L)} in R^{n x d} that every sublayer reads from and adds to. Because writes are additive "
  "into one d-dimensional space, features written by different mechanisms SUPERPOSE, and any read is a linear functional of the sum.",
  "SH", "S because it is the coordinate system of the whole model; H because it is the fast working memory through which mechanisms at "
  "different depths communicate within one forward pass.",
  "Additive decomposability: the stream at layer l is exactly the sum of the embedding and every sublayer's write up to l, so the "
  "path decomposition is exact.",
  "One-feature-per-direction: when more features are carried than d, directions must be shared, so linear readability of any single "
  "feature without interference is NOT preserved.",
  "The stream is a bandwidth-limited shared bus. Interference between concurrently carried features is the cost of the bus; "
  "superposition is what lets a width-d model carry more than d features when they are rarely simultaneously active.",
  ["ΔL_sem", "ΔL_rob", "ΔB_mem"],
  "ΔB_mem is the activation cost n d per layer; ΔL_sem and ΔL_rob degrade as the number of simultaneously live features approaches "
  "and exceeds d.",
  "Force each sublayer to write into a DISJOINT slice of the width (no shared directions, same total width, same parameters): the bus "
  "is partitioned, superposition is impossible, and the interference mechanism is removed.",
  "Concatenation-based state (each layer appends its own coordinates) removes superposition at linear memory cost; a bottlenecked "
  "read/write with per-layer projections reproduces the sharing with an explicit capacity constraint.",
  [cv(V_ELHAGE, "the residual-stream-as-communication-channel framing and the path decomposition"),
   cv(V_SHAI, "the measured geometric structure (belief-state simplices) that the stream carries"),
   cv(V_PIOTROWSKI, "the constrained-belief-update account of that geometry"),
   cv(V_MICHAUD, "the discrete-capability reading of what a fixed-width stream can carry")],
  None, "MLX-41 probe vs causal-use separation and MLX-42 mechanism witness invariance; gap G-T08 residual-stream superposition/interference law",
  "A model is shown to carry, without measurable interference, a number of simultaneously active linearly-readable features far "
  "exceeding d, which would contradict the bandwidth reading.",
  "OPEN_NONBLOCKING",
  "The stream is where 'my probe found feature X' becomes an unpriced claim. Charge every interpretability claim with a causal "
  "intervention (MLX-41), and charge n d L activation bytes to ΔB_mem.",
  "7. Feature atlas - residual stream and normalization / Residual stream (S,H)")

F("TF-028", "LayerNorm",
  "LN(x) = gamma (x - mu(x)) / sqrt(sigma^2(x) + eps) + beta with mu and sigma^2 the mean and variance over the d feature coordinates "
  "of a single position. It is exactly invariant to x -> a x + b 1 for a > 0 (up to eps), then re-parameterized by learned gamma, beta.",
  "NU", "N because it imposes a gauge (per-position shift and scale) on the state; U because that gauge changes the loss surface the "
  "optimizer traverses.",
  "Per-position affine gauge: the output is unchanged (as eps -> 0) by adding a constant to all coordinates or by rescaling them, so "
  "any claim about activation scale upstream of LN is not observable downstream.",
  "Relative magnitude information across positions and across layers: LN discards the per-position norm, so an obligation that depends "
  "on absolute activation scale is not preserved.",
  "Removing scale and shift drift makes the effective input distribution of each sublayer stationary across depth and across training "
  "steps, which conditions the optimization problem; the learned gamma, beta restore the expressivity the gauge removed.",
  ["ΔB_train", "ΔL_rob", "ΔB_serve"],
  "ΔB_train falls (larger stable learning rates, less depth-dependent drift); ΔB_serve rises by the mean/variance reduction and the "
  "division; ΔL_rob improves against input-scale shift.",
  "Replace LN by a FIXED affine map with the same gamma, beta and a constant divisor equal to the average observed sigma: the "
  "arithmetic shape and the parameters are kept and the per-input normalization is removed.",
  "RMSNorm (TF-029) drops the recentering; a fixed scaling schedule per depth reproduces the conditioning without per-input statistics; "
  "weight normalization moves the gauge onto the parameters instead of the activations.",
  [tv("Ba, Kiros, Hinton (2016). Layer Normalization, arXiv:1607.06450", "the LayerNorm construction and its invariances"),
   cv(V_COHEN_EOS, "the curvature/step-size regime that normalization moves the run into"),
   cv(V_LYLE, "normalization as one of the identified levers on plasticity and conditioning")],
  None, "B2.9 normalization (factorial: depth x activation-scale drift x precision x batch/sequence statistics; arms none / center+scale / RMS-like)",
  "A deep stack trains equally well with no normalization at matched depth, learning rate schedule and precision, which would remove "
  "the conditioning mediator and leave normalization an arbitrary convention.",
  "REGISTERED_FOR_EXPERIMENT",
  "Normalization is cheap in FLOPs and expensive in memory traffic and in precision requirements. Charge the reduction's bandwidth to "
  "ΔB_serve, and record eps and the accumulation precision (TF-031) with any exactness claim.",
  "7. Feature atlas - residual stream and normalization / LayerNorm (N,U)")

F("TF-029", "RMSNorm",
  "RMS(x) = gamma x / sqrt(mean(x^2) + eps): the same per-position scale gauge as LayerNorm with the recentering (subtracting mu) and "
  "usually the bias beta removed. It is invariant to x -> a x for a > 0 but NOT to x -> x + b 1.",
  "NUP", "N/U as for LayerNorm; P additionally, because dropping the mean pass removes one reduction over d per position and one "
  "elementwise subtraction, which matters at serving bandwidth.",
  "Positive-scale gauge invariance, which is the part of LayerNorm's invariance that the conditioning argument actually uses.",
  "Shift invariance: a constant offset added to all coordinates survives RMSNorm, so any downstream mechanism sensitive to the mean is "
  "affected where LayerNorm would have removed it.",
  "If the residual stream's per-position mean carries no obligation-relevant information, recentering is pure cost; RMSNorm is the "
  "cheaper gauge that keeps the scale control and discards the unused shift control.",
  ["ΔB_serve", "ΔB_mem", "ΔB_train", "ΔL_sem"],
  "ΔB_serve and the memory traffic fall relative to LayerNorm; ΔB_train and ΔL_sem are predicted flat in the regime where the mean "
  "carries nothing, and degrade otherwise.",
  "LayerNorm with the recentering computed but then ADDED BACK (compute mu, subtract it, then add it): identical cost to LayerNorm, "
  "identical function to RMSNorm-with-bias, isolating 'the cost of recentering' from 'the effect of recentering'.",
  "LayerNorm with beta frozen at zero and the mean empirically near zero is functionally close; scaled weight normalization moves the "
  "same gauge to the parameters.",
  [tv("Zhang, Sennrich (2019). Root Mean Square Layer Normalization, NeurIPS 2019", "the RMSNorm construction and the claim that recentering is dispensable"),
   tv("Ba, Kiros, Hinton (2016). Layer Normalization, arXiv:1607.06450", "the LayerNorm baseline whose invariance set RMSNorm narrows"),
   cv(V_TVM, "the general point that a cheaper realization of the same semantics is a P-level, not a semantic, improvement")],
  None, "B2.9 normalization (RMS-like arm, same factorial)",
  "An obligation is found where the per-position MEAN of the residual stream is load-bearing and RMSNorm therefore degrades protected "
  "performance while LayerNorm does not - or, conversely, RMSNorm is shown to help beyond its cost saving.",
  "REGISTERED_FOR_EXPERIMENT",
  "Report the normalizer WITH its eps and accumulation dtype. An RMSNorm-for-LayerNorm swap is a serving-cost change; presenting the "
  "resulting throughput gain as a model improvement is an implementation-label error (TMT-7).",
  "7. Feature atlas - residual stream and normalization / RMSNorm (N,U,P)")

F("TF-030", "Pre-norm vs post-norm placement",
  "Pre-norm: x_{l+1} = x_l + f_l(N(x_l)), so the identity path from input to output is normalization-free. Post-norm: "
  "x_{l+1} = N(x_l + f_l(x_l)), so every skip passes through a normalizer. The two give different end-to-end Jacobians: pre-norm "
  "keeps an exact identity term at every depth, post-norm does not.",
  "NU", "N/U: the placement is a pure update-geometry decision; it changes neither parameter count nor FLOPs.",
  "Parameter count, FLOPs and the per-block function class: both placements use the same f and the same N.",
  "The depth-composed Jacobian and hence trainability at depth: post-norm stacks typically require warmup (TF-059) to train at depth "
  "where pre-norm stacks do not.",
  "Pre-norm preserves the exact identity term of TMT-9 through arbitrary depth; post-norm multiplies the skip by the normalizer's "
  "Jacobian at every layer, so gradient magnitude at depth depends on the accumulated normalizer geometry.",
  ["ΔB_train", "ΔL_sem"],
  "ΔB_train falls for pre-norm at depth (fewer warmup steps, larger stable learning rate); ΔB_serve and ΔB_mem are identical; ΔL_sem "
  "differences are reported to run through what becomes trainable, not through capacity.",
  "Post-norm with the normalizer's gain FROZEN to the identity at initialization: placement is post-norm, the initial Jacobian is "
  "pre-norm-like, so the placement effect separates from the initialization effect.",
  "A residual scaling factor alpha_l (DeepNet-style or a learned per-layer scale) applied to post-norm reproduces the pre-norm "
  "Jacobian condition without moving the normalizer; a final-only normalizer is a third placement.",
  [tv("Xiong, Yang, He, Zheng, Zheng, Xing, Zhang, Lan, Wang, Liu (2020). On Layer Normalization in the Transformer Architecture, ICML 2020", "the pre-norm/post-norm gradient analysis and the warmup implication"),
   cv(V_COHEN_EOS, "the edge-of-stability framing of why placement changes the usable learning rate"),
   cv(V_VASWANI, "the original post-norm placement")],
  TH("TMT-9", "X-TMT9"),
  "B2.10 pre/post norm (optimization stability vs depth and residual magnitude)",
  "Post-norm trains as easily as pre-norm at large depth with no warmup and the same learning rate, which would remove the "
  "Jacobian-composition mediator.",
  "REGISTERED_FOR_EXPERIMENT",
  "Placement is free in FLOPs and buys schedule. Charge the warmup steps a post-norm stack needs to ΔB_train; comparing pre-norm with "
  "warmup against post-norm without it is not a controlled comparison.",
  "7. Feature atlas - residual stream and normalization / Pre-norm vs post-norm (N,U)")

F("TF-031", "Epsilon constants and value clipping",
  "The additive eps inside every normalizer's sqrt, the clamp applied to logits or activations (clip(x, -c, c)), and the "
  "denominator floors in the optimizer (Adam's eps). Each replaces an exactly-defined but numerically unstable operation with a "
  "nearby bounded one, at a bias whose size is set by the constant.",
  "NU", "N because these are conditioning constants on the state and its statistics; U because Adam's eps and clipping change the "
  "update law itself.",
  "The computation in the regime where the quantity being guarded is far from its degenerate value: for sigma^2 >> eps the normalizer "
  "is unchanged to within eps/2 sigma^2.",
  "Exactness near the boundary: an activation at the clamp, or a variance comparable to eps, is silently altered, so 'this model "
  "computes f' is not preserved there.",
  "These constants set the precision at which a degenerate case stops being handled exactly. Their optimum is a function of the "
  "numeric format and the activation statistics, not of the task semantics.",
  ["ΔL_rob", "ΔB_train", "ΔL_sem"],
  "Larger eps and tighter clipping improve ΔL_rob (no NaN, no overflow) and cost ΔL_sem near the boundary; ΔB_train falls where the "
  "alternative is a diverged run.",
  "Run the identical model with eps and clips set to their degenerate limits (eps -> 0, c -> infinity) in WIDE arithmetic: the "
  "semantics is the unguarded one and the numerical hazard is removed by precision instead of by a constant, separating the two.",
  "Higher-precision accumulation (TF-075) removes the need for a large eps; a smooth soft-clip (tanh-based) replaces the hard clamp "
  "with a bounded map of the same range.",
  [tv("Ba, Kiros, Hinton (2016). Layer Normalization, arXiv:1607.06450", "the eps inside the normalizer"),
   tv("Kingma, Ba (2015). Adam: A Method for Stochastic Optimization, ICLR 2015", "the optimizer eps and its role as a denominator floor"),
   tv("Micikevicius, Narang, Alben, Diamos, Elsen, Garcia, Ginsburg, Houston, Kuchaiev, Venkatesh, Wu (2018). Mixed Precision Training, ICLR 2018", "the interaction of these constants with the numeric format")],
  TH("TMT-12", "X-TMT12"),
  "B2.9 normalization (precision axis of the factorial) and B2.14 quantization / distillation",
  "An eps or clip value is shown optimal independently of the numeric format and the activation statistics, which would make it a "
  "semantic rather than a numerical constant.",
  "REGISTERED_FOR_EXPERIMENT",
  "These constants are almost never reported and they change results. Record eps, clip bounds and accumulation dtype in every receipt; "
  "an 'exact' claim that does not state them is not checkable (X-TMT12 is the general form of the collision they can cause).",
  "7. Feature atlas - residual stream and normalization / epsilon constants / clipping (N,U)")

F("TF-032", "Initialization scheme",
  "The distribution from which Theta_0 is drawn: Glorot/Xavier (variance 2/(fan_in + fan_out)), He/Kaiming (2/fan_in, matched to "
  "ReLU), small-scale output-projection init (often scaled by 1/sqrt(2L) in deep decoders), and zero-init for biases and for the "
  "final projection of each residual branch.",
  "US", "U because Theta_0 is the starting point of the development trajectory and fixes the early gradient scale; S because it sets "
  "the initial geometry of the state coordinates.",
  "The function CLASS: every initialization reaches the same parameter space, so nothing about what the model can represent depends "
  "on Theta_0.",
  "Which solutions are REACHABLE at a given budget: the trajectory and hence the found solution are not preserved, and neither is the "
  "forward/backward signal scale at depth.",
  "Initialization sets the forward and backward variance at every depth. A scheme that keeps both near 1 across L layers gives "
  "non-degenerate gradients at step 0; a residual-branch init near zero makes the stack start as the identity and grow function "
  "gradually.",
  ["ΔB_train", "ΔL_gen"],
  "ΔB_train falls sharply when the scheme matches the activation and depth (fewer steps, larger stable learning rate); ΔL_gen moves "
  "through which basin is reached.",
  "The same scheme with the same variance but a FIXED SEED-INDEPENDENT rank-deficient draw (e.g. all rows equal within a layer): "
  "the scale is matched exactly and the symmetry-breaking is removed.",
  "Orthogonal initialization at the same scale, a data-dependent (LSUV-style) rescaling pass, or a normalizer that enforces the same "
  "forward variance at run time reach the same conditioning by different means.",
  [tv("Glorot, Bengio (2010). Understanding the difficulty of training deep feedforward neural networks, AISTATS 2010", "the fan-in/fan-out variance rule"),
   tv("He, Zhang, Ren, Sun (2015). Delving Deep into Rectifiers, ICCV 2015", "the ReLU-matched variance rule"),
   cv(V_JACOT, "the regime in which the initialization scale decides whether training is kernel-like or feature-learning"),
   cv(V_WANN, "the demonstration that architecture alone carries function even with weights untrained, bounding what init 'explains'")],
  None, "B2.8 residual connection / B2.10 pre-post norm factorials both vary initialization scale; MLX-11 lazy/kernel vs feature-learning regime",
  "Training outcome at a fixed budget is invariant to the initialization scale across depths, which would remove the signal-scale "
  "mechanism and make the scheme cosmetic.",
  "REGISTERED_FOR_EXPERIMENT",
  "Initialization is free at serve time and decides training cost. Record the scheme and the seed; a result that depends on an "
  "unreported init is not reproducible, and seed variance must be reported alongside any claimed difference.",
  "13. Small-feature closure table (initialization enters through the update-geometry rows)")

F("TF-033", "Weight tying (input embedding / unembedding)",
  "Impose W_U = E^T (or more generally theta_1 = theta_2 for two otherwise independent parameter blocks). By TMT-8 the tied family is "
  "a SUBSET of the untied family: F_tied subseteq F_untied, with the inclusion strict in general.",
  "SC", "S because it constrains the state coordinates to serve both the read-in and the read-out role; C because both maps are "
  "compiler interfaces between symbols and coordinates.",
  "Everything the tied family can express, trivially: any tied setting is a legal untied setting.",
  "The untied degrees of freedom: a target requiring the input and output geometries to differ cannot be met exactly under the tie, "
  "and X-TMT8 exhibits the strictness of the inclusion on an enumerated tiny family.",
  "Tying halves the vocabulary parameter count and forces the same similarity geometry on read-in and read-out, which is the right "
  "prior when the obligation is symmetric in that sense and a bias cost when it is not.",
  ["ΔB_mem", "ΔL_gen", "ΔL_sem"],
  "ΔB_mem falls by Vd; ΔL_gen improves in the low-data regime through the reduced description; ΔL_sem can degrade when the symmetry "
  "is wrong.",
  "Untied embeddings with the SAME total parameter count (halve d for both tables): the parameter saving is matched exactly and the "
  "symmetry constraint is removed, separating 'fewer parameters' from 'this particular equality'.",
  "A tied pair plus a learned low-rank correction W_U = E^T + AB recovers the untied freedom at controlled cost; tying with a learned "
  "diagonal rescaling is an intermediate constraint.",
  [tv("Press, Wolf (2017). Using the Output Embedding to Improve Language Models, EACL 2017", "the tying construction and its parameter/quality claim"),
   tv("Inan, Khosravi, Socher (2017). Tying Word Vectors and Word Classifiers: A Loss Framework for Language Modeling, ICLR 2017", "the loss-framework justification for the tie"),
   cv(V_NFL, "the general statement that a constraint helps only where it matches the target, which is TMT-8's consequence")],
  TH("TMT-8", "X-TMT8"),
  "B2.6 / MLX-06 symmetry x parameter sharing",
  "A tied family is shown to express a function outside the untied family with the same parameterization, contradicting TMT-8. "
  "X-TMT8 enumerates a tiny two-layer family and verifies both the inclusion and its strictness.",
  "PROVED_AT_SCOPE",
  "Tying is reported as free parameters saved. Charge the lost degrees of freedom: report the tied and untied arms at matched TOTAL "
  "parameters, not matched d, or the saving and the constraint are conflated.",
  "8. Feature atlas - output and decoding / Unembedding / tied input-output embeddings (C,S)")

F("TF-034", "Dropout and stochastic depth",
  "Dropout zeroes each unit of a hidden activation independently with probability p during training and rescales by 1/(1-p). "
  "Stochastic depth does the same at the SUBLAYER level: with probability p_l the whole residual branch is skipped, so "
  "x_{l+1} = x_l. Both are identity at evaluation.",
  "US", "U because both are development-time stochastic subrealization sampling; S because what is perturbed is the carried state.",
  "The serving computation: with the mechanisms disabled at evaluation, the deployed function is deterministic and unperturbed.",
  "The developmental morphology: during training the effective network is a random subnetwork each step, so 'the model is an L-layer "
  "stack' is not true of the training-time object.",
  "Random subrealization forces the surviving units/branches to be individually sufficient, which spreads the represented function "
  "over redundant paths rather than concentrating it in a few fragile ones.",
  ["ΔL_gen", "ΔL_rob", "ΔB_train"],
  "ΔL_gen and ΔL_rob improve in over-parameterized/low-data regimes and degrade in under-fit ones; ΔB_train rises (more steps); "
  "stochastic depth additionally LOWERS per-step ΔB_train by skipping branches.",
  "Additive Gaussian noise on the same activations with matched variance: the perturbation magnitude is held and the "
  "subnetwork-sampling structure is removed.",
  "Weight decay (TF-061), data augmentation, or an explicit ensemble of narrower models reach related regularization; layer-drop at "
  "inference time (a different mechanism) turns stochastic depth into a serving compiler instead.",
  [tv("Srivastava, Hinton, Krizhevsky, Sutskever, Salakhutdinov (2014). Dropout: A Simple Way to Prevent Neural Networks from Overfitting, JMLR 15", "the unit-dropout mechanism"),
   tv("Huang, Sun, Liu, Sedra, Weinberger (2016). Deep Networks with Stochastic Depth, ECCV 2016", "the sublayer-drop mechanism and its training-cost saving"),
   cv(V_BELKIN, "the over-parameterized regime in which the regularization/interpolation tradeoff is not the classical one")],
  None, "B2.8 residual connection (depth x perturbation factorial) and MLX-12 overparameterization and optimization accessibility",
  "Dropout or stochastic depth improves protected performance in a regime with no overfitting at matched training steps, which would "
  "remove the redundancy mechanism as the explanation.",
  "REGISTERED_FOR_EXPERIMENT",
  "Both are serve-time free and train-time costly; stochastic depth also changes the effective depth seen per step. Charge the extra "
  "steps to ΔB_train and report the EXPECTED depth, not the nominal one.",
  "9. Feature atlas - autoregressive objective and training protocol / dropout / stochastic depth (U,S)")


# ======================================================================================================================
# E. Output map and decoding (calculus section 8)
# argument order reminder: ... parents, formal_theorem, experiment, KILL, STATUS, hidden_cost_rule, section
# ======================================================================================================================

F("TF-035", "Unembedding and output softmax",
  "z_i = W_U N_f(r_i^{(L)}) in R^V, then p(x_{i+1} | x_{<=i}) = softmax(z_i / T_d). The unembedding is the compiler back from the "
  "continuous residual coordinate to the discrete alphabet; the softmax makes the result a normalized categorical distribution.",
  "CD", "C because W_U is the read-out interface to the symbol alphabet; D because the normalized distribution is the object every "
  "decision policy consumes.",
  "The ARGMAX token under any positive T_d, and the full ordering of logits: softmax is strictly monotone.",
  "Calibration: the probability VALUES depend on T_d and on the logit scale, so a claim about p(x) is not preserved under a "
  "temperature change even though the argmax is.",
  "The softmax turns an unnormalized compatibility score into a proper distribution, which is what makes the cross-entropy objective "
  "(TF-054) a proper scoring rule and what makes calibration a separately checkable obligation from accuracy.",
  ["ΔB_serve", "ΔB_mem", "ΔL_cal", "ΔL_sem"],
  "ΔB_serve and ΔB_mem rise as Vd (the dominant per-step cost at small d and large V); ΔL_cal is decided here and nowhere else in the "
  "forward pass.",
  "Replace the softmax by an unnormalized score and take the argmax directly: accuracy is preserved exactly and the distribution (and "
  "therefore calibration, sampling and the cross-entropy signal) is removed.",
  "A hierarchical or sampled softmax computes the same distribution with different cost; a normalizing-flow or energy-based head is "
  "a different realization of the same normalization obligation.",
  [cv(V_VASWANI, "the linear unembedding plus softmax construction"),
   tv("Yang, Dai, Salakhutdinov, Cohen (2018). Breaking the Softmax Bottleneck: A High-Rank RNN Language Model, ICLR 2018", "the rank limitation of a single linear-plus-softmax head, i.e. the non-preserved part"),
   cv(V_ELHAGE, "the logit-lens reading in which the unembedding is applied to intermediate residual states")],
  TH("TMT-11", "X-TMT11"),
  "MLX-27 abstention vs unsafe serving and MLX-32 emergence metric audit (both turn on the distribution, not the argmax)",
  "A calibration claim is shown to be invariant to the decoding temperature, which would collapse the accuracy/calibration distinction "
  "this entry rests on.",
  "PROVED_AT_SCOPE",
  "Vd parameters and a V-way normalization per step are the serving cost. Report them separately from the body, and state T_d with "
  "every probability: an uncalibrated probability quoted without T_d is not a measurement.",
  "8. Feature atlas - output and decoding / Softmax output (D)")

F("TF-036", "Decoding policy (the decision object)",
  "A decoder D maps the model distribution p_theta, a prompt and any search/random state to an emitted sequence. By TMT-15 the pair "
  "(p_theta, D) determines behaviour, and D can be changed with theta untouched, so 'the model improved' and 'the decoder improved' "
  "are different claims about different objects.",
  "D", "D alone: the decoder is the action-selection stage. It reads the predictive state but changes no parameter and no stored "
  "knowledge.",
  "p_theta itself: every decoder in this family consumes the same conditional table and leaves it bit-identical (X-TMT15 verifies the "
  "table's hash is unchanged across eight decoders).",
  "The emitted sequence and every metric computed from it: X-TMT15 exhibits one p_theta and eight decoders producing three distinct "
  "emissions, one of which is the sequence argmax and one of which is not.",
  "The decoder selects a point (or a set) from a distribution the model already defines. All of its effect is in the selection rule; "
  "none of it is in what the model knows.",
  ["ΔL_sem", "ΔL_cal", "ΔB_serve", "ΔB_search"],
  "ΔB_search and ΔB_serve rise with search breadth; ΔL_sem moves without any change to ΔB_train or to the stored parameters, which is "
  "the whole point of the distinction.",
  "The SAME decoder applied to a p_theta obtained by a different training run, and the SAME p_theta decoded by a different decoder: "
  "running both arms is the only way to attribute a measured change to one object.",
  "Any of TF-037..TF-042 instantiates D; a constrained/grammar decoder and a verifier-gated decoder (TF-043, TF-069) are decoders "
  "with an admission rule attached.",
  [cv(V_SNELL, "the explicit treatment of test-time decoding compute as a resource traded against parameters"),
   cv(V_MONKEYS, "the measurement of how coverage moves with sampling budget at fixed theta"),
   tv("Holtzman, Buys, Du, Forbes, Choi (2020). The Curious Case of Neural Text Degeneration, ICLR 2020", "the demonstration that decoding rule alone changes generated-text quality at fixed theta")],
  TH("TMT-15", "X-TMT15"),
  "B2.18 chain-of-thought/test-time working state and B2.19 speculative decoding both hold theta fixed and vary D; MLX-37 planning vs compiled policy",
  "A measured improvement is shown to be attributable to p_theta while the decoder differed between arms, i.e. the two objects are "
  "shown not to be separable. X-TMT15 establishes the separation on an exact finite scope.",
  "PROVED_AT_SCOPE",
  "State the decoder (and its temperature, k, p, beam width and sample count) with EVERY reported number. An evaluation that names "
  "only the model is not attributable, and its compute is not comparable.",
  "8. Feature atlas - output and decoding / Temperature / top-k / top-p (D)")

F("TF-037", "Sampling temperature T_d",
  "Sample x_{t+1} ~ softmax(z_t / T_d). T_d -> 0 is greedy argmax; T_d = 1 is the model's own distribution; T_d > 1 flattens it. By "
  "TMT-4 this is the same entropy-regularized family as attention temperature, applied to the output decision instead of to routing.",
  "D", "D alone. It changes no parameter, no cached state and no stored knowledge; it reweights the decision over an unchanged "
  "distribution.",
  "The support and the ordering of p_theta: no token gains or loses positive probability under any finite T_d > 0.",
  "The sampled distribution, its entropy, and every diversity/quality statistic computed from samples.",
  "T_d trades expected per-sample quality against sample diversity. Low T_d concentrates on the mode (better single-sample accuracy, "
  "worse coverage); high T_d spreads mass (better coverage for best-of-N, worse single samples).",
  ["ΔL_sem", "ΔL_cal", "ΔB_search"],
  "Lower T_d improves single-sample ΔL_sem on unambiguous obligations and degrades the coverage that best-of-N (TF-041) exploits; "
  "ΔB_serve per token is exactly unchanged.",
  "Sample from a FIXED distribution with the same entropy as softmax(z/T_d) but ignoring z: entropy is matched and the "
  "score-dependence removed, separating 'more diversity' from 'diversity in the right places'.",
  "Top-k (TF-038) and top-p (TF-039) reach comparable concentration by truncation rather than by rescaling; a Mirostat-style "
  "controller targets an entropy level directly.",
  [tv("Holtzman, Buys, Du, Forbes, Choi (2020). The Curious Case of Neural Text Degeneration, ICLR 2020", "the systematic comparison of temperature against truncation sampling"),
   cv(V_MONKEYS, "the coverage-versus-budget measurement in which temperature sets the exploration rate"),
   cv(V_IB, "the score-versus-entropy trade of which TMT-4 is the finite instance")],
  TH("TMT-15", "X-TMT15"),
  "B2.18 (test-time working state at controlled total compute) and MLX-27 abstention vs unsafe serving",
  "A single T_d is optimal for both single-sample accuracy and best-of-N coverage on the same obligation, which would collapse the "
  "quality/diversity trade.",
  "REGISTERED_FOR_EXPERIMENT",
  "Temperature is free in FLOPs, so it is the easiest hidden knob in any comparison. Fix it across arms or charge the search to "
  "ΔB_search; report T_d with every generation metric.",
  "8. Feature atlas - output and decoding / Temperature / top-k / top-p (D)")

F("TF-038", "Top-k truncation",
  "Keep only the k highest-probability tokens, set the rest to zero, renormalize, then sample: "
  "p'(x) proportional to p(x) 1[x in TopK_k(p)]. k = 1 is exactly greedy decoding.",
  "D", "D alone: a hard admission rule over the decision alphabet at each step.",
  "The relative probabilities WITHIN the retained set: truncation renormalizes without reordering.",
  "The tail: every token outside the top k gets probability exactly zero, so any continuation requiring one is unreachable at that "
  "step - a hard, not soft, restriction.",
  "Truncation removes the low-probability tail that accumulates over many steps into a high chance of at least one bad token, at the "
  "cost of making a fixed number of options available regardless of how peaked or flat the step actually is.",
  ["ΔL_sem", "ΔL_rob", "ΔL_cal"],
  "ΔL_rob improves (no tail accidents); ΔL_cal degrades (the emitted distribution is no longer p_theta); ΔL_sem improves on peaked "
  "steps and degrades on genuinely flat ones where k is too small.",
  "Keep a RANDOM k-subset of the vocabulary (excluding the argmax to avoid triviality) and renormalize: the support size is matched "
  "exactly and the ranking is removed.",
  "Top-p (TF-039) adapts the retained set size to the step's entropy; epsilon-sampling (drop below an absolute probability floor) is "
  "a third truncation rule; k = 1 coincides with greedy.",
  [tv("Fan, Lewis, Dauphin (2018). Hierarchical Neural Story Generation, ACL 2018", "top-k sampling as introduced"),
   tv("Holtzman, Buys, Du, Forbes, Choi (2020). The Curious Case of Neural Text Degeneration, ICLR 2020", "the argument that a FIXED k mismatches steps of differing entropy"),
   cv(V_SNELL, "the treatment of decoding-time choices as a compute/quality allocation")],
  TH("TMT-15", "X-TMT15"),
  "B2.18 test-time working state; MLX-27 abstention vs unsafe serving (truncation is a crude admission rule)",
  "A fixed k is optimal across steps whose entropy is deliberately varied, which would remove the entropy-mismatch objection and make "
  "top-p's adaptivity pointless.",
  "REGISTERED_FOR_EXPERIMENT",
  "Truncation silently changes the served distribution. Any perplexity or calibration number must be computed under the UNTRUNCATED "
  "p_theta, or reported explicitly as a property of the truncated decoder (TMT-15).",
  "8. Feature atlas - output and decoding / Temperature / top-k / top-p (D)")

F("TF-039", "Top-p (nucleus) truncation",
  "Keep the smallest set S of highest-probability tokens with sum_{x in S} p(x) >= p, renormalize over S, then sample. The retained "
  "set size |S| ADAPTS to the step: it is 1 at a fully peaked step and large at a flat one.",
  "D", "D alone, like top-k, but with a mass-based rather than a count-based admission rule.",
  "The relative probabilities within the nucleus and the argmax (always retained).",
  "The tail outside the nucleus, and the entropy of the emitted distribution, which is capped by construction.",
  "Conditioning the retained set on the step's own probability mass matches the admission rule to the model's own confidence, so "
  "confident steps are effectively greedy and uncertain steps stay diverse without a global k.",
  ["ΔL_sem", "ΔL_rob", "ΔL_cal"],
  "Same directions as top-k, with the difference concentrated on steps whose entropy differs from the corpus average; ΔL_cal is "
  "degraded in the same way and for the same reason.",
  "Truncate to a set of the SAME SIZE |S| as top-p would choose at each step, but pick it at random among non-argmax tokens: the "
  "adaptive set size is matched step by step and the ranking is removed.",
  "Top-k (TF-038) with k tuned per domain approximates it when step entropy is homogeneous; a typical-sampling rule truncates by "
  "information content rather than by mass.",
  [tv("Holtzman, Buys, Du, Forbes, Choi (2020). The Curious Case of Neural Text Degeneration, ICLR 2020", "nucleus sampling and the adaptivity argument"),
   tv("Meister, Pimentel, Wiher, Cotterell (2023). Locally Typical Sampling, TACL 11", "the information-content alternative to mass-based truncation"),
   cv(V_MONKEYS, "the coverage measurement that truncation directly limits")],
  TH("TMT-15", "X-TMT15"),
  "B2.18 test-time working state; MLX-27 abstention vs unsafe serving",
  "Top-p shows no advantage over a well-tuned top-k on a corpus with deliberately heterogeneous step entropy, which would remove the "
  "adaptivity mechanism.",
  "REGISTERED_FOR_EXPERIMENT",
  "As for top-k: report p and state that likelihood-based metrics are computed under the untruncated distribution. Comparing a "
  "top-p arm's text quality against a greedy arm's perplexity compares two different objects.",
  "8. Feature atlas - output and decoding / Temperature / top-k / top-p (D)")

F("TF-040", "Beam search",
  "Maintain B partial sequences; at each step expand every beam by every token, score by the accumulated log p_theta (optionally "
  "length-normalized), and keep the best B. It is a bounded-width search for the sequence argmax, which greedy decoding does NOT "
  "find in general.",
  "DP", "D because it is a decision/search policy over sequences; P because the B-fold widening is a real serving-compute and "
  "serving-memory multiplier (B copies of the KV cache).",
  "p_theta: beam search reads the same conditional table as greedy and changes nothing in it.",
  "The emitted sequence: X-TMT15 exhibits an exact p_theta where greedy emits (0,0,0) with probability 11/80 while beam B=2 and B=4 "
  "emit the true argmax (1,0,0) with probability 729/2000 - a factor 2.65 in sequence likelihood from the decoder alone.",
  "Greedy commits at each step to the locally best token and cannot recover from a high-probability prefix that leads only to "
  "low-probability continuations; beam defers the commitment across B alternatives, so it finds higher-likelihood sequences.",
  ["ΔL_sem", "ΔB_serve", "ΔB_mem", "ΔB_search"],
  "ΔB_serve, ΔB_mem and ΔB_search all rise linearly in B (including B copies of the KV cache); ΔL_sem improves on obligations where "
  "sequence likelihood is the right target and can DEGRADE on open-ended generation where the mode is degenerate.",
  "Sample B independent continuations at T_d = 1 and keep the one with highest log p_theta: identical compute, identical selection "
  "criterion, and the shared-prefix pruning structure of beam removed.",
  "Best-of-N sampling with likelihood reranking (TF-041) approximates the same objective stochastically; A*-style or MCTS decoding "
  "(TF-042) allocates the same search budget non-uniformly.",
  [cv(V_SNELL, "test-time search budget as a resource traded against parameters"),
   tv("Holtzman, Buys, Du, Forbes, Choi (2020). The Curious Case of Neural Text Degeneration, ICLR 2020", "the finding that maximizing sequence likelihood degrades open-ended generation, i.e. that the beam objective is not always the right one"),
   cv(V_HTPS, "search over sequences under a learned model as a general decoding mechanism")],
  TH("TMT-15", "X-TMT15"),
  "B2.19 speculative decoding shares the serving-economics frame; MLX-37 planning vs compiled policy",
  "Greedy is shown to find the sequence argmax for the model class in question, which would make beam search pure overhead. X-TMT15 "
  "exhibits a counterexample in exact arithmetic at its scope.",
  "PROVED_AT_SCOPE",
  "Beam multiplies serving compute AND cache memory by B. Report B with every quality number and charge B-fold ΔB_serve; a beam-B "
  "result compared against a greedy baseline at 'the same model' is a B-fold compute comparison.",
  "8. Feature atlas - output and decoding / Beam search (D,P)")

F("TF-041", "Self-consistency / best-of-N",
  "Draw N independent samples from p_theta under a stochastic decoder and return either the plurality answer (self-consistency) or "
  "the sample maximizing an external score (best-of-N with a reward model or verifier). Compute scales as N; the returned object is a "
  "SELECTED sample, not a new distribution.",
  "DVP", "D because it is a decision rule over samples; V because the aggregation or scoring step is an admission/selection authority; "
  "P because N proposals are N full generations.",
  "p_theta and every parameter: nothing is trained, and the base distribution is untouched.",
  "The relationship between reported accuracy and per-sample accuracy: an N-sample result is not comparable to a 1-sample result at "
  "any level, and improvement can come entirely from the selector rather than from the model.",
  "Independent samples explore different reasoning paths; when correctness is checkable (by majority agreement or by a verifier) the "
  "selection converts coverage into accuracy. The gain is bounded by coverage (does any sample contain the answer) and by selector "
  "precision.",
  ["ΔL_sem", "ΔB_serve", "ΔB_search", "ΔB_verify"],
  "ΔB_serve and ΔB_search rise as N; ΔB_verify rises with the scorer's cost; ΔL_sem improves while coverage grows and saturates at "
  "the selector's precision ceiling.",
  "Return a RANDOM sample of the N rather than the selected one: the N-fold generation cost is paid in full and the selection "
  "mechanism is removed, which isolates 'more samples' from 'choosing among samples'.",
  "Beam search (TF-040) selects by model likelihood instead of by an external score; rejection sampling into training data (TF-069) "
  "is the same selector used as a development signal instead of at serve time.",
  [cv(V_MONKEYS, "the coverage-versus-N measurement and the gap between coverage and selected accuracy"),
   cv(V_SNELL, "the compute-optimal allocation between sampling and model size"),
   cv(V_SETLUR, "the result that scaling test-time sampling without verification is suboptimal, i.e. the selector is load-bearing"),
   tv("Wang, Wei, Schuurmans, Le, Chi, Narang, Chowdhery, Zhou (2023). Self-Consistency Improves Chain of Thought Reasoning in Language Models, ICLR 2023", "the plurality-vote aggregation rule")],
  TH("TMT-15", "X-TMT15"),
  "B2.18 chain-of-thought/test-time working state (controlled total inference compute) and MLX-26 verifier-gated speculative compiler",
  "Best-of-N improves protected performance with a selector no better than random at matched compute, which would show the gain is "
  "not selection but something else.",
  "REGISTERED_FOR_EXPERIMENT",
  "Charge ALL N proposals plus the judge/verifier to ΔB_serve and ΔB_verify. A best-of-N number compared against a single-sample "
  "baseline without the N-fold charge is the most common unpriced comparison in this whole atlas.",
  "8. Feature atlas - output and decoding / Self-consistency / best-of-N (D,V,P)")

F("TF-042", "Test-time search",
  "Any serving-time procedure that expands and evaluates more than one continuation under an explicit search policy: tree search over "
  "steps, MCTS with a learned value, iterative refine-and-rescore, or a proof-search loop against a checker. Formally it replaces the "
  "decoder D by a search operator with a node budget and an evaluation function.",
  "DVP", "D because it selects the emitted action; V because the evaluation/verification function admits or rejects nodes; P because "
  "the node budget is serving compute.",
  "p_theta and the parameters: search consumes the model as a proposal distribution and a value estimate without changing either.",
  "The compute-performance relation: a searched result cannot be compared to an unsearched one without the node budget, and the "
  "reachable quality is bounded by the evaluator's accuracy.",
  "Search converts serving compute into solution quality at a rate set by (a) the proposal distribution's coverage and (b) the "
  "evaluator's ability to rank. Where an EXACT checker exists (proofs, code tests) the second factor is free and the trade is "
  "unusually favourable.",
  ["ΔL_sem", "ΔB_search", "ΔB_serve", "ΔB_verify"],
  "ΔB_search and ΔB_verify rise with the node budget; ΔL_sem improves steeply where an exact checker is available and saturates "
  "quickly where the evaluator is a noisy proxy.",
  "Expand the SAME node budget with a random (unguided) policy and no evaluator ranking: the compute is matched exactly and the "
  "guidance and admission mechanisms are removed.",
  "Best-of-N (TF-041) is depth-1 search with a flat policy; beam (TF-040) is search scored by likelihood alone; a verifier-gated "
  "draft-accept loop (TF-043) is search with an exactness-preserving acceptance rule.",
  [cv(V_SNELL, "the measured compute-optimal allocation of test-time search against parameters"),
   cv(V_SETLUR, "the necessity of verification for test-time scaling to pay"),
   cv(V_HTPS, "hypertree proof search against an exact checker"),
   cv(V_PROVER, "proof-assistant feedback used as the evaluator inside the search loop")],
  None, "B2.18 chain-of-thought/test-time working state; MLX-26 verifier-gated speculative compiler; MLX-37 planning vs compiled policy",
  "Test-time search improves protected performance at matched total compute on a task where NO checker or reliable evaluator exists, "
  "which would contradict the evaluator-bounded reading.",
  "REGISTERED_FOR_EXPERIMENT",
  "Report the node budget, the evaluator and its cost. 'The model solved it' with an unstated search budget is not a model claim at "
  "all (TMT-15); the verifier's own error rate must be charged to ΔB_verify and to the reported reliability.",
  "8. Feature atlas - output and decoding / Self-consistency / best-of-N (D,V,P)")

F("TF-043", "Speculative decoding",
  "A cheap draft model q proposes gamma tokens; the target model p scores them in ONE parallel forward pass; each is accepted with "
  "probability min(1, p(x)/q(x)) and the first rejection is replaced by a sample from the residual (p - q)_+ renormalized. The "
  "accepted output is distributed EXACTLY as p, independently of q.",
  "DVHP", "D because it emits tokens; V because the acceptance test is an admission rule; H because the draft's and target's caches "
  "are both maintained; P because the entire benefit is wall-clock serving economics.",
  "The output distribution: exactly p_theta, for any draft q. This is the property that makes the mechanism a pure P-level change "
  "rather than a model change.",
  "Latency, the number of target forward passes, and the memory footprint (two models plus two caches): none is preserved.",
  "The target's forward pass is memory-bandwidth-bound, so scoring gamma tokens costs nearly the same as scoring one. A draft that "
  "agrees often converts that slack into accepted tokens; the expected speedup is set by the acceptance rate and the draft/target "
  "cost ratio.",
  ["ΔB_serve", "ΔB_mem", "ΔB_verify"],
  "ΔB_serve (latency) falls with the acceptance rate; ΔB_mem rises (draft model plus its cache); ΔL_sem, ΔL_cal and ΔL_gen are "
  "EXACTLY zero by the acceptance rule.",
  "Accept the draft's tokens WITHOUT the probability test (pure draft-and-trust): the same proposals and the same compute, and the "
  "exactness-preserving admission rule removed. The output distribution then depends on q, which is the mechanism under test.",
  "Medusa-style multi-head self-drafting, n-gram/lookup drafting, or early-exit drafting supply proposals from the same model; "
  "batching more requests (TF-082) fills the same bandwidth slack without a draft.",
  [cv(V_SPEC, "the speculative sampling construction and the exact-distribution acceptance proof"),
   tv("Chen, Borgeaud, Irving, Lespiau, Sifre, Jumper (2023). Accelerating Large Language Model Decoding with Speculative Sampling, arXiv:2302.01318", "the concurrent formulation and its acceptance-rate analysis"),
   cv(V_PIC, "the general inline-cache pattern of a cheap speculative path validated against an authoritative one")],
  TH("TMT-7", "X-TMT7"),
  "B2.19 speculative decoding (vary draft quality, target cost, acceptance rate and latency)",
  "A speculative-decoding arm shows a quality change relative to exact decoding of the same target, which would mean the acceptance "
  "rule was not implemented exactly and the mechanism is no longer distribution-preserving.",
  "PARENT_THEOREM_UNDER_ASSUMPTIONS",
  "Charge the draft model's parameters and cache to ΔB_mem and its forward passes to ΔB_serve. A speedup quoted without the draft's "
  "memory cost hides a real serving-capacity loss; and a QUALITY claim for speculative decoding is a bug report, not a result.",
  "8. Feature atlas - output and decoding / Speculative decoding (D,V,H,P)")


# ======================================================================================================================
# F. Memory, history, retrieval, tools (calculus section 11)
# argument order reminder: ... parents, formal_theorem, experiment, KILL, STATUS, hidden_cost_rule, section
# ======================================================================================================================

F("TF-044", "Context window W",
  "The maximum number of past tokens a forward pass may attend to. A model whose decision at step i is a function of suffix_W(x_{<=i}) "
  "and nothing else is a W-window machine. By TMT-2, if suffix_W(h) = suffix_W(h') while q_O(h) != q_O(h'), no such machine is exact "
  "on both histories.",
  "HP", "H because W is exactly how much history is carried; P because attention cost grows as Theta(W^2) (or Theta(nW) with a window "
  "mask) and cache memory as Theta(W).",
  "Every distinction realized INSIDE the window: within W, order and content are fully available.",
  "Any distinction whose witness lies further back than W. X-TMT2 enumerates this: for the first-token obligation at W in {1,2,3} "
  "EVERY W-suffix class collides, and the minimal error of ANY suffix-only rule is exactly 1/2.",
  "W is the amount of history the model can condition on directly. Extending it, compressing the past into recurrent state (TF-045) "
  "and retrieving it from a store (TF-046) are SUBSTITUTABLE ways of supplying the same missing distinctions at different burdens.",
  ["ΔL_sem", "ΔB_serve", "ΔB_mem", "ΔB_train"],
  "ΔL_sem improves only while required distinctions lie outside the current W; ΔB_serve rises quadratically (dense) or linearly "
  "(windowed) and ΔB_mem linearly in W through the cache.",
  "Hold W but SHUFFLE the tokens beyond a distance W' < W so their content is destroyed while the sequence length, the cost and the "
  "cache size are identical: this separates 'has a long window' from 'uses the long window'.",
  "A recurrent/state-space summary (TF-045), a retrieval store (TF-046), or an explicit scratchpad carried forward (TF-051) supply "
  "the same distinctions; TMT-2 says nothing about which is cheaper.",
  [cv(V_JELASSI, "the measured separation between window-limited and state-compressed models on copying, i.e. which distinctions each can carry"),
   cv(V_MEMTRANS, "kNN-augmented attention as a way to exceed the window without extending it"),
   cv(V_ZHOU_LEN, "length generalization as a property of the task and the position mechanism, not of W alone"),
   cv(V_SHALIZI, "the causal-state formulation of exactly which history distinctions must be carried")],
  TH("TMT-2", "X-TMT2"),
  "B2.11 context vs recurrence vs retrieval (histories with exact required memory depth; burden at fixed semantic adequacy)",
  "A stateless W-window realization is exhibited that is exact on a history pair with identical W-suffixes and distinct protected "
  "outputs. X-TMT2 enumerates the collisions that make this impossible at its scope.",
  "PROVED_AT_SCOPE",
  "Advertised context length is not delivered capability. Meter (a) the cache bytes 2 L W d H_kv the window actually costs, and "
  "(b) measured performance as a function of where in the window the required evidence sits - not the maximum W alone.",
  "11. Feature atlas - memory, retrieval and tools / recurrent/state-space memory (H,S,T)")

F("TF-045", "Recurrence / state-space memory",
  "A fixed-size carried state updated causally: h_t = A h_{t-1} + B x_t, y_t = C h_t (+ D x_t), with A, B, C possibly input-dependent "
  "(selective SSM) or diagonal/structured for fast parallel scan. Serving cost is Theta(1) per token and state memory is Theta(dim h) "
  "INDEPENDENT of sequence length.",
  "HST", "H because h_t is the compressed history; S because it is a carried coordinate; T because the update is a local transform "
  "applied recurrently.",
  "Causality and constant per-token serving cost: the update reads only the past and never rescans it.",
  "Exact recall of the far past: a finite-dimensional h_t is a lossy summary, so a distinction requiring more than dim(h) bits of "
  "history is not preserved - which is precisely the measured copying gap.",
  "Recurrence substitutes a COMPRESSION of the past for a re-read of it. It is on the frontier when the required history statistic is "
  "low-dimensional and off it when exact token-level recall is required.",
  ["ΔB_serve", "ΔB_mem", "ΔL_sem", "ΔB_train"],
  "ΔB_serve falls from Theta(n) to Theta(1) per token and ΔB_mem from Theta(n) to Theta(1); ΔL_sem degrades exactly on obligations "
  "needing more history than dim(h) can carry.",
  "The same recurrence with A = 0 (state reset every step): identical arithmetic, identical cost, and the history-carrying mechanism "
  "removed - a pure per-token transform. This isolates 'recurrent cost profile' from 'recurrent memory'.",
  "A sliding window of width W (TF-019) carries the last W tokens exactly instead of a lossy summary of all of them; linear attention "
  "with a matrix-valued state is the same recurrence written as an attention; chunked/hybrid stacks interleave both.",
  [cv(V_S4, "structured state-space sequence modelling and the parallel-scan realization"),
   cv(V_MAMBA, "input-dependent (selective) state transitions"),
   cv(V_SSD, "the duality that makes SSMs and a class of attentions the same computation"),
   cv(V_ILLUSION, "the exact expressivity ceiling of the fixed-state formulation and the measured copying gap the lossy-summary reading predicts")],
  TH("TMT-2", "X-TMT2"),
  "B2.11 context vs recurrence vs retrieval (compressed-recurrent-state arm)",
  "A fixed-dimension recurrent state is shown exact on an obligation family whose required history distinctions exceed its capacity, "
  "contradicting the pigeonhole argument behind TMT-2.",
  "REGISTERED_FOR_EXPERIMENT",
  "Constant per-token cost is real; constant CAPACITY is the price. Report dim(h) and the measured recall-vs-distance curve alongside "
  "the throughput number, or a linear-time claim conceals a capacity claim.",
  "11. Feature atlas - memory, retrieval and tools / recurrent/state-space memory (H,S,T)")

F("TF-046", "Retrieval / RAG",
  "At serve time, a retriever selects k passages from an external corpus by a query-dependent score and they are placed in the "
  "context (or cross-attended, TF-020) before generation. The corpus is MUTABLE and external; the parameters are not consulted for "
  "its content.",
  "HRC", "H because the corpus is persistent external state; R because retrieval is a routing decision over that state; C because "
  "whether a retrieved passage is authoritative, advisory or merely suggestive is an interface declaration.",
  "The parametric model: theta is untouched, so anything the model knew before is still known, and the corpus can be edited without "
  "retraining.",
  "Attribution: a correct answer does not establish that the retrieved passage caused it, and a retrieved-but-wrong passage can "
  "override correct parametric knowledge. Faithfulness to the source is a separate obligation.",
  "Retrieval moves volatile, long-tail or provenance-bearing facts OUT of the weights into a store whose update cost is a write "
  "instead of a gradient step. Its advantage grows with fact volatility, tail size and provenance requirements.",
  ["ΔB_update", "ΔB_serve", "ΔB_comm", "ΔL_sem", "ΔL_rob", "ΔB_verify"],
  "ΔB_update falls dramatically for volatile facts (a write, not a retrain); ΔB_serve and ΔB_comm rise (retrieval latency plus k "
  "passages of context); ΔL_rob degrades under retrieval noise.",
  "Retrieve k passages by a query-INDEPENDENT rule (random or most-frequent) and place them identically: context length, latency and "
  "token cost are matched exactly and the relevance mechanism is removed.",
  "Fine-tuning the facts into the weights is the parametric alternative with a different update cost; a kNN-LM interpolation "
  "(TF-049) mixes at the distribution level rather than at the context level; long context (TF-044) with the corpus pasted in is the "
  "degenerate retriever.",
  [cv(V_RAG, "the retrieval-augmented generation construction"),
   cv(V_KNNLM, "distribution-level interpolation with a datastore as the alternative realization"),
   cv(V_RETRO, "chunked cross-attention retrieval at pretraining scale"),
   cv(V_SELFRAG, "self-critique over retrieved evidence, i.e. retrieval with an explicit admission step")],
  None, "B2.17 RAG/tool authority (vary fact volatility, source authority, retrieval noise, provenance requirement, tool latency) and MLX-22 RAG/provenance/freshness decomposition",
  "Retrieval fails to beat parametric-only adaptation on a task family with deliberately high fact volatility and a strict provenance "
  "obligation, at matched total burden - which would remove the volatility/provenance mechanism.",
  "REGISTERED_FOR_EXPERIMENT",
  "Charge the retriever's index memory to ΔB_mem, its latency to ΔB_comm, the k retrieved passages to ΔB_serve (they are tokens), and "
  "any provenance/verification step to ΔB_verify. A RAG win reported as 'same model, better answers' hides all four.",
  "11. Feature atlas - memory, retrieval and tools / retrieval / RAG (H,R,C)")

F("TF-047", "KV cache",
  "Store (K_t, V_t) = f_theta(x_{<=t}) once and reuse them for every later decoding step instead of recomputing the prefix. By TMT-6, "
  "for fixed theta and an immutable prefix the cached values EQUAL the recomputed ones, so every downstream deterministic output is "
  "unchanged; only the operation count differs.",
  "HP", "H because the cache is derived serving state with no authority of its own; P because the whole effect is a "
  "compute-for-memory trade.",
  "Every output, exactly. X-TMT6 runs a 6-step continuation in exact rational arithmetic: outputs are identical while projection "
  "multiplications fall from 2(t+1)d^2 per step to 2d^2 per step.",
  "Memory: the cache holds 2 L n d H_kv elements (TMT-13/X-TMT13) and that is a hard serving-capacity constraint; and the cache is "
  "invalidated by any change to theta or to the prefix.",
  "The cache is an A2-style authority/serving separation: parameters plus legal prefix are authoritative, cached K/V are a disposable "
  "materialization. Its benefit rises with prefix reuse and continuation length; its cost rises with cached length, layers and H_kv.",
  ["ΔB_serve", "ΔB_mem"],
  "ΔB_serve falls by a factor that grows with continuation length; ΔB_mem rises linearly in cached length; ΔL_sem, ΔL_gen, ΔL_rob and "
  "ΔL_cal are EXACTLY zero.",
  "Recompute the full prefix at every step (no cache) with identical arithmetic. X-TMT6 runs exactly this arm and finds identical "
  "outputs with a 7:2 multiplication ratio at n = 6; RV-377-055 measures the crossover as a function of prefix reuse.",
  "Recomputation under activation checkpointing (TF-076) is the memory-frugal extreme; paged or compressed caches (TF-048) are the "
  "same materialization at lower byte cost; a recurrent state (TF-045) replaces the cache with a lossy summary.",
  [cv(V_MICHIE, "memoization as the general mechanism: a pure function's value stored instead of recomputed"),
   cv(V_FUTAMURA, "the staging/partial-evaluation frame in which prefix computation is specialized once and reused"),
   cv(V_SNOOPY, "the competitive-caching frame for when materialization pays"),
   cv(V_VASWANI, "the decoder whose prefix computation is being cached")],
  TH("TMT-6", "X-TMT6"),
  "B2.12 KV cache (vary prefix reuse and continuation length; confirm exact equality and the predicted compute-memory crossover) - EXECUTED as RV-377-055",
  "A cached and an uncached run of the same deterministic decoder produce different outputs, which would mean the implementation is "
  "not referentially transparent (a bug, not a mechanism). X-TMT6 and RV-377-055 check exactly this equality.",
  "PROVED_AT_SCOPE",
  "The cache is free compute and expensive memory. Report the cache bytes alongside every throughput number: a serving system's real "
  "capacity is set by 2 L n d H_kv per concurrent sequence, not by the model's parameter count.",
  "11. Feature atlas - memory, retrieval and tools / KV cache (H,P)")

F("TF-048", "KV cache compression / quantization",
  "A serving compiler on the cache: store Q(K_t), Q(V_t) at reduced precision (int8/int4 per-channel or per-token scaling), or evict "
  "or merge entries by a heuristic importance score, or project them to a lower-rank latent. Unlike TF-047 this is NOT exact: it "
  "introduces a distortion eps_C in exchange for a byte reduction.",
  "PH", "P because it is a precision/IO realization choice; H because the object compiled is the persistent serving state.",
  "The uncompressed authoritative state: theta and the legal prefix are untouched and the exact cache can always be recomputed.",
  "Output equality: by TMT-12, if the quantizer merges two cache states whose downstream protected behaviour differs, exactness on "
  "both is impossible. X-TMT12 exhibits such a merge (drop-low-bit on a parity obligation) and a side channel that avoids it.",
  "Cache bytes, not FLOPs, bound concurrent serving capacity. Compression buys concurrency at a distortion whose admissibility is set "
  "by the obligation - which is why eviction hurts exactly the obligations that need the evicted tokens.",
  ["ΔB_mem", "ΔB_comm", "ΔB_serve", "ΔL_sem", "ΔL_rob"],
  "ΔB_mem and ΔB_comm fall by the compression ratio; ΔL_sem and ΔL_rob degrade on obligations whose required distinctions the "
  "quantizer or the eviction policy merges away.",
  "Evict or quantize the SAME number of cache entries chosen at RANDOM rather than by the importance score: the byte saving is "
  "identical and the selection mechanism is removed.",
  "Grouped/shared KV heads (TF-018) cut the same bytes by reducing H_kv rather than the per-entry precision; a recurrent summary "
  "(TF-045) replaces the cache entirely; paged allocation reduces fragmentation without any distortion.",
  [tv("Zhang, Sheng, Zhou, Chen, Zheng, Cai, Song, Tian, Re, Barrett, Wang, Chen (2023). H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models, NeurIPS 2023", "score-based cache eviction"),
   tv("Liu, Yuan, Jin, Zhong, Xu, Braverman, Chen, Hu (2024). KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache, ICML 2024", "low-bit cache quantization with per-channel/per-token scaling"),
   tv("Kwon, Li, Zhuang, Sheng, Zheng, Yu, Gonzalez, Zhang, Stoica (2023). Efficient Memory Management for Large Language Model Serving with PagedAttention, SOSP 2023", "paged cache allocation as the lossless alternative")],
  TH("TMT-12", "X-TMT12"),
  "B2.14 quantization / distillation (vary allowed semantic distortion and hardware price) and B2.5 (cache capacity axis)",
  "A compression scheme is shown exact on an obligation whose required distinctions it provably merges, contradicting TMT-12. "
  "X-TMT12 enumerates the collision structure.",
  "PARENT_THEOREM_UNDER_ASSUMPTIONS",
  "Report the distortion, not only the ratio. Charge ΔL_sem on obligations that depend on evicted or merged entries, and evaluate on "
  "long-context tasks: a cache compressor tested only on short prompts has not been tested.",
  "12. Feature atlas - serving and systems / KV quantization / compression (P,H)")

F("TF-049", "External database / knowledge graph",
  "A structured, addressable, versioned store outside the model: rows with keys, typed relations, timestamps and provenance. The "
  "model reads it by an explicit query and (in write-enabled systems) writes to it by an explicit transaction. Identity and lineage "
  "are properties OF THE STORE, not of any activation.",
  "HCV", "H because it is durable external state; C because the schema is an interface declaration; V because the store can be the "
  "authority against which a generated claim is admitted or rejected.",
  "Exact identity, provenance and recency of the stored facts, and the ability to delete or amend one of them without touching "
  "anything else - none of which a parametric store provides.",
  "Coverage and query adequacy: a fact absent from the schema is unrepresentable, and a required inference the query language cannot "
  "express is not recoverable by reading harder.",
  "A structured store preserves the distinctions (identity, version, source, time) that gradient-compressed weights alias together, "
  "and makes a single-fact update a bounded transaction rather than an unbounded change to a distributed representation.",
  ["ΔB_update", "ΔB_verify", "ΔB_comm", "ΔB_mem", "ΔL_sem"],
  "ΔB_update falls by orders of magnitude for a single fact; ΔB_verify falls when the store is authoritative; ΔB_comm rises with "
  "every query; ΔB_mem is moved out of parameters and into the store.",
  "The same store queried with the provenance and timestamp columns STRIPPED: identical query cost and identical content, and the "
  "identity/lineage mechanism removed - which is the only thing that distinguishes it from a flat corpus.",
  "A versioned document corpus with a dense retriever (TF-046) supplies the same content without the relational structure; "
  "parametric editing (TF-070) attempts the same update inside the weights at a very different collateral cost.",
  [cv(V_PERSIST, "persistent/versioned data structures as the mechanism that makes past states addressable"),
   cv(V_BUILD, "explicit dependency tracking and rebuild semantics, the analogue of an invalidated fact"),
   cv(V_LARIMAR, "an explicit episodic memory attached to an LLM"),
   cv(V_GRACE, "discrete key-value adaptors as a store bolted onto a frozen model")],
  None, "B2.17 RAG/tool authority (source authority and provenance-requirement axes) and MLX-22 RAG/provenance/freshness decomposition; MLX-25 model editing / unlearning locality",
  "A parametric model is shown to support exact single-fact deletion with a bounded, verifiable collateral cone, which would remove "
  "the store's distinguishing advantage.",
  "REGISTERED_FOR_EXPERIMENT",
  "Charge the store's size to ΔB_mem, every query to ΔB_comm, and the schema/ingestion pipeline to ΔB_train. A system that reads a "
  "curated store is not comparable to one that does not, however similar the model inside it.",
  "11. Feature atlas - memory, retrieval and tools / external database / knowledge graph (H,C,V)")

F("TF-050", "Tool calls / external APIs",
  "The model emits a structured call (name, arguments); an external realization executes it; the result is inserted into the context "
  "and generation resumes. The sub-obligation is DELEGATED: its correctness, latency and failure mode belong to the tool, not to "
  "theta.",
  "RVP", "R because choosing which tool to call with which arguments is a routing decision over external realizations; V because the "
  "tool's result carries an authority level; P because latency and failure rate are physical properties of the call.",
  "The delegated computation's exactness where the tool is exact: a calculator's arithmetic or an interpreter's execution is correct "
  "regardless of the model's own numerical competence.",
  "End-to-end reliability: the composite system's failure rate is bounded below by the tool's, and a tool result that is wrong, stale "
  "or adversarial propagates into the output with the model's own fluency.",
  "Delegation replaces a learned approximation of a sub-obligation with an exact (or differently-erring) external realization. It pays "
  "when the sub-obligation is expensive to learn, cheap to call, and checkable.",
  ["ΔL_sem", "ΔB_serve", "ΔB_comm", "ΔB_verify", "ΔB_train"],
  "ΔL_sem improves on exactly-delegable sub-obligations; ΔB_comm and ΔB_serve rise with call latency; ΔB_verify rises unless the tool "
  "is authoritative; ΔB_train falls (the capability need not be learned).",
  "Give the model the tool's OUTPUT FORMAT and cost but a stub that returns a plausible-looking wrong answer: the call structure, the "
  "latency and the token cost are matched and the external correctness is removed.",
  "A fine-tuned subnetwork that computes the same sub-obligation internally, or a retrieval store of precomputed results (TF-049), "
  "delegates to a different realization with a different authority and failure profile.",
  [tv("Schick, Dwivedi-Yu, Dessi, Raileanu, Lomeli, Zettlemoyer, Cancedda, Scialom (2023). Toolformer: Language Models Can Teach Themselves to Use Tools, NeurIPS 2023", "self-supervised tool-call insertion"),
   cv(V_PROVER, "an exact external checker in the loop as the authoritative-tool limit"),
   cv(V_SELFRAG, "explicit critique of externally supplied evidence"),
   cv(V_TVM, "the general pattern of delegating a computation to a specialized external realization")],
  None, "B2.17 RAG/tool authority (tool latency, source authority and retrieval-noise axes); MLX-26 verifier-gated speculative compiler",
  "A delegated sub-obligation with an EXACT tool shows no reliability gain over the parametric path at matched compute, which would "
  "remove the delegation mechanism.",
  "REGISTERED_FOR_EXPERIMENT",
  "Charge tool latency to ΔB_comm, tool compute to ΔB_serve, and the tool's own error rate to the system's reported reliability. "
  "Benchmark scores obtained with tools are not comparable to scores obtained without them.",
  "11. Feature atlas - memory, retrieval and tools / tool calls / APIs (R,V,P)")

F("TF-051", "Scratchpad / chain-of-thought working state",
  "The model emits intermediate tokens before its answer, and those tokens re-enter the context as input to subsequent steps. The "
  "scratchpad is additional TEST-TIME working state: it extends the computation available per answer from O(1) forward passes to "
  "O(length) of them, with the intermediate state written in the output alphabet.",
  "HD", "H because the emitted trace is working memory carried forward through the context; D because it is produced by the decoding "
  "policy and is itself a sequence of decisions.",
  "theta: no parameter changes. And the legality structure: each scratchpad token is still produced from the legal prefix only.",
  "Faithfulness: the emitted trace need not be the computation the model actually performed, so a plausible trace is not an "
  "explanation. Utility and faithfulness must be measured separately.",
  "Serial depth. A fixed-depth forward pass has bounded serial computation (TMT-3's parallelism ceiling in the cited parent); writing "
  "intermediate results into the context and reading them back converts serial steps into sequence length, which is why the gain "
  "concentrates on multi-step compositional obligations.",
  ["ΔL_sem", "ΔB_serve", "ΔB_search", "ΔL_cal"],
  "ΔL_sem improves on multi-step obligations; ΔB_serve rises linearly in trace length (every scratchpad token is a decoded token); "
  "ΔL_cal can degrade because a confident-sounding trace does not track correctness.",
  "Emit the SAME NUMBER of tokens of content-free filler before the answer: total inference compute and context length are matched "
  "exactly and the intermediate-computation content is removed. This is the decisive control for the serial-depth claim.",
  "An explicit external scratch buffer (a tool-backed workspace, TF-050), a recurrent latent-state loop that does not surface tokens, "
  "or adaptive-computation-time layers add serial depth without emitting it.",
  [tv("Nye, Andreassen, Gur-Ari, Michalewski, Austin, Bieber, Dohan, Lewkowycz, Bosma, Luan, Sutton, Odena (2021). Show Your Work: Scratchpads for Intermediate Computation with Language Models, arXiv:2112.00114", "the scratchpad mechanism and the serial-computation reading"),
   tv("Wei, Wang, Schuurmans, Bosma, Ichter, Xia, Chi, Le, Zhou (2022). Chain-of-Thought Prompting Elicits Reasoning in Large Language Models, NeurIPS 2022", "the prompting realization and its task profile"),
   tv("Turpin, Michael, Perez, Bowman (2023). Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting, NeurIPS 2023", "the measured unfaithfulness that separates utility from explanation"),
   cv(V_MERRILL_PAR, "the fixed-depth parallelism ceiling that intermediate tokens circumvent")],
  None, "B2.18 chain-of-thought/test-time working state (randomize/ablate scratchpad accessibility and content at controlled total inference compute); MLX-19 in-context algorithm execution",
  "Content-free filler tokens reproduce the full chain-of-thought gain at matched token budget on a multi-step obligation, which "
  "would show the mechanism is compute, not intermediate content.",
  "REGISTERED_FOR_EXPERIMENT",
  "Every scratchpad token is a decoded token. Charge the full trace to ΔB_serve and compare at matched TOTAL inference compute, not "
  "at matched answers; and never report a trace as an explanation without an intervention on its content.",
  "11. Feature atlas - memory, retrieval and tools / scratchpads / chain-of-thought state (H,D)")


# ======================================================================================================================
# G. Autoregressive objective and training protocol (calculus section 9)
# argument order reminder: ... parents, formal_theorem, experiment, KILL, STATUS, hidden_cost_rule, section
# ======================================================================================================================

F("TF-052", "Autoregressive factorization",
  "p(x_{1:n}) = p(x_1) prod_{t=2}^n p(x_t | x_{<t}). The chain rule is an IDENTITY for any distribution with defined conditionals; "
  "modelling it autoregressively is a choice about which conditionals to represent, not an approximation.",
  "CD", "C because the factorization declares the legal conditioning structure; D because generation proceeds by sequential decision "
  "over the factors.",
  "The joint distribution exactly: X-TMT10 verifies, in exact rational arithmetic over all 8 binary sequences of length 3, that the "
  "product of conditionals reproduces the joint for every sequence.",
  "Computational symmetry: sampling and scoring are cheap left-to-right and expensive in any other order, so 'the model represents "
  "the joint' does not mean every marginal or infilling query is cheap.",
  "The factorization converts a distribution over an exponentially large sequence space into n local decision problems, each over the "
  "vocabulary, at the cost of fixing one conditioning order.",
  ["ΔB_train", "ΔB_serve", "ΔL_sem"],
  "ΔB_train falls (with a causal mask every position trains in one pass, TF-014); ΔB_serve is Theta(n) sequential steps for "
  "generation, which is the mechanism's characteristic cost.",
  "A non-autoregressive (one-shot, conditionally independent) decoder at matched parameters and compute: the same capacity, and the "
  "exact factorization of dependencies between output positions removed.",
  "Any fixed permutation of the conditioning order is equally exact; a masked/diffusion language model factors over a random mask "
  "order; an energy-based model represents the joint without a factorization at all.",
  [cv(V_VASWANI, "the decoder formulation trained on this factorization"),
   tv("Radford, Wu, Child, Luan, Amodei, Sutskever (2019). Language Models are Unsupervised Multitask Learners (GPT-2), OpenAI technical report", "the scaled realization of the factorization as the sole training objective"),
   cv(V_SHALIZI, "the causal-state formulation of sequential conditioning")],
  TH("TMT-10", "X-TMT10"),
  "MLX-15 predictive-target quotient overlap and MLX-36 generative factorization comparison",
  "A sequence distribution with defined conditionals is exhibited that the chain rule fails to reproduce, contradicting TMT-10. "
  "X-TMT10 checks the identity exactly at its scope.",
  "PROVED_AT_SCOPE",
  "Exactness of the factorization is not exactness of the LEARNED conditionals. Never let TMT-10 carry weight it does not have: the "
  "identity is free, and every gap is in representing and fitting the conditionals.",
  "9. Feature atlas - autoregressive objective and training protocol / Autoregressive factorization (C,D)")

F("TF-053", "Teacher forcing",
  "During training the conditioning prefix is the GROUND-TRUTH x_{<t}, not the model's own generations. The training distribution is "
  "therefore p_data(x_{<t}) while the serving distribution is p_theta(x_{<t}), and the two coincide only if the model is exact.",
  "UC", "U because it defines the development distribution the update law sees; C because it is a declaration about what the model is "
  "conditioned on during development.",
  "Parallelism and the objective: with ground-truth prefixes every position's loss is computable in one forward pass, and the "
  "population optimum is still the true conditional (TMT-11).",
  "The match between training and serving input distributions: once the model generates its own prefix, errors compound into states "
  "never seen in training (exposure bias), so free-running behaviour is NOT predicted by teacher-forced loss.",
  "Teacher forcing buys a fully parallel, low-variance development signal by evaluating the model only on data-distributed prefixes. "
  "The cost is that the serving-time state distribution is never trained on.",
  ["ΔB_train", "ΔL_gen", "ΔL_rob"],
  "ΔB_train falls by a factor of n relative to sequential rollout training; ΔL_rob under long free-running generation degrades, and "
  "the gap grows with generation length.",
  "Scheduled sampling / student forcing: the identical model and objective with the prefix drawn from the model's own samples at "
  "rate epsilon. The compute changes; the distribution mismatch is what is being removed.",
  "Sequence-level training (minimum-risk, REINFORCE on full rollouts) removes the mismatch at much higher variance and cost; "
  "rejection-sampled self-generated data (TF-069) trains on model-distributed prefixes that passed a filter.",
  [tv("Ranzato, Chopra, Auli, Zaremba (2016). Sequence Level Training with Recurrent Neural Networks, ICLR 2016", "the exposure-bias diagnosis and sequence-level alternative"),
   tv("Bengio, Vinyals, Jaitly, Shazeer (2015). Scheduled Sampling for Sequence Prediction with Recurrent Neural Networks, NeurIPS 2015", "the scheduled-sampling negative twin as a method"),
   cv(V_VASWANI, "the teacher-forced parallel training of the decoder")],
  TH("TMT-11", "X-TMT11"),
  "B2.16 instruction/preference separation and MLX-09 feedback density x semantic alignment",
  "Free-running generation quality is shown to be predicted by teacher-forced loss alone across generation lengths, which would "
  "make the distribution mismatch inert.",
  "REGISTERED_FOR_EXPERIMENT",
  "Teacher-forced perplexity is a measurement of one object and free-running quality of another. Report both, or a training-loss "
  "improvement will be credited to a generation capability it does not establish.",
  "9. Feature atlas - autoregressive objective and training protocol / Teacher forcing (U,C)")

F("TF-054", "Cross-entropy next-token loss",
  "L(theta) = E_{x ~ p_data} [ -log p_theta(x_t | x_{<t}) ]. It is a strictly proper scoring rule: by the decomposition "
  "E[-log q(y|x)] = H_p(Y|X) + E_x KL(p(.|x) || q(.|x)), the population optimum over a class containing p is q* = p.",
  "UC", "U because it is the development signal; C because the loss is defined over the compiler's token alphabet, so its value is "
  "not comparable across tokenizers.",
  "The optimum's identity: X-TMT11 verifies the decomposition to 1e-12 on a 3-context x 2-outcome exact distribution and confirms "
  "that q = p attains the minimum with E KL = 0.",
  "Everything finite: finite data, misspecification, optimization failure, distribution shift, and any target distinction not present "
  "in the predictive quotient (TMT-9) remain as separate residual terms.",
  "Cross entropy makes the CONDITIONAL DISTRIBUTION the fitted object, so the model is pushed toward the predictive quotient of the "
  "data. Every capability claim beyond prediction requires the target quotient to factor through it.",
  ["ΔL_sem", "ΔL_cal", "ΔB_train"],
  "ΔL_cal is directly optimized (it is the KL term); ΔL_sem improves only insofar as the target factors through the predictive "
  "quotient; ΔB_train is the dominant cost term of the whole programme.",
  "Train on a NON-proper scoring rule of the same magnitude (e.g. a hinge or accuracy surrogate on the argmax): the same data and "
  "the same steps, and the distribution-recovering property removed - calibration should collapse while argmax accuracy survives.",
  "Any strictly proper scoring rule (Brier, spherical) has the same population optimum with different gradients; masked-language "
  "modelling fits a different set of conditionals with the same rule.",
  [cv(V_HOFFMANN, "the loss-versus-compute frontier on which this objective is optimized in practice"),
   cv(V_SCHAEFFER, "the demonstration that metric choice, not the loss, produces apparent discontinuities"),
   cv(V_IB, "the information-theoretic decomposition that underlies the H + KL identity"),
   cv(V_PSR, "the predictive-state framing of what the optimum's sufficient statistic is")],
  TH("TMT-11", "X-TMT11"),
  "MLX-15 predictive-target quotient overlap; MLX-32 emergence metric audit; MLX-01 predictive residual quotient bound",
  "A target obligation is shown to be exactly recoverable from the predictive optimum although its quotient provably does NOT factor "
  "through the predictive quotient, which would contradict TMT-9's separation.",
  "PROVED_AT_SCOPE",
  "Cross-entropy is per-token and tokenizer-relative. Report bits-per-byte or an explicitly stated tokenizer with every loss number, "
  "and never compare losses across tokenizers - the comparison is meaningless (TF-001).",
  "9. Feature atlas - autoregressive objective and training protocol / Cross-entropy next-token loss (U,C)")

F("TF-055", "Data mixture",
  "The development distribution is a weighted mixture p_data = sum_d w_d p_d over declared domains d (web, code, math, books, "
  "multilingual, synthetic), with sum w_d = 1. The weights are a free development-context choice and they determine which predictive "
  "distinctions the objective rewards.",
  "UC", "U because the mixture IS the development pressure; C because domain membership is an interface-level declaration about what "
  "the data means.",
  "The objective and the architecture: only the distribution changes.",
  "Which capabilities appear: a distinction absent from the mixture is not rewarded, so any capability claim is a claim about the "
  "mixture as much as about the model, and is not preserved under reweighting.",
  "Mixture weights allocate the model's finite capacity and the run's finite steps across domains. The optimal weights depend on the "
  "target obligation and on each domain's marginal value per token, which is why no universal mixture exists.",
  ["ΔL_sem", "ΔL_gen", "ΔB_train"],
  "ΔL_sem and ΔL_gen move per domain with w_d in a zero-sum way at fixed token budget; ΔB_train is unchanged by reweighting at fixed "
  "budget, which is what makes mixture a free-looking but decisive knob.",
  "A mixture matched in TOTAL TOKENS and in per-domain token counts but with each domain's documents replaced by "
  "length-and-vocabulary-matched shuffled text: the budget allocation is identical and the domain content is removed.",
  "Curriculum ordering (the same weights applied over time rather than i.i.d.), per-domain loss reweighting, or domain-specific "
  "fine-tuning reach related allocations with different update geometry.",
  [tv("Xie, Pham, Dong, Du, Liu, Lu, Liang, Le, Ma, Yu (2023). DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining, NeurIPS 2023", "an explicit optimization over mixture weights"),
   cv(V_HOFFMANN, "the token-budget frame in which mixture weights are an allocation"),
   cv(V_NFL, "the statement that no data distribution is universally best without an assumption about the target")],
  None, "MLX-13 data-mixture -> capability/quotient coverage law (gap G-T13) and MLX-43 label quality x quantity",
  "One mixture is shown optimal across target obligations whose domain relevance is deliberately varied, at matched budget.",
  "REGISTERED_FOR_EXPERIMENT",
  "The mixture is the most commonly unreported determinant of a capability claim. Register w_d with every result; a capability "
  "attributed to architecture but produced by mixture is the central confound of this whole layer.",
  "9. Feature atlas - autoregressive objective and training protocol / Data mixture (U,C)")

F("TF-056", "Sequence packing and batching",
  "Concatenate documents to fill a fixed-length training sequence (packing) and group sequences into a batch of size B. Packing "
  "removes padding waste; batching averages B gradients per step. With document masks (TF-015) and position resets, packing is "
  "semantics-preserving.",
  "PU", "P because both are throughput mechanisms; U because batch size changes the gradient noise scale and hence the update "
  "trajectory.",
  "The per-example loss and gradient: with correct masking, packing changes no example's contribution, and batching changes only the "
  "variance of their average.",
  "The optimization trajectory: batch size interacts with learning rate and with the noise scale, so two runs at different B are not "
  "the same run even at equal total tokens.",
  "Packing converts padding into useful tokens (a pure throughput win); batching trades gradient variance against step count and "
  "hardware utilization at a rate set by the gradient noise scale.",
  ["ΔB_train", "ΔB_comm", "ΔL_gen"],
  "ΔB_train falls with packing (no wasted tokens) and with larger B up to the noise-scale limit; ΔB_comm rises with B in data-parallel "
  "settings (TF-077); ΔL_gen can degrade at very large B without a matched learning rate.",
  "Pack WITHOUT document masks or position resets (TF-015): identical throughput and identical token count, and the declared "
  "independence removed - which measures the contamination the masks are there to prevent.",
  "Length-bucketed batching reduces padding without concatenation; gradient accumulation reproduces a large effective B at small "
  "memory; sorting by length trades throughput against ordering bias.",
  [tv("Raffel, Shazeer, Roberts, Lee, Narang, Matena, Zhou, Li, Liu (2020). Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer (T5), JMLR 21", "packing at scale with boundary handling"),
   tv("McCandlish, Kaplan, Amodei, OpenAI Dota Team (2018). An Empirical Model of Large-Batch Training, arXiv:1812.06162", "the gradient-noise-scale account of the batch-size limit"),
   tv("Goyal, Dollar, Girshick, Noordhuis, Wesolowski, Kyrola, Tulloch, Jia, He (2017). Accurate, Large Minibatch SGD, arXiv:1706.02677", "the linear-scaling rule coupling B to the learning rate")],
  None, "B2.20 parallelism/precision repricing; MLX-10 optimizer implicit bias (batch-size axis)",
  "Training outcome at fixed total tokens is shown invariant to batch size across the whole feasible range, which would remove the "
  "noise-scale mechanism.",
  "REGISTERED_FOR_EXPERIMENT",
  "Report tokens, not steps, and report B with the learning rate. A throughput gain from packing is a ΔB_train gain and must not be "
  "reported as a modelling improvement.",
  "9. Feature atlas - autoregressive objective and training protocol / Sequence packing / batching (P,U)")

F("TF-057", "Adam / AdamW",
  "m_t = b1 m_{t-1} + (1-b1) g_t; v_t = b2 v_{t-1} + (1-b2) g_t^2; theta_{t+1} = theta_t - eta ( m_t_hat / (sqrt(v_t_hat) + eps) "
  "+ lambda theta_t ). The per-coordinate division by sqrt(v) is a diagonal preconditioner; AdamW applies the decay term lambda "
  "theta_t DECOUPLED from the gradient rather than through an L2 term inside g_t.",
  "U", "U alone: it is the update law. It changes no forward computation and no served function directly.",
  "The stationary points of the loss: any minimizer of L is still a minimizer; the optimizer changes which one is reached and how "
  "fast, not what counts as good.",
  "The implicit bias and the reached solution: SGD and Adam converge to different points from the same initialization, so "
  "generalization claims do not transfer between optimizers.",
  "The diagonal preconditioner makes the effective step size per coordinate roughly scale-free, which is what allows one global eta "
  "across parameter blocks whose gradient magnitudes differ by orders of magnitude (embeddings vs norms vs projections).",
  ["ΔB_train", "ΔB_mem", "ΔL_gen"],
  "ΔB_train falls (fewer steps than tuned SGD on these problems); ΔB_mem rises by 2x the parameter count for m and v (the dominant "
  "training-memory term after activations); ΔL_gen moves through the implicit bias.",
  "Adam with the preconditioner FROZEN at its step-0 value (v held fixed): identical memory, identical arithmetic, and the adaptive "
  "rescaling removed - isolating 'per-coordinate scaling' from 'momentum'.",
  "Shampoo/Adafactor approximate a richer or cheaper preconditioner; SGD with per-block learning rates reproduces part of the "
  "scale-freeness explicitly; Lion replaces the second moment with a sign rule.",
  [tv("Kingma, Ba (2015). Adam: A Method for Stochastic Optimization, ICLR 2015", "the update law"),
   tv("Loshchilov, Hutter (2019). Decoupled Weight Decay Regularization (AdamW), ICLR 2019", "the decoupling of weight decay from the adaptive denominator"),
   cv(V_SOUDRY, "implicit bias of gradient methods as a determinant of the reached solution"),
   cv(V_COHEN_EOS, "the edge-of-stability regime in which the effective step size self-organizes")],
  None, "MLX-10 optimizer implicit bias; MLX-12 overparameterization and optimization accessibility",
  "Adam and tuned SGD are shown to reach the same solution and the same generalization at matched budget across scales, which would "
  "make the preconditioner a pure speed mechanism with no bias.",
  "REGISTERED_FOR_EXPERIMENT",
  "Optimizer state is 2x the parameters in fp32. Charge it to ΔB_mem explicitly - a 'model size' quoted for training feasibility that "
  "omits m and v understates the requirement by a factor of roughly three.",
  "9. Feature atlas - autoregressive objective and training protocol / Adam/AdamW (U)")

F("TF-058", "Learning-rate schedule",
  "eta(t) as an explicit function of step: constant, cosine decay to a floor, linear decay, inverse-sqrt, or a "
  "warmup-stable-decay trapezoid. It is a declared, time-dependent control on the update magnitude, independent of the loss value.",
  "U", "U alone: a time-varying coefficient on the update law.",
  "The loss landscape and the model class: the schedule changes only the trajectory through them.",
  "The endpoint: a run stopped mid-schedule is not the run's result, and two runs with different schedules at the same step count are "
  "not comparable - which is why schedule length must be declared BEFORE the run.",
  "The schedule controls the effective exploration radius over time: large eta early reaches distant basins, small eta late resolves "
  "within one. Decay to a small floor is what converts a noisy random walk into a settled solution.",
  ["ΔB_train", "ΔL_gen"],
  "ΔB_train is directly set by the schedule's length; ΔL_gen improves with a properly annealed tail and degrades if the run is cut "
  "before the decay completes.",
  "A CONSTANT learning rate equal to the schedule's time-average, run for the same number of steps: the total update magnitude is "
  "matched and the time-dependence removed.",
  "Cyclical or restart schedules (SGDR) reach comparable annealing with a different exploration profile; an adaptive schedule keyed "
  "to a validation signal replaces the declared function with a feedback loop (and must then be charged to ΔB_search).",
  [tv("Loshchilov, Hutter (2017). SGDR: Stochastic Gradient Descent with Warm Restarts, ICLR 2017", "the cosine/restart schedule family"),
   cv(V_HOFFMANN, "the requirement that the schedule be matched to the token budget for a compute-optimal comparison"),
   cv(V_COHEN_EOS, "the interaction between step size and the curvature regime the run occupies")],
  None, "MLX-10 optimizer implicit bias; MLX-31 model/data/compute scaling surface (schedule must be matched to budget)",
  "Final quality at a fixed budget is shown invariant to the schedule shape once the time-average is matched, which would remove the "
  "time-dependence mechanism.",
  "REGISTERED_FOR_EXPERIMENT",
  "A schedule set for budget N and then truncated at N/2 produces a run that is worse than a properly scheduled N/2 run. Declare the "
  "budget and the schedule before the run, and never compare mid-schedule checkpoints across arms.",
  "9. Feature atlas - autoregressive objective and training protocol / learning-rate warmup / decay (U)")

F("TF-059", "Warmup",
  "eta rises from (near) zero to its peak over the first T_w steps, usually linearly. Its purpose is to avoid large updates while the "
  "optimizer's second-moment estimate v_t is still based on few samples and while the network is at its initialization geometry.",
  "U", "U alone. It is the leading segment of the schedule (TF-058), separated here because its mechanism is distinct: it is about "
  "the optimizer's and the network's early-state, not about annealing.",
  "Everything after step T_w: with a well-chosen T_w the run reaches the same regime it would have reached, only without diverging.",
  "The early trajectory, and hence which basin is entered; and the necessity itself is architecture-dependent (post-norm stacks "
  "need it where pre-norm stacks often do not, TF-030).",
  "Early in training Adam's v_t is a high-variance estimate, so the effective step eta m/sqrt(v) can be far larger than intended; "
  "warmup caps the damage until the estimate stabilizes. In post-norm stacks it additionally protects against the large early "
  "gradients the normalizer placement produces.",
  ["ΔB_train", "ΔL_gen"],
  "ΔB_train falls in the sense that a diverged run costs everything; the warmup steps themselves are a small additive cost; ΔL_gen "
  "moves through basin selection.",
  "A run with eta held at the PEAK from step 0 and gradient clipping (TF-060) set to cap the same maximum update magnitude: the "
  "update-size bound is matched by a different mechanism, isolating 'small early steps' from 'stabilized second moment'.",
  "Bias-corrected Adam with a longer b2 horizon, Adam's own bias correction, or a residual-branch zero-init (TF-032) reduce or remove "
  "the need for warmup by fixing the same early-state problem.",
  [tv("Xiong, Yang, He, Zheng, Zheng, Xing, Zhang, Lan, Wang, Liu (2020). On Layer Normalization in the Transformer Architecture, ICML 2020", "the demonstration that warmup necessity depends on normalizer placement"),
   tv("Liu, Jiang, He, Chen, Liu, Gao, Han (2020). On the Variance of the Adaptive Learning Rate and Beyond (RAdam), ICLR 2020", "the early-variance diagnosis of why warmup is needed"),
   tv("Goyal, Dollar, Girshick, Noordhuis, Wesolowski, Kyrola, Tulloch, Jia, He (2017). Accurate, Large Minibatch SGD, arXiv:1706.02677", "warmup as a large-batch stabilizer")],
  None, "B2.10 pre/post norm (warmup requirement is the measured response) and MLX-10 optimizer implicit bias",
  "A pre-norm stack with bias-corrected Adam is shown to still require warmup at every depth, which would rule out both named "
  "mechanisms and leave warmup unexplained.",
  "REGISTERED_FOR_EXPERIMENT",
  "Warmup length is a free knob that can rescue an otherwise-diverging arm. Fix T_w across arms or report it; an arm that needed "
  "longer warmup had a stability problem, and that is a result, not a nuisance to tune away silently.",
  "9. Feature atlas - autoregressive objective and training protocol / learning-rate warmup / decay (U)")

F("TF-060", "Gradient clipping",
  "If ||g||_2 > c then g <- c g / ||g||_2 (global norm clipping), or clip each coordinate to [-c, c]. The update direction is "
  "preserved under global-norm clipping; only the magnitude is bounded.",
  "UN", "U because it modifies the update; N because it is a conditioning/stability constant of the same family as TF-031.",
  "The update DIRECTION under global-norm clipping, and the update entirely on steps where ||g|| <= c.",
  "Unbiasedness: clipping is a nonlinear function of the minibatch gradient, so the expected clipped update is not the expected "
  "gradient. The bias is concentrated on exactly the rare large-gradient steps that motivated it.",
  "Language-model gradients are heavy-tailed: rare batches produce gradients orders of magnitude larger than typical. Clipping "
  "bounds the damage a single such batch can do, converting a divergence risk into a small persistent bias.",
  ["ΔB_train", "ΔL_gen", "ΔL_rob"],
  "ΔB_train falls (fewer diverged runs, larger usable eta); ΔL_gen carries the bias cost; nothing at serve time changes.",
  "Clip at a threshold so large it never binds (c = infinity) with everything else identical: the mechanism is present in the code "
  "path and inert in effect, which separates 'clipping is implemented' from 'clipping binds'.",
  "Gradient normalization (always rescale to norm c) removes the threshold; loss-scaling in mixed precision (TF-075) addresses the "
  "opposite overflow problem; per-layer trust-ratio methods (LARS/LAMB) bound the relative rather than absolute update.",
  [tv("Pascanu, Mikolov, Bengio (2013). On the difficulty of training recurrent neural networks, ICML 2013", "the exploding-gradient diagnosis and the norm-clipping remedy"),
   tv("Zhang, He, Sra, Jadbabaie (2020). Why Gradient Clipping Accelerates Training: A Theoretical Justification for Adaptivity, ICLR 2020", "the heavy-tail/relative-smoothness account of why clipping accelerates"),
   cv(V_COHEN_EOS, "the stability-regime framing of when a step is too large")],
  None, "B2.9 normalization (stability axis); MLX-10 optimizer implicit bias",
  "Clipping is shown to improve final quality in a regime where it never binds, which would mean the effect is not the magnitude "
  "bound.",
  "REGISTERED_FOR_EXPERIMENT",
  "Report c AND the fraction of steps on which it binds. A run where clipping binds on most steps is effectively running normalized "
  "gradient descent under another name, and its learning rate is not comparable to an unclipped arm's.",
  "9. Feature atlas - autoregressive objective and training protocol / gradient clipping (U,N)")

F("TF-061", "Weight decay",
  "An explicit shrinkage of the parameters toward zero: in AdamW, theta <- theta - eta lambda theta applied SEPARATELY from the "
  "gradient step. Coupled L2 regularization instead adds lambda theta to g_t, which the adaptive denominator then rescales - a "
  "different mechanism with the same name.",
  "U", "U alone: a selection pressure on the development trajectory, independent of the data.",
  "The data-fitting objective: decay adds a term that does not depend on the data at all.",
  "The solution reached: decay changes the stationary point, so the trained function is different, not merely smaller.",
  "Decay imposes a constant pressure toward smaller parameters, which in the presence of normalization acts mainly on the effective "
  "learning rate (a scale-invariant layer's direction changes faster when its norm is smaller). Its benefit is regime-dependent, not "
  "universal.",
  ["ΔL_gen", "ΔB_train", "ΔL_sem"],
  "ΔL_gen improves in the regime where capacity exceeds data; ΔB_train can rise or fall through the effective-learning-rate coupling; "
  "ΔL_sem degrades if decay is strong enough to prevent fitting.",
  "Decoupled decay applied ONLY to the normalizer gains and biases (the scale-invariant-free parameters) rather than to the "
  "projections: the same mechanism and the same coefficient, applied where the effective-learning-rate story predicts it should NOT "
  "matter.",
  "An explicit constraint ||theta|| <= r enforced by projection, or a fixed rescaling of normalized layers, reaches the same effective "
  "learning-rate control without a penalty term.",
  [tv("Loshchilov, Hutter (2019). Decoupled Weight Decay Regularization (AdamW), ICLR 2019", "the decoupled construction and the demonstration that coupling changes the mechanism"),
   tv("Van Laarhoven (2017). L2 Regularization versus Batch and Weight Normalization, arXiv:1706.05350", "the effective-learning-rate account of decay under normalization"),
   cv(V_VARMA, "the circuit-efficiency account in which a parameter-norm penalty selects between memorizing and generalizing solutions")],
  None, "MLX-10 optimizer implicit bias; MLX-14 grokking (weight decay is the selection pressure in the cited account)",
  "Weight decay is shown to have the same effect on scale-invariant and scale-sensitive parameters at matched coefficient, which "
  "would rule out the effective-learning-rate mechanism.",
  "REGISTERED_FOR_EXPERIMENT",
  "Report lambda AND which parameter groups it is applied to (embeddings and norms are usually excluded). Two papers reporting "
  "'weight decay 0.1' with different exclusion sets are not running the same experiment.",
  "9. Feature atlas - autoregressive objective and training protocol / Adam/AdamW (U)")


# ======================================================================================================================
# H. Adaptation and alignment (calculus section 10)
# argument order reminder: ... parents, formal_theorem, experiment, KILL, STATUS, hidden_cost_rule, section
# ======================================================================================================================

F("TF-062", "Adapters (bottleneck modules)",
  "Insert a small trainable module into each block - typically h <- h + W_up phi(W_down h) with W_down in R^{r x d}, W_up in "
  "R^{d x r}, r << d - and FREEZE the backbone. Only the adapter parameters (order 2 r d per insertion point) receive gradients.",
  "US", "U because it restricts which parameters the update law may touch; S because the adapter adds a small new state pathway to "
  "the block.",
  "The backbone exactly: theta_base is unchanged, so the original model is recoverable by removing the adapters, and many tasks can "
  "share one backbone.",
  "Serving cost neutrality: adapters add layers to the forward pass, so latency rises unless they are merged (which a nonlinear "
  "adapter cannot be).",
  "By TMT-12's residual-adaptation reading, when the pretrained substrate already resolves most target distinctions, the required "
  "update has low effective complexity and a bounded module suffices; B_adapt* should GROW with the target's residual complexity.",
  ["ΔB_update", "ΔB_train", "ΔB_mem", "ΔB_serve", "ΔL_sem"],
  "ΔB_update and ΔB_train fall by orders of magnitude (few trainable parameters, no optimizer state for the backbone); ΔB_serve rises "
  "slightly; ΔL_sem degrades when the residual complexity exceeds the module's capacity.",
  "Train the SAME NUMBER of parameters chosen at RANDOM inside the frozen backbone (a random sparse mask of equal cardinality): the "
  "trainable budget is matched exactly and the structured bottleneck placement is removed.",
  "LoRA (TF-063) is the linear, mergeable version; prompt tuning (TF-064) adapts through the input instead of the weights; a "
  "last-layer-only fine-tune is the crudest bounded update.",
  [tv("Houlsby, Giurgiu, Jastrzebski, Morrone, de Laroussilhe, Gesmundo, Attariyan, Gelly (2019). Parameter-Efficient Transfer Learning for NLP, ICML 2019", "the bottleneck-adapter construction"),
   cv(V_MODULAR, "the survey framing of adapters inside the modular-deep-learning mechanism family"),
   cv(V_LORALIB, "reuse and composition of many small adapters over one backbone")],
  None, "B2.15 LoRA/adapters/full fine-tune (targets with controlled residual rank / conditional quotient complexity) and MLX-18 parameter-efficient adaptation vs residual complexity",
  "Minimum adapter capacity at protected performance is shown NOT to increase with the target's residual complexity, which is the "
  "explicit falsifier of TM-12's strong form.",
  "REGISTERED_FOR_EXPERIMENT",
  "Charge the frozen backbone's memory to ΔB_mem (it is still resident) and the added forward modules to ΔB_serve. 'Only 0.1 percent "
  "of parameters trained' is a ΔB_update claim, not a memory or latency claim.",
  "10. Feature atlas - adaptation/alignment / LoRA / adapters / prompt tuning (U,S)")

F("TF-063", "LoRA (low-rank adaptation)",
  "Replace a frozen weight W_0 by W_0 + BA with B in R^{d x r}, A in R^{r x k}, rank r << min(d, k), A initialized to a random small "
  "matrix and B to zero so the initial function is exactly the base model. Only A and B train; at serve time BA can be MERGED into "
  "W_0, giving zero added latency.",
  "US", "U because it constrains the update to a rank-r subspace; S because the merged result is a genuine change of the state "
  "transform.",
  "The base model before merging, and the serving cost after merging: the merged W_0 + BA has exactly the shape and cost of W_0.",
  "The reachable update set: the update is confined to a rank-r subspace, so a target requiring a higher-rank change to W is NOT "
  "reachable at that r.",
  "TM-12: adaptation cost should track the target's residual complexity, not the base model's size. The rank r is a direct, "
  "measurable handle on the assumed residual dimension, which makes B2.15 a quantitative test of that claim rather than a slogan.",
  ["ΔB_update", "ΔB_train", "ΔB_mem", "ΔL_sem"],
  "ΔB_update and ΔB_train fall as r/d; ΔB_serve is EXACTLY unchanged after merging; ΔL_sem degrades when the required update's "
  "effective rank exceeds r.",
  "A rank-r update with A and B FROZEN at their random initialization and only a per-row scalar trained: the same parameter shape and "
  "the same merge property, and the learned-subspace mechanism removed.",
  "Full fine-tuning is the r = min(d,k) limit; a bottleneck adapter (TF-062) adds the same capacity nonlinearly and unmergeably; "
  "(IA)^3-style learned rescalings adapt with even fewer parameters and a stronger constraint.",
  [tv("Hu, Shen, Wallis, Allen-Zhu, Li, Wang, Wang, Chen (2021). LoRA: Low-Rank Adaptation of Large Language Models, ICLR 2022", "the low-rank construction, the zero-init merge property and the intrinsic-rank hypothesis"),
   cv(V_LORALIB, "composition and routing over a library of LoRA modules"),
   cv(V_MODULAR, "the modular-adaptation mechanism family in which LoRA is the linear case"),
   cv(V_JACOT, "the linearized-regime account in which a low-rank parameter change suffices near a good initialization")],
  None, "B2.15 LoRA/adapters/full fine-tune; MLX-18 parameter-efficient adaptation vs residual complexity (gap: the B_adapt* law)",
  "Minimum adequate rank r* is shown to be independent of the target's residual complexity at matched information and matched "
  "protected performance - the direct falsifier of TM-12.",
  "REGISTERED_FOR_EXPERIMENT",
  "Charge the search over r and over which matrices to adapt to ΔB_search: a LoRA arm tuned over r compared against one full "
  "fine-tune run is not a controlled comparison. Merging makes serving free; UNMERGED multi-adapter serving is not.",
  "10. Feature atlas - adaptation/alignment / LoRA / adapters / prompt tuning (U,S)")

F("TF-064", "Prompt tuning / prefix tuning",
  "Prepend m trainable continuous vectors to the input (prompt tuning) or to the keys and values of every layer (prefix tuning), and "
  "freeze all of theta. The trainable state is m d (or 2 L m d) parameters that live in the INPUT or the cache, never in the weights.",
  "US", "U because it is the only thing the update law touches; S because the learned prefix is carried state, not a transform.",
  "theta exactly, and therefore every capability the base model had: prompt tuning cannot remove knowledge, only re-address it.",
  "Serving cost: the prefix occupies m context positions (or 2 L m d cache elements) on every request forever, so it is a permanent "
  "serving tax rather than a one-time weight change.",
  "A learned prefix selects a REGION of the base model's conditional behaviour. It can expose and re-weight existing capability but "
  "cannot add a distinction the base model cannot make, which makes it the sharpest instrument for separating exposure from "
  "acquisition (B2.16).",
  ["ΔB_update", "ΔB_train", "ΔB_serve", "ΔB_mem", "ΔL_sem"],
  "ΔB_update and ΔB_train are the smallest in the adaptation family; ΔB_serve and ΔB_mem rise permanently by the prefix length; "
  "ΔL_sem is capped by what the frozen model can already express.",
  "A DISCRETE prompt of the same token length selected by search: the same serving cost and the same frozen backbone, with the "
  "continuous-optimization mechanism removed - this separates 'conditioning helps' from 'continuous conditioning helps'.",
  "Instruction tuning (TF-065) achieves similar re-addressing by changing theta; a retrieved exemplar prefix (TF-046) supplies "
  "conditioning per request instead of once.",
  [tv("Lester, Al-Rfou, Constant (2021). The Power of Scale for Parameter-Efficient Prompt Tuning, EMNLP 2021", "the continuous-prompt construction and its scale dependence"),
   tv("Li, Liang (2021). Prefix-Tuning: Optimizing Continuous Prompts for Generation, ACL 2021", "the per-layer key/value prefix variant"),
   cv(V_GARG, "in-context conditioning as a mechanism that selects behaviour from a frozen model"),
   cv(V_VONOSWALD, "the account of in-context conditioning as implicit optimization inside the forward pass")],
  None, "B2.16 instruction/preference separation (capability state vs instruction policy) and MLX-19 in-context algorithm execution",
  "A learned prefix is shown to give a frozen model a capability it demonstrably lacked under every prompt, which would contradict "
  "the exposure-not-acquisition reading.",
  "REGISTERED_FOR_EXPERIMENT",
  "The prefix is charged on EVERY request. Report m and the resulting per-request context and cache overhead; a 'cheapest adaptation "
  "method' claim that counts only trained parameters inverts the serving economics.",
  "10. Feature atlas - adaptation/alignment / LoRA / adapters / prompt tuning (U,S)")

F("TF-065", "Instruction tuning / SFT",
  "Supervised fine-tuning on (instruction, response) pairs with the same cross-entropy loss, usually on a small, curated, "
  "distributionally narrow set relative to pretraining. It changes the POLICY mapping from latent capability to "
  "instruction-conditioned behaviour.",
  "UC", "U because it is a gradient update; C because the instruction format is an interface contract about how requests are "
  "expressed.",
  "Most of what pretraining installed: SFT on a small set changes behaviour far more than it changes stored knowledge.",
  "The separation between 'the model can do X' and 'the model does X when asked': SFT moves the second sharply, so a post-SFT "
  "capability measurement is not a measurement of the pretrained model.",
  "SFT re-addresses existing capability into an instruction-following policy. The strong claim is a SPLIT: the fraction of measured "
  "gain that is exposure of latent capability versus genuine acquisition, which B2.16 is constructed to separate.",
  ["ΔL_sem", "ΔB_train", "ΔB_update", "ΔL_gen"],
  "ΔL_sem on instruction-formatted evaluation rises steeply for a small ΔB_train; ΔL_gen can degrade on the pretraining distribution "
  "(alignment tax / forgetting).",
  "Fine-tune on the same number of tokens of the same responses with the INSTRUCTIONS REMOVED or scrambled: the update magnitude and "
  "the response distribution are matched and the instruction-conditioning is removed.",
  "Prompt tuning (TF-064) and in-context exemplars reach the same re-addressing without changing theta; preference optimization "
  "(TF-066, TF-068) continues it with a different signal.",
  [tv("Wei, Bosma, Zhao, Guu, Yu, Lester, Du, Dai, Le (2022). Finetuned Language Models Are Zero-Shot Learners (FLAN), ICLR 2022", "instruction tuning and its zero-shot transfer claim"),
   tv("Ouyang, Wu, Jiang, Almeida, Wainwright, Mishkin, Zhang, Agarwal, Slama, Ray, et al. (2022). Training language models to follow instructions with human feedback (InstructGPT), NeurIPS 2022", "the SFT stage inside the full alignment pipeline"),
   cv(V_DOHARE, "plasticity/forgetting as the cost side of a narrow fine-tuning distribution"),
   cv(V_GUPTA_EDIT, "the measured forgetting that accompanies sequential narrow updates")],
  None, "B2.16 instruction/preference separation (latent-capability tasks where instruction mapping varies independently of knowledge) and MLX-14 instruction tuning -> capability exposure vs acquisition split",
  "SFT on a small curated set is shown to install a capability that no prompt, prefix or in-context exemplar could elicit from the "
  "base model, which would move the mechanism from exposure to acquisition (gap G-T14).",
  "REGISTERED_FOR_EXPERIMENT",
  "Report the base model's best ELICITED performance (over prompts and in-context exemplars) as the baseline, not its zero-shot "
  "default. Against the default baseline, every exposure effect is miscounted as acquisition.",
  "10. Feature atlas - adaptation/alignment / SFT / instruction tuning (U,C)")

F("TF-066", "RLHF (policy optimization against a learned preference model)",
  "Optimize E_{x ~ D, y ~ pi_theta(.|x)} [ r_phi(x, y) ] - beta KL(pi_theta || pi_ref) by a policy-gradient method (PPO-style), where "
  "r_phi is a reward model fit to human comparisons and pi_ref is the SFT policy. The optimized object is a PROXY, not the obligation.",
  "UV", "U because it is a policy update law; V because r_phi acts as an admission/preference authority over generated outputs.",
  "The KL anchor's guarantee only: for large beta the policy stays near pi_ref, which bounds how far behaviour can move.",
  "Truth, calibration and the obligation itself: r_phi rewards what annotators preferred, which is not the same function. "
  "Over-optimization of r_phi predictably decreases true quality past a point.",
  "RLHF shifts the policy toward the proxy's high-reward region. The measured gain is the product of (a) how well r_phi correlates "
  "with the obligation and (b) how far the KL budget lets the policy move - which is exactly why the cited scaling laws for reward "
  "over-optimization exist.",
  ["ΔL_sem", "ΔL_cal", "ΔB_train", "ΔB_verify", "ΔB_update"],
  "ΔL_sem on preference-shaped evaluation rises and then FALLS with over-optimization; ΔL_cal typically degrades (RLHF'd models are "
  "systematically over-confident); ΔB_train and ΔB_verify rise substantially (sampling plus reward-model inference).",
  "Optimize against a reward model trained on RANDOM preference labels with the identical KL budget and identical compute: the "
  "optimization pressure and the compute are matched and the preference SIGNAL is removed.",
  "DPO-like direct preference optimization (TF-068) reaches a related optimum without an explicit sampler; best-of-N with the same "
  "reward model (TF-041) applies the same proxy at serve time instead of at train time; rejection-sampling fine-tuning (TF-069) is "
  "the offline version.",
  [tv("Christiano, Leike, Brown, Martic, Legg, Amodei (2017). Deep Reinforcement Learning from Human Preferences, NeurIPS 2017", "the preference-model-plus-policy-optimization construction"),
   tv("Ouyang, Wu, Jiang, Almeida, Wainwright, Mishkin, Zhang, Agarwal, Slama, Ray, et al. (2022). Training language models to follow instructions with human feedback (InstructGPT), NeurIPS 2022", "the full RLHF pipeline at LLM scale"),
   cv(V_GAO, "the measured scaling law for reward-model over-optimization"),
   cv(V_KWA, "the result that a KL penalty does not by itself mitigate heavy-tailed reward misspecification")],
  None, "B2.16 instruction/preference separation and MLX-15 preference optimization -> policy shift / truth divergence law (gap G-T15)",
  "Preference-optimized policies are shown NOT to diverge from the obligation as reward-model optimization proceeds, at any KL "
  "budget, which would remove the Goodhart mechanism the cited parents establish.",
  "PARENT_THEOREM_UNDER_ASSUMPTIONS",
  "Charge the reward model's training data, its parameters and its inference to ΔB_verify and ΔB_mem, and report the KL from pi_ref "
  "with every quality number. A preference win reported without the KL budget is unfalsifiable.",
  "10. Feature atlas - adaptation/alignment / reward model + RLHF (U,V)")

F("TF-067", "Reward models",
  "r_phi(x, y) fit to human comparisons, typically by the Bradley-Terry likelihood "
  "P(y_w > y_l | x) = sigma(r_phi(x, y_w) - r_phi(x, y_l)). It is a learned scalar proxy for a preference relation, identified only up "
  "to an additive function of x.",
  "V", "V alone: it is an admission/ranking authority. It is not a truth verifier and does not become one by being accurate on "
  "held-out comparisons.",
  "Pairwise ordering on the distribution it was fit to: a well-fit r_phi ranks in-distribution pairs as the annotators did.",
  "Ordering off-distribution: policy optimization actively pushes y into regions with no comparison data, where r_phi's ranking is "
  "unconstrained - which is the mechanism of reward hacking, not an implementation defect.",
  "The reward model transfers a sparse human signal to an unbounded number of generations. Its value is bounded by its "
  "out-of-distribution accuracy, which DECREASES exactly where the optimizer is pushing.",
  ["ΔB_verify", "ΔB_train", "ΔB_mem", "ΔL_sem"],
  "ΔB_verify is where its whole cost lives (training data, parameters and per-sample inference); ΔL_sem improves only while the "
  "policy stays where r_phi is accurate.",
  "A reward model of the same size and the same training compute fit to a PROVABLY IRRELEVANT surface feature (response length, "
  "formatting): the proxy machinery is identical and the correspondence to human preference is removed. Reward models that in fact "
  "track length are the empirical instance of this twin.",
  "An exact checker (a unit test, a proof assistant) is the authoritative limit with zero proxy error; a pairwise LLM judge replaces "
  "the scalar head with a generative comparison; DPO (TF-068) embeds the same Bradley-Terry model implicitly.",
  [cv(V_GAO, "reward-model over-optimization scaling and the accuracy-versus-KL frontier"),
   cv(V_SKALSE, "the formal definition and characterization of reward hacking"),
   cv(V_KARWOWSKI, "Goodhart's law in RL as a general phenomenon of proxy optimization"),
   cv(V_PAN, "the measured effects of reward misspecification across environments")],
  None, "B2.16 instruction/preference separation; MLX-15 preference optimization -> truth divergence; the Goodhart gates of GMI_BIOSPHERE_NO_FREE_LUNCH_AND_GOODHART_GATES_V1.md",
  "A reward model is shown to retain its ranking accuracy in the regions policy optimization drives it to, which would remove the "
  "out-of-distribution mechanism behind reward hacking.",
  "PARENT_THEOREM_UNDER_ASSUMPTIONS",
  "A reward model is a VERIFIER with an error rate, not a ground truth. Charge its error to ΔL_sem and its inference to ΔB_verify; "
  "'the reward went up' is a statement about r_phi, never about the obligation.",
  "10. Feature atlas - adaptation/alignment / reward model + RLHF (U,V)")

F("TF-068", "DPO-like direct preference optimization",
  "Optimize a closed-form loss on preference pairs directly: "
  "-log sigma( beta [ log(pi_theta(y_w|x)/pi_ref(y_w|x)) - log(pi_theta(y_l|x)/pi_ref(y_l|x)) ] ). Under the Bradley-Terry assumption "
  "this has the same optimum as the KL-regularized RLHF objective, with no reward model and no sampling loop.",
  "UV", "U because it is a supervised update law on preference data; V because the preference signal still functions as an admission "
  "authority - it is merely implicit in the loss.",
  "The KL-regularized optimum under the stated assumptions: the algorithm change does not change what is being optimized toward.",
  "The optimization PATH and the off-distribution behaviour: DPO sees only the offline pairs, so it never observes the policy's own "
  "samples, and the implicit reward it induces is unconstrained off the pair distribution.",
  "DPO removes the sampler and the reward model, replacing an on-policy loop with an offline supervised one. GMI's claim is that this "
  "is an information-legality and burden change, not a semantic privilege: the same proxy problem remains.",
  ["ΔB_train", "ΔB_verify", "ΔB_mem", "ΔL_sem", "ΔL_cal"],
  "ΔB_train and ΔB_verify fall sharply (no sampling, no reward-model inference); ΔB_mem falls (no reward model resident); ΔL_sem and "
  "ΔL_cal inherit the same over-optimization exposure as RLHF.",
  "The identical loss with the preference LABELS SHUFFLED within each pair: identical data, identical compute, identical "
  "regularization, and the preference information removed.",
  "RLHF (TF-066) reaches the same stated optimum on-policy at higher cost; rejection-sampling fine-tuning (TF-069) uses the same "
  "offline principle with a hard filter instead of a soft contrast; IPO/KTO vary the contrastive functional.",
  [tv("Rafailov, Sharma, Mitchell, Ermon, Manning, Finn (2023). Direct Preference Optimization: Your Language Model is Secretly a Reward Model, NeurIPS 2023", "the closed-form equivalence and the algorithm"),
   cv(V_GAO, "the over-optimization scaling that the follow-on work extends to direct alignment algorithms"),
   cv(V_GOODHART, "the general categorization of proxy failure that applies identically to implicit and explicit rewards")],
  None, "B2.16 instruction/preference separation; MLX-15 preference optimization -> policy shift / truth divergence law",
  "DPO is shown to avoid the over-optimization/truth-divergence behaviour of explicit-reward RLHF at matched preference data and "
  "matched KL, which would give the algorithm a semantic privilege GMI denies it.",
  "REGISTERED_FOR_EXPERIMENT",
  "Cheaper is not safer. Report the implicit KL from pi_ref and evaluate off the preference distribution; DPO's burden saving must "
  "not be reported as a reduction in Goodhart exposure.",
  "10. Feature atlas - adaptation/alignment / DPO-like preference optimization (U,V)")

F("TF-069", "Rejection sampling / verifier fine-tuning",
  "Sample N candidate outputs per prompt from the current policy, keep only those a filter admits (an exact checker, a reward "
  "threshold, or self-consistency agreement), and fine-tune on the survivors. It is a development-data ADMISSION mechanism: the "
  "update law is ordinary cross-entropy on a selected set.",
  "VU", "V because the filter is the admission authority that defines the training set; U because the surviving data drives an "
  "ordinary supervised update.",
  "The objective and the update law: nothing changes except which data is admitted.",
  "The training distribution's relation to the policy's own: selection introduces a bias toward whatever the filter over-admits, so "
  "the fine-tuned model inherits the filter's blind spots, amplified by iteration.",
  "When the filter correlates with the obligation, selection converts the policy's own coverage into higher-quality development data "
  "at no annotation cost. The gain is bounded by coverage (does any of the N pass) and by filter precision (do passing samples "
  "deserve to).",
  ["ΔL_sem", "ΔB_train", "ΔB_search", "ΔB_verify"],
  "ΔB_search rises as N generations per prompt and ΔB_verify as N filter evaluations; ΔL_sem improves while the filter is precise and "
  "degrades (self-amplifying bias) under iteration with an imprecise one.",
  "Fine-tune on N samples selected at RANDOM rather than by the filter: the generation and training compute are identical and the "
  "selection is removed - the decisive control for 'selection, not self-training, is the mechanism'.",
  "Best-of-N at serve time (TF-041) applies the identical filter without changing theta; expert iteration / STaR-style loops iterate "
  "this mechanism; a preference optimizer (TF-068) uses a soft contrast where this uses a hard cut.",
  [tv("Zelikman, Wu, Mu, Goodman (2022). STaR: Bootstrapping Reasoning With Reasoning, NeurIPS 2022", "the filter-and-finetune loop on self-generated rationales"),
   tv("Cobbe, Kosaraju, Bavarian, Chen, Jun, Kaiser, Plappert, Tworek, Hilton, Nakano, Hesse, Schulman (2021). Training Verifiers to Solve Math Word Problems, arXiv:2110.14168", "the trained-verifier filter and its selection effect"),
   cv(V_SETLUR, "the result that verification is what makes test-time and self-improvement scaling pay"),
   cv(V_MONKEYS, "the coverage measurement that bounds what any filter can select from")],
  None, "B2.16 instruction/preference separation; MLX-26 verifier-gated speculative compiler; MLX-44 synthetic data novelty/fidelity",
  "Selection by a filter no better than chance reproduces the full gain at matched compute, which would show the mechanism is "
  "self-training on more data rather than admission.",
  "REGISTERED_FOR_EXPERIMENT",
  "Charge all N generations to ΔB_search and all N filter calls to ΔB_verify - the visible cost is one fine-tune, the real cost is N "
  "times the corpus. Report filter precision and recall, or the selection bias is invisible and compounds across iterations.",
  "10. Feature atlas - adaptation/alignment / rejection sampling / verifier fine-tuning (V,U)")

F("TF-070", "Model editing",
  "A targeted parameter change intended to alter ONE fact or association while leaving everything else intact: a rank-one update to a "
  "located MLP key-value pair (ROME/MEMIT-style), or a memory-based override (SERAC/GRACE-style) that routes matching inputs to a "
  "separate module. The obligation is LOCALITY, not accuracy.",
  "UHV", "U because it is a (bounded) parameter update; H because memory-based editors add persistent external state; V because the "
  "edit must be admissible and checkable.",
  "The edited fact itself, by construction: every editor succeeds on the exact prompt it was fitted to.",
  "The collateral cone: paraphrases, logical consequences, and unrelated facts. The cited ripple-effect and sequential-editing work "
  "measures exactly this failure, so 'the edit worked' does not transfer.",
  "Facts are not stored in isolated parameters, so a bounded parameter change has an unbounded and unmeasured downstream dependency "
  "cone. Memory-based editors bound the cone by construction at the price of carrying explicit external state.",
  ["ΔB_update", "ΔL_sem", "ΔL_rob", "ΔB_verify", "ΔB_mem"],
  "ΔB_update falls dramatically relative to retraining; ΔL_sem and ΔL_rob degrade on the collateral cone, and the degradation "
  "COMPOUNDS with the number of sequential edits; ΔB_verify rises if locality is actually checked.",
  "Apply a rank-one update of the same norm at a RANDOMLY CHOSEN location: the parameter perturbation magnitude is matched exactly and "
  "the localization is removed, which measures how much of the collateral damage is localization-specific.",
  "Retrieval or an external store (TF-046, TF-049) makes the same correction without touching theta; full fine-tuning on the corrected "
  "fact is the unbounded-cost, unbounded-cone alternative; a routed override module externalizes the edit entirely.",
  [cv(V_MENG, "the located rank-one and mass-editing constructions"),
   cv(V_MITCHELL, "the memory-based routing alternative that bounds the cone by construction"),
   cv(V_RIPPLE, "the measurement of consequence/paraphrase failures after a successful edit"),
   cv(V_GUPTA_EDIT, "the measured gradual and catastrophic forgetting under sequential editing")],
  None, "MLX-25 model editing / unlearning locality; B2.17 RAG/tool authority (the external-store alternative)",
  "A parametric editor is shown to achieve an exact, verifiable, bounded collateral cone under long sequences of edits, which would "
  "remove the distributed-storage objection and make external stores unnecessary for this purpose.",
  "PARENT_THEOREM_UNDER_ASSUMPTIONS",
  "Score an edit by four numbers, not one: efficacy on the target, generalization to paraphrase, LOCALITY on unrelated inputs, and "
  "retained competence after k sequential edits. An editor reported on efficacy alone has not been measured.",
  "10. Feature atlas - adaptation/alignment / model editing / unlearning (U,H,V)")

F("TF-071", "Unlearning",
  "Produce a model that behaves as if a designated subset of the training data had never been present. EXACT unlearning requires that "
  "the result be indistinguishable from retraining without that data (achieved by sharded retraining, SISA-style); approximate "
  "unlearning targets a bounded divergence from that hypothetical model.",
  "UHV", "U because it is a reverse update obligation; H because it is an obligation about the training HISTORY, not about current "
  "behaviour; V because the result must be certifiable.",
  "Exactly what the exact construction guarantees: with sharded retraining, the produced model is one that could have been trained "
  "without the forgotten shard, so the guarantee is definitional.",
  "Anything approximate: a model that merely fails to emit the forgotten content may still encode it recoverably, so behavioural "
  "suppression is NOT unlearning and cannot be certified as such.",
  "The cost of exact removal is set by how much of the computation depended on the removed data. Sharding bounds that dependence in "
  "advance (at a capability cost from reduced cross-shard sharing); unsharded training makes exact removal require full retraining.",
  ["ΔB_update", "ΔB_verify", "ΔL_sem", "ΔB_mem"],
  "ΔB_update for exact unlearning is a shard retrain (or a full one); ΔB_verify is the certification cost; ΔL_sem degrades under "
  "sharding because shards cannot share data.",
  "Behavioural suppression: fine-tune the model to refuse the forgotten content with matched compute, WITHOUT any removal guarantee. "
  "The observable output distribution can match while the certification property is absent - which is the whole point.",
  "Differentially-private training bounds any single example's influence in advance; an external-store design (TF-049) makes deletion "
  "a database transaction; influence-function-based approximate removal trades certification for cost.",
  [cv(V_BOURTOULE, "the SISA sharded-retraining construction and the exact-unlearning definition"),
   cv(V_MENG, "parametric editing as the approximate-removal neighbour with the same locality problem"),
   cv(V_RIPPLE, "the measurement showing that a successful surface change leaves consequences intact"),
   cv(V_PERSIST, "versioned state as the mechanism that makes selective removal a bounded operation")],
  None, "MLX-25 model editing / unlearning locality; B2.17 (external authority as the deletion-friendly design)",
  "An approximate unlearning method is shown to be certifiably indistinguishable from retraining-without-the-data, which would "
  "collapse the exact/approximate distinction this entry rests on.",
  "PARENT_THEOREM_UNDER_ASSUMPTIONS",
  "State which guarantee is claimed. Charge sharded-retraining capability loss to ΔL_sem and certification to ΔB_verify; a "
  "'forgetting' result demonstrated only by prompting the model is a behavioural claim and must be labelled as one.",
  "10. Feature atlas - adaptation/alignment / model editing / unlearning (U,H,V)")

F("TF-072", "Distillation",
  "Train a student q_psi on a teacher p_theta's outputs: minimize E_x KL(p_theta(.|x) || q_psi(.|x)) over a transfer set (optionally "
  "at a softening temperature), instead of on hard labels. The student receives the teacher's full conditional distribution, which "
  "carries far more information per example than a one-hot label.",
  "UP", "U because it is a development signal (a different target distribution); P because the point is a smaller, cheaper serving "
  "realization - it is TM-11's serving compiler with a training-time implementation.",
  "The teacher's ranking on the transfer set, approximately, to within the student's capacity and the transfer set's coverage.",
  "Behaviour off the transfer set: the student is constrained only where it was shown examples, so distillation is a compilation "
  "with a declared input domain, not a global equivalence.",
  "The teacher's soft distribution reveals its whole conditional structure per example (the 'dark knowledge' of relative "
  "probabilities among wrong answers), so the student needs far fewer examples than training from labels would require.",
  ["ΔB_serve", "ΔB_mem", "ΔB_train", "ΔL_sem", "ΔL_rob"],
  "ΔB_serve and ΔB_mem fall by the size ratio; ΔB_train rises (teacher inference over the transfer set); ΔL_sem degrades where the "
  "student's capacity or the transfer set's coverage binds.",
  "Train the same student on HARD LABELS from the same transfer set with the same compute: the data, the architecture and the budget "
  "are matched and the soft-distribution information is removed.",
  "Post-training quantization (TF-074) compiles the same model to a cheaper format without a student; pruning removes capacity in "
  "place; a smaller model trained from scratch on the same data is the no-teacher control.",
  [tv("Hinton, Vinyals, Dean (2015). Distilling the Knowledge in a Neural Network, NeurIPS 2014 Deep Learning Workshop / arXiv:1503.02531", "the soft-target construction and the dark-knowledge argument"),
   cv(V_HOFFMANN, "the compute-optimal frame against which a distilled student must be compared"),
   cv(V_KCMAP, "knowledge compilation as the general frame: pay once to obtain a cheaper-to-query representation with a declared query class"),
   cv(V_MICHAUD, "the discrete-capability reading of what a smaller student can and cannot retain")],
  TH("TMT-12", "X-TMT12"),
  "B2.14 quantization / distillation (vary allowed semantic distortion and hardware price) and MLX-28 distillation as quotient-preserving compilation",
  "A student is shown to match its teacher on obligations whose required distinctions exceed the student's representational capacity, "
  "contradicting the collision argument of TMT-12.",
  "REGISTERED_FOR_EXPERIMENT",
  "Charge the teacher's inference over the whole transfer set to ΔB_train, and the teacher's own training if it exists only to make "
  "the student. Report the transfer set's coverage: a student evaluated only inside it has not been tested for compilation error.",
  "12. Feature atlas - serving and systems / weight quantization (P,S) and 3. TM-11 approximate serving compilation principle")


# ======================================================================================================================
# I. Serving and systems (calculus section 12)
# argument order reminder: ... parents, formal_theorem, experiment, KILL, STATUS, hidden_cost_rule, section
# ======================================================================================================================

F("TF-073", "FlashAttention-style exact IO compilation",
  "Compute the SAME map softmax(QK^T/sqrt(d) + M)V by tiling over key blocks with an online running maximum and rescaling, so the "
  "n x n score matrix is never materialized in slow memory. HBM traffic falls from Theta(n^2) to Theta(n^2 d / SRAM) while the "
  "arithmetic performed is the same function.",
  "P", "P alone. By TMT-7, two algorithms computing the same map under the same numeric semantics belong to ONE semantic mechanism "
  "class; calling this a new form of attention is an implementation-label error.",
  "The mathematical result exactly. X-TMT7 verifies this in exact rational arithmetic (naive vs online blocks of size 2 and 3 agree "
  "bit for bit) and in float64 with real exp (max absolute difference <= 1e-12 over all positions).",
  "The numerical error profile and the memory-traffic signature: the online rescaling changes the summation ORDER, so float results "
  "can differ in the last bits, and the activation-memory requirement changes by orders of magnitude.",
  "Attention is memory-bandwidth-bound, not FLOP-bound, at practical sizes. Restructuring the loop so the score tile stays in fast "
  "memory removes the dominant cost without changing the computed function.",
  ["ΔB_serve", "ΔB_mem", "ΔB_train"],
  "ΔB_mem falls from Theta(n^2) to Theta(n) activation memory; ΔB_serve and ΔB_train fall by the bandwidth saving; every ΔL_* "
  "component is EXACTLY zero at the mathematical level.",
  "The same tiled loop with the running-maximum rescaling REMOVED (naive online accumulation): identical memory traffic and identical "
  "tile structure, with the numerical-stability mechanism gone - which separates 'tiling' from 'stable online softmax'.",
  "Memory-efficient attention with recomputation, chunked attention with explicit rescaling, or a fused kernel that materializes tiles "
  "in registers are alternative schedules of the same map; TVM-style autoscheduling searches this space automatically.",
  [tv("Dao, Fu, Ermon, Rudra, Re (2022). FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness, NeurIPS 2022", "the IO-aware tiled exact algorithm and its HBM-traffic analysis"),
   tv("Rabe, Staats (2021). Self-attention Does Not Need O(n^2) Memory, arXiv:2112.05682", "the online-rescaling memory argument this schedule uses"),
   cv(V_TVM, "the general point that schedule search changes cost, not semantics"),
   cv(V_VASWANI, "the map being computed")],
  TH("TMT-7", "X-TMT7"),
  "B2.13 exact IO attention implementation (mathematically identical implementations with different IO schedules)",
  "An exact IO-restructured attention is shown to change a protected semantic outcome beyond floating-point reassociation, which "
  "would contradict TMT-7. X-TMT7 fixes the equality in exact arithmetic at its scope.",
  "PROVED_AT_SCOPE",
  "Report the numeric semantics (dtype, accumulation precision, summation order) with any exactness claim: 'exact' means exact as a "
  "real-arithmetic map, and float reassociation is a real, meterable difference that TMT-7's assumption explicitly excludes.",
  "12. Feature atlas - serving and systems / FlashAttention / tiling (P)")

F("TF-074", "Weight quantization",
  "A serving compiler C: theta -> Q(theta) into a low-bit format (int8, int4, NF4) with per-group scales, applied post-training or "
  "with quantization-aware training. By TMT-11 it is admissible when the induced semantic distortion eps_C is tolerated by the "
  "obligation and the lifecycle saving dominates the compilation burden.",
  "PS", "P because the format is a physical realization choice; S because the state's representable set changes.",
  "The computation wherever the quantization grid separates the states that matter: if Q is injective on obligation-relevant "
  "distinctions, behaviour is preserved.",
  "Exactness in general. By TMT-12, if Q(z) = Q(z') while q_O(z) != q_O(z'), exact behaviour on both is impossible. X-TMT12 exhibits "
  "such a collision (drop-low-bit merging parity-distinct states) AND a side-channel quantizer that avoids it.",
  "Serving is memory-bandwidth-bound, so halving the bytes per weight nearly halves the time per token. The distortion is "
  "concentrated in outlier channels, which is why per-group scaling and outlier-preserving schemes recover most of the loss.",
  ["ΔB_mem", "ΔB_serve", "ΔB_comm", "ΔL_sem", "ΔL_rob"],
  "ΔB_mem falls by the bit ratio and ΔB_serve roughly with it; ΔL_sem and ΔL_rob degrade in proportion to how many "
  "obligation-relevant distinctions the grid merges.",
  "Add ZERO-MEAN NOISE of the same variance as the quantization error at FULL precision: the perturbation magnitude is matched and "
  "the deterministic grid structure (and the memory saving) is removed - which separates 'noise tolerance' from 'grid collisions'.",
  "Distillation into a smaller full-precision model (TF-072) reaches a similar serving budget by a different compiler; pruning removes "
  "weights rather than precision; a mixed scheme keeps outlier channels wide.",
  [tv("Dettmers, Lewis, Belkada, Zettlemoyer (2022). LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale, NeurIPS 2022", "the outlier-channel diagnosis and the mixed-precision remedy"),
   tv("Frantar, Ashkboos, Hoefler, Alistarh (2023). GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers, ICLR 2023", "one-shot post-training weight quantization"),
   cv(V_KCMAP, "compilation into a cheaper representation with a declared query class"),
   cv(V_TVM, "the serving-compiler framing of format and schedule choices")],
  TH("TMT-12", "X-TMT12"),
  "B2.14 quantization / distillation (vary allowed semantic distortion and hardware price); MLX-29 quantization precision threshold",
  "A quantizer is shown exact on an obligation whose required distinctions it provably merges, contradicting TMT-12. X-TMT12 "
  "enumerates the collision structure and the side-channel escape.",
  "PROVED_AT_SCOPE",
  "Report the format AND the evaluation that would reveal the merged distinctions. Average benchmark deltas hide collisions that are "
  "concentrated on rare, high-stakes inputs - which is exactly where TMT-12's no-go bites.",
  "12. Feature atlas - serving and systems / weight quantization (P,S)")

F("TF-075", "Mixed-precision training",
  "Keep an fp32 (or bf16) master copy of the weights, run the forward and backward passes in a low-precision format (fp16/bf16), and "
  "accumulate in a wider format; with fp16, scale the loss by a constant s so that small gradients survive the format's limited "
  "exponent range, then unscale before the update.",
  "PU", "P because it is a numeric-format choice; U because the update law is applied to the master copy with a different noise and "
  "overflow profile than pure low-precision training would have.",
  "The mathematical update law: with a wide master copy and wide accumulation, the computed update approximates the fp32 one to the "
  "accumulation precision.",
  "Bit-exactness and determinism across hardware: reduction order, format and loss scaling all affect the result, so a "
  "'mixed-precision run' is not one reproducible object without those declared.",
  "Low precision halves memory traffic and doubles arithmetic throughput on matched hardware, while the wide master copy prevents the "
  "update from being lost to rounding - the small updates that low precision cannot represent are exactly what accumulate over many "
  "steps.",
  ["ΔB_train", "ΔB_mem", "ΔB_comm", "ΔL_sem"],
  "ΔB_train, ΔB_mem and ΔB_comm all fall substantially; ΔL_sem is intended to be zero and is a bug when it is not (overflow, "
  "underflow or a lost accumulation).",
  "Pure low-precision training with NO master copy and NO wide accumulation at the same format: identical memory traffic and "
  "throughput, and the precision-preservation mechanism removed.",
  "bf16 with its wider exponent removes the need for loss scaling at the cost of mantissa bits; fp8 with per-tensor scaling pushes "
  "the same trade further; stochastic rounding preserves the expected update without a master copy.",
  [tv("Micikevicius, Narang, Alben, Diamos, Elsen, Garcia, Ginsburg, Houston, Kuchaiev, Venkatesh, Wu (2018). Mixed Precision Training, ICLR 2018", "the master-copy plus loss-scaling construction"),
   cv(V_TVM, "the framing of numeric format as a compilation choice with a measurable cost/accuracy frontier"),
   cv(V_COHEN_EOS, "the sensitivity of training stability to effective step size, which precision directly perturbs")],
  TH("TMT-12", "X-TMT12"),
  "B2.20 parallelism/precision repricing; B2.9 normalization (precision axis); MLX-29 quantization precision threshold",
  "Pure low-precision training with no master copy is shown to match mixed precision at matched steps and schedule, which would "
  "remove the lost-update mechanism.",
  "REGISTERED_FOR_EXPERIMENT",
  "Record dtype, accumulation width, loss scale and reduction order in every receipt. A reproducibility claim that omits them is not "
  "checkable, and a quality difference between two 'identical' runs may be entirely numeric.",
  "12. Feature atlas - serving and systems / mixed precision (P,U)")

F("TF-076", "Activation checkpointing / recomputation",
  "Store only a subset of forward activations and recompute the rest during the backward pass. With sqrt(L)-spaced checkpoints, "
  "activation memory falls from Theta(L) to Theta(sqrt(L)) at the cost of one extra forward pass over the recomputed segments. The "
  "gradients are mathematically identical.",
  "PH", "P because it is a memory/compute schedule; H because what is being traded is retained intermediate state.",
  "The gradients, exactly in real arithmetic, and hence the training trajectory up to numeric reassociation. This is TMT-6's "
  "recompute-versus-store trade run in the opposite direction from the KV cache.",
  "Wall-clock cost and numeric bit-identity: roughly 30 percent more compute, and recomputed activations can differ in the last bits "
  "under non-deterministic kernels.",
  "Activation memory, not parameter memory, is usually what bounds trainable depth and batch size. Recomputation converts that "
  "constraint into compute, which is abundant relative to memory on current accelerators.",
  ["ΔB_mem", "ΔB_train"],
  "ΔB_mem falls from Theta(L) to Theta(sqrt(L)); ΔB_train rises by the recomputed fraction; every ΔL_* is zero in exact arithmetic.",
  "Store ALL activations (no checkpointing) at the same batch size where memory allows: identical mathematics, and the "
  "memory/compute trade removed - the control that shows the gradients really are identical.",
  "Reversible layers reconstruct activations from outputs at no memory cost and a structural constraint; CPU offload moves them "
  "rather than recomputing them; a smaller micro-batch with accumulation reduces the same memory differently.",
  [tv("Chen, Xu, Zhang, Guestrin (2016). Training Deep Nets with Sublinear Memory Cost, arXiv:1604.06174", "the sqrt-spacing checkpointing schedule and its cost analysis"),
   cv(V_MICHIE, "the memoize-or-recompute trade in its general form"),
   cv(V_ADAPTON, "demand-driven recomputation with explicit dependency tracking as the general mechanism")],
  TH("TMT-6", "X-TMT6"),
  "B2.20 parallelism/precision repricing (memory/compute axis)",
  "Checkpointed and uncheckpointed training are shown to differ beyond numeric reassociation, which would mean the recomputation is "
  "not reproducing the same forward values (a bug, not a mechanism).",
  "PARENT_THEOREM_UNDER_ASSUMPTIONS",
  "Report the recomputation fraction with the throughput number. A 'this model trains in X GB' claim without the checkpointing policy "
  "is not comparable, and the extra compute is real.",
  "12. Feature atlas - serving and systems / activation checkpointing / recomputation (P,H)")

F("TF-077", "Data parallelism",
  "Replicate the model on N workers, give each a different micro-batch, and all-reduce the gradients before the update: "
  "g = (1/N) sum_i g_i. Communication is Theta(|theta|) per step, independent of batch size. Sharded variants (ZeRO/FSDP) partition "
  "the parameters, gradients and optimizer state across the same N workers to cut per-worker memory.",
  "PR", "P because it is a placement/communication realization; R only in the weak sense that sharding decides which worker holds "
  "which parameter.",
  "The update exactly: the all-reduced gradient equals the gradient of the summed loss, so N-way data parallelism computes the same "
  "step as a single worker with N times the batch.",
  "The effective batch size and hence the trajectory (TF-056), and bit-identity (reduction order varies with the topology).",
  "Data parallelism converts wall-clock into hardware count at a communication cost independent of batch size, so it scales until "
  "the all-reduce time exceeds the compute time - a ratio set entirely by |theta| and the interconnect bandwidth.",
  ["ΔB_train", "ΔB_comm", "ΔB_mem"],
  "ΔB_train (wall clock) falls roughly as 1/N until communication binds; ΔB_comm rises as Theta(|theta|) per step; sharded variants "
  "cut ΔB_mem by N at additional ΔB_comm.",
  "N workers with NO gradient synchronization (independent models, results averaged at the end): identical compute and zero "
  "communication, which isolates the value of the synchronization from the value of the parallel compute.",
  "Gradient accumulation on one worker reaches the same effective batch serially; sharded data parallelism trades memory for "
  "communication; local-SGD/federated averaging synchronizes less often at a trajectory cost.",
  [tv("Rajbhandari, Rasley, Ruwase, He (2020). ZeRO: Memory Optimizations Toward Training Trillion Parameter Models, SC 2020", "the partitioning of parameters, gradients and optimizer state across data-parallel workers"),
   tv("Goyal, Dollar, Girshick, Noordhuis, Wesolowski, Kyrola, Tulloch, Jia, He (2017). Accurate, Large Minibatch SGD, arXiv:1706.02677", "the scaling rule that makes large data-parallel batches trainable"),
   tv("McCandlish, Kaplan, Amodei, OpenAI Dota Team (2018). An Empirical Model of Large-Batch Training, arXiv:1812.06162", "the noise-scale limit on how far this parallelism pays")],
  None, "B2.20 parallelism/precision repricing (same abstract model under substrate graphs with different communication/memory/compute ratios); MLX-40 communication-price phase",
  "The optimal parallelism split is shown to be independent of the interconnect bandwidth and topology, which would contradict the "
  "substrate-dependence claim of section 12 and of gap G-T19.",
  "REGISTERED_FOR_EXPERIMENT",
  "Charge the all-reduce to ΔB_comm and report the interconnect. Throughput numbers from different cluster topologies are not "
  "comparable, and a parallelism 'improvement' is usually a repricing under a different substrate graph, not a model change.",
  "12. Feature atlas - serving and systems / data / tensor / pipeline / sequence / expert parallelism (P,R)")

F("TF-078", "Tensor (intra-layer) parallelism",
  "Split each weight matrix across N devices - column-parallel for the first projection, row-parallel for the second - so each device "
  "computes a slice of every layer. One all-reduce (or reduce-scatter plus all-gather) per parallel block per forward and per "
  "backward pass, with a volume of Theta(batch x seq x d).",
  "PR", "P because it is a placement/communication realization; R because it partitions the computation graph across devices.",
  "The computed function exactly: the concatenated slices reconstruct the full matrix product.",
  "Latency and bandwidth requirements: the per-block all-reduce is on the critical path of every token, so tensor parallelism is "
  "viable only within a high-bandwidth domain (typically one node).",
  "Tensor parallelism makes a layer too large for one device's memory fit, and cuts per-device compute, at the price of a "
  "synchronous collective inside every block. The frontier is set by the ratio of intra-node bandwidth to per-device FLOPs.",
  ["ΔB_mem", "ΔB_comm", "ΔB_serve", "ΔB_train"],
  "ΔB_mem per device falls as 1/N; ΔB_comm rises as Theta(batch x seq x d) per block; ΔB_serve latency falls only while the "
  "collective is cheaper than the saved compute.",
  "Run the same N devices on N INDEPENDENT copies of a 1/N-sized model with no collectives: the aggregate compute and memory are "
  "matched and the single-large-model constraint is removed.",
  "Pipeline parallelism (TF-079) splits by depth instead of by width with a different communication profile; sharded data "
  "parallelism (TF-077) gets the same memory reduction with communication on the parameter rather than the activation axis.",
  [tv("Shoeybi, Patwary, Puri, LeGresley, Casper, Catanzaro (2019). Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism, arXiv:1909.08053", "the column/row-parallel decomposition of the Transformer block"),
   tv("Narayanan, Shoeybi, Casper, LeGresley, Patwary, Korthikanti, Vainbrand, Kashinkunti, Bernauer, Catanzaro, Phanishayee, Zaharia (2021). Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM, SC 2021", "the measured 3D-parallelism frontier across topologies"),
   cv(V_TVM, "placement and schedule as a compilation problem over a substrate graph")],
  TH("TMT-7", "X-TMT7"),
  "B2.20 parallelism/precision repricing; MLX-40 communication-price phase",
  "A parallelism layout is shown optimal across substrate graphs with materially different bandwidth/FLOP ratios, which would close "
  "gap G-T19 against the phase-diagram reading.",
  "REGISTERED_FOR_EXPERIMENT",
  "Report N, the collective volume and the interconnect. Tensor parallelism changes no semantics (TMT-7), so any quality difference "
  "between layouts is a numeric or a bug finding and must be reported as such.",
  "12. Feature atlas - serving and systems / data / tensor / pipeline / sequence / expert parallelism (P,R)")

F("TF-079", "Pipeline parallelism",
  "Partition the L layers into S consecutive stages on S devices and stream micro-batches through them. Communication is only the "
  "boundary activations between adjacent stages (Theta(batch x seq x d) per boundary), but the schedule has a bubble: with M "
  "micro-batches the idle fraction is about (S-1)/(M+S-1).",
  "PR", "P because it is placement and scheduling; R because it decides which stage computes which part of the graph.",
  "The computed function and the gradients exactly, when the schedule is synchronous (all micro-batches of a step complete before the "
  "update).",
  "Device utilization and update semantics: the bubble is real idle time, and ASYNCHRONOUS pipeline schedules change the update law "
  "(stale weights), so they are not semantics-preserving.",
  "Pipelining fits a deep model across devices with the smallest communication volume of any model-parallel scheme, at the cost of a "
  "scheduling bubble that only a large micro-batch count amortizes - which in turn costs activation memory.",
  ["ΔB_mem", "ΔB_comm", "ΔB_train"],
  "ΔB_mem per device falls as 1/S; ΔB_comm is the lowest of the model-parallel family; ΔB_train carries the bubble overhead "
  "(S-1)/(M+S-1).",
  "The same stage partition run SEQUENTIALLY on one device (no pipelining): the same memory profile per stage and zero bubble, "
  "isolating the parallel speedup from the partitioning.",
  "Tensor parallelism (TF-078) splits within layers at much higher communication; interleaved (virtual-stage) schedules cut the "
  "bubble at more communication; ZeRO-style sharding (TF-077) avoids stage partitioning entirely.",
  [tv("Huang, Cheng, Bapna, Firat, Chen, Chen, Lee, Ngiam, Le, Wu, Chen (2019). GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism, NeurIPS 2019", "the micro-batch pipeline schedule and the bubble analysis"),
   tv("Narayanan, Harlap, Phanishayee, Seshadri, Devanur, Ganger, Gibbons, Zaharia (2019). PipeDream: Generalized Pipeline Parallelism for DNN Training, SOSP 2019", "the asynchronous variant whose weight staleness changes the update law"),
   cv(V_BUILD, "staged dependency scheduling as the general frame")],
  TH("TMT-7", "X-TMT7"),
  "B2.20 parallelism/precision repricing; MLX-40 communication-price phase",
  "An asynchronous pipeline schedule is shown to compute the same updates as a synchronous one, which would remove the staleness "
  "distinction this entry rests on.",
  "REGISTERED_FOR_EXPERIMENT",
  "Report S, M and whether the schedule is synchronous. The bubble is real ΔB_train; an asynchronous pipeline is a DIFFERENT update "
  "law and its results are not comparable to a synchronous baseline's.",
  "12. Feature atlas - serving and systems / data / tensor / pipeline / sequence / expert parallelism (P,R)")

F("TF-080", "Sequence / context parallelism",
  "Partition the SEQUENCE axis across devices: each holds a contiguous block of positions, and attention is computed by rotating "
  "key/value blocks around a ring (or by an all-gather) so every query eventually sees every legal key. Activation memory per device "
  "falls as 1/N and the context length becomes bounded by aggregate rather than per-device memory.",
  "PR", "P because it is a placement/communication realization; R because the routing stage is what must be reassembled across the "
  "partition.",
  "The attention result exactly: ring attention's online rescaling is the same tiled computation as TF-073, distributed - so TMT-7 "
  "applies and X-TMT7's exact block-equality check is the local instance of it.",
  "Communication volume and its overlap with compute: the ring must pass Theta(N) key/value blocks per layer, so the scheme is "
  "bandwidth-bound rather than memory-bound.",
  "Long-context training and serving are bounded by activation and cache memory, not by parameters. Splitting the sequence converts "
  "that bound into a bandwidth requirement, which the ring schedule can overlap with the block computation.",
  ["ΔB_mem", "ΔB_comm", "ΔB_train", "ΔB_serve"],
  "ΔB_mem per device falls as 1/N; ΔB_comm rises with the ring volume; ΔB_train and ΔB_serve fall only while the transfer overlaps "
  "the compute.",
  "Split the sequence across devices WITHOUT the ring exchange (each device attends only within its own block): the memory saving is "
  "identical and the global attention is removed - which is exactly a block-sparse mask (TF-019) and shows what the communication buys.",
  "A sliding-window or block-sparse mask (TF-019) obtains the same memory profile by giving up the far edges; sharded KV caches with "
  "an all-gather realize the same partition with different scheduling.",
  [tv("Liu, Zaharia, Abbeel (2024). Ring Attention with Blockwise Transformers for Near-Infinite Context, ICLR 2024", "the ring schedule for exact distributed attention"),
   tv("Korthikanti, Casper, Lym, McAfee, Andersch, Shoeybi, Catanzaro (2023). Reducing Activation Recomputation in Large Transformer Models, MLSys 2023", "sequence parallelism for the non-attention sublayers and its activation-memory analysis"),
   tv("Dao, Fu, Ermon, Rudra, Re (2022). FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness, NeurIPS 2022", "the single-device tiling the distributed schedule generalizes")],
  TH("TMT-7", "X-TMT7"),
  "B2.20 parallelism/precision repricing; B2.11 context vs recurrence vs retrieval (the 'larger window' arm's real cost); MLX-40 communication-price phase",
  "A distributed exact attention schedule is shown to change the computed map, which would contradict TMT-7 (and indicate an "
  "implementation error rather than a mechanism).",
  "REGISTERED_FOR_EXPERIMENT",
  "Long context obtained by sequence parallelism costs bandwidth, not nothing. Report N and the ring volume; a context-length claim "
  "without the substrate it was served on is not a capability claim.",
  "12. Feature atlas - serving and systems / data / tensor / pipeline / sequence / expert parallelism (P,R)")

F("TF-081", "Expert parallelism",
  "Place MoE experts on different devices and route tokens to them with an all-to-all exchange: tokens are dispatched to their "
  "selected experts, computed, and combined back. Communication is Theta(tokens x d x top_k) per MoE layer and is IRREGULAR because "
  "the routing distribution is input-dependent.",
  "PRG", "P because it is placement and communication; R because the routing decision determines the communication pattern; G "
  "because expert placement is an architectural partition of the computation.",
  "The computed function exactly, PROVIDED no token is dropped: with unlimited expert capacity the distributed result equals the "
  "single-device one.",
  "Exactness under capacity limits: when an expert's capacity factor is exceeded, tokens are DROPPED or rerouted, which changes the "
  "computed function - a semantics change disguised as a systems parameter.",
  "Expert parallelism makes total parameter count grow without growing per-token FLOPs, at the price of an all-to-all whose volume "
  "and IMBALANCE are set by the router. Load balancing (TF-084) exists to keep that exchange affordable.",
  ["ΔB_mem", "ΔB_comm", "ΔB_serve", "ΔL_sem"],
  "ΔB_mem per device falls with expert count; ΔB_comm rises as an all-to-all whose cost is set by the worst-loaded expert; ΔL_sem "
  "degrades whenever capacity-induced token dropping occurs.",
  "Route tokens to experts UNIFORMLY AT RANDOM: the all-to-all volume and the compute are matched exactly and the content-dependent "
  "specialization is removed - the decisive control for whether MoE gains come from routing or from parameters.",
  "Dense parallelism over a model with the same total parameters (TF-078) removes the irregular communication at much higher FLOPs; "
  "expert-choice routing inverts the assignment to bound load by construction.",
  [cv(V_SWITCH, "the distributed expert-parallel realization, the capacity factor and token dropping"),
   cv(V_SHAZEER_MOE, "the original sparsely-gated layer and its distributed formulation"),
   cv(V_CLARK_ROUTED, "the scaling laws that make the parameters-versus-FLOPs trade quantitative"),
   cv(V_DEEPSEEKMOE, "fine-grained and shared-expert placement as an alternative partition")],
  None, "B2.20 parallelism/precision repricing; MLX-08 heterogeneity x MoE/modularity; MLX-40 communication-price phase; gap G-T19",
  "MoE gains are reproduced at matched total parameters by a RANDOM router, which would show the mechanism is capacity rather than "
  "content-dependent routing.",
  "REGISTERED_FOR_EXPERIMENT",
  "Report the capacity factor and the measured token-drop rate. A dropped token is a SEMANTIC change, so a throughput number obtained "
  "with dropping is not comparable to an exact one; charge the all-to-all to ΔB_comm.",
  "12. Feature atlas - serving and systems / data / tensor / pipeline / sequence / expert parallelism (P,R)")

F("TF-082", "Continuous batching",
  "A serving scheduler that admits and retires requests at TOKEN granularity rather than at request granularity: finished sequences "
  "leave the batch immediately and waiting ones join, so the batch is re-formed at every decoding step. Combined with paged cache "
  "allocation it keeps the accelerator near peak utilization under heterogeneous request lengths.",
  "PD", "P because it is a scheduling/utilization mechanism; D only in the weak sense that it decides when each request's next token "
  "is produced. It changes no cognitive semantics.",
  "Each request's output exactly: batching composition does not affect any sequence's computation (given correct masking, TF-015).",
  "Per-request latency distribution and fairness: a request's time-to-completion now depends on the other requests present, so "
  "tail-latency claims are not preserved under a different arrival pattern.",
  "Static batching wastes the accelerator whenever requests have different lengths (short requests wait for the longest). "
  "Token-granularity scheduling removes that waste; the gain is proportional to the length heterogeneity of the workload.",
  ["ΔB_serve", "ΔB_mem", "ΔB_comm"],
  "ΔB_serve (throughput per accelerator) rises substantially under heterogeneous lengths and not at all under homogeneous ones; "
  "ΔB_mem is what bounds the achievable batch, which is why paged cache allocation is the enabling mechanism.",
  "Static batching at the SAME average batch size on the same workload: identical model, identical arithmetic, and the scheduling "
  "mechanism removed - which measures exactly the length-heterogeneity waste.",
  "Length-bucketed static batching captures part of the gain without token-granularity scheduling; chunked prefill smooths the "
  "prefill/decode imbalance; disaggregated prefill-and-decode serving splits the two phases onto different hardware.",
  [tv("Yu, Jeong, Kim, Kim, Chun (2022). Orca: A Distributed Serving System for Transformer-Based Generative Models, OSDI 2022", "iteration-level (continuous) scheduling"),
   tv("Kwon, Li, Zhuang, Sheng, Zheng, Yu, Gonzalez, Zhang, Stoica (2023). Efficient Memory Management for Large Language Model Serving with PagedAttention, SOSP 2023", "the paged cache allocation that makes large continuous batches feasible"),
   cv(V_SLEATOR, "the amortized-scheduling frame for online admission decisions")],
  TH("TMT-6", "X-TMT6"),
  "B2.20 parallelism/precision repricing (serving-scheduler axis)",
  "Continuous batching changes any request's output, which would mean the per-request isolation is broken (a bug); or it delivers a "
  "throughput gain on a perfectly homogeneous workload, which would refute the heterogeneity mechanism.",
  "REGISTERED_FOR_EXPERIMENT",
  "Report throughput AND the latency distribution under a declared arrival process. A throughput number under continuous batching "
  "with no workload description is unreproducible, and the gain belongs entirely to ΔB_serve, never to capability.",
  "12. Feature atlas - serving and systems / continuous batching (P,D)")

F("TF-083", "MoE routing",
  "A gate g(x) in R^E scores E experts per token; the top_k experts are selected and their outputs combined with the (renormalized) "
  "gate weights: y = sum_{e in TopK(g(x))} g_e(x) f_e(x). Total parameters scale with E while per-token FLOPs scale with top_k, so "
  "capacity and compute are decoupled.",
  "RGP", "R because it is conditional routing over computations rather than over positions; G because the expert partition is an "
  "architectural split of the function; P because the selection determines the communication pattern (TF-081).",
  "The dense limit: at top_k = E with uniform gates the layer computes a dense mixture, so MoE is a restriction of a dense family "
  "rather than a new kind of computation.",
  "Differentiability and stability of the selection: top-k is discrete, so the router's gradient is a surrogate, and small gate "
  "perturbations flip assignments - which is the mechanism behind routing instability and expert collapse.",
  "Conditional computation pays exactly when the input distribution is HETEROGENEOUS enough that different tokens need different "
  "transformations. This is TMT-3's structure applied to computations instead of edges: a dense layer is the fixed graph that must "
  "cover the union of what all inputs need.",
  ["ΔB_mem", "ΔB_serve", "ΔB_comm", "ΔL_sem", "ΔB_train"],
  "ΔB_mem rises as E (all experts resident) while ΔB_serve per token stays at top_k; ΔB_comm rises with the all-to-all; ΔL_sem "
  "improves with input heterogeneity and not otherwise.",
  "A FROZEN RANDOM router with the same top_k and the same expert count: identical parameters, identical FLOPs, identical "
  "communication, and the learned content-dependent selection removed. TMT-3 predicts the gap is governed by the heterogeneity of "
  "what inputs require.",
  "A dense model with the same total parameters removes the routing at top_k = E cost; hash-based routing fixes the assignment by "
  "token identity; expert-choice routing inverts the selection direction; a dense gated MLP (TF-025) is the fine-grained limit.",
  [cv(V_SHAZEER_MOE, "the sparsely-gated top-k mixture-of-experts layer"),
   cv(V_SWITCH, "the top-1 simplification and its stability analysis"),
   cv(V_JACOBS, "the original adaptive-mixtures-of-experts formulation and the specialization argument"),
   cv(V_CLARK_ROUTED, "the unified scaling laws that quantify the capacity/compute decoupling")],
  TH("TMT-3", "X-TMT3"),
  "B2.3 fixed vs dynamic routing (the same union-vs-mean structure); MLX-08 heterogeneity x MoE/modularity; gap G-T20 MoE specialization/routing-collapse causal law",
  "A learned router is shown to give no advantage over a frozen random router at matched parameters, FLOPs and communication on an "
  "input distribution with deliberately high heterogeneity - the direct falsifier of the conditional-computation reading.",
  "REGISTERED_FOR_EXPERIMENT",
  "Report TOTAL parameters, ACTIVE parameters per token, and the all-to-all volume as three separate numbers. Quoting active "
  "parameters alone makes an MoE look like a small model it is not; quoting total alone makes it look like a compute cost it is not.",
  "12. Feature atlas - serving and systems / load balancing in MoE (P,R,U)")

F("TF-084", "MoE load balancing",
  "An auxiliary loss (and/or a hard capacity factor) that pushes the router toward uniform expert utilization, typically "
  "L_aux = alpha E sum_e f_e p_e where f_e is the fraction of tokens routed to expert e and p_e the mean gate probability. Without it "
  "the router collapses onto a few experts.",
  "PRU", "P because expert imbalance is a communication and utilization problem; R because it constrains the routing distribution; U "
  "because the balancing term is an addition to the update law.",
  "The expert functions themselves: balancing shapes the ASSIGNMENT, not what any expert computes.",
  "The router's freedom to specialize: a strong balancing term forces a token distribution that may not match the genuine "
  "heterogeneity of the data, so 'the router learned the best assignment' is not preserved.",
  "Routing has a rich-get-richer dynamic: an expert that receives more tokens trains faster and attracts more. The auxiliary loss is "
  "a counter-pressure whose coefficient trades specialization against balance - and hence against the all-to-all's worst-case cost.",
  ["ΔB_comm", "ΔB_serve", "ΔL_sem", "ΔB_train"],
  "ΔB_comm and ΔB_serve fall with balance (the all-to-all is bounded by the busiest expert); ΔL_sem can degrade if the balance "
  "pressure overrides genuine heterogeneity; ΔB_train falls by avoiding collapsed, undertrained experts.",
  "Enforce the identical utilization distribution by a FIXED token-hash assignment rather than by pressuring a learned router: "
  "balance is perfect by construction and the learned selection is removed, which separates 'balanced' from 'balanced AND chosen'.",
  "Expert-choice routing (each expert selects its top tokens) makes balance structural with no auxiliary loss; a bias-adjustment "
  "scheme corrects utilization without adding a loss term; a hard capacity factor enforces balance by dropping (at a semantic cost, "
  "TF-081).",
  [cv(V_SWITCH, "the auxiliary load-balancing loss in the form given and the capacity factor"),
   cv(V_SHAZEER_MOE, "the importance/load losses and the original collapse diagnosis"),
   cv(V_DEEPSEEKMOE, "shared and fine-grained experts as a structural alternative to pure balancing pressure"),
   cv(V_KRAJEWSKI, "the fine-grained MoE scaling laws in which granularity and balance interact")],
  None, "MLX-08 heterogeneity x MoE/modularity; gap G-T20 MoE specialization/routing-collapse causal law; B2.20 (communication axis)",
  "Routers are shown not to collapse without a balancing term at any expert count, which would remove the rich-get-richer mechanism "
  "and make the auxiliary loss pure specialization damage.",
  "REGISTERED_FOR_EXPERIMENT",
  "Report alpha, the measured utilization distribution and the token-drop rate. A balancing coefficient tuned per arm is a hidden "
  "search (ΔB_search), and an unbalanced arm's throughput is not comparable to a balanced one's.",
  "12. Feature atlas - serving and systems / load balancing in MoE (P,R,U)")


# ======================================================================================================================
# Build
# ======================================================================================================================

GROUPS = [("A", "Interface and input representation", "TF-001", "TF-009"),
          ("B", "Attention and routing", "TF-010", "TF-021"),
          ("C", "Local transforms / MLP", "TF-022", "TF-025"),
          ("D", "Residual stream, normalization, initialization, regularization", "TF-026", "TF-034"),
          ("E", "Output map and decoding", "TF-035", "TF-043"),
          ("F", "Memory, history, retrieval, tools", "TF-044", "TF-051"),
          ("G", "Autoregressive objective and training protocol", "TF-052", "TF-061"),
          ("H", "Adaptation and alignment", "TF-062", "TF-072"),
          ("I", "Serving and systems", "TF-073", "TF-084")]

NOT_EVIDENCE = ("A TYPED LOCATION IS NOT EVIDENCE. Assigning a feature a GMI type, a mechanism hypothesis and a resource-effect "
                "direction records where the feature LIVES in the calculus and what would have to be measured; it establishes nothing "
                "about any trained neural network. The only fields that carry epistemic weight are `evidence_status` and the "
                "`formal_theorem` receipt reference behind it, and every X-TMT receipt check is a MATHEMATICAL IMPLEMENTATION CHECK "
                "on a finite enumerated scope -- not neural evidence. No entry in this registry claims that an LLM phenomenon is "
                "explained by its typed location.")


def build():
    registry = {
        "schema": "GMITransformerMicrofeatureRegistryV1",
        "status": "MACHINE-READABLE MICROFEATURE ATLAS -- TYPED LOCATIONS PLUS CLAIM LEVELS; NOT NEURAL EVIDENCE",
        "status_date": "2026-09-12",
        "issue": [377, 422],
        "sources": {
            "calculus": "GMI_NEURAL_LLM_TRANSFORMER_MICROFEATURE_CALCULUS_V1.md (section 1 acceptance fields; type alphabet; Delta_f)",
            "theorems": "GMI_TRANSFORMER_MICROFEATURE_THEOREMS_V1.md (TMT-1..TMT-15)",
            "receipt": "GMI_TRANSFORMER_MICROFEATURE_EXACT_RECEIPT_V1.json (X-TMT1..X-TMT15, executed)",
            "experiments": "GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md stage B2 (B2.1..B2.20); GMI_ML_THEORY_EXPERIMENT_MATRIX_V1.md (MLX-00..52)",
            "claim_levels": "GMI_RECURSIVE_THEORY_HARDENING_FIXED_POINT_V1.md section 3",
            "literature": "GMI_PARENT_LITERATURE_LEDGER_V2.json (127 verified works, 16 areas)",
            "executed_predictions": "REVIVAL_LEDGER_TF.jsonl (RV-377-055 KV cache, RV-377-056 routing)",
        },
        "not_evidence": NOT_EVIDENCE,
        "type_alphabet": TYPE_ALPHABET,
        "effect_vector": DELTA_F,
        "claim_levels": CLAIM_LEVELS,
        "tiers": TIERS,
        "evidence_status_rule": EVIDENCE_RULE,
        "required_fields": ["id", "name", "exact_definition", "gmi_type", "gmi_type_note", "semantic_invariance",
                            "mechanism_hypothesis", "resource_effect", "negative_twin", "implementation_equivalent_alternative",
                            "parent_literature", "formal_theorem", "experiment", "kill_condition", "evidence_status",
                            "hidden_cost_rule", "calculus_section"],
        "groups": [{"group": g, "title": t, "first": a, "last": b} for g, t, a, b in GROUPS],
        "n_features": len(FEATURES),
        "counts_by_evidence_status": {},
        "counts_by_type": {},
        "features": FEATURES,
    }
    for f in FEATURES:
        registry["counts_by_evidence_status"][f["evidence_status"]] = registry["counts_by_evidence_status"].get(f["evidence_status"], 0) + 1
        for t in f["gmi_type"]:
            registry["counts_by_type"][t] = registry["counts_by_type"].get(t, 0) + 1
    registry["registry_sha256"] = sha256_of({k: v for k, v in registry.items() if k != "registry_sha256"})
    return registry


def render_md(reg):
    L = []
    A = L.append
    A("# GMI Transformer Microfeature Registry v1")
    A("")
    A("Status: **" + reg["status"] + "**")
    A("")
    A("Status date: " + reg["status_date"] + ".  Generated by `gmi_microscope/registry.py`; validated by `gmi_microscope/registry_check.py`.")
    A("")
    A("Machine-readable source: `GMI_TRANSFORMER_MICROFEATURE_REGISTRY_V1.json` (sha256 `" + reg["registry_sha256"][:16] + "...`).")
    A("")
    A("---")
    A("")
    A("## 0. A typed location is not evidence")
    A("")
    A("> " + NOT_EVIDENCE.replace("\n", " "))
    A("")
    A("Concretely: `gmi_type`, `gmi_type_note`, `mechanism_hypothesis` and `resource_effect` are a LOCATION and a PREDICTION SHAPE. "
      "They say where a feature lives in `GMI_NEURAL_LLM_TRANSFORMER_MICROFEATURE_CALCULUS_V1.md` and what an intervention would have "
      "to move. They are not a result, and they must never be cited as one. In particular:")
    A("")
    A("```text")
    A("PROVED_AT_SCOPE        = an executed X-TMT check verifies the statement on a finite enumerated scope.")
    A("                         The check is MATHEMATICAL. It says nothing about a trained network.")
    A("REGISTERED_FOR_EXPERIMENT = a B2.x / MLX row exists. Nothing has been measured yet.")
    A("OPEN_NONBLOCKING       = typed, killable, and undecided.")
    A("```")
    A("")
    A("No entry here claims that an LLM phenomenon is EXPLAINED by its typed location.")
    A("")
    A("---")
    A("")
    A("## 1. Counts by evidence status")
    A("")
    A("| evidence status | count | meaning |")
    A("|---|---:|---|")
    order = [s for s in CLAIM_LEVELS if s in reg["counts_by_evidence_status"]] + \
            sorted(s for s in reg["counts_by_evidence_status"] if s not in CLAIM_LEVELS)
    for s in order:
        A("| `%s` | %d | %s |" % (s, reg["counts_by_evidence_status"][s], EVIDENCE_RULE.get(s, "").split(";")[0]))
    A("| **total** | **%d** | |" % reg["n_features"])
    A("")
    A("Counts by GMI type letter (an entry may carry several):")
    A("")
    A("| type | " + " | ".join(sorted(reg["counts_by_type"])) + " |")
    A("|---|" + "---|" * len(reg["counts_by_type"]))
    A("| entries | " + " | ".join(str(reg["counts_by_type"][t]) for t in sorted(reg["counts_by_type"])) + " |")
    A("")
    A("Type alphabet: " + "; ".join("`%s` %s" % (k, v) for k, v in TYPE_ALPHABET.items()) + ".")
    A("")
    A("Effect vector `Delta_f` = (" + ", ".join(DELTA_F) + ").")
    A("")
    A("---")
    A("")
    A("## 2. Registry")
    A("")
    byid = {f["id"]: f for f in reg["features"]}
    for g, title, a, b in GROUPS:
        A("### %s. %s (`%s`-`%s`)" % (g, title, a, b))
        A("")
        A("| id | name | type | theorem | experiment | evidence status |")
        A("|---|---|---|---|---|---|")
        for f in reg["features"]:
            if not (a <= f["id"] <= b):
                continue
            th = f["formal_theorem"]
            thtxt = "-" if th is None else "%s / %s" % (th["tmt"], th["receipt_check"])
            exp = f["experiment"] or "none registered"
            if len(exp) > 62:
                exp = exp[:59].rstrip() + "..."
            A("| `%s` | %s | `%s` | %s | %s | `%s` |" % (f["id"], f["name"], "".join(f["gmi_type"]), thtxt, exp, f["evidence_status"]))
        A("")
    A("---")
    A("")
    A("## 3. Entries with an executed receipt check")
    A("")
    A("These are the only entries whose central statement is settled inside this programme, and they are settled MATHEMATICALLY:")
    A("")
    A("| id | name | check | what the check actually establishes |")
    A("|---|---|---|---|")
    for f in reg["features"]:
        if f["evidence_status"] == "PROVED_AT_SCOPE" and f["formal_theorem"]:
            A("| `%s` | %s | `%s` | %s |" % (f["id"], f["name"], f["formal_theorem"]["receipt_check"],
                                             f["semantic_invariance"]["preserved"].split(".")[0]))
    A("")
    A("Every row above is `MATH_IMPLEMENTATION_CHECK__NOT_EMPIRICAL_NEURAL_EVIDENCE`. Section 17 of "
      "`GMI_TRANSFORMER_MICROFEATURE_THEOREMS_V1.md` lists what remains empirical, and none of it is touched by these rows.")
    A("")
    A("---")
    A("")
    A("## 4. Full entries")
    A("")
    for f in reg["features"]:
        A("### %s %s" % (f["id"], f["name"]))
        A("")
        A("- **exact definition** — " + f["exact_definition"])
        A("- **GMI type** — `%s` (%s)" % ("".join(f["gmi_type"]), f["gmi_type_note"]))
        A("- **semantic invariance** — preserved: " + f["semantic_invariance"]["preserved"])
        A("- **semantic invariance** — NOT preserved: " + f["semantic_invariance"]["not_preserved"])
        A("- **mechanism hypothesis** — " + f["mechanism_hypothesis"])
        A("- **resource effect** — `%s`: %s" % (", ".join(f["resource_effect"]["components"]), f["resource_effect"]["direction"]))
        A("- **negative twin** — " + f["negative_twin"])
        A("- **implementation-equivalent alternative** — " + f["implementation_equivalent_alternative"])
        A("- **parent literature** — " + "; ".join("%s [%s] (owns: %s)" % (p["citation"], "verified" if p["citation_status"].startswith("verified") else "to_verify", p["owns"]) for p in f["parent_literature"]))
        th = f["formal_theorem"]
        A("- **formal theorem** — " + ("none" if th is None else "%s, receipt check `%s` (%s)" % (th["tmt"], th["receipt_check"], th["check_kind"])))
        A("- **experiment** — " + f["experiment"])
        A("- **kill condition** — " + f["kill_condition"])
        A("- **evidence status** — `%s`" % f["evidence_status"])
        A("- **hidden-cost rule** — " + f["hidden_cost_rule"])
        A("- **calculus section** — " + f["calculus_section"])
        A("")
    A("---")
    A("")
    A("## 5. Claim boundary")
    A("")
    A("This file supports:")
    A("")
    A("```text")
    A("every listed neural / LLM / Transformer feature has a typed GMI location, a matched negative twin,")
    A("a hidden-cost metering rule, a kill condition and exactly one claim level;")
    A("%d of them have an executed exact receipt check behind their central statement." % reg["counts_by_evidence_status"].get("PROVED_AT_SCOPE", 0))
    A("```")
    A("")
    A("It does **not** support:")
    A("")
    A("```text")
    A("that any of these features is explained;")
    A("that any LLM behaviour is predicted by its typed location;")
    A("that the resource-effect directions have been measured;")
    A("that the exact receipt checks are evidence about trained networks.")
    A("```")
    return "\n".join(L) + "\n"


def main():
    reg = build()
    json.dump(reg, open(JSON_PATH, "w"), indent=1, sort_keys=True, ensure_ascii=False)
    open(MD_PATH, "w").write(render_md(reg))
    return reg


if __name__ == "__main__":
    r = main()
    print("features:", r["n_features"], "sha:", r["registry_sha256"][:16])
    for k, v in sorted(r["counts_by_evidence_status"].items(), key=lambda kv: -kv[1]):
        print("  %-38s %d" % (k, v))

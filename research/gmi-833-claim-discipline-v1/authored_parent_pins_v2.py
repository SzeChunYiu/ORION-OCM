#!/usr/bin/env python3
"""Authored v2 registrations for the 8 REGISTERED_GAP slots (SUCCESSOR_TRANCHE_V2.md).

Per-slot terminal states (science bar, parent-subtraction doctrine):
  - PINNED_AT_SCOPE: strongest parent(s) identified at exact formal scope, with
    internal file:line citations and/or precise external references; every
    external reference was verified this tranche (verification record in
    VERIFICATIONS); the delta of our object vs the parent is stated.
  - RESOLVED_BY_SUPPORT_LOCATION / RESOLVED_BY_DERIVATION: the two status-marker
    slots resolved as claims (support located / observable derived); no
    NOT_APPLICABLE reclassification was needed.

No parent is pinned without verification; unverifiable parents would be
PARENT_UNVERIFIED with checks recorded (none occurred). Source rows in other
packages are never edited (the TF-055 registry author-list defect is recorded
here and in the analysis doc; the source stays untouched).
"""

# Web verifications performed this tranche (2026-09-16, macOS Mac mini, WebSearch/WebFetch):
VERIFICATIONS = {
    "randomized_convexification": (
        "Wald/Blackwell-Girshick randomized-decision convexification: statement verified via "
        "Warwick APTS Statistical Inference notes ('the risk set is the convex hull of the rows "
        "of the risk matrix R'), Wikipedia 'Randomised decision rule' ('the risk set is the "
        "convex hull of the risks' of the deterministic rules), and G. Schwarz, Ways of "
        "Randomizing and the Problem of Their Equivalence (1974), Springer DOI "
        "10.1007/BF02756820, which cites Blackwell & Girshick Sections 7.2 and 8.3 for "
        "randomized decision functions/risk sets. The primary books were NOT read (paywalled); "
        "section numbers are secondhand via Schwarz (1974). Verification scope recorded."
    ),
    "pointwise_bayes": (
        "Pointwise Bayes-action characterization ('a rule is Bayes iff per observation cell the "
        "action minimizes posterior expected loss'): verified via CMU 10-624 Lecture 3 notes, "
        "Georgia Tech ISyE Bayesian handout, Wikipedia 'Bayes estimator' (which cites Ferguson "
        "1967 and Berger 1985 as the standard treatments). Ferguson ch. 1-2 / Berger ch. 4 cited "
        "at book+chapter level; exact theorem numbers not read from the primary texts. "
        "Verification scope recorded."
    ),
    "doremi": (
        "DoReMi VERIFIED: Sang Michael Xie, Shibani Santurkar, Tengyu Ma, Percy Liang, 'DoReMi: "
        "Optimizing Data Mixtures Speeds Up Language Model Pretraining', NeurIPS 2023, "
        "arXiv:2305.10429 (group DRO over domain weights then resampled pretraining). The "
        "registry row's author list ('Xie, Pham, Dong, Du, Liu, Lu, Liang, Le, Ma, Yu') is "
        "INACCURATE - the row's own [to_verify] flag was correct. Correction registered here; "
        "source row untouched."
    ),
    "chinchilla": (
        "Chinchilla VERIFIED: Jordan Hoffmann, Sebastian Borgeaud, Arthur Mensch, et al. (22 "
        "authors, DeepMind), 'Training Compute-Optimal Large Language Models', NeurIPS 2022, "
        "arXiv:2203.15556 (compute-optimal token/parameter scaling). Registry row's author "
        "list matches."
    ),
    "goldblum_nfl": (
        "Goldblum et al. VERIFIED: Micah Goldblum, Marc Finzi, Keefer Rowan, Andrew Gordon "
        "Wilson, 'The No Free Lunch Theorem, Kolmogorov Complexity, and the Role of Inductive "
        "Biases in Machine Learning', arXiv:2304.05366, NeurIPS 2023. Registry row matches."
    ),
}

# v1 gap reasons (drift guard: each pin must replace exactly this reason)
V1_REASON = {
    "CD-1": "no parent literature registered for this ledger row; registry section-H does not key CLAIM_LEDGER_V1.md",
    "CD-2": "no parent literature registered for this ledger row; registry section-H does not key CLAIM_LEDGER_V1.md",
    "FORMAL_DERIVATION_INTEGRATION_V1": "gap-queue integration row; no parent literature keyed",
    "GRAND_GMI_EMPIRICAL_PROGRAMME_COMPLETE": "programme-level closure verdict row; no theorem parent exists to register",
    "READY_FORMAL": "readiness status definition row; no parent literature keyed in the audit doc",
    "TF-055": 'registry row: theorem column is "-"; only the MLX-13 experiment row exists (verified by extraction pass)',
    "V0.2": "document preamble scoping sentence; invokes no premises (rescore v2: UNSCORED_WITH_REASON / SUPPORT_NOT_LOCATED - the census object is a preamble, not a claim statement)",
    "NON-FINAL": "status-marker row: the sheet asserts its own non-finality with a per-sentence claim ceiling; no claim-specific observable exists without new analysis",
}

PINS_V2 = [
    {
        "result_id": "GMI833_V2_LEGACY_023_CD-1",
        "object_id": "CD-1",
        "field": "strongest_parents",
        "outcome": "PINNED_AT_SCOPE",
        "status": "DERIVED",
        "v1_reason": V1_REASON["CD-1"],
        "content": [
            "gmi-grand-unification-v1/COMMON_DECODER_CORRECTION_V1.md:L22: internal anchor - 'The full randomized common-decoder risk set is the convex hull of the deterministic risk profiles, using a constructive mixture over decoder tables.'",
            "external strongest parent at CD-1's exact scope: the randomized-decision-function convexification of classical statistical decision theory - for a finite state set and finite action set, the risk vectors attainable by randomized decision rules are exactly the convex hull of the risk vectors of the deterministic rules. Canonical locus: A. Wald, Statistical Decision Functions (Wiley, 1950); D. Blackwell and M. A. Girshick, Theory of Games and Statistical Decisions (Wiley, 1954), randomized decision functions and risk sets (Sections 7.2 and 8.3 cited for this material by G. Schwarz, Ways of Randomizing and the Problem of Their Equivalence, 1974, Springer DOI 10.1007/BF02756820).",
            "delta vs parent: zero mathematical delta at CD-1's own statement level - CD-1 instantiates the parent exactly (finite ecology set E = state set; decoder tables = deterministic decision rules; mixture over tables = randomization). The correction tranche's novel content is CD-2's simultaneous-attainment condition and CD-4's counterexample, not the convexity itself. The falsified predecessor use (SEMANTIC_CUT_THEOREM_V1.md sections 6-8; separately-optimized ecology risks read as one attainable profile, refuted at COMMON_DECODER_CORRECTION_V1.md:L7-L16) is precisely the misuse the parent frame rules out.",
        ],
        "basis": "parent identification at exact scope; external statement verified this tranche (see VERIFICATIONS['randomized_convexification']); primary texts not read (paywalled), secondhand section numbers labelled as such - the pin claims the statement (verified) and the canonical locus, not an unread passage.",
    },
    {
        "result_id": "GMI833_V2_LEGACY_024_CD-2",
        "object_id": "CD-2",
        "field": "strongest_parents",
        "outcome": "PINNED_AT_SCOPE",
        "status": "DERIVED",
        "v1_reason": V1_REASON["CD-2"],
        "content": [
            "gmi-grand-unification-v1/CLAIM_LEDGER_V1.md:L10: internal strongest parent - GG4: 'For a fixed stochastic ecology coordinate and cut channel, optimal expected loss is posterior pointwise decision risk.' (ledger row explicitly typed 'THEOREM / parent specialization', finite bounded-loss case). CD-2 generalizes GG4's single fixed-ecology pointwise risk to simultaneous multi-ecology envelope attainment.",
            "external parent at GG4's scope (hence CD-2's single-ecology face): the pointwise Bayes-action characterization of classical Bayesian decision theory - a decision rule is Bayes iff, for each observation cell, the chosen action minimizes the posterior expected loss there. Canonical treatments: T. S. Ferguson, Mathematical Statistics: A Decision Theoretic Approach (Academic Press, 1967), ch. 1-2; J. O. Berger, Statistical Decision Theory and Bayesian Analysis (Springer, 2nd ed. 1985), ch. 4.",
            "delta vs parents: neither GG4 nor the classical pointwise-Bayes lemma addresses SIMULTANEOUS attainment across several states. CD-2's own content is the intersection condition - a single common decoder attains the separate-ecology oracle envelope iff the per-cell argmin sets intersect across all ecologies - plus the zero-probability-cell exemption (cells impossible under one ecology impose no constraint from it). CD-4 (CLAIM_LEDGER_V1.md:L33) exhibits instances where the intersection is empty, so the condition is non-vacuous.",
        ],
        "basis": "parent identification at exact scope; external statement verified this tranche (see VERIFICATIONS['pointwise_bayes']); books cited at chapter level only, theorem numbers not read from primary texts.",
    },
    {
        "result_id": "GMI833_V2_LEGACY_031_FORMAL_DERIVATION_INTEGR",
        "object_id": "FORMAL_DERIVATION_INTEGRATION_V1",
        "field": "strongest_parents",
        "outcome": "PINNED_AT_SCOPE",
        "status": "EXTRACTED",
        "v1_reason": V1_REASON["FORMAL_DERIVATION_INTEGRATION_V1"],
        "content": [
            "gmi-formal-derivation-v1/CORE.md:L23: the proof-route integration table (AXIOMS/ADAPTIVE/STATE-DISCOVERY/COMPOSITION/REPRESENTATION/REALIZATIONS/ARCHITECTURE/LEARNING/OPTIMIZATION/LEARNER/MEMORY/CAUSALITY/AGENCY-RESOURCES) - the module theorems this row aggregates; 'Parent mechanisms are cited beside their derivations' (gmi-formal-derivation-v1/CORE.md:L46)",
            "gmi-formal-derivation-v1/STATE-DISCOVERY.md:L44: SD1 theorem - 'The retained machine is behaviorally equivalent to the unknown machine from corresponding roots on all finite and infinite input streams' (acquisition of an unknown bounded transducer at distinguishing depth 2m-1; stopped mass-floor support recovery)",
            "gmi-formal-derivation-v1/ADAPTIVE.md:L21: A2 global confidence theorem (one global filtration, predictable birth/visit choices, conditional evidence contracts)",
            "gmi-formal-derivation-v1/COMPOSITION.md:L46: CMP2 assume-guarantee safety theorem - 'Pr(intersect_{t>=0} I_t) >= 1-delta, without independence' (countably many calls)",
            "gmi-formal-derivation-v1/REPRESENTATION.md:L16: REP1 constructive deterministic residual quotient theorem (classes Q = A*/~ with root [epsilon])",
            "gmi-formal-derivation-v1/LEARNING.md:L41: L2 - finite/countable learning with one explicit generalization certificate",
            "gmi-formal-derivation-v1/LEARNER.md:L74: C2 - certificate and full-lifecycle forecast bound for the charged certified executable-structure learner",
            "gmi-grand-unification-v1/FORMAL_DERIVATION_INTEGRATION_V1.md:L60: GAC5 correction (GAC_WELL_FOUNDED_COMPOSITION_CORRECTION_V1.md) repairs the active theorem's founded-dependency premise without changing the frozen formal unit",
            "gmi-grand-unification-v1/FORMAL_DERIVATION_INTEGRATION_V1.md:L64: learning/memory correction (LEARNING_MEMORY_INTEGRATION_CORRECTION_V1.md) reconciles the parallel PR568 contribution under the same fixed-class, one-sided-regret, complete-view premises",
        ],
        "basis": "all parents internal and cited at file:line. The integration row's own claim is route coherence plus custody of the 32-file unit (byte/hash-verified wrapper, claim ceiling 'no proof-assistant or empirical-completion claim', FORMAL_DERIVATION_INTEGRATION_V1.md:L42-L57); its strongest parents are the module theorems it aggregates. Each module carries its own external classical anchors beside its derivation (CORE.md:L46) - those are one level down and are NOT restated here (they are registered in the modules' own discipline rows, not this row's).",
    },
    {
        "result_id": "GMI833_V2_LEGACY_048_GRAND_GMI_EMPIRICAL_PROG",
        "object_id": "GRAND_GMI_EMPIRICAL_PROGRAMME_COMPLETE",
        "field": "strongest_parents",
        "outcome": "PINNED_AT_SCOPE",
        "status": "EXTRACTED",
        "v1_reason": V1_REASON["GRAND_GMI_EMPIRICAL_PROGRAMME_COMPLETE"],
        "content": [
            "gmi-grand-unification-v1/MASTER_CLOSURE_LEDGER_V1.md:L62: parent rule 1 (schema-coverage convention) - 'That convention does not establish completeness of the possible sectors, the correctness of all theorem statements, or the absence of gaps.'",
            "gmi-grand-unification-v1/RECURSIVE_GAP_AUDIT_20260913.md:L371: parent rule 2 (recursive reopen rule) - 'Reopen an affected claim when a counterexample satisfies its premises, a required comparison/selector/realization lacks a proof, a new information pattern invalidates a transported bound, a source or receipt changes without review, an instrument fails validation, or new data invalidate a registered coverage/model assumption.'",
            "gmi-grand-unification-v1/MASTER_CLOSURE_LEDGER_V1.md:L68: parent rule 3 (the section-7 empirical programme enumeration: richer-language kappa/tau spectra, measured hardware/quantum instantiation, resource-conditioned phase transitions, preregistered empty regions, independent replication and modern-scale tests) - the measurements whose absence the verdict registers",
        ],
        "basis": "verdict row (value FALSE at MASTER_CLOSURE_LEDGER_V1.md:L86): its strongest parents are the governing rules it applies, not theorems it specializes. The verdict applies rule 1 + rule 2 to the corpus state (finite formal repairs supply none of rule 3's measurements; counterexamples can reopen theorem claims) - exactly the supports already registered in this object's v1 assumptions DERIVED row (same convention and reopen rule); no theorem parent exists or is claimed, which the pin now states with citations instead of leaving as a gap.",
    },
    {
        "result_id": "GMI833_V2_LEGACY_057_READY_FORMAL",
        "object_id": "READY_FORMAL",
        "field": "strongest_parents",
        "outcome": "PINNED_AT_SCOPE",
        "status": "EXTRACTED",
        "v1_reason": V1_REASON["READY_FORMAL"],
        "content": [
            "gmi-grand-unification-v1/NN_NONNN_EMPIRICAL_EVIDENCE_READINESS_AUDIT_V1.md:L26: parent definition (audit-rule section 2) - 'READY_FORMAL: the theorem/protocol needed to consume evidence exists'",
            "gmi-grand-unification-v1/NN_NONNN_EMPIRICAL_EVIDENCE_READINESS_AUDIT_V1.md:L50: the formal layers the family-definitions assignment rests on - 'The NN/non-NN derivation certificate, realization compilation layer and intra-family architecture-refinement layer provide the operational distinction needed to register neural, non-neural and hybrid candidates without making the family name fundamental.'",
            "gmi-grand-unification-v1/NN_NONNN_DERIVATION_CERTIFICATE_AND_BOUNDARY_THEOREM_V1.md:L66: DC-1 certificate sufficiency theorem - the NN/non-NN derivation certificate the status consumes (its registry discipline row: gmi-grand-unification-v1/FALSIFIABILITY_REGISTRY_V1.md:L148)",
            "gmi-grand-unification-v1/NN_NONNN_EMPIRICAL_EVIDENCE_READINESS_AUDIT_V1.md:L171: scope bound the definition carries - 'UNDECIDED_FROM_CURRENT_EVIDENCE is the only valid real-world NN/non-NN family terminal at the audited repository scope' (a READY_FORMAL field cannot emit a family verdict alone; audit matrix marks all five READY_FORMAL rows 'not by itself')",
        ],
        "basis": "status-definition row: strongest parents = the defining audit rule + the named formal layers the assignment rests on (derivation certificate, realization compilation, architecture refinement) + the verdict-gate bound. Delta: the row TYPES formal readiness; it specializes no theorem and asserts no empirical content - the pin registers the rule and layers it rests on at their stated scope.",
    },
    {
        "result_id": "GMI833_V2_LEGACY_169_TF-055",
        "object_id": "TF-055",
        "field": "strongest_parents",
        "outcome": "PINNED_AT_SCOPE",
        "status": "EXTRACTED",
        "v1_reason": V1_REASON["TF-055"],
        "content": [
            "machine-intelligence-morphogenesis-v1/GMI_TRANSFORMER_MICROFEATURE_REGISTRY_V1.md:L1215: registry parent-literature field (verbatim, source-row tags kept): DoReMi [to_verify] owns 'an explicit optimization over mixture weights'; Hoffmann et al. 2022 [verified] owns 'the token-budget frame in which mixture weights are an allocation'; Goldblum et al. 2023 [verified] owns 'the statement that no data distribution is universally best without an assumption about the target'",
            "machine-intelligence-morphogenesis-v1/GMI_TRANSFORMER_MICROFEATURE_REGISTRY_V1.md:L1216: 'formal theorem - none' (the registry's own registration that no theorem parent exists for this row)",
            "machine-intelligence-morphogenesis-v1/GMI_TRANSFORMER_MICROFEATURE_REGISTRY_V1.md:L15: ceiling on what the pin means - gmi_type/mechanism_hypothesis/resource_effect are 'a LOCATION and a PREDICTION SHAPE... not a result, and they must never be cited as one': the pinned parents own TF-055's prediction shape (mixture weights allocate finite capacity/steps; no universal mixture exists), not any measured or proved result about trained networks",
        ],
        "basis": "externals verified this tranche (VERIFICATIONS): DoReMi = Xie, Santurkar, Ma, Liang, NeurIPS 2023, arXiv:2305.10429 (registry author list inaccurate; [to_verify] flag was correct - correction recorded here, source untouched); Chinchilla = Hoffmann, Borgeaud, Mensch et al. (22 authors, DeepMind), NeurIPS 2022, arXiv:2203.15556; Goldblum, Finzi, Rowan, Wilson, arXiv:2304.05366, NeurIPS 2023. The v1 table-row pass keyed only the registry TABLE row (theorem column '-'); the registry's per-feature detail section carries the parent-literature field this pin extracts.",
    },
    {
        "result_id": "GMI833_V2_LEGACY_001_V0.2",
        "object_id": "V0.2",
        "field": "assumptions",
        "outcome": "RESOLVED_BY_SUPPORT_LOCATION",
        "status": "EXTRACTED",
        "v1_reason": V1_REASON["V0.2"],
        "content": [
            "gmi-adaptive-row-confidence-v1/raw/OCM_FOUNDATIONS_CLOSURE_V1.md:L106: the bounded reference model the located support invokes - 'assume exactly one acceptable repair among n candidates, probabilities p_i, known deterministic test costs c_i>0, no shared test work, and a failed test revealing only that this candidate is not the correct one. The successful repair must be tested before use.'",
            "gmi-adaptive-row-confidence-v1/raw/OCM_FOUNDATIONS_CLOSURE_V1.md:L104: the coordinate-defining premise - the V0.2 quantity chi = 2^H(R|e) is a diversity descriptor under a fixed conditional repair law R|e; guesswork and Shannon entropy are different objects ([R5] Christiansen and Duffy, Guesswork, large deviations and Shannon entropy, IEEE Trans. IT 59(2):796-802, 2013, DOI 10.1109/TIT.2012.2219036)",
            "gmi-adaptive-row-confidence-v1/raw/OCM_FOUNDATIONS_CLOSURE_V1.md:L122: the boundary premise - multiple acceptable repairs, information-rich failures, state-dependent costs, correlated evaluations, side effects and shared computation require a richer search model; chi is not a sufficient statistic for evolvability",
        ],
        "basis": "rescore-v2 SUPPORT_NOT_LOCATED upgraded: the L7 classification claim ('supplies useful research coordinates, not an unconditional efficiency theorem') has locatable support in the same document, section 5 FC-T4 - the cost-aware ordering theorem (L106-L112) proves the coordinate reading; the entropy-vs-guesswork counterexample (L116-L120) refutes the efficiency-theorem reading. The premises that support actually invokes are exactly the L106 bounded model plus the L104 descriptor definition, bounded by L122. The object IS a claim with located support, so no NOT_APPLICABLE reclassification is needed.",
    },
    {
        "result_id": "GMI833_V2_LEGACY_126_NON-FINAL",
        "object_id": "NON-FINAL",
        "field": "falsifiers",
        "outcome": "RESOLVED_BY_DERIVATION",
        "status": "DERIVED",
        "v1_reason": V1_REASON["NON-FINAL"],
        "content": [
            "a sentence of GMI_NOTE_QUESTIONS_STATUS_V1.md that carries no claim ceiling - i.e., asserts a result beyond its registered ceiling (for example a universal-law statement without scope), refuting the marker's 'Every sentence carries a claim ceiling' assertion; observable by a per-sentence ceiling audit of the sheet (the per-question ceiling terminals, e.g. GMI_NOTE_QUESTIONS_STATUS_V1.md:L33 and L58, are the registered per-sentence ceilings the audit compares against)",
            "a proof of a universal law inside the sheet itself - any sentence that IS a proof of a universal law refutes the marker's second assertion 'nothing below is a proof of a universal law' (GMI_NOTE_QUESTIONS_STATUS_V1.md:L3)",
        ],
        "basis": "derived from the marker's own statement: the status line asserts two document-universals over a finite sheet ('every sentence', 'nothing below'), whose negations are direct document-internal observables. Scope note: a future terminal flip of the four questions (e.g. PROSPECTIVE_CROSS_PARADIGM_BIAS_RESOURCE_LAW_NOT_YET_ESTABLISHED -> established) would make a SUCCESSOR sheet final without falsifying this marker - the two observables above are the refuting ones for this object.",
    },
]

OUTCOMES = [
    {"object": "CD-1", "slot": "strongest_parents", "outcome": "PINNED_AT_SCOPE", "parent_class": "external classical (Wald 1950 / Blackwell-Girshick 1954) + internal anchor", "verification": "statement verified via secondary formulations; primary texts not read (recorded)"},
    {"object": "CD-2", "slot": "strongest_parents", "outcome": "PINNED_AT_SCOPE", "parent_class": "internal GG4 + external pointwise-Bayes (Ferguson 1967 / Berger 1985)", "verification": "statement verified via secondary formulations; cited at chapter level"},
    {"object": "FORMAL_DERIVATION_INTEGRATION_V1", "slot": "strongest_parents", "outcome": "PINNED_AT_SCOPE", "parent_class": "internal (formal-derivation module theorems + GAC5/LMT corrections)", "verification": "all file:line citations in-corpus"},
    {"object": "GRAND_GMI_EMPIRICAL_PROGRAMME_COMPLETE", "slot": "strongest_parents", "outcome": "PINNED_AT_SCOPE", "parent_class": "internal governing rules (schema-coverage convention; recursive reopen rule; section-7 programme)", "verification": "all file:line citations in-corpus"},
    {"object": "READY_FORMAL", "slot": "strongest_parents", "outcome": "PINNED_AT_SCOPE", "parent_class": "internal (audit definition rule; derivation certificate DC-1 + compilation/refinement layers; verdict gate)", "verification": "all file:line citations in-corpus"},
    {"object": "TF-055", "slot": "strongest_parents", "outcome": "PINNED_AT_SCOPE", "parent_class": "registry parent-literature field: DoReMi + Chinchilla + Goldblum (prediction-shape parents; 'formal theorem - none' registered in-object)", "verification": "all three externals verified this tranche; DoReMi author list corrected against the source row (source untouched)"},
    {"object": "V0.2", "slot": "assumptions", "outcome": "RESOLVED_BY_SUPPORT_LOCATION", "parent_class": "n/a", "verification": "support located in the same document (section 5 FC-T4); premises extracted at file:line"},
    {"object": "NON-FINAL", "slot": "falsifiers", "outcome": "RESOLVED_BY_DERIVATION", "parent_class": "n/a", "verification": "two document-internal observables derived from the marker's own universals"},
]

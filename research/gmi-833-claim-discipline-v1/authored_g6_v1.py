#!/usr/bin/env python3
"""GMI #833 claim-discipline v1 — authored registrations for the seven G6 objects.

G6 (FREEZE_V2 section 4): ANALYTIC_PROOF without registered falsifiers -> EV0/M0.
Each of these seven holds a genuine in-doc deductive proof with explicit premises;
this module registers the missing discipline fields, derived from each claim's own
statement/support/proof (FREEZE_V1.md section 4 taxonomy). The maturity consequence
is computed in MATURE_RESCORE_BRIDGE.md — the rescore-v2 package is NOT modified.

Every falsifier below is a concrete observable of its own claim; every assumption
is a premise the printed proof actually invokes; every forbidden extrapolation
names a boundary the proof does not cross.
"""

G6 = [
    {
        "result_id": "GMI833_V2_LEGACY_003_AS-1",
        "package": "gmi-analog-semantics-closure-v1",
        "object_id": "AS-1",
        "locator": "ANALOG_SEMANTICS_THEOREM_V1.md:L19",
        "fields": {
            "scope_quantifiers": {"status": "CARRIED_SCORES_V2", "content": "CONDITIONAL_AT_REGISTERED_SCOPE"},
            "assumptions": {"status": "EXTRACTED", "source": "ANALOG_SEMANTICS_THEOREM_V1.md:L19-L27", "content": [
                "f computable and L-Lipschitz in state on a bounded region (drives the (1+Lh) error-contraction factor)",
                "one-step numerical method with local truncation error at most C h^2 (drives the Ch^2 injection term)",
                "N = T/h steps over the finite declared horizon T (finite geometric unrolling)",
            ]},
            "falsifiers": {"status": "DERIVED", "derivation": "observable negation of the bound/certificate clauses in the claim's own terms", "content": [
                "a declared tuple (X,U,f,eta,P,x0,rho,T) satisfying the premises whose realized global error ||e_N|| exceeds C h (e^{LT}-1)/L (or C T h at L=0) under exact arithmetic — refutes the error bound",
                "any of the 162 exhaustive parameter/input/state/noise certificate cases for sampled rational affine interval systems showing an interval or compiler violation — refutes compiler exactness",
                "a declared (T,epsilon,L,C,d,P) at which the D1/D6 compiler's overhead is not finite and explicit — refutes the overhead claim",
            ]},
            "strongest_parents": {"status": "DERIVED", "derivation": "the printed proof is the classical one-step method error-recurrence argument", "content": [
                "classical one-step numerical ODE error theory (error recurrence e_{k+1}<=(1+Lh)e_k+Ch^2 unrolled with (1+Lh)^N<=e^{LT}; Dahlquist-Bjorck-lineage LTE/global-error analysis)",
            ]},
            "forbidden_extrapolations": {"status": "EXTRACTED", "source": "ANALOG_SEMANTICS_THEOREM_V1.md:L44-L46,L59-L63", "content": [
                "no uniform polynomial bound is claimed when the declared coordinates (T,epsilon,L,C,d,P) grow adversarially or regularity fails (doc: 'does not establish a uniform polynomial bound')",
                "a semantics and simulation bound is not a measurement of physical advantage — Issue #602 real-burden separation remains open (doc claim ceiling)",
            ]},
        },
    },
    {
        "result_id": "GMI833_V2_LEGACY_014_EC-2",
        "package": "gmi-extended-cognition-closure-v1",
        "object_id": "EC-2",
        "locator": "EXTENDED_COGNITION_THEOREM_V1.md:L41",
        "fields": {
            "scope_quantifiers": {"status": "CARRIED_SCORES_V2", "content": "forall_fin[W finite/effectively encodable, matched primitives]"},
            "assumptions": {"status": "EXTRACTED", "source": "EXTENDED_COGNITION_THEOREM_V1.md:L41-L53", "content": [
                "W finite or effectively encodable",
                "the parent receives matched read/write and transition primitives (no bandwidth/storage/dynamics mismatch)",
                "finite-horizon trace equality by induction on time (protected traces compared over finite runs)",
            ]},
            "falsifiers": {"status": "DERIVED", "derivation": "observable negation of the compilation claim and of the frozen ecology predictions stated with it", "content": [
                "a finite/effectively-encodable W with matched primitives where the compiled A x W system's protected trace differs from the extended system's, or total-state information or read/write counts change under matched primitives — refutes the exact reduction",
                "the frozen DELAYED_EXTERNAL_BIT ecology failing any of its four registered predictions (extended arm capability < 1; some deterministic zero-bit agent-only arm > 1/2; erase-write twin != 1/2; matched one-bit D2 parent != 1 with identical answers) — refutes the predicted ecology of the compiled form",
            ]},
            "strongest_parents": {"status": "EXTRACTED", "source": "EXTENDED_COGNITION_THEOREM_V1.md:L55-L57", "content": [
                "CR-7 in GMI_CLASSICAL_DOMAIN_REDUCTION_COMPLETION_V3.md (repo parent; this theorem is CR-7 made executable)",
                "product-state construction / internalization of environment state (A' = A x W relabeling tradition)",
            ]},
            "forbidden_extrapolations": {"status": "EXTRACTED", "source": "EXTENDED_COGNITION_THEOREM_V1.md:L36-L37,L57-L61", "content": [
                "being physically outside the body is neither necessary nor sufficient for external state (EC-1 boundary; EC-2 inherits it)",
                "under unmatched primitives any observed separation is a primitive/resource mismatch and must be reported on that coordinate — not as semantic domain novelty",
            ]},
        },
    },
    {
        "result_id": "GMI833_V2_LEGACY_089_DE-3",
        "package": "machine-intelligence-morphogenesis-v1",
        "object_id": "DE-3",
        "locator": "GMI_DESCRIPTOR_ESTIMATION_BOUNDS_V1.md:L139",
        "fields": {
            "scope_quantifiers": {"status": "CARRIED_SCORES_V2", "content": "forall_fin[n IID development cells], probability >= 1-delta"},
            "assumptions": {"status": "EXTRACTED", "source": "GMI_DESCRIPTOR_ESTIMATION_BOUNDS_V1.md:L131-L139", "content": [
                "residual indicators R_i are IID across the n development cells with rho = P(R=1)",
                "rho_hat is the plain empirical mean (1/n) sum R_i",
            ]},
            "falsifiers": {"status": "DERIVED", "derivation": "observable negation of the coverage statement and of the zero-observation consequence", "content": [
                "an IID residual setup at declared (rho, n, delta) where P(|rho_hat - rho| > sqrt(ln(2/delta)/(2n))) exceeds delta — refutes the coverage constants",
                "a zero-residual sample (rho_hat = 0) from n IID cells at confidence 1-delta with rho exceeding 1 - delta^(1/n) beyond the one-sided bound — refutes the zero-observation consequence",
            ]},
            "strongest_parents": {"status": "DERIVED", "derivation": "the displayed inequality is the Hoeffding bounded-variable concentration bound applied to [0,1] indicators", "content": [
                "Hoeffding-type bounded-variable concentration (Hoeffding 1963 inequality for sums of bounded independent variables, applied to [0,1] residual indicators)",
            ]},
            "forbidden_extrapolations": {"status": "EXTRACTED", "source": "GMI_DESCRIPTOR_ESTIMATION_BOUNDS_V1.md:L141-L157", "content": [
                "observing zero residuals does not prove rho = 0 (only rho <~ 1 - delta^(1/n)) — false zero-residual claims in RAG/adapter/full-update selection are exactly what the theorem forbids",
                "the bound is distribution-free over IID cells; it licenses no claim under correlated residuals",
            ]},
        },
    },
    {
        "result_id": "GMI833_V2_LEGACY_091_DP2-6",
        "package": "machine-intelligence-morphogenesis-v1",
        "object_id": "DP2-6",
        "locator": "GMI_DEVELOPMENTAL_POTENTIAL_THEOREMS_V2.md:L212",
        "fields": {
            "scope_quantifiers": {"status": "CARRIED_SCORES_V2", "content": "iff over declared finite horizon H, additive burdens, one-time switch cost"},
            "assumptions": {"status": "EXTRACTED", "source": "GMI_DEVELOPMENTAL_POTENTIAL_THEOREMS_V2.md:L203-L212", "content": [
                "current morphology A incurs per-use burden c_A(t); candidate B incurs c_B(t) after a one-time switch cost C_switch; burdens add over the finite horizon H (no discounting or interaction terms)",
            ]},
            "falsifiers": {"status": "DERIVED", "derivation": "observable negation of the iff criterion at declared instances", "content": [
                "a declared instance (c_A, c_B, C_switch, H) where sum_{t=1..H}(c_A(t)-c_B(t)) > C_switch yet switching is not beneficial, or <= C_switch yet beneficial — refutes the iff (exactness of the criterion)",
                "a stationary Delta c > 0 instance where the threshold H > C_switch/Delta c misclassifies the switch decision — refutes the stationary corollary",
            ]},
            "strongest_parents": {"status": "DERIVED", "derivation": "the statement is the classical finite-horizon replacement rule (cumulative operating saving vs one-time replacement cost)", "content": [
                "classical finite-horizon replacement/renewal analysis (operations-research equipment-replacement criterion: replace iff cumulative savings exceed switch cost)",
            ]},
            "forbidden_extrapolations": {"status": "EXTRACTED", "source": "GMI_DEVELOPMENTAL_POTENTIAL_THEOREMS_V2.md:L214-L218", "content": [
                "developmental potential is horizon-dependent: no claim that a structurally simple species is deficient in a short-lived ecology (doc interpretation is the boundary)",
                "no stochastic-burden or option-value claim: the criterion covers deterministic additive burdens only",
            ]},
        },
    },
    {
        "result_id": "GMI833_V2_LEGACY_124_NC-3",
        "package": "machine-intelligence-morphogenesis-v1",
        "object_id": "NC-3",
        "locator": "GMI_NONCLASSICAL_END_TO_END_PHASE_THEOREM_V1.md:L65",
        "fields": {
            "scope_quantifiers": {"status": "CARRIED_SCORES_V2", "content": "sufficiency bound for bounded observable X in [a,b], independent samples"},
            "assumptions": {"status": "EXTRACTED", "source": "GMI_NONCLASSICAL_END_TO_END_PHASE_THEOREM_V1.md:L65-L73", "content": [
                "X bounded in [a,b]; samples independent; additive error epsilon; failure probability delta",
            ]},
            "falsifiers": {"status": "DERIVED", "derivation": "observable negation of the sufficiency constants (both displayed forms)", "content": [
                "a bounded X in [a,b] sampled independently with m >= (b-a)^2/(2 epsilon^2) log(2/delta) yet P(|X_hat - E X| > epsilon) > delta — refutes the sample bound",
                "a majority-vote setting at margin gamma with m >= log(1/delta)/(2 gamma^2) yet error > delta — refutes the repetition bound it builds on",
            ]},
            "strongest_parents": {"status": "EXTRACTED", "source": "GMI_NONCLASSICAL_END_TO_END_PHASE_THEOREM_V1.md:L50-L64", "content": [
                "Hoeffding inequality (named in-doc: 'By Hoeffding, majority vote over m independent trials has error at most exp(-2 m gamma^2)')",
            ]},
            "forbidden_extrapolations": {"status": "DERIVED", "derivation": "the proof establishes sufficiency only; the doc's own 'requires, by Hoeffding sufficiency' wording marks the direction", "content": [
                "the bound is a sufficiency bound — no necessity/lower-bound claim that fewer samples cannot suffice (would need different machinery)",
                "a large hidden state space does not make information unreadable for free: measurement/sample complexity is charged to serving burden — no free-readout claims",
            ]},
        },
    },
    {
        "result_id": "GMI833_V2_LEGACY_166_SG-1",
        "package": "machine-intelligence-morphogenesis-v1",
        "object_id": "SG-1",
        "locator": "GMI_STABILITY_GENERALIZATION_THEOREMS_V1.md:L43",
        "fields": {
            "scope_quantifiers": {"status": "CARRIED_SCORES_V2", "content": "forall[A with uniform stability beta]: bound on the EXPECTED generalization gap"},
            "assumptions": {"status": "EXTRACTED", "source": "GMI_STABILITY_GENERALIZATION_THEOREMS_V1.md:L30-L45", "content": [
                "A has uniform stability beta: |l(A(S),z) - l(A(S'),z)| <= beta for all test z whenever S,S' differ in one example",
                "data drawn IID (exchangeability of S and the ghost example z_i')",
            ]},
            "falsifiers": {"status": "DERIVED", "derivation": "observable negation of the expected-gap bound", "content": [
                "an algorithm with uniform stability beta whose expected generalization gap |E_S[R(A(S)) - R_hat_S(A(S))]| exceeds beta — refutes the bound (constructible/exactly enumerable on finite domains)",
            ]},
            "strongest_parents": {"status": "DERIVED", "derivation": "the ghost-sample exchangeability argument is the Bousquet-Elisseeff stability bound verbatim in structure", "content": [
                "Bousquet-Elisseeff algorithmic stability theory (stability bounds on expected generalization error via ghost-sample exchangeability, 2002)",
            ]},
            "forbidden_extrapolations": {"status": "DERIVED", "derivation": "the statement bounds the expectation only; no tail/high-probability term appears in the proof", "content": [
                "beta bounds the EXPECTED gap, not a high-probability/tail gap — no PAC-style failure-probability claim from this theorem alone",
                "uniform stability is a sufficient side-condition; no claim that unstable algorithms generalize poorly",
            ]},
        },
    },
    {
        "result_id": "GMI833_V2_LEGACY_170_TI-2",
        "package": "machine-intelligence-morphogenesis-v1",
        "object_id": "TI-2",
        "locator": "GMI_TARGET_INFORMATION_ACQUISITION_THEOREM_V1.md:L95",
        "fields": {
            "scope_quantifiers": {"status": "CARRIED_SCORES_V2", "content": "conditional lower bound whenever (Z,Q,A) determines W exactly; rate-distortion form under a declared distortion constitution"},
            "assumptions": {"status": "EXTRACTED", "source": "GMI_TARGET_INFORMATION_ACQUISITION_THEOREM_V1.md:L60-L104", "content": [
                "(Z,Q,A) determines W exactly (for the I >= H form)",
                "P and R independent of W; target information arrives only through registered development/query/authority channels (D,Q,A)",
                "distortion constitution declared (for the R_{W|Q,A}(D) form)",
            ]},
            "falsifiers": {"status": "DERIVED", "derivation": "observable negation of the conditional information bound and of the leak dichotomy", "content": [
                "a finite world family where (Z,Q,A) determines W exactly yet I(W;Z|Q,A) < H(W|Q,A) — refutes the conditional information bound (exactly computable on finite families)",
                "a fixed realization with no informative D/Q/A achieving success probability > 1/M on the uniform M-world exact-identification obligation — refutes the leak-or-degenerate dichotomy (would imply protected-target leakage or a degenerate obligation)",
            ]},
            "strongest_parents": {"status": "DERIVED", "derivation": "the bound is a direct conditional-information/identifiability inequality; the general form is Shannon conditional rate-distortion", "content": [
                "Shannon information theory (mutual-information/conditional-entropy inequalities; conditional rate-distortion R_{W|Q,A}(D) for the distortion-constitution form)",
            ]},
            "forbidden_extrapolations": {"status": "DERIVED", "derivation": "the theorem is a lower bound on carried information and explicitly does not select among the listed bridges", "content": [
                "the bound licenses no claim about HOW or whether the residual is actually learned through D — the D/exact-query/retrieval/hybrid bridge list is descriptive, not selective",
                "the 1/M consequence holds under the uniform M-world exact-identification obligation only — no claim about non-uniform or partial-credit obligations",
            ]},
        },
    },
]

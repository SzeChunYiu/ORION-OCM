#!/usr/bin/env python3
"""GMI #833 claim-discipline v1 — author-authored overrides (FREEZE_V1.md section 4).

Two sections:
  ARRIVALS: field registrations for v2-arrival packages whose extraction pass
    reported wording-level gaps (the operative content exists in freeze/theorem
    wording; overrides cite it verbatim or derive with basis).
  LEGACY: per-object derivations/gap decisions for legacy objects where the
    extraction pass found no in-package content (basis or typed reason recorded).

No boilerplate: every falsifier is an observable of its own claim; every
assumption is operative in the claim's own support; every gap carries a reason.
"""

ARRIVALS = {
    "gmi-833-ai0-convergence-spine-v1": {
        "assumptions": {"status": "DERIVED", "derivation": "the spine object's own declared universe and authority inventory are its operative inputs", "content": [
            "the frozen #833 corpus DAG inventory (19 registered material-theory nodes, 12 notation entries, 5 interface classes) is complete at the frozen SHA — the forall_fin declared-universe quantifier of the claim",
            "authority/dependency relations as registered in GMI_THEORY_DEPENDENCY_DAG.json are the input to be normalized (the object validates, never creates, authority)",
        ]},
        "falsifiers": {"status": "DERIVED", "derivation": "check_ai0.py is the package's own executable validator; its failing is the observable refutation", "content": [
            "check_ai0.py failing on the frozen DAG (node/edge violating the registered invariants: class not allowed, missing owner, interface outside the canonical five, dep not a node) — refutes the spine-validation claim",
            "a cycle or a second integration spine appearing in the authority DAG — refutes the single-canonical-spine normalization claim",
        ]},
    },
    "gmi-833-aj0-foundation-scope-v1": {
        "assumptions": {"status": "DERIVED", "derivation": "the demotion contract operates on the registered #837 claim set as its input authority", "content": [
            "the #837 foundation claim registry (flagship question, weakest defensible core, strongest eventual claim, EV0-EV5 contract) as registered — the contract demotes/labels these, it does not re-derive them",
        ]},
    },
    "gmi-833-aj3-distinguishability-v1": {
        "assumptions": {"status": "EXTRACTED", "source": "gmi-833-aj3-distinguishability-v1/THEORY.md:L15-L36", "content": [
            "THEORY.md:L16: probabilistic discrimination premises: equal priors in the registered binary hypothesis problem (optimal single-test success (1+Delta_E)/2)",
            "THEORY.md:L15: approximate distinguishability uses a declared threshold WITHOUT assuming the threshold relation is an equivalence relation",
            "THEORY.md:L36: information measures only after a prior and outcome probability model are registered (equal-prior perfect binary test = 1 bit as derived control, not assumed ontology)",
        ]},
    },
    "gmi-833-aj4-process-organizations-v1": {
        "falsifiers": {"status": "DERIVED", "derivation": "observable negation of the separation-witness claims the package registers", "content": [
            "two process organizations in M_B(O,S) whose lifecycle-stage separation the theorem claims distinct yet which the registered witness computation finds identical (or conversely a claimed-identical pair separated) — refutes the separation theorem",
            "a lifecycle-stage membership certificate that changes under relabeling of the declared finite organization space — refutes stage-computation well-definedness",
        ]},
    },
    "gmi-833-aj5-g0-lowering-v1": {
        "assumptions": {"status": "DERIVED", "derivation": "the lowering claim's operative inputs as registered in its own certificate", "content": [
            "the G0 instruction set and micro-procedure basis as frozen in the G0 register (the lowering maps between two registered presentations)",
            "the two-presentation (P-FUN functional / operational-role) certificate is the equivalence standard the lowering is checked against",
        ]},
        "falsifiers": {"status": "DERIVED", "derivation": "observable negation of the lowering-table claim", "content": [
            "a G0 instruction class whose lowered micro-procedure disagrees between the two registered presentations (certificate mismatch) — refutes presentation equivalence",
            "a lowering whose overhead exceeds the registered overhead bound, or whose result differs across the declared transfer boundary — refutes the overhead/transfer claims",
        ]},
    },
    "gmi-833-aj7-objective-provenance-v1": {
        "assumptions": {"status": "DERIVED", "derivation": "the no-go's operative premises: the frozen one-state/two-action world registered as scope, with deterministic dynamics", "content": [
            "the frozen one-state/two-action world with its registered deterministic dynamics (the no-go is computed exactly on this world)",
        ]},
        "falsifiers": {"status": "DERIVED", "derivation": "the claim is a no-go on unique objective derivability; its refutation is the positive direction", "content": [
            "a proof/construction that world dynamics alone DO determine a unique objective/requirement on the frozen world (uniqueness where the no-go asserts non-uniqueness) — refutes AJ7_NO_GO",
            "exhibition of a third objective function consistent with the same world dynamics beyond the registered two (strengthens, does not refute); conversely failure of both registered objective functions to replay the dynamics — refutes the construction",
        ]},
    },
    "gmi-833-aj8-intelligence-boundary-v1": {
        "assumptions": {"status": "DERIVED", "derivation": "the boundary claim's operative measurement protocol as registered", "content": [
            "the scoped control-capability measurement protocol (task distribution, budgets, abstention rule) as registered — the boundary is measured relative to it",
        ]},
    },
    "gmi-833-aj9a-known-family-benchmark-v1": {
        "assumptions": {"status": "EXTRACTED", "source": "gmi-833-aj9a-known-family-benchmark-v1/FREEZE_V1.md:L10-L12", "content": [
            "FREEZE_V1.md:L10: generator/search/evaluator access to the known-family registry: forbidden (custody ban is the benchmark's operative assumption)",
            "FREEZE_V1.md:L12: no AJ9 family recovery result exists at this freeze — later recovery evidence is valid only against this frozen benchmark state",
        ]},
    },
    "gmi-833-aj9c-k02-blind-recovery-v1": {
        "assumptions": {"status": "EXTRACTED", "source": "gmi-833-aj9c-k02-blind-recovery-v1/FREEZE_V1.md:L3-L8", "content": [
            "FREEZE_V1.md:L3: the freeze predates search implementation, candidate outcome, and post-hoc family adjudication",
            "FREEZE_V1.md:L7: generation/search/evaluation receives only the temporal task and generic primitives (no family material)",
            "FREEZE_V1.md:L8: the search must not read the known-family registry, family IDs/names, post-hoc fingerprints, or any named architecture macro",
        ]},
    },
    "gmi-833-aj9d-k03-blind-recovery-v1": {
        "assumptions": {"status": "EXTRACTED", "source": "gmi-833-aj9d-k03-blind-recovery-v1/FREEZE_V1.md:L7-L8", "content": [
            "FREEZE_V1.md:L7: generation/search/evaluation sees all eight three-site binary inputs and the exact requirement — nothing else",
            "FREEZE_V1.md:L8: no locality, sharing, convolution, equivariance, family label, or K03 fingerprint in any search-visible source",
        ]},
    },
    "gmi-833-aj9e-k04-blind-recovery-v1": {
        "assumptions": {"status": "EXTRACTED", "source": "gmi-833-aj9e-k04-blind-recovery-v1/FREEZE_V1.md:L7-L8", "content": [
            "FREEZE_V1.md:L7: search/evaluation sees only all eight (c,a,b) Boolean inputs and the exact requirement",
            "FREEZE_V1.md:L8: no family label/fingerprint, attention/routing/selector/multiplexer macro, or family-specific operator in search-visible sources",
        ]},
    },
    "gmi-833-aj9f-k05-blind-recovery-v1": {
        "assumptions": {"status": "EXTRACTED", "source": "gmi-833-aj9f-k05-blind-recovery-v1/FREEZE_V1.md:L7-L9", "content": [
            "FREEZE_V1.md:L7: task laws are explicitly flagged as not a supplied solver architecture (the search must construct, not receive, the solver structure)",
            "FREEZE_V1.md:L9: two generic graph/path procedures and two data presentations registered before the run",
        ]},
    },
    "gmi-833-aj9g-k06-blind-recovery-v1": {
        "assumptions": {"status": "EXTRACTED", "source": "gmi-833-aj9g-k06-blind-recovery-v1/THEORY.md:L3-L7", "content": [
            "THEORY.md:L3: the blind phase receives only a finite two-hypothesis evidence problem, prior weights, and generic update primitives",
            "THEORY.md:L7: the K06 post-hoc fingerprint is applied only after the blind outcome is frozen",
        ]},
    },
}

# LEGACY section: author decisions for residual gaps (basis or typed reason each).
LEGACY = [
 {
  "object_id": "SA-4",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "falsifiers": {
    "status": "DERIVED",
    "content": [
     "a stationary quotient update operating correctly WITHOUT right congruence (refutes the necessity clause), or a truncated-continuation equality whose countdown update diverges from the registered semantics (refutes the countdown clause)"
    ],
    "derivation": "observable negation of the two clauses of the CLAIM_LEDGER_V2.md:L32 row"
   },
   "forbidden_extrapolations": {
    "status": "DERIVED",
    "content": [
     "claim boundary = the row's registered scope (coherent finite deterministic transition semantics): no asymptotic/unbounded variant, no claim about unregistered structures, and the registry's typed-analogy parents stay analogies"
    ],
    "derivation": "the ledger row's own scope field is the boundary the proof does not cross"
   }
  }
 },
 {
  "object_id": "S_T",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "falsifiers": {
    "status": "DERIVED",
    "content": [
     "a horizon pair T<T' where the canonical coarse-graining S_(T+1) ->> S_T maps a state inconsistently, or a finite exact semantic-state cardinality that DECREASES as horizon grows - refutes the nondecreasing cardinality claim"
    ],
    "derivation": "observable negation of the nested-horizon coarse-graining claim at CLAIM_LEDGER_V2.md:L9"
   },
   "forbidden_extrapolations": {
    "status": "DERIVED",
    "content": [
     "claim boundary = the row's registered scope (nested exact response families): no asymptotic/unbounded variant, no claim about unregistered structures, and the registry's typed-analogy parents stay analogies"
    ],
    "derivation": "the ledger row's own scope field is the boundary the proof does not cross"
   }
  }
 },
 {
  "object_id": "CCD-1",
  "package": "machine-intelligence-morphogenesis-v1",
  "fields": {
   "falsifiers": {
    "status": "DERIVED",
    "content": [
     "an ordinary classical computable M for which no universal U and finite encoding <M> reproduce its registered semantic execution trace over all finite legal interaction histories h - refutes the collapse claim"
    ],
    "derivation": "negation of the forall-M exists-U form at GMI_CLASSICAL_DOMAIN_COLLAPSE_THEOREM_V1.md:L27"
   }
  }
 },
 {
  "object_id": "CI-T1",
  "package": "machine-intelligence-morphogenesis-v1",
  "fields": {
   "falsifiers": {
    "status": "DERIVED",
    "content": [
     "a proof/construction that nondecreasing finite observations plus boundedness identify the ceiling uniquely - i.e. the claimed bounded nondecreasing continuations matching every observed point with two different ceilings L_a,L_b do not exist - refutes the underdetermination theorem"
    ],
    "derivation": "negation of the compatibility construction at GMI_DOMAIN_CAPABILITY_IDENTIFIABILITY_THEOREMS_V1.md:L27"
   },
   "strongest_parents": {
    "status": "DERIVED",
    "content": [
     "finite-sample underdetermination: compatibility of finite monotone observations with distinct asymptotes/ceilings"
    ],
    "derivation": "the construction is the classical compatibility-by-continuation argument"
   }
  }
 },
 {
  "object_id": "CI-T2",
  "package": "machine-intelligence-morphogenesis-v1",
  "fields": {
   "falsifiers": {
    "status": "DERIVED",
    "content": [
     "an estimation procedure certified to recover the True asymptotic scaling exponent from finite monotone-compatible observations - refutes the exponent non-identifiability claim at L76-78"
    ],
    "derivation": "negation of the multiple-smooth-fits construction"
   },
   "strongest_parents": {
    "status": "DERIVED",
    "content": [
     "power-law fitting non-identifiability: multiple smooth monotone fits with distinct exponents agreeing on a finite interval"
    ],
    "derivation": "same construction family as CI-T1 applied to scaling exponents"
   }
  }
 },
 {
  "object_id": "GM-2",
  "package": "machine-intelligence-morphogenesis-v1",
  "fields": {
   "falsifiers": {
    "status": "DERIVED",
    "content": [
     "two worlds identical on the radius-R neighborhood of an output node but differing outside it, where a deterministic R-round strictly local message-passing algorithm yields DIFFERENT state at that node - refutes the locality isomorphism"
    ],
    "derivation": "negation of the neighborhood-invariance claim at GMI_GRAPH_MESSAGE_COMMUNICATION_THEOREMS_V1.md:L81"
   }
  }
 },
 {
  "object_id": "L8.1",
  "package": "machine-intelligence-morphogenesis-v1",
  "fields": {
   "falsifiers": {
    "status": "DERIVED",
    "content": [
     "a frozen-protocol run at the declared scope where the prediction 'r = 0: D4/D5 at H >= 2; D2 at H = 1 when its row is admissible' fails (a revision becomes necessary) - refutes the frozen law row"
    ],
    "derivation": "prediction-failure observable of the frozen row (predict_domain.py:L92)"
   }
  }
 },
 {
  "object_id": "DISCRETE_FINITE",
  "package": "machine-intelligence-morphogenesis-v1",
  "fields": {
   "falsifiers": {
    "status": "DERIVED",
    "content": [
     "a re-census of the signature coordinate system where the M0 slot's occupant differs from the registered row (parent class not finite transducer/DFA/elementary CA, an update law present where 'no update law' is registered, or the loop bound changed), or a morphology occupying the slot while exhibiting an update law - refutes the frozen occupancy row"
    ],
    "derivation": "occupancy-row mismatch observable (signature_hole_census.py:L59)"
   }
  }
 },
 {
  "object_id": "FORMAL_DERIVATION_INTEGRATION_V1",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "falsifiers": {
    "status": "DERIVED",
    "content": [
     "an integration delivery claiming the listed acquisitions (bounded resettable state, stopped mass-floor recovery, global-history composition, contextual representation, charged certified learner) while one is supplied by unregistered prior structure - refutes the under-explicit-assumptions requirement of the row",
     "a demonstration that the sufficient operational core alone supplies one of the listed missing acquisition laws - contradicts the row's registered premise"
    ],
    "derivation": "violation observables of the row's own integration contract (SCIENTIFIC_GAP_QUEUE_V2.md:L46)"
   },
   "strongest_parents": {
    "status": "REGISTERED_GAP",
    "reason": "gap-queue integration row; no parent literature keyed"
   }
  }
 },
 {
  "object_id": "GRAND_GMI_EMPIRICAL_PROGRAMME_COMPLETE",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "assumptions": {
    "status": "DERIVED",
    "content": [
     "the master-closure convention as registered at MASTER_CLOSURE_LEDGER_V1.md:L62 (sector-based convention; no completeness of possible sectors) and the recursive-gap reopen rule (RECURSIVE_GAP_AUDIT_20260913.md:L371)"
    ],
    "derivation": "the FALSE verdict is computed under exactly these two registered conventions"
   },
   "falsifiers": {
    "status": "DERIVED",
    "content": [
     "a finite formal repair demonstrably supplying one of the missing measurements, or all counterexample-reopen conditions becoming structurally impossible - the registered verdict COMPLETE = FALSE flips only under these observables"
    ],
    "derivation": "the row is a verdict; its falsifiers are the verdict-flipping observables named in the row's own text"
   },
   "strongest_parents": {
    "status": "REGISTERED_GAP",
    "reason": "programme-level closure verdict row; no theorem parent exists to register"
   }
  }
 },
 {
  "object_id": "HPL-2003-97R1",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "falsifiers": {
    "status": "DERIVED",
    "content": [
     "the mirrored Theorem 2.1 statement diverging from the cited primary (Weissman et al., HPL-2003-97, pp. 2-6) upon primary access, or the primary being misattributed/inaccessible - refutes the mirror-fidelity of the import row"
    ],
    "derivation": "attribution-fidelity observable of a parent-mirror row (FINITE_DATA_PARENTS_AND_COSTS_V1.md:L7)"
   }
  }
 },
 {
  "object_id": "PROGRAMME_METHOD_NOVELTY",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "falsifiers": {
    "status": "DERIVED",
    "content": [
     "a GMI result used before its novelty-bucket placement (violates the row's own rule at NOVELTY_PARENT_SUBTRACTION_V1.md:L22), or a bucket assignment contradicted by parent literature already containing the claimed novel element - refutes the novelty-subtraction audit"
    ],
    "derivation": "rule-violation observables of the audit's own registered rule"
   }
  }
 },
 {
  "object_id": "NON-FINAL",
  "package": "machine-intelligence-morphogenesis-v1",
  "fields": {
   "falsifiers": {
    "status": "REGISTERED_GAP",
    "reason": "status-marker row: the sheet asserts its own non-finality with a per-sentence claim ceiling; no claim-specific observable exists without new analysis"
   }
  }
 },
 {
  "object_id": "GG-P2",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "forbidden_extrapolations": {
    "status": "DERIVED",
    "content": [
     "claim boundary = the row's registered scope (finite proof process): no asymptotic/unbounded variant, no claim about unregistered structures, and the registry's typed-analogy parents stay analogies"
    ],
    "derivation": "the ledger row's own scope field is the boundary the proof does not cross"
   }
  }
 },
 {
  "object_id": "GG-P3",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "forbidden_extrapolations": {
    "status": "DERIVED",
    "content": [
     "claim boundary = the row's registered scope (finite quotient-compatible proof graph; right congruence at registered scope): no asymptotic/unbounded variant, no claim about unregistered structures, and the registry's typed-analogy parents stay analogies"
    ],
    "derivation": "the ledger row's own scope field is the boundary the proof does not cross"
   }
  }
 },
 {
  "object_id": "GG-P6",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "forbidden_extrapolations": {
    "status": "DERIVED",
    "content": [
     "claim boundary = the row's registered scope (unsound-verifier counterexample): no asymptotic/unbounded variant, no claim about unregistered structures, and the registry's typed-analogy parents stay analogies"
    ],
    "derivation": "the ledger row's own scope field is the boundary the proof does not cross"
   }
  }
 },
 {
  "object_id": "GG-R3",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "forbidden_extrapolations": {
    "status": "DERIVED",
    "content": [
     "claim boundary = the row's registered scope (finite exact self-response semantics): no asymptotic/unbounded variant, no claim about unregistered structures, and the registry's typed-analogy parents stay analogies"
    ],
    "derivation": "the ledger row's own scope field is the boundary the proof does not cross"
   }
  }
 },
 {
  "object_id": "GG-R7",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "forbidden_extrapolations": {
    "status": "DERIVED",
    "content": [
     "claim boundary = the row's registered scope (finite registered update graph): no asymptotic/unbounded variant, no claim about unregistered structures, and the registry's typed-analogy parents stay analogies"
    ],
    "derivation": "the ledger row's own scope field is the boundary the proof does not cross"
   }
  }
 },
 {
  "object_id": "GG-S1",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "forbidden_extrapolations": {
    "status": "DERIVED",
    "content": [
     "claim boundary = the row's registered scope (finite registered strategic process): no asymptotic/unbounded variant, no claim about unregistered structures, and the registry's typed-analogy parents stay analogies"
    ],
    "derivation": "the ledger row's own scope field is the boundary the proof does not cross"
   }
  }
 },
 {
  "object_id": "A-G",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "strongest_parents": {
    "status": "DERIVED",
    "content": [
     "index object over registry sections A-G: each indexed row registers its own competing parent (registry column); no single strongest parent exists for the index itself"
    ],
    "derivation": "the object is the per-theorem triple index (FALSIFIABILITY_REGISTRY_V1.md:L114)"
   }
  }
 },
 {
  "object_id": "ALL_PARENTS_KNOWN",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "strongest_parents": {
    "status": "DERIVED",
    "content": [
     "the broad parent-first atlas + amendments whose saturation the Q-caveat row governs (same row, GMI_602_FORMAL_GAP_CLOSURE_V2.md:L549)"
    ],
    "derivation": "the caveat row's own content names what it governs"
   }
  }
 },
 {
  "object_id": "D1-D8",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "strongest_parents": {
    "status": "DERIVED",
    "content": [
     "the D1-D8 dependency entries the section-J row indexes (same JSON)"
    ],
    "derivation": "dependencies-index row; its indexed entries are its parent structure"
   }
  }
 },
 {
  "object_id": "EXECUTED_AT_REGISTERED_FOUR_CANDIDATE_SCOPE",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "strongest_parents": {
    "status": "DERIVED",
    "content": [
     "the four frozen NN/non-NN candidate comparisons whose executed scope the provenance row registers (NN_NONNN_POINT_PARITY3_HOSTED_PROVENANCE_V4.json)"
    ],
    "derivation": "provenance row over the four registered comparisons"
   }
  }
 },
 {
  "object_id": "KF-3",
  "package": "machine-intelligence-morphogenesis-v1",
  "fields": {
   "strongest_parents": {
    "status": "DERIVED",
    "content": [
     "Bayesian decision theory: posterior sufficiency for expected utility (EU(a|e)=p(e)^T u_a is the standard posterior-sufficiency argument over a finite hypothesis set)"
    ],
    "derivation": "the printed statement/proof is the classical posterior-sufficiency argument"
   }
  }
 },
 {
  "object_id": "KF-16",
  "package": "machine-intelligence-morphogenesis-v1",
  "fields": {
   "strongest_parents": {
    "status": "DERIVED",
    "content": [
     "message-passing receptive-field locality analysis (radius-T neighborhood dependence; the oversquashing literature the doc's own boundary at L274 cites)"
    ],
    "derivation": "the theorem is the standard synchronous message-passing locality fact"
   }
  }
 },
 {
  "object_id": "NS-2",
  "package": "machine-intelligence-morphogenesis-v1",
  "fields": {
   "strongest_parents": {
    "status": "DERIVED",
    "content": [
     "independent-draw coverage bounds: multiplicative miss probability (1-p_min)^n (classical random-search coverage)"
    ],
    "derivation": "the displayed inequality is the independent-draw product bound"
   }
  }
 },
 {
  "object_id": "SEARCH-T1",
  "package": "machine-intelligence-morphogenesis-v1",
  "fields": {
   "strongest_parents": {
    "status": "DERIVED",
    "content": [
     "uninformed worst-case tree search: adversarial argument forcing inspection of all b^d leaves (classical blind-search lower bound)"
    ],
    "derivation": "the proof is the standard adversary argument on complete b-ary trees"
   }
  }
 },
 {
  "object_id": "CD-1",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "strongest_parents": {
    "status": "REGISTERED_GAP",
    "reason": "no parent literature registered for this ledger row; registry section-H does not key CLAIM_LEDGER_V1.md"
   }
  }
 },
 {
  "object_id": "CD-2",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "strongest_parents": {
    "status": "REGISTERED_GAP",
    "reason": "no parent literature registered for this ledger row; registry section-H does not key CLAIM_LEDGER_V1.md"
   }
  }
 },
 {
  "object_id": "READY_FORMAL",
  "package": "gmi-grand-unification-v1",
  "fields": {
   "strongest_parents": {
    "status": "REGISTERED_GAP",
    "reason": "readiness status definition row; no parent literature keyed in the audit doc"
   }
  }
 },
 {
  "object_id": "TF-055",
  "package": "machine-intelligence-morphogenesis-v1",
  "fields": {
   "strongest_parents": {
    "status": "REGISTERED_GAP",
    "reason": "registry row: theorem column is \"-\"; only the MLX-13 experiment row exists (verified by extraction pass)"
   }
  }
 },
 {
  "object_id": "ANALOG_SEMANTICS_THEOREM_V1",
  "package": "gmi-analog-semantics-closure-v1",
  "fields": {
   "falsifiers": {
    "content": [
     "the ledger row's GREEN closure flipping: AS-1's registered falsifiers (this tranche, authored_g6_v1) firing, or the ledger's evidence pointer (theorem-as-1 assumption-indexed D1/D6 reduction) failing to resolve to the in-doc proof - refutes the ledger row's closure registration"
    ],
    "derivation": "the ledger row registers AS-1's closure; its refutation observables are the closure-flipping ones",
    "status": "DERIVED"
   },
   "strongest_parents": {
    "content": [
     "AS-1's parent structure (classical one-step numerical ODE error theory, Dahlquist-Bjorck lineage) - the row registers AS-1's reduction claim, so its strongest parent is AS-1's"
    ],
    "derivation": "ledger pointer row over AS-1",
    "status": "DERIVED"
   }
  }
 },
 {
  "object_id": "F1-S",
  "package": "gmi-capability-contract-v1",
  "fields": {
   "falsifiers": {
    "content": [
     "a premise-class instance (bounded paired differences in [-1,1], independence at the declared unit) where P(E+ union E-_upper union E-_lower) exceeds alpha - i.e. the simultaneous gates fail more often than the declared level - refutes the simultaneous-coverage claim (constants checkable by exact enumeration at declared n)"
    ],
    "derivation": "coverage-violation observable of the probability statement at FORMALIZATION_V1.md:L120",
    "status": "DERIVED"
   }
  }
 },
 {
  "object_id": "DRS-3",
  "package": "gmi-experimental-validation-v1",
  "fields": {
   "falsifiers": {
    "content": [
     "an assimilated axis later shown NOT owned by any registered parent (a requested cross-family axis with no registered owner, or an unresolved ownership conflict between two parents) - refutes the assimilation finding the row records"
    ],
    "derivation": "the row's finding is parent-ownership completeness; its negation is an unowned axis",
    "status": "DERIVED"
   }
  }
 },
 {
  "object_id": "V0.2",
  "package": "gmi-adaptive-row-confidence-v1",
  "fields": {
   "assumptions": {
    "reason": "document preamble scoping sentence; invokes no premises (rescore v2: UNSCORED_WITH_REASON / SUPPORT_NOT_LOCATED - the census object is a preamble, not a claim statement)",
    "status": "REGISTERED_GAP"
   }
  }
 }
]

# Post-merge appends: rescore-v2 quantifier-overreach crosshands -> forbidden_extrapolations.
CROSSHAND_APPEND = {
 "TT-1|forbidden_extrapolations": "quantifier boundary (rescore v2 crosshand, MATURITY_RESCORE_V2.md quantifier-overreach list): 'every Boolean task' exceeds the n=3..8 exact receipt + by-construction remark; the universal wording is NOT licensed beyond measured n",
 "S0002-9947-1965-0188316-1|forbidden_extrapolations": "quantifier boundary (rescore v2 crosshand, MATURITY_RESCORE_V2.md quantifier-overreach list): universal Krohn-Rhodes prime-decomposition asserted from a NOT_ACCESSIBLE primary with unverified DOI via secondary digest only; no universal claim is licensed until the primary is accessed"
}

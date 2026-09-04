# KSO_CORE_V1 — the canonical KnowledgeSpace object (M1)

Status: **M1 consolidation of the frozen M0 substrate. NO NOVELTY, SUPERIORITY, LANGUAGE OR FRONTIER-MATH CLAIM.**
Inherited contract: `research/orion-machine/theory/KSO_SUBSTRATE_CONTRACT_V1.md` (Part I §1–§23, Part II §24–§36), cited below as *contract §n*; component view `research/orion-machine/theory/KSO_ARCHITECTURE_V1.md`; parents `research/orion-machine/theory/KSO_PARENT_SUBTRACTION_V1.md`.
Implementation: `src/ocm/kso/` (`space.py`, `types.py`, `ids.py`, `warrant.py`, `revocation.py`, `resources.py`, `admission.py`). Obligation registry: `docs/theorems/KSO_OBLIGATION_REGISTRY_V1.json`.
Companion specs: `KSO_WARRANT_V1.md`, `KSO_NAVIGATION_REFERENCE_V1.md`, `KSO_REPRESENTATION_ABSTRACTION_V1.md`.

M1 distinguishes (issue §Goal): constitutional/epistemic invariants (the theorems below), candidate representational choices (hypergraph, restart diffusion, summaries — replaceable), and parent-owned mathematics (named per mechanism). Nothing in this document is claimed as new; the only statements first *written down* at M1 (KS-T21, KS-T22, KS-T04c, KS-T23, KS-T24, KS-T07b) are consolidations of inherited pieces and each names its parents.

## 1. Object of study

The object is the tuple of contract §1, unchanged:

\[
\mathcal K_t=(V_t,H_t,\tau_V,\tau_H,\Lambda_t,A_t,S_t,W_t,\mathscr F_t,\Pi_t,\mathcal P_t,\mathcal R_t),
\]

finite atoms `V_t`, typed directed hyperedges `H_t`, type maps `τ_V, τ_H`, warrant `Λ_t`, authority `A_t`, scope/epoch `S_t`, weights `W_t`, atlas assignment `𝓕_t`, navigation operator `Π_t` (the replaceable reference mechanic, `KSO_NAVIGATION_REFERENCE_V1.md`), procedure algebra `𝓟_t` (contract §8; no control-flow language is invented at M1), resource ledger `𝓡_t` (§7). The constitutional boundary `𝔠 = (Check, Authority, Meter, Commit)` stays external (contract §1; architecture C8).

## 2. Canonical object model and well-formedness

One schema replaces four inherited wrappers (`space.py` docstring). An atom is contract §2's `v = (id, c_v, τ_v, Λ_v, A_v, S_v, e_v, κ_v)`, implemented as `space.Atom(atom_id, atom_type, warrant, authority, scope, epoch, quarantined, content_ref, meta)`; a hyperedge is contract §2's `h = (T_h, O_h, r_h, φ_h, Λ_h, A_h, S_h, w_h, γ_h)`, implemented as `space.Hyperedge(edge_id, tails, heads, relation_type, weight, head_weights, warrant, authority, scope, executable_ref, meta)`. `warrant` is a **warrant interval** `WarrantProfile(lower, upper)` (`KSO_WARRANT_V1.md` §3), `authority` a product lattice `types.Authority`, `scope` a context set with a half-open epoch interval `types.Scope`, `content_ref`/`executable_ref` the payload or `φ_h` reference, `meta` the `κ_v` provenance/resource tuple. `head_weights` normalise to `γ_h` (`Hyperedge.normalized_head_weights`). Ordinary edges are `Hyperedge.is_pairwise`. `space.KnowledgeSpace(atoms, hyperedges, registry)` is immutable; edits (`with_atoms`, `with_edges`, `replace_atom`, `without`) return a new space; `digest` is the SHA-256 of the canonical JSON of both tuples.

**KS-T00 (well-formedness, PROVED by construction).** `KnowledgeSpace.validate` (run from `__post_init__`) rejects duplicate atom ids, duplicate edge ids, an incident atom that does not exist, and unregistered atom/relation types; `Hyperedge.__post_init__` rejects empty tails or heads, a repeated incident atom, a negative weight and non-positive head-weight mass; `resources.ResourceVector.__post_init__` rejects a negative coordinate. Limitation: finite spaces only (registry).

**The four inherited wrappers become views.**

| inherited wrapper (source) | what it carried | view in the canonical model |
|---|---|---|
| `KnowledgeSpace` (`reference/kso_math_v1.py`) | two-valued profiles, weights | `space.from_reference` lifts a profile to a certified interval; `space.to_reference` projects back (drops authority, scope, upper); KS-EQ asserts old-vs-new equivalence on every registered witness |
| `GovernedSpace` (`reference/kso_m0_freeze_checks_v1.py`) | certificates, revoked set, meter, Γ | `admission.GovernedSpace(ks, certificates, revoked, meter, registered_revocations)` — the same `KnowledgeSpace` plus governance data; genome KS-S1…S7 in `admission.check_genome`, digest in `admission.genome_digest` |
| `RecursiveKSO` (`reference/recursive_kso_v0.py`) | macro cells with export sets and a bridge | a `summary` atom whose `meta` records `constituents`/`exported`, created by `abstraction.summarize` with one `REPRESENTATION_TRANSPORT` edge; refinement by `abstraction.descend` (`KSO_REPRESENTATION_ABSTRACTION_V1.md` §4–§5) |
| `UnifiedKSO` (`reference/kso_multidomain_v1.py`) | 60-bit domain evidence ids, per-domain stores | one evidence-id scheme (§4) and domains as `Scope` context tags on atoms/edges |

## 3. Type registry (A1) and conjunctive hyperrelations (A2)

**Registry.** `types.TypeRegistry(atom_types, relation_types)` is data. Atom types default to `types.CORE_ATOM_TYPES` (claim, procedure, constraint, representation, observation, goal, counterexample, proof, model, query_seed, summary — contract §2's list plus `summary`). Relation types are the atlas vocabulary of contract §24: `types.ATLAS_CONTEXT_MAP_KINDS` (six `ContextMapKind` values, read from `src/orion_v2/epistemic_atlas.py` by `types.atlas_vocabulary_from_source`; drift is checked by `TypeRegistry.bound_to_atlas`, unimportability is `None`, never a pass) plus `types.KSO_RELATION_KINDS` = DEPENDENCE, SUPPORT, COMPOSITION, CONSTRAINT. Each `types.RelationSpec` declares `dependency` (participates in the impact cone; true for the four KSO kinds, false for the six atlas kinds), `executable` (may carry `φ_h`; COMPOSITION) and `conjunctive`. Unregistered types are the typed rejections `UNREGISTERED_ATOM_TYPE` / `UNREGISTERED_RELATION_TYPE` (`types.TypeError_`, raised at construction and at `admission.admit`).

**KS-A1 (extensibility, PROVED).** `TypeRegistry.register_atom_type` / `register_relation_type` add a type without touching `warrant.py`, `navigation.py`, `firing.py` or `revocation.py`: no function in those modules inspects a type name except through `registry.dependency_types` and the literal `"COMPOSITION"` in `admission.py`. The extensibility test registers a new atom type and a new relation type, builds a space with them, and re-runs navigation and liveness unchanged; the mutant is the unregistered type, which must be a typed rejection.

**KS-A2 (conjunctive is not pairwise, PROVED; parent: hypergraph vs clique expansion, Chitra & Raphael 2019).** A hyperedge `{a, b} → c` is not three independent edges. `space.pairwise_expansion` is provided *only* as the wrong reading; the two-tail witness shows (i) enabling differs: `firing.enabling_verdict` needs every tail LIVE and above threshold, whereas the pairwise copies fire from one tail; (ii) navigation differs: `navigation.navigation_matrix` gates the whole edge by `Π_{z∈T_h} g(z)` and `navigation.gated_closure` requires all tails reached, whereas the expansion propagates from any single tail. A pairwise reading is accepted only through `space.expand_pairwise` with a `space.PairwiseEquivalenceCertificate(edge_id, scope, proof_ref)`; without one it is the rejection `CONJUNCTIVE_RELATION_NOT_PAIRWISE`. Equivalence is never a default.

## 4. Evidence identity

Three inherited schemes (small integers in `kso_math_v1`; 60-bit SHA-256 prefixes in `kso_multidomain_v1`; free strings in the M0 runtime) resolve to one (`ids.py`):

\[
\mathrm{ev}\!:\!\langle\text{namespace}\rangle\!:\!\mathrm{sha256}(\text{namespace}\,\|\,\mathrm{canonical\_json(payload)})[:16].
\]

`ids.evidence_id(namespace, payload)` (namespace non-empty, no `:`), `ids.legacy_evidence_id` for the canonical string of a small-integer id, `ids.object_id(kind, payload)` for atoms. `ids.EvidenceRegistry.register` detects a **collision** (same id, different payload digest → `ids.IdentityCollision`, never a merge) and `is_duplicate` a **duplicate** (same payload, different provenance). The algebra is generic over hashable ids, so legacy integer fixtures keep working.

## 5. Liveness (summary)

Liveness is three-valued (`warrant.Liveness`): LIVE iff an exhibited warrant survives `R`; DEAD iff no possible warrant survives; UNKNOWN otherwise (`WarrantProfile.liveness`; `KSO_WARRANT_V1.md` §3–§4, KS-T21). Space-level views: `KnowledgeSpace.live_atoms`, `dead_atoms`, `unknown_atoms`, and `edge_enabled_liveness` (edge ∧ tails ∧ heads under Kleene ∧). Warranted navigation gates on LIVE only; UNKNOWN is gated out and is reported as a distinct gap reason (`WARRANT_UNKNOWN_TARGET_CLOSURE_REACHABLE`). Parent: Kleene 1938; ATMS labels (de Kleer 1986).

## 6. Impact cone and reopening

**KS-T09 (impact cone, PROVED; parent: Knaster–Tarski least fixed point).** For dependency types `D` (default `registry.dependency_types`),

\[
\operatorname{Impact}_D(X)=\mu Y.\;X\cup\{u:\exists h,\ r_h\in D,\ T_h\cap Y\neq\varnothing,\ u\in O_h\},
\]

computed by `revocation.impact_cone`; `revocation.is_dependency_closed` is the independent predicate. Proof: contract §13 (monotone operator on the finite lattice `2^V`; cycles are handled by the fixed point itself). Mutant: `revocation.mutant_impact_cone_direct_only` (one hop only; a stale deep dependent stays live).

**KS-T22 (reopening locality, PROVED at M1 as a consolidation of KS-T09 + KS-T04b(ii); parents: dependency-directed backtracking, Doyle 1979; ATMS label update, de Kleer 1986; incremental computation, Acar 2005).** For a revocation delta `R_b → R_a`, let `C` be the atoms whose three-valued liveness differs plus the heads of hyperedges whose liveness differs, and `K = Impact_D(C)`. `revocation.reopening_report` returns

\[
\text{reopen}=K\cap C,\qquad \text{recheck}=K\setminus C,\qquad \text{unaffected}=V\setminus K,\qquad \text{activation\_changed}\subseteq\operatorname{Reach}(D),
\]

where `D` is the non-live set under either revocation (atoms and dead-edge heads; `revocation.reach_of_dead`). *Proof.* An atom outside `K` has unchanged liveness (`C ⊆ K`) and no dependency path from any changed atom or edge (else it lies in the closure, KS-T09), so no obligation depending on changed liveness passes through it. A cone member outside `C` keeps its liveness (an alternative warrant survives, or its warrant is independent), so its status is not reopened, but its activation may change because activation flows along the cone; by KS-T04b(ii) the fixed point is exactly unchanged outside `Reach(D)`. An irrelevant revocation (evidence in no lower/upper warrant) changes no liveness, so `C = ∅`, `K = ∅`, and the fixed point is identical (KS-T04b(iv)). ∎ Limitation (registry): reopening is a re-evaluation *obligation*, not automatic repair.

**Six required cases** (checker `check_impact_and_reopening`; each states the expected report exactly, no-alarm included):

1. **direct dependency** — revoke the sole warrant of `a` with `a → b`: `a ∈ reopen`; `b ∈ K`; `b ∈ reopen` iff `b`'s own liveness changed, else `recheck`.
2. **deep chain** — `a → b → c → d`: every chain member is in `K`; the one-hop mutant loses `c, d` (registry mutant for KS-T22).
3. **shared dependency** — `{b, x} → d`: revoking `x` puts `d` in `K` and leaves `a, b, c` unaffected.
4. **alternative live warrant path** — an atom with profile `{{e₁},{e₅}}`: revoking `e₅` changes no liveness; `reopen = recheck = ∅`.
5. **cyclic dependency** — `p ⇄ q`: handled by the fixed point (both in `K`); no rejection and no divergence.
6. **irrelevant revocation** — evidence outside the universe: empty report, `unaffected = V`, `activation_changed = ∅`.

## 7. Resource vector (G)

`resources.ResourceVector` has the coordinates `object_count, relation_count, warrant_size, index_size, navigation_steps, navigation_work, composition_work, memory_bytes, io_calls, verification_calls, update_work` (contract §19's ledger, one integer per coordinate). Comparison is Pareto only: `no_worse_than`, `dominates`, `incomparable_with`; addition is coordinate-wise. **KS-R1 (PROVED by construction; parent: multi-objective dominance; ORION-V2 `CostVector`).** Every reference mechanic reports a vector: `admission.AdmissionReceipt.resources`, `admission.CompositionReceipt.resources`, `navigation.NavigationResult.resources`; `resources.Meter` is the running ledger of a governed space (KS-S7). Mutant: `resources.mutant_scalar_collapse` (a weighted sum hides a trade).

## 8. Documented tightening vs the frozen reference

Two deviations from `kso_m0_freeze_checks_v1.py` are deliberate and recorded (registry KS-EQ limitation):

- **COMPOSITION_WARRANT_MISMATCH is rejected at admission.** `admission.admit` refuses a warranted atom that is the head of a COMPOSITION edge unless its warrant equals `bridge ⊗ ⊗ tails` (`warrant.meet_all_profiles`). The reference enforced KS-S2 only as a genome predicate after the fact (its F4 case 1 did not check it); M1 enforces it at the boundary, so a head can never mint warrant the composition denies.
- **CertificateKind gains OBSERVATION and IMPORTED.** The inherited six (`admission.INHERITED_KINDS`: INSTRUCTION, DEMONSTRATION, INTERACTION, EXPERIMENTATION, FEEDBACK, EXACT_CHECKER) become eight so the M2 evidence channels map one-to-one: instruction→INSTRUCTION, demonstration→DEMONSTRATION, observation→OBSERVATION, interaction→INTERACTION, experiment→EXPERIMENTATION, proof→EXACT_CHECKER, feedback→FEEDBACK, imported→IMPORTED. FEEDBACK is the only non-warranting kind (`admission.WARRANTING_KINDS`; KS-T18).

## 9. Inherited terminals preserved

M1 changes no scientific terminal. Restated from the inherited records, not re-derived:

- **M2 solve = `PARENT_SUFFICIENT`** (`results/KSO_M2_COMPARATOR_OUTCOME_V1.md`): the full arm ties the strongest faithful parent federation exactly; the mechanic's own number is the **navigation-only row, 38/50**, non-significant against RWR (p = 0.31) and CBR (p = 0.52) at n = 50.
- **M5 = controlled codec only** (`theory/KSO_M3_M5_EXECUTABLE_CONTRACT_V1.md` §3, §5): `M5_CONTROLLED_CODEC_CHAT_GREEN` is a two-codec invariance proof of concept; a systems property, not a theory of language. KS-T10 stays `OPEN_M5`.
- **M6a = proof-kernel integration, not frontier math** (`theory/KSO_M6_FORMAL_MATH_INTEGRATION_V1.md`): `M6A_FORMAL_VERIFIER_CHANNEL = INTEGRATED`, `M6_FULL_FRONTIER_MATH = NOT_RUN`, upstream ME-X3 terminal `PARENT_SUFFICIENT`.
- **Novelty = `NOT_ESTABLISHED`** (contract §22, §36; M2; M6a). KS-P1 (`PARENT_PRODUCT_OWNED`) may not be cited in any novelty statement (registry rule).

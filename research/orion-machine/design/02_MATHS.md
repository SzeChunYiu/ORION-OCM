# 02 — Mathematics: objects and theorems

Every row: statement · proof location · checker (planted failure + no-alarm) · parent · ledger id.
Source of truth for proofs: `theory/KSO_SUBSTRATE_CONTRACT_V1.md` (KS-T00..T16) and
`reference/kso_math_v1.py`, `reference/kso_m0_freeze_checks_v1.py` (#295). Zero `ABSENT` is the
acceptance; `[OPEN_Mn]` rows carry the reason they cannot be stated earlier.

## Objects

| symbol | definition | tag |
|---|---|---|
| `A`, `H`, `τ`, `w` | finite atoms; hyperedges with nonempty `tails`, `heads`, weight `w ≥ 0`; type `τ: H → T` | `[MACHINE: KnowledgeSpace.validate]` KS-T00 |
| `𝓛`, `⊕`, `⊗`, `0`, `1` | antichains of environments; min-union; min-pairwise-union; `∅`; `{∅}` | `[PROVED: KS-T01]` |
| `live(l, R)` | `∃ e ∈ l : e ∩ R = ∅` | `[MACHINE: profile_live]` |
| `g_R` | gate: `g_R(x) = 1` if `live(L(x), R)` else `0`, for `x ∈ A ∪ H` | `[MACHINE: _gate]` |
| `d(a)` | frozen out-mass `Σ_{h ∋ a ∈ tails} w(h)`, computed once at `R = ∅` | `[PROVED: KS-T04]` |
| `η_Q: T → [0,1]` | query-conditioned type weights (registered per domain, default from the parameter study, 04 §P) | `[SPEC → M2]` |
| `s_Q ∈ Δ(A)` | committed seed vector from atomization | `[MACHINE: kso_m0_freeze_checks_v1 (atomisation)]` |
| `W_Q` | gated typed transition, `W_Q[a,b] = Σ_h η_Q(τ(h)) w(h) g_R(h) g_R(b) / d(a)` | `[MACHINE: navigation_matrix]` |
| `ρ_Q` | restart fixed point `ρ = α s_Q + (1−α) W_Qᵀ ρ` | `[MACHINE: restart_fixed_point]` |
| `ρ_∅` | background fixed point with the uniform seed | `[MACHINE: reaction_surprise]` |
| `r_Q(a)` | reaction surprise `ρ_Q(a) − ρ_∅(a)` | `[PROVED: KS-T06]` |
| `E_R` | enabled hyperedges: `g_R(h)=1 ∧ ∀ a ∈ tails(h): g_R(a)=1 ∧ ρ_Q(a) > θ` | `[MACHINE: enabled_hyperedges]` |
| `X_Q` | extracted subgraph: support of `ρ_Q` restricted to the seed-connected component of `(A, E_R)` | `[SPEC → M2]` KS-T11 |
| `π` | procedure: hyperpath in `E_R` from seeds to target; `L(π) = ⊗` of its parts | `[SPEC → M2]` |
| `cone(R)` | impact cone: least dependency-closed superset of the atoms whose gate flips under `R` | `[PROVED: KS-T09]` |
| `Ω` | navigation outcome ∈ {FOUND, GAP_NOT_FOUND, OBSTRUCTION_WITNESSED, CANNOT_CHECK} | `[MACHINE: kso_m0_freeze_checks_v1 (four-valued outcome)]` |
| `Σ` | genome predicates S1..S7 on `𝒦` | `[MACHINE: kso_m0_freeze_checks_v1 (7 planted violations)]` |
| `B` | `NavigationBudget = (steps, edge_visits, restarts, wall_proxy)` per arm | `[SPEC → M2 comparator]` A14 |

## Theorems

| id | statement | proof | checker (planted / no-alarm) | parent | tag |
|---|---|---|---|---|---|
| KS-T01 | `(𝓛, ⊕, ⊗, 0, 1)` is an idempotent commutative semiring | contract §3 | exhaustive n=3 (20/400/8,000) | de Kleer 1986; GKT 2007 provenance semiring | `[PROVED]` |
| KS-T02 | if `R` kills a required tail or the edge, `h ∉ E_R` (conjunctive firing disabled) | §4 | planted firing witness | ATMS | `[PROVED]` |
| KS-T03 | `W_Q` is substochastic | §5 | 2/2 | RWR | `[PROVED]` |
| KS-T04 | gating with frozen `d` ≡ pruning the revoked rows/cols and keeping original denominators; renormalisation differs | §5 | two implementations agree; renormalising mutant caught | — (delta over PPR, 08) | `[PROVED]` |
| KS-T05 | `ρ ↦ α s_Q + (1−α) W_Qᵀ ρ` is an `ℓ1` contraction with factor `≤ 1−α`; unique fixed point; exact rational solution exists | §6 | rational witness + 200 random | Banach; PPR | `[PROVED]` |
| KS-T06 | background-equal atom ⇒ `r_Q(a) = 0` | §6 | no-alarm direction | — | `[PROVED]` |
| **KS-T06b** | (i) `s_Q` touching hub `u` and specific `v` with `ρ_∅(u) ≫ ρ_∅(v)`: `ρ_Q(u) > ρ_Q(v)` (raw) while `r_Q(v) > r_Q(u)` for `α` above a stated bound; (ii) `s_Q = δ_u` ⇒ `r_Q(u) > r_Q(a) ∀ a ≠ u`; (iii) uniform seed ⇒ `r ≡ 0` | #295 `kso_m0_freeze_checks_v1` | planted popularity ranker fails (i); least-connected-atom-as-hub must **not** pass (ii) — the replay's VACUOUS P4 is the failure this row now must catch | Collins & Loftus (fan effect) | `[MACHINE — being re-checked after replay]` |
| KS-T07 | lumpable quotient commutes with navigation (`pushforward ∘ step = step ∘ pushforward`) | §9 | 80/80 + negative control | Kemeny–Snell lumpability | `[PROVED; PARENT_THEOREM_ADOPTED]` |
| KS-T08 | admission preserves connectivity-or-quarantine: every admitted atom is navigation-reachable or is quarantined and cannot fire | §10 | 5 cases; planted isolated atom rejected 50/50 (M1) | — | `[PROVED; implementation invariant]` |
| KS-T09 | `cone(R)` is the least dependency-closed superset | §13 | 1/1 | Doyle dependency-directed backtracking | `[PROVED]` |
| KS-T10a | extraction is a function of `(𝒦, s_Q)`: two codecs with equal `s_Q` produce identical `X_Q` | #295 | two atomizers, byte-equal `X_Q`; planted seed perturbation must differ | — | `[MACHINE]` |
| KS-T10 | two codecs on the same text produce equal `s_Q` on the registered probe classes | — | held-out paraphrases | — | `[OPEN_M5: needs two codecs]` |
| KS-T11 | `X_Q` is unique (support of the unique fixed point on the seed component); the prize-collecting optimiser over it may tie, and ties are reported | §7 + #295 | planted tie distinguishes the two | PCST (Johnson et al.) | `[MACHINE (uniqueness); SPEC (optimiser) → M2]` |
| KS-T12 | consolidation `𝒦 → 𝒦/~` is lifecycle-safe iff `~` is lumpable (T07) and warrant-measurable (S4) | §11 | `[SPEC → M3]` planted non-measurable merge | DreamCoder library learning | `[SPEC → M3]` |
| KS-T13 | gap closure: an acquisition transaction `(A⁺, H⁺, cert)` that passes admission changes `Ω` from GAP to FOUND for the query that triggered it, and leaves `L` of pre-existing atoms unchanged | — | planted transaction that edits an existing label rejected | — | `[SPEC → M3]` |
| KS-T14 | governed Jump: a rewrite `J` (new type / atom class / quotient) is admissible only after `Ω = OBSTRUCTION_WITNESSED` at the current level and `JumpTrigger.is_admissible`; `J` preserves `Σ` and existing labels | — | planted Jump without witness rejected; planted `Σ` edit rejected | ME-X2 minimum escalation; v1 J0–J8 | `[SPEC → M4]` |
| KS-T15 | **feedback cannot warrant**: a FEEDBACK certificate enters with `L = 0`, hence never `live`, hence never in `E_R`; EXACT_CHECKER enters with `L = {{c}}` for its checker assumption `c` | #295 | planted feedback atom cannot enable any edge; exact-checker atom can | RLHF (negative), proof assistants (positive) | `[MACHINE]` |
| KS-T16 | stem-cell invariant: acquire → compose → self-revise → revoke → fixed point in ≤ k steps, with `Σ` digest unchanged and every pre-existing live label still live | #295 | three cancers caught (Σ edit, label merge, unwarranted growth) | Gödel machine × ATMS | `[MACHINE]` |
| **KS-T17** | budget clause: an arm exceeding matched `B` is `CANNOT_CHECK`; a comparison is valid only under equal `B` and equal `(𝒦, s_Q)` | #295 | overrun ⇒ exit 2 | FM60 / ME-F1 budget isolation | `[MACHINE]` |
| **KS-T18** | typing is a coverage prior: with full type coverage, typed and untyped navigation reach the same `Ω`; an advantage is admissible only on an unexercised type | #295 | planted full-coverage tie; planted unexercised type shows advantage | ME-X6 V3 | `[MACHINE]` |
| **KS-T19** | obstruction witness: `Ω = OBSTRUCTION_WITNESSED` iff the bounded gated walker fails **and** the ceiling walker (ungated, unbounded closure over all registered types) fails, or the target is non-identifiable under `s_Q`; timeout alone ⇒ GAP | #295 | planted reachable target under ceiling ⇒ GAP not OBSTRUCTION | H-EXT-1R ("gate fires AND parent witnessed off ceiling") | `[MACHINE]` |
| **KS-T20** | procedure warrant: `live(L(π), R) ⇔ ∀ parts p: live(L(p), R)` | by `⊗` definition | compose checker: component revocation kills composite | ATMS | `[MACHINE]` |
| **KS-T21** | parameter defaults are the argmax of the registered walk-forward study under all costs; no default is free | — | receipt cites the study row | `[[feedback-no-hardcoded-params]]` | `[SPEC → M2 study]` |

## Genome S1–S7 on the hypergraph `[MACHINE: kso_m0_freeze_checks_v1]`

| id | predicate on `𝒦` | planted violation caught |
|---|---|---|
| S1 revocation-completeness | every assumption named in any label is revocable and its `cone` computable | unreachable assumption |
| S2 label soundness | `L(h) ⊆ ⊗ tails` refinement holds for every admitted edge | edge with a label stronger than its tails |
| S3 exact-share retraction | `ρ` under `R` equals the pruned-with-frozen-`d` walk (KS-T04) | renormalisation |
| S4 coarsest authority partition | any quotient used is generated by the revocation family (Theorem S4) | non-measurable merge |
| S5 signature invariance | self-revision preserves `T`, the label algebra and `Σ` | type vocabulary edit outside Jump |
| S6 channel typing | every atom carries a certificate kind; FEEDBACK ⇒ `L = 0` | feedback atom with live label |
| S7 obstruction honesty | `Ω` is computed by KS-T19, never set by a codec | codec-written outcome |

## Absent rows: none. Open rows: KS-T10 (M5), KS-T12/13 (M3), KS-T14 (M4), KS-T21 (study).

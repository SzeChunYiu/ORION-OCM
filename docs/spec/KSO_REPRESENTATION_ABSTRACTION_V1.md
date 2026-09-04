# KSO_REPRESENTATION_ABSTRACTION_V1 — quotients, summaries and abstraction laws (M1)

Status: **M1 consolidation of contract §9, §11 and the abstraction laws of `research/orion-machine/theory/RECURSIVE_KSO_ARCHITECTURE_V1.md` §4. NO NOVELTY CLAIM.** Implementation: `src/ocm/kso/abstraction.py` (with `warrant.py`, `types.py`). The mathematics of quotienting is parent-owned (Kemeny–Snell); the warrant law of summaries is KS-T21 applied; KS-T12 stays OPEN; the recursive/fibred organisation is explicitly *unfrozen* (§7).

## 1. Navigation lumpability (KS-T07, parent theorem)

For a partition `κ: V → V̄` into blocks, Kemeny–Snell lumpability of the navigation matrix `P` is

\[
\forall B,B',\ \forall v,v'\in B:\quad \sum_{u\in B'}P(v,u)=\sum_{u\in B'}P(v',u)\qquad(\texttt{abstraction.is\_lumpable}),
\]

and then the quotient `P̄(B,B') = Σ_{u∈B'} P(v,u)` (`abstraction.lump`) is representative-independent and commutes with pushforward (`abstraction.pushforward`, `abstraction.row_vector_step`):

\[
\kappa_*(xP)=(\kappa_*x)\,\bar P\quad\text{for every distribution }x.
\]

**KS-T07 (PARENT_OWNED; Kemeny & Snell 1976).** The equality is the standard lumpability theorem; KSO adopts it as a representation gate and claims nothing (contract §9.1). Mutant: `abstraction.mutant_bad_quotient` (row averaging inside a block whether or not the partition is lumpable). Inherited calibration: contract §21 (80 commutation checks, one planted non-lumpable matrix rejected).

## 2. Warrant measurability

Lumpability does **not** imply warrant/revocation preservation (contract §9.2). A partition is *warrant-measurable* with respect to the registered revocations `Γ` when every block has one three-valued liveness under every `R ∈ Γ`:

\[
\forall B\in\kappa,\ \forall R\in\Gamma,\ \forall v,v'\in B:\quad \ell^3_R(\Lambda_v)=\ell^3_R(\Lambda_{v'})\qquad(\texttt{abstraction.warrant\_measurable}).
\]

This is the genome's S4 requirement (`admission.ks_S4_measurability`: every registered revocation is a subset of the evidence universe) lifted to a partition of atoms; with `Γ = ∅` the check runs on `R = ∅` alone. Because liveness is three-valued (KS-T21), a block mixing LIVE and UNKNOWN atoms is *not* measurable: the quotient would launder incompleteness.

## 3. KS-T07b — admissibility verdict

**Statement (PROVED at M1; consolidation of KS-T07 and S4; parents: lumpability ∧ measurability).** A representation move is admissible iff

\[
\text{navigation lumpability}\;\land\;\text{warrant measurability}.
\]

`abstraction.quotient_admissible(ks, P, blocks, Γ)` returns `abstraction.QuotientVerdict` ∈ {ADMISSIBLE, NOT_LUMPABLE, NOT_WARRANT_MEASURABLE, NEITHER}, the two failures kept distinct and never collapsed. *Proof.* Lumpability is necessary and sufficient for the quotient dynamics to commute with pushforward (KS-T07); measurability is necessary and sufficient for the quotient to answer every registered revocation exactly, because a block with two liveness values has no single value under `R`; neither implies the other (a lumpable-but-not-measurable and a measurable-but-not-lumpable partition are the two planted refusals of the registry). ∎ Consequence: a good dynamical compression cannot launder an epistemic distinction, and an exact epistemic partition cannot launder navigation.

## 4. Summary / macro atoms and KS-T23 — no authority from abstraction

`abstraction.summarize(ks, constituents, summary_id, exported, correspondence_warrant)` adds a `summary` atom over constituents `X` with exported parts `X_e ⊆ X` (default: all of `X`, the strongest reading) and one `REPRESENTATION_TRANSPORT` hyperedge `X → summary` carrying the correspondence warrant `Λ_corr` (`abstraction.SummaryReceipt`). The law (`RECURSIVE_KSO_ARCHITECTURE_V1.md` §4 item 2; `recursive_kso_v0.py` macro warrant; contract §3):

\[
\Lambda(\text{summary})=\Lambda_{\rm corr}\otimes\bigotimes_{x\in X_e}\Lambda(x),\qquad
A(\text{summary})=\bigwedge_{x\in X}A(x),\qquad
S(\text{summary})=\bigcap_{x\in X}S(x),
\]

via `warrant.meet_all_profiles`, `types.meet_authority`, `types.intersect_scopes`.

**KS-T23 (PROVED at M1; consolidation; parents: ATMS conjunction; `recursive_kso_v0` macro warrant).** (i) `LIVE(summary) ⇒` live support exists below it: by KS-T21, `LIVE(Λ_corr ⊗ ⊗Λ(x)) ⇔ LIVE(Λ_corr) ∧ ⋀ LIVE(Λ(x))`, so every exported part and the correspondence are LIVE. (ii) DEAD and UNKNOWN propagate by KS-T21: with every exported part DEAD the summary is DEAD; with any exported part UNKNOWN (and none DEAD) it is at most UNKNOWN. (iii) Authority is the meet and scope the intersection (KS-T20), so no aggregation, majority, embedding similarity or compression mints authority. (iv) A summary answers a query family only under a registered sufficiency certificate (§5). ∎ Mutant: `abstraction.mutant_summary_majority` (⊕ over constituents: LIVE while support below is dead — authority minted by aggregation). Hostile helper: `abstraction.strip_summary_support` (the evidence that must be revoked to kill every exported part; the summary must then be DEAD).

## 5. REFINE_REQUIRED (F3) and refinement access

Query-relative abstraction (issue F1; `RECURSIVE_KSO_ARCHITECTURE_V1.md` §4 item 1): a summary may answer a query family `𝒬` without descent only when a registered `abstraction.SufficiencyCertificate(summary_id, query_family, proof_ref)` covers `𝒬`. `abstraction.answer_with_summary(ks, summary_id, query_family, certificates, revoked)` returns `abstraction.SummaryAnswer` ∈ {ANSWERED_FROM_SUMMARY, REFINE_REQUIRED, SUMMARY_NOT_LIVE}: a non-live summary never answers; without a matching certificate (non-empty `proof_ref`) the runtime emits `REFINE_REQUIRED` and must descend rather than guess. Refinement access (item 4) is `abstraction.descend(ks, summary_id)`: the provenance map `χ` to the constituents recorded in the summary's `meta`; a non-summary atom is the rejection `NOT_A_SUMMARY`. Reopening locality for summaries (item 5) is KS-T22 applied to the `REPRESENTATION_TRANSPORT` edge: it is not a dependency type (`types.RelationSpec.dependency = False` for atlas kinds), so a change below reaches the summary through its warrant (KS-T21), not through the impact cone; the cone continues through DEPENDENCE/SUPPORT/COMPOSITION/CONSTRAINT edges leaving the summary.

## 6. MDL is necessary, not sufficient; KS-T12 stays OPEN

A consolidation candidate may be scored by contract §11's MDL criterion

\[
\Delta L=L(G)-[L(m)+L(\chi)+L(\text{exceptions})]\qquad(\texttt{abstraction.mdl\_delta}),
\]

but positive compression is never sufficient for admission: semantics on the registered scope, the warrant law (§4), scope, and future-revocation behaviour must also pass. **KS-T12 (OPEN; parent: DreamCoder/LILO library learning).** Lifecycle-safe consolidation — maintaining/reopening a macro in work proportional to the affected dependency region — is not proved at M1; summaries implement only the warrant/authority law (KS-T23). Revocation commutation `q(Prune_R(K)) ≅ Prune_R(q(K))` (item 3) is asserted only where an abstraction contract claims exactness and is then exactly KS-T07b's measurability applied to the pruned chain.

## 7. F4 — candidate recursive/fibred organisation remains unfrozen

The recursive KSO (`RECURSIVE_KSO_ARCHITECTURE_V1.md`: overlapping local spaces, macro cells, fibres, multiscale dynamics) is **not** M1 constitution. M1 freezes only the laws above (KS-T07, KS-T07b, KS-T23, REFINE_REQUIRED). The following are recorded as *candidate parents for M8*, not as structure any later milestone must respect:

| candidate organisation | parent mathematics | status at M1 |
|---|---|---|
| families of local spaces over scopes | indexed categories / Grothendieck fibrations | candidate, unfrozen |
| local-to-global restriction and gluing | presheaves / sheaves (Robinson 2017; Hansen & Ghrist 2019); the existing atlas is presheaf-like (contract §9.3) | candidate; a global section still needs an independent witness |
| recursive typed composition of operators | operads; hypergraph categories / typed wiring (Fong & Spivak 2019) | candidate, unfrozen |
| open-system interfaces between fibres | cospans / structured cospans / double categories | candidate, unfrozen |
| hierarchical routing of skills | hierarchical RL / options | candidate, unfrozen |

Each candidate's valid terminal is `PARENT_SUFFICIENT` (`RECURSIVE_KSO_ARCHITECTURE_V1.md` §10). Nothing in this document may be cited as a residual.

## 8. Parents

| mechanism | parent | what the parent owns |
|---|---|---|
| quotient of navigation | Kemeny & Snell 1976 | lumpability: necessary and sufficient block-transition equality |
| measurability of revocations | S4 (#201; genome) | exact answers require block-union revocations |
| summary warrant conjunction | ATMS (de Kleer 1986); `recursive_kso_v0` bridge ⊗ exports | label conjunction under composition |
| compression objective | MDL (Rissanen) | description-length criterion — necessary, not sufficient |
| library consolidation | DreamCoder (Ellis et al. 2021); LILO (Grand et al.) | abstraction/library learning; KS-T12 open against them |
| safe abstraction in general | abstract interpretation; Markov lumpability | sound over-approximation of dynamics |

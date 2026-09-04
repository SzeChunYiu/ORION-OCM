# KSO_WARRANT_V1 — warrant algebra, intervals and three-valued liveness (M1)

Status: **M1 consolidation. NO NOVELTY CLAIM.** Consolidates contract §3 (`research/orion-machine/theory/KSO_SUBSTRATE_CONTRACT_V1.md`, profile algebra, KS-T01), the `complete` flag of `theory/OCM_OPERATIONAL_SEMANTICS_V1.md` (absence of a surviving warrant is UNKNOWN, not false) and the composition law of contract §3/§30 into `src/ocm/kso/warrant.py` and `src/ocm/kso/types.py`. Every mechanism names its parent (§8). KS-T21 is first *stated* here; it is a consolidation, not a residual.

## 1. Evidence, warrants, profiles

`E` is the finite evidence universe (ids per `KSO_CORE_V1.md` §4). A warrant is `W ⊆ E`; a profile is the antichain of inclusion-minimal sufficient warrants (contract §3):

\[
P\subseteq 2^E,\qquad \forall W,W'\in P:\ W\not\subset W'.
\]

`warrant.canon` computes `Min` (drop duplicates and non-minimal sets; deterministic order by size then elements); `warrant.is_antichain` is the predicate. Every profile is associated with the monotone Boolean function `f_P(X) = 1 ⇔ ∃W∈P: W ⊆ X`; this map is a bijection onto monotone Boolean functions on `E` (contract §3 proof of KS-T01). `warrant.all_profiles(n)` enumerates them (Dedekind numbers 2, 3, 6, 20, 168, …).

## 2. The semiring: ⊕, ⊗, 0, 1 (KS-T01)

\[
P\oplus Q=\operatorname{Min}(P\cup Q)\ \text{(alternative)},\qquad
P\otimes Q=\operatorname{Min}\{W_P\cup W_Q: W_P\in P,\ W_Q\in Q\}\ \text{(conjunctive)},
\]
\[
\mathbf 0=\varnothing\ (\texttt{warrant.ZERO}),\qquad \mathbf 1=\{\varnothing\}\ (\texttt{warrant.ONE}).
\]

`warrant.join` is ⊕, `warrant.meet` is ⊗ (with `P ⊗ 0 = 0`), `warrant.meet_all` folds ⊗ from `1`. The semiring order is `P ≤ Q ⇔ f_P ≤ f_Q ⇔` every warrant of `P` contains a warrant of `Q` (`warrant.leq`). The two-valued live predicate under revoked `R ⊆ E` is

\[
\ell_R(P)=1\iff \exists W\in P:\ W\cap R=\varnothing\qquad(\texttt{warrant.live}),
\]

and the key identity used throughout is `ℓ_R(P) = f_P(E ∖ R)`.

**KS-T01 (PROVED; parents: ATMS labels, de Kleer 1986; provenance semirings, Green, Karvounarakis & Tannen 2007).** `(𝒜_E, ⊕, ⊗, 0, 1)` is a commutative idempotent semiring. *Proof sketch* (contract §3). Under the bijection `P ↦ f_P`, `f_{P⊕Q} = f_P ∨ f_Q` and `f_{P⊗Q} = f_P ∧ f_Q`; Boolean `∨, ∧` are associative, commutative and distributive, `∨` is idempotent, `false`/`true` are the identities and `false` annihilates under `∧`; injectivity transfers every law to antichains. ∎ Checker `warrant.check_semiring` (identities, idempotence, commutativity, closure under antichains, associativity, distributivity) is exhaustive at `n = 3` (§7). Mutant: `warrant.mutant_meet_as_union`.

## 3. The warrant interval and three-valued liveness

A `warrant.WarrantProfile(lower, upper)` is an interval of profiles, `lower ≤ upper` in the semiring order (enforced in `__post_init__`): `lower` = the *exhibited* sufficient warrants, `upper` = every warrant that could *possibly* suffice. Constructors: `certified(p)` (`lower = upper = p`, the inherited two-valued profile), `partial(p)` (`upper = ONE`: anything might still warrant it), `zero()` (`[0, 0]`, certified-unwarranted: FEEDBACK atoms by construction, KS-T18), `one()`. `complete` is `lower == upper`. Interval operations are coordinate-wise: `WarrantProfile.join` = `[L_P⊕L_Q, U_P⊕U_Q]`, `WarrantProfile.meet` = `[L_P⊗L_Q, U_P⊗U_Q]` (well-formed because `f` is monotone in both arguments); `warrant.meet_all_profiles` folds `meet`.

Liveness under `R` (`WarrantProfile.liveness`, values `warrant.Liveness`):

\[
\ell^3_R(P)=
\begin{cases}
\mathrm{LIVE} & \ell_R(L_P)=1,\\
\mathrm{DEAD} & \ell_R(U_P)=0,\\
\mathrm{UNKNOWN} & \text{otherwise.}
\end{cases}
\]

LIVE and DEAD are exclusive: `L_P ≤ U_P` gives `ℓ_R(L_P) ⇒ ℓ_R(U_P)` (a surviving `W ∈ L_P` contains some `W' ∈ U_P`, which also survives). `is_live` is `liveness is LIVE`; `evidence` is the union of the exhibited warrants. Kleene strong connectives are `warrant.kleene_and` (DEAD dominates, then UNKNOWN) and `warrant.kleene_or` (LIVE dominates, then UNKNOWN).

## 4. KS-T21 — liveness is a Kleene homomorphism on intervals

**Statement (PROVED at M1; consolidation; parents: Kleene 1938; Belnap 1977; rough-set lower/upper approximation, Pawlak 1982).** For all intervals `P, Q` and every `R ⊆ E`:

\[
\ell^3_R(P\otimes Q)=\ell^3_R(P)\wedge_K \ell^3_R(Q),\qquad
\ell^3_R(P\oplus Q)=\ell^3_R(P)\vee_K \ell^3_R(Q);
\]

(a) *reduction*: a certified interval is never UNKNOWN and `ℓ³_R(P) = LIVE ⇔ ℓ_R(L_P)`; (c) *refinement monotonicity*: if `Q` refines `P` (`L_P ≤ L_Q` and `U_Q ≤ U_P`) then `ℓ³_R(P) ∈ {ℓ³_R(Q), UNKNOWN}` — certifying can only move UNKNOWN to LIVE or DEAD, never flip LIVE and DEAD.

*Proof.* By `ℓ_R(P) = f_P(E∖R)` and KS-T01, `ℓ_R(A⊗B) = ℓ_R(A) ∧ ℓ_R(B)` and `ℓ_R(A⊕B) = ℓ_R(A) ∨ ℓ_R(B)` for profiles. For ⊗ on intervals:

\[
\mathrm{LIVE}(P\otimes Q)\iff \ell_R(L_P\otimes L_Q)\iff \ell_R(L_P)\wedge\ell_R(L_Q)\iff \mathrm{LIVE}(P)\wedge\mathrm{LIVE}(Q),
\]
\[
\mathrm{DEAD}(P\otimes Q)\iff \neg\ell_R(U_P\otimes U_Q)\iff \neg\ell_R(U_P)\vee\neg\ell_R(U_Q)\iff \mathrm{DEAD}(P)\vee\mathrm{DEAD}(Q).
\]

"DEAD if either is DEAD, LIVE if both are LIVE, UNKNOWN otherwise" is exactly Kleene strong ∧. For ⊕: `LIVE(P⊕Q) ⇔ ℓ_R(L_P) ∨ ℓ_R(L_Q)` and `DEAD(P⊕Q) ⇔ ¬ℓ_R(U_P) ∧ ¬ℓ_R(U_Q)`, which is Kleene strong ∨. (a): `L = U` makes the two cases `ℓ_R(L)` and `¬ℓ_R(L)`, exhaustive. (c): `f_{L_P} ≤ f_{L_Q} ≤ f_{U_Q} ≤ f_{U_P}`, so `LIVE(P) ⇒ ℓ_R(L_P) ⇒ ℓ_R(L_Q) ⇒ LIVE(Q)` and `DEAD(P) ⇒ ¬ℓ_R(U_P) ⇒ ¬ℓ_R(U_Q) ⇒ DEAD(Q)`. ∎

Checker `warrant.check_three_valued_reduction` verifies (a), (b) and (c) exhaustively over every valid interval at `n = 3` and all `2^n` revocations (§7). Mutants: `warrant.mutant_unknown_as_live`, `warrant.mutant_unknown_as_dead`. Consequences used elsewhere: warranted navigation gates on LIVE only (`KSO_NAVIGATION_REFERENCE_V1.md` §2); enabling is ENABLED/DISABLED/UNKNOWN (`firing.enabling_verdict`, KS-T02); summaries inherit UNKNOWN (KS-T23).

## 5. Composition law: warrant ⊗, authority meet, scope intersection (KS-T20)

For components `x_1..x_n` and bridge/operator `(P_b, A_b, S_b)` (contract §3, §30), `admission.compose` produces the head with

\[
\Lambda=P_b\otimes\bigotimes_i\Lambda(x_i),\qquad
A=A_b\wedge\bigwedge_i A_i,\qquad
S=S_b\cap\bigcap_i S_i,
\]

via `warrant.meet_all_profiles`, `types.meet_authority` and `types.intersect_scopes`, and one COMPOSITION hyperedge carrying the bridge warrant. `types.Authority` is a product lattice of named non-negative ranks (`Authority.meet` = coordinate-wise minimum, missing = 0; order `<=` coordinate-wise), so corroboration on one coordinate never promotes another and composition never amplifies (`A_comp ⪯ A_b ∧ ⋀A_i`). `types.Scope` is a context set (`None` = universal) with a half-open epoch `[lo, hi)`; `Scope.intersect` intersects contexts and epochs; an empty result is the rejection `SCOPE_EMPTY`. `admission.ks_S2_composition` re-checks the law on every COMPOSITION head (genome KS-S2); `admission.admit` enforces it at the boundary (`KSO_CORE_V1.md` §8).

**KS-T20 (PROVED; parents: ATMS/provenance composition; lattice-based information flow, Denning 1976; WLL-4 union-scope countermodel).** The head is non-live whenever any component is (KS-T21 with `⊗`); the merge `⊕_iΛ(x_i)` outlives a revoked component and is not a composition.

## 6. Planted mutants (each must be caught; a mutation test asserts the mutant executed)

| defect (issue B3 / J3) | planted function in `src/ocm/kso/` | law it violates |
|---|---|---|
| union where intersection is required | `warrant.mutant_meet_as_union` | KS-T01 / KS-T20 (⊗) |
| dropped bridge warrant | `admission.mutant_compose_drop_bridge` | §5 composition law |
| merge instead of compose | `admission.mutant_compose_merge` | KS-T20 |
| duplicate evidence changes the result | no separate mutant; guarded by `warrant.canon` (idempotent minimisation) and `warrant.check_semiring` (`join(a, a) == a`); duplicate payloads are detected by `ids.EvidenceRegistry.is_duplicate` | KS-T01 idempotence |
| unknown treated as live | `warrant.mutant_unknown_as_live` | KS-T21 |
| unknown collapsed into dead | `warrant.mutant_unknown_as_dead` | KS-T21 |
| authority amplification / cross-axis promotion | `types.mutant_authority_max` | KS-T20 (meet) |
| scope union | `types.mutant_scope_union` | KS-T20 (WLL-4 countermodel) |
| feedback retains warrant | `admission.mutant_feedback_retains_warrant` | KS-T18 / KS-S1 |

## 7. Exhaustive calibration denominators (finite calibration, not proof authority)

Computed by running the checkers in `warrant.py` at `n = 3` (contract §21 for the inherited three):

| checker | quantity | value |
|---|---|---|
| `check_semiring(3)` | antichain profiles | 20 |
| | ordered pairs | 400 |
| | ordered triples (associativity, distributivity) | 8,000 |
| `check_three_valued_reduction(3)` | valid intervals (`lower ≤ upper`) | 168 |
| | homomorphism checks (168 × 168 × 8 revocations, ⊗ and ⊕ each) | 225,792 |
| | refinement-monotonicity checks | 27,920 |
| | reduction checks (20 certified profiles × 8 revocations) | 160 |

Registry rule: finite enumeration calibrates the implementation; the all-size statements rest on the proofs in §2 and §4.

## 8. Parents

| mechanism | parent | what the parent already owns |
|---|---|---|
| antichain labels, exact retraction | de Kleer, *An assumption-based TMS*, 1986 | assumption-set labels, alternatives, context switching |
| ⊕/⊗ propagation | Green, Karvounarakis & Tannen, *Provenance Semirings*, 2007 | semiring annotation propagation through composition |
| three-valued connectives | Kleene 1938 (strong logic); Belnap 1977 (four-valued reading, UNKNOWN as absence of information) | the truth tables of `kleene_and` / `kleene_or` |
| lower/upper interval | Pawlak 1982 (rough sets) | lower and upper approximation of a set |
| authority meet | Denning 1976 (lattice information flow) | non-amplifying lattice composition |
| scope intersection | WLL-4 union-scope countermodel (inherited) | union scope is unsound |

Nothing above is a KSO residual; `KSO_PARENT_SUBTRACTION_V1.md` lists every row as `PARENT_OWNED`.

# Lane #200 revival — rectangularity, decomposability, and the natural non-rectangular class

**Terminal: `NATURAL_NONRECTANGULAR_CLASSES_EXIST__ONE_NATURAL_NONDECOMPOSABLE_INSTANCE_REGISTERED__PARENT_OWNED`.**
**Residual `STRICT_WARRANTED_LIFECYCLE_RESIDUAL`: still `NOT_EARNED`; the obstruction is restated.**

Date: 2026-09-04 · Umbrella: #194 · Execution master: #197 · Lane: #200 (revival) · Reviews (unreturned): #199, #245
Exact checker: `reference/ocm_nonrectangular_class_exact.py` · Results: `results/OCM_NONRECTANGULAR_CLASS_EXACT_RESULTS_V1.json` · Tests: `tests/unit/test_ocm_nonrectangular_class_exact.py`

**Status: NO NOVELTY OR BREAKTHROUGH CLAIM.** This record takes the single named obstruction of
the first pass — *every registered class is rectangular; a residual needs a non-rectangular natural
class* (`OCM_LANE_200_TERMINAL_V1.md` §8) — as the lever the doctrine says it is, and works it to
a terminal. Three things happen: the criterion is stated precisely and turns out to be the wrong
coordinate for the obstruction; natural non-rectangular classes are shown to exist in abundance,
with the reason the registered ones were rectangular; and one natural instance is registered on
which the joint problem is provably *not* a product of two parent learners — and that instance is
owned by a named parent. `PARENT_OWNED` is a successful outcome and is said as such.

## 1. The criterion, stated precisely

Let `Omega` be a finite lifecycle class with current-behaviour map `B: Omega -> Bset` and warrant
map `Z: Omega -> Zset`; the lifecycle target is `L = (B, Z)`. Worlds with equal `L` are
identified (quotient by the target kernel), so `Omega` is the image of `L`.

**Definition R0 (coordinate rectangularity).** `Omega` is *rectangular* iff
`{(B(w), Z(w)) : w in Omega} = B(Omega) x Z(Omega)`. Equivalent forms: every behaviour fibre
carries every warrant value; `H_0(B, Z) = H_0(B) + H_0(Z)` (Hartley additivity);
`|Omega| = |B(Omega)| * |Z(Omega)|`.

**Decision procedure.** Count distinct pairs, distinct `B` values, distinct `Z` values; compare.
Invariant under relabelling of either value set and under the quotient above.

**Verification (§A of the checker).** The three committed classes WPL V1, WPL V2, WGPL
(2,048 worlds) satisfy R0; the three planted coupled classes COUPLED_FULL / HALF / FORCED
(648 worlds) fail it — the control fires. The first pass's claim stands as stated.

## 2. R0 is not the content of the obstruction

The obstruction's *intent* is Theorem D(ii): on a rectangular class the lifecycle problem is a
Cartesian product and the composition of two parent learners attains the exact query complexity.
What matters for a residual is therefore not the shape of `Im(B, Z)` but whether the joint problem
can be *decomposed into two parent problems*. That is a statement about strategies:

**Definition (sequential product, interaction term).** Fix a behaviour oracle (queries that are
functions of `B(w)`) and a warrant oracle (queries that are functions of `Z(w)`). Let `D(Omega)`
be the exact deterministic query complexity with both oracles. A *B-first* strategy determines
`B(w)` completely using behaviour queries and then identifies the world inside the fibre using
warrant queries; its exact cost is the optimum of a weighted decision tree on `B(Omega)` whose
leaf `b` costs `D(fibre_b | warrant queries)`. *Z-first* is symmetric. Let
`I(Omega) = min(B_first, Z_first) - D(Omega) >= 0`. `Omega` is *decomposable* iff `I = 0`.

**Theorem N1.** (i) Rectangular with cardinality-tight factor learners ⇒ decomposable
(Theorem D(ii)). (ii) Non-rectangular ⇏ non-decomposable: all three planted coupled classes have
`I = 0` (COUPLED_FULL 3 = 3, COUPLED_HALF 8 = 8, COUPLED_FORCED 9 = 9, each equal to the counting
bound, each certified by a simulated sequential strategy). (iii) `I > 0` is attainable: the planted
pointer-chasing class (8 worlds; `z_0` selects the live behaviour bit, which selects the live
warrant bit) has `D = 3`, `B_first = Z_first = 4`, `I = 1`, with an existence witness (a depth-3
tree exists, no depth-2 tree exists).

*Proof of (ii).* Each planted class is `Z = g(B, U)` with `U` free and `g(b, .)` injective
(COUPLED_FULL: `U` trivial; COUPLED_HALF: `U = {0,1}^5`) or has fibres of two sizes (COUPLED_FORCED,
64 and 32); in every case learning `B` first and then `U` inside the fibre meets `ceil(log2 |Omega|)`.
The checker establishes each value by two independently written exact solvers that must agree and by
simulating the optimal strategy on every world. ∎

**Consequence.** The lever "construct a non-rectangular class" is satisfiable by objects that leave
the obstruction untouched. The obstruction, restated in the coordinate that carries its content:
*a natural class with `I >= 1` whose joint optimum is not owned by a parent.* This is recorded in
`OCM_FAILURE_LEDGER.md` as `PRESENTATION_DEPENDENT_OBSTRUCTION`.

## 3. Where natural non-rectangularity comes from: the version-space warrant class

The registered classes carry their warrant as *planted independent bits* (backup certificates
`INDEX`-coded next to a parity). A real task family does not plant warrant; warrant is induced by
what the learner knows. The substrate's own object gives the induced form directly:

**Definition (VSW).** Let `X` be a finite domain and `C ⊆ {0,1}^X` a concept class. Evidence atoms
are the points of `X`: atom `a` is *certified* when the labelled example `(a, c(a))` has been
admitted. A world is `(c, S)` with `c in C` the concept and `S ⊆ X` the certified set. The
record for query point `x` is **live after revoking `R`** iff every concept consistent with the
surviving evidence `c|_(S \ R)` agrees at `x` — the version space's agreement region (Mitchell
1982). Its warrant profile is the antichain of minimal `J ⊆ S` on which the version space already
agrees at `x`: **the ATMS label of `x` induced by the hypothesis class** (de Kleer 1986), with the
certified examples as assumptions. `B = c`; `Z` = the liveness signature over all `(x, R)`.

The checker computes every profile as an antichain through the committed `rcl_model.canonical_profile`
and evaluates liveness through `rcl_model.live`; an independently written direct evaluator (version
space agreement) must agree on every `(world, x, R)` cell — 78,848 cells, 0 mismatches. So VSW is
the substrate's own warrant semantics on a concept class, not a new object bolted on.

**Theorem R (affinity).** For `C ⊆ F_2^X` nonempty, the following are equivalent:
(a) `VSW(X, C)` is rectangular; (b) the agreement region of every sample depends only on the sample's
points, not on its labels; (c) `C` is an affine subspace (a coset of a linear subspace) of `F_2^X`.

*Proof of (c) ⇒ (b).* Let `C = c_0 + V`. The concepts consistent with `(S, ℓ)` are
`c_1 + V_S` for any consistent `c_1`, where `V_S = {v in V : v|_S = 0}`; they agree at `x` iff
`v(x) = 0` for all `v in V_S` — a condition on `S` and `V` only. ∎ *(b) ⇒ (a)*: label-independence
makes every behaviour fibre carry the same set of signatures. *(a),(b) ⇒ (c)* is verified
exhaustively over every nonempty class on 2, 3 and 4 points (15 + 255 + 65,535 classes; the
counts `affine ∧ label-dependent` and `non-affine ∧ label-independent` are 0 in every census) and
is not claimed at all sizes by hand; the checker's affinity test is closure under `a + b + c`.

**Consequence.** WPL V1/V2 and WGPL are rectangular *because parity is affine* — the row-span
warrant of a linear class is label-independent (a matroid fact about the sample's inputs). "No
registered class is non-rectangular" was an artefact of registering only affine classes.
**Every non-affine concept class — conjunctions, threshold functions, DNF, decision lists,
singletons — is a natural non-rectangular lifecycle class**, and its non-rectangularity is
intrinsic: the same evidence warrants different queries under different concepts.

## 4. Decomposability of the natural classes

| class (VSW) | concepts | affine | R0 | worlds | `D` | B-first | Z-first | `I` | certified by |
|---|---|---|---|---|---|---|---|---|---|
| LINEAR_F2^2 (parities on 4 points) | 4 | yes | **yes** | 32 | 5 | 5 | 5 | 0 | both solvers; simulated strategies |
| MONO_CONJ_2 (monotone conjunctions, 2 vars) | 4 | no | no | 32 | 5 | 5 | 6 | 0 | same |
| LTF_2 (threshold functions on {0,1}^2) | 14 | no | no | 224 | 8 | 8 | 11 | 0 | simulated strategies; counting bound met |
| SINGLETONS_4 | 4 | no | no | 64 | 7 | 7 | 7 | 0 | both solvers; simulated |
| **SINGLETONS_5** | 5 | no | no | 160 | **8** | **9** | **9** | **1** | `D = 8` = counting bound (tree simulated); B-first 9 and Z-first 9 by solvers A and B agreeing and the composite strategies simulated on all 160 worlds |
| SINGLETONS + empty concept, 5 points | 6 | no | no | 192 | 10 | 10 | 10 | 0 | same |

Every class on 3 points is decomposable (255/255, exploratory sweep). On 4 points a random sample of
300 classes found one search-found class with `I = 1` (7 concepts, 112 worlds, `D = 7`, B-first 8),
verified by an independent existence search; it is not a named family and is recorded, not
registered. A full 4-point census was left running at the time of writing and is reported in the
receipt if it finished.

**The registered natural non-decomposable instance is `SINGLETONS_5`** — the class
`{e_a : a in X}`, `|X| = 5`, which is Angluin's own example of a membership-query lower bound
(`m − 1` queries for `m` concepts, against `ceil(log2 m)` bits). Mechanism, verified on every cell:
for `x` outside the surviving evidence `J = S \ R`, `live(x, R) = [c in {e_a : a in J}]` unless
`X \ J = {x}` (elimination; 25 of 400 cells), i.e. **liveness queries on singletons are Angluin
subset queries** ("is the target in this sub-class?"), which halve the version space where
membership queries split it 1 : m−1. The joint learner uses them and meets the counting bound; a
learner forced to settle behaviour first pays `D_MQ(singletons_5) = 4` and then 5 for the fibre.

## 5. Candidates from the brief, each with its strongest parent

| candidate seam | is it non-rectangular? | decomposable? | strongest parent | disposition |
|---|---|---|---|---|
| (a) warrant depending jointly on *which channel* delivered a procedure and *when* authority changed | No, on the substrate: `live()` is a function of `(profile, complete, R)`; channel enters only through `complete` (closure vs positive-only), epoch never enters; the class `{(B, channel, epoch, profile)}` is a product because `B` is chosen independently | product | **ATMS labels are derivation-history-free** (de Kleer 1986: a label depends on its environments, not on when or how the node was derived); epoch-window scope is context/scope intersection (S2, WLL-4); revocation-by-epoch is a family `Γ` handled by S4 | `PARENT_OWNED` |
| (b) composed skill whose warrant is not a function of the component warrants | Only when the composite carries a *direct* justification; then `profile(p∘q) = min(unions ∪ direct)` — a function of `(Z_p, Z_q, Z_direct)`, rectangular in generating coordinates | product (twisted) | ATMS label update under multiple justifications (label = minimal environments over all derivations) | `PARENT_OWNED` |
| (c) representation change altering which retractions are recoverable | S4 says exactly which `R` a coarsening answers; if the admitted family `Γ` is hidden and *adversarial* (targets warrants that matter), `Γ = g(profile)` is derived, hence a twisted product | product | Blackwell/L1 (coarsest sufficient partition), L4 conservation, CEGAR reopening; adversarial deletion is deletion-robust / certified unlearning (`P-UNLEARN-SPACE-2025`) | `PARENT_OWNED` |
| (d) **version-space warrant** (this record) | **Yes, for every non-affine class** (Theorem R) | not always: `SINGLETONS_5` has `I = 1` | Mitchell 1982 (version space); **Angluin 1988** (query types — subset queries; the singletons lower bound); Hegedüs 1995 (extended teaching dimension = membership-query complexity); **Balcázar–Castro–Guijarro 2001, Castro et al. 2002** (general / abstract identification dimension: exact query complexity for *any* set of query types); de Kleer 1986 (the label) | `PARENT_OWNED`: the joint optimum on `{membership, liveness}` is the general dimension of that protocol; the interaction term is the gap between the mixed and the sequential protocols on one class — a class-specific quantity, not a theorem about the substrate |

Absorbed, not avoided: the parent that owns (d) is the one the first pass named in advance
("ordinary exact learning of a joint concept with two query types, Angluin 1988"). What is new
relative to the first pass is only that the concrete instance now exists and the second query type
is identified: the substrate's liveness query is, on this class, a subset query.

## 6. What this does and does not change

- **RCL-C, item 5** ("a lower bound for the strongest parent product at the same information").
  Read as the *sequential* product — trace-learner for behaviour, then provenance/INDEX for warrant —
  `SINGLETONS_5` is a lower bound against it by one query at equal information, certified. Read as
  the *adaptive* parent — exact learning under the mixed query protocol — the parent contains the
  joint learner, and no lower bound against it is possible. RCL-C: `NOT_EARNED__NONDECOMPOSABLE_INSTANCE_PARENT_OWNED`.
- **Blindness.** Non-rectangular classes are not blind (Theorem D(iii)); on VSW the current-function
  oracle leaks warrant because warrant is *induced by* the concept. The programme's use of blindness
  as the residual's signature is therefore a property only planted-warrant classes can have.
- **The separation claim.** Non-rectangularity, and even non-decomposability, does not make the
  approximator-FAILS verdict reachable at equal information; see `OCM_SEPARATION_TEST_REAUDIT_V2.md`
  (Theorem N2, class-independent).

## 7. Checker denominators and controls

R0: 2,048 registered worlds pass, 648 planted fail. Decomposability: 3 planted classes certified
decomposable, pointer control certified non-decomposable with existence witness, rectangular
control decomposable. Affinity census: 65,805 classes, both off-diagonal counts 0. ATMS-label
cells: 78,848 with 0 mismatches. Subset-query identity: 128/128 (4 points), 400/400 (5 points).
Mutations asserted applied then detected: M1 sequential cost by the first-draft formula
`D_first + max fibre` (overstates LTF_2's Z-first by one; the simulated strategy refutes it),
M2 subspace test on a non-zero coset, M3 label-independence over the empty sample only (vacuous),
M4 joint solver without warrant queries (the pointer control cannot fire). Exit `2 = CANNOT_CHECK`
is never a pass. Two checker defects were made and caught while writing (see the failure ledger):
an earlier draft pruned the factor solver on the world count and reported a spurious `I = 1` on
MONO_CONJ_2; the sequential-cost formula was then found not to be the cost of any strategy.

## 8. Non-consequences and reopen conditions

Supported: R0 and its verification; Theorem N1; Theorem R with (c)⇒(b) by hand and the equivalence
verified on ≤ 4 points; the registered instance `SINGLETONS_5` with `I = 1`; the parent assignments.
Not supported: literature priority, novelty, an all-size Theorem R, architecture, language, quantum,
publication, or any separation between learners. No checkbox in #197 is closed (OPS-012); #199 and
#245 remain unreturned and were not simulated.

Reopens if: a natural class with `I >= 1` is exhibited whose joint optimum is *not* the general
dimension of a registered query protocol (i.e. a bound that is about the substrate's constraints,
not about a concept class); Theorem R's (a)⇒(c) fails at some size; or an independent review finds
a defect in N1, R, or the certified values.

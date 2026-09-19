# FREEZE_V1 — GMI #833 Section I: update-law regimes for seven external signatures

**This file is committed BEFORE any implementation commit. Git order is the evidence.**

- `source_main`: `bfb7d8c296a60c0bc76632ed69551540644e74e6`
- direct parent branch merged into this worktree: `research/833-i-core` at
  `e017e081de4a521bb4c0916a525630daa989760b` (PR #1014, package
  `research/gmi-833-update-law-space-v1`)
- package: `research/gmi-833-update-law-regimes-v1`
- branch: `research/833-i-rest`
- frozen (UTC): 2026-09-18

**Claim ceiling (pre-committed, may not be widened by any later file):**

```
GMI_833_SECTION_I_UPDATE_LAW_REGIME_CONDITIONS_AND_PROSPECTIVE_SELECTOR_AT_REGISTERED_FINITE_SCOPE
```

Evidence level EV1 (deductive, explicit premises and falsifiers) plus EV2 (exact
finite certificates over declared universes). **Not EV3, EV4 or EV5.** Maturity
M1-M2. Nothing here is validated on real trained systems.

---

## 0. Rows this tranche may reconcile, and only these

Anchor line, verbatim:

```
# I. Learning-law derivation without algorithm priors
```

Candidate rows, verbatim from the issue body at `source_main`:

```
- [ ] Derive conditions favoring Bayesian update behavior.
- [ ] Derive conditions favoring memory/exemplar update.
- [ ] Derive conditions favoring rule induction.
- [ ] Derive conditions favoring program/library learning.
- [ ] Derive conditions favoring evolutionary/population search.
- [ ] Derive conditions favoring meta-learning.
- [ ] Derive conditions favoring self-modification.
- [ ] Build a prospective learning-law selector.
- [ ] Recover selected learning laws under neutral search.
- [ ] Test held-out crossover boundaries.
- [ ] Test on realistic learning systems.
```

**No neighboring row is earned here.** In particular the four rows closed by the
direct parent (`Define the space of admissible update laws architecture-neutrally`,
`Derive conditions favoring local trial-and-error updates`,
`Derive conditions favoring directional/gradient information`,
`Derive reverse-mode credit assignment from graph/resource structure rather than
naming backprop`) are NOT re-claimed, and no row outside Section I is touched.

**Pre-committed abstention.** `Test on realistic learning systems` is expected to
remain OPEN. It is listed above only because it is in this tranche's scope; the
rule pre-committed here is: **it closes only on real trained systems with
sha256-bound real data sources and predictions frozen before outcomes, following
`research/gmi-833-real-transition-receipts-v1` (#903). Synthetic data may not
close it.** If real systems are not reached in this round the row is reported
open, by name, in `CORE.md` and in the reconciliation JSON's `rows_not_closed`.

---

## 1. What the parents own, and what is left

`PARENT_OWNERSHIP_V1.md` carries the full disclosure with citations. The binding
statement frozen here:

- **#870** (`gmi-833-update-law-nfl-v1`) owns the no-free-lunch boundary: a useful
  preference between update laws requires stated ecological, informational and
  resource assumptions. Every row below is therefore of the form *which stated
  assumption class favours which external signature*, and is stated relative to a
  registered assumption set. No universal preference is claimed.
- **#1014** (`gmi-833-update-law-space-v1`) owns the admissible update-law space
  `A_k` over the #837 realization contract (IL-1), the evaluative-versus-directional
  crossover `rho*` (IL-2/IL-3) and the accumulation-direction recovery (IL-4).
  **Every regime defined here is a subset of that space.** No new space is defined.
- **#897** (`gmi-833-g0-grammar-growth-v1`) owns grammar growth `G_t -> G_{t+1}`,
  recursive library formation / primitive invention, the lifecycle threshold
  `H_eff * Delta > K`, and the held-out reuse study. **The `program/library
  learning` row is pre-committed to the reconciliation route**: this tranche
  places #897's already-earned condition inside the update-law space and states
  the demarcation. It does NOT re-run or re-derive the invention result and
  claims no novelty for it.
- **#848 / #874 and the governed-self-change package** own governed self-change
  and its authority contract. The `self-modification` row here is a **cost and
  reachability** statement inside `A_k`, not a governance statement. Nothing here
  licenses a self-promoting or self-signing law.
- Literature parents: de Finetti (1937) exchangeability; Savage (1954); Cover &
  Hart (1967) nearest-neighbour; Aha, Kibler & Albert (1991) instance-based
  learning; Rissanen (1978) MDL; Holland (1975); Rechenberg (1973);
  Schwefel (1977); Droste, Jansen & Wegener (2002) (1+1)-EA;
  Baxter (2000) inductive bias learning; Thrun & Pratt (1998);
  Wolpert & Macready (1997); Schmidhuber (1987, 2003) self-referential learning.
  All own their results; none of them states the finite exact crossover inside a
  registered architecture-neutral law space, which is the residual claimed here.

**Named residual of this tranche.** Seven *external structural signatures* on
laws in `A_k`, each defined without naming any mechanism; for each, an exact
rational dominance threshold in registered ecology invariants together with a
matched converse, five of which are unconditional; an exact statement of which
signature predicates are jointly satisfiable (a compatibility matrix, explicitly
NOT asserted to be a partition); an unconditional argmin-cell partition of the
positive price space with its crossover hyperplanes; and a prospective selector
frozen before its census.

---

## 2. Registered scope `S_L`

All arithmetic is exact (`fractions.Fraction` / `int`). **No float appears in
any claim.** A float anywhere in a registered price, probability, score or loss
is a hard refusal (hostile `HR-02`).

### 2.1 The price vector (commensuration decided HERE, before any run)

```
pi = (p_test, p_carry, p_store, p_build, p_branch, p_meta, p_mut, lam)  in  Q_{>0}^8
```

| coordinate | charges one unit of |
|---|---|
| `p_test`  | one elementary evaluation of one candidate on one instance |
| `p_carry` | retaining one candidate-indexed weight slot for one step |
| `p_store` | retaining one observed instance for one step |
| `p_build` | constructing one description symbol |
| `p_branch`| maintaining one ADDITIONAL parallel candidate for one step |
| `p_meta`  | retaining one cross-episode slot for one episode |
| `p_mut`   | one change of the admissible successor set |
| `lam`     | one unit of registered loss on the held-out query set |

**Loss commensuration (frozen decision, not deferred).** Total charge of a law
`L` on a registered environment `E` is

```
C(L, E, pi) = < a(L, E), pi >,      a(L,E) in Z_{>=0}^8
```

where the eighth coordinate of `a` is the law's exact integer loss on the
registered held-out query set. Resource charge and loss are therefore commensurated
**inside the single price vector** by the explicit loss price `lam`. The
alternative (restricting to iso-loss ecologies) is rejected here and may not be
substituted later; substituting it after seeing a census would be the #976
`POST_HOC_SUSPECT` shape.

Because `a` has nonnegative integer entries and `pi` is positive, every `C` is an
exact rational and every comparison is an exact rational comparison.

### 2.2 The registered environment

A registered environment is

```
E = (Z, H, prior, eps, target, train, Qset, retr, RS, nbr, Vfun, starts, Fam)
```

- `Z` — a finite instance set, presented as an explicit tuple; `nz = |Z|`.
- `H` — a finite candidate set, each candidate an explicit total map `Z -> {0,1}`;
  `M = |H|`. `H` is a set of tables. It carries no architecture.
- `prior` — exact rational weights on `H`, summing to `1`.
- `eps` — a registered exact rational noise rate, **frozen at `eps = 1/4`**, used
  in the likelihood `eps^(#disagreements) * (1-eps)^(#agreements)`. Frozen here so
  that no later run may tune it.
- `target` — an explicit total map `Z -> {0,1}`. It may lie in `H` (the registered
  stable generative structure is present) or outside `H` (it is absent). Both
  cases are registered.
- `train` — a tuple of `T` instances of `Z` (repeats permitted), each observed
  with its `target` label.
- `Qset` — a tuple of `nq` instances of `Z`, **disjoint from the set of instances
  appearing in `train`**.
- `retr : Qset -> train-index` — a registered structural retrieval map: each query
  names the stored training position it retrieves. Structural, declared per
  environment, never learned.
- `RS` — a registered production space: a finite tuple of productions, each a pair
  (a subset of `Z` it fires on, an output bit) with a registered description
  length `len >= 1`.
- `nbr : H -> tuple of H` — a registered undirected neighbour relation.
- `Vfun : H -> Q` — a registered exact rational score.
- `starts` — a registered tuple of elements of `H`, the single-incumbent start set.
- `Fam` — a registered episode family: `K` environments sharing `Z` and `H`, whose
  targets all lie in a registered sub-family `H' subset H`; `k0` is the registered
  number of leading episodes the cross-episode slot needs before it is informative.

**All derived quantities are COMPUTED by the executor from `E`, never asserted:**
`M`, `T`, `nq`, the exact posterior, `alpha_gain`, `mu`, `Dmin`, `cover`, `disc`,
the local optima of `(H, nbr, Vfun)`, `Vglob`, `Vloc`, `Bmin`, `Tsteps`,
`r = M - |H'|`, and every per-law loss. Both routes compute them independently.

**Tie rules, declared here.** Every argmax/argmin over candidates breaks ties by
smallest index in the registered tuple order. Every predictor tie (weight exactly
split) predicts `0`. These are declared, not discovered, and are part of the
frozen scope.

### 2.3 The registered environments

Twelve environments are registered. **Six are the DERIVATION set** (`D1`..`D6`),
on which thresholds are derived and reported. **Six are the HELD-OUT set**
(`X1`..`X6`), used only in section 6, after the derivation-set census is written.
The construction rules of all twelve are frozen here; their computed invariants
are not known at freeze time and are not predicted numerically.

Derivation set, by the structural property each isolates:

| id | structural property registered |
|---|---|
| `D1` | target in `H`, prior diffuse, query set chosen so weighted and single-best predictions can differ |
| `D2` | target in `H`, posterior concentrates on one candidate before the last step |
| `D3` | target NOT in `H` (no registered stable generative structure) |
| `D4` | retrieval map re-queries only a strict subset of the stored instances |
| `D5` | `(H, nbr, Vfun)` has two local optima with distinct scores |
| `D6` | `(H, nbr, Vfun)` is unimodal (exactly one local optimum) |

Held-out set `X1`..`X6`: the same six structural properties, instantiated over a
DIFFERENT instance set and a DIFFERENT candidate table (declared in section 6).

### 2.4 The price grid

The numeraire is `p_test = 1`. The **pairwise threshold grid** is the 46 reduced
fractions `a/b` with `1 <= a <= 12`, `1 <= b <= 6` — the same grid the direct
parent pre-committed, adopted unchanged so that no grid was chosen after seeing an
outcome. The **joint census grid** is the product over the seven non-numeraire
coordinates of `{1/4, 1, 4}`, i.e. `3^7 = 2187` price vectors, crossed with the
six derivation environments: `13122` joint cases.

---

## 3. The seven external signatures

A signature is a predicate on a law's **trace** (its sequence of charged channel
calls) and its **emitted predictor**. No signature mentions an architecture, a
family, an optimizer, a representation or an algorithm; section 8 verifies that
mechanically rather than asserting it.

| id | external signature predicate |
|---|---|
| `SIG-W` | the carried state at every step is a normalized exact-rational weighting over `H` equal to the exact conditional of `prior` given the observed prefix, and the emitted predictor is the weighted majority |
| `SIG-X` | no candidate-indexed weight slot is carried; the emitted predictor's value at a query is a function of the stored observed instances only, through `retr` |
| `SIG-R` | the emitted predictor is a finite set of conditioned productions whose total registered description length is strictly less than the description length of the instance set it covers, and no observed instance is retained after emission |
| `SIG-L` | `SIG-R` holds AND at least one sub-description is re-invoked at more than one invocation site, charged once per site |
| `SIG-P` | a multiset of at least two candidates is carried and the successor is a function of a selection over that multiset |
| `SIG-T` | the step rule is indexed by a parameter carried ACROSS episodes and updated between them |
| `SIG-S` | the admissible successor set the law is evaluated against changes during the episode |

**These seven predicates are NOT asserted to partition law space.** Section 5.1
computes the exact 21-pair compatibility matrix. Asserting a non-partitioning
taxonomy as a partition is the defect corrected in
`research/gmi-833-capability-interaction-partition-v1` (DEF-2, PR #1011) and this
freeze pre-commits to not reproducing it.

---

## 4. The seven derivations, frozen in form

Each row below fixes the **form** of its threshold. The numbers are computed by
the executor. `[num]` marks a value not known at freeze time.

### 4.1 `SIG-W` — exact conditional weighting

Comparator: the **single-best point summary** — same tests, carrying one slot
instead of `M`, emitting the single highest-weighted candidate's prediction.

- Extra charge of `SIG-W`: `p_carry * (M - 1) * T`.
- Value of `SIG-W`: `lam * alpha_gain`, where
  `alpha_gain = #{q : point summary wrong and weighted right} - #{q : weighted wrong and point summary right}`,
  an exact integer computed from `E`.
- **Threshold:** `SIG-W` strictly dominates the point summary iff
  `p_carry / lam < beta*(E) := alpha_gain / ((M - 1) * T)`.
- **Matched converse, claimed UNCONDITIONAL:** if `alpha_gain <= 0` then
  `beta* <= 0` and `SIG-W` is strictly dominated at EVERY positive price vector.
  Falsifier: a registered `E` with `alpha_gain <= 0` where `SIG-W` is not strictly
  dominated at some positive price.
- Pre-committed expectation of the mechanism: `alpha_gain > 0` should require the
  registered stable generative structure to be present AND the posterior to stay
  spread. `D2` (concentrating) and `D3` (structure absent) are registered
  precisely so this can fail, and a failure is reported, not hidden.

### 4.2 `SIG-X` — stored-instance retrieval

- **Wastefulness lemma, claimed UNCONDITIONAL:** an instance that no query
  retrieves may be deleted from the store with no change to the emitted predictor
  and a strictly lower charge whenever `p_store > 0`. Hence the minimal-charge
  law with `SIG-X` stores exactly the retrieved set, of size `mu`.
- Comparator: the compression law (`SIG-R`).
- **Threshold:** with every price but `p_store` at the registered unit, `SIG-X`
  strictly dominates `SIG-R` iff `p_store < chi*(E)`, where `chi*` is the exact
  rational obtained by solving the two affine costs for equality. Its general form
  is the crossover hyperplane `<a_X - a_R, pi> = 0`.
- Matched converse: above `chi*` the compression law strictly dominates.
- Falsifier: a registered `E` where deleting a never-retrieved instance changes the
  emitted predictor.

### 4.3 `SIG-R` — production compression

- **Threshold:** compression pays its discovery charge iff
  `(cover - Dmin) * (p_carry * T + p_test * nq) > p_test * disc + p_build * Dmin`,
  with `disc = |RS| * T` the registered discovery charge and `Dmin` the minimum
  total description length of a consistent covering subset of `RS` of size at most
  the registered `kmax = 3`. In the reduced two-price form (all other prices at
  unit) the boundary is `p_build < psi*(E)`, an exact rational.
- The threshold is **relative to the registered `RS`**, which is declared per
  environment in the frozen construction rules and may not be enlarged after a run.
- Matched converse: below the amortization horizon the uncompressed law dominates.

### 4.4 `SIG-L` — reuse-indexed construction

**Pre-committed to the RECONCILIATION route.** #897 owns the invention result and
its lifecycle threshold `H_eff * Delta > K`. This tranche states the demarcation
and places the condition in the law space:

- `SIG-L` refines `SIG-R` by charging a re-invoked sub-description once per
  invocation site rather than once per occurrence. The extra admissible structure
  is exactly #897's `G_t -> G_(t+1)`.
- **Threshold (the same inequality in this tranche's units):** `SIG-L` strictly
  dominates `SIG-R` iff `Hocc * Delta > Kdef`, where `Hocc` is the number of
  invocation sites, `Delta` the per-site symbol saving and `Kdef` the definition
  length plus its maintenance. Computed from `E`, reported, and checked to agree
  in sign with #897's earned result.
- **No novelty is claimed for the invention result, the grammar growth, or the
  held-out reuse benefit.** If the computed condition adds nothing beyond #897 at
  its stated strength, the row is closed BY RECONCILIATION TO #897 and says so.

### 4.5 `SIG-P` — breadth selection

- Mechanism: the local-optimum structure of `(H, nbr, Vfun)`. A single incumbent
  ascends to the local optimum of its start's basin; a breadth-`B` law covering the
  global basin reaches `Vglob`.
- **Threshold:** `SIG-P` strictly dominates the single incumbent iff
  `p_branch / lam < pistar*(E) := (Vglob - Vloc) / ((B - 1) * Tsteps)`.
- **Matched converse, claimed UNCONDITIONAL:** if `(H, nbr, Vfun)` is unimodal then
  every start ascends to the same optimum, `Vglob - Vloc = 0`, `pistar* = 0`, and
  every additional carried member is strictly wasteful at every positive price.
  `D6` is registered to exercise exactly this.
- Falsifier: a unimodal registered `E` where breadth strictly helps.

### 4.6 `SIG-T` — cross-episode indexing

- Registered relatedness `r := M - |H'| >= 0`, computed from `Fam`.
- **Threshold:** `SIG-T` strictly dominates the base law over the `K`-episode family
  iff `p_meta / p_test < tau*(E) := r * T * (K - k0) / (|H'| * K)`.
- **Reduction falsifier, claimed UNCONDITIONAL, and this is the row's falsifier:**
  when `r = 0` the carried cross-episode parameter is the constant `H`, the indexed
  step rule equals the base step rule **on every registered input** — behavioural
  identity is to be verified pointwise over all registered `(episode, step)` pairs,
  not merely inferred from equal cost — and the charge exceeds the base charge by
  `p_meta * M * K > 0`. So `SIG-T` is strictly dominated at every positive price.
  Falsifier: a registered family with `r = 0` where the two rules differ at any
  registered input, or where `SIG-T` is not strictly dominated.

### 4.7 `SIG-S` — successor-set change

Two readings are distinguished, both frozen here, because they have different
answers and conflating them would be an over-claim.

- **Reading (a), mode selection.** The law selects, at each registered triple,
  which of a registered family `{L_i} subset A_k` to apply.
  **`UL-1` (pointwise-selection closure), claimed UNCONDITIONAL:** `A_k` is closed
  under pointwise selection — for any selector `s : R x HIST x Bgrid -> I` and any
  `{L_i} subset A_k`, the law `L(r,h,b) := L_{s(r,h,b)}(r,h,b)` is in `A_k`, because
  the parent's `A1`-`A4` are a pointwise conjunction over presented triples. This
  strictly generalizes the parent's IL-1.2 mixture closure (mixture is the
  distributional special case) and it absorbs HISTORY-DEPENDENT switching, which
  the parent's composition operator does not.
  **Consequence:** under reading (a) the conditions favouring `SIG-S` are **EMPTY**:
  the self-modifying law is extensionally equal to a fixed member of `A_k` and pays
  `p_mut > 0` on top. Strictly dominated at every positive price.
- **Reading (b), successor-set extension.** The law changes the grade it is
  admissible against, reaching realizations no fixed law of the comparison class
  can reach. **Threshold:** `SIG-S` strictly dominates the best fixed law of the
  class `A_reg` iff `p_mut / lam < s*(E) := (loss of best in A_reg) - (loss of best
  reachable after the change)`, which is strictly positive exactly when the change
  reaches a strictly better region.
  **Matched positive, from the parent's own counterexample:** `A_1` (the ONE_STEP
  grade) is NOT closed under composition (parent IL-1.3, EARNED-BY-COUNTEREXAMPLE:
  the composite places mass at `r2` where `Succ_ONE_STEP(r0,h0) = {r0,r1}`). So a
  law confined to `A_1` that changes its successor set reaches `r2`, which no fixed
  `A_1` law can. If `r2` carries strictly the best registered score, `s* > 0`.
  **Matched negative:** if the reachable set after the change is contained in the
  comparison class, `s* = 0` and the law is strictly worse by exactly its overhead.
- **Frozen convention:** `p_mut > 0` always. A zero mutation charge is not
  registered; the `p_mut = 0` tie is reported as a boundary, never as a win.

---

## 5. Joint structure

### 5.1 Compatibility matrix — NOT a partition

For each of the `C(7,2) = 21` unordered signature pairs the executor returns
either `COMPATIBLE` with an explicit witness law satisfying both predicates, or
`EXCLUSIVE` with the exact clause pair that cannot hold together. The matrix is
reported as a matrix. **The word "partition" is not applied to it.**

### 5.2 `UL-10` — the argmin-cell partition of the price space

**Statement, claimed UNCONDITIONAL, `forall[pi in Q_{>0}^8]`.** Fix a registered
`E` and the seven representative coefficient vectors `a_1..a_7 in Z_{>=0}^8`. The
sets

```
Cell_i = { pi > 0 : <a_i,pi> < <a_j,pi> for all j != i }
Tie_S  = { pi > 0 : argmin is exactly the set S, |S| >= 2 }
```

are pairwise disjoint and their union is all of `Q_{>0}^8`. The `21` crossover
surfaces are the exact hyperplanes `<a_i - a_j, pi> = 0`, reported with exact
integer normal vectors. **The theorem is deductive and its scope is every positive
price vector; the census in 5.3 exhibits cells and is `forall_fin` over a grid. The
grid's coverage is NOT the theorem's scope and may not be reported as such.**

### 5.3 Reachability of each cell

For each `(E, i)` the executor reports exactly one of:

- `WITNESSED` — a grid price vector at which `i` is the strict argmin, with the
  witness recorded so Route B can verify it independently;
- `DOMINATED_EVERYWHERE` — some `j` with `a_j <= a_i` coordinatewise and
  `a_j != a_i`, an unconditional certificate that `i` is never argmin at any
  positive price, with the dominating index recorded;
- `UNDETERMINED_AT_REGISTERED_SCOPE` — neither. This is reported as an open
  question, never as an absence.

**Empty cells are a finding and are reported as such**, with the count, per
environment.

### 5.4 Soundness scope of every dominance claim

Every dominance statement in section 4 and 5 is scoped to **the seven registered
representatives and their rational mixture hull**. The hull extension is licensed
by the parent's IL-1.2: a mixture's charge is the convex combination of the stage
charges, so the argmin over the pure representatives is the minimum over the whole
hull. **Nothing broader is claimed.** `BEST_LAW_IN_A_STAR` is a forbidden
promotion.

---

## 6. The prospective selector, its decision table, frozen

`select(E_invariants, channel, pi) -> regime | typed abstention`

**The decision table below is frozen before any census is run.**

```
INPUT   the computed invariant record of E, the registered channel declaration,
        and a price vector pi in Q_{>0}^8.

STEP 1  If any invariant required by any of the seven representatives is absent
        from the record, return ABSTAIN_UNDERDETERMINED with the missing key.
STEP 2  If any coordinate of pi is not a positive exact rational, return
        ABSTAIN_ILL_TYPED.
STEP 3  Compute the seven exact charges C_i = <a_i(E), pi>.
STEP 4  If the argmin is a unique index i, return REGIME_i.
STEP 5  Otherwise return ABSTAIN_TIE with the exact tied index set.
```

- The function is **total** on its declared input type and **deterministic**.
- **Soundness (the claim):** whenever it returns `REGIME_i`, `a_i` attains the
  strict minimum charge among the seven representatives and their rational mixture
  hull at `pi`. Proof obligation: strict argmin plus the IL-1.2 hull argument.
- **Abstention is typed, not silent.** Three typed abstentions and no fourth.
- "Prospective" here means exactly this: the table above is in the freeze commit;
  the census that exercises it is in a later commit; `git log` is the evidence.

---

## 7. Neutral-search recovery, frozen

**The neutral law grammar.** A law is a tuple of structural switches:

```
g = (carry, store, build, breadth, meta, mut)
carry   in {0, 1, M}            candidate-indexed weight slots retained per step
store   in {0, mu, T}           observed instances retained per step
build   in {0, Dmin, Dmin_L}    description symbols constructed
breadth in {1, Bmin, M}         candidates carried in parallel
meta    in {0, |H'|}            cross-episode slots retained per episode
mut     in {0, 1}               successor-set changes
```

`3*3*3*3*2*2 = 324` tuples per environment; `324 * 6 = 1944` enumerated laws on
the derivation set. The enumeration is exhaustive; there is no search heuristic
and therefore no heuristic to bias.

**Blindness, structural.** No tuple coordinate, no objective term and no tie rule
names a family, a signature or a mechanism. The objective is exactly
`<a(g,E), pi>` — the same charge function as everything else. The signature of the
argmin tuple is computed **afterwards** by applying the section-3 predicates to the
tuple's induced trace. The label is never an input.

**The claim to be tested:** on every registered `(E, pi)` case where `select`
returns a regime, the blind argmin tuple's derived signature equals that regime.
Where `select` abstains on a tie, the blind argmin must be tied over the same set.
**Mismatches are reported with their case, not suppressed.**

---

## 8. Held-out crossover boundaries, predictions frozen BEFORE outcomes

Held-out environments `X1`..`X6` are built by the frozen rules of section 2.3 over
a different instance set and candidate table. They are **not** used to derive any
threshold. The following predictions are frozen now:

- **`HO-P1`** For every held-out environment and every threshold of section 4 that
  is defined there, the closed-form threshold value equals, EXACTLY, the crossover
  located independently by exact rational bisection on the two affine charges —
  where the bisection uses only the charge evaluator and never the closed form.
  Predicted hit rate: **6/6 environments on every defined threshold**.
- **`HO-P2`** On the held-out joint grid, `select`'s regime agrees with the blind
  enumeration argmin's derived signature in **every** case where `select` returns a
  regime.
- **`HO-P3`** The unconditional converses hold on the held-out set: on any held-out
  environment with `alpha_gain <= 0`, `SIG-W` is argmin at no grid price; on any
  unimodal held-out environment, no `breadth > 1` tuple is argmin at any grid price.
- **`HO-P4`** At least one held-out environment produces a `DOMINATED_EVERYWHERE`
  certificate, i.e. the empty-cell finding is not an artefact of the derivation set.

**A miss is a lead, not a failure to hide.** Every miss is reported with its case,
its predicted and observed value, and a single-stage attribution.

---

## 9. Verification contract

1. **Two materially independent routes.** Route A (`update_law_regimes_v1.py`) and
   Route B (`oracle_update_law_regimes_v1.py`). Route B imports nothing from Route
   A, shares no helper module, transcribes the registered environments
   independently, and derives every verdict from literal enumeration rather than
   from any closed form. Before any agreement figure is reported, a scope
   fingerprint computed independently by each route must match; a drift there makes
   every agreement number meaningless and is checked, not assumed.
2. **Hostiles, all to be DETECTED.** Registered now:
   `HR-01` non-normalized prior; `HR-02` float price refused; `HR-03` float
   probability refused; `HR-04` a never-retrieved instance deleted yet the emitted
   predictor changes (the wastefulness lemma's falsifier, planted); `HR-05` the
   `SIG-W` threshold shifted by one in the denominator (`M` for `M-1`);
   `HR-06` a claimed partition of the seven signature predicates (the CIU DEF-2
   shape, planted, must be refused); `HR-07` `SIG-T` declared to beat the base law
   at `r = 0`; `HR-08` `SIG-P` declared to beat the single incumbent on a unimodal
   environment; `HR-09` `SIG-S` declared to beat the best fixed law inside a
   pointwise-selection-closed class; `HR-10` a tie silently absorbed into a regime
   cell (gapped argmin); `HR-11` a `DOMINATED_EVERYWHERE` certificate whose
   dominating vector is not coordinatewise `<=`; `HR-12` planted mechanism-named
   identifiers in the search grammar (the blindness screen's recall test);
   `HR-13` the selector made partial by dropping a typed abstention;
   `HR-14` a held-out prediction evaluated after the outcome is known (ordering
   hostile: the predictions above must hash-match the freeze blob).
3. **Nulls.** (i) `200` randomized regime assignments per environment must fail to
   reproduce the blind argmin's signature more often than chance; (ii) `200`
   shuffled thresholds drawn from a different registered environment must fail to
   locate the exact crossover of the target environment, and the true threshold
   must locate it on every environment; (iii) each null is shown non-vacuous by
   exhibiting a case where it CAN fire.
4. **Determinism.** `RESULT_V1.json` byte-identical under `python3 -I -B` and
   `python3 -I -O -B`. No claim gated by a bare `assert`.
5. **Name-freedom screen.** The parent's `A1` lexical screen, extended. Denylist =
   the parent's 26 entries plus this tranche's additions. `DENYLIST_V1.json` carries
   occurrence-level allowances with reasons; a hit with no allowance fails, and an
   allowance never exercised fails. **Strictly clean (zero hits, no allowance may
   name them):** `update_law_regimes_v1.py`, `oracle_update_law_regimes_v1.py`,
   `test_update_law_regimes_v1.py`, `CORE.md`, `RESULT_V1.json`,
   `ORACLE_RESULT_V1.json`. Prose and governance files may carry justified
   occurrences; the routes, the tests and the receipts may not.
6. **Execution host.** All runs on `laptop-billy` (`python3` 3.8.10), never on the
   Mac. Standard library only.

---

## 10. Forbidden promotions (pre-committed)

```
UNIVERSAL_BEST_UPDATE_LAW
BEST_LAW_IN_A_STAR
ALL_UPDATE_LAWS_ENUMERATED
SEVEN_SIGNATURES_PARTITION_LAW_SPACE
SIGNATURE_TAXONOMY_IS_EXHAUSTIVE
ARCHITECTURE_PRIOR_FREE_IN_ABSOLUTE_SENSE
NEUTRALITY_PROVEN_SEMANTICALLY_COMPLETE
NAMED_ALGORITHM_DERIVED_AS_NECESSARY
LIBRARY_INVENTION_RESULT_IS_NOVEL_HERE
GRAMMAR_GROWTH_OWNED_HERE
SELF_MODIFICATION_GOVERNANCE_SETTLED
REAL_SYSTEM_VALIDATION
CONTINUOUS_OR_INFINITE_SCOPE
SELECTOR_OPTIMAL_OVER_ALL_LAWS
GRID_COVERAGE_IS_PARTITION_SCOPE
P3_RECOVERY_COMPLETE
SECTION_I_COMPLETE
COMPLETE_GMI
ONTOLOGICAL_COMPLETENESS
```

---

## 11. Deviation discipline

Any decision taken AFTER seeing a result and affecting a claim is recorded as a
numbered deviation in `SUPPLEMENT_1_POST_FREEZE_DEVIATIONS.md`, and its exposure is
**MEASURED**, not asserted: re-run with the deviation forced off and diff every
leaf field of the regenerated receipt, reporting the count of changed fields out of
the total. This is the standard the direct parent set with `D1_SENSITIVITY_V1.json`
(1 changed field of 774) and it is adopted here unchanged.

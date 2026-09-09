# HST Core Proofs V1 (lane A, D2)

Theorem set: HST-T01, T03, T05, T06, T07, T18. Statements are frozen verbatim in
`HST_THEOREM_REGISTRY_V1.json`; nothing below edits a statement. Notation follows
`HST_DEFINITIONS_V1.md`.

**Honesty preamble (binding on every row in this file).** Four of the six rows
(T01, T05, T07, T18) are, once their frozen quantities are read literally, elementary
order/arithmetic arguments (subset infimum comparison, linear inequality, running
maximum, telescoping). We prove them fully and then say exactly that: their mathematical
content is trivial; their scientific value is (a) the assumption ledger that licenses
them and (b) the hostile witnesses showing what happens when each load-bearing
assumption is removed. T03 is a genuine (small) impossibility theorem. T06 is the row
where the iff-direction carries real content, and it is the one whose failure mode
(false locality from an incomplete graph) is operationally dangerous. No row below is
promoted above what its assumptions license; per the freeze, a passing Python checker
certifies only the finite specialization, never the P1 claim.

---

## HST-T01 — Optional inheritance monotonicity [P1]

### Statement (with explicit quantifiers)

Let τ be a fixed task. Let `C : A × {τ} → ℝ` be a fixed scalarized cost functional
(scalarization frozen before the comparison; `C` may itself be an infimum/expectation
over internal randomness — any functional, as long as it is the *same* functional on
both sets). If

1. `A_t ⊆ A_{t+1}` (every strategy legal at t is legal at t+1), and
2. **zero mandatory overhead**: for every `a ∈ A_t`, `C_{t+1}(a, τ) = C_t(a, τ)` — the
   old strategy's cost under the new regime is *unchanged* (no storage/index/maintenance
   surcharge `M` is charged to it), and
3. `C_t(a,τ) < ∞` for at least one `a ∈ A_t` (the old infimum is attained or is an
   infimum over a nonempty set of reals),

then

> `inf_{a∈A_{t+1}} C(a,τ) ≤ inf_{a∈A_t} C(a,τ)`.

For all `Σ_t, Σ_{t+1}, τ, C` satisfying 1–3. (Universality over instances, no
distribution on tasks, no claim about which strategy the controller *chooses*.)

### Assumption ledger

| assumption | load-bearing? | what fails without it (see hostile W-T01) |
|---|---|---|
| `A_t ⊆ A_{t+1}` | YES | infimum can strictly increase (old best strategy outlawed) |
| `C_{t+1}(a,τ) = C_t(a,τ)` on `A_t` (M = 0) | YES | with `M > 0` every old strategy is charged; if no new strategy saves > M the infimum strictly increases |
| fixed scalarization frozen before comparison | YES | incomparable vectors make `≤` ill-typed; a post-hoc scalarization can manufacture any order |
| same functional on both sides | YES (cosmetic-seeming but essential) | comparing `C_t` to a *different* `C` is vacuous dominance |
| τ fixed | cosmetic for the math, load-bearing for the claim | the theorem is per-τ; no uniform-in-τ statement is claimed (that would need a distribution — P3, not P1) |

### Proof

Let `m_t = inf_{a∈A_t} C(a,τ)` and `m_{t+1} = inf_{a∈A_{t+1}} C(a,τ)`; both are infima
of real-valued functions over nonempty sets, so both exist in `ℝ ∪ {±∞}` (boundedness
is not needed: infima of arbitrary real-valued families exist in the extended reals;
assumption 3 only rules out `m_t = +∞` triviality).

Since `A_t ⊆ A_{t+1}`, the set over which `m_{t+1}` is taken contains the set over
which `m_t` is taken. For any real `r`, `{a ∈ A_{t+1} : C(a,τ) < r} ⊇ {a ∈ A_t : C(a,τ) < r}`,
so every lower bound achieved inside `A_t` is achieved inside `A_{t+1}`. Formally:
for every `a ∈ A_t`, `C(a,τ) ≥ m_{t+1}` by definition of infimum over the larger set;
hence `m_{t+1}` is a lower bound for `{C(a,τ) : a ∈ A_t}`, and `m_t` is the greatest
such lower bound, giving `m_{t+1} ≤ m_t`. ∎

**Where assumption 2 entered:** nowhere in the algebra above — and that is the point.
The subset inclusion alone gives the inequality of infima *of the same functional*.
Assumption 2 is what licenses using the *same* `C` on both sides: if inheriting
`H_{t+1}` charges every strategy (old ones included) a maintenance surcharge `M`, then
the honest comparison is `inf_{A_t} C ≤ m_t + M`, not `≤ m_t` (see Corollary T01-M).
The dominance is a statement about *sets of options with their costs*, and "optional
inheritance" (frozen definition §6) is precisely the guarantee that the option-cost
pairs survive the transition unchanged. The theorem is thus exactly as strong as the
phrase "available at unchanged cost" and not one bit more.

### Corollary T01-M (conditional form with mandatory overhead M > 0)

If `A_t ⊆ A_{t+1}` but every strategy in `A_{t+1}` (including the old ones) is charged
a mandatory overhead `M > 0` (storage/index/maintenance of `H_{t+1}`), then

> `m_{t+1} ≤ inf_{a∈A_t} (C_t(a,τ) + M) = m_t + M` if and only if each old strategy's
> cost under the new regime is exactly `C_t(a,τ) + M`;

and inheritance is *strictly beneficial at τ* iff

> `m_{t+1} < m_t`, which requires at minimum that some `a* ∈ A_{t+1}` has
> `C_{t+1}(a*,τ) < m_t` — i.e. **future savings > M** (acquisition cost is charged in
> `C_build`-style coordinates on top; in lifecycle form: future savings > acquisition +
> maintenance + revision, matching the frozen statement).

No unconditional "memory always helps" theorem exists: hostile witness W-T01 exhibits a
finite world where `M > 0` reverses the conclusion (`m_{t+1} > m_t`).

### Claim ceiling

P1 order-arithmetic dominance only. Not evidence that a real controller selects the old
strategy; not a statement about realized (as opposed to optimal achievable) burden; not
uniform over τ; no rate. Parent attribution: superset-dominance is folklore order
argument — **PARENT_SUFFICIENT for the inequality itself (trivial order argument), HST
residual = the M-conditional boundary and the "unchanged cost" definitional discipline**
(freeze §6), per `LITERATURE_LEDGER.md` (no NFL conflict: τ fixed, no averaging over a
problem class).

---

## HST-T03 — Representation insufficiency by indistinguishability [P1]

### Statement (with explicit quantifiers)

Let `S` be a set of world states, `φ : S → Z` an observation/representation map, and
`G : S → 2^A` a contract assigning to each state its set of correct actions, with the
convention that a policy `π : Z → A` (a deterministic function of the internal state —
i.e. the policy is *measurable w.r.t. φ*, its σ-algebra being `φ^{-1}(2^Z)`) satisfies
the contract at `s` iff `π(φ(s)) ∈ G(s)`. If there exist `s1, s2 ∈ S` with

1. `φ(s1) = φ(s2)`, and
2. `G(s1) ∩ G(s2) = ∅`,

then for **every** policy `π : Z → A`, `π` fails the contract at `s1` or at `s2` (or
both). Equivalently: no φ-measurable policy satisfies the contract on
`{s1, s2}` — a two-point impossibility, uniform over all π.

### Assumption ledger

| assumption | load-bearing? | note |
|---|---|---|
| contract = correct-action-set semantics (`G(s)` well-defined) | YES | probabilistic/expected-utility contracts weaken the theorem to "no π achieves utility ≥ u on both states" — same one-line pigeonhole |
| policy depends only on `φ(s)` | YES | this is definitional for "policy over the representation"; a policy reading extra channels is not φ-measurable and is exactly the escape the theorem forces |
| `G(s1) ∩ G(s2) = ∅` | YES | overlapping correct sets can be satisfied by any action in the intersection |
| determinism of π | cosmetic | randomized π is a mixture: it puts probability 1 on actions correct-at-`s1` *or* on actions correct-at-`s2` only if the intersection is nonempty; with disjoint G's, any randomized π has `P(correct at s1) + P(correct at s2) ≤ 1`, so success probability on the pair is ≤ 1/2. Same pigeonhole. |

### Proof

Let `π : Z → A` be any policy and put `z = φ(s1) = φ(s2)`, `a = π(z)`. Since `G(s1) ∩ G(s2) = ∅`,
the action `a` cannot belong to both `G(s1)` and `G(s2)`. If `a ∉ G(s1)`, π fails at
`s1`; otherwise `a ∈ G(s1)`, so `a ∉ G(s2)` by disjointness, and π fails at `s2`. In
both cases π fails the contract on at least one of the two states. Since π was
arbitrary, no φ-measurable policy satisfies the contract on both states. ∎

(One line: a function constant on a fiber of φ cannot separate points the contract
requires separated. This is the pigeonhole quotient argument — the dual of
Mealy-machine state-merging validity: merging is safe exactly when merged states have
intersecting output-behavior requirements; T03 is the contrapositive.)

### Corollary (search cannot repair representation insufficiency)

Since the quantifier over π is universal and independent of any search procedure:
repeated sampling, better optimization, longer horizons, or any selection dynamics
operating *within the policy class over φ* cannot produce a satisfying policy — the
entire search space lies in the failing set. Repair requires changing the hypotheses:
(a) a new observation channel (replace φ by φ′ with `φ′(s1) ≠ φ′(s2)`), (b) a richer
internal state (context/memory that splits the fiber), or (c) renegotiating the
contract. This is the falsifiable counterpart of "sufficiently expressive
representation" (definitions §7): expressiveness failure is *checkable* by exhibiting
an aliased pair with disjoint `G`.

### Claim ceiling

P1 impossibility over a two-point subproblem, uniform over the whole φ-measurable
policy class. Says nothing about *which* real representations alias (that is the OCM
residual: #152 decision-region diagnosis), nothing about stochastic contracts with
overlap, nothing about whether the *distribution* over states makes the aliased pair
negligible (a P3/P4 question). Parent: quotient/aliasing argument —
**PARENT_SUFFICIENT (Ashby requisite variety context; Mealy minimization duality); HST
residual = the diagnostic use (aliasing pair = certificate of necessary representation
change) and the #152 bridge.** Hostile W-T03 gives the minimal exact witness.

---

## HST-T05 — Macro amortization threshold [P1]

### Statement (with explicit quantifiers)

Fix a scalar cost coordinate (frozen prospectively). Let `m` be a candidate macro
replacing composition `s` on the uses where it applies. Freeze the four quantities

- `C_build(m)` ≥ 0: one-time construction/admission cost of m;
- `C_maint(m, H_eff)` ≥ 0: maintenance over the effective reuse horizon (charged once,
  in lifecycle form);
- `ΔC_use = C_use(s) − C_use(m)`: per-use cost delta (may be negative: macro *slower*
  or *costlier* per use);
- `H_eff` ≥ 0: expected number of useful reuses before invalidation/reset (an
  expectation under the frozen model), and `E[C_revision]` ≥ 0 expected revision cost.

Then, on that scalar coordinate,

> macro acquisition is lifecycle-beneficial **iff** `H_eff · ΔC_use > C_build + C_maint + E[C_revision]`.

For all real values of the quantities (universality: it is an equivalence between a
linear inequality and a sign).

### Assumption ledger

| assumption | load-bearing? | note |
|---|---|---|
| frozen scalar cost coordinate | YES | vector costs make "beneficial" a cone question, not a sign (Pareto form below) |
| quantities are expectations under one frozen model | YES | with model drift the identity compares apples to a *different distribution's* oranges — the science is exactly that drift |
| per-use delta uniform across uses (or ΔC_use already the use-weighted expectation) | YES | heterogeneous uses require summing `Σ_i ΔC_use(i)`; `H_eff · ΔC_use` is the homogeneous specialization |
| all costs charged (build + maint + revision) | YES | dropping any one inflates the LHS; hostiles target this |
| `H_eff` counted only over *useful* reuses | YES | reuse that is admissible-but-useless contributes cost, not saving: it enters RHS (use cost without benefit) — counting gross reuse overstates benefit |

### Proof

Lifecycle cost of the no-macro baseline over the horizon: `C_base = H_eff · C_use(s)`
(plus zero build/maint). Lifecycle cost with macro adopted:
`C_macro = C_build + C_maint + E[C_revision] + H_eff · C_use(m)`.
The macro is strictly beneficial iff `C_macro < C_base`, i.e.

```
C_build + C_maint + E[C_revision] + H_eff·C_use(m) < H_eff·C_use(s)
⟺  C_build + C_maint + E[C_revision] < H_eff·(C_use(s) − C_use(m))
⟺  C_build + C_maint + E[C_revision] < H_eff · ΔC_use.   ∎
```

This is the subtraction of two linear functions — nothing more. **The mathematical
content is trivial by design**: the row exists to fix *which* quantities must be frozen
before the comparison means anything, and to expose that the entire scientific
difficulty sits in `H_eff` (prospective, distribution-laden, invalidation-dependent)
and transfer scope. Parent attribution: amortization arithmetic; DreamCoder-class
library-learning cost models own the framing (**PARENT_SUFFICIENT for the identity;
HST residual = the invalidation/revision coordinates and the burden-form bookkeeping**).

### Corollary (vector/Pareto analogue, issue §T05 checkbox)

With a price vector `p` frozen prospectively (definitions §3), apply the identity
coordinate-wise: `H_eff · ΔC_use^{(i)} > (C_build + C_maint + E[C_rev])^{(i)}` for each
coordinate i charged in that unit. Absent a frozen price vector the correct statement
is only Pareto-conditional: adoption is *unambiguously* beneficial iff the vector
inequality `H_eff · Δ𝐂_use > 𝐂_build + 𝐂_maint + 𝐄[C_rev]` holds component-wise; any
mixed sign pattern is a trade-off decision, not a theorem.

### Claim ceiling

Arithmetic identity (P1 at the strength of an algebraic equivalence), conditional on
frozen quantities. No claim that `H_eff` is estimable prospectively, no claim that
real libraries amortize (P4), no claim on which macros to build (that is a search
question — T04 governs the allocation side). Hostile W-T05: exact finite world where
`H_eff · ΔC_use < C_build + C_maint` (macro never pays back), and the companion
case the issue's hostile list demands: a macro that *shortens code* (description cost
down) while *raising* per-use cost (`ΔC_use < 0`) — beneficial under a pure
description-length reading, harmful on the execution coordinate.

---

## HST-T06 — Exact dependency-cone locality [P1] — the load-bearing row

### Statement (with explicit quantifiers)

Let `D = (N, E)` be a finite directed acyclic graph (nodes N, edges E ⊆ N×N), with a
value assignment `v : N → Vals` satisfying the **locality law**: for each node n,
`v(n) = f_n(v(a) : a ∈ Anc_D(n))` — each node's value is a (deterministic) function of
exactly its declared ancestors, and of nothing else. Let `Desc_D(S)` be the descendant
closure of `S ⊆ N` in D (S plus all nodes reachable from S; equivalently the smallest
set containing S and closed under "has a member of S among ancestors" — non-ancestors
of S are untouched).

**(Forward direction — locality.)** For **all** D, S, and all pairs of value
assignments `(v, v′)` both satisfying the locality law with the *same* functions
`{f_n}`, if `v(a) = v′(a)` for every `a ∈ N \ Desc_D(S)` ... then automatically
`v(n) = v′(n)` for every `n ∈ N \ Desc_D(S)`. Restated as an intervention claim: a
change of inputs localized to S (an intervention setting S's values, with all functions
fixed) cannot change the value of any node outside `Desc_D(S)`.

**(Reverse direction — the iff.)** "Exact recomputation outside `Desc(S)` is
unnecessary **iff** the registered dependency semantics are complete for the protected
outputs." Formally: let `R ⊆ N` be the protected outputs. Recomputation of R after an
intervention on S is *unnecessary* (values provably unchanged) if `R ∩ Desc(S) = ∅`.
This inference is **sound only if** the declared graph is complete for R: i.e. for
every n ∈ R and every undeclared influence `u → n` (any quantity varied by the
intervention that the computation of `v(n)` actually reads, directly or transitively,
but which is not an ancestor of n in D), the value of `v(n)` is invariant to it. An
incomplete graph yields **false locality**: the inference "R ∩ Desc(S) = ∅ ⟹ R
unchanged" is invalid in general, and the invalidity is witnessed by exactly the
missing-edge construction (hostile W-T06).

### Assumption ledger

| assumption | load-bearing? | note |
|---|---|---|
| acyclicity | YES for the *form* (DAG gives well-founded recursion order; TMS/cyclic generalization is a declared boundary, not a corollary) |
| locality law: `v(n)` a function of declared ancestors **only** | YES — this is the whole content | with undeclared reads the forward direction is false too |
| completeness of declared dependencies for protected outputs | YES for the iff direction | the missing-edge hostile lives here |
| deterministic functions | cosmetic | randomization adds a coupling argument: equality in distribution outside the cone, given shared randomness; same proof shape |
| functions unchanged by the intervention | YES | an intervention that also rewrites `f_n` outside the cone is a different operation (change to the program, not to the data) |

### Proof (forward)

Let `T = N \ Desc_D(S)`. Since D is a DAG, the restriction `D|_T` is a DAG and every
ancestor (in D) of a node `n ∈ T` that lies in `T`... we must be careful: ancestors of
`n ∈ T` may include members of `Desc(S)`. Claim not so: if `a ∈ Anc(n)` and
`a ∈ Desc(S)` then n is reachable from S through a, so `n ∈ Desc(S)`, contradiction.
Hence for every `n ∈ T`, `Anc_D(n) ⊆ T`. Now prove `v(n) = v′(n)` for all `n ∈ T` by
well-founded induction on the DAG order of `D|_T`: base nodes of `D|_T` have all
ancestors in `N \ Desc(S)`... more precisely, induct on the topological order of
`D|_T`. Let `n ∈ T` and suppose `v(a) = v′(a)` for all `a ∈ Anc_D(n)` (inductive
hypothesis, applicable since `Anc_D(n) ⊆ T` and precedes n). Then
`v(n) = f_n(v(a): a ∈ Anc(n)) = f_n(v′(a): a ∈ Anc(n)) = f_n(v′(a): a ∈ Anc(n)) = v′(n)`.
The middle equality is function application: same function, equal inputs. So v and v′
agree on T. The intervention reading: any two worlds agreeing off the cone and
differing only within S agree off the cone after updating — the update cannot leak. ∎

(The proof is structural induction over a topological order — the standard
d-separation/"manipulation theorem" shape; parent-owned: causal DAG intervention
locality, Pearl-class. **The forward direction is PARENT_SUFFICIENT.**)

### Proof (reverse / iff — where the row earns its keep)

We exhibit the two failure modes and show they are the *only* ones, i.e. prove the
contrapositive: **if** the declared semantics are incomplete for R (some protected
output n ∈ R has its value depend on a quantity w that the intervention varies but w ∉
Anc_D(n)), **then** there exist two executions consistent with the declared graph and
the intervention on S whose declared-ancestors inputs at n agree while `v(n)` differs —
so "R ∩ Desc(S) = ∅" holds in the graph, yet R changed.

Construction. Let n ∈ R with an undeclared read of w, where w is varied by the
intervention (w ∈ the intervention's write set; w ∉ Anc_D(n) by incompleteness). Since
`v(n)` genuinely reads w, there exist two values `w0 ≠ w1` of w and an agreeing
assignment of the declared ancestors such that `f_n^actual(v(Anc(n)), w0) ≠
f_n^actual(v(Anc(n)), w1)` — otherwise the read of w would be dead and the dependency
semantics *would* be complete at n (contradiction with the assumption that the
undeclared influence is real). Run the intervention twice, once forcing w = w0 and once
w = w1 (both runs identical elsewhere, all declared ancestors of n taking the same
values in both runs — possible because w ∉ Anc_D(n), so no declared path carries the
difference). Declared-graph locality inference says "R unchanged"; actual values at n
differ. Hence the inference from `R ∩ Desc(S) = ∅` to "unchanged" is unsound unless
completeness holds. ∎

**Therefore**: recomputation-skipping is licensed *exactly* by (graph locality) ∧
(completeness of declared dependencies for the protected outputs) — and *only* by them.
This is why the missing-edge case (W-T06) is the important hostile: in operational
terms, a provenance/dependency graph that omits even one real influence converts a
correct-sounding locality theorem into a silent-corruption license. The graph being a
DAG does not certify it; only completeness does, and completeness of a declared graph
is itself not decidable from the graph alone (it is a property of the *actual*
computation — cf. T15; checking it is exactly what C's protected validation must do
empirically or by contract).

### Boundaries (explicit, per the issue)

- Cyclic dependencies (TMS/truth-maintenance): the induction order does not exist;
  locality must be re-founded on fixpoint semantics; declared **boundary**, no corollary
  claimed here.
- The theorem is about *values*, not *costs*: skipping recomputation of R saves cost,
  and that saving is the T05/T01 cost question, deliberately not mixed into this row.

### Claim ceiling

P1 (forward: structural induction; reverse: explicit construction). Parent-owned
forward direction (Pearl-class d-separation/intervention semantics —
**PARENT_SUFFICIENT for locality**); **HST residual = the iff-completeness formulation:
the proof obligation "graph complete for protected outputs" is a *precondition*, not an
inference** — this is the anti-false-locality discipline the OCM residual
(provenance-graph completeness) must satisfy.

---

## HST-T07 — Elitist ratchet monotonicity [P1]

### Statement (with explicit quantifiers)

Let `q : X → ℝ` be a fixed evaluator (frozen total order: for the theorem it suffices
that q induces a total order on admissible objects, e.g. a fixed utility functional,
ties broken by a frozen rule so "best" is unique). Let `(x_t)_{t≥0}` be **any** sequence
of candidate objects (arbitrary proposal process — adversarial is allowed). Define the
elitist archive recursion with immutable retention:

```
b_{-1} = -∞  (archive empty);
b_t    = q(x_t)   if x_t is admissible and q(x_t) > b_{t-1};
        b_{t-1}   otherwise.
```

Then for all t: `b_t ≥ b_{t-1}` (monotone non-decreasing), with equality whenever the
new candidate is inadmissible or not better. Universality: over all sequences and all
evaluators satisfying the frozen-order hypothesis.

### Assumption ledger

| assumption | load-bearing? | note |
|---|---|---|
| fixed evaluator (q frozen, not itself rewritten mid-run) | YES | if q can change (T17's register attack), "best-so-far under q" is not a well-defined monotone object |
| immutable archive with **unlimited capacity** | YES for the P1 form | under finite capacity K, the retained best can *decrease* — see the capacity variant |
| frozen total order (decidable comparison) | YES | partial orders are the Pareto variant; "best" may not exist |
| admissibility gate before retention | YES for the claim's honesty | without it the archive can retain inadmissible objects — monotonicity of a meaningless quantity |
| candidate sequence arbitrary | (none needed) | the theorem holds even adversarially — that is the ratchet's only strength |

### Proof

By cases on the recursion's branch. If the candidate is inadmissible or not better,
`b_t = b_{t-1} ≥ b_{t-1}`. If it is admissible and strictly better, `b_t = q(x_t) > b_{t-1}`.
Both branches give `b_t ≥ b_{t-1}`; chaining over t gives monotonicity over any
horizon. ∎ (Running-maximum monotonicity: **PARENT_SUFFICIENT — trivial; the row's
content is what it does *not* prove.**)

### What it does NOT prove (explicit negative list, frozen statement)

Not open-endedness (T12/T13 own the boundary), not complexity growth, not
generalization, not self-improvement efficiency, not any statement about the *rate* —
monotone bounded sequences converge, and with a bounded quality range the ratchet
saturates (that is exactly T18's structure applied to quality space: at most
`(q_max − q_0)/ε` ε-improvements).

### Corollary (Pareto/archive variant with exact conditions — issue checkbox)

Replace the scalar order by a partial order ⪯ on quality vectors.

1. **Unlimited capacity:** the nondominated *set* is monotone under set-inclusion of
   the dominance relation only in the weak sense: the dominance relation among retained
   points never weakens (a stored point is never dominated by a point it dominated
   before), but the set itself grows without bound; the *hypervolume* w.r.t. a fixed
   reference point r (below all attainable vectors, frozen) is monotone non-decreasing
   — the exact scalar-ratchet analogue, since hypervolume adds a nonnegative increment
   per nondominated admission.
2. **Finite capacity K (the honest operational case):** monotonicity **fails** in both
   directions. Exact conditions: (a) the nondominated set can *lose* points when an
   admitted point evicts (eviction under a bounded archive with crowding/niche rules is
   a *policy*, not an order — the ratchet theorem does not apply to it at all); (b)
   fixed-reference hypervolume remains non-decreasing **iff** the eviction policy never
   removes a point contributing positive hypervolume not covered by a retained point —
   a condition on the archive policy, checkable per policy, not a theorem of elitism
   alone. Statement for the registry: *with finite capacity, archive quality is
   monotone only relative to the eviction policy's retention guarantee; "elitist" must
   be defined as "retains a maximizer of the frozen quality functional", and any weaker
   retention voids the ratchet.*

### Claim ceiling

P1 running-maximum monotonicity (trivial). The science is entirely in the negative
list and the capacity conditions. **PARENT_SUFFICIENT** (running-maximum monotonicity
is folklore); HST residual = the finite-capacity exact conditions and the
admissibility-gate discipline. Hostile W-T07: perfect ratchet on one benchmark with
zero transfer (the frozen "NOT" list made executable).

---

## HST-T18 — Fixed-epsilon bounded-burden improvement limit [P1]

### Statement (with explicit quantifiers)

Let `(B_g)_{g=0,1,2,…}` be a scalar sequence of burdens with `B_g ≥ b_min` for all g
(burden bounded below by `b_min ∈ ℝ`). If generations g = 1..N each satisfy
`B_g ≤ B_{g-1} − ε` with fixed `ε > 0`, then

> `N ≤ (B_0 − b_min)/ε`.

For all real `B_0 ≥ b_min` and ε > 0. Equivalently: a sequence of strict ε-improvements
on a [b_min, B_0]-bounded burden is finite with the displayed uniform bound.

### Assumption ledger

| assumption | load-bearing? | note |
|---|---|---|
| `B_g ≥ b_min` for all g | YES | unbounded-below burden (free resources) admits infinitely many ε-drops |
| fixed ε > 0, uniform over generations | YES | ε_g → 0 permits infinitely many improvements (Σ ε_g < ∞) — that is the actual asymptotic regime of real systems |
| improvements measured on ONE frozen scalar coordinate / benchmark family | YES | scope expansion resets the coordinate; the bound is per-coordinate |
| scalar | YES | vector burden has no total order to improve along without a frozen scalarization |

### Proof

Telescoping: `B_N = B_0 − Σ_{g=1}^{N} (B_{g-1} − B_g) ≤ B_0 − Nε`. Since `B_N ≥ b_min`,
`b_min ≤ B_0 − Nε`, hence `N ≤ (B_0 − b_min)/ε`. ∎ (Archimedean/telescoping argument —
**PARENT_SUFFICIENT, trivial arithmetic; the row's function is claim-discipline.**)

### Corollary (the five-route escape disjunction)

Indefinite continuation of fixed-ε improvements is possible only by leaving the
hypotheses, i.e. at least one of the following must hold eventually:

1. **shrinking effect size** — ε is not actually fixed (ε_g → 0; Σε_g converges);
2. **expanding task/ecology scope** — the benchmark family grows, changing the
   reference class against which B is measured (b_min/B_0 re-frozen);
3. **expanding precision/capability frontier** — the burden coordinate is re-normalized
   (higher-precision variants re-open slack: b_min effectively lowered);
4. **new representational/search dimensions** — a new coordinate/axis added: the
   improvement is no longer an improvement on the *old* scalar sequence (this is T02's
   reach expansion and T11's major-transition criterion, cited, not re-proved here);
5. **regime/resource change** — the price vector or hardware regime changes,
   re-defining the scalarization (violating "frozen scalarization").

Formally: if none of 1–5 ever occurs, the hypotheses of the theorem hold in perpetuity
and the number of ε-improvements is bounded by the display — so any claim of unbounded
fixed-ε improvement on one frozen finite benchmark family contradicts the theorem. This
bars defining open-ended self-improvement as fixed-ε gains on one frozen finite
benchmark (frozen statement), and binds #221 GS stopping/claim language: a GS-style
stopping rule may not be deferred indefinitely by re-labeling saturation as plateau.

### Claim ceiling

P1 arithmetic bound on improvement *counts* under frozen coordinates. Says nothing
about when real systems saturate (that is P4 measurement), nothing about varying ε
protocols (covered by route 1), nothing about quality-space improvements (T07's
negative list, same telescoping shape). Hostile W-T18: exact fixed-ε saturation trace —
a deterministic lineage achieving the bound exactly, then forced into one of the five
routes (the witness takes route 1 with ε halving, and shows the re-defined "unbounded
improvement" claim that follows is an artifact of the ε-protocol, not of search
capability).

---

## Cross-row summary for the registry patch

| row | math content | honest grade | parent |
|---|---|---|---|
| T01 | subset-infimum inequality (trivial) + M-conditional boundary | PROVED; PARENT_SUFFICIENT for the inequality; ceiling: per-τ order dominance, no rate, no selection claim | superset dominance (folklore) |
| T03 | two-point φ-measurability impossibility (pigeonhole) | PROVED; PARENT_SUFFICIENT (quotient/aliasing); ceiling: uniform-π two-point impossibility only | Mealy minimization duality; Ashby context |
| T05 | linear lifecycle identity | PROVED (arithmetic); PARENT_SUFFICIENT; ceiling: frozen-quantity equivalence only | amortization/library cost models |
| T06 | DAG structural induction + iff-completeness construction | PROVED; forward direction PARENT_SUFFICIENT (Pearl-class); **HST residual = iff-completeness precondition discipline**; ceiling: values not costs, acyclic only | causal DAG intervention locality |
| T07 | running-maximum monotonicity (trivial) | PROVED; PARENT_SUFFICIENT; ceiling: ratchet only; finite-capacity conditions are policy-relative | running maximum |
| T18 | telescoping bound (trivial) | PROVED; PARENT_SUFFICIENT; ceiling: frozen-scalar improvement counting; five-route disjunction is definitional escape analysis | archimedean argument |

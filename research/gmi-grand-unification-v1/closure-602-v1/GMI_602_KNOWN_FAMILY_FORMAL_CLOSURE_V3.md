# GMI #602 known-family formal closure V3

Status: **NORMATIVE FORMAL SUPPLEMENT FOR REMAINING B-FAMILY GAPS**  
Date: 2026-09-14.  
Read with the V1 spine, V1 parent amendments, V2 formal-gap supplement, and their corrigenda.

## 0. Why this exists

A direct audit of the still-open B-family boxes in #602 left three theorem-shaped obligations that should not be deferred to experiment:

1. the exact condition separating fixed/local, adaptive sparse, and full access;
2. the formal selector/emitter split behind symbolic rewrite systems; and
3. the generic search-burden law behind retained program/library chunks.

The mechanisms themselves have mature parents. The theorems below expose only the architecture-neutral obligation/resource residual.

---

# T602-34 — fixed/local vs adaptive-sparse vs full-access routing [P1]

## 34.1 Registered coordinate-query model

Let an input be `x in X_1 x ... x X_n`, protected target be `f(x)`, and one coordinate read cost `c_r>0`.

A fixed/local access scheme sees only coordinates in a prospectively specified set `L subseteq {1,...,n}` (or a location-relative neighborhood `L_r(q)` under a registered query/index `q`). Let `pi_L(x)` be the corresponding projection.

### Fixed/local sufficiency theorem

An exact predictor using only `pi_L(x)` exists **iff**

\[
pi_L(x)=pi_L(x')\Rightarrow f(x)=f(x')
\]

for every admitted pair `x,x'`.

Equivalently, `f=g circ pi_L` for some `g`.

**Proof.** If the predictor exists, equal observations must give equal outputs. Conversely, constancy of `f` on projection fibers makes `g` well-defined. ∎

Thus one exhibited pair identical on the local window but with different target values proves that window insufficient. This is the same quotient/factorization logic as T602-01/T602-17, now applied to an access cut.

## 34.2 Adaptive sparse routing

In the ordinary adaptive coordinate-query model, a depth-`k` decision tree may choose its next coordinate from the previously observed coordinate/value transcript.

Define exact deterministic query complexity `D(f)` as the minimum worst-case number of coordinate queries needed to determine `f` on the registered input set.

Then an exact adaptive `k`-read router exists **iff**

\[
D(f)\le k.
\]

This is definitional after quotienting decision trees by their transcripts, but it is the correct architecture-neutral object behind “content-dependent sparse attention” in this access model.

A fixed local pattern can fail even when `D(f)` is small: adaptivity can choose *which* location matters from content already read. Conversely, if `D(f)=n`, no exact sparse coordinate reader exists; full access is necessary in the worst case.

## 34.3 Resource crossover

Let full access read all `n` coordinates, total fixed overhead `rho_full`, and adaptive sparse access use worst-case `k` reads with routing/control overhead `rho_sparse` on the same obligation and verifier. Under the additive serving model,

\[
C_{full}=rho_{full}+n c_r,
\]

\[
C_{sparse}=rho_{sparse}+k c_r.
\]

When both are exact/admissible, sparse access is cheaper iff

\[
rho_{sparse}-rho_{full}<(n-k)c_r.
\]

A fixed local scheme is admitted only if its projection passes the fiber-sufficiency theorem. Therefore the phase ordering is:

```text
first:  obligation sufficiency / exact query complexity
then:   routing + read + communication + verification cost
```

Cost may never legalize an insufficient access pattern.

For variable query count `K(x)`, replace `k c_r` by the registered expected, worst-case or tail-controlled query cost required by the claim; do not switch summaries post hoc.

## 34.4 Multi-target / locality consequence

If the protected output contains several components `f_j(x)`, fixed locality radius `r` is sufficient only if each required component factors through its registered local projection. Adaptive sparse routing may share reads across targets; therefore its burden is a **joint decision-tree/query-complexity problem**, not the sum of independently chosen attention windows unless that decomposition is proved.

This is the formal gap left by the single-pointer microscope in #659: the multi-target/full-vs-sparse distinction requires an ecology whose joint dependency structure makes `D(f)` nontrivial.

## 34.5 Parent subtraction

Decision-tree/query complexity, adaptive querying, local algorithms, data-structure/cell-probe lower bounds and sparse-attention theory receive first refusal. Recent sparse-attention analyses can establish approximation guarantees under specific attention-matrix sparsity assumptions, but that mechanism/approximation theory is parent-owned.

**GMI residual:** derive the relevant dependency/access quotient from the protected obligation, freeze the routing/read prices, predict which access regime should enter the frontier, then test neutral recovery.

### #602 rows formally addressed

- B7 sparse/local attention regime under locality/budget pressure;
- B7 full vs sparse/local routing phase boundary.

**Still empirical:** a protected multi-target ecology, frozen pre-search phase prediction, neutral recovery and disjoint search/encoding replication.

---

# T602-35 — selector/emitter factorization for symbolic rewrite systems [P1]

## 35.1 Information cut

A generic rule/rewrite machine is represented as two stages:

\[
a=Sigma(x),
\]

\[
y=E(a,c(x)),
\]

where:

- `Sigma` is the selector/control stage;
- `a` is a selected rule/control code (possibly an ordered candidate list);
- `c(x)` is the **explicitly registered information carried past the selector** (captured variables, copied slots, constants, etc.);
- `E` is the emitter/action stage.

This information cut is necessary. If `E` secretly receives all of `x`, selector complexity can be moved into the emitter and no selector necessity theorem is possible.

## 35.2 Selector sufficiency theorem

For a fixed carried-information map `c` and selector `Sigma`, exact realization of obligation `f` is possible **iff** `f` is constant on every fiber of the joint control representation

\[
q(x)=(Sigma(x),c(x)).
\]

Equivalently,

\[
f=g circ q
\]

for some emitter `g`.

**Proof.** Identical to the quotient/factorization proof: if two inputs yield the same selector output and carried state but require different protected outputs, no emitter using only those objects can distinguish them; if every fiber has one target value, define the emitter by that value. ∎

This theorem cleanly separates **selector expressivity** from **emitter expressivity**.

## 35.3 Comparing selector families

Let `F_1,F_2,...` be registered selector families—for example positional pinning, equality/relational constraints, tree-pattern selectors, discrimination networks or arbitrary finite subsets. For family `F`, define its exact burden frontier

\[
B_F(f,c)=\min_{Sigma in F:\ f\ factors\ through\ (Sigma,c)} lifecycle(Sigma,c,E).
\]

A family that has no sufficient selector has burden `+infinity` for the exact obligation. Among sufficient families, the winner is the lower/Pareto lifecycle burden after matching information access and emitter power.

There is no universal best selector family: richer selectors can reduce emitter/table burden while increasing match/index/update burden. Rete/discrimination-network and term-rewriting pattern-matching literatures already own algorithms for many-pattern matching and rule selection.

## 35.4 Minimal selector quotient

At a fixed carried-information contract `c`, define

\[
x sim_c x'\iff c(x)=c(x')\ \text{and}\ f(x)=f(x').
\]

Any exact selector/emitter realization must refine enough of these target distinctions that `(Sigma(x),c(x))` never merges two different protected outputs. A selector family whose representational equivalence forces such a merge is formally insufficient, regardless of cost.

This does **not** say the quotient itself is the cheapest selector implementation; parent pattern-matching/index structures may implement the same distinction with different lifecycle burdens.

## 35.5 Parent subtraction

Production-system matching (including Rete and successors), term-rewriting/pattern-matching algorithms, decision-tree/discrimination-network indexing and symbolic-learning parents receive first refusal.

**GMI residual:** the obligation-derived selector quotient and lifecycle crossover among matched selector families; not pattern matching itself.

### #602 rows formally addressed

- B14 derivation of rule/rewrite **selector** pressure, complementing the already-derived emitter result;
- exact protocol for the requested positional/equality/arbitrary-subset selector-family comparison.

**Still P2/P4:** execute that family comparison and neutral search; theorem alone does not choose the empirical winner.

---

# T602-36 — retained program/library search-burden law [P1]

Let future obligation set or sequence be indexed by `i=1,...,m`. Under the base grammar, verified search burden for target `i` is `b_i`.

Consider adding a candidate reusable chunk/library item `ell`. Charge:

- one-time acquisition/verification/installation cost `K_ell`;
- maintenance/revision cost `M_ell` over the registered horizon;
- modified verified search burden `b_i^(ell)` for each future target, including **both** any reduced derivation depth and any increased branching/choice cost caused by enlarging the grammar.

Then retaining `ell` reduces total search burden exactly when

\[
K_ell+M_ell+\sum_i b_i^{(ell)} < \sum_i b_i.
\]

Equivalently, with per-target saving `Delta_i=b_i-b_i^(ell)`, retain iff

\[
\sum_i Delta_i>K_ell+M_ell.
\]

This is T602-05 applied specifically to verified search and makes two points explicit:

1. a chunk can shorten descriptions while **increasing** total search because the expanded grammar raises branching/confusion burden;
2. library pressure is corpus/future-task-distribution dependent—frequency of useful reuse, not syntactic “abstraction quality,” pays the acquisition bill.

When target sampling is stochastic, replace the finite sum by the prospectively registered expectation/risk criterion and use the appropriate statistical parent for uncertainty.

## Parent subtraction

DreamCoder/Stitch/library learning, inductive programming, MDL, Levin/OOPS, GP/program synthesis and amortized-search parents own reusable-library mechanisms.

**GMI residual:** predict from obligation recurrence and full search/resource accounting when a neutral base grammar should retain a discovered composite. A macro that is inserted by name is not neutral recovery.

### #602 rows formally addressed

- B15 DreamCoder/Stitch-like **library pressure without inserting those mechanisms** at the formal level.

The existing #660 finite witness may supply a bounded instance; broader neutral/held-out recovery remains an evidence gate.

---

# 4. Claim ceiling

T602-34..36 close the generic formal debt behind the remaining B7/B14/B15 theorem-shaped rows. They do not close:

- held-out neural-family winning ecology;
- held-out long-sequence recovery;
- held-family generative response tests;
- real continual-learning task sequences;
- neutral recovery/replication obligations.

Those are correctly empirical/certificate requirements and remain open in #602.

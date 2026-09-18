# Developmental-reuse theorems (#833 Section L)

Scope is fixed by `FREEZE_V1.md` (commit `01c6a820`, written before any
implementation) and `FROZEN_FIXTURES_V1.json`. Every quantity is an exact
integer or `fractions.Fraction`; `independent_oracle_v1.py` recomputes each one
by a different method (literal enumeration, extreme-rank checking, exhaustive
start-point sweeps). Notation: `Φ(n, ℓ) = Σ_{j=1..ℓ} n^j`, `Φ(n, 0) = 0`;
`B_G(w)` is the #897 breadth-by-length discovery burden; `n = |A_0|`,
`n' = |A_1|`, `ℓ0 = ℓ*_{G0}(w)`, `ℓ1 = ℓ*_{G1}(w)`.

---

## L0 (bracket lemma — the only new fact everything else rests on)

For every acyclic grammar `G` with alphabet size `n ≥ 2` and every base target
`w`,

```text
Φ(n, ℓ* − 1) + 1  ≤  B_G(w)  ≤  Φ(n, ℓ*)
```

and both bounds are attained (rank `0`, rank `n^{ℓ*} − 1`).

*Proof.* #897 `T3` gives `B_G(w) = Φ(n, ℓ*−1) + rank + 1` with
`rank ∈ [0, n^{ℓ*} − 1]`; substitute the extremes and use
`Φ(n, ℓ*−1) + n^{ℓ*} = Φ(n, ℓ*)`. ∎

L0 is what turns a burden comparison — which naively needs both ranks, i.e.
the lex-least hit program in each grammar — into an arithmetic on four
integers that depends only on `(n, n', ℓ0, ℓ1)`.

---

## REP-1 (exact decision bracket for a representation change)

**Statement.** For `G1 = G0 ∪ L` acyclic with `n' > n`:

```text
GUARANTEED_REDUCTION   iff  Φ(n', ℓ1)      ≤  Φ(n, ℓ0 − 1)        ⇒ B1 < B0 always
GUARANTEED_INCREASE    iff  Φ(n', ℓ1 − 1)  ≥  Φ(n, ℓ0)            ⇒ B1 > B0 always
RANK_DECIDED           otherwise
```

*Proof.* In the first case `B1 ≤ Φ(n',ℓ1) ≤ Φ(n,ℓ0−1) < Φ(n,ℓ0−1)+1 ≤ B0` by
L0. In the second `B1 ≥ Φ(n',ℓ1−1)+1 > Φ(n,ℓ0) ≥ B0`. The two conditions are
mutually exclusive: if both held then
`Φ(n,ℓ0) ≤ Φ(n',ℓ1−1) < Φ(n',ℓ1) ≤ Φ(n,ℓ0−1) < Φ(n,ℓ0)`, absurd. ∎

**Reading.** A representation change reduces future search cost when its
*length compression* outruns its *alphabet inflation* at this exact rate — and
the criterion decides this **without running the search** and without knowing
either lex-least hit program. Compression alone is not the criterion; the trade
is.

**Registered census.** All `(n, n', ℓ0, ℓ1)` with `n ∈ {2,3,4}`,
`n' ∈ {n+1, n+2, n+3}`, `1 ≤ ℓ1 ≤ ℓ0 ≤ 12`: **702 cells**, classified
**359 / 167 / 176**. Band-disjointness violations: **0**. Monotonicity in
compression depth `d = ℓ0 − ℓ1` (deeper compression never moves a cell towards
INCREASE): **0** violations. Route B re-checks every cell against the extreme
rank assignments: **0** violations of either guaranteed band.

**Falsifier.** An instance in a guaranteed band whose exactly computed burdens
contradict the band, on either route.

## REP-1b (five-way completion — found by the second route, not by the first)

Route B's extreme-rank check reported **4** cells that the frozen three-way rule
sends to `RANK_DECIDED` even though their sign is rank-free in the *weak* sense.
Adding `b1_lo = Φ(n',ℓ1−1)+1`, `b1_hi = Φ(n',ℓ1)`, `b0_lo = Φ(n,ℓ0−1)+1`,
`b0_hi = Φ(n,ℓ0)`:

```text
GUARANTEED_REDUCTION        b1_hi <  b0_lo      B1 < B0 always
WEAK_REDUCTION_OR_EQUALITY  b1_hi == b0_lo      B1 ≤ B0 always, equality realisable
RANK_DECIDED                both strict signs realisable
WEAK_INCREASE_OR_EQUALITY   b1_lo == b0_hi      B1 ≥ B0 always, equality realisable
GUARANTEED_INCREASE         b1_lo >  b0_hi      B1 > B0 always
```

The four cells are `(n,n',ℓ0,ℓ1)` = `(2,3,2,1)`, `(3,4,2,1)`, `(4,5,2,1)`
(weak reduction) and `(2,5,2,2)` (weak increase). Refined counts:
**359 / 3 / 172 / 1 / 167**.

**The frozen rule is SOUND but INCOMPLETE:** it never asserts a wrong strict
sign (0 conflicts), it merely declines to decide 4 boundary cells. The frozen
three-way statement is reported unchanged; REP-1b is recorded as a refinement
**earned by the registered second route**, with its provenance in the receipt.
This is the two-route obligation doing the work it exists for.

---

## REP-2 (portfolio form: which changes reduce *expected* future cost)

**Statement.** For a frozen finite target multiset `T`,

```text
ΔNet(T, L) = Σ_{w∈T} (B1(w) − B0(w)) + K_total(L)
           = − Saving(T⁺) + Tax(T⁰) + K_total(L)
```

where `T⁺ = {w : ℓ1 < ℓ0}`, `T⁰ = {w : ℓ1 = ℓ0}`, and on `T⁰`

```text
Tax(w) = [Φ(n',ℓ0−1) − Φ(n,ℓ0−1)] + [rank_{n'}(p*) − rank_n(p*)]  >  0
```

where `p*` is each grammar's own lex-least hit program. On the **registered**
`T⁰` the two are the same program — `H−` was constructed to contain no `ab` or
`ba`, so no macro-using program for those targets exists at all — and the rank
difference is then exactly the re-indexing of one fixed program from base `n` to
base `n'`, making `Tax(w) > 0` whenever `n' > n` and `ℓ0 ≥ 2` (#897 `T4`,
generalised off its fixture). In general the two lex-least programs need **not**
coincide even when `ℓ1 = ℓ0`: macros sort after base tokens but lexicographic
order compares position-wise, so a same-length macro-using program such as
`(a, m1, …)` can precede `(b, a, …)`. The formula above is stated with the two
ranks kept separate for that reason, and `rep2_portfolio` computes `B1 − B0`
directly rather than through the parenthetical. **A representation
change reduces expected future search cost iff `Saving(T⁺) > Tax(T⁰) + K_total(L)`.**
Per-target membership of `T⁺` in a guaranteed band is decided by REP-1 without
computing ranks.

**Registered validation (required, not optional).** REP-2's decomposition
recomputes #897's published `HLD-1` integers **exactly**, on both routes:

| set | `Σ B_{G0}` | `Σ B_{G1}` | `K_total` | `ΔNet` |
|---|---|---|---|---|
| `H+` (12 reuse-positive) | 50,052 | 1,307 | 6 | **−48,739** |
| `H−` (12 unrelated control) | 538 | 1,710 | 6 | **+1,178** |
| combined (24) | 50,590 | 3,017 | 6 | **−47,567** |

Combined decomposition: `Saving(T⁺) = 48,745`, `Tax(T⁰) = 1,172`,
`K_total = 6`; `−48,745 + 1,172 + 6 = −47,567` = the directly computed `ΔNet`.
`dNet_direct == dNet_decomposed` on every registered set.

**CAPITAL-1 boundary (mandatory case).** The solution-capital library
`L_sol = {m1 → ababababab}` is **accepted by REP-1** on its own target
(`ΔNet = −36,890`, `GUARANTEED_REDUCTION`) and **rejected by REP-2** on the
registered 24-target distribution (`ΔNet = +18,139`). Storing an answer is not
a search-cost reduction; only the portfolio form separates the two. This is the
burden-metric instance of `CAPITAL-1` (#909/#908), which separates solution
capital from search-policy improvement without a burden model.

**No-reuse hostile.** `L = {m1 → ccc}`, whose body occurs in no registered
target: `Saving(T⁺) = 0`, `ΔNet = +437,558` — pure tax, as REP-2 requires.

**Falsifier.** Decomposition not reproducing `ΔNet` exactly; `L_sol` not
rejected; `Tax` not strictly positive on a nonempty `T⁰`.

---

## REP-3 (EARNED-BY-COUNTEREXAMPLE: description shortening is not sufficient)

**Statement.** Take `w = cccccabcccc` (`|w| = 11`, exactly one greedy `ab`),
`L = {m1 → (a,b)}`, so `n = 3 → n' = 4` and `ℓ0 = 11 → ℓ1 = 10`. The lex-least
hit program under `G1` is `cccccm1cccc`: the macro **is** used and the
description **is** strictly shorter. Yet

```text
B_{G1}(w) ≥ Φ(4, 9) + 1 = 349,525  >  265,719 = Φ(3, 11) ≥ B_{G0}(w)
```

so the burden strictly increases **for every possible rank assignment**.
Measured exactly, on both routes: `B_{G0} = 265,152 → B_{G1} = 1,048,831`,
`Δ = +783,679`.

**Consequence.** *"The target uses the macro"* / *"the macro shortens the
description"* is **not sufficient** for future-search-cost reduction. The
informal reading of the neighbouring parent statement (grammar-growth v2 `T9`:
burden strictly decreases when macro depth `g ≤` target reuse depth `t`) is
**bounded here**: it holds at the parent's measured parameter point and fails as
a general law. The boundary is mapped by counterexample, not asserted.

**Registered near-miss hostile.** The same construction at `|w| = 10`
(`ℓ0 = 10 → ℓ1 = 9`) has `Φ(4,8) = 87,380 < 88,572 = Φ(3,10)`: the brackets
**overlap**, so REP-1 must return `RANK_DECIDED` — and it does. The exact
burdens there happen to increase too (`88,005 → 262,399`), which is precisely
why the hostile matters: a checker that generalised from the measured sign to a
guaranteed band would have been wrong at exactly this point. The criterion
declines to decide it; that is the correct behaviour, not a weakness.

**Falsifier.** Enumeration disagreeing with the closed form on either instance;
REP-1 classifying the near-miss outside `RANK_DECIDED`.

---

## NOV-1 (conservative grammar growth adds ZERO expressive power)

**Statement.** For every acyclic library `L` reachable by conservative growth
from `G0` and every `t`,

```text
{ Expand(p) : p a program over A_t }  =  Σ⁺  =  { Expand(p) : p a program over Σ }
```

*Proof.* (⊆) By induction on a topological order of the macro dependency DAG
(which exists iff acyclic — #897 `T1`(3)): every macro body is a sequence over
`Σ ∪ M_{k−1}`, each of whose symbols expands to a `Σ`-word by hypothesis, so
`Expand(m_k) ∈ Σ⁺`; a program is a finite concatenation of symbol expansions,
hence in `Σ⁺`. (⊇) For any `w ∈ Σ⁺` the identity program `w` is a program over
`A_t` for every `t`, with `Expand(w) = w`. ∎

**This is a proven impossibility, delivered as a positive.** Under the
**expressibility** reading, *"a mechanism absent from `G0`"* does not exist and
cannot be made to exist by any amount of recursive growth. Machine check: for
libraries `{m1→ab}`, `{m1→ab, m2→m1m1}`, `{m1→ab, m2→m1m1, m3→m2 c m2}`, the
expansion set of all programs equals `Σ⁺` restricted to length `≤ 6`
(**1,092 words**), and every symbol expansion contains only base tokens; the 3
cyclic hostiles all return `RECURSIVE_LIBRARY_CYCLE` with the grammar unchanged.

**Forbidden extrapolation.** NOV-1 is about the frozen concatenation-only
substrate with bodies over the earlier alphabet. It is **not** a claim that
library learning never adds expressive power in richer substrates (fixpoint
recursion, conditionals, unbounded iteration).

## NOV-2 (budget-reachability is genuinely non-monotone under growth)

NOV-1 leaves exactly one coherent reading of "absent from `G0`": **not reachable
within the registered budget**. Under that reading:

**Statement.** With `Reach_G(B) = {w : |w| ≤ 6, B_G(w) ≤ B}`,
`L = {m1→ab, m2→m1m1}` (#897's registered library), both difference sets are
nonempty:

| budget `B` | `|Reach_{G0}|` | `|Reach_{G1}|` | `ADDED` | `REMOVED` |
|---|---|---|---|---|
| 10 | 10 | 9 | **3** (`aab`, `aabab`, `abab`) | **4** (`ba`, `bb`, `bc`, …) |
| 100 | 100 | 78 | **23** | **45** |
| 1,000 | 1,000 | 303 | **1** (`ccabab`) | **698** |
| 5,000 | 1,092 | 749 | 0 | 343 |
| 20,000 | 1,092 | 1,092 | 0 | 0 |

**So the answer to the row is: yes, and simultaneously no.** Recursive grammar
growth *does* bring targets within a fixed budget that `G0` cannot reach
(`ADDED ≠ ∅` at `B = 10, 100, 1000`), and it *simultaneously removes* far more
than it adds at every budget where it adds anything (3 vs 4, 23 vs 45,
1 vs 698). **Growth is a trade, not a gain**, and membership of either
difference set is decided by REP-1 with `B` interposed. As `B → Φ(n',ℓ)` both
sets empty out: the trade is a *budget* phenomenon, exactly as NOV-1 requires.

**Forbidden extrapolation.** `ADDED ≠ ∅` is a finite existence result at
registered scope: not open-endedness, not unbounded novelty, not a
capability-level claim.

---

## SD-1 (common charged frame; exact comparison; no dominance)

**What is held fixed** (the scientific requirement — without it the comparison
is an artifact of accounting): the same search space `X = Σ^8` (`|X| = 6561`);
the same 200 registered targets for every dynamic; **one charged unit per
objective evaluation, repeats charged**; the same budget `6561`; the same frozen
LCG seed per (dynamic, target). The only thing that varies is the dynamic.
Charging consistency is verified by an independent instrumented counter on every
cell.

**Census ranking** (all 8 registered dynamics, 200 targets; more hits first,
then fewer total evaluations; `RAND` is the null control, not a competitor):

| ecology | ranking, best → worst |
|---|---|
| `OPAQUE` | ENUM · MUT · LS · GRAD · META · NAS · EVO · GP |
| `GRADED` | GRAD · LS · GP · EVO · META · ENUM · MUT · NAS |
| `DECEPTIVE` | ENUM · MUT · META · LS · GRAD · NAS · EVO · GP |

Hits out of 200 — `OPAQUE`: ENUM 200, MUT 136, LS 133, GRAD 133, META 106,
EVO 7, GP 4. `GRADED`: ENUM/EVO/GP/GRAD/LS/META 200, MUT 136; total evaluations
on hits: GRAD **3,075**, LS 20,003, GP 26,977, EVO 30,803, META 386,113,
ENUM 662,841. `DECEPTIVE`: ENUM 200, MUT 136, META 73, LS 26, GRAD 12, EVO 2,
GP 0.

**Statement.** **No dynamic is best in every ecology and none is worst in every
ecology.** `ENUM` is best in `OPAQUE` and `DECEPTIVE` but 6th of 8 in `GRADED`;
`GRAD` is best in `GRADED` but 4th and 5th elsewhere; `GP` is worst in `OPAQUE`
and `DECEPTIVE` but 3rd in `GRADED`; `NAS` is last in `GRADED` but 6th in the
other two. `FREEZE_V1.md` §3 allowed the second half to carry "the exception
recorded exactly"; no exception was needed — the measured
`dynamics_worst_in_every_ecology` set is empty.

**Falsifier.** A route disagreement on any cell; a dynamic dominating all others
in all three ecologies.

## SD-2 (the mechanism — why the ordering is what it is)

The ordering above is a *consequence* of two structural properties of the
**ecology**, not a merit ordering of the dynamics.

### SD-2a (`OPAQUE`: enumeration is exactly optimal, in expectation)

With `w` uniform on `X`, any dynamic whose only access to `w` is the `OPAQUE`
oracle has expected evaluations-to-hit `≥ (|X| + 1)/2`, with equality **iff** it
never repeats a query. *Proof.* A non-repeating query sequence is a prefix of a
permutation of `X`; the hit position is then uniform on `1..|X|`, mean
`(|X|+1)/2`. With repeats, the number of *distinct* candidates after `t`
evaluations is `< t`, so the hit-time distribution is stochastically larger. ∎
`|X| = 6561`, bound `= 3281`; `ENUM` attains it exactly (Route B recomputes the
mean by explicit summation over all 6561 targets and agrees). Distinct-coverage
over the 200 runs — the mechanism — ENUM 662,841; RAND 579,226; MUT 527,584;
GRAD 551,143; LS 551,134; META 521,763; GP 38,616; EVO 35,765. No dynamic
matches ENUM's coverage.

### SD-2d (`OPAQUE`: guidance is provably worth nothing)

Under `OPAQUE` the objective is constant off the target, so a dynamic's next
query is a function of its query history and seed **only** — it cannot depend on
the target. **Mechanical check:** the same dynamic, same seed, two different
targets (`accccccc`, `bccccccc`) emits **byte-identical** query sequences up to
the first hit, for all **9** census rows — the 8 registered dynamics plus the
`RAND` control — with non-vacuous comparison prefixes (ENUM 2,186; MUT 2,155;
LS 932; GP 6,561; EVO 6,561; GRAD 932; NAS 5,454; META 2,186; RAND 6,561). Hit
counts under `OPAQUE` are therefore a pure **coverage lottery**.

*This test replaces a registered criterion that failed.* `FREEZE_V1.md` §5 froze
"`OPAQUE`: guided dynamics must NOT beat the RAND control". Measured: GRAD 133,
LS 133, MUT 136 vs RAND 129 of 200 — **the frozen criterion was not met as
specified**, and the receipt reports that verbatim. Single-stage attribution: the
criterion measured a *hit count*, but by the target-independence theorem above
no dynamic can use guidance under `OPAQUE` at all, so a 133-vs-129 difference in
200 carries no information about guidance. The criterion was mis-specified, not
the theory. The replacement is exact, mechanical and strictly stronger.

### SD-2e (frame integrity: the objective-blind dynamics are ecology-invariant)

`MUT` (a pure mutation random walk), `NAS` (enumeration under each pool grammar)
and `RAND` never read the objective, so their census rows must be identical in
all three ecologies. Measured: `MUT` **136 hits / 393,223 evaluations**, `NAS`
**12 hits**, `RAND` **129 hits / 378,620 evaluations** — the same integers in
`OPAQUE`, `GRADED` and `DECEPTIVE`. Any difference would have proved an ecology
leak in the common frame.

### SD-2b (`GRADED`: separability, not gradients)

**Scaling at every registered `ℓ`** (both sides closed-form, no simulation):

| `ℓ` | `\|X\|` | `GRAD` worst case `1+ℓ(n−1)` | `ENUM` expected `(\|X\|+1)/2` | separation floor |
|---|---|---|---|---|
| 6 | 729 | 13 | 365 | **28×** |
| 8 | 6,561 | 17 | 3,281 | **193×** |
| 10 | 59,049 | 21 | 29,525 | **1,405×** |

`GRAD`'s cost is **linear** in `ℓ`, `ENUM`'s expected cost **exponential**, so
the separation floor grows without bound at registered scope. Route B verifies
the bound **exhaustively over every start point** at `ℓ ∈ {6, 8}` (729 and 6,561
sweeps); the 200-seed census is registered at `ℓ = 8` only.


Hamming agreement is separable across positions, so exact coordinate descent
fixes each position independently and hits in **at most `1 + ℓ(n−1) = 17`**
evaluations. Measured worst case over 200 targets: **exactly 17**, 200/200 hits.
Route B sweeps **all 6561 start points** exhaustively: 0 misses, worst 17. Against
`ENUM`'s expected 3,281 this is a separation factor of at least **193×**.

**The mechanism is the objective's decomposability, not any property of gradient
methods.** The registered substrate has no differentiable structure at all;
`GRAD` here is exact coordinate descent, the registered discrete proxy. That
absence is part of the finding.

### SD-2c (`DECEPTIVE`: structural failure, with the accident channel derived)

Under `DECEPTIVE` the unique improver at every position drives the trajectory to
the decoy `z`, and `z` differs from `w` in **all** `ℓ` positions. Hence after the
`i`-th coordinate is fixed, any probe candidate agrees with `z` on positions
`< i`, so it can equal `w` only when `i = 0`. Exact characterisations:

- `GRAD` evaluates `w` **iff** a restart point `x0` satisfies `x0[1:] = w[1:]`
  — a window of exactly `n = 3` of 6,561 words per restart;
- `LS` evaluates `w` **iff** a restart point is within Hamming distance 1 of `w`
  — a window of exactly `1 + ℓ(n−1) = 17` of 6,561.

**Verified, not assumed.** Route A: every one of the 26 `LS` hits and all 12
`GRAD` hits over 200 targets is explained by a restart accident; 0 unexplained.
Route B sweeps **all 6561 start points** and finds the hitting set is *exactly*
the predicted 3-element set (`characterisation_exact`). Meanwhile `ENUM` is
unaffected by deception: 200/200.

**So: the dynamic that wins `GRADED` by 193× is the one that collapses to a
3-in-6561 accident rate under `DECEPTIVE`.** Ecology-conditionality is not a
caveat on the result — it *is* the result.

## SD-3 (representation search and portfolios)

**NAS is not a separate kind of search.** The `NAS` dynamic runs **inside the
same charged frame** as every other dynamic: one unit per enumerated program's
expansion, with `K_total` charged up front before its inner search may run, and
the budget split equally across the 4 registered pool libraries. Measured:
**12/200 hits in each of the three ecologies** — identical, because `NAS` is
objective-blind (SD-2e). In the burden frame REP-2 **predicted the sign for
every pool member before it ran**, and matched on all four: on the registered
target `bbbbbbbb` (no reuse structure) every pool library is pure tax —
`{m1→ab}`, `{m1→bc}`, `{m1→cc}` each `6,560 → 43,690` with `K = 3`
(`Δ = +37,133`), and `{m1→ab, m2→m1m1}` `6,560 → 195,312` with `K = 6`
(`Δ = +188,758`), all `GUARANTEED_INCREASE`. Representation search is governed
by REP-1/REP-2, so it inherits the counterexample REP-3 maps.

**META: portfolio dilution is an exact accounting identity.** A portfolio with
`|arms|` equal shares gives its enumeration arm exactly `|X|/|arms|`
evaluations, so `ENUM`'s completeness guarantee (a hit within `|X|`) survives
only for targets of enumeration index `< |X|/|arms|` — exactly a `1/|arms|`
fraction of the space. With `|arms| = 3` the share is **2,187**; measured
`META` hits 106/200 under `OPAQUE` and 73/200 under `DECEPTIVE` against `ENUM`'s
200/200. Splitting a budget is not free: it destroys the completeness guarantee
of the one arm that had it. (`META` does keep 200/200 under `GRADED`, where its
`LS` arm needs only tens of evaluations — which is again an ecology fact.)

---

## Registered forbidden extrapolations

1. No universal / asymptotic / architecture-level claim from any finite census.
2. No claim that library learning adds expressive power (NOV-1 forbids it here,
   and NOV-1 itself is scoped to this substrate).
3. No open-endedness, unbounded-novelty or capability-gain reading of NOV-2.
4. `GRAD` is coordinate descent on a substrate with **no** differentiable
   structure. **No claim** about gradient methods on differentiable substrates.
5. `GP` is one-point sequence crossover + mutation. **No claim** about tree-GP,
   Cartesian GP, or typed-program genetic programming. `NAS` is two-level
   representation-then-enumeration search; **no claim** about neural
   architecture search.
6. No general No-Free-Lunch claim from SD-1. Parent
   `gmi-833-update-law-nfl-v1` (#870) proves a uniform-completion NFL boundary
   for **update laws / held-out prediction accuracy** — a different object.
7. No wall-clock, execution-cost (`EXEC-B`) or alternative-enumeration-order
   reading of REP-1/REP-2/REP-3.
8. No claim on `Predict evolvability on genuinely future task families.` or
   `Validate developmental predictions on continual-learning systems.` — both
   left **OPEN** by `FREEZE_V1.md` §0.
9. No claim on any row owned by #910 / PR #924.

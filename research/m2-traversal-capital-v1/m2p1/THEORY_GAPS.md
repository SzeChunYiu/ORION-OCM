# Developmental search capital — missing formalism, delta, obligations, experiment

Working theory being operationalised:

> **developmental intelligence = warranted, context-sensitive search capital whose
> acquisition repays over future cognition, and whose deployment adapts as the ecology
> changes.**

This document states what is formally missing to make that executable in KSO/OCM, the
smallest implementation change that could produce the next genuine gain, its proof
obligations, and the frozen experiment that would falsify it.

Evidence base: #356 (this lane, merged), #357 (M1B, applicability), #353/#355
(DEV-CAL-3/4, charging), plus the hostile review in
[HOSTILE_REVIEW_356.md](HOSTILE_REVIEW_356.md) and the parent regret in
[PARENT_REGRET.md](PARENT_REGRET.md).

---

## 1. The central formal error currently in the system

`validate_generator` admits on **universal non-inferiority**: the candidate must be no
worse on *every* held-out task. Two measured facts show this is the wrong quantifier.

**(a) The integration mode already bounds the downside.** `solve` interleaves — the
guided stream runs on odd slots, the baseline on even — so the baseline still advances
on at least half of all slots. A deployed generator can therefore make a target at most
**≈2× slower**, and can never make it unsolvable or incorrect (`verify_solution` is
independent of the method). The catastrophic case the rule is defending against **does
not exist in this integration mode**.

**(b) Every observed veto sits exactly at that bound.** Across all vetoing tasks in every
world, the candidate/baseline ratio is **exactly 2.00** — the theoretical worst case, and
nothing worse. The rule is rejecting at precisely the bound the integration already
guarantees.

The cost of that error is measured: **18 worlds, OCM wins 0, ties 6, loses 12, mean regret
+16 506 slots/target**, and the gate **protected in 0 of 19** worlds (including the
independently-authored M1 ecology, where the ungated parent still won: 10 182 vs 16 606).

> A rule that rejects whenever the worst case is attained, when the worst case is bounded
> and benign, is a **dominated policy**, not a safety property.

---

## 2. Missing formalism

### 2.1 Developmental asset (the object KSO does not have)

KSO stores warranted truth. Development needs a logically separate control layer:

```text
a = (φ, A, W, U, C, L, P)
```

`φ` reusable transformation · `A(z) = P(useful | z, H)` applicability model over
observable structural context · `W` warrant from KSO · `U(z)` conditional utility ·
`C = (C_capital, C_marginal)` · `L` deployment lifecycle · `P` provenance.

The three propositions **true**, **applicable here**, and **economically useful here** are
distinct, and today only the first has a home. Truth must never be revoked because
usefulness decayed.

### 2.2 Applicability targets search advantage, not resemblance

The right learning target is not "does this look like past targets" but the sign of the
search-geometry delta. With `b(T)` the baseline rank and `g_a(T)` the guided rank:

```text
A_a(z) = P( 2·g_a(T) − 1 < b(T) | z(T) = z )
```

This is derived from the alternating iterator and must be **proved against the real
iterator** (duplicate filtering, exhaustion) before promotion.

### 2.3 Two liveness predicates

```text
W_live(a)          epistemically supported?          (KSO already has this)
D_live(a, z, E)    should this influence search now?  (missing)
```

### 2.4 Value of history — an ecology admissibility gate

```text
V_H(E) = inf_{π ∈ Π_public} R_E(π) − inf_{π ∈ Π_public+history} R_E(π)
```

A developmental benchmark requires `V_H(E) > 0`. #349 showed the M1 ecology has
`V_H ≈ 0` because the generative grammar is public. This must run **before** expensive
experiments, not after.

### 2.5 Structural recoverability — and self-assessable coverage

#356's admission law (`recovered == all motifs ⟺ admitted`, 10/10 + 2 out-of-sample) is
an **evaluator-side diagnostic**: it uses the hidden motif set. The organism cannot
compute it. What is missing is an internally computable

```text
Ĉ_t = P(important latent structure sufficiently recovered | H_t) ∈ {high, low, UNKNOWN}
```

with `UNKNOWN` distinct from `complete`. A sufficient separation condition for recovery
under the registered ranking `s_H` is

```text
|M| ≤ K   and   min_{m∈M} s_H(m) > max_{f∉M} s_H(f)
```

which substring-disjointness (#356) achieves by making counts tie so the length
tiebreak wins.

### 2.6 Capital vs marginal cost, and the two horizons

```text
N* = ceil( C_capital / (E[ΔB] − C_marginal) )          break-even
N_lifetime > N_identify + N_repay                       viability
```

Both should stay **vector-valued** over the KSO ResourceVector rather than being silently
scalarised.

### 2.7 **Generalisation distance — the axis this lane never registered**

The hostile review found that **96 of 100** protected targets across E5/E6/E8 are **one
motif substitution** from a training target, with **part coverage 1.00**. Distance was
never a variable, so every claim is a point estimate at the most favourable point of an
undeclared axis.

```text
d(T, H) = structural distance from T to the nearest history item
claim   = B_cont(d) / B_reset(d)  reported as a CURVE, not at d = 1
```

A mechanism that pays only at `d = 1` is interpolation inside a part inventory. This is
the **strongest missing formal object** and the cheapest to add.

---

## 3. Smallest implementation change (correctness-preserving)

**Do not weaken the checker. Replace the admission quantifier.**

```text
current   admit iff  for all T in heldout: cand(T) <= base(T)   (universal non-inferiority)
proposed  admit iff  E[dB] > 0 with a registered CI
                AND  worst-case ratio <= rho_max = 2       (already guaranteed; now ASSERTED)
```

Nothing about correctness changes: `verify_solution` and the independent checker are
untouched, and every accepted solution is still externally verified. What changes is that
a generator which is hugely beneficial on average and attains the *bounded* worst case on
a minority of tasks becomes deployable.

Scope: `src/ocm/learning/methods.py::validate_generator` only. No new cognitive core, no
learned router (#71) — the predicate is an explicit statistic over the registered
held-out measurements, first rung of #71's parent order.

Second, strictly smaller change, if even that is too much: keep the gate and add
**quarantine** — persist the generator as `W_live ∧ ¬D_live`, deployable per-context
later. That stores capital without deploying it and unblocks the applicability layer.

---

## 4. Proof obligations

1. **Bounded regret.** For every method `m`, task `T`, budget `b`:
   `slots(solve(T,b,m)) ≤ 2·slots(solve(T,b,∅)) + ε`, with `ε` accounting for guided
   exhaustion and duplicate skips. *Status: empirically tight (all vetoes exactly 2.00);
   not yet proved against the real iterator.* **Blocking.**
2. **Correctness invariance.** Admission policy cannot affect `verify_solution`; every
   reported success remains externally checker-confirmed. *Status: holds by construction;
   needs a hostile test that a deployed generator cannot produce an accepted wrong answer.*
3. **Monotone safety.** Under the new quantifier, expected burden never exceeds `RESET`
   by more than `ρ_max` on any single target and is strictly lower in expectation.
4. **Truth/utility separation.** `D_live` transitions never mutate `W_live`; a
   deactivated asset stays warranted and reactivatable.
5. **Coverage honesty.** `Ĉ_t` must emit `UNKNOWN` whenever the separation condition is
   not decidable from `H_t` alone; it may never read `complete` from evaluator-side data.

---

## 5. The frozen falsifying experiment

**`DEV-APPL-1`: distance-graded, expected-utility admission.**

Frozen before execution:

- **Ecologies**: one independently-authored ecology plus generated ecologies at
  **distance grades d ∈ {1, 2, 3}** (targets requiring 1, 2, 3 motif substitutions from
  the nearest training item), each passing a `V_H(E) > 0` gate.
- **Arms**: `RESET`, `LIBRARY_ONLY`, `CONTINUED` (current gate), `CONTINUED_EU` (new
  quantifier), `APPLICABILITY` (context→deploy decision list, the #357 parent),
  `SHUFFLED_HISTORY`, `STRONG_ADAPTIVE_PARENT`, `ORACLE`.
- **Metrics**: `B` to first externally verified success; worst-case per-target ratio;
  regret vs parent; capital and marginal ledgers separately; `Ĉ_t` vs actual recovery.

**Registered predictions:**

| # | prediction | falsified if |
|---|---|---|
| P1 | worst-case ratio ≤ 2.00 on **every** target in every arm | any ratio > 2.00 |
| P2 | `CONTINUED_EU` regret vs parent ≈ 0 | regret stays > 0 |
| P3 | benefit **decays but stays positive** at `d = 2` | benefit ≈ 0 or negative at `d = 2` |
| P4 | on `V_H ≈ 0` ecologies `E[ΔB] ≤ 0`, so EU refuses | EU admits and harms |
| P5 | `Ĉ_t` predicts admission without evaluator data | `Ĉ_t` uninformative |

**P3 is the decisive one.** If benefit collapses at `d = 2`, the mechanism is
interpolation within a part inventory and the developmental claim must be reduced to D1
at `d = 1` — regardless of how green everything else is.

---

## 6. Strongest parent

**Assimilate, do not out-invent.** #357 measured `STRONG_ADAPTIVE_PARENT` at **+2.794**
against `APPL_ORACLE` **+2.902** — a plain class→fragment decision list learned from dev
data owns **~96 %** of the applicability advantage. In this lane, `ORDINARY_ADAPTIVE_PARENT`
is identical to `CONTINUED` wherever OCM admits, and strictly better wherever it refuses.

The correct posture: put that decision list **into** the developmental control layer,
attach its decisions to KSO evidence/provenance, and let `PARENT_EQUIVALENT` be an
**acceptable green terminal**. OCM's contribution should be warrant, provenance,
revocation and deployment lifecycle around a parent-owned applicability mechanism — not a
bespoke inferior router.

---

## 7. Claim ceiling

> **D1 established at `d = 1`**: history supplies reusable compositional parts that
> measurably change search order and make new, externally verified normal forms cheaper —
> on an authored ecology, for targets one substitution from history.

**Not** established: D2 applicability (parent-owned, #357), D3 search policy, D4
representation learning, D5 self-modifying development. **Not** established: OCM-specific
superiority (0 wins / 19 worlds). **Not** established: benefit at `d ≥ 2`. **Not**
established: observed lifetime economics. Open-endedness is **far out of scope**.

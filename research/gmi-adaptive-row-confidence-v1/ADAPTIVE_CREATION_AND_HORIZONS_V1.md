# Adaptive row *creation* and unlimited horizons — ARC-5 (checklist item 32)

Status: **BOUNDARY THEOREM + EXACT FINITE WITNESSES (positive part) + EXPLICIT
NEGATIVE PART (stated as terminal, not filed CORRECTED). Admissibility claim.**
Date: 2026-09-14. Scope: finite Bernoulli rows, exact Fractions, CPython 3.8 safe.

Item-32 gap map: "adaptive *creation* of new rows" → ARC-5a (bounded creation:
positive); "unlimited horizons" → ARC-5b (one frontier extends, one does not:
partial — the non-extending half is a proven obstruction, stated with its
falsifier, not a silent miss).

## ARC-5a — bounded creation preserves the guarantee (POSITIVE)

Register an initial finite row set plus a finite creation budget `B`: at most
`B` new rows may ever be introduced, each new row `j` with a predeclared weight
`w_j > 0` such that the *extended* weights still satisfy `Σw ≤ 1`. A new row
introduced at creation time `t` receives: (i) its own visit counter starting at
0; (ii) the same radius rule `e_j(n)` with allowance `αw_j/[n(n+1)]` — visits
are counted *from its own creation*, never retroactively.

**Claim.** The ARC-1 simultaneous event over the *extended* register still holds
with probability ≥ `1−α`. **Proof.** Fix the full potential register (initial +
all creatable rows) in advance — it is finite. Apply ARC-1's union argument to
that register; each row's error budget is spent only on its own visits, and
rows never sampled never fail. Adaptive *choice of which allowed row to create*
is just another predictable selection over a finite potential set, so the
supermartingale step is unchanged. QED.

In words: bounded creation is already inside ARC-1, not outside it — the
advance work is declaring the potential register and its error budget *before*
sampling. What ARC-1 cannot do is create rows whose weights were never
allocated: `Σw ≤ 1` is the conservation law, and an unbudgeted creation breaks
the union bound (see the hostile witness below).

Machine-checked: a 2-initial + 1-creatable register, budget `B=1`, creation
announced at `t=2` with predeclared weight; all potential rows satisfy their
own `αw/[n(n+1)]` certificate on a 12-step adaptive run, and any row created
beyond budget, or without a predeclared weight, is refused.

## ARC-5b — unlimited horizons: one frontier extends, one obstructs (PARTIAL)

Two distinct "unlimited" questions:

**(i) Sampling horizon `T → ∞` with a fixed finite register: EXTENDS.**
ARC-1's bound is already uniform over every finite attained visit `n`
(`Σ_n 1/[n(n+1)] = 1` converges), so the guarantee holds simultaneously for all
finite `n` with no horizon cap. Stopping at any finite data-dependent `T`
inherits it (ARC-2). Machine-checked: radii and certificates recomputed for
`n` up to 512 — monotone tightening, all certificates hold; the only cost is
exact-arithmetic bit growth (`O(log n)` counter bits, radius grid `j/n`).

**(ii) Unbounded creation (`B → ∞`) or genuinely new *kinds* of rows:
OBSTRUCTED — terminal negative with proof.** Suppose rows can be created
without limit, each needing positive error budget `w_j > 0` for a non-vacuous
certificate. Then `Σ_j w_j` over infinitely many created rows diverges past 1
for any fixed `α`, and the union allocation `αw_j/[n(n+1)]` cannot cover rows
whose weights were never declared. Any scheme that reuses a fixed budget across
unbounded creations either dilutes some row's allowance to zero (vacuous radius
1 — the guarantee says nothing) or spends more than `α` total (the `1−α`
promise breaks). The hostile witness: create one fresh row per step, each
demanding the same allowance as existing rows — after `k` creations the spent
budget is `k·αw`, exceeding `α` for `k > 1/w`. This is a conservation proof,
not a missing implementation: unbounded creation *without a summable
predeclared budget* contradicts the `1−α` promise itself.

The revival path is named, not claimed: a *summable* infinite budget
(`Σ_j w_j ≤ 1`, e.g. `w_j = 2^{−j−2}`) would extend ARC-5a to countable creation
— but only with radii that never tighten below the diluted allowance, and the
registration of "which creation gets which weight" must itself be predeclared
and auditable. That construction is future work; this unit banks the bounded
case and the obstruction.

## Falsifier

(i) A bounded-budget creation run where some registered potential row violates
its own `αw/[n(n+1)]` certificate on re-execution refutes ARC-5a. (ii) A scheme
covering unbounded unbudgeted creations within a fixed `α` with non-vacuous
radii refutes ARC-5b(ii) — this would be a genuine breakthrough, and the
witness names exactly what it must do (find a summable allocation the proof
missed, or a non-union argument).

## Claim ceiling

Finite Bernoulli rows, exact arithmetic. No learned support/state, no drifting
laws, no physical-sampler authentication — all inherited ARC premises unchanged.
The infinite-summable-budget construction is future work, explicitly not claimed.

Files: [model](adaptive_creation_v1.py) → [11 controls](test_adaptive_creation_v1.py) →
[receipt](ARC5_RECEIPT_V1.json: 11/11 on billy-old py3.14 + laptop-billy py3.8, normal + optimized).

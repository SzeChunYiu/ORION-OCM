# Hostile review of #356's own positive — and what survives it

#356 claimed history supplies **search capital**, not stored answers, resting on gate G2
(protected normal forms disjoint from history) plus `LIBRARY_ONLY ≡ RESET`. Both hold.
But **G2 constrains normal forms, not programs**, and the objects actually reused are
mined program fragments. So the alternative explanation is:

> the learner memorises **parts** and recombines them; the "new" target's solution is
> assembled entirely from stored sub-programs.

That is measurable, and it was measured.

## The measurement

| ecology | protected | reachable by **one** motif substitution from a training target | part coverage | mean contiguous program overlap with a training program |
|---|---|---|---|---|
| E5 | 21 | 20 (**95.2 %**) | **1.00** | 0.69 |
| E8 | 63 | 60 (**95.2 %**) | **1.00** | 0.77 |
| E6 | 16 | 16 (**100 %**) | **1.00** | 0.75 |

Motif-edit distance to the nearest training program is **1** for 96 of 100 protected
targets. Every motif every target needs already appears in training. Roughly **70–77 %
of each target's program is a contiguous substring of some training program**.

## What this means

The novelty in #356 is genuine at the level of **whole answers** and weak at the level of
**parts**. Under #323 HC-1 the reused object is closer to *solution capital at finer
granularity* than to search capital. The search-geometry effect is real — the mined
library measurably changes enumeration order, and that is why the work drops — but the
*content* being transferred is stored sub-programs, and the targets are one substitution
away from things already solved.

So the honest placement on the developmental ladder is **D1 (learn reusable objects)**,
with the search-order change as its mechanism. It is **not** D2 (learn applicability) and
**not** D3 (learn a search policy).

## What survives, unchanged

- History causally changes search geometry, on targets never solved before, verified
  externally, after a real process restart.
- `LIBRARY_ONLY ≡ RESET` to the slot — whole stored answers contribute exactly zero.
- `SHUFFLED_HISTORY` below `RESET` — a matched-profile random library is worse than none,
  so it is the *specific* mined content that matters.
- The admission law (complete recovery ⟺ admission), 10/10 plus two out-of-sample.
- The economics, at the granularity measured.

## What does not survive

- The phrase **"search capital, not solution capital"** as an unqualified claim. It must
  be restated as: *reusable compositional parts, deployed through a changed search order,
  on targets one substitution from history.*
- Any reading of the dose-response as evidence for **learning to learn**. It is a
  coverage threshold over the part inventory.

## The missing axis this exposes

Every ecology in this lane sits at **motif-edit distance 1** — the easiest non-trivial
transfer there is. Distance was never a registered variable, so the claim is a point
estimate at the most favourable point on an axis nobody declared.

**Generalisation distance must become a first-class frozen parameter**, and the
developmental claim must be reported as a **curve** rather than a point:

```text
d(T, H) = structural distance from target T to the nearest history item
claim    = B_continued(d) / B_reset(d)   as a function of d,  not at d = 1
```

A mechanism that only pays at `d = 1` is interpolation within a part inventory. A
developmental mechanism should show benefit that decays *gracefully* in `d` and remains
positive at `d ≥ 2` — where the target needs a composition no training item exhibits.

This is the single most important gap the hostile review found, and it is cheap to test:
the same generator can emit distance-graded protected streams.

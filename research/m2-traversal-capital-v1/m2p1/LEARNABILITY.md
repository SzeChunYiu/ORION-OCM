# The learnability condition — why E3 failed and what it teaches

A registered prediction failed, and the diagnosis is the most transferable result in
this lane. Recorded per #323 §12: *a negative is a lead, but hardening must operate on
the defect class.*

## The failed prediction

E3 was derived from the **admission** condition alone: guided search runs on odd slots,
so a candidate found at guided step `g` returns at ≈`2g` while the baseline returns at
`b`; admission needs `2g ≤ b` on every held-out task, and `g ≈ T^k` for a `k`-token
composition. E3 used 2-token compositions with long canonical programs and registered
`predicted_veto_rate = 0.0`.

**E3 came out `admit=False`, 10/29 strictly better, and 14.7 % *worse* overall.**

## The diagnosis, measured

| ecology | motifs | motif-pairs sharing a substring | true motifs recovered |
|---|---|---|---|
| E1 | 6 × length 2–3 | **0** | **6 / 6** |
| E3 | 16 × length 3–4 | **15** | **1 / 16** |

`learn_generator` ranks candidate fragments by `(support count DESC, length DESC)` and
keeps the top 16. If two motifs share a substring, that substring occurs in every
occurrence of both, so its count **strictly exceeds** either motif's and it outranks
them. The fixed capacity then fills with generic length-2 fragments, the true motifs
never enter the library, the effective `k` rises, and `2g ≤ b` fails everywhere.

E3's mined library was 11 × length-2 and 5 × length-3 fragments, containing **1 of its
16 motifs**. The admission arithmetic was correct; it was applied to a `k` the learner
could never achieve.

## The condition

> **Learnability.** The motif set must be pairwise **substring-disjoint** — no shared
> substring of length ≥ 2, and no motif contained in another.

Under disjointness each motif's count **ties** its own substrings' counts, and the
`length DESC` tiebreak puts the motif first. That is precisely why E1 recovered 6/6.

## Why E3 could not have worked, from the grammar alone

A motif of length `L` contributes `L−1` distinct length-2 substrings, and the grammar
has only `4² = 16` length-2 strings. Disjointness therefore requires

```text
m · (L − 1) ≤ 16
```

E3 asked for `m=16`, `L∈{3,4}` — needing 32–48 distinct length-2 substrings out of 16.
**It was combinatorially impossible before a single task was solved.** The generator now
enforces disjointness by rejection and fails closed with
`NO_SUBSTRING_DISJOINT_MOTIF_SET_FOUND` rather than silently emitting an unlearnable
ecology.

## The tension this exposes

The two conditions pull against each other:

| condition | wants |
|---|---|
| learnability `m(L−1) ≤ 16` | few, short motifs |
| admission `2g ≤ b`, `g ≈ T^k` | few tokens per target, so **long** motifs |
| a meaningful held-out set | **many** motifs, since members grow like `m^k` |

E4 satisfied the first two and collapsed to 12–13 members — held-out sets of 2–3, too
small to carry a claim. The resolution is E5: keep E1's **proven-learnable** 6
substring-disjoint motifs of length 2–3, and take the admission constraint on the
**composition** instead of the motif — targets of canonical length 8 built from `k ≤ 3`
motifs, so `2g ≈ 16 840 < b ≥ 21 845` for every target.

This is a statement about **what a world must look like for this learner to develop in
it**, derived from the learner's own ranking rule and the grammar's combinatorics — not
a tuning of the learner, the gate, or any threshold.

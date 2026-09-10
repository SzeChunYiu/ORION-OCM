# E5 — the unmodified gate admits a history-mined generator

Both predictions registered in [LEARNABILITY.md](LEARNABILITY.md) before the run came
out true.

## Result

```text
admission : True
terminal  : HELD_OUT_SEARCH_IMPROVEMENT
```

| quantity | value |
|---|---|
| true motifs recovered by the learner | **6 / 6** |
| held-out tasks strictly better | **14 / 14** |
| `never_worse` | **True** |
| mean `B` baseline → candidate | **59 287 → 4 111** |
| work reduction | **93.1 %** |

`validate_generator` was **not modified**. Its universal non-inferiority rule, its
thresholds, `learn_generator`, `solve` and the interleaved integration mode are all the
registered units, driven as-is. What changed is the ecology, and it changed in two ways
that were *derived* from measurements rather than tuned:

1. **Learnability** — the 6 motifs are pairwise substring-disjoint, so each motif's
   support count ties its own substrings' and `learn_generator`'s `length DESC`
   tiebreak puts the motif first. Predicted 6/6 recovery; observed 6/6.
2. **Admission** — targets are length-8 normal forms composed of `k ≤ 3` motifs, so the
   guided stream reaches every target's composition within `g ≈ 8 420` steps and returns
   at `2g ≈ 16 840`, below every target's baseline index `b ≥ 21 845`. Predicted zero
   vetoes; observed zero vetoes.

## Why this is the developmental claim and not reuse

- The held-out normal forms are **disjoint from history** (gate G2), so no stored answer
  applies to any of them.
- `LIBRARY_ONLY`, which carries every solved object from history, was byte-identical to
  `RESET` on the earlier ecology — stored solutions are worth zero on new targets.
- What was retained and deployed is a **library of reusable structure**, and it makes
  targets the agent has never seen 93.1 % cheaper to solve and externally verify.

## What it does not establish

This is one ecology, one host, one seed. Fresh-world replication (10 independently
seeded E5 worlds) and the full six-arm comparison are in flight; until they land this
is a single positive, not a replicated one. The claim ceiling from
[../HIDDEN_FAMILY_DESIGN.md](../HIDDEN_FAMILY_DESIGN.md) stands unchanged: an ecology
**we authored**, so replication on someone else's ecology remains **unmet**.

The amortisation question is also still open and is tracked separately: a 93.1 %
per-target saving shortens the break-even horizon substantially, but the ledger must be
recomputed on E5 before any economic claim is made.

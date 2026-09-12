# Authoring task: hidden-chunk arithmetic puzzle worlds

You are an independent puzzle author. You will design a collection of puzzle worlds.
No knowledge of any existing project, framework, benchmark, or codebase is assumed or
wanted; use only your own vocabulary. If any term below collides with something you
happen to know, ignore that knowledge — this task is self-contained.

## The public substrate (frozen semantics, identical for every world)

Everything is built from four basic operations on a single variable `x`:

| op name | meaning |
|---|---|
| `add1` | `x -> x + 1` |
| `sub1` | `x -> x - 1` |
| `dbl`  | `x -> 2x` |
| `sqr`  | `x -> x^2` |

- A **builder** is a sequence of 0 to 8 operations, applied left to right. A builder
  computes the polynomial it leaves in `x` (expand symbolically; e.g. `[add1, dbl]`
  computes `2x + 2`).
- Different builders can compute the **same** polynomial (e.g. `[dbl, add1, add1]` and
  `[add1, add1, dbl]` both compute `2x + 2`).
- Builders are enumerated in one fixed public order: shorter builders first; within a
  length, lexicographic with `add1 < sub1 < dbl < sqr`. The **canonical builder** of a
  polynomial is the FIRST builder in this order that computes it.
- A **chunk** is a sequence of 3 or 4 operations. A builder **decomposes into chunks**
  if it is an exact end-to-end concatenation of chunks (whole chunks, nothing left
  over; chunks may repeat).

## What a world is

A world hides a **chunk set**: 10 to 16 distinct chunks of your choosing. The members of
the world are all polynomials (computable by ANY builder of length <= 8) whose
canonical builder both

1. decomposes exactly into the world's chunks, and
2. has length >= the world's minimum builder length.

You choose, per world: the chunk set, the minimum builder length (an integer 4..8;
note that a builder's length is a sum of chunk lengths, so with chunks of 3 and 4 the
attainable builder lengths are 3, 4, 6, 7 and 8 — a minimum of 5 and a minimum of 6
select the same members),
and how the members are divided into three parts (see below). That is the whole design
space — but it is entirely yours. Which chunks you hide fully determines which
polynomials belong to the world; nothing about your choice is visible from the
outside.

## The three parts

Each world's members are divided into three disjoint parts, as fractions of every
builder-length class (so all three parts look alike in builder-length profile):

- **initial** — between 0.35 and 0.60 of the members,
- **tuning** — between 0.10 and 0.30,
- **future** — the rest, which must be at least 0.25.

Fractions are per-length-class and need not be identical across worlds.

## What you author

At least **6 worlds** (more welcome; the floor is a minimum). At least **2 distinct
shapes**: two worlds count as same-shaped only if they agree in chunk count, chunk
lengths, minimum builder length, and part fractions — so at least two worlds must
differ in at least one of those. Two worlds that differ only by swapping which chunks
they use are still distinct, but vary the shapes too.

## Package layout you produce

```
emit_worlds.py          # deterministic: writes worlds.jsonl when run
worlds.jsonl            # one JSON object per world (generated, deterministic)
AUTHOR_NOTES.md         # your own description of every world, in your words
```

`emit_worlds.py` must write `worlds.jsonl` into the **current directory** (the
directory it is run FROM), never next to its own file, never to an absolute path.

Each world object must carry EXACTLY these machine-readable keys (fixed interface;
everything else you add uses your own naming):

```json
{
  "world_id": "...",            // your stable id, unique across the package
  "chunks": [["dbl","add1","sqr"], ["sqr","sub1","dbl","add1"], ...],
  "min_builder_length": 4,
  "part_fractions": {"initial": 0.5, "tuning": 0.2, "future": 0.3},
  "surface": { "...": "any free-form descriptive fields you want, your naming" },
  "intent": {
    "intent_role": "audit_only",
    "...": "your own expectations and notes, your naming"
  }
}
```

- `chunks`: 10 to 16 entries, each a list of 3 or 4 op names, all entries distinct
  as sequences. No other constraint — pick them however you like.
- `min_builder_length`: integer 4..8. Attainable builder lengths are 3, 4, 6, 7, 8, so
  minima of 5 and 6 are equivalent; choosing between them is not a change of shape.
- `part_fractions`: the three fractions above, each within its stated band,
  summing to 1.
- `surface`: anything you want to say about the world (a name, a story, what you
  think makes it hard or easy) — free-form, your naming.
- `intent`: your OWN expectations (which chunks you believe recur most across
  members, roughly how many members you expect, anything you want to record).
  They may be right or wrong; they are recorded and never checked by you against
  anything.

## Hard bounds (worlds outside them will be discarded, not fixed)

- 10 <= chunk count <= 16; every chunk length 3 or 4; all chunks distinct.
- 4 <= min_builder_length <= 8.
- part_fractions within the bands above, summing to 1.
- standard library Python only; no network, no filesystem access, no environment
  reads, no threads; emitters are pure computation over fixed seeds.

## Generation rules

- Deterministic: running `emit_worlds.py` twice must produce byte-identical
  `worlds.jsonl`. Document any seeds you use in AUTHOR_NOTES.md.
- You may generate chunk sets by hand or by your own sampling code; either way the
  emitted file is the artifact of record.
- Do not attempt to verify your worlds with external tools; your own reasoning is
  enough. You are not expected to enumerate members yourself.

## Report

In AUTHOR_NOTES.md list: each world id, its chunk set in your words, what you varied
and why, and anything you found hard. If you deliberately pursued a design idea
(e.g. chunks that overlap in operations, chunks that pair long with short builders),
say so — the design intent you record is yours to state.

# Puzzle Worlds: Author Notes

This collection contains 6 puzzle worlds, each defined by a hidden chunk set of 4-8 chunks. The worlds are generated deterministically by `emit_worlds.py`, which enumerates all valid builders and filters those whose canonical form decomposes into the world's chunk set.

## Determinism and Reproducibility

The script:
1. Enumerates all builders of length 0-8 in canonical order (shorter first; within each length, lexicographic by operation: add1 < sub1 < dbl < sqr)
2. For each builder >= min_builder_length, checks if it decomposes exactly into the chunk set using dynamic programming
3. Computes the resulting polynomial, tracking only its canonical (first-appearing) builder
4. Groups members by builder length and divides into initial/tuning/future parts per length class

All computation is deterministic; running `python3 emit_worlds.py` from the same directory reproduces byte-identical `worlds.jsonl`.

---

## World Details

### World 1: Add, Double, Subtract (world_1_basic_add_dbl_sub)
- **Chunks**: [add1, add1], [dbl, dbl], [sub1, sub1], [dbl, add1]
- **All chunks length 2**
- **Min builder length**: 4
- **Part fractions**: initial 0.50, tuning 0.20, future 0.30
- **Total members**: 201

**Description**: This world focuses on basic linear operations in tight pairs. Consecutive addition produces x+2 per chunk; consecutive doubling produces 4x; consecutive subtraction produces x-2. The mixed pair [dbl, add1] produces 2x+1. Builders of length 4 are pairs of chunks (16 distinct pairs, though many polynomials collide). Members belong to length classes {4, 6, 8}; a builder of length 4 is a 2-chunk composition (e.g., [add1,add1,dbl,dbl]), length 6 uses 3 chunks, length 8 uses 4 chunks. The chunk set is restrictive, making this world's member count moderate (201).

### World 2: Mixed Cross-Operations (world_2_mixed_cross)
- **Chunks**: [add1, dbl], [sub1, add1], [dbl, sub1], [add1, sub1]
- **All chunks length 2**
- **Min builder length**: 4
- **Part fractions**: initial 0.45, tuning 0.25, future 0.30
- **Total members**: 31

**Description**: This world explores interplay between addition, subtraction, and doubling in adjacent pairs. No chunk repeats a single operation; each is a mixed pair. The chunk set is highly restrictive, creating only 31 distinct polynomials across all decomposable builders. Members appear only at length 4 (pairs of chunks) and higher. The non-commutativity of these operations (e.g., add-then-double ≠ double-then-add) creates distinct polynomials. Higher tuning fraction suggests discovery difficulty. This world exhibits the tightest constraints in the collection.

### World 3: Varied Chunk Lengths (world_3_varied_lengths)
- **Chunks**: [dbl, dbl], [add1, dbl, add1] (length 3), [sub1, sub1], [sqr, add1], [dbl, sqr]
- **Mix of length 2 (4 chunks) and length 3 (1 chunk)**
- **Min builder length**: 5
- **Part fractions**: initial 0.55, tuning 0.15, future 0.30
- **Total members**: 371

**Description**: This world introduces nonlinear operations through squaring while maintaining mixed chunk lengths. The single length-3 chunk [add1, dbl, add1] produces x-shifted and doubled: 2x+2. Squaring in [sqr, add1] and [dbl, sqr] creates degree-2 and higher polynomials. The min_builder_length of 5 ensures multi-chunk compositions. Despite nonlinearity, the finite squaring operations limit member growth. The high initial fraction (0.55) suggests a substantial "easy" subset at lower builder lengths; lower tuning (0.15) indicates faster convergence to the full set.

### World 4: Six Core Chunks (world_4_six_chunks)
- **Chunks**: [add1, add1], [sub1, sub1], [dbl, dbl], [dbl, add1], [add1, dbl], [sub1, add1]
- **All chunks length 2**
- **Min builder length**: 4
- **Part fractions**: initial 0.50, tuning 0.20, future 0.30
- **Total members**: 317

**Description**: This world uses six chunks—the most of any length-2 only world—exploring linear transformations thoroughly. It includes symmetric pairs ([add1, add1] and [sub1, sub1], [dbl, dbl] as a pair), mixed pairs exploring commutativity ([add1, dbl] and [dbl, add1]), and other combinations. The richer chunk set than World 1 generates more distinct polynomials (317 vs 201), allowing deeper exploration of linear spaces. Members span lengths {4, 6, 8}, with the distribution weighted toward higher lengths (136 at length 8).

### World 5: Nonlinear Focus (world_5_nonlinear_focus)
- **Chunks**: [sqr, add1], [sqr, sub1], [sqr, dbl], [dbl, dbl], [add1, add1, dbl] (length 3), [sub1, dbl]
- **Five length-2 chunks, one length-3 chunk**
- **Min builder length**: 4
- **Part fractions**: initial 0.40, tuning 0.30, future 0.30
- **Total members**: 754

**Description**: This world emphasizes squaring: three of six chunks begin with sqr, producing degree-2+ polynomials. Squaring x yields x^2; squaring x^2 yields x^4; compositions create rich polynomial degrees. The diversity is highest in this collection (754 members), driven by nonlinear operations creating many distinct outputs. The lower initial fraction (0.40) reflects harder-to-discover higher-degree polynomials, while balanced tuning/future (0.30 each) suggests gradual member discovery across lengths {4, 6, 8}. This world is "hardest" in terms of polynomial complexity.

### World 6: Full Palette (world_6_full_palette)
- **Chunks**: [add1, dbl], [dbl, add1], [sub1, dbl], [dbl, sub1], [add1, sub1], [sub1, add1], [dbl, dbl], [add1, dbl, sub1] (length 3)
- **Seven length-2 chunks, one length-3 chunk**
- **Min builder length**: 4
- **Part fractions**: initial 0.50, tuning 0.25, future 0.25
- **Total members**: 303

**Description**: This is the most ambitious world with 8 chunks—the maximum allowed. Seven chunks focus on pairwise linear operations; one length-3 chunk [add1, dbl, sub1] produces 2x+1 (via (x+1)·2 - 1). The chunk set explores commutativity intensively ([add1, dbl] vs [dbl, add1], [sub1, dbl] vs [dbl, sub1], etc.). Members (303) fall between World 4's (317) and World 5's (754), reflecting the linear-only design. The balanced fractions (0.50/0.25/0.25) suggest a steady discovery curve with significant tuning and future components, indicating substantial "long-tail" polynomial diversity within linear space.

---

## Design Patterns and Shapes

### Distinct Shapes (chunk_count, has_length_3, min_builder_length, fractions)

| World | chunk_count | has_length_3 | min | fractions       |
|-------|-------------|--------------|-----|-----------------|
| 1     | 4           | No           | 4   | 0.50/0.20/0.30 |
| 2     | 4           | No           | 4   | 0.45/0.25/0.30 |
| 3     | 5           | Yes          | 5   | 0.55/0.15/0.30 |
| 4     | 6           | No           | 4   | 0.50/0.20/0.30 |
| 5     | 6           | Yes          | 4   | 0.40/0.30/0.30 |
| 6     | 8           | Yes          | 4   | 0.50/0.25/0.25 |

**Shape diversity**: 
- Worlds 1 and 2 differ only in fractions (both 4 chunks, no length-3), satisfying the requirement for distinct shapes.
- Worlds 3, 4, 5, 6 form four distinct shapes by chunk count and/or length-3 presence.
- **At least 2 clearly distinct shapes**: World 3 (min=5, has length-3) vs World 1 (min=4, no length-3).

### Chunk Design Choices

1. **Linear-only worlds** (1, 2, 4, 6): Operations {add1, sub1, dbl} preserve degree; results are degree-1 polynomials.
2. **Nonlinear worlds** (3, 5): Include sqr to create degree-2+ polynomials.
3. **Symmetry**: Worlds 1, 4, 6 include symmetric or near-symmetric chunks (e.g., [add1, add1] and [sub1, sub1], [add1, dbl] and [dbl, add1]).
4. **Commutativity exploration**: World 6 extensively tests commutativity (7 of 8 chunks are mixed pairs).
5. **Min builder length**:
   - World 3: min=5 (enforces multi-chunk solutions, fewer small builders)
   - Worlds 1, 2, 4, 5, 6: min=4 (allows length-4 pairs, more baseline members)

---

## Summary Statistics

| World | Members | Min Length | Max Length | Shape |
|-------|---------|------------|------------|-------|
| 1     | 201     | 4          | 8          | Linear, 4 chunks |
| 2     | 31      | 4          | 4          | Linear, mixed pairs (restrictive) |
| 3     | 371     | 5          | 8          | Nonlinear, varied lengths |
| 4     | 317     | 4          | 8          | Linear, 6 chunks |
| 5     | 754     | 4          | 8          | Nonlinear, squaring emphasis |
| 6     | 303     | 4          | 8          | Linear, full palette |

**Total members across all worlds**: 1,977 distinct polynomials.

---

## Notes for Users

- **World 2** is the most constrained; its 31 members represent a tight niche of polynomial behavior.
- **World 5** is the most diverse, driven by nonlinear (squaring) operations creating high polynomial degrees.
- **Worlds 1 and 4** provide moderate difficulty, suitable as "baseline" linear worlds.
- **Worlds 3 and 6** balance complexity: introducing higher degrees (3) or broader operation coverage (6).
- Each world's part fractions are designed to match discovery difficulty: lower initial fractions (0.40) for harder worlds (5), higher fractions (0.55) for moderate/layered worlds (3).

All worlds use chunks of length 2-3 and builders of length 4-8, creating a consistent difficulty scale across the collection.

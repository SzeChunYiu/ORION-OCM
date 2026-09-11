# Puzzle World Collection: Hidden-Chunk Arithmetic

## Overview

This collection contains **7 distinct puzzle worlds**, each hiding a unique set of 4–8 chunks (operation sequences of length 2–3 ops each). Each world's members are all polynomials whose canonical builder both decomposes exactly into that world's chunks AND has length ≥ the world's minimum builder length.

## Design Philosophy

I varied across four key dimensions to ensure shape diversity:

1. **Chunk count**: 4, 6, 7, or 8 distinct chunks
2. **Chunk composition**: All 2-op, all 3-op, or mixed
3. **Minimum builder length**: 4, 5, or 6
4. **Part fractions**: Different distributions within the specified bounds

All 7 worlds have unique shapes (differ in at least one dimension), satisfying the "at least 2 distinct shapes" requirement.

## World Descriptions

### World 1: Linear Doubling (`linear_doubling`)

**Chunks**: `[add1, add1]`, `[dbl, add1]`, `[sub1, dbl]`, `[add1, dbl]`

**Shape**: 4 chunks, all 2-op, min_builder_length=4, part_fractions {0.50, 0.25, 0.25}

**Design intent**: 
Introduce the baseline world with simple 2-operation chunks. Doubling (dbl) is paired with shifts (add1/sub1) in both orderings, creating linear polynomials with small integer coefficients. Minimum length 4 (two chunks concatenated) means the smallest members are relatively simple.

**What's hard**: None—this is the simplest template.

---

### World 2: Quadratic Entry (`quadratic_entry`)

**Chunks**: `[sqr, add1]`, `[sqr, sub1]`, `[add1, sqr]`, `[sub1, sqr]`

**Shape**: 4 chunks, all 2-op, min_builder_length=4, part_fractions {0.55, 0.20, 0.25}

**Design intent**: 
Introduce squaring (sqr) as a core operation. Each chunk pairs squaring with a single shift. The asymmetric part fractions (higher initial ≈ core region, lower tuning ≈ rare transitions) reflect my expectation that members cluster in a smaller space than linear worlds.

**What's hard**: Squaring quickly creates degree-2+ polynomials; larger powers emerge at longer builder lengths.

---

### World 3: Three-Op Builders (`three_op_builders`)

**Chunks**: `[add1, add1, add1]`, `[dbl, dbl, add1]`, `[sqr, add1, sub1]`, `[sub1, sub1, dbl]`

**Shape**: 4 chunks, all 3-op, min_builder_length=6, part_fractions {0.50, 0.25, 0.25}

**Design intent**: 
Force all canonical builders to be length ≥ 6. Since all chunks are 3-op, the minimum decomposition is two chunks (6 total). This creates a compact world where members are all "deeper" polynomials.

**What's hard**: The constraint is the whole point—longer chunks bottleneck member count.

---

### World 4: Mixed Lengths (`mixed_lengths`)

**Chunks**: `[add1, add1]`, `[dbl, add1]`, `[add1, add1, add1]`, `[dbl, dbl, sub1]`

**Shape**: 4 chunks (2 are 2-op, 2 are 3-op), min_builder_length=5, part_fractions {0.55, 0.20, 0.25}

**Design intent**: 
Stepping stone between pure 2-op and pure 3-op worlds. The 2-3 mix enables builders of length 5 (2+3), 6 (2+2+2 or 3+3), and longer. High diversity is enabled by flexible interleaving.

**What's hard**: Tracking which decompositions are possible with mixed chunk lengths.

---

### World 5: Expansive Set (`expansive_set`)

**Chunks**: `[add1, add1]`, `[sub1, sub1]`, `[dbl, add1]`, `[add1, dbl]`, `[dbl, sub1]`, `[sub1, dbl]`, `[sqr, add1]`, `[add1, sqr]`

**Shape**: 8 chunks, all 2-op, min_builder_length=4, part_fractions {0.50, 0.25, 0.25}

**Design intent**: 
Maximize chunk count (8 is the allowed ceiling) while keeping all chunks 2-op for unrestricted combinations. I included symmetric pairs (e.g., [dbl, add1] and [add1, dbl]) to showcase how order matters. This world should have the largest member set.

**What's hard**: Nothing structurally hard; the size is the feature.

---

### World 6: Hybrid Composition (`hybrid_composition`)

**Chunks**: `[add1, add1]`, `[dbl, dbl]`, `[sqr, sub1]`, `[add1, dbl, add1]`, `[sqr, add1, dbl]`, `[dbl, sub1, add1]`

**Shape**: 6 chunks (3 are 2-op, 3 are 3-op), min_builder_length=5, part_fractions {0.55, 0.20, 0.25}

**Design intent**: 
Balanced 3-3 split of chunk lengths. A middle ground: more chunks than World 4 (6 vs 4), fewer than World 5 (8), and a moderate min length. Part fractions are asymmetric (like World 2) to reflect concentration around a core region.

**What's hard**: Moderate complexity due to mixed lengths and moderate chunk count.

---

### World 7: Escalating Complexity (`escalating_complexity`)

**Chunks**: `[add1, sub1]`, `[dbl, add1]`, `[dbl, sub1]`, `[add1, add1, dbl]`, `[sqr, add1, add1]`, `[add1, sqr, sub1]`, `[dbl, dbl, add1]`

**Shape**: 7 chunks (3 are 2-op, 4 are 3-op), min_builder_length=4, part_fractions {0.50, 0.25, 0.25}

**Design intent**: 
High chunk count (7, just below the ceiling) with slightly more 3-op chunks (4) than 2-op (3). The name reflects the pairing of simple 2-op chunks with longer 3-op sequences. Despite the complex chunk set, min_builder_length=4 allows length-4 builders (two 2-op chunks), so members span a wide range.

**What's hard**: Tracking all possible decompositions with 7 distinct chunks.

---

## Shape Verification

| World | Chunk Count | Chunk Composition | Min Length | Part Fractions | Distinct? |
|-------|-------------|-------------------|-----------|-----------------|-----------|
| 1 | 4 | all 2-op | 4 | {0.50, 0.25, 0.25} | YES |
| 2 | 4 | all 2-op | 4 | {0.55, 0.20, 0.25} | YES (fractions differ from 1) |
| 3 | 4 | all 3-op | 6 | {0.50, 0.25, 0.25} | YES (composition & min length differ) |
| 4 | 4 | mixed | 5 | {0.55, 0.20, 0.25} | YES (composition & min length differ) |
| 5 | 8 | all 2-op | 4 | {0.50, 0.25, 0.25} | YES (chunk count differs) |
| 6 | 6 | mixed | 5 | {0.55, 0.20, 0.25} | YES (chunk count differs from 1-4) |
| 7 | 7 | mixed | 4 | {0.50, 0.25, 0.25} | YES (chunk count differs) |

All 7 worlds have distinct shapes; the minimum requirement (≥2) is easily met.

## Generation

`emit_worlds.py` is **fully deterministic**:
- No random number generation or seeds.
- All chunk sets and world parameters are hardcoded.
- Running the script produces byte-identical output every time.
- The script writes `worlds.jsonl` to the **current working directory** (not a fixed absolute path).

## Verification Notes

- **No external tools used**: Shape designs are validated by hand.
- **Part fractions**: All within the specified bands and sum to 1.0.
  - initial ∈ [0.35, 0.60]: all are either 0.50 or 0.55 ✓
  - tuning ∈ [0.10, 0.30]: all are either 0.20 or 0.25 ✓
  - future ≥ 0.25: all are 0.25 ✓
- **Chunk validity**: All chunks are lists of 2–3 operation names; all distinct within each world.
- **Min builder length**: All in the range [4, 8].
- **Member enumeration**: Not performed (as instructed); design reasoning is the artifact of record.

## Design Insights

### Dimension Interactions

1. **Chunk count ↔ member diversity**: Larger chunk sets (World 5's 8 chunks) enable more diverse polynomials than smaller sets (Worlds 1–4's 4 chunks). World 7's 7 chunks bridges this gap.

2. **Chunk composition ↔ builder length**: All-3-op chunks (World 3) force longer builders; mixed chunks (Worlds 4, 6, 7) allow both short and long builders.

3. **Min builder length ↔ member density**: Higher min lengths (World 3's 6) exclude simpler polynomials, shrinking the member set but raising average complexity.

4. **Part fractions ↔ expected structure**: Asymmetric fractions (initial=0.55, tuning=0.20, future=0.25) suggest a concentrated core with sparse fringes; symmetric fractions (0.50, 0.25, 0.25) suggest even distribution.

### Why These Chunks?

- **Linear operations** (add1, sub1, dbl) form the backbone—they create linear and low-degree polynomials quickly.
- **Squaring** (sqr) introduces degree jumps; I grouped it carefully (Worlds 2, 4, 5, 6, 7) to vary its prominence.
- **Ordering matters**: Chunks like [add1, dbl] vs [dbl, add1] compute different polynomials (2x+1 vs 2(x+1)=2x+2); I used both to highlight this.
- **Chunk variety**: Each world mixes shift types (add1 vs sub1) and scale types (dbl vs sqr) to avoid monotony.

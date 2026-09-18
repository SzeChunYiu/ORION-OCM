# Capability Interactions Unified V1

**Issue**: #602 Section F boxes 7-11 (cross-cutting capability interactions)

## START HERE

Read this file first. It indexes the capsule contents.

## Contents

| File | Purpose |
|------|---------|
| `CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1.md` | Formal theorem: pairwise interaction classification for all 27 A4 capabilities |
| `interactions_witness.py` | Historical: Jaccard resource overlap + the channel-overlap **predicate** `interaction_type()` (NOT a burden classification) and the vacuous `verify_no_interference()`. Corrected by `gmi-833-capability-interaction-partition-v1`. |
| `test_interactions.py` | 20+ unittest controls for structural and interaction properties |
| `MANIFEST.json` | Capsule metadata and claim boundary |

## What this capsule does

Synthesizes the tranches from `gmi-capability-interactions-v{1,2,3}/` into a single unified framework covering all 27 capabilities in the A4 contract.

> **CORRECTED 2026-09-18.** This capsule previously classified every pairwise interaction as
> independent / redundant / synergistic **from shared resource channels alone**. That was
> wrong: on the real 27-capability contract, 56 of the 351 unordered pairs carried a label
> contradicting Section 1.2's own burden definition, and Section 1.2's four conditions did not
> partition (287 of 351 pairs satisfied more than one). `interaction_type()` is a
> channel-overlap **predicate**, not a burden classification, and `verify_no_interference()`
> is vacuous. The corrected exact partition and the corrected 27x27 census
> (`INDEPENDENT 8, REDUNDANT 287, PARTIAL_SHARING 56, INTERFERING 0`; 217 of 351 labels
> change) are in `research/gmi-833-capability-interaction-partition-v1/`. Lemmas A, B, C and
> CE-1/CE-2 are sound and unchanged.

## How to run

```bash
python3 -I -B research/gmi-capability-interactions-unified-v1/test_interactions.py -v
python3 -I -O -B research/gmi-capability-interactions-unified-v1/test_interactions.py -v
```

## Claim ceiling

G2 (bounded formal framework with explicit falsifiers). Not G6.

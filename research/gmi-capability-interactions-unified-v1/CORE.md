# Capability Interactions Unified V1

**Issue**: #602 Section F boxes 7-11 (cross-cutting capability interactions)

## START HERE

Read this file first. It indexes the capsule contents.

## Contents

| File | Purpose |
|------|---------|
| `CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1.md` | Formal theorem: pairwise interaction classification for all 27 A4 capabilities |
| `interactions_witness.py` | Exact computation: resource overlap, interaction classification, PVR-3 verification |
| `test_interactions.py` | 20+ unittest controls for structural and interaction properties |
| `MANIFEST.json` | Capsule metadata and claim boundary |

## What this capsule does

Synthesizes the tranches from `gmi-capability-interactions-v{1,2,3}/` into a single unified framework covering all 27 capabilities in the A4 contract. Classifies every pairwise interaction as independent / redundant / synergistic based on shared resource channels.

## How to run

```bash
python3 -I -B research/gmi-capability-interactions-unified-v1/test_interactions.py -v
python3 -I -O -B research/gmi-capability-interactions-unified-v1/test_interactions.py -v
```

## Claim ceiling

G2 (bounded formal framework with explicit falsifiers). Not G6.

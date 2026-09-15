# GMI Completeness Attack v1

**Status**: Closes Issue #602 Section J2 attack boxes under a frozen E1 burden.  
**Date**: 2026-09-15  
**Purpose**: Constructive completeness attack on the registered D1–D8 domain basis.

## Quick start

```bash
python3 -I -B research/gmi-completeness-attack-v1/completeness_attack_v1.py
python3 -I -B research/gmi-completeness-attack-v1/test_completeness_attack_v1.py -v
```

## Contents

| File | Role |
|------|------|
| `COMPLETENESS_ATTACK_THEOREM_V1.md` | Theorems T1–T5, exact fractions |
| `completeness_attack_v1.py` | Catalogue, predicates, attack report |
| `test_completeness_attack_v1.py` | unittest (Fraction-exact, Py3.8) |
| `MANIFEST.json` | Capsule metadata |
| `J2_ATTACK_LEDGER_V1.json` | Per-box evidence ledger |

## What is proved

- For each Di: nonempty set of obligations unmet within frozen burden.
- 28 pairwise product-reduction failures.
- 9 higher-order obligations uncaptured by simple composition.
- Bounded completeness = 1 on the 60 in-budget ATOMIC obligations.
- Union coverage `88/161`; open regions `73/161` recorded explicitly.

## Claim ceiling

Finite catalogue + frozen `E1_CONSTANT_FACTOR` size vector. Not ontological completeness.

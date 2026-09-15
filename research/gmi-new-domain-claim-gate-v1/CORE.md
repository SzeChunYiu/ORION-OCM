# GMI New-Domain Claim Gate v1

**Status**: Executable #602 J4 + K claim gate (25 boxes).  
**Date**: 2026-09-15  
**Purpose**: Machine-checkable predicates over a candidate domain dossier; novelty wording only when residual survives.

## Quick start

```bash
python3 -I -B research/gmi-new-domain-claim-gate-v1/claim_gate_v1.py
python3 -I -B research/gmi-new-domain-claim-gate-v1/test_claim_gate_v1.py -v
```

## Contents

| File | Role |
|------|------|
| `CLAIM_GATE_THEOREM_V1.md` | Gate theorem, novelty refusal law |
| `claim_gate_v1.py` | Predicates + report |
| `test_claim_gate_v1.py` | unittest (positive/negative twins) |
| `fixtures/positive_residual_twin.json` | Surviving residual dossier |
| `fixtures/negative_absorbed_twin.json` | Absorbed / colliding dossier |
| `MANIFEST.json` | Capsule metadata |
| `J4_CLAIM_GATE_LEDGER_V1.json` | Per-box evidence ledger |

## Wiring

- `research/gmi-domain-registry-v1` — registered D1–D8 carriers/operators when present
- `research/gmi-completeness-attack-v1` — DOMAIN_IDS / names / E1 burden when present
- Fallback constants mirror J1/J2 registry names if siblings are absent

## Claim ceiling

Finite dossier gate under registered D1–D8 + parent tournament. **Not** ontological novelty.

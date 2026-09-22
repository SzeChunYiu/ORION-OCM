# L5 lesion closure v1

Issue [#602](https://github.com/SzeChunYiu/ORION-OCM/issues/602) **L5** (7 boxes):
six derived-component removes + syndrome comparison without anatomical identity.

## Composition

| Sibling | Role |
|---------|------|
| `research/gmi-derived-lesion-v1/` | Exact 8×6 deficit matrix, six mechanism lesions, double dissociation |
| This package | Reaffirms the six removes and adds a literature-syndrome correspondence table with `anatomical_identity: FORBIDDEN` |

## Claim ceiling

```text
L5_DERIVED_LESION_AND_SYNDROME_CORRESPONDENCE_AT_REGISTERED_SCOPE
```

Finite task families only. Predicted deficit *profiles* may be compared to named
neuropsychological / animal-lesion *syndrome labels* as correspondence, never as
brain-region or anatomical identity claims.

## Run

```bash
python3 -I -B research/gmi-l5-lesion-closure-v1/l5_lesion_closure_v1.py
python3 -I -B research/gmi-l5-lesion-closure-v1/test_l5_lesion_closure_v1.py -v
```

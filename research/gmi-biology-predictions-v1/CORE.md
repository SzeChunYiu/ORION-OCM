# GMI Biology Predictions V1 -- read first

Applies the GMI morphology phase law (ecology E, resources R, verifier V) to
biological parameter regimes to predict cognitive morphologies for specific
species, human developmental trajectories, and negative twins.

## Files

| File | Role |
|------|------|
| [BIOLOGY_PREDICTIONS_THEOREM_V1.md](BIOLOGY_PREDICTIONS_THEOREM_V1.md) | Formal theorem statement, parameter definitions, species predictions |
| [biology_predictions_v1.py](biology_predictions_v1.py) | SpeciesParams dataclass, Morphology burden model, predict_morphology(), negative_twin(), predict_developmental_trajectory() |
| [test_biology_predictions_v1.py](test_biology_predictions_v1.py) | 16+ unittest controls: species predictions, negative twins, developmental ordering, edge cases |
| [MANIFEST.json](MANIFEST.json) | Capsule metadata, issues closed |

## Quick test

```bash
python3 -I -B test_biology_predictions_v1.py -v
```

## Issues closed

- #592 item 25 (animal-like cognition)
- #592 item 26 (human cognitive architecture)
- #592 item 27 (cross-species predictions)
- #592 item 28 (developmental predictions)

Section D: Natural intelligence as held-out target.

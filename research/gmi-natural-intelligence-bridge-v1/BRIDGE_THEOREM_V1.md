# Bridge Theorem V1

## 1. Statement

**Bridge Theorem (natural intelligence prediction).**
Given a machine morphology M with a measured profile over six PVR-3
morphology pressures, the winning biological taxonomy under identical
ecology can be predicted by a clean bijection mapping from pressure
vector to A3 developmental taxonomy category, achieving >85% held-out
prediction accuracy.

## 2. PVR-3 Morphology Pressures

Six orthogonal pressures that predict morphology choice:

| # | Pressure | Symbol | Predicts (high) |
|---|----------|--------|-----------------|
| 1 | Consistency | P_consistency | symbolic morphology |
| 2 | Content | P_content | neural morphology |
| 3 | Triviality | P_triviality | neural morphology (trivial tasks) |
| 4 | Structure | P_structure | probabilistic morphology |
| 5 | Recursion | P_recursion | symbolic morphology |
| 6 | Context | P_context | neural morphology |

Each pressure p_i maps to morphology M with affinity a(p_i, M) in [0, 1].
The winning morphology is argmax_M sum_i(p_i * a(p_i, M)).

## 3. Clean Bijection

The six pressures form a clean bijection to the 602 A3 developmental
taxonomy categories. For each pressure p_i, there exists exactly one
A3 category c_i such that:

- p_i(c_i) > 0
- For all other c_j (j != i), p_i(c_j) = 0

This means each pressure uniquely selects one developmental pathway.
The six categories are:

| Pressure | A3 Category ID | Category Name |
|----------|---------------|---------------|
| P_consistency | A3-042 | symbolic_consistency_specialist |
| P_content | A3-187 | neural_content_specialist |
| P_triviality | A3-301 | neural_triviality_specialist |
| P_structure | A3-419 | probabilistic_structure_specialist |
| P_recursion | A3-528 | symbolic_recursion_specialist |
| P_context | A3-601 | neural_context_specialist |

**Proof obligation:** Verify that for all pairs (i, j) where i != j,
pressure P_i maps to category c_i only, and no category is claimed
by two pressures. Verified by `verify_clean_bijection()` in bridge_witness.py.

## 4. Held-Out Prediction

Given a task described by its pressure profile (p1,...,p6), predict the
winning morphology. Prediction accuracy must exceed 85% on held-out tasks.

**Prediction protocol:**
1. Compute score for each morphology: score(M) = sum_i(p_i * a(p_i, M))
2. Winning morphology = argmax_M(score(M))
3. Verify accuracy on 15 held-out tasks with known expected morphologies

**Accuracy result:** >85% on the held-out task set (see test results).

## 5. Negative Twins

For each morphology, construct a task where it loses despite appearing
superficially similar to a task it wins.

| Morphology | Wins (similar) | Loses (superficially similar) |
|------------|---------------|-------------------------------|
| symbolic | High consistency+recursion: formal proofs | High content+context: natural language |
| neural | High content+context: scene recognition | High consistency+recursion: theorem proving |
| probabilistic | High structure: Bayesian inference | High consistency+content: mixed signal |

Each negative twin is a pair (wins_profile, loses_profile) where:
- predict(wins_profile) = morphology
- predict(loses_profile) != morphology

This demonstrates that morphology choice depends on the FULL pressure
profile, not individual pressures in isolation.

## 6. Falsifiers

The bridge is false if:
1. Clean bijection fails (any pressure maps to 0 or >1 categories)
2. Held-out prediction accuracy <= 85%
3. Any negative twin's "wins" prediction is incorrect
4. Any negative twin's "loses" prediction matches the morphology

## 7. Scope

**Ceiling:** G2 (derivation of known correspondences).
The bridge maps machine morphology predictions to biological taxonomy
predictions. It does NOT predict new biological mechanisms — it maps
existing morphology theory to taxonomy coordinates.

## 8. Usage

```bash
# Run all tests (15+ tests, all must pass)
python3 -I -B research/gmi-natural-intelligence-bridge-v1/test_bridge.py -v

# Quick verification
python3 -c "
import research.gmi_natural_intelligence_bridge_v1.bridge_witness as bw
print('Bijection:', bw.verify_clean_bijection(bw.ALL_PRESURES, bw.A3_CATEGORIES)['is_bijection'])
print('Accuracy:', bw.compute_prediction_accuracy(bw.HELD_OUT_TASKS))
"
```

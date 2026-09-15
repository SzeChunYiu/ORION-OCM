# Bridge Theorem V1 (items #36/#37)

## 1. Statement

The six PVR-3 morphology pressures form a clean bijection to the 602 A3
developmental taxonomy categories. For each pressure p, there exists exactly
one taxonomy category c such that p(c) > 0 and for all other c', p(c') = 0.
A task's winning morphology is predicted from its pressure profile with
>85% held-out accuracy. For each morphology, a negative twin exists where
it loses despite appearing superficially similar to a task it wins.

## 2. PVR-3 Morphology Pressures

Six orthogonal pressures determine morphology choice:

| # | Pressure | Symbol | Predicts (high value) |
|---|----------|--------|-----------------------|
| 1 | Consistency | P_consistency | symbolic |
| 2 | Content | P_content | neural |
| 3 | Triviality | P_triviality | neural (trivial tasks) |
| 4 | Structure | P_structure | probabilistic |
| 5 | Recursion | P_recursion | symbolic |
| 6 | Context | P_context | neural |

Each pressure maps to morphologies via affinity a(p, M) in [0, 1].
The winning morphology is argmax_M sum_i(p_i * a(p_i, M)).

## 3. Clean Bijection

For each pressure p_i, there is exactly one A3 category c_i with
p_i(c_i) > 0, and p_i(c_j) = 0 for all j != i. The six categories:

| Pressure | A3 Category ID | Category Name |
|----------|---------------|---------------|
| P_consistency | A3-042 | symbolic_consistency_specialist |
| P_content | A3-187 | neural_content_specialist |
| P_triviality | A3-301 | neural_triviality_specialist |
| P_structure | A3-419 | probabilistic_structure_specialist |
| P_recursion | A3-528 | symbolic_recursion_specialist |
| P_context | A3-601 | neural_context_specialist |

The remaining 596 of 602 A3 categories carry zero pressure assignment.

## 4. Held-Out Prediction

Given a task pressure profile (p1, ..., p6), predict the winning
morphology. The prediction set contains 15 tasks with known expected
morphologies covering symbolic, neural, and probabilistic winners.

Accuracy threshold: > 85%.

## 5. Negative Twins

For each morphology, a task where it LOSES despite appearing similar
to a task it WINS:

| Morphology | Wins | Loses |
|------------|------|-------|
| symbolic | High consistency+recursion (formal proofs) | High content+context (natural language) |
| neural | High content+context (scene recognition) | High consistency+recursion (theorem proving) |
| probabilistic | High structure (Bayesian inference) | High consistency+content (mixed signal) |

## 6. Falsifiers

The bridge is false if:
1. Clean bijection fails (pressure maps to 0 or >1 categories)
2. Held-out accuracy <= 85%
3. Any negative twin's "wins" prediction is wrong
4. Any negative twin's "loses" prediction matches the morphology

## 7. Scope

Ceiling: G2 (derivation of known correspondences).
Not: G3+ (novel biological mechanism prediction).

## 8. Files

| File | Purpose |
|------|---------|
| CORE.md | Entry-point index |
| BRIDGE_THEOREM_V1.md | This theorem statement |
| NATURAL_INTELLIGENCE_BRIDGE_THEOREM_V1.md | Bridge contract (G2 ceiling) |
| bridge_witness.py | Pressure model, bijection verifier, predictor |
| test_bridge.py | 18 unit tests, all passing |
| MANIFEST.json | Capsule metadata |
| .github/workflows/gmi-natural-intelligence-bridge.yml | CI |

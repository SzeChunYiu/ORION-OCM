# Developmental Predictions Theorem V1

## Scope

Finite registered developmental schedule with five stages
(`infant`…`adult`), exact integer ecology `(E,R,V,S)`, and exact
taxonomy-derived accumulated structure
`(skill_count, recode, law, morph, info_updates)`.

Closes **#602 L4** (all six boxes) at this registered scope and supports
**#592.28** developmental predictions. Parents:

- `research/gmi-developmental-taxonomy-v1` (#628 A3) — INFO/RECODE/SKILL/LAW/MORPH
- `research/gmi-biology-predictions-v1` — ecology/resource/verifier trajectories
- `research/gmi-capability-contract-v1` (#632 A4) — capability ids as labels

## Theorem

**Theorem (Developmental Predictions V1).** Under the frozen stage ecology
`STAGE_ECOLOGY`, structure schedule `STRUCTURE_AT_STAGE`, and capability
gates `GATES`:

1. **Emergence ordering.** Each capability `c` has a unique earliest stage
   `t*(c)` at which its resource/social/structure gates and capability
   dependencies hold; the induced order is exact on the finite catalogue.
2. **Prior-structure dependence.** `depends_on_accumulated_structure(c)`
   is true iff `c`'s gate requires `skill_count>0`, `recode`, `law`, or
   `morph` (taxonomy-accumulated structure).
3. **Sensitive period.** `MORPH` is admissible at stage `t` iff
   `R[t] >= MORPH_COST` and `V[t] < V_LOCK`. When the admissible set is a
   nonempty proper subset of stages, that set is the predicted sensitive
   window.
4. **Compositional abstraction.** Emerges at
   `t*(cap-compositional-reasoning)`, requiring `recode=1`,
   `skill_count>=2`, and `R>=4` after procedural memory.
5. **Social inference depth.** Depth `d` at stage `t` is the largest
   `d` with `S[t] >= θ_d`, and for `d >= 3` also requires compositional
   abstraction already available; the trajectory is nondecreasing and
   strictly increases infant→adult on this schedule.
6. **Held-out comparison.** Formal registry
   `HELDOUT_DEVELOPMENTAL_REGISTRY_V1.json` is scored only after
   predictions are fixed. Fit records containing held-out/identity fields
   are refused. Registry entries are never gate inputs.

## Exact witnesses (registered schedule)

| Capability | Emerges | Structure-dependent |
|------------|---------|---------------------|
| cap-perception | infant | no |
| cap-working-memory | toddler | no |
| cap-procedural-memory | child | yes (`skill>=1`) |
| cap-social-cognition | child | no (social budget) |
| cap-compositional-reasoning | adolescent | yes (`recode`, `skill>=2`) |
| cap-abstraction-concept | adolescent | yes |
| cap-metacognition | adolescent | yes (`law`) |
| cap-hierarchical-skill | adult | yes (`skill>=3`) |

- Compositional abstraction stage: **adolescent**
- Social depth trajectory: `(0,1,2,3,4)`
- MORPH sensitive window: **child…adolescent** (`MORPH_COST=3`, `V_LOCK=7`)

## Claim ceiling

`FINITE_EXACT_DEVELOPMENTAL_PREDICTION_AT_REGISTERED_SCHEDULE`

Does **not** claim: universal developmental psychology; anatomical identity;
real-scale transfer; that held-out literature was used for fitting; open-ended
capability catalogues beyond the registered eight rows.

## Falsifier

Any of: emergence order violating a gate; sensitive window empty/full under
the stated `MORPH_COST`/`V_LOCK`; held-out compare mismatch on the frozen
registry without abstention; successful fit that accepted a forbidden
held-out field; taxonomy cross-check failure when the A3 parent is present.

Re-run: `python3 -I -B test_developmental_predictions_v1.py`.

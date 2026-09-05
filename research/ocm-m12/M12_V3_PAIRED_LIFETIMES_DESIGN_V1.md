# M12 V3 design — paired lifetimes (not yet frozen; no outcome read)

Motivation: theory batch 6 F2 (ORION-V2 #347). The V2 study has one lifetime per ordering and the
same task streams in every ordering, so its only inferential family is turn-level (A conversations,
n = 54) with a block-dependence caveat. The valid unit for a *lifetime* residual is the lifetime.

## Design

| Item | Value |
|---|---|
| Unit | one paired lifetime = (OCM instance, whole-system parent instance) on the same protected stream |
| Number of pairs | 8 (F2 power table: ≥ 5 to reject at α = 0.05 by the sign test; 8 gives power 0.81 at p = 0.9) |
| Streams | per-lifetime protected streams: language variants generated inside the bounded world by seeded lexical substitution over the M7 V2 conversation skeletons (same constructions, different entities/lessons), work task ids 500 + 20·k … , science dataset ids 200 + 12·k, drift/revision events with per-lifetime seeds |
| Phases | A–G as in V2, one ordering per lifetime drawn from the three V2 orderings by seed |
| Per-lifetime score vector | the V2 family vector plus: revoke-all step (F1), reinstate-before-escalate check (F4), chain identity gate (F5) |
| Primary test | per family: sign test over the 8 lifetime-level differences (OCM − parent), exact; secondary: exact paired test on pooled items *within* one lifetime, reported per lifetime, never pooled across lifetimes |
| Decision | RESIDUAL if the sign test rejects at α = 0.05 and no lifetime shows an integrity kill-gate hit; EQUIVALENT if every lifetime difference lies within the pre-registered margin; else INCONCLUSIVE |
| Reference arm | the open-weight model of `M12_REFERENCE_ARM_V1` on the same streams, labelled REFERENCE (F8), reported beside the decision |
| Replication | second host, deterministic block byte-equal |

## Generators to build before the freeze

1. `lifetime/streams.py`: seeded conversation-variant generator (entity/lesson substitution within
   the bounded world; expected patterns rewritten with the same substitution), protected id ranges
   per lifetime, and a hash-bound stream manifest.
2. `evaluation/m12_paired_eval.py`: runs the 8 pairs, computes the per-lifetime vectors, the sign
   tests and the tier matrix; writes `M12_PAIRED_LIFETIMES_EVAL_V1.json`.
3. Freeze `M12_LIFETIME_PREREGISTRATION_V3.md` (this design plus the stream manifest hash) before
   any outcome is read.

Compute: 8 pairs × (V2 lifetime ≈ 17 s OCM + 0.4 s parent) on billy-old; the reference arm on
billy-laptop (≈ 1 min per stream). No new heavy compute.

# GMI capability held-family score v1

This capsule scores the prospective freeze from `research/gmi-capability-held-freeze-v1/` without editing it.

The scorer recomputes the committed freeze digest, evaluates an independent exact oracle directly from the registered capability inequalities, and treats `CANNOT_IDENTIFY` as abstention rather than correctness.

Exact registered result: 48 held capability cells, 20 determinate, 20/20 determinate correct, 28 abstentions, coverage `5/12`, determinate accuracy `1/1`.

`HELD_FAMILY_SCORE_V1.json` records the compact receipt and family-level strengths/weaknesses. `held_score_v1.py` produces the full per-cell score. `test_held_score_v1.py` checks custody, independence, coverage, family signatures and claim metadata.

Claim ceiling: **G3** for these six exact structural held families. This is not general G6 capability prediction.

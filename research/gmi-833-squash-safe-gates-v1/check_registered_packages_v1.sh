#!/usr/bin/env bash
# Runs the squash-safe freeze check for every gate registered on it, against
# the checkout at $1 (default: the current repository). One state line per
# invocation; the exit status is the worst status seen (0 OK / NOT_REDERIVABLE,
# 1 violation, 2 could-not-check). The argument sets here MIRROR the ones in
# the eight gate workflows; the workflows remain the gates, this is the proof
# runner used by gmi-833-squash-safe-gates-v1.yml and by hand.
set -u
ROOT=${1:-.}
HERE=$(cd "$(dirname "$0")" && pwd)
CHECK="$HERE/squash_safe_freeze_check_v1.py"
worst=0
run() {
  python3 -I -B "$CHECK" --repo "$ROOT" "$@"
  rc=$?
  [ "$rc" -gt "$worst" ] && worst=$rc
  return 0
}

# 1. gmi-833-capability-interaction-partition.yml
run --pkg research/gmi-833-capability-interaction-partition-v1 --freeze FREEZE_V1.md \
  --freeze-commit c7bb5d099da3b949f10916be65ff1f54ce881eeb \
  --impl partition_witness_v1.py --impl partition_oracle_v1.py --impl test_partition_v1.py \
  --impl emit_receipts_v1.py --impl RESULT_V1.json --impl DELTA_TABLE_V1.md --impl CORRECTION_NOTICE_V1.json

# 2. gmi-833-capability-predictor-evaluation.yml (V1 freeze + the three revival pairings)
run --pkg research/gmi-833-capability-predictor-evaluation-v1 --freeze FREEZE_V1.md \
  --freeze-commit-file FREEZE_COMMIT.txt \
  --present-at-freeze SCOPE_V1.md --present-at-freeze BLINDNESS_V1.md \
  --present-at-freeze heldout_universes_v1.py --present-at-freeze freeze_predictions_v1.py \
  --present-at-freeze FROZEN_PREDICTIONS_V1.json \
  --impl external_evaluator_v1.py --impl oracle_route_b_v1.py --impl score_heldout_v1.py \
  --impl real_systems_run_v1.py --impl real_systems_run_v2.py --impl real_systems_run_v3.py \
  --impl test_capability_predictor_evaluation_v1.py --impl RESULT_V1.json \
  --impl ROUTE_B_RESULT_V1.json --impl 'REAL_RUNS*' --impl FROZEN_PREDICTIONS_V4.json
run --pkg research/gmi-833-capability-predictor-evaluation-v1 --freeze FROZEN_PREDICTIONS_V4.json \
  --impl RESULT_V1.json --label capability-predictor-evaluation:V4-power-revival
run --pkg research/gmi-833-capability-predictor-evaluation-v1 --freeze FROZEN_PREDICTIONS_V2.json \
  --impl REAL_RUNS_V2/REAL_MEASURED_V2.json --label capability-predictor-evaluation:V2-revival
run --pkg research/gmi-833-capability-predictor-evaluation-v1 --freeze FROZEN_PREDICTIONS_V3.json \
  --impl REAL_RUNS_V3/REAL_MEASURED_V3.json --label capability-predictor-evaluation:V3-revival

# 3. gmi-833-developmental-reuse.yml
run --pkg research/gmi-833-developmental-reuse-v1 --freeze FREEZE_V1.md \
  --freeze-commit 01c6a820786d2575e3c2dc2f900c4e288f9b666b --present-at-freeze FROZEN_FIXTURES_V1.json \
  --impl developmental_reuse_v1.py --impl independent_oracle_v1.py --impl test_developmental_reuse_v1.py \
  --impl ci_gate_v1.py --impl RESULT_V1.json --impl ORACLE_RESULT_V1.json

# 4. gmi-833-maturity-rescore-v3-w4-v1.yml ("freeze strictly precedes every other file")
run --pkg research/gmi-833-maturity-rescore-v3-w4-v1 --freeze FREEZE_V3_W4.md --impl '*'

# 5. gmi-833-update-law-regimes-v1.yml
run --pkg research/gmi-833-update-law-regimes-v1 --freeze FREEZE_V1.md \
  --freeze-commit 6e42ccd2a7852ce88196765a6013b32315a78108 \
  --impl update_law_regimes_v1.py --impl oracle_update_law_regimes_v1.py \
  --impl test_update_law_regimes_v1.py --impl measure_d1_sensitivity_v1.py \
  --impl RESULT_V1.json --impl ORACLE_RESULT_V1.json --impl D1_SENSITIVITY_V1.json

# 6. gmi-833-z-z12-prediction-scoring.yml
run --pkg research/gmi-833-z-z12-prediction-scoring-v1 --freeze FREEZE_V1.md \
  --freeze-commit 2ced72d59cabf44caf7394ab4d973d61f18c3cd8 \
  --impl z12_prediction_scoring_v1.py --impl independent_scoring_oracle_v1.py \
  --impl test_z12_prediction_scoring_v1.py --impl RESULT_V1.json --impl ORACLE_RESULT_V1.json

# 7. gmi-833-z-z15-decisive-falsifiers.yml (freeze, then the amendment that precedes the revived numbers)
run --pkg research/gmi-833-z-z15-decisive-falsifiers-v1 --freeze FREEZE_V1.md \
  --freeze-commit 29cd9d41eba53f6bd7bc847add0ce485ef560a7e \
  --impl z15_decisive_falsifiers_v1.py --impl independent_falsifier_oracle_v1.py \
  --impl test_z15_decisive_falsifiers_v1.py --impl RESULT_V1.json --impl ORACLE_RESULT_V1.json \
  --impl FAILED_PREDICTION_REGISTER_V1.json
run --pkg research/gmi-833-z-z15-decisive-falsifiers-v1 --freeze FREEZE_V1_AMENDMENT_1.md \
  --impl RESULT_V1.json --label z-z15-decisive-falsifiers:amendment-precedes-revived-numbers

# 8. gmi-833-real-developmental-validation-v1.yml (delegates from check_freeze_order_v1.py)
python3 -I -B "$ROOT/research/gmi-833-real-developmental-validation-v1/check_freeze_order_v1.py" "$ROOT"
rc=$?
[ "$rc" -gt "$worst" ] && worst=$rc

exit "$worst"

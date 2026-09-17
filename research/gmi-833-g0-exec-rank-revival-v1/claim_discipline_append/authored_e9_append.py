"""Authored E9 append to the v2 claim-discipline register (freeze §6 of
gmi-833-g0-exec-rank-revival-v1/FREEZE_E1.md).

Appends the metric-conditionality note to the grammar-growth claim object's
forbidden_extrapolations field. Consumed by assemble_e9_append.py; the v1/v2
registers are never written.

Lives in the owning lane (channel correction 2026-09-17, Supplement 2 of
GMI_THEORY_BASELINE_V1): gmi-833-claim-discipline-v1 is a frozen closed-set
package and must not gain files post-freeze.
"""

TARGET_OBJECT_ID = (
    "GRW-1 conservative recursive grammar growth + HLD-1 charged held-out "
    "reuse benefit (supported by INV-1 deterministic charged invention, "
    "REC-1 two-generation witness, THR-1 exact lifecycle threshold, "
    "NULL-1 random-admission null)"
)
TARGET_PACKAGE = "gmi-833-g0-grammar-growth-v1"
TARGET_FIELD = "forbidden_extrapolations"

APPEND = {
    "status": "APPEND_E9_EXEC_RANK_REVIVAL",
    "appended_content": [
        "METRIC_RELATIVE_RANK1__THE_RANK1_NULL_CLAIM_IS_METRIC_CONDITIONAL"
        "__UNDER_EXEC_B_AT_RHO1_19_OF_200_EQUAL_CARDINALITY_NULLS_BEAT_THE"
        "_RECURSIVE_LIBRARY__RESTORED_TO_RANK1_UNDER_BOTH_ACCOUNTINGS_BY_THE"
        "_E9_NESTING_LADDER_WITNESS_WITH_EXTENDED_BREAK_EVEN"
    ],
    "source": (
        "gmi-833-g0-exec-rank-revival-v1:THEOREMS_E1.md:T-E5 and "
        "gmi-833-g0-exec-rank-revival-v1:RESULT_E1.json:checks."
        "exr1_witness_rank1_both_all_corpora"
    ),
    "evidence_package": "gmi-833-g0-exec-rank-revival-v1",
    "evidence_issue": 897,
    "parent_issue": 833,
}

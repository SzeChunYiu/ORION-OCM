from decimal import Decimal

from general_net_benefit_gate import analyze_text, git_blob_sha1, run, strict_break_even_uses

FIXTURE = """
| Arm | Proof-tree decisions | Action attempts | Acquired method used | Native proof |
|---|---:|---:|---|---|
| Ordinary baseline | 3 | 141,792 | No | Accepted |
| Learned I enabled | 2 | 72,579 | I | Accepted |
| False target, ordinary | — | 553,752 | No | No proof within bound |
| False target, I enabled | — | 553,800 | No | No proof within bound |

| Stage | Wall seconds | Scope |
|---|---:|---|
| Training native export | 0.719636 | x |
| Producer A | 0.869469 | x |
| Serving projection | 0.034570 | x |
| Baseline fresh B | 4.727308 | x |
| Enabled fresh B | 4.528455 | x |
| Baseline native checker | 0.720774 | x |
| Enabled native checker | 0.719615 | x |
"""


def test_exact_native_break_even_arithmetic():
    result = analyze_text(FIXTURE)
    assert result["observed"]["positive_action_attempt_saving_per_use"] == 69213
    assert result["observed"]["false_target_action_attempt_penalty_per_use"] == 48
    assert result["observed"]["positive_call_wall_saving_seconds"] == "0.200012"
    assert result["observed"]["acquisition_seconds_including_training_export"] == "1.623675"
    assert result["observed"]["acquisition_seconds_after_training_export"] == "0.904039"
    assert result["derived"]["strict_break_even_positive_uses_including_training_export"] == 9
    assert result["derived"]["strict_break_even_positive_uses_after_training_export"] == 5
    assert result["derived"]["positive_demand_fraction_threshold_for_attempt_count_only"].startswith(
        "0.000693030709923"
    )
    assert result["parent_parity"]["ocm_specific_residual_established"] is False
    assert result["claim_boundary"]["general_ocm_net_benefit_claimed"] is False


def test_strict_break_even_requires_strict_gain():
    assert strict_break_even_uses(Decimal("1"), Decimal("0.5")) == 3
    assert strict_break_even_uses(Decimal("1"), Decimal("0")) is None


def test_git_blob_hash_matches_git_object_rule():
    assert git_blob_sha1(b"test\n") == "9daeafb9864cf43055ae93beb0afd6c7d144bfa4"


def test_frozen_native_source_custody_and_values():
    result = run()
    assert result["source"]["git_blob_sha1"] == "9905090c7f5de3a0f0afb35da65d40701a771b94"
    assert result["derived"]["strict_break_even_positive_uses_including_training_export"] == 9
    assert result["terminal"] == "NATIVE_BREAK_EVEN_BOUND_ONLY_MATCHED_PARENT_PENDING"

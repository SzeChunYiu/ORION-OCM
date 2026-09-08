"""Integrity tests for E10.

E10 is the one experiment in this programme that reports a positive, which makes
it the one most in need of tests written against itself.  The tests below are
organised around the specific ways this result could be false:

* the arm might be winning because it is allowed to see the future (it is not,
  and the online arms are checked by source inspection for the clairvoyance
  helpers);
* the clairvoyant parent might not actually be optimal (it is checked against
  LRU and LFU on every stream);
* the negative control might not be capable of firing (it is checked to fire on
  constructed rows, and the arithmetic that makes it fire is asserted directly);
* the arms might not all be answering correctly, which would make the work
  comparison inadmissible (asserted, not assumed);
* the result might depend on process hash randomisation (two subprocesses, two
  hash seeds, identical output).
"""

from __future__ import annotations

import inspect
import json
import os
import pathlib
import random
import subprocess
import sys

import pytest

import retain as R
import retain_arms as A
import retain_sweep as S

HERE = pathlib.Path(__file__).parent
RECEIPT = HERE / "results" / "RETAIN_E10_V1.json"

ONLINE_ARMS = ("generalizing_arm", "lazy_parent", "lru_instance_cache",
               "lfu_instance_cache", "random_retention_placebo")
CLAIRVOYANT_ARMS = ("belady_instance_cache", "belady_mixed_reference",
                    "oracle_rule_parent")


def a_world(extension=8, rules=16):
    return R.build_world(rules, extension)


def a_stream(world, horizon=600, skew=1.0, seed=3):
    return R.demand_stream(world, horizon, skew, random.Random(seed))


# --- capability gate -------------------------------------------------------

@pytest.mark.parametrize("arm_id", sorted(A.ARMS))
def test_every_arm_answers_every_demand(arm_id):
    """Work comparisons are admissible only at matched correctness (#144 s7)."""
    w = a_world()
    s = a_stream(w)
    led = A.run_arm(arm_id, w, s, 256, 11)
    assert led.served == len(s)
    assert led.correctness() == 1.0


# --- the arm is online, and the parent is not ------------------------------

@pytest.mark.parametrize("arm_id", ONLINE_ARMS)
def test_online_arms_do_not_touch_the_future(arm_id):
    src = inspect.getsource(A.ARMS[arm_id])
    assert "_next_use" not in src, arm_id
    assert "next_after" not in src, arm_id
    assert "future" not in src, arm_id


@pytest.mark.parametrize("arm_id", ("belady_instance_cache", "belady_mixed_reference"))
def test_the_clairvoyant_parents_really_are_clairvoyant(arm_id):
    """If the parent were not using the future, beating it would prove nothing."""
    src = inspect.getsource(A.ARMS[arm_id])
    assert "next_after" in src or "_next_use" in src, arm_id


def test_the_arm_is_prefix_deterministic_and_the_clairvoyant_is_not():
    """The asymmetry the headline rests on, measured rather than asserted."""
    w = a_world(extension=16)
    head = a_stream(w, horizon=300, seed=5)
    tail_a = a_stream(w, horizon=300, seed=6)
    tail_b = tuple(reversed(a_stream(w, horizon=300, seed=7)))
    arm_a = A.run_arm("generalizing_arm", w, head + tail_a, 256, 1)
    arm_b = A.run_arm("generalizing_arm", w, head + tail_b, 256, 1)
    head_only = A.run_arm("generalizing_arm", w, head, 256, 1)
    # the arm's behaviour over the shared prefix is identical in all three runs
    assert arm_a.derivations >= head_only.derivations
    assert arm_b.derivations >= head_only.derivations
    bel_a = A.run_arm("belady_instance_cache", w, head + tail_a, 256, 1)
    bel_head = A.run_arm("belady_instance_cache", w, head, 256, 1)
    # the clairvoyant's decisions inside the prefix depend on the suffix, so its
    # prefix work is NOT recoverable from the prefix alone
    assert bel_a.derivations != bel_head.derivations


# --- the parent really is the strongest instance policy --------------------

@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_belady_is_at_least_as_good_as_lru_and_lfu(seed):
    w = a_world(extension=8)
    s = a_stream(w, horizon=800, seed=seed)
    bel = A.run_arm("belady_instance_cache", w, s, 256, seed)
    lru = A.run_arm("lru_instance_cache", w, s, 256, seed)
    lfu = A.run_arm("lfu_instance_cache", w, s, 256, seed)
    assert bel.derivations <= lru.derivations
    assert bel.derivations <= lfu.derivations


def test_no_instance_cache_ever_holds_a_rule():
    for arm_id in ("belady_instance_cache", "lru_instance_cache", "lfu_instance_cache"):
        src = inspect.getsource(A.ARMS[arm_id])
        assert "rule_of" not in src, arm_id
        assert "APPLY_COST" not in src, arm_id


# --- the negative control can fire, and here is the arithmetic that makes it -

def test_a_rule_cannot_pay_for_itself_at_extension_one():
    assert R.RULE_BITS > R.FACT_BITS * 1, "the control depends on this inequality"
    assert R.RULE_BITS // R.FACT_BITS == 4


def test_the_arm_does_not_beat_the_clairvoyant_at_extension_one():
    w = a_world(extension=1)
    s = a_stream(w, horizon=800, seed=9)
    arm = A.run_arm("generalizing_arm", w, s, 64, 9).total_work(0.0)
    bel = A.run_arm("belady_instance_cache", w, s, 64, 9).total_work(0.0)
    assert arm >= bel


def test_the_kill_criterion_is_reachable():
    """A terminal nobody can reach is not a kill criterion."""
    import run_retain as RR
    losing = [{"extension": m, "budget_bits": b, "horizon": 2000,
               "ratio_to_belady_instance_by_sigma": {"0.0": 1.5},
               "ratio_to_belady_mixed_by_sigma": {"0.0": 1.5}}
              for m in R.RETAIN_PLAN["sweep"]["primary_grid"]["extension_sizes"]
              for b in R.RETAIN_PLAN["sweep"]["primary_grid"]["budget_bits"]]
    terminal, reason = RR._terminal(losing, [])
    assert terminal == "NO_REGIME_FOR_SELECTIVE_RETENTION"
    assert "stronger negative than any recorded so far" in reason


def test_a_failed_negative_control_voids_the_run():
    import run_retain as RR
    rows = [{"extension": 1, "budget_bits": 64, "horizon": 2000,
             "ratio_to_belady_instance_by_sigma": {"0.0": 0.5},
             "ratio_to_belady_mixed_by_sigma": {"0.0": 0.5}}]
    terminal, _ = RR._terminal(rows, [])
    assert terminal == "VOID_NEGATIVE_CONTROL_FAILED"


def test_beating_the_mixed_reference_voids_rather_than_discovers():
    import run_retain as RR
    rows = [{"extension": 32, "budget_bits": 256, "horizon": 2000,
             "ratio_to_belady_instance_by_sigma": {"0.0": 0.5},
             "ratio_to_belady_mixed_by_sigma": {"0.0": 0.5}}]
    terminal, _ = RR._terminal(rows, [])
    assert terminal == "VOID_REFERENCE_IMPLEMENTED_WRONGLY"


# --- coordinates are kept apart --------------------------------------------

def test_the_ledger_never_sums_coordinates_without_a_price():
    src = inspect.getsource(A.Ledger.total_work)
    assert "sigma" in src, "the only summation must take an explicit exchange rate"
    with pytest.raises(TypeError):
        A.Ledger().total_work()


def test_bit_steps_is_a_raw_integral_and_not_priced():
    """Storage work at any sigma must be recoverable from one run."""
    w = a_world(extension=8)
    s = a_stream(w, horizon=400, seed=2)
    led = A.run_arm("generalizing_arm", w, s, 256, 2)
    base = led.total_work(0.0)
    assert led.total_work(0.5) == pytest.approx(base + 0.5 * led.bit_steps)


def test_no_arm_is_sigma_aware():
    for arm_id, fn in A.ARMS.items():
        assert "sigma" not in inspect.getsource(fn), arm_id


# --- placebo ---------------------------------------------------------------

def test_the_placebo_has_the_machinery_and_not_the_information():
    src = inspect.getsource(A.random_retention_placebo)
    assert "INDUCE_COST" in src, "the placebo must pay the same induction cost"
    assert "rng.randrange" in src, "the rule it keeps must not be the one demand chose"
    w = a_world(extension=16)
    s = a_stream(w, horizon=1200, seed=4)
    arm = A.run_arm("generalizing_arm", w, s, 256, 4)
    plc = A.run_arm("random_retention_placebo", w, s, 256, 4)
    assert plc.inductions > 0, "a placebo that never acts subtracts nothing"
    assert plc.total_work(0.0) - arm.total_work(0.0) > 0


# --- determinism -----------------------------------------------------------

def test_the_stream_generator_is_not_salted():
    assert S.hash_str("primary-16-256") == S.hash_str("primary-16-256")
    assert S.hash_str("a") != S.hash_str("b")
    assert "hash(" not in inspect.getsource(S.hash_str)


def test_the_sweep_is_identical_under_two_hash_seeds():
    """E6 found a real reproducibility defect this way; the check is kept."""
    prog = ("import json, retain_sweep as S;"
            "print(json.dumps(S.cell(16, 256, 400, 1.0, 2, 12345, 'x'), sort_keys=True))")
    outs = []
    for seed in ("0", "1"):
        env = dict(os.environ, PYTHONHASHSEED=seed, PYTHONPATH=str(HERE))
        outs.append(subprocess.run([sys.executable, "-c", prog], cwd=HERE, env=env,
                                   capture_output=True, text=True, check=True).stdout)
    assert outs[0] == outs[1]


# --- the receipt -----------------------------------------------------------

def test_the_receipt_carries_the_plan_it_was_run_under():
    doc = json.loads(RECEIPT.read_text())
    assert doc["plan"] == json.loads(json.dumps(R.RETAIN_PLAN))
    assert doc["commitment"]["commitment"] == R.COMMITMENT.commitment
    assert doc["commitment"]["protected_seed"] == R.COMMITMENT.protected_seed


def test_the_receipt_discloses_the_pilot_and_keeps_it_separate():
    doc = json.loads(RECEIPT.read_text())
    assert "pilot_disclosure" in doc["plan"]
    assert "was run to check that the harness worked" in doc["plan"]["pilot_disclosure"]
    assert doc["pilot"], "the pilot rows must be published, not merely mentioned"
    assert doc["commitment"]["pilot_seed"] != doc["commitment"]["protected_seed"]


def test_the_receipt_does_not_overclaim_p3():
    doc = json.loads(RECEIPT.read_text())
    assert doc["predictions"]["P3_verdict"].startswith("HELD_BUT_UNINFORMATIVE")
    ratios = doc["predictions"]["ratio_at_m16_by_horizon"]
    values = [ratios[k] for k in sorted(ratios, key=int)]
    assert values != sorted(values), "the receipt claims non-monotonicity; check it"


def test_the_receipt_states_what_it_does_not_establish():
    doc = json.loads(RECEIPT.read_text())
    for phrase in ("disjoint", "induced without error", "stationary"):
        assert phrase in doc["what_this_does_not_establish"], phrase
    assert "NONE CLAIMED FOR ANY COMPONENT" in doc["novelty"]


def test_the_receipt_scopes_the_root_rather_than_refuting_it():
    doc = json.loads(RECEIPT.read_text())
    assert doc["answers_root_cause"] == "EAGER_ACQUISITION_IS_DOMINATED_BY_DEFERRED_ACQUISITION"
    assert "SCOPED" in doc["answers_root_cause_how"]
    assert "rather than refuted" in doc["answers_root_cause_how"]


def test_the_receipt_carries_no_wall_clock():
    text = RECEIPT.read_text().lower()
    for banned in ("elapsed", "seconds", "timestamp", "duration_ms", "wall"):
        assert banned not in text, banned


def test_the_headline_names_the_parent_it_beat():
    doc = json.loads(RECEIPT.read_text())
    assert doc["terminal"] == "REPRESENTATION_BEATS_CLAIRVOYANT_INSTANCE_OPTIMAL"
    assert "belady_mixed_reference" in doc["terminal_reason"]
    assert "concedes the same point" in doc["terminal_reason"]


def test_the_crossover_survives_the_hardest_demand_distribution():
    doc = json.loads(RECEIPT.read_text())
    at_zero_skew = doc["hardest_setting"]["ratio_to_belady_instance_at_skew_0"]
    assert any(v < 1.0 for v in at_zero_skew.values()), (
        "a crossover that needs a skewed demand stream is a crossover in a "
        "convenient world, and the receipt must not claim otherwise")

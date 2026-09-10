#!/usr/bin/env python3
"""12-test selftest for calibration_reference.py (STEERING_MEMO 2026-09-10 section 4).

Reimplemented from STEERING_MEMO 2026-09-10 section 4 spec; the memo's
calibration_reference.py file was not delivered. Assay validation only: this
validates the DEV-CAL-2 readout pipeline before binding to OCM; NOT an OCM
result, confers no claim; never imported by src/ocm.

TEST -> MEMO LINE MAP
  1  test_canonicalization_representative_independent_state
       "learn THREE independent prior functions ... their verified coefficient
        vectors must SPAN S" — canonical form (unique RREF + digest) must be
        invariant to which representatives of the span were learned.
  2  test_new_evidence_dependence
       Development is learned FROM observations: different evidence (a
        different world / a flipped observation stage) must change the learned
        state and its predictions.
  3  test_counterfactual_history_invariance
       Two different histories spanning the SAME S give identical downstream
        acquisition (same cost, same success): the readout measures structure,
        not history tokens.
  4  test_actual_observation_counts_learned_3_parent_3_reset_8
       "the learner chooses r=3 ... RESET uses 8" — assert from oracle
        counters the learner REALLY used 3 not 8, the equally adaptive
        ordinary parent also used exactly 3 (memo: "each use 3"), and RESET
        used 8. (The 3+8 paid fallback belongs to the wrong-structure case.)
  5  test_parent_parity_same_outcome_same_observation_count
       "an equally adaptive ordinary parent each use 3 fresh observations" —
        the classical parent derives the SAME structural prior from the SAME
        history and achieves PARITY in outcome AND observation count (3==3);
        parity is reported, never as learner failure.
  6  test_insufficient_history_distinct_from_any_no_headroom_verdict
       "rank-deficient history -> INSUFFICIENT_HISTORY state, distinct from
        any no-headroom verdict".
  7  test_malformed_observations_rejected_never_leakage_proof
       "Malformed observations ... are NOT treated as proof of leakage".
  8  test_persistence_serialization_roundtrip
       "persistence serialization" — serialize/deserialize learned state and
        reproduce identical acquisition behavior.
  9  test_wrong_structure_refusal_then_paid_ambient_recovery
       "a wrong prior fails and then recovers through the PAID ambient
        fallback (3+8 observations)".
 10  test_all_targets_verified_on_all_256_inputs
       "verified on ALL 256 inputs" — exhaustive match for every arm's final
        hypothesis on every checked target.
 11  test_identification_lower_bounds_r_and_d
       "Worst-case identification lower bounds r and d respectively for the
        full noiseless classes".
 12  test_positive_and_negative_controls_adjudicate
       "validate constructive positive and negative controls": learned 3 vs
        reset 8; no-op cannot earn 3-observation success; INSUFFICIENT_HISTORY
        is never a global no-headroom verdict; both authorized=false flags.
"""

import json
import random
import sys

import calibration_reference as cr


def _dev_state(seed):
    world = cr.build_world(seed)
    obs = cr.developmental_observations(world, random.Random(seed))
    state, name = cr.developmental_learn(obs)
    assert state is not None and name == cr.STATE_SOLVED, name
    return world, obs, state


# 1
def test_canonicalization_representative_independent_state():
    world, _, state = _dev_state(cr.DEFAULT_SEED)
    rng = random.Random(cr.DEFAULT_SEED + 1)
    # Same span, different representatives: random invertible row mixtures.
    mixed = []
    for _ in range(8):
        rows = [cr.combine([rng.randint(0, 1) for _ in range(state.rank)],
                           state.canonical_basis)
                for _ in range(state.rank)]
        if cr.rank_of(rows, cr.D) == state.rank:
            mixed.append(rows)
    for rows in mixed:
        other = cr.LearnedState(rows)
        assert other.canonical_basis == state.canonical_basis
        assert other.digest == state.digest
    # Different span -> different canonical digest.
    other_world, _, other_state = _dev_state(cr.DEFAULT_SEED + 99)
    assert other_state.digest != state.digest
    assert other_state.canonical_basis != state.canonical_basis
    # Permuted history order still canonicalizes identically.
    world2 = cr.build_world(cr.DEFAULT_SEED)
    obs_shuffled = list(world2 and cr.developmental_observations(
        world2, random.Random(cr.DEFAULT_SEED)))
    obs_shuffled.reverse()
    st2, _ = cr.developmental_learn(obs_shuffled)
    assert st2.digest == state.digest


# 2
def test_new_evidence_dependence():
    world_a, _, state_a = _dev_state(cr.DEFAULT_SEED)
    world_b, _, state_b = _dev_state(cr.DEFAULT_SEED + 99)
    # Different evidence -> different learned state ...
    assert state_a.digest != state_b.digest
    # ... and different predictions on a fixed probe input.
    probe = [1, 0, 1, 0, 1, 0, 1, 0]
    differ = any(
        cr.dot(ba, probe) != cr.dot(bb, probe)
        for ba, bb in zip(state_a.canonical_basis, state_b.canonical_basis)
    )
    assert differ or state_a.canonical_basis != state_b.canonical_basis
    # Within one world, replacing one prior's evidence with a different
    # function's evidence changes the learned state (or its rank).
    rng = random.Random(cr.DEFAULT_SEED + 5)
    obs = cr.developmental_observations(world_a, rng)
    swapped = list(obs)
    for i, (k, x, y) in enumerate(swapped):
        if k == 2:
            swapped[i] = (k, x, y ^ 1)  # relabeled evidence = new function
    st_swapped, name = cr.developmental_learn(swapped)
    if st_swapped is not None:
        assert st_swapped.digest != state_a.digest
    else:
        assert name == cr.STATE_INSUFFICIENT_HISTORY


# 3
def test_counterfactual_history_invariance():
    world, _, state = _dev_state(cr.DEFAULT_SEED)
    # A second, different history spanning the SAME subspace: fresh random
    # prior functions inside S (different from the world's priors).
    rng = random.Random(cr.DEFAULT_SEED + 21)
    S = world["subspace_basis"]
    alt_priors = []
    while len(alt_priors) < cr.N_PRIORS:
        v = cr.combine([rng.randint(0, 1) for _ in range(cr.R)], S)
        if all(v != p for p in alt_priors) and \
                cr.rank_of(alt_priors + [v], cr.D) == len(alt_priors) + 1:
            alt_priors.append(v)
    alt_obs = []
    for k in range(cr.N_PRIORS):
        rows = []
        while len(rows) < cr.OBS_PER_PRIOR:
            x = [rng.randint(0, 1) for _ in range(cr.D)]
            if cr.rank_of(rows + [x], cr.D) == len(rows) + 1:
                rows.append(x)
        alt_obs.extend((k, x, cr.dot(alt_priors[k], x)) for x in rows)
    alt_state, name = cr.developmental_learn(alt_obs)
    assert alt_state is not None and name == cr.STATE_SOLVED
    # Identical canonical span -> identical acquisition behavior and cost.
    assert alt_state.digest == state.digest
    o1 = cr.ParityOracle(world["targets"])
    o2 = cr.ParityOracle(world["targets"])
    r1 = cr.acquire_learned_basis(o1, 0, state, random.Random(7))
    r2 = cr.acquire_learned_basis(o2, 0, alt_state, random.Random(7))
    assert r1["state"] == r2["state"] == cr.STATE_SOLVED
    assert r1["observations"] == r2["observations"] == cr.R
    assert r1["coefficient"] == r2["coefficient"]


# 4
def test_actual_observation_counts_learned_3_parent_3_reset_8():
    report = cr.run_calibration(cr.DEFAULT_SEED)
    arms = report["arms"]
    assert arms["LEARNED_BASIS"]["oracle_actual_counts"] == [cr.R] * cr.N_CHECKED_TARGETS
    assert arms["ORDINARY_ADAPTIVE_PARENT"]["oracle_actual_counts"] == \
        [cr.R] * cr.N_CHECKED_TARGETS
    assert arms["RESET"]["oracle_actual_counts"] == [cr.D] * cr.N_CHECKED_TARGETS
    # The learner REALLY used 3 not 8: counts come from the oracle, and a
    # second, counter-instrumented run must reproduce them exactly.
    report2 = cr.run_calibration(cr.DEFAULT_SEED)
    assert report2["arms"]["LEARNED_BASIS"]["oracle_actual_counts"] == \
        [cr.R] * cr.N_CHECKED_TARGETS
    assert report2["arms"]["ORDINARY_ADAPTIVE_PARENT"]["oracle_actual_counts"] == \
        [cr.R] * cr.N_CHECKED_TARGETS
    # A 3-observation solve is arithmetically impossible in the ambient basis
    # (that is RESET's 8 and the wrong-structure arm's paid fallback, not the
    # parent's route: the parent derives the structural prior itself).
    xs = [[1, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 0, 0]]
    _, rank = cr.solve_gf2(xs, [0, 0, 0], cr.D)
    assert rank < cr.D


# 5
def test_parent_parity_same_outcome_same_observation_count():
    world, history, state = _dev_state(cr.DEFAULT_SEED)
    # The classical parent runs the same structural-learning algorithm on the
    # same history, outside OCM bookkeeping, and derives the same span.
    parent_rows, pstate = cr.learn_prior_rows(history)
    assert pstate == cr.STATE_SOLVED
    assert not isinstance(parent_rows, cr.LearnedState)
    assert cr.canonical_basis(parent_rows)[3] == state.digest
    # Outcome AND observation-count parity per target, from oracle counters.
    for t in range(cr.N_CHECKED_TARGETS):
        o_l = cr.ParityOracle(world["targets"])
        o_p = cr.ParityOracle(world["targets"])
        r_l = cr.acquire_learned_basis(o_l, t, state, random.Random(100 + t))
        r_p = cr.acquire_ordinary_adaptive_parent(
            o_p, t, random.Random(100 + t), history)
        assert r_l["state"] == r_p["state"] == cr.STATE_SOLVED
        assert o_p.observation_counts[t] == o_l.observation_counts[t] == cr.R
        assert r_p["verified_all_256"] is True
        assert r_p["count_parity_with_learner"] is True
        assert r_p["coefficient"] == world["targets"][t]
    report = cr.run_calibration(cr.DEFAULT_SEED)
    lb = report["arms"]["LEARNED_BASIS"]
    pa = report["arms"]["ORDINARY_ADAPTIVE_PARENT"]
    assert pa["all_solved"] and lb["all_solved"]
    assert pa["oracle_actual_counts"] == lb["oracle_actual_counts"]
    assert all(pa["count_parity_with_learner"])
    assert report["controls"]["parent_parity_classical_parent_3_equals_learner_3"] == "PASS"
    # Parity is reported, never as learner failure:
    assert "parent" not in json.dumps(report["no_op_control"])


# 6
def test_insufficient_history_distinct_from_any_no_headroom_verdict():
    world = cr.build_world(cr.DEFAULT_SEED)
    history = cr._rank_deficient_history(world, cr.DEFAULT_SEED + 11)
    state, name = cr.developmental_learn(history)
    assert state is None
    assert name == cr.STATE_INSUFFICIENT_HISTORY
    assert name not in cr.HEADROOM_VERDICT_NAMES
    assert "HEADROOM" not in name
    report = cr.run_calibration(cr.DEFAULT_SEED)
    ib = report["insufficient_history"]
    assert ib["state"] == cr.STATE_INSUFFICIENT_HISTORY
    assert ib["is_headroom_verdict"] is False
    assert ib["distinct_from_no_headroom"] is True


# 7
def test_malformed_observations_rejected_never_leakage_proof():
    o = cr.ParityOracle([[1] * cr.D])
    for bad_x in ([1, 0], [2] * cr.D, "01010101", [0.5] + [1] * 7):
        try:
            o.observe(0, bad_x)
            raise AssertionError("malformed input accepted: %r" % (bad_x,))
        except cr.MalformedObservation:
            pass
    try:
        o.observe(99, [1] + [0] * (cr.D - 1))
        raise AssertionError("unknown task accepted")
    except cr.MalformedObservation:
        pass
    world = cr.build_world(cr.DEFAULT_SEED)
    good = cr.developmental_observations(world, random.Random(cr.DEFAULT_SEED))
    for corrupt in [
        good[:-1],                                   # wrong count
        good[:-1] + [(0, [0, 1], 1)],                # wrong-length vector
        good[:-1] + [(0, [1] * cr.D, 7)],            # non-binary value
        good[:-1] + [(9, [1] * cr.D, 1)],            # unknown prior index
    ]:
        try:
            cr.developmental_learn(corrupt)
            raise AssertionError("malformed history accepted")
        except cr.MalformedObservation:
            pass
    report = cr.run_calibration(cr.DEFAULT_SEED)
    m = report["malformed_observation"]
    assert m["state"] == cr.STATE_MALFORMED_REJECTED
    assert m["treated_as_leakage"] is False


# 8
def test_persistence_serialization_roundtrip():
    world, obs, state = _dev_state(cr.DEFAULT_SEED)
    text = state.to_json()
    restored = cr.LearnedState.from_json(text)
    assert isinstance(text, str) and json.loads(text)["schema"] == \
        "OCM_CALIBRATION_LEARNED_STATE_V1"
    assert restored.to_json() == text
    assert restored.digest == state.digest
    assert restored.canonical_basis == state.canonical_basis
    # Identical acquisition behavior after the round-trip.
    o1 = cr.ParityOracle(world["targets"])
    o2 = cr.ParityOracle(world["targets"])
    r1 = cr.acquire_learned_basis(o1, 3, state, random.Random(3))
    r2 = cr.acquire_learned_basis(o2, 3, restored, random.Random(3))
    assert r1 == r2 and r1["state"] == cr.STATE_SOLVED
    # Tampered persistence payload is rejected.
    bad = json.loads(text)
    bad["canonical_basis"][0][0] ^= 1
    try:
        cr.LearnedState.from_json(json.dumps(bad))
        raise AssertionError("tampered state accepted")
    except ValueError:
        pass


# 9
def test_wrong_structure_refusal_then_paid_ambient_recovery():
    report = cr.run_calibration(cr.DEFAULT_SEED)
    w = report["wrong_structure_arm"]
    assert w is not None
    assert w["refused"] is True
    assert w["refusal_state"] == cr.STATE_WRONG_STRUCTURE_REFUSED
    assert w["attempt_observations"] == cr.R
    assert w["fallback_observations"] == cr.D
    assert w["total_observations"] == cr.R + cr.D
    assert w["verified_all_256"] is True
    assert w["treated_as_leakage"] is False


# 10
def test_all_targets_verified_on_all_256_inputs():
    world = cr.build_world(cr.DEFAULT_SEED)
    _, _, state = _dev_state(cr.DEFAULT_SEED)
    for t in range(cr.N_CHECKED_TARGETS):
        o = cr.ParityOracle(world["targets"])
        learned = cr.acquire_learned_basis(o, t, state,
                                           random.Random(100 + t))
        assert learned["state"] == cr.STATE_SOLVED
        assert o.exhaustive_matches(t, learned["coefficient"]) == cr.N_INPUTS
        assert learned["coefficient"] == world["targets"][t]
        history = cr.developmental_observations(
            world, random.Random(cr.DEFAULT_SEED))
        parent = cr.acquire_ordinary_adaptive_parent(
            o, t, random.Random(200 + t), history)
        assert parent["state"] == cr.STATE_SOLVED
        assert o.exhaustive_matches(t, parent["coefficient"]) == cr.N_INPUTS
        reset = cr.acquire_ambient(o, t, random.Random(300 + t))
        assert reset["state"] == cr.STATE_SOLVED
        assert o.exhaustive_matches(t, reset["coefficient"]) == cr.N_INPUTS
    # Developmental priors also verified on all 256 inputs.
    o_dev = cr.ParityOracle(world["priors"])
    for k in range(cr.N_PRIORS):
        assert o_dev.exhaustive_matches(
            k, cr._solve_prior(k, cr.developmental_observations(
                world, random.Random(cr.DEFAULT_SEED)))) == cr.N_INPUTS


# 11
def test_identification_lower_bounds_r_and_d():
    lb = cr.identification_lower_bounds()
    assert lb["learned_basis_worst_case_measurements"] == cr.R
    assert lb["ambient_worst_case_measurements"] == cr.D
    assert lb["holds"] is True
    world = cr.build_world(cr.DEFAULT_SEED)
    S = world["subspace_basis"]
    span = [cr.combine(c, S)
            for c in _all_tuples(cr.R)]
    ambient = [cr.combine(c, _ambient_basis())
               for c in _all_tuples(cr.D)]
    rng = random.Random(0)
    # With S known, 2 adaptive measurements leave >= 2 consistent hypotheses
    # for the worst-case target (so 3 is a genuine lower bound).
    xs = []
    while len(xs) < cr.R - 1:
        x = [rng.randint(0, 1) for _ in range(cr.D)]
        if x not in xs and cr.rank_of(xs + [x], cr.D) == len(xs) + 1:
            xs.append(x)
    worst = max(
        (sum(1 for a in span
             if all(cr.dot(a, x) == cr.dot(true, x) for x in xs))
         for true in span))
    assert worst >= 2
    # Without S, 7 measurements leave >= 2 consistent hypotheses in GF(2)^8.
    xs7 = []
    while len(xs7) < cr.D - 1:
        x = [rng.randint(0, 1) for _ in range(cr.D)]
        if x not in xs7 and cr.rank_of(xs7 + [x], cr.D) == len(xs7) + 1:
            xs7.append(x)
    worst7 = max(
        (sum(1 for a in ambient
             if all(cr.dot(a, x) == cr.dot(true, x) for x in xs7))
         for true in ambient))
    assert worst7 >= 2


# 12
def test_positive_and_negative_controls_adjudicate():
    report = cr.run_calibration(cr.DEFAULT_SEED)
    c = report["controls"]
    assert c["positive_control_learned_3_vs_reset_8"] == "PASS"
    assert c["parent_parity_classical_parent_3_equals_learner_3"] == "PASS"
    assert c["negative_control_no_op_cannot_earn_3_observation_success"] == "PASS"
    assert c["negative_control_insufficient_history_is_not_no_headroom"] == "PASS"
    assert c["all_controls_passed"] is True
    assert report["no_op_control"]["any_earned"] is False
    assert all(not e for e in report["no_op_control"]["earned_3_observation_success"])
    assert report["economic_claim_authorized"] is False
    assert report["ocm_specific_claim_authorized"] is False
    assert "not delivered" in report["provenance"]
    assert report["development"]["state"] == cr.STATE_SOLVED
    assert report["development"]["observations"] == cr.DEV_OBS_TOTAL == 24
    assert report["development"]["learned_rank"] == cr.R == 3
    assert len(report["arms"]["LEARNED_BASIS"]["oracle_actual_counts"]) == \
        cr.N_CHECKED_TARGETS == 5


def _all_tuples(n):
    if n == 0:
        yield ()
        return
    for tail in _all_tuples(n - 1):
        yield (0,) + tail
        yield (1,) + tail


def _ambient_basis():
    return [[1 if i == j else 0 for i in range(cr.D)] for j in range(cr.D)]


TESTS = [
    test_canonicalization_representative_independent_state,
    test_new_evidence_dependence,
    test_counterfactual_history_invariance,
    test_actual_observation_counts_learned_3_parent_3_reset_8,
    test_parent_parity_same_outcome_same_observation_count,
    test_insufficient_history_distinct_from_any_no_headroom_verdict,
    test_malformed_observations_rejected_never_leakage_proof,
    test_persistence_serialization_roundtrip,
    test_wrong_structure_refusal_then_paid_ambient_recovery,
    test_all_targets_verified_on_all_256_inputs,
    test_identification_lower_bounds_r_and_d,
    test_positive_and_negative_controls_adjudicate,
]


def main():
    results = []
    for t in TESTS:
        name = t.__name__
        try:
            t()
            results.append((name, "PASS", ""))
            print("PASS %s" % name)
        except Exception as exc:  # noqa: BLE001 - report and keep going
            results.append((name, "FAIL", "%s: %s" % (type(exc).__name__, exc)))
            print("FAIL %s :: %s: %s" % (name, type(exc).__name__, exc))
    passed = sum(1 for _, s, _ in results if s == "PASS")
    print("%d/%d tests passed" % (passed, len(results)))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())

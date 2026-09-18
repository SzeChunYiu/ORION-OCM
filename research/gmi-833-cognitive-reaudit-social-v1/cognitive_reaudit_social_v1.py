#!/usr/bin/env python3
"""Route A: analytic executor for the #833 Section-M social/metacognitive re-audit.

Rows audited (and only these):

  MC-1  metacognition and value of computation
  MC-2  social cognition / theory of mind
  MC-3  communication
  MC-4  imitation and teaching
  MC-5  cultural accumulation

Every claim is decided twice: once here by the analytic route (closed forms,
backward induction, the refinement-value decomposition, the exact classification
of the transmission recursion) and once by `route_b_oracle_v1`, which enumerates
policies and iterates recursions and knows none of these results.

Exact arithmetic only: `int` and `fractions.Fraction`. No float is constructed.

Reproduce:
    python3 -I -B  research/gmi-833-cognitive-reaudit-social-v1/cognitive_reaudit_social_v1.py
    python3 -I -O -B research/gmi-833-cognitive-reaudit-social-v1/cognitive_reaudit_social_v1.py
Both modes must write a byte-identical `RESULT_V1.json`.
"""

from __future__ import annotations

from fractions import Fraction as F
from hashlib import sha1
import json
import os
from pathlib import Path
import sys
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import registered_scopes_v1 as scopes          # noqa: E402  (pure data)
import route_b_oracle_v1 as route_b            # noqa: E402  (independent oracle)


CLAIM_CEILING = (
    "GMI_833_METACOGNITION_SOCIAL_COMMUNICATION_TEACHING_CULTURE_"
    "REAUDIT_AT_REGISTERED_EXACT_SCOPE"
)
FROZEN_SOURCE_MAIN = "332af6682a8f79e155eed9f22aa4df6295d2a18b"

FORBIDDEN_PROMOTIONS = (
    "METACOGNITIVE_MACHINERY_IDENTIFIED_FROM_TRACE",
    "ALLOCATION_TRACE_IDENTIFIES_ARCHITECTURE",
    "GENERAL_OPTIMAL_STOPPING_SOLVED",
    "PLAN_SEARCH_STOPPING_CLAIMED",
    "THEORY_OF_MIND_IS_MACHINE_PROPERTY",
    "SCORE_GAP_IDENTIFIES_MENTALIZING",
    "COORDINATION_IDENTIFIES_COMMUNICATION",
    "UNIVERSAL_COMMUNICATION_ARCHITECTURE",
    "CONCURRENT_COST_FALL_IDENTIFIES_IMITATION",
    "FREE_DEMONSTRATOR_LABOUR",
    "TRAJECTORY_IDENTIFIES_CULTURAL_TRANSMISSION",
    "WITHIN_LIFETIME_LIBRARY_GROWTH_CLAIMED",
    "EMPIRICAL_COGNITIVE_VALIDATION",
    "HUMAN_OR_ANIMAL_COGNITION_CLAIMED",
    "COMPLETE_GMI",
)

ABSTENTIONS = {
    "MC-1": "CANNOT_IDENTIFY_FROM_ALLOCATION_TRACE",
    "MC-2": "CANNOT_IDENTIFY_FROM_SCORE_ALONE",
    "MC-3": "CANNOT_IDENTIFY_FROM_COORDINATION_ALONE",
    "MC-4": "CANNOT_IDENTIFY_WITHOUT_CONTROL_ARM",
    "MC-5": "CANNOT_IDENTIFY_FROM_CAPABILITY_TRAJECTORY",
}

PARENT_PINS = (
    ("foundation",
     "research/gmi-833-foundation-v1/RESULT_V1.json",
     "c0c574c4ec6e237d5fdafa694eac131399625a70",
     "terminal",
     "GMI_833_FOUNDATION_V1_FORMALIZED_AT_DECLARED_SCOPE"),
    ("axiom_core",
     "research/gmi-833-axiom-core-v1/RESULT_V1.json",
     "3366a3bc7236d286f8d123bf53e4e3b2d22ad7b9",
     "claim_ceiling",
     "GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE"),
    ("cognitive_reaudit_v1",
     "research/gmi-833-cognitive-reaudit-v1/RESULT_V1.json",
     "0da555464ea698517e337abedc87984bef2a7605",
     "claim_ceiling",
     "GMI_833_COGNITIVE_REAUDIT_FUNCTIONAL_DIFFERENTIATION_RESOURCE_RATIONAL_"
     "SELECTION_AND_STATIC_QUOTIENT_WITH_ABSTENTION"),
    ("morphcap",
     "research/gmi-833-morphcap-v1/RESULT_V1.json",
     "bdc5c3cd42e312d8c7af52f7ba84220631a25f8a",
     "claim_ceiling",
     "GMI_MORPHOLOGY_AND_CAPABILITY_OBJECTS_AT_REGISTERED_FINITE_SCOPE"),
    ("global_uncertainty",
     "research/gmi-833-global-uncertainty-v1/RESULT_V1.json",
     "9ab16cf59087214e093ace3b18c6d08fc79ab871",
     "claim_ceiling",
     "GMI_GLOBAL_UNCERTAINTY_AND_ABSTENTION_CONTRACT_AT_REGISTERED_FINITE_SCOPE"),
    ("theory_baseline",
     "research/gmi-833-theory-baseline-v1/BASELINE_V1.md",
     "201ee8e8b290f5bfa3e283e6f8be2429ce8eeb78",
     None,
     None),
)


class RedResult(Exception):
    """Raised when a frozen falsifier fires. Never caught inside the executor."""


def require(condition: bool, message: str) -> None:
    """`assert` is stripped by -O; this is not."""
    if not condition:
        raise RedResult(message)


def frac(value: F) -> str:
    if isinstance(value, float):
        raise RedResult("float reached serialization")
    value = F(value)
    return "%d/%d" % (value.numerator, value.denominator)


# --------------------------------------------------------------------------
# parent custody
# --------------------------------------------------------------------------

def repo_root() -> Path:
    current = HERE
    while current.parent != current:
        if (current / ".git").exists() or (current / "research").is_dir():
            return current
        current = current.parent
    return HERE.parents[1]


def git_blob_sha(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def audit_parents() -> Dict[str, object]:
    root = repo_root()
    rows = []  # type: List[Dict[str, object]]
    for name, path, expected_blob, field, expected_claim in PARENT_PINS:
        target = root / path
        if not target.is_file():
            rows.append({"name": name, "path": path, "blob_ok": False,
                         "claim_ok": False, "actual_blob": None})
            continue
        data = target.read_bytes()
        actual = git_blob_sha(data)
        claim_ok = True
        if field is not None:
            try:
                payload = json.loads(data.decode("utf-8"))
                claim_ok = payload.get(field) == expected_claim
            except (ValueError, UnicodeDecodeError):
                claim_ok = False
        rows.append({"name": name, "path": path, "blob_ok": actual == expected_blob,
                     "claim_ok": claim_ok, "actual_blob": actual})
    drift = [r["name"] for r in rows if not (r["blob_ok"] and r["claim_ok"])]
    return {"rows": rows, "drift": drift, "all_pinned": not drift}


# ==========================================================================
# MC-1  metacognition and value of computation
# ==========================================================================
#
# REGISTERED EXTERNAL DEFINITION.  A system allocates metacognitively when the
# number and placement of its charged deliberation steps is produced by
# evaluating a registered internal estimate of expected gain.  The only
# admissible evidence is the external allocation trace: which charged steps were
# taken, at which reached nodes.  Nothing here inspects an internal state.
#
# DEMARCATION.  Object-level plan-search stopping is owned by #926 / PR #927.
# VOC-2 below is an instrumental backward-induction lemma over the registered
# finite deliberation scope; the myopic-versus-optimal comparison is theirs and
# is neither computed nor reported here.


def route_a_retained_best(scope: Dict[str, object], path: Tuple[int, ...]) -> F:
    node_value = scope["node_value"]
    best = F(0)
    for cut in range(len(path) + 1):
        candidate = node_value[path[:cut]]
        if candidate > best:
            best = candidate
    return best


def route_a_voc(scope: Dict[str, object], path: Tuple[int, ...]) -> Tuple[F, bool]:
    """VOC-1: exact expected improvement of one further charged step, and whether
    it strictly exceeds that step's exact price."""
    node_value = scope["node_value"]
    prob = scope["prob"]
    price = scope["price"]
    branch = scope["branch"]
    best = route_a_retained_best(scope, path)
    expected = F(0)
    for outcome in range(branch):
        child = node_value[path + (outcome,)]
        expected += prob[outcome] * (child if child > best else best)
    improvement = expected - best
    return improvement, improvement > price[path]


def route_a_optimal_allocation(
    scope: Dict[str, object],
) -> Tuple[F, Dict[Tuple[int, ...], bool]]:
    """VOC-2 (instrumental): backward induction over the registered finite
    deliberation scope. Registered tie rule: stop on ties."""
    node_value = scope["node_value"]
    price = scope["price"]
    prob = scope["prob"]
    depth = scope["depth"]
    branch = scope["branch"]
    policy = {}  # type: Dict[Tuple[int, ...], bool]

    def solve(path: Tuple[int, ...], best: F) -> F:
        best2 = best if best >= node_value[path] else node_value[path]
        if len(path) == depth:
            return best2
        continuation = -price[path]
        for outcome in range(branch):
            continuation += prob[outcome] * solve(path + (outcome,), best2)
        if continuation > best2:
            policy[path] = True
            return continuation
        policy[path] = False
        return best2

    return solve((), F(0)), policy


def route_a_trace(
    scope: Dict[str, object],
    policy: Dict[Tuple[int, ...], bool],
) -> Tuple[Tuple[Tuple[int, ...], bool], ...]:
    depth = scope["depth"]
    branch = scope["branch"]
    seen = []  # type: List[Tuple[Tuple[int, ...], bool]]

    def walk(path: Tuple[int, ...]) -> None:
        if len(path) == depth:
            return
        seen.append((path, policy[path]))
        if policy[path]:
            for outcome in range(branch):
                walk(path + (outcome,))

    walk(())
    return tuple(seen)


def route_a_fixed_schedule_twin(
    observed: Dict[str, List[Tuple[Tuple[Tuple[int, ...], bool], ...]]],
) -> Optional[Dict[str, Tuple[Tuple[Tuple[int, ...], bool], ...]]]:
    """NONID-1 (analytic direction): a fixed schedule reproducing the allocation
    trace-for-trace on every registered instance exists iff the allocation is a
    deterministic function of the registered observable instance label -- in
    which case the schedule IS that function."""
    schedule = {}  # type: Dict[str, Tuple[Tuple[Tuple[int, ...], bool], ...]]
    for label in sorted(observed):
        traces = observed[label]
        distinct = []
        for trace in traces:
            if trace not in distinct:
                distinct.append(trace)
        if len(distinct) != 1:
            return None
        schedule[label] = distinct[0]
    return schedule


def run_mc1() -> Dict[str, object]:
    voc_cases = 0
    voc_worth_true = 0
    voc_nonnegative = 0
    voc_equal_price = 0
    allocation_cases = 0
    value_mismatch = 0
    trace_mismatch = 0
    voc_mismatch = 0
    hostile_nonstrict_voc_detected = 0
    scope_count = 0

    for scope in scopes.iter_deliberation_scopes():
        scope_count += 1
        value_a, policy_a = route_a_optimal_allocation(scope)
        value_b, _policy_b = route_b.brute_force_best_allocation(scope)
        allocation_cases += 1
        if value_a != value_b:
            value_mismatch += 1
        trace_a = route_a_trace(scope, policy_a)
        trace_b = route_b.brute_force_reachable_trace(scope, policy_a)
        if trace_a != trace_b:
            trace_mismatch += 1

        for path in scopes.delib_decision_paths(scope["depth"], scope["branch"]):
            best = route_a_retained_best(scope, path)
            best_b = route_b.brute_force_retained_best(scope, path)
            if best != best_b:
                voc_mismatch += 1
            improvement, worth = route_a_voc(scope, path)
            worth_b, stop_value, step_value = route_b.brute_force_myopic_step_worth(
                scope, path, F(0) if not path else route_a_retained_best(scope, path[:len(path)])
            )
            voc_cases += 1
            if worth != worth_b:
                voc_mismatch += 1
            if step_value - stop_value != improvement - scope["price"][path]:
                voc_mismatch += 1
            if improvement >= 0:
                voc_nonnegative += 1
            if worth:
                voc_worth_true += 1
            if improvement == scope["price"][path]:
                voc_equal_price += 1
                # HOSTILE H1a: a non-strict `>=` threshold calls this worth its
                # charge although the exact net gain is zero. Detected exactly
                # here, by disagreeing with the brute-forced policy comparison.
                if (improvement >= scope["price"][path]) != worth_b:
                    hostile_nonstrict_voc_detected += 1

    # --- NONID-1: exhaustive fixed-schedule aliasing census -----------------
    instance_scopes = scopes.aliasing_instance_scopes()
    observed_det = {}
    for label in sorted(instance_scopes):
        _value, policy = route_a_optimal_allocation(instance_scopes[label])
        observed_det[label] = [route_a_trace(instance_scopes[label], policy)]
    schedule_a = route_a_fixed_schedule_twin(observed_det)
    require(schedule_a is not None,
            "NONID-1: deterministic optimal allocation must admit a fixed-schedule twin")
    matches_b = route_b.brute_force_all_matching_schedules(
        instance_scopes, dict((k, v[0]) for k, v in observed_det.items())
    )
    schedule_space = route_b.brute_force_schedule_space_size(instance_scopes)
    require(len(matches_b) == 1,
            "NONID-1 route B: exactly one fixed schedule must reproduce a deterministic trace")
    require(matches_b[0] == schedule_a,
            "NONID-1: the two routes must agree on the twin")

    # --- boundary, EARNED_BY_COUNTEREXAMPLE ---------------------------------
    # A metacognitive allocator whose internal estimate consults a registered
    # latent draw `z` that is NOT part of the observable instance label emits two
    # distinct traces on one label. No fixed schedule can then reproduce it
    # trace-for-trace: the twin construction has an exact boundary.
    latent_label = sorted(instance_scopes)[0]
    latent_scope = instance_scopes[latent_label]
    decisions = scopes.delib_decision_paths(latent_scope["depth"], latent_scope["branch"])
    trace_z0 = route_a_trace(latent_scope, dict((d, False) for d in decisions))
    trace_z1 = route_a_trace(latent_scope, dict((d, True) for d in decisions))
    require(trace_z0 != trace_z1, "latent-draw counterexample needs two distinct traces")
    observed_latent = dict((k, list(v)) for k, v in observed_det.items())
    observed_latent[latent_label] = [trace_z0, trace_z1]
    require(route_a_fixed_schedule_twin(observed_latent) is None,
            "NONID-1 boundary: a label-nondeterministic allocation must admit no twin")
    # HOSTILE H1b: claiming a fixed-schedule twin for the latent-draw allocator.
    # Route B enumerates the ENTIRE registered schedule space and finds none,
    # which is how the claim is detected as false rather than assumed false.
    latent_matches_b = route_b.brute_force_schedules_matching_trace_sets(
        instance_scopes, observed_latent
    )
    require(latent_matches_b == [],
            "NONID-1 boundary route B: no fixed schedule may reproduce a latent-draw trace set")
    # control: the same exhaustive enumeration DOES find the twin for the
    # deterministic allocator, so the search is not vacuously empty.
    control_matches_b = route_b.brute_force_schedules_matching_trace_sets(
        instance_scopes, observed_det
    )
    require(len(control_matches_b) == 1,
            "NONID-1 boundary control: the exhaustive schedule search must not be vacuous")

    require(value_mismatch == 0, "MC-1: two-route optimal-allocation mismatch")
    require(trace_mismatch == 0, "MC-1: two-route allocation-trace mismatch")
    require(voc_mismatch == 0, "MC-1: two-route VOC threshold mismatch")
    require(voc_nonnegative == voc_cases, "MC-1: VOC must be nonnegative everywhere")
    require(hostile_nonstrict_voc_detected == voc_equal_price and voc_equal_price > 0,
            "MC-1: the non-strict-threshold hostile must be detected on every tie case")

    return {
        "row": "Re-audit metacognition and value of computation.",
        "results": ["VOC-1", "VOC-2", "NONID-1"],
        "external_definition": (
            "metacognition is registered as allocation of charged computation "
            "driven by a registered internal estimate of expected gain, evidenced "
            "only by the external allocation trace"
        ),
        "census": {
            "deliberation_scopes": scope_count,
            "optimal_allocation_two_route_cases": allocation_cases,
            "voc_threshold_two_route_cases": voc_cases,
            "voc_worth_true": voc_worth_true,
            "voc_exact_tie_cases": voc_equal_price,
            "aliasing_instances": len(instance_scopes),
            "aliasing_schedule_space": schedule_space,
            "aliasing_matching_schedules": len(matches_b),
        },
        "two_route_mismatches": {
            "optimal_value": value_mismatch,
            "allocation_trace": trace_mismatch,
            "voc_threshold": voc_mismatch,
        },
        "hostiles_detected": {
            "H1a_non_strict_voc_threshold": hostile_nonstrict_voc_detected,
            "H1b_twin_claimed_for_latent_draw_allocator": 1,
        },
        "abstention": ABSTENTIONS["MC-1"],
        "boundary": "EARNED_BY_COUNTEREXAMPLE",
        "demarcation": (
            "object-level plan-search stopping and the myopic-versus-optimal EVC "
            "counterexample are owned by #926 / PR #927 and are not computed here"
        ),
    }


# ==========================================================================
# REF-1  the shared refinement-value kernel (MC-2 and MC-3)
# ==========================================================================

def route_a_refinement_value(
    prior: Sequence[F],
    score: Sequence[Sequence[F]],
    partition: Sequence[int],
    n_actions: int,
) -> F:
    """REF-1: the best exact score achievable by a policy measurable with respect
    to `partition`, computed blockwise in closed form rather than by enumeration."""
    n_blocks = max(partition) + 1
    total = F(0)
    for block in range(n_blocks):
        members = [s for s in range(len(prior)) if partition[s] == block]
        block_best = None  # type: Optional[F]
        for action in range(n_actions):
            value = F(0)
            for s in members:
                value += prior[s] * score[s][action]
            if block_best is None or value > block_best:
                block_best = value
        total += block_best
    return total


def route_a_finest_value(prior: Sequence[F], score: Sequence[Sequence[F]], n_actions: int) -> F:
    total = F(0)
    for s in range(len(prior)):
        best = None  # type: Optional[F]
        for action in range(n_actions):
            if best is None or score[s][action] > best:
                best = score[s][action]
        total += prior[s] * best
    return total


def route_a_blockwise_constant_optimum(
    prior: Sequence[F],
    score: Sequence[Sequence[F]],
    partition: Sequence[int],
    n_actions: int,
) -> bool:
    """Is a single action simultaneously optimal in every block of `partition`?"""
    n_blocks = max(partition) + 1
    for candidate in range(n_actions):
        good = True
        for block in range(n_blocks):
            members = [s for s in range(len(prior)) if partition[s] == block]
            block_best = None  # type: Optional[F]
            candidate_value = F(0)
            for action in range(n_actions):
                value = F(0)
                for s in members:
                    value += prior[s] * score[s][action]
                if action == candidate:
                    candidate_value = value
                if block_best is None or value > block_best:
                    block_best = value
            if candidate_value != block_best:
                good = False
                break
        if good:
            return True
    return False


def route_a_pointwise_sufficient(
    prior: Sequence[F],
    score: Sequence[Sequence[F]],
    partition: Sequence[int],
    n_actions: int,
) -> bool:
    """SOC-1 equality condition, stated only on the positive-probability support:
    every block admits a block-optimal action that is also pointwise optimal for
    every member of that block carrying positive probability."""
    n_blocks = max(partition) + 1
    for block in range(n_blocks):
        members = [s for s in range(len(prior)) if partition[s] == block]
        support = [s for s in members if prior[s] > 0]
        block_values = []
        for action in range(n_actions):
            value = F(0)
            for s in members:
                value += prior[s] * score[s][action]
            block_values.append(value)
        block_best = max(block_values)
        attainers = [a for a in range(n_actions) if block_values[a] == block_best]
        pointwise_max = {}
        for s in support:
            best = None  # type: Optional[F]
            for action in range(n_actions):
                if best is None or score[s][action] > best:
                    best = score[s][action]
            pointwise_max[s] = best
        found = False
        for action in attainers:
            if all(score[s][action] == pointwise_max[s] for s in support):
                found = True
                break
        if not found:
            return False
    return True


# ==========================================================================
# MC-2  social cognition / theory of mind
# ==========================================================================

def run_mc2() -> Dict[str, object]:
    total = 0
    channel_mismatch = 0
    hidden_mismatch = 0
    predicate_mismatch = 0
    strict_gap_cases = 0
    zero_gap_cases = 0
    negative_gap = 0
    behaviour_reader_matches = 0
    hostile_ignore_channel_detected = 0
    max_gap = F(0)
    max_gap_witness = None  # type: Optional[Dict[str, object]]

    for eco in scopes.iter_social_ecologies():
        total += 1
        prior = eco["prior"]
        require(scopes.is_probability_vector(prior),
                "MC-2: registered prior must be an exact probability vector")
        score = eco["score"]
        channel = eco["channel"]
        n_actions = eco["n_actions"]

        v_obs_a = route_a_refinement_value(prior, score, channel, n_actions)
        v_hid_a = route_a_finest_value(prior, score, n_actions)
        v_obs_b = route_b.brute_force_channel_value(eco)
        v_hid_b = route_b.brute_force_hidden_value(eco)
        if v_obs_a != v_obs_b:
            channel_mismatch += 1
        if v_hid_a != v_hid_b:
            hidden_mismatch += 1

        gap = v_hid_a - v_obs_a
        if gap < 0:
            negative_gap += 1
        equality_predicate = route_a_pointwise_sufficient(prior, score, channel, n_actions)
        if equality_predicate != (gap == 0):
            predicate_mismatch += 1
        if gap > 0:
            strict_gap_cases += 1
            if gap > max_gap:
                max_gap = gap
                max_gap_witness = {
                    "family": eco["family"],
                    "prior": [frac(p) for p in prior],
                    "channel": list(channel),
                    "score": [[frac(v) for v in row] for row in score],
                    "behaviour_reader_value": frac(v_obs_a),
                    "mentalizer_value": frac(v_hid_a),
                    "gap": frac(gap),
                }
        else:
            zero_gap_cases += 1
            behaviour_reader_matches += 1
        # HOSTILE H2a: a broken behaviour-reader that ignores the observed action
        # channel and secretly reads the hidden state. Its reported value is
        # recomputed here from the hostile's own (wrong) measurability, then
        # checked against route B's honest enumeration over channel-measurable
        # policies. The disagreement is the detection.
        hostile_obs_value = route_a_finest_value(prior, score, n_actions)
        if hostile_obs_value != v_obs_b:
            hostile_ignore_channel_detected += 1

    require(channel_mismatch == 0, "MC-2: two-route behaviour-reader value mismatch")
    require(hidden_mismatch == 0, "MC-2: two-route mentalizer value mismatch")
    require(negative_gap == 0, "MC-2: SOC-1 monotonicity violated")
    require(predicate_mismatch == 0, "MC-2: SOC-1 equality characterization failed")
    require(strict_gap_cases > 0 and zero_gap_cases > 0,
            "MC-2: both the separating and the matched-twin regime must be witnessed")
    require(hostile_ignore_channel_detected == strict_gap_cases,
            "MC-2: the channel-ignoring hostile must be detected on exactly the "
            "separating ecologies and nowhere else (no-alarm case asserted)")

    # the registered false-belief-shaped separation: the other agent's observed
    # action history is CONSTANT while its hidden state decides the payoff.
    fb_prior = (F(1, 2), F(1, 2))
    fb_score = ((F(2), F(0)), (F(0), F(2)))
    fb_channel = (0, 0)
    fb_obs = route_a_refinement_value(fb_prior, fb_score, fb_channel, 2)
    fb_hid = route_a_finest_value(fb_prior, fb_score, 2)
    fb_obs_b = route_b.brute_force_channel_value(
        {"prior": fb_prior, "score": fb_score, "channel": fb_channel, "n_actions": 2}
    )
    require(fb_obs == fb_obs_b, "MC-2: false-belief witness route disagreement")
    require(fb_hid - fb_obs == F(1), "MC-2: false-belief witness gap must be exactly 1")

    # the matched hostile twin: a sufficient channel, gap exactly 0.
    tw_channel = (0, 1)
    tw_obs = route_a_refinement_value(fb_prior, fb_score, tw_channel, 2)
    tw_hid = route_a_finest_value(fb_prior, fb_score, 2)
    require(tw_hid - tw_obs == F(0),
            "MC-2: the behaviour-reading hostile twin must match the mentalizer exactly")

    return {
        "row": "Re-audit social cognition/theory of mind.",
        "results": ["SOC-1", "REF-1"],
        "external_definition": (
            "the focal system's behaviour depends on the other agent's unobserved "
            "state rather than only on that agent's observed action history"
        ),
        "census": {
            "ecologies": total,
            "separating_ecologies": strict_gap_cases,
            "behaviour_reader_matches_mentalizer": behaviour_reader_matches,
            "largest_exact_gap": frac(max_gap),
        },
        "two_route_mismatches": {
            "behaviour_reader_value": channel_mismatch,
            "mentalizer_value": hidden_mismatch,
            "soc1_equality_predicate": predicate_mismatch,
        },
        "false_belief_witness": {
            "prior": [frac(p) for p in fb_prior],
            "behaviour_reader_value": frac(fb_obs),
            "mentalizer_value": frac(fb_hid),
            "gap": frac(fb_hid - fb_obs),
        },
        "hostile_twin": {
            "sufficient_channel_gap": frac(tw_hid - tw_obs),
            "matched_ecologies": behaviour_reader_matches,
        },
        "hostiles_detected": {
            "H2a_channel_ignoring_behaviour_reader": hostile_ignore_channel_detected,
            "H2b_tom_claimed_on_sufficient_channel": behaviour_reader_matches,
        },
        "largest_gap_witness": max_gap_witness,
        "abstention": ABSTENTIONS["MC-2"],
    }


# ==========================================================================
# MC-3  communication
# ==========================================================================

def run_mc3() -> Dict[str, object]:
    total = 0
    value_mismatch = 0
    silent_mismatch = 0
    pay_mismatch = 0
    com2_mismatch = 0
    strict_pay = 0
    free_but_useless = 0
    valuable_but_unaffordable = 0
    shared_observation_alias = 0
    hostile_nonstrict_pay_detected = 0
    exact_tie_price = 0
    negative_gain = 0

    cached_key = None  # type: Optional[Tuple[object, ...]]
    cached = None  # type: Optional[Dict[str, object]]

    for eco in scopes.iter_communication_ecologies():
        total += 1
        prior = eco["prior"]
        require(scopes.is_probability_vector(prior),
                "MC-3: registered prior must be an exact probability vector")
        key = (eco["family"], eco["score"], eco["partition"], prior)
        if key != cached_key:
            score = eco["score"]
            partition = eco["partition"]
            n_actions = eco["n_actions"]
            trivial = tuple(0 for _ in prior)
            v_pi_a = route_a_refinement_value(prior, score, partition, n_actions)
            v_0_a = route_a_refinement_value(prior, score, trivial, n_actions)
            v_fin_a = route_a_finest_value(prior, score, n_actions)
            v_pi_b = route_b.brute_force_channel_partition_value(eco)
            v_0_b = route_b.brute_force_silent_value(eco)
            v_fin_b = route_b.brute_force_shared_observation_value(eco)
            constant_a = route_a_blockwise_constant_optimum(prior, score, partition, n_actions)
            constant_b = route_b.brute_force_constant_action_is_blockwise_optimal(eco)
            cached_key = key
            cached = {
                "v_pi_a": v_pi_a, "v_0_a": v_0_a, "v_fin_a": v_fin_a,
                "v_pi_b": v_pi_b, "v_0_b": v_0_b, "v_fin_b": v_fin_b,
                "constant_a": constant_a, "constant_b": constant_b,
            }
            if v_pi_a != v_pi_b or v_fin_a != v_fin_b:
                value_mismatch += 1
            if v_0_a != v_0_b:
                silent_mismatch += 1
            gain = v_pi_a - v_0_a
            if gain < 0:
                negative_gain += 1
            # COM-2 proved, not assumed: `the receiver can act differentially` is
            # equivalent to a strictly positive refinement value. Route A decides
            # it by comparing values; route B decides it by enumerating actions.
            if (gain == 0) != constant_b:
                com2_mismatch += 1
            if constant_a != constant_b:
                com2_mismatch += 1
            if v_fin_a == v_pi_a:
                cached["aliased"] = True
            else:
                cached["aliased"] = False

        gain = cached["v_pi_a"] - cached["v_0_a"]
        price = eco["price"]
        pays_a = gain > price
        pays_b = route_b.brute_force_channel_strictly_pays(eco)
        if pays_a != pays_b:
            pay_mismatch += 1
        if pays_a:
            strict_pay += 1
        if price == 0 and gain == 0:
            free_but_useless += 1
        if gain > 0 and gain <= price:
            valuable_but_unaffordable += 1
        if gain == price:
            exact_tie_price += 1
            # HOSTILE H3a: a non-strict `>=` pay rule adopts a channel whose exact
            # net joint gain is zero.
            if (gain >= price) != pays_b:
                hostile_nonstrict_pay_detected += 1
        if cached["aliased"] and gain > 0:
            # HOSTILE H3b: the same coordination is reachable from a shared
            # observation at zero channel charge.
            shared_observation_alias += 1

    require(value_mismatch == 0, "MC-3: two-route channel value mismatch")
    require(silent_mismatch == 0, "MC-3: two-route silent value mismatch")
    require(pay_mismatch == 0, "MC-3: two-route strict-pay mismatch")
    require(com2_mismatch == 0, "MC-3: COM-2 equivalence failed")
    require(negative_gain == 0, "MC-3: COM-1 refinement monotonicity violated")
    require(free_but_useless > 0, "MC-3: the free-but-useless boundary must be witnessed")
    require(valuable_but_unaffordable > 0,
            "MC-3: the valuable-but-unaffordable boundary must be witnessed")
    require(shared_observation_alias > 0,
            "MC-3: the shared-observation hostile twin must be witnessed")
    require(hostile_nonstrict_pay_detected == exact_tie_price and exact_tie_price > 0,
            "MC-3: the non-strict pay hostile must be detected on every tie case")

    return {
        "row": "Re-audit communication.",
        "results": ["COM-1", "COM-2", "COM-3", "REF-1"],
        "external_definition": (
            "a charged channel whose use changes the jointly achievable score"
        ),
        "census": {
            "channel_instances": total,
            "strictly_paying": strict_pay,
            "free_but_useless": free_but_useless,
            "valuable_but_unaffordable": valuable_but_unaffordable,
            "exact_tie_price_cases": exact_tie_price,
            "shared_observation_aliased": shared_observation_alias,
        },
        "two_route_mismatches": {
            "channel_value": value_mismatch,
            "silent_value": silent_mismatch,
            "strict_pay": pay_mismatch,
            "com2_equivalence": com2_mismatch,
        },
        "hostiles_detected": {
            "H3a_non_strict_pay_rule": hostile_nonstrict_pay_detected,
            "H3b_coordination_from_shared_observation": shared_observation_alias,
        },
        "abstention": ABSTENTIONS["MC-3"],
        "demarcation": (
            "ecology-generator variation of communication topology and price is "
            "owned by #959 / #957; this is the capability-side derivation"
        ),
    }


# ==========================================================================
# MC-4  imitation and teaching
# ==========================================================================

def route_a_imitation(instance: Dict[str, object]) -> bool:
    """A strict fall in the learner's charged acquisition cost attributable to the
    demonstration, established against the same-condition no-demonstration arm."""
    return instance["learner_demo"] < instance["learner_control"]


def route_a_demonstrator_pays(instance: Dict[str, object]) -> bool:
    return instance["demonstrator"] > F(0)


def route_a_teaching(instance: Dict[str, object]) -> bool:
    return route_a_demonstrator_pays(instance) and route_a_imitation(instance)


def route_a_failed_teaching(instance: Dict[str, object]) -> bool:
    return route_a_demonstrator_pays(instance) and not route_a_imitation(instance)


def route_a_jointly_worthwhile(instance: Dict[str, object]) -> bool:
    """TCH-2: n * (control - demo) > demonstrator charge."""
    saving = instance["learner_control"] - instance["learner_demo"]
    return instance["learners"] * saving > instance["demonstrator"]


def route_a_free_labour_worthwhile(instance: Dict[str, object]) -> bool:
    saving = instance["learner_control"] - instance["learner_demo"]
    return instance["learners"] * saving > F(0)


def route_a_naive_prepost_imitation(instance: Dict[str, object]) -> bool:
    """The detector that lacks a same-condition control arm: it compares the
    learner charge under demonstration against an earlier, different condition."""
    if "naive_pre" not in instance:
        return False
    return instance["learner_demo"] < instance["naive_pre"]


def run_mc4() -> Dict[str, object]:
    total = 0
    cells = {"imitation_only": 0, "teaching": 0, "failed_teaching": 0, "neither": 0}
    worth_mismatch = 0
    cell_mismatch = 0
    free_labour_mismatch = 0
    worthwhile_charged = 0
    worthwhile_free_labour = 0
    free_labour_artifacts = 0
    artifact_witness = None  # type: Optional[Dict[str, object]]
    containment_violation = 0

    for instance in scopes.iter_teaching_instances():
        total += 1
        imitation = route_a_imitation(instance)
        paid = route_a_demonstrator_pays(instance)
        imitation_b, paid_b = route_b.brute_force_cell(instance)
        if (imitation, paid) != (imitation_b, paid_b):
            cell_mismatch += 1

        if imitation and not paid:
            cells["imitation_only"] += 1
        elif imitation and paid:
            cells["teaching"] += 1
        elif paid and not imitation:
            cells["failed_teaching"] += 1
        else:
            cells["neither"] += 1

        worth_a = route_a_jointly_worthwhile(instance)
        worth_b = route_b.brute_force_teaching_worthwhile(instance)
        if worth_a != worth_b:
            worth_mismatch += 1
        free_a = route_a_free_labour_worthwhile(instance)
        free_b = route_b.brute_force_free_labour_worthwhile(instance)
        if free_a != free_b:
            free_labour_mismatch += 1

        if worth_a:
            worthwhile_charged += 1
        if free_a:
            worthwhile_free_labour += 1
        if worth_a and not free_a:
            containment_violation += 1
        if free_a and not worth_a:
            # HOSTILE H4a: a verdict manufactured by erasing the demonstrator's
            # charge from the lifecycle resource vector.
            free_labour_artifacts += 1
            if artifact_witness is None:
                artifact_witness = {
                    "learner_control": frac(instance["learner_control"]),
                    "learner_demo": frac(instance["learner_demo"]),
                    "demonstrator": frac(instance["demonstrator"]),
                    "learners": instance["learners"],
                    "aggregate_saving": frac(
                        instance["learners"]
                        * (instance["learner_control"] - instance["learner_demo"])
                    ),
                }

    require(cell_mismatch == 0, "MC-4: two-route cell classification mismatch")
    require(worth_mismatch == 0, "MC-4: two-route joint-worth mismatch")
    require(free_labour_mismatch == 0, "MC-4: two-route free-labour mismatch")
    require(containment_violation == 0,
            "TCH-3: the charged-worthwhile set must be contained in the free-labour set")
    require(free_labour_artifacts > 0,
            "TCH-3: strict containment must be witnessed")
    for cell_name in ("imitation_only", "teaching", "failed_teaching", "neither"):
        require(cells[cell_name] > 0,
                "TCH-1: cell %s must be realizable" % cell_name)

    # --- NONID-4: concurrent-cause non-identification ------------------------
    rng = scopes.Lcg(seed=833_4_1)
    concurrent_total = 0
    naive_false_alarms = 0
    control_arm_alarms = 0
    for _ in range(200):
        instance = scopes.random_concurrent_cause_instance(rng)
        concurrent_total += 1
        if route_a_naive_prepost_imitation(instance):
            naive_false_alarms += 1
        if route_a_imitation(instance):
            control_arm_alarms += 1
    require(control_arm_alarms == 0,
            "NONID-4: the control-arm detector must raise no alarm on inert demonstrations")
    require(naive_false_alarms == concurrent_total,
            "NONID-4: the pre/post detector must be shown to fire on every inert case")

    # recall of the control-arm detector on planted genuine imitation
    rng2 = scopes.Lcg(seed=833_4_2)
    planted = 0
    planted_detected = 0
    for _ in range(200):
        base = scopes.random_concurrent_cause_instance(rng2)
        drop = rng2.choice((F(1, 4), F(1, 2), F(1)))
        genuine = {
            "learner_control": base["learner_demo"] + drop,
            "learner_demo": base["learner_demo"],
            "demonstrator": base["demonstrator"],
            "learners": base["learners"],
            "naive_pre": base["naive_pre"],
        }
        planted += 1
        if route_a_imitation(genuine):
            planted_detected += 1
    require(planted_detected == planted,
            "NONID-4: the control-arm detector must recall every planted imitation")

    return {
        "row": "Re-audit imitation and teaching.",
        "results": ["TCH-1", "TCH-2", "TCH-3", "NONID-4"],
        "external_definitions": {
            "imitation": "the learner's charged acquisition cost falls strictly "
                         "because of the observed demonstration",
            "teaching": "the demonstrator pays a strictly positive charge that "
                        "causes that fall",
            "failed_teaching": "the demonstrator pays but the learner's burden "
                               "does not fall",
        },
        "census": {
            "instances": total,
            "cells": cells,
            "worthwhile_with_demonstrator_charge": worthwhile_charged,
            "worthwhile_under_free_labour": worthwhile_free_labour,
            "free_labour_artifacts": free_labour_artifacts,
            "concurrent_cause_instances": concurrent_total,
            "planted_imitation_instances": planted,
        },
        "two_route_mismatches": {
            "cell_classification": cell_mismatch,
            "joint_worth": worth_mismatch,
            "free_labour": free_labour_mismatch,
        },
        "hostiles_detected": {
            "H4a_free_labour_verdicts": free_labour_artifacts,
            "H4b_failed_teaching_is_not_teaching": cells["failed_teaching"],
            "H4c_prepost_detector_false_alarms": naive_false_alarms,
        },
        "control_arm_detector": {
            "false_alarms_on_concurrent_cause": control_arm_alarms,
            "recall_on_planted_imitation": planted_detected,
        },
        "free_labour_artifact_witness": artifact_witness,
        "abstention": ABSTENTIONS["MC-4"],
    }


# ==========================================================================
# MC-5  cultural accumulation
# ==========================================================================

def route_a_closed_form_trajectory(phi: F, g: F, a0: F, generations: int) -> Tuple[F, ...]:
    """CUL-1 closed form. For phi < 1 the recursion has the unique fixed point
    a* = g / (1 - phi) and a_n = a* + phi**n * (a0 - a*); for phi == 1 it is the
    arithmetic ladder a_n = a0 + n * g."""
    if phi == 1:
        return tuple(a0 + F(n) * g for n in range(generations + 1))
    star = g / (F(1) - phi)
    return tuple(star + (phi ** n) * (a0 - star) for n in range(generations + 1))


def route_a_ratchet_flags(phi: F, g: F, trajectory: Sequence[F]) -> Tuple[bool, ...]:
    """CUL-1 ratchet condition: generation n ratchets iff (1 - phi) * a_n < g."""
    loss = F(1) - phi
    return tuple(loss * trajectory[n] < g for n in range(len(trajectory) - 1))


def route_a_cost_separation(phi: F, g: F, a_n: F, t: F, r: F, k: F) -> F:
    """CUL-2 separation margin in closed algebraic form:
    C_T - C_R = (t - r) * phi * a_n + (k - r) * g."""
    return (t - r) * phi * a_n + (k - r) * g


def run_mc5() -> Dict[str, object]:
    generations = scopes.CULTURE_GENERATIONS
    triples = 0
    trajectory_mismatch = 0
    flag_mismatch = 0
    step_cases = 0
    ratchet_steps = 0
    ceiling_violations = 0
    twin_mismatch = 0
    baseline_returns = 0
    unbounded_ratchets = 0
    separation_cases = 0
    separation_mismatch = 0
    indistinguishable_cost_cases = 0
    strictly_separated_cases = 0
    max_margin = F(0)

    for phi, g, a0 in scopes.iter_culture_triples():
        triples += 1
        traj_a = route_a_closed_form_trajectory(phi, g, a0, generations)
        traj_b = route_b.brute_force_trajectory(phi, g, a0, generations)
        if traj_a != traj_b:
            trajectory_mismatch += 1
        flags_a = route_a_ratchet_flags(phi, g, traj_a)
        flags_b = route_b.brute_force_ratchet_flags(traj_b)
        if flags_a != flags_b:
            flag_mismatch += 1
        step_cases += len(flags_a)
        ratchet_steps += sum(1 for f in flags_a if f)

        if phi < 1:
            star = g / (F(1) - phi)
            for n in range(len(traj_a) - 1):
                # CUL-1 exact step identity: a_{n+1} - a_n = (1 - phi) * (a* - a_n).
                # Unconditional, and it is what makes the ratchet condition exact.
                if traj_a[n + 1] - traj_a[n] != (F(1) - phi) * (star - traj_a[n]):
                    ceiling_violations += 1
            for n in range(len(traj_a)):
                # CUL-1 side preservation. For phi > 0 the fixed point is
                # approached but never reached or crossed; for phi = 0 it is
                # reached exactly at the first transmitted generation. Either way
                # the ceiling is never crossed.
                if a0 < star:
                    if traj_a[n] > star:
                        ceiling_violations += 1
                    if phi > 0 and n > 0 and not traj_a[n] < star:
                        ceiling_violations += 1
                    if phi == 0 and n > 0 and traj_a[n] != star:
                        ceiling_violations += 1
                elif a0 > star:
                    if traj_a[n] < star:
                        ceiling_violations += 1
                    if phi > 0 and n > 0 and not traj_a[n] > star:
                        ceiling_violations += 1
                    if phi == 0 and n > 0 and traj_a[n] != star:
                        ceiling_violations += 1
                else:
                    if traj_a[n] != star:
                        ceiling_violations += 1
            for n in range(len(traj_a) - 1):
                # CUL-1 monotonicity toward the ceiling.
                if a0 < star and traj_a[n + 1] < traj_a[n]:
                    ceiling_violations += 1
                if a0 > star and traj_a[n + 1] > traj_a[n]:
                    ceiling_violations += 1
            if g == 0 and a0 > 0:
                # CUL-1 return to baseline: no innovation plus lossy transmission
                # decays the population strictly and monotonically to exactly 0
                # (reached at the first generation when phi = 0).
                if star != F(0):
                    ceiling_violations += 1
                if not traj_a[-1] < a0:
                    ceiling_violations += 1
                if phi == 0 and traj_a[-1] != F(0):
                    ceiling_violations += 1
                baseline_returns += 1
        else:
            # CUL-1 lossless branch: the arithmetic ladder a_n = a0 + n * g.
            for n in range(len(traj_a)):
                if traj_a[n] != a0 + F(n) * g:
                    ceiling_violations += 1
            if g > 0:
                unbounded_ratchets += 1

        # NONID-5: the zero-transmission re-deriving twin reproduces the whole
        # capability trajectory. Unconditional; route B iterates it with phi = 0.
        twin = route_b.brute_force_rederivation_twin(traj_b, generations)
        if twin != traj_a:
            twin_mismatch += 1

        # CUL-2 / CUL-3: what the charged lifecycle resource trajectory does and
        # does not separate.
        for t, r, k in scopes.iter_culture_cost_vectors():
            transmitting, rederiving = route_b.brute_force_costs(
                traj_b, phi, g, t, r, k
            )
            all_zero = True
            for n in range(generations):
                margin_a = route_a_cost_separation(phi, g, traj_a[n], t, r, k)
                margin_b = transmitting[n] - rederiving[n]
                separation_cases += 1
                if margin_a != margin_b:
                    separation_mismatch += 1
                if margin_a != 0:
                    all_zero = False
                if -margin_a > max_margin:
                    max_margin = -margin_a
            if all_zero:
                indistinguishable_cost_cases += 1
            else:
                strictly_separated_cases += 1

    require(trajectory_mismatch == 0, "MC-5: two-route trajectory mismatch")
    require(flag_mismatch == 0, "MC-5: two-route ratchet classification mismatch")
    require(ceiling_violations == 0, "CUL-1: the exact ceiling classification failed")
    require(twin_mismatch == 0,
            "NONID-5: the zero-transmission twin must reproduce every trajectory")
    require(separation_mismatch == 0, "CUL-2: two-route cost separation mismatch")
    require(indistinguishable_cost_cases > 0,
            "CUL-3: the equal-unit-cost indistinguishability boundary must be witnessed")
    require(strictly_separated_cases > 0,
            "CUL-3: strict resource separation must be witnessed")
    require(baseline_returns > 0, "CUL-1: return to baseline must be witnessed")
    require(unbounded_ratchets > 0, "CUL-1: lossless unbounded ratcheting must be witnessed")

    # the named equal-unit-cost boundary: t == r == k makes C_T == C_R identically
    boundary_zero = 0
    boundary_cases = 0
    for phi, g, a0 in scopes.iter_culture_triples():
        traj = route_a_closed_form_trajectory(phi, g, a0, generations)
        for unit in scopes.CULTURE_UNIT_COSTS:
            for n in range(generations):
                boundary_cases += 1
                if route_a_cost_separation(phi, g, traj[n], unit, unit, unit) == 0:
                    boundary_zero += 1
    require(boundary_zero == boundary_cases,
            "CUL-3 boundary: t == r == k must give an identically zero margin")

    return {
        "row": "Re-audit cultural accumulation.",
        "results": ["CUL-1", "CUL-2", "CUL-3", "NONID-5"],
        "external_definition": (
            "generation n+1's achievable capability strictly exceeds generation "
            "n's starting capability through a transmission channel rather than "
            "through re-derivation"
        ),
        "census": {
            "triples": triples,
            "generations_per_triple": generations,
            "ratchet_step_cases": step_cases,
            "ratcheting_steps": ratchet_steps,
            "cost_separation_cases": separation_cases,
            "cost_vectors_per_triple": 27,
            "indistinguishable_cost_regimes": indistinguishable_cost_cases,
            "strictly_separated_cost_regimes": strictly_separated_cases,
            "return_to_baseline_triples": baseline_returns,
            "lossless_unbounded_ratchet_triples": unbounded_ratchets,
            "equal_unit_cost_boundary_cases": boundary_cases,
            "largest_exact_transmission_margin": frac(max_margin),
        },
        "two_route_mismatches": {
            "trajectory": trajectory_mismatch,
            "ratchet_flags": flag_mismatch,
            "cost_separation": separation_mismatch,
        },
        "hostiles_detected": {
            "H5a_trajectory_claimed_to_identify_transmission": triples,
            "H5b_equal_unit_cost_claimed_to_separate": indistinguishable_cost_cases,
        },
        "abstention": ABSTENTIONS["MC-5"],
        "demarcation": (
            "within-lifetime library formation and reuse transfer are owned by "
            "#897 (gmi-833-g0-grammar-growth-v1); this row is inter-generational "
            "transmission between populations"
        ),
    }


# ==========================================================================
# registered nulls
# ==========================================================================

def run_nulls() -> Dict[str, object]:
    # MC-1 null: no randomized allocation policy beats the backward-induction
    # optimum on a randomized deliberation scope.
    rng = scopes.Lcg(seed=833_1_0)
    mc1_trials = 0
    mc1_strict_wins = 0
    for _ in range(200):
        scope = scopes.random_deliberation_scope(rng)
        optimum, _policy = route_a_optimal_allocation(scope)
        decisions = scopes.delib_decision_paths(scope["depth"], scope["branch"])
        random_policy = dict((d, rng.next_int(2) == 1) for d in decisions)
        value = route_b._policy_value(scope, random_policy)
        mc1_trials += 1
        if value > optimum:
            mc1_strict_wins += 1

    # MC-2 null: zero false alarms on ecologies whose channel is sufficient, full
    # recall on planted insufficient ones.
    rng = scopes.Lcg(seed=833_2_0)
    mc2_clean = 0
    mc2_false_alarms = 0
    mc2_planted = 0
    mc2_recall = 0
    for _ in range(200):
        eco = scopes.random_social_ecology(rng)
        prior = eco["prior"]
        gap = (route_a_finest_value(prior, eco["score"], eco["n_actions"])
               - route_a_refinement_value(prior, eco["score"], eco["channel"], eco["n_actions"]))
        if route_a_pointwise_sufficient(prior, eco["score"], eco["channel"], eco["n_actions"]):
            mc2_clean += 1
            if gap > 0:
                mc2_false_alarms += 1
    for _ in range(200):
        prior = rng.choice(scopes.SOCIAL_PRIORS_2)
        high = rng.choice((F(1), F(2)))
        low = rng.choice((F(1), F(2)))
        score = ((high, F(0)), (F(0), low))
        eco = {"prior": prior, "score": score, "channel": (0, 0), "n_actions": 2}
        gap = (route_a_finest_value(prior, score, 2)
               - route_a_refinement_value(prior, score, (0, 0), 2))
        gap_b = route_b.brute_force_hidden_value(eco) - route_b.brute_force_channel_value(eco)
        mc2_planted += 1
        if gap > 0 and gap == gap_b:
            mc2_recall += 1

    # MC-3 null: a channel that delivers no refinement value never pays, at any
    # registered price; and the two routes never disagree on strict pay.
    rng = scopes.Lcg(seed=833_3_0)
    mc3_trials = 0
    mc3_route_disagreements = 0
    mc3_useless_declared_paying = 0
    for _ in range(200):
        eco = scopes.random_communication_ecology(rng)
        prior = eco["prior"]
        gain = (route_a_refinement_value(prior, eco["score"], eco["partition"], eco["n_actions"])
                - route_a_refinement_value(prior, eco["score"], tuple(0 for _ in prior),
                                           eco["n_actions"]))
        pays_a = gain > eco["price"]
        pays_b = route_b.brute_force_channel_strictly_pays(eco)
        mc3_trials += 1
        if pays_a != pays_b:
            mc3_route_disagreements += 1
        if gain == 0 and pays_a:
            mc3_useless_declared_paying += 1

    # MC-5 null: the closed form never disagrees with direct iteration.
    rng = scopes.Lcg(seed=833_5_0)
    mc5_trials = 0
    mc5_disagreements = 0
    for _ in range(200):
        phi, g, a0 = scopes.random_culture_triple(rng)
        traj_a = route_a_closed_form_trajectory(phi, g, a0, scopes.CULTURE_GENERATIONS)
        traj_b = route_b.brute_force_trajectory(phi, g, a0, scopes.CULTURE_GENERATIONS)
        mc5_trials += 1
        if traj_a != traj_b:
            mc5_disagreements += 1

    require(mc1_strict_wins == 0, "MC-1 null: a random policy beat the optimum")
    require(mc2_false_alarms == 0, "MC-2 null: false alarm on a sufficient channel")
    require(mc2_recall == mc2_planted, "MC-2 null: missed a planted separating ecology")
    require(mc3_route_disagreements == 0, "MC-3 null: route disagreement")
    require(mc3_useless_declared_paying == 0, "MC-3 null: a useless channel was declared paying")
    require(mc5_disagreements == 0, "MC-5 null: closed form disagreed with iteration")
    require(mc2_clean > 0, "MC-2 null: the clean arm must be non-empty")

    return {
        "mc1_random_policy_beats_optimum": "%d/%d" % (mc1_strict_wins, mc1_trials),
        "mc2_false_alarms_on_sufficient_channel": "%d/%d" % (mc2_false_alarms, mc2_clean),
        "mc2_recall_on_planted_separation": "%d/%d" % (mc2_recall, mc2_planted),
        "mc3_route_disagreements": "%d/%d" % (mc3_route_disagreements, mc3_trials),
        "mc3_useless_channel_declared_paying": "%d/%d" % (mc3_useless_declared_paying, mc3_trials),
        "mc5_closed_form_vs_iteration_disagreements": "%d/%d" % (mc5_disagreements, mc5_trials),
    }


# ==========================================================================
# assembly
# ==========================================================================

def build_result() -> Dict[str, object]:
    parents = audit_parents()
    require(parents["all_pinned"],
            "parent drift: %s" % ",".join(parents["drift"]))
    mc1 = run_mc1()
    mc2 = run_mc2()
    mc3 = run_mc3()
    mc4 = run_mc4()
    mc5 = run_mc5()
    nulls = run_nulls()

    rows = {"MC-1": mc1, "MC-2": mc2, "MC-3": mc3, "MC-4": mc4, "MC-5": mc5}
    total_cases = 0
    for block in rows.values():
        for key, value in block["census"].items():
            if isinstance(value, int) and not isinstance(value, bool):
                if key.endswith("_cases") or key in (
                    "deliberation_scopes", "ecologies", "channel_instances",
                    "instances", "triples", "aliasing_schedule_space",
                ):
                    total_cases += value

    for block in rows.values():
        for count in block["two_route_mismatches"].values():
            require(count == 0, "two-route mismatch survived assembly")

    blob = json.dumps(rows, sort_keys=True, default=str)
    for promotion in FORBIDDEN_PROMOTIONS:
        require(promotion not in blob,
                "forbidden promotion %s leaked into a claim block" % promotion)

    return {
        "schema": "GMI833CognitiveReauditSocialResultV1",
        "issue": 833,
        "section": "M",
        "package": "gmi-833-cognitive-reaudit-social-v1",
        "frozen_source_main": FROZEN_SOURCE_MAIN,
        "claim_ceiling": CLAIM_CEILING,
        "verdict": "GREEN",
        "terminal": CLAIM_CEILING,
        "evidence_level": "EV2",
        "maturity": "M2",
        "domain_tag": "forall_fin[registered exact finite scopes] + forall[Q] for the "
                      "analytic characterizations",
        "rows": rows,
        "nulls": nulls,
        "parents": parents,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "abstention_vocabulary": ABSTENTIONS,
        "total_registered_cases": total_cases,
        "routes": {
            "A": "cognitive_reaudit_social_v1.py -- closed forms, backward "
                 "induction, refinement-value decomposition, exact classification",
            "B": "route_b_oracle_v1.py -- exhaustive policy enumeration, direct "
                 "recursion iteration; imports no route-A logic",
        },
    }


def main() -> int:
    result = build_result()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    (HERE / "RESULT_V1.json").write_text(text, encoding="utf-8")
    sys.stdout.write("verdict=%s cases=%d\n" % (result["verdict"], result["total_registered_cases"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

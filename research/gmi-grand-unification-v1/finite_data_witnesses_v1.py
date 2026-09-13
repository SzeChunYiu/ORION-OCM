"""Decisive exact controls; all numbers describe finite synthetic registers."""
from fractions import Fraction as F
from finite_data_model_v1 import (Problem, certificate, cheapest_mixture, model_distance,
                                 synthesize, transfer_bounds)
from finite_data_oracle_v1 import (all_profiles, dual_mixture_cost, mixed_evaluate,
                                  selected_sample_control)
from finite_data_sampling_v1 import (confidence_upper, empirical_register,
                                    row_confidence_upper, simultaneous_failure)


def require(value, reason):
    if not value:
        raise AssertionError(reason)


def chain(h, epsilon, settlement=3):
    n, goal, hazard = h+2, h, h+1
    rows = []
    for s in range(h):
        row = [F(0)]*n
        row[s+1], row[hazard] = 1-epsilon, epsilon
        rows.append((tuple(row),))
    rows += [(), ()]
    stage = tuple(tuple(((F(t+1),) if s < h else ()) for s in range(n)) for t in range(h))
    return Problem(tuple(rows), stage, tuple(F(settlement) if s == goal else F(0)
                   for s in range(n)), frozenset({goal}))


def choice(probability=F(15, 16), horizon=1, penalty=4):
    rows = (((F(0), probability, 1-probability), (F(0), F(1), F(0))), (), ())
    stage = (((F(1), F(3)), (), ()),)*horizon
    return Problem(rows, stage, (F(0), F(0), F(penalty)), frozenset({1}))


def sharp_controls():
    cases = 0
    for h in range(5):
        for epsilon in (F(0), F(1, 4), F(1, 2), F(1)):
            empirical, true = chain(h, F(0)), chain(h, epsilon)
            p, _ = all_profiles(empirical)
            require(len(p) == 1, "one-action chain policy")
            policy = ((F(1), next(iter(p.values()))),)
            a, b = mixed_evaluate(empirical, policy), mixed_evaluate(true, policy)
            slack, work = transfer_bounds(empirical, epsilon)
            require(a[0]-b[0] == slack and a[1]-b[1] == work, "sharp joint accumulation")
            cases += 1
    return dict(sharp_cases=cases, H4_epsilon_quarter=list(transfer_bounds(chain(4, F(0)), F(1, 4))))


def positive_certificate():
    n, epsilon = 768, F(1, 16)
    records = tuple((0, 0, i, 1 if i < 720 else 2) for i in range(n))
    rows, custody = empirical_register((2, 0, 0), {(0, 0): (1, 2)},
                                      {(0, 1): (0, 1, 0)}, records, n)
    reference = choice()
    empirical = Problem(rows, reference.stage, reference.settlement, reference.goals)
    result, stats = certificate(empirical, epsilon, F(7, 8), F(1, 4))
    probability, work = mixed_evaluate(reference, result["policy"]["policies"])
    bound = row_confidence_upper((2,), n, epsilon)
    require(bound < F(1, 20), "nonvacuous fixed-N confidence")
    require(result["success_interval"] == (F(7, 8), F(1)), "clipped success interval")
    require(result["cost_interval"][1] == F(3, 2), "terminal penalty retained")
    require((probability, work) == (F(15, 16), F(5, 4)), "actual chosen policy")
    return dict(samples=n, confidence_failure_upper=bound, alpha=F(1, 20), custody=custody,
                success_interval=result["success_interval"], work_interval=result["cost_interval"],
                actual_profile=(probability, work), seed_charge=result["policy"]["seed_charge"],
                acquisition_setup=12+4*n, dense_count_payload_bits=30, synthesis=stats)


def falsifying_controls():
    epsilon, n = F(1, 8), 8
    empirical, true = choice(F(1)), choice(1-epsilon)
    points, _ = synthesize(empirical)
    cheap = min(points, key=lambda p: p[1])
    policy = ((F(1), points[cheap]),)
    p0, c0 = mixed_evaluate(empirical, policy)
    p1, c1 = mixed_evaluate(true, policy)
    slack, work = transfer_bounds(empirical, epsilon)
    require(p0-p1 == epsilon and c1-c0 == 4*epsilon, "rare hazard and terminal charge")
    require(p0-p1 > 0 and c1-c0 > 0, "H-1/omitted-terminal mutations")
    require(model_distance(empirical, true) == epsilon, "half-L1 normalization")
    require(p0-p1 > epsilon/2, "quarter-L1 radius fails")
    require((1-epsilon)**n > 0 and p1 < 1, "all-safe finite data cannot certify sure success")
    fair = (F(1, 2), F(1, 2))
    correlated_tail = F(1)
    iid_bound = confidence_upper(1, 2, 32, F(1, 4))
    require(correlated_tail > iid_bound, "copied draws are not iid samples")
    one_row_tail = simultaneous_failure((fair,), 4, F(1, 4))
    two_row_tail = simultaneous_failure((fair, fair), 4, F(1, 4))
    selected = selected_sample_control()
    require(one_row_tail == F(1, 8) and two_row_tail == F(15, 64), "simultaneous event")
    require(selected["simultaneous_failure"] == two_row_tail, "ordered-data cross-check")
    require(selected["expected_selection_optimism"] > 0, "data-selected arm optimism")
    fees = {(F(0), F(0)): ("cheap",), (F(1), F(2)): ("safe",)}
    fee_policy = cheapest_mixture(fees, F(1, 2), 10)
    require(fee_policy["cost"] == 2 and dual_mixture_cost(fees, F(1, 2), 10) == 2,
            "seed fee changes optimum")
    no_fee = cheapest_mixture(fees, F(1, 2))
    require(no_fee["cost"] == 1, "unaugmented regret would fail at epsilon zero")
    mixed = cheapest_mixture(fees, F(1, 2), F(1, 4))
    require(mixed["cost"] == F(5, 4) and mixed["seed_charge"] == F(1, 4), "seed fee charged")
    return dict(rare_hazard=dict(N=n, eta=epsilon, all_safe_probability=(1-epsilon)**n,
                empirical_success=p0, true_success=p1, cost_gap=c1-c0, bound=(slack, work)),
                mutated_post_transition_cost_gap=epsilon, invalid_pretransition_bound=F(0),
                quarter_L1_mutation_bound=epsilon/2, copied_draw_failure=correlated_tail,
                falsely_applied_iid_upper=iid_bound, single_row_tail=one_row_tail,
                two_row_tail=two_row_tail, selected=selected, charged_mixture_cost=mixed["cost"],
                fee_sensitive_optima=(no_fee["cost"], fee_policy["cost"]))


def register_controls():
    errors = []
    for label, supports, known, records in (
        ("omitted_unreachable_row", {}, {(0, 0): (0, 0, 1)}, ()),
        ("missing_draw", {(1, 0): (1, 2)}, {(0, 0): (0, 0, 1)}, ((1, 0, 0, 2),)),
        ("duplicate_draw", {(1, 0): (1, 2)}, {(0, 0): (0, 0, 1)}, ((1, 0, 0, 2), (1, 0, 0, 2))),
        ("outside_supplied_alphabet", {(1, 0): (1,)}, {(0, 0): (0, 0, 1)}, ((1, 0, 0, 2), (1, 0, 1, 2))),
    ):
        try:
            empirical_register((1, 1, 0), supports, known, records, 2)
        except ValueError:
            errors.append(label)
        else:
            raise AssertionError(label)
    p = choice()
    changed = Problem(p.rows, (((2, 3), (), ()),), p.settlement, p.goals)
    try:
        model_distance(p, changed)
    except ValueError:
        errors.append("changed_known_costs")
    else:
        raise AssertionError("changed known costs accepted")
    rows, _ = empirical_register((2, 0, 0), {(0, 0): (1,)}, {(0, 1): (0, 1, 0)},
                                ((0, 0, 0, 1), (0, 0, 1, 1)), 2)
    fake_support = Problem(rows, p.stage, p.settlement, p.goals)
    require(row_confidence_upper((1,), 2, 0) == 0 and model_distance(p, fake_support) == F(1, 16),
            "observed support is not a true support certificate")
    points, _ = all_profiles(choice(F(1, 2), penalty=0))
    require(set(points) == {(F(1, 2), F(1)), (F(1), F(3))}, "different policies on same kernel")
    require(certificate(choice(F(1)), F(1), F(1))[0] is None,
            "conservative certificate may be absent in a feasible true model")
    safe, drifted = choice(F(1)), choice(F(0))
    tree = all_profiles(safe)[0][(F(1), F(1))]
    gap = mixed_evaluate(safe, ((F(1), tree),))[0]-mixed_evaluate(drifted, ((F(1), tree),))[0]
    require(gap == 1, "unregistered deployment drift")
    return dict(rejected=errors, false_support_radius=F(0), true_omitted_hazard=F(1, 16),
                different_policy_success_gap=F(1, 2), drift_success_gap=gap,
                conservative_certificate_absent_despite_safe_policy=True)

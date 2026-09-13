"""Exact finite policy/path diagnostics for certified reuse with invalidation."""
from fractions import Fraction as F
from itertools import product
from math import lcm
import json


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate(horizon, model, certified):
    if type(horizon) is not int or horizon < 0 or type(certified) is not bool:
        raise ValueError("nonnegative integer horizon and explicit repair admission required")
    if len(model) != 6 or any(type(x) not in (int, F) for x in model):
        raise ValueError("A,R,C,U,M,q must be finite exact non-Boolean rationals")
    a, r, c, u, m, q = map(F, model)
    if min(a, r, c, u, m) < 0 or not 0 <= q <= 1 or u > c:
        raise ValueError("nonnegative costs, U<=C and q in [0,1] required")
    return a, r, c, u, m, q


def bellman(horizon, model, certified, objective="expected"):
    a, r, c, u, m, q = validate(horizon, model, certified)
    if objective not in ("expected", "worstcase"):
        raise ValueError("declare expected or support-worstcase cost")
    cold = damaged = valid = F(0)
    for h in range(1, horizon + 1):
        hold = m if h > 1 else 0
        future = (1-q)*valid + q*damaged
        if objective == "worstcase":
            future = valid if q == 0 else damaged if q == 1 else max(valid, damaged)
        retained = min(cold, hold + future)
        damaged_options = [c+cold, c+hold+damaged, a+u+retained]
        if certified:
            damaged_options.append(r+u+retained)
        cold, damaged, valid = (min(c+cold, a+u+retained),
                                min(damaged_options), u+retained)
    return {"cold": cold, "damaged": damaged, "valid": valid}


def execute(costs, policy, failures, certified, initial_state=0, trace=False):
    """Direct lifetime ledger, including zero-cost logical release after service."""
    a, r, c, u, m = costs
    state, paid, visited = initial_state, 0, []  # cold=0, valid=1, damaged=2
    if type(state) is not int or state not in (0, 1, 2):
        raise ValueError("unknown initial state")
    if len(failures) != max(0, len(policy)-1):
        raise ValueError("one event per between-request interval required")
    for t, choices in enumerate(policy):
        visited.append(state)
        action = choices[state]
        if state == 0:
            if action not in (0, 1, 2):
                raise ValueError("illegal cold action")
            paid += a+u if action else c
            state = 1 if action == 1 else 0
        elif state == 1:
            if action not in (1, 2):
                raise ValueError("illegal valid action")
            paid += u
            state = 1 if action == 1 else 0
        else:
            if action not in (0, 1, 2, 3, 4, 5) or (action in (2, 4) and not certified):
                raise ValueError("repair is not admitted")
            paid += c if action < 2 else (r if action in (2, 4) else a)+u
            state = 2 if action == 1 else 1 if action in (2, 3) else 0
        if t < len(policy)-1:
            if type(failures[t]) is not int or failures[t] not in (0, 1):
                raise ValueError("binary invalidation event required")
            if state:
                paid += m
            if state == 1 and failures[t]:
                state = 2
    return (paid, visited) if trace else paid


def policy_oracle(horizon, model, certified, initial_state=0):
    """Enumerate reachable policy tables; direct path execution, no value recurrence."""
    values = validate(horizon, model, certified)
    scale = lcm(*(x.denominator for x in values[:5]))
    costs, q = tuple(int(x*scale) for x in values[:5]), values[5]
    intervals = max(0, horizon-1)
    paths = [(bits, q.numerator**sum(bits)*(q.denominator-q.numerator)**
              (intervals-sum(bits))) for bits in product((0, 1), repeat=intervals)]
    paths = [(bits, weight) for bits, weight in paths if weight]
    actions = ((0, 1, 2), (1, 2), (0, 1, 2, 3, 4, 5) if certified else (0, 1, 3, 5))
    best_mean = best_worst = None
    count = 0

    def visit(prefix):
        nonlocal best_mean, best_worst, count
        if len(prefix) == horizon:
            bills = [(execute(costs, prefix, bits, certified, initial_state), weight)
                     for bits, weight in paths]
            mean, worst = sum(p*w for p, w in bills), max(p for p, _ in bills)
            best_mean = mean if best_mean is None else min(best_mean, mean)
            best_worst = worst if best_worst is None else min(best_worst, worst)
            count += 1
            return
        padded = prefix+((0, 1, 0),)*(horizon-len(prefix))
        reachable = sorted({execute(costs, padded, bits, certified, initial_state, True)[1][len(prefix)]
                            for bits, _ in paths})
        for selected in product(*(actions[state] for state in reachable)):
            choices = [0, 1, 0]
            for state, action in zip(reachable, selected):
                choices[state] = action
            visit(prefix+(tuple(choices),))

    visit(())
    return {"expected": F(best_mean, scale*q.denominator**intervals),
            "worstcase": F(best_worst, scale), "policies": count,
            "positive_probability_histories": len(paths)}


def fixed_repair_gain(horizon, model, certified):
    a, r, c, u, m, q = validate(horizon, model, certified)
    if not certified or horizon == 0:
        raise ValueError("positive workload and admitted total repair required")
    return horizon*(c-u)-a-(horizon-1)*(m+q*r)


def safety_control():
    # Authored finite certificate interface, not a proof of any real repair mechanism.
    verifier = lambda context, proof: proof == ("accepted", context)
    rejected = transported = 0
    for old, new in ((0, 1), (1, 0)):
        original = ("accepted", old)
        rejected += not verifier(new, original)
        transported += verifier(new, ("accepted", new))
    attempt_work, fresh_work = F(1), F(2)
    accepted = verifier(1, ("accepted", 0))
    paid = attempt_work + (0 if accepted else fresh_work)
    require((rejected, transported, accepted, paid) == (2, 2, False, 3),
            "stale repair accepted or failed work uncharged")
    return {"stale_certificates_rejected": rejected, "transported_accepted": transported,
            "failed_attempt_cost": str(attempt_work), "failed_then_fresh_cost": str(paid)}


def run():
    catalog = ((0, 0, 2, 1, 0), (2, 1, 2, 1, 0), (2, 2, 2, 1, 0),
               (3, 4, 2, 1, F(1, 4)), (1, 1, 2, 2, F(1, 4)))
    census = []
    for h, costs, q in product(range(1, 4), catalog, (F(0), F(1, 2), F(1))):
        model = costs+(q,)
        actual = policy_oracle(h, model, True)
        for objective in ("expected", "worstcase"):
            require(actual[objective] == bellman(h, model, True, objective)["cold"],
                    "policy enumeration disagrees with Bellman value")
        census.append(actual)
    witnesses = []
    for hold, expected_cost in ((F(0), F(15, 2)), (F(1, 8), F(63, 8))):
        model = (2, 1, 2, 1, hold, F(1, 2))
        actual = policy_oracle(4, model, True)
        require(actual["expected"] == expected_cost and actual["worstcase"] == 8,
                "expected/guaranteed distinction lost")
        require(actual["expected"] == bellman(4, model, True)["cold"], "witness DP mismatch")
        policy = ((1, 1, 2),)*4
        path_costs = [execute(model[:5], policy, bits, True)
                      for bits in product((0, 1), repeat=3)]
        gain = 8-sum(path_costs)/F(8)
        require(gain == fixed_repair_gain(4, model, True), "renewal accounting mismatch")
        one_shot = sum(F(1, 2)**t for t in range(4))-2-hold*sum(F(1, 2)**t for t in range(3))
        require(one_shot < 0 and gain > 0 and 8-max(path_costs) < 0, "revival control lost")
        witnesses.append({"holding": str(hold), "optimal_expected_cost": str(actual["expected"]),
            "optimal_worstcase_cost": str(actual["worstcase"]), "fresh_cost": "8",
            "one_shot_expected_gain": str(one_shot), "repair_expected_gain": str(gain),
            "repair_worstcase_gain": str(8-max(path_costs)), "policies": actual["policies"],
            "histories": actual["positive_probability_histories"]})
    inadmissible = (2, 0, 2, 1, 0, F(1, 2))
    refused = policy_oracle(3, inadmissible, False)
    require(refused["expected"] == bellman(3, inadmissible, False)["cold"] == 6,
            "uncertified zero-price repair improved the verdict")
    release_model = (3, 1, 2, 1, 100, F(1, 2))
    release = policy_oracle(2, release_model, True, initial_state=1)
    release_path = execute(release_model[:5], ((0, 2, 0),)*2, (0,), True, initial_state=1)
    require(release["expected"] == release["worstcase"] == release_path ==
            bellman(2, release_model, True)["valid"] == 3, "post-service release omitted")
    safety = safety_control()
    return {"schema": "certified-reuse-invalidation-v1", "all_checks_green": True,
            "terminal": "CERTIFIED_REUSE_INVALIDATION_FINITE_GREEN",
            "census": {"instances": len(census), "expected_and_worstcase_matches": len(census),
                       "policy_history_executions": sum(x["policies"]*x["positive_probability_histories"] for x in census)},
            "witnesses": witnesses, "unadmitted_repair_optimal_cost": str(refused["expected"]),
            "certificate_safety": safety,
            "release_control": {"valid_start_optimum": "3", "fresh_abandon_cost": "4",
                                "holding_per_interval": "100", "logical_release_charge": "0"},
            "scope": "finite repair/release graph; authored costs, not measured proof performance"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))

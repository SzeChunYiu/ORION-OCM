from itertools import product

from developmental_quotient_minimizer import Transition, minimize_mealy


LOCAL_STATES = (0, 1, 2)
# 0: teachable-unlearned, query->0, teach1->2
# 1: stubborn-unlearned, query->0, teach1->1
# 2: learned, query->1, teach1->2


def local_query_output(state):
    return 1 if state == 2 else 0


def local_teach1(state):
    return 2 if state == 0 else state


def product_machine(n):
    states = tuple(product(LOCAL_STATES, repeat=n))
    events = tuple(
        [("query", i) for i in range(n)]
        + [("teach1", i) for i in range(n)]
    )
    transition = {}

    for state in states:
        row = {}
        for kind, i in events:
            if kind == "query":
                row[(kind, i)] = Transition(state, ("answer", i, local_query_output(state[i])))
            else:
                next_state = list(state)
                next_state[i] = local_teach1(state[i])
                row[(kind, i)] = Transition(tuple(next_state), ("ack", i))
        transition[state] = row

    return states, events, transition


def census(max_n=5):
    rows = []
    for n in range(1, max_n + 1):
        states, events, transition = product_machine(n)
        quotient = minimize_mealy(states, events, transition)
        rows.append(
            {
                "n_units": n,
                "explicit_global_states": len(states),
                "minimal_developmental_quotient_states": len(quotient),
                "expected_3_pow_n": 3 ** n,
                "factorized_local_state_symbols": 3 * n,
                "one_teaching_event_touches_units": 1,
            }
        )
    return rows


if __name__ == "__main__":
    import json
    print(json.dumps(census(), indent=2, sort_keys=True))

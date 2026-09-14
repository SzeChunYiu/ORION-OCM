"""One fixed exposed staged construction; all arm and audit costs are retained."""
from copy import deepcopy
from machine_v1 import Ledger, clone, empty, gate, hold
from search_v1 import acquire, flatten, solve, verify_primitive
from parent_oracle_v1 import first_hit, words

BOUND = 5


def task(offset, inputs=(0, 1, 2, 3)):
    return [(x, x + offset) for x in inputs]


def phase(before, after, result, ledger):
    return {"before": before, "after": deepcopy(after), "result": result,
            **ledger.record()}


def acquisition(start, offset, name, generator=None):
    ledger = Ledger()
    state = clone(start, ledger)
    before = deepcopy(state)
    kwargs = {} if generator is None else {"generator": generator}
    result = acquire(state, name, task(offset), BOUND, ledger, **kwargs)
    hold(state, ledger)
    return state, phase(before, state, result, ledger)


def serving(start):
    ledger = Ledger()
    state = clone(start, ledger)
    before = deepcopy(state)
    result = solve(state, task(5), BOUND, ledger)
    if result["status"] != "SOLVED":
        raise ValueError("fixed construction failed")
    body = flatten(result["body"], state, ledger)
    verify_primitive(body, task(5), ledger)
    fresh = verify_primitive(body, task(5, (4, 5)), ledger)
    hold(state, ledger)
    result["fresh_inputs"] = [4, 5]
    result["fresh_outputs"] = fresh
    expected = first_hit(state, task(5), BOUND)
    if {k: result[k] for k in ("body", "rank")} != expected:
        raise ValueError("independent first-hit mismatch")
    return phase(before, state, result, ledger)


def run():
    history, first = acquisition(empty(), 2, "h")
    setup = Ledger()
    reset = clone(history, setup)
    gate(reset, "h", False, setup)
    acquired, h_acq = acquisition(history, 4, "m")
    reset_acquired, r_acq = acquisition(reset, 4, "m")
    parent, p_acq = acquisition(history, 4, "m", words)
    if parent != acquired or p_acq != h_acq:
        raise ValueError("same-library parent mismatch")
    # No acquisition per lesion arm; only exact clones of one acquired state.
    intervention = Ledger()
    states = {}
    for arm in ("acquired", "disabled", "sham", "restored"):
        state = clone(acquired, intervention)
        if arm == "disabled":
            gate(state, "m", False, intervention)
        elif arm == "restored":
            gate(state, "m", False, intervention)
            gate(state, "m", True, intervention)
        else:
            gate(state, "m", True, intervention)
        states[arm] = state
    if states["acquired"] != states["sham"] or states["acquired"] != states["restored"]:
        raise ValueError("pre-query equality failed")
    arms = {name: serving(state) for name, state in states.items()}
    primitive_m, empty_acq = acquisition(empty(), 4, "m")
    empty_serve = serving(primitive_m)
    without_new = serving(history)
    empty_without_new = serving(empty())
    def signature(p):
        return p["result"], p["cost"], p["events"], p["before"], p["after"]
    if signature(arms["acquired"]) != signature(arms["sham"]) or signature(arms["acquired"]) != signature(arms["restored"]):
        raise ValueError("restore/sham mismatch")
    gained = h_acq["cost"] < r_acq["cost"]
    useful = (arms["acquired"]["result"]["rank"] < arms["disabled"]["result"]["rank"]
              and arms["acquired"]["cost"] < arms["disabled"]["cost"])
    if not gained or not useful:
        raise ValueError("fixed positive construction failed its stated gates")
    first_success = arms["acquired"]["result"]["candidates"][-1]
    prefix = arms["acquired"]["events"][:first_success["events_end"]]
    if not any(e["kind"] == "lookup" and e["name"] == "m" for e in prefix):
        raise ValueError("missing mediator use before success")
    traces = {"history": first, "acquisition_H": h_acq, "acquisition_RESET": r_acq,
              "same_library_parent": p_acq, "from_empty_acquisition": empty_acq,
              "from_empty_serving": empty_serve, "without_new_serving": without_new,
              "empty_without_new_serving": empty_without_new,
              **{"later_" + k: v for k, v in arms.items()}}
    diagnostics = {"reset_setup": setup.record(), "interventions": intervention.record()}
    return {"status": "PASS", "terminal": "PARENT_SUFFICIENT",
            "scope": "authored finite conditional new-capital acquisition; not #323",
            "conditional_acquisition": {"H": h_acq["cost"], "RESET_search_disabled": r_acq["cost"], "RESET_empty": empty_acq["cost"]},
            "later_costs": {k: v["cost"] for k, v in arms.items()},
            "later_ranks": {k: v["result"]["rank"] for k, v in arms.items()},
            "lifecycle": {"history_then_new_then_later": first["cost"] + h_acq["cost"] + arms["acquired"]["cost"],
                          "empty_then_new_then_later": empty_acq["cost"] + empty_serve["cost"]},
            "experiment_cost": sum(p["cost"] for p in traces.values()) + sum(p["cost"] for p in diagnostics.values()),
            "traces": traces, "diagnostics": diagnostics}

"""Reject a bare solving claim unless the fixed staged witness gates are present."""
from copy import deepcopy
from parent_oracle_v1 import value
from cost_oracle_v1 import check


def require(condition, message):
    if not condition:
        raise ValueError(message)


def certify(record):
    traces = record["traces"]
    h, disabled, reset = [traces[k] for k in
        ("acquisition_H", "acquisition_RESET", "from_empty_acquisition")]
    require(h["cost"] < disabled["cost"] and h["cost"] < reset["cost"],
            "conditional acquisition advantage missing")
    for phase in (h, disabled, reset):
        result = phase["result"]
        require(result["status"] == "SOLVED" and result.get("stored"),
                "solving is not stored acquisition")
        body = result["stored"]["body"]
        require(result["stored"]["name"] == "m" and
                dict(phase["after"]["library"]).get("m") == body,
                "stored mediator missing")
        response = [value(body, {}, x) for x in range(4)]
        require(response == [4, 5, 6, 7], "wrong acquired response")
        initial = [["double"], ["inc"]] + [b for _, b in phase["before"]["library"]]
        require(all([value(b, {}, x) for x in range(4)] != response for b in initial),
                "direct recall is not new capital")
    a = traces["later_acquired"]
    b = traces["later_disabled"]
    require(a["before"] == h["after"], "post-acquisition state changed")
    expected = deepcopy(a["before"])
    expected["active"].remove("m")
    require(b["before"] == expected, "lesion changed another causal field")
    for arm in ("sham", "restored"):
        require(traces["later_" + arm] == a, "sham/restore mismatch")
    require(a["cost"] < b["cost"] and a["result"]["rank"] < b["result"]["rank"],
            "new mediator has no later effect")
    require(traces["from_empty_serving"]["cost"] < traces["empty_without_new_serving"]["cost"],
            "RESET mediator has no later effect")
    require(any(e["kind"] == "lookup" and e["name"] == "m" for e in
                a["events"][:a["result"]["candidates"][-1]["events_end"]]),
            "mediator never executed before success")
    require(traces["same_library_parent"] == h, "parent subtraction missing")
    check(record)
    return {"conditional_new_capital_gate": True, "later_mediation_gate": True,
            "truly_empty_RESET_checked": True, "parent": "PARENT_SUFFICIENT",
            "scope": "this fixed exposed machine/task/price register"}

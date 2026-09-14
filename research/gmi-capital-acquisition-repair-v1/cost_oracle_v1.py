"""Independent closed-form event counts from programs, not copied event totals."""
def copy_cost(state):
    return 1 + len(state["active"]) + sum(1 + len(b) for _, b in state["library"])


def expanded(body, state):
    table = dict(state["library"])
    return sum(len(table[op]) if op in table else 1 for op in body)


def search_cost(state, result):
    total = 8
    table = dict(state["library"])
    for row in result["candidates"]:
        word = row["body"]
        macro_calls = sum(op in table for op in word)
        total += 1 + len(word) + 4 * (2 * expanded(word, state) + 2 * macro_calls) + 4
    return total


def acquisition_cost(before, after, result):
    # Newness: eight task coordinates, then four exact responses per old entry.
    known_lengths = [1, 1] + [len(b) for _, b in before["library"]]
    newness = 8 + sum(8 * k + 5 for k in known_lengths)
    body_len = len(result["stored"]["body"])
    admission = body_len + (12 + 8 * body_len) + (1 + body_len) + 2
    holding = sum(len(b) for _, b in after["library"])
    return copy_cost(before) + newness + search_cost(before, result) + admission + holding


def serving_cost(before, result):
    k = expanded(result["body"], before)
    # Flatten + independent four-input check + separate two-input evaluation.
    verification = k + (12 + 8 * k) + (6 + 4 * k)
    return (copy_cost(before) + search_cost(before, result) + verification
            + sum(len(b) for _, b in before["library"]))


def check(record):
    for name, phase in record["traces"].items():
        if "stored" in phase["result"]:
            expected = acquisition_cost(phase["before"], phase["after"], phase["result"])
        else:
            expected = serving_cost(phase["before"], phase["result"])
        if phase["cost"] != expected:
            raise ValueError(("independent cost mismatch", name, phase["cost"], expected))
    return {"all_phase_costs_agree": True, "phases": len(record["traces"])}

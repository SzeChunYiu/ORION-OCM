"""Independent recursive schedule and primitive first-hit oracle; no product import."""


def words(alphabet, bound):
    def extend(prefix, left):
        if not left:
            yield tuple(prefix)
        else:
            for symbol in alphabet:
                yield from extend(prefix + [symbol], left - 1)
    for length in range(1, bound + 1):
        yield from extend([], length)


def value(body, table, x):
    for op in body:
        if op == "double":
            x *= 2
        elif op == "inc":
            x += 1
        else:
            x = value(table[op], {}, x)
    return x


def first_hit(state, examples, bound):
    table = dict(state["library"])
    alphabet = [n for n, _ in state["library"][::-1] if n in state["active"]]
    alphabet += ["double", "inc"]
    for rank, body in enumerate(words(alphabet, bound), 1):
        outputs = [value(body, table, x) for x, _ in examples]
        if outputs == [y for _, y in examples]:
            return {"body": list(body), "rank": rank}
    return {"body": None, "rank": None}

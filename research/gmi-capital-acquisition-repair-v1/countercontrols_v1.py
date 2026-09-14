"""Independent exact order/claim countermodels, not historical campaign reruns."""
from itertools import product


def first_hit(alphabet, functions, target):
    for size in (1, 2):
        for rank, word in enumerate(product(alphabet, repeat=size), 1):
            outputs = []
            for x in range(4):
                for op in word:
                    x = functions[op](x)
                outputs.append(x)
            if tuple(outputs) == target:
                return size, sum(len(alphabet) ** n for n in range(1, size)) + rank, word
    raise ValueError("missing exact witness")


def run():
    table = {"inc": lambda x: x+1, "dec": lambda x: x-1,
             "double": lambda x: 2*x, "square": lambda x: x*x}
    target = (1, 3, 5, 7)
    reset = first_hit(sorted(table), table, target)
    augmented = {**table, "a": lambda x: 2*(x+1), "p2": lambda x: (x-1)**2}
    history = first_hit(sorted(augmented), augmented, target)
    if reset != (2, 11, ("double", "inc")) or history != (2, 8, ("a", "dec")):
        raise ValueError("order countermodel failed")
    return {"same_functions_renamed": {"target": list(target),
            "RESET": {"length": reset[0], "cost": reset[1], "body": list(reset[2])},
            "H": {"length": history[0], "cost": history[1], "body": list(history[2])}},
            "conditional_vs_lifecycle": {"history": 100, "acq_H": 1,
            "acq_RESET": 2, "later_equal": 1,
            "H_total": 102, "RESET_total": 3},
            "new_target_success_without_store": {"rank_improved": True,
            "stored_mediator": False, "original_K2_certificate": False}}

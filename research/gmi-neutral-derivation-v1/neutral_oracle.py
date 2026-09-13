"""Independent raw grammar enumerator for bounded exhaustive cross-checks."""
from collections import Counter
from functools import lru_cache
from neutral_machine import signature


@lru_cache(maxsize=None)
def raw_programs(arity, size):
    if size == 1:
        return (("c", 0), ("c", 1)) + tuple(("r", i) for i in range(arity))
    programs = []
    for left_size in range(1, size - 1):
        right_size = size - left_size - 1
        for table in range(16):
            for left in raw_programs(arity, left_size):
                for right in raw_programs(arity, right_size):
                    programs.append(("b", table, left, right))
    for test_size in range(1, size - 2):
        for yes_size in range(1, size - test_size - 1):
            no_size = size - test_size - yes_size - 1
            for no in raw_programs(arity, no_size):
                for yes in raw_programs(arity, yes_size):
                    for condition in raw_programs(arity, test_size):
                        programs.append(("i", condition, yes, no))
    return tuple(programs)


def raw_fibers(arity, size):
    return Counter(signature(program, arity) for program in raw_programs(arity, size))

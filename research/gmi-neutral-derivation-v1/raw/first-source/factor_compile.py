"""Distributive elimination lowered to scalar operations and table accesses.

Counters describe the registered abstract execution schedule, not Python RAM
or wall time. Original input tables remain resident throughout the schedule.
"""

from math import prod

from factor_model import Factor, assignments, encoded_bits, validate


def eliminate(sizes, factors, algebra, order):
    validate(sizes, factors, algebra)
    order = tuple(order)
    if sorted(order) != list(range(len(sizes))):
        raise ValueError("order must contain every variable exactly once")
    active = [(factor, False) for factor in factors]
    input_entries = sum(len(f.values) for f in factors)
    input_bits = sum(encoded_bits(x) for f in factors for x in f.values)
    counters = dict(multiply=0, add=0, lookup=0, scope_tests=0,
                    scope_coordinate_visits=0, index_coordinates=0,
                    assignment_coordinate_writes=0, input_value_checks=input_entries,
                    input_scope_checks=sum(len(f.scope) for f in factors),
                    generated_entries=0, generated_bits=0,
                    peak_table_entries=input_entries, peak_table_bits=input_bits,
                    arithmetic_result_bits=0,
                    max_scalar_bits=max([1] + [encoded_bits(x) for f in factors
                                              for x in f.values]))
    live_entries = live_bits = 0
    steps = []

    def observe(value):
        bits = encoded_bits(value)
        counters["arithmetic_result_bits"] += bits
        counters["max_scalar_bits"] = max(counters["max_scalar_bits"], bits)
        return value

    for variable in order:
        counters["scope_tests"] += len(active)
        counters["scope_coordinate_visits"] += sum(len(f.scope) for f, _ in active)
        bucket = [(f, generated) for f, generated in active if variable in f.scope]
        counters["scope_coordinate_visits"] += sum(len(f.scope) for f, _ in bucket)
        union = tuple(sorted({variable} | {v for f, _ in bucket for v in f.scope}))
        output_scope = tuple(v for v in union if v != variable)
        values = []
        for row in assignments(output_scope, sizes):
            counters["assignment_coordinate_writes"] += len(output_scope)
            accumulated = algebra.zero
            for value in range(sizes[variable]):
                counters["assignment_coordinate_writes"] += 1
                row[variable] = value
                term = algebra.one
                for factor, _ in bucket:
                    counters["lookup"] += 1
                    counters["index_coordinates"] += len(factor.scope)
                    counters["multiply"] += 1
                    term = observe(algebra.multiply(term, factor.at(row, sizes)))
                counters["add"] += 1
                accumulated = observe(algebra.add(accumulated, term))
            values.append(accumulated)
        generated = Factor(output_scope, tuple(values))
        new_entries = len(values)
        new_bits = sum(encoded_bits(x) for x in values)
        counters["generated_entries"] += new_entries
        counters["generated_bits"] += new_bits
        counters["peak_table_entries"] = max(counters["peak_table_entries"],
                                             input_entries + live_entries + new_entries)
        counters["peak_table_bits"] = max(counters["peak_table_bits"],
                                          input_bits + live_bits + new_bits)
        live_entries += new_entries - sum(len(f.values) for f, old in bucket if old)
        live_bits += new_bits - sum(encoded_bits(x) for f, old in bucket if old
                                   for x in f.values)
        steps.append(dict(variable=variable, union=list(union), factors=len(bucket),
                          assignments=prod(sizes[v] for v in union),
                          output_entries=new_entries))
        active = [(f, old) for f, old in active if variable not in f.scope]
        active.append((generated, True))
    result = algebra.one
    for factor, _ in active:
        counters["lookup"] += 1
        counters["multiply"] += 1
        result = observe(algebra.multiply(result, factor.values[0]))
    counters["work"] = counters["multiply"] + counters["add"] + counters["lookup"]
    counters["input_entries"] = input_entries
    counters["input_bits"] = input_bits
    counters["final_scalars"] = len(active)
    counters["width"] = max([0] + [len(step["union"]) - 1 for step in steps])
    return dict(value=result, order=order, profile=counters, steps=steps)

"""Finite witness rosters for fixed partial-context resource images."""
from core_v21 import Context, checked, machine_checked, nat, nat_set, need, subset, word_checked
from execution_v21 import weighted_run


def _data(context, histories, machine, selected):
    checked(context)
    machine_checked(machine)
    need(type(histories) is tuple and len(histories) == context.n, "history dimension")
    for history in histories:
        need(type(history) is tuple and len(history) == 2, "raw history pair required")
        word_checked(machine, history[0], history[1])
    need(len(set(histories)) == len(histories), "duplicate raw history")
    subset(selected, context.n)
    return tuple(weighted_run(machine, *history) for history in histories)


def restrict(context, histories, machine, budget, selected):
    if budget is not None:
        nat(budget)
    runs = _data(context, histories, machine, selected)
    chosen = set(selected)
    admitted = tuple(context.admitted[i] and i in chosen and runs[i] is not None
                     and (budget is None or runs[i][1] <= budget) for i in range(context.n))
    return Context(context.n, context.m, admitted, context.defined, context.values, context.order)


def joint(context, histories, machine, selected):
    runs = _data(context, histories, machine, selected)
    return tuple(sorted({(runs[i][1], context.values[i]) for i in selected
                         if runs[i] is not None and context.admitted[i] and context.defined[i]}))


def joint_checked(pairs):
    need(type(pairs) is tuple, "canonical joint image required")
    for pair in pairs:
        need(type(pair) is tuple and len(pair) == 2, "cost/value pair required")
        nat(pair[0])
        nat(pair[1])
    need(len(set(pairs)) == len(pairs), "duplicate cost/value pair")
    return pairs


def attained(context):
    checked(context)
    return tuple(sorted({context.values[i] for i in range(context.n)
                         if context.admitted[i] and context.defined[i]}))


def attained_at(pairs, budget):
    joint_checked(pairs)
    nat(budget)
    return tuple(sorted({value for cost, value in pairs if cost <= budget}))


def capability(pairs, budget, target):
    nat_set(target)
    values = attained_at(pairs, budget)
    return any(value in target for value in values)


def threshold(pairs, target):
    joint_checked(pairs)
    nat_set(target)
    costs = [cost for cost, value in pairs if value in target]
    return min(costs) if costs else None


def threshold_witness(context, histories, machine, selected, target):
    runs = _data(context, histories, machine, selected)
    subset(target, context.m)
    witnesses = [(runs[i][1], i) for i in selected if runs[i] is not None
                 and context.admitted[i] and context.defined[i] and context.values[i] in target]
    return min(witnesses) if witnesses else None


def projection(values, rho):
    nat_set(values)
    need(type(rho) is tuple, "declared total coordinate map required")
    for output in rho:
        nat(output)
    subset(values, len(rho))
    return tuple(sorted({rho[value] for value in values}))

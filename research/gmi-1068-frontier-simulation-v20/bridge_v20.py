"""Declared endpoint observations on actual residual-budget continuation states."""
from core_v20 import LegacyMachine, budget_lift, checked, nat, need, order
from maps_v20 import guarded, image
from simulation_v20 import Machine, checked as checked_machine, endpoints


def from_v8(machine, base, max_budget):
    need(type(machine) is LegacyMachine, "actual V8 Machine required")
    nat(max_budget)
    lifted = budget_lift(machine, max_budget)
    base = order(base)
    need(len(base) == len(lifted.observations), "base must cover residual-budget states")
    rows = tuple(tuple(None if edge is None else edge[2] for edge in row)
                 for row in lifted.transitions)
    return Machine(base, rows, len(lifted.transitions[0]))


def valued_endpoints(machine, context, states, word):
    checked_machine(machine)
    checked(context)
    need(context.n == len(machine.base), "endpoint context dimension")
    values = tuple(context.values[x] if context.admitted[x] and context.defined[x] else None
                   for x in range(context.n))
    need(guarded(machine.base, context.order, values),
         "active endpoint evaluation must be guarded-monotone for the base order")
    return image(values, endpoints(machine, states, word), context.m)

"""Partial-loss plan contexts retain the common identity universe."""
from dataclasses import dataclass
from core_v24 import need, ids as check_ids, rational, index, subset, code_context, frontier


@dataclass(frozen=True)
class PlanTable:
    ids: tuple
    admitted: tuple
    defined: tuple
    losses: tuple

    def __post_init__(self):
        check_ids(self.ids)
        fields = (self.admitted, self.defined, self.losses)
        need(all(type(v) is tuple for v in fields), "canonical history matrices required")
        need(len(self.admitted) == len(self.defined) == len(self.losses), "history dimension")
        for matrix in fields:
            need(all(type(row) is tuple and len(row) == len(self.ids) for row in matrix), "plan dimension")
        need(all(type(v) is bool for matrix in fields[:2] for row in matrix for v in row), "Boolean flags required")
        for row in self.losses:
            for value in row:
                rational(value)


def _table(table):
    need(type(table) is PlanTable, "validated PlanTable required")
    return table


def plan_context(table, history):
    _table(table)
    index(history, len(table.admitted))
    losses = table.losses[history]
    relation = tuple(tuple(b <= a for b in losses) for a in losses)
    return (code_context(table.admitted[history], table.defined[history], relation),
            tuple(zip(table.ids, losses)))


def feasible_ids(table, history, epsilon):
    _table(table)
    rational(epsilon)
    context, decoder = plan_context(table, history)
    attained = frontier.attained(context, tuple(range(context.n)))
    return tuple(sorted(decoder[i][0] for i in attained if decoder[i][1] <= epsilon))


def common_plans(table, histories, epsilon):
    _table(table)
    rational(epsilon)
    subset(histories, len(table.admitted))
    feasible = set(table.ids)
    for history in histories:
        feasible.intersection_update(feasible_ids(table, history, epsilon))
    return tuple(sorted(feasible))

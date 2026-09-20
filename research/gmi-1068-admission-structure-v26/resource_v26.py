"""Exact additive natural costs and explicit bounded resource-state categories."""
from dataclasses import dataclass, field
from core_v26 import Table, Typed, checked_category, checked_path, nat, need
from functors_v26 import Functor


@dataclass(frozen=True)
class ResourceLift:
    base: object
    costs: tuple
    max_balance: int
    category: object = field(init=False)
    forgetful: object = field(init=False)
    object_labels: tuple = field(init=False)
    arrow_labels: tuple = field(init=False)

    def __post_init__(self):
        base = checked_category(self.base)
        nat(self.max_balance)
        need(type(self.costs) is tuple and len(self.costs) == len(base.table.rows), "cost shape")
        for cost in self.costs:
            nat(cost)
        for identity in base.identities:
            need(self.costs[identity] == 0, "identity cost")
        for f, row in enumerate(base.table.rows):
            for g, product in enumerate(row):
                if product is not None:
                    need(self.costs[product] == self.costs[f] + self.costs[g], "additive cost")
        width = self.max_balance + 1
        objects = tuple((a, r) for a in range(base.object_count) for r in range(width))
        arrows = tuple((f, r) for f in range(len(self.costs))
                       for r in range(self.costs[f], width))
        lookup = {label: i for i, label in enumerate(arrows)}
        source = tuple(base.source[f] * width + r for f, r in arrows)
        target = tuple(base.target[f] * width + r - self.costs[f] for f, r in arrows)
        identities = tuple(lookup[(base.identities[a], r)] for a, r in objects)
        rows = tuple(tuple(None if target[i] != source[j]
                           else lookup[(base.table.rows[f][g], r)]
                           for j, (g, _) in enumerate(arrows)) for i, (f, r) in enumerate(arrows))
        category = Typed(len(objects), source, target, identities, Table(rows))
        checked_category(category)
        forgetful = Functor(category, base, tuple(a for a, _ in objects),
                            tuple(f for f, _ in arrows))
        for name, value in (("category", category), ("forgetful", forgetful),
                            ("object_labels", objects), ("arrow_labels", arrows)):
            object.__setattr__(self, name, value)


def lift_path(model, path, initial_balance):
    need(type(model) is ResourceLift, "expected ResourceLift")
    start, word = checked_path(model.base, path)
    nat(initial_balance)
    need(initial_balance <= model.max_balance, "balance outside declared range")
    lookup = {label: i for i, label in enumerate(model.arrow_labels)}
    obj, balance, lifted = start, initial_balance, []
    for arrow in word:
        if model.base.source[arrow] != obj or model.costs[arrow] > balance:
            return None
        lifted.append(lookup[(arrow, balance)])
        balance -= model.costs[arrow]
        obj = model.base.target[arrow]
    resource_start = start * (model.max_balance + 1) + initial_balance
    return (resource_start, tuple(lifted)), balance

from __future__ import annotations
from typing import Sequence
from factor_core_v2 import *
from factor_arms_v1 import FactorLocal as _FactorLocal, LazySymbolic, GlobalRefit, SurrogateParent, loo_relevance, evolutionary_fit

class FactorLocal(_FactorLocal):
    name = "factor_local"

class SymbolicCompact(FactorLocal):
    name = "symbolic_compact_parent"
    def __init__(self):
        super().__init__()
        self.relevance = set()
    def update(self, rows: Sequence[Episode], generation: int) -> None:
        touched = []
        for a in range(ACTIONS):
            if generation == 1 or any(predict_model(self.models[a], e.x) != e.correct_actions[a] for e in rows):
                touched.append(a)
        for a in touched:
            m, c = learn_minimal_dnf(rows, a)
            self.models[a] = m
            self.cost.add(c)

class SymbolicMemory(SymbolicCompact):
    name = "symbolic_incremental_memory_parent"
    def __init__(self):
        super().__init__()
        self.history: list[Episode] = []
    def update(self, rows: Sequence[Episode], generation: int) -> None:
        self.history.extend(rows)
        super().update(rows, generation)

class ResetFactor(FactorLocal):
    name = "reset_factor_ablation"
    def __init__(self):
        super().__init__()
        self.history: list[Episode] = []
    def update(self, rows: Sequence[Episode], generation: int) -> None:
        self.history.extend(rows)
        self.models = [tuple() for _ in range(ACTIONS)]
        self.relevance = set()
        for a in range(ACTIONS):
            m, c = learn_minimal_dnf(rows, a)
            self.models[a] = m
            self.cost.add(c)
        self.relevance = {i for m in self.models for c in m for i in c}
        self.cost.maintenance_ops += len(self.relevance) + ACTIONS

def retained_state_bytes(arm) -> int:
    if isinstance(arm, SymbolicMemory):
        return state_bytes(arm.models) + archive_bytes(arm.history)
    if isinstance(arm, ResetFactor):
        return state_bytes(arm.models, arm.relevance) + archive_bytes(arm.history)
    if isinstance(arm, GlobalRefit):
        return state_bytes(arm.models) + archive_bytes(arm.history)
    if isinstance(arm, LazySymbolic):
        return state_bytes(arm.models) + archive_bytes(arm.current)
    if isinstance(arm, SymbolicCompact):
        return state_bytes(arm.models)
    if isinstance(arm, FactorLocal):
        return state_bytes(arm.models, arm.relevance)
    raise TypeError(type(arm))

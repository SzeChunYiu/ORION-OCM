#!/usr/bin/env python3
"""Development-only source/accounting audit for protected V3. Never opens protected seeds."""
from pathlib import Path
from factorization_survival_v3 import *

assert tuple(Episode.__dataclass_fields__) == ("x", "correct_actions")

# Correct-but-non-identifiable oracle support is neither rewarded nor penalized as a false positive.
oracle = (
    ((0,), (1,)), ((2,), (3,)), ((4,), (5,)), ((6,), (7,)),
)
ident = [{(0,)}, set(), set(), set()]
models = [((0,), (1,)), tuple(), tuple(), tuple()]
sm = support_metrics(models, oracle, ident)
assert sm["support_precision"] == 1.0 and sm["support_recall"] == 1.0 and sm["support_f1"] == 1.0
assert sm["identifiable_supports"] == 1 and sm["nonidentifiable_supports"] == 7

# Locality does not get a free contradiction detector.
x = (1, 1) + (0,) * 10
row = Episode(x, (1, 0, 0, 0))
c = Cost()
assert not contradicted(((0, 1),), [row], 0, c)
assert c.invalidation_examples == 1 and c.invalidation_literal_evals == 2

# Exact-retention parents really retain the cross-generation episode stream.
w = World.make(1, "sparse_stable")
g1 = episodes(w, 1, "sparse_stable", 1, "train", TRAIN_N)
g2 = episodes(w, 1, "sparse_stable", 2, "train", TRAIN_N)
lazy = LazySymbolic(); memory = SymbolicMemory()
for arm in (lazy, memory):
    arm.update(g1, 1); arm.update(g2, 2)
assert len(lazy.history) == len(memory.history) == 2 * TRAIN_N
assert lazy.history[:TRAIN_N] == memory.history[:TRAIN_N] == g1
assert lazy.history[TRAIN_N:] == memory.history[TRAIN_N:] == g2

# Window and persistent learned-surrogate parents are distinct and both are present.
sw, sp = Surrogate(False), Surrogate(True)
sw.update(g1, 1); sp.update(g1, 1); sp_before = sp.size()
sw.update(g2, 2); sp.update(g2, 2)
assert sp.size() >= sp_before
assert sw.name == "surrogate_window_parent" and sp.name == "surrogate_persistent_parent"

# OCM-like factor and compact symbolic parent get identical factor powers; the cache is the only extra state.
factor, compact = FactorLocal(), SymbolicCompact()
for generation, rows in ((1, g1), (2, g2)):
    factor.update(rows, generation); compact.update(rows, generation)
assert factor.models == compact.models
for key in ("induction_literal_evals", "induction_candidates", "induction_selection_ops",
            "invalidation_literal_evals", "invalidation_examples", "update_components_touched",
            "validation_examples", "rediscovery_ops"):
    assert getattr(factor.cost, key) == getattr(compact.cost, key)
assert factor.cost.maintenance_ops >= compact.cost.maintenance_ops
assert factor.size() > compact.size()

# The decision rule is componentwise, not a sum of heterogeneous resources.
assert "lifetime_median_learning_work" not in Path(__file__).with_name("factorization_survival_v3.py").read_text()
assert "RESOURCE_KEYS" in Path(__file__).with_name("factorization_survival_v3.py").read_text()

# No protected seed is a default or hard-coded execution target.
source = Path(__file__).with_name("factorization_survival_v3.py").read_text()
assert 'default="1,2,3,4,5,6,7,8"' in source
for seed in range(9301, 9341):
    assert str(seed) not in source

# One development-only end-to-end smoke: exact sparse factor recovery and strongest-parent subtraction.
r = run_seed(1, "sparse_stable")
last = r["generations"][-1]["arms"]
assert last["factor_local"]["heldout_accuracy"] == 1.0
assert last["factor_local"]["heldout_balanced_accuracy"] == 1.0
assert last["factor_local"]["support_f1"] == 1.0
assert last["symbolic_compact_parent"]["support_f1"] == 1.0
ft = {k: life_sum(r, "factor_local", k) for k in RESOURCE_KEYS}
pt = {k: life_sum(r, "symbolic_compact_parent", k) for k in RESOURCE_KEYS}
assert dominates(last["symbolic_compact_parent"], last["factor_local"], pt, ft)
assert life_sum(r, "reset_factor_ablation", "rediscovery_ops") > life_sum(r, "factor_local", "rediscovery_ops")
print("V3_DEV_SOURCE_ACCOUNTING_AUDIT_PASS")

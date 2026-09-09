"""Vectorized T0 tape: batched, bit-identical run_lifetime (GS GPU lane).

The frozen T0 battery (evaluation/lifetime.py run_lifetime) is a fixed-tape
deterministic cost simulation: every charge is an arithmetic expression of
compiled features, with per-organism branch selection but NO data-dependent
iteration.  This module re-executes the SAME tape over a batch of encoded
organisms (gpu/encode.py), preserving each organism's accumulation ORDER,
so every float output is bit-identical to the CPU reference.

Backends (identical results, verified by tests):
  'py'     pure stdlib python columns (CPython 3.8-3.14, no numpy)
  'numpy'  numpy float64/int64 columns
  'torch'  torch float64 tensors on CPU or CUDA (gpua40 lane)

Honesty rules encoded here:
  * rounding: the CPU reference rounds only at REPORT time (epoch series +
    summary).  The tape accumulates raw doubles and rounds with python
    round() during per-organism assembly, never inside the accumulation,
    so no backend rounding drift is possible.
  * masked charges add exactly 0.0 where an organism does not take a
    branch; adding +0.0 to a non-negative accumulator is an exact no-op,
    so branch masks cannot perturb sums.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from evaluation.lifetime import COST_MODEL_V1
from evaluation.invariants import CAPABILITY_FLOOR_V1

# frozen battery constants (bound to the frozen cost model at import so this
# file can never silently diverge from evaluation/lifetime.py)
_W1 = COST_MODEL_V1["w1_expansions"]        # 8.0
_W2 = COST_MODEL_V1["w2_expansions"]        # 14.0
_W4 = COST_MODEL_V1["w4_expansions"]        # 6.0
_W7_K = COST_MODEL_V1["w7_k"]               # 3.0
_W7_ITEMS = COST_MODEL_V1["w7_items"]       # 10.0
_W6_N = COST_MODEL_V1["w6_n_obs"]           # 12.0
_PROBE_N = int(-(-int(COST_MODEL_V1["w6_info_need"])
                // int(COST_MODEL_V1["w6_probe_yield"])))   # 2
_C_OBSERVE = COST_MODEL_V1["observe_work"]            # 1.0
_C_CLOSURE = COST_MODEL_V1["closure_work"]            # 2.0
_C_EXPANSION = COST_MODEL_V1["expansion_work"]        # 3.0
_C_RULE = COST_MODEL_V1["rule_fire_work"]             # 1.0
_C_REWRITE = COST_MODEL_V1["rewrite_work"]            # 4.0
_C_PROBE = COST_MODEL_V1["probe_work"]                # 2.0
_C_IDXBUILD = COST_MODEL_V1["index_build_work"]       # 8.0
_C_IDXQUERY = COST_MODEL_V1["index_query_work"]       # 1.0
_C_SCAN = COST_MODEL_V1["scan_item_work"]             # 1.0
_C_CONSIST = COST_MODEL_V1["consistency_work"]        # 4.0
_C_ABSTR = COST_MODEL_V1["abstraction_work"]          # 6.0
_C_STORE = COST_MODEL_V1["store_work"]                # 2.0
_C_REUSE = COST_MODEL_V1["reuse_work"]                # 1.0
_C_SCHEMAAPPLY = COST_MODEL_V1["schema_apply_work"]   # 1.0
_C_RESCAN = COST_MODEL_V1["rescan_work"]              # 10.0
_C_REVOK_FACTS = COST_MODEL_V1["revocation_facts"]    # 6.0
_C_CONE = COST_MODEL_V1["cone_reopen_work"]           # 3.0
_C_DISPATCH = COST_MODEL_V1["dispatch_work"]          # 1.0
_C_CONSOLIDATE = COST_MODEL_V1["consolidate_work"]    # 3.0


# ---------------------------------------------------------------- backends
class PyCol:
    """Pure-python float column: per-element IEEE-double ops (stdlib only)."""
    __slots__ = ("v",)

    def __init__(self, values):
        self.v = list(values)


def _py_zip(a, b):
    if isinstance(a, PyCol) and isinstance(b, PyCol):
        return zip(a.v, b.v)
    if isinstance(a, PyCol):
        return zip(a.v, _py_repeat(b, len(a.v)))
    if isinstance(b, PyCol):
        return zip(_py_repeat(a, len(b.v)), b.v)
    raise TypeError("at least one PyCol required")


def _py_repeat(x, n):
    return [x] * n


class PyBackend:
    name = "py"

    def col(self, values):
        return PyCol(values)

    def const(self, x, n):
        return PyCol([float(x)] * n)

    def add(self, a, b):
        if isinstance(a, PyCol) and isinstance(b, PyCol):
            return PyCol([x + y for x, y in zip(a.v, b.v)])
        if isinstance(a, PyCol):
            return PyCol([x + b for x in a.v])
        return PyCol([a + y for y in b.v])

    def sub(self, a, b):
        if isinstance(a, PyCol) and isinstance(b, PyCol):
            return PyCol([x - y for x, y in zip(a.v, b.v)])
        if isinstance(a, PyCol):
            return PyCol([x - b for x in a.v])
        return PyCol([a - y for y in b.v])

    def mul(self, a, b):
        if isinstance(a, PyCol) and isinstance(b, PyCol):
            return PyCol([x * y for x, y in zip(a.v, b.v)])
        if isinstance(a, PyCol):
            return PyCol([x * b for x in a.v])
        return PyCol([a * y for y in b.v])

    def div(self, a, b):
        if isinstance(a, PyCol) and isinstance(b, PyCol):
            return PyCol([x / y for x, y in zip(a.v, b.v)])
        if isinstance(a, PyCol):
            return PyCol([x / b for x in a.v])
        return PyCol([a / y for y in b.v])

    def le(self, a, b):
        return self._cmp(a, b, lambda x, y: x <= y)

    def lt(self, a, b):
        return self._cmp(a, b, lambda x, y: x < y)

    def ge(self, a, b):
        return self._cmp(a, b, lambda x, y: x >= y)

    def _cmp(self, a, b, op):
        if isinstance(a, PyCol) and isinstance(b, PyCol):
            return PyCol([op(x, y) for x, y in zip(a.v, b.v)])
        if isinstance(a, PyCol):
            return PyCol([op(x, b) for x in a.v])
        return PyCol([op(a, y) for y in b.v])

    def and_(self, a, b):
        return PyCol([bool(x) and bool(y) for x, y in _py_zip(a, b)])

    def or_(self, a, b):
        return PyCol([bool(x) or bool(y) for x, y in _py_zip(a, b)])

    def not_(self, a):
        return PyCol([not bool(x) for x in a.v])

    def where(self, cond, a, b):
        if isinstance(a, PyCol) or isinstance(b, PyCol):
            out = []
            ai = a.v if isinstance(a, PyCol) else None
            bi = b.v if isinstance(b, PyCol) else None
            n = len(cond.v)
            for i in range(n):
                x = ai[i] if ai is not None else a
                y = bi[i] if bi is not None else b
                out.append(x if cond.v[i] else y)
            return PyCol(out)
        return PyCol([a if c else b for c in cond.v])

    def floor_int(self, a):
        # CPU uses int(need) on non-negative floats: truncation toward zero
        return PyCol([int(x) for x in a.v])

    def as_float(self, a):
        return PyCol([float(x) for x in a.v])

    def to_list(self, a):
        return [float(x) for x in a.v]

    def to_intlist(self, a):
        return [int(x) for x in a.v]


class NumpyBackend:
    name = "numpy"

    def __init__(self):
        import numpy as np
        self.np = np

    def col(self, values):
        if isinstance(values, PyCol):
            return self.np.array(values.v, dtype=self.np.float64)
        return self.np.asarray(values, dtype=self.np.float64)

    def const(self, x, n):
        return self.np.full(n, float(x), dtype=self.np.float64)

    def add(self, a, b):
        return a + b

    def sub(self, a, b):
        return a - b

    def mul(self, a, b):
        return a * b

    def div(self, a, b):
        return a / b

    def le(self, a, b):
        return a <= b

    def lt(self, a, b):
        return a < b

    def ge(self, a, b):
        return a >= b

    def and_(self, a, b):
        return self.np.logical_and(a, b)

    def or_(self, a, b):
        return self.np.logical_or(a, b)

    def not_(self, a):
        return self.np.logical_not(a)

    def where(self, cond, a, b):
        return self.np.where(cond, a, b)

    def floor_int(self, a):
        return a.astype(self.np.int64)

    def as_float(self, a):
        return a.astype(self.np.float64)

    def to_list(self, a):
        return [float(x) for x in a.tolist()]

    def to_intlist(self, a):
        return [int(x) for x in a.tolist()]


class TorchBackend:
    name = "torch"

    def __init__(self, device: str = "cpu"):
        import torch
        self.torch = torch
        self.device = torch.device(device)

    def col(self, values):
        if isinstance(values, PyCol):
            return self.torch.tensor(values.v, dtype=self.torch.float64,
                                     device=self.device)
        return self.torch.as_tensor(values, dtype=self.torch.float64,
                                    device=self.device)

    def const(self, x, n):
        return self.torch.full((n,), float(x), dtype=self.torch.float64,
                               device=self.device)

    def add(self, a, b):
        return a + b

    def sub(self, a, b):
        return a - b

    def mul(self, a, b):
        return a * b

    def div(self, a, b):
        return a / b

    def le(self, a, b):
        return a <= b

    def lt(self, a, b):
        return a < b

    def ge(self, a, b):
        return a >= b

    def and_(self, a, b):
        return a.bool() & b.bool()

    def or_(self, a, b):
        return a.bool() | b.bool()

    def not_(self, a):
        return ~a.bool()

    def where(self, cond, a, b):
        return self.torch.where(cond.bool(), a, b)

    def floor_int(self, a):
        return a.trunc().to(self.torch.int64)

    def as_float(self, a):
        return a.to(self.torch.float64)

    def to_list(self, a):
        return [float(x) for x in a.tolist()]

    def to_intlist(self, a):
        return [int(x) for x in a.tolist()]


def make_backend(name: str = "auto", device: str = "cpu"):
    """auto: torch+cuda > numpy > py (torch CPU is used only when asked)."""
    if name == "auto":
        try:
            tb = TorchBackend("cuda")
            if tb.torch.cuda.is_available():
                return tb
        except Exception:
            pass
        try:
            import numpy  # noqa: F401
            return NumpyBackend()
        except Exception:
            return PyBackend()
    if name == "numpy":
        return NumpyBackend()
    if name == "torch":
        return TorchBackend(device)
    return PyBackend()


# ---------------------------------------------------------------- the tape
def run_t0_tape(batch, backend=None):
    """Execute the frozen T0 battery over an encoded batch.

    batch: as returned by gpu.encode.encode_batch (columns + meta).
    Returns per-organism dicts with EXACTLY the keys/roundings of
    evaluation.lifetime._summarize plus T0 gate verdicts.  Bit-identical
    to run_lifetime for every backend.
    """
    V = backend if backend is not None else PyBackend()
    C = batch["columns"]
    n = batch["n"]

    def col(name):
        return V.col(C[name])

    def const(x):
        return V.const(x, n)

    zero = const(0.0)
    one = const(1.0)

    # ---- capability flags ------------------------------------------
    can_rule = col("has_production_rule")
    can_plan = col("has_search_planner")
    can_fsm = col("has_fsm_controller")
    can_rewrite = col("has_rewrite_program")
    can_index = col("has_exact_index")
    can_assoc = col("has_assoc_similarity")
    can_check = col("can_check")
    can_probe = col("can_probe")
    can_schema = col("can_schema")
    persists = col("persists")
    fibred = col("f_hierarchical_fibred")
    r_none = col("r_none")
    r_full = col("r_full_rescan")
    budget = col("queue_budget")
    idx_theta = col("index_build_theta")
    fm_admit = col("fm_admit")
    fm_retrieve = col("fm_retrieve")
    fm_reopen = col("fm_reopen")
    fm_bytes = col("fm_bytes")
    fm_compose = col("fm_compose")
    tm_cross = col("tm_cross")
    tm_maint = col("tm_maintenance")
    em_dispatch = col("em_dispatch")
    em_exp = col("em_expansion")
    em_probe = col("em_probe")
    n_mod = col("n_modules")
    unit_prior = col("unit_prior")

    # work accumulators (float64, raw; rounded only at assembly)
    work = const(0.0)
    acq = const(0.0)
    reason = const(0.0)
    verif = const(0.0)
    maint = const(0.0)
    revis = const(0.0)
    epoch_acc = const(0.0)

    # integer state columns
    expansions = V.floor_int(const(0.0))
    probes = V.floor_int(const(0.0))
    facts = V.floor_int(const(0.0))
    schemas = V.floor_int(const(0.0))
    methods = V.floor_int(const(0.0))
    index_built = V.not_(one)  # all False
    zero_i = V.floor_int(const(0.0))

    def _chg(bucket_acc, w):
        return V.add(bucket_acc, w)

    # dispatch charge: dispatch_work * em_dispatch  (reasoning)
    disp_w = V.mul(const(_C_DISPATCH), em_dispatch)

    # epoch-series capture: raw epoch acc + per-epoch state snapshots
    epoch_work_raw = []
    epoch_caps_raw = []
    epoch_pb_raw = []

    # ================= EPOCH 1: acquisition + retrieval =================
    # 4 * observe_work * fm.admit (acquisition); facts += 4
    w_acq4 = V.mul(V.mul(const(4.0), const(_C_OBSERVE)), fm_admit)
    work = _chg(work, w_acq4); acq = _chg(acq, w_acq4)
    epoch_acc = _chg(epoch_acc, w_acq4)
    facts = V.add(facts, V.floor_int(const(4.0)))
    # solve_task("method_acq", w1=8, rule_path=can_rule, composition=False)
    work = _chg(work, disp_w); epoch_acc = _chg(epoch_acc, disp_w)
    reason = _chg(reason, disp_w)
    need1 = V.mul(const(_W1), em_exp)
    ma1_within = V.le(need1, budget)
    ma1_plan = V.and_(V.not_(can_rule), can_plan)
    ma1_plan_w = V.where(ma1_within,
                         V.mul(need1, const(_C_EXPANSION)),
                         V.mul(V.as_float(budget), const(_C_EXPANSION)))
    w_ma1 = V.where(can_rule, const(_C_RULE),
                    V.where(can_plan, ma1_plan_w, zero))
    work = _chg(work, w_ma1); epoch_acc = _chg(epoch_acc, w_ma1)
    reason = _chg(reason, w_ma1)
    exp_add1 = V.where(can_rule, zero_i,
                       V.where(can_plan,
                               V.where(ma1_within, V.floor_int(need1), budget),
                               zero_i))
    expansions = V.add(expansions, exp_add1)
    ma1_s = V.or_(can_rule, V.and_(can_plan, ma1_within))
    # store if persists (acquisition); methods += 1
    w_store = V.mul(persists, const(_C_STORE))
    work = _chg(work, w_store); acq = _chg(acq, w_store)
    epoch_acc = _chg(epoch_acc, w_store)
    methods = V.add(methods, V.floor_int(persists))
    # similarity recall: dispatch + branch (index > assoc > scan)
    work = _chg(work, disp_w); epoch_acc = _chg(epoch_acc, disp_w)
    reason = _chg(reason, disp_w)
    build_now = V.and_(V.and_(can_index, V.not_(index_built)),
                       V.ge(idx_theta, const(1.0)))
    w_build = V.where(build_now, const(_C_IDXBUILD), zero)
    work = _chg(work, w_build); acq = _chg(acq, w_build)
    epoch_acc = _chg(epoch_acc, w_build)
    index_built = V.or_(index_built, V.and_(can_index,
                                            V.ge(idx_theta, const(1.0))))
    w_idxq = V.where(can_index,
                     V.mul(V.mul(const(_C_IDXQUERY), fm_retrieve),
                           const(_W7_K)), zero)
    w_assoc_p = V.where(V.and_(V.not_(can_index), can_assoc),
                        V.mul(V.mul(const(_C_PROBE), const(_W7_K)),
                              fm_retrieve), zero)
    w_scan = V.where(V.and_(V.not_(can_index), V.not_(can_assoc)),
                     V.mul(const(_C_SCAN), const(_W7_ITEMS)), zero)
    for w_ev in (w_idxq, w_assoc_p, w_scan):
        work = _chg(work, w_ev); epoch_acc = _chg(epoch_acc, w_ev)
        reason = _chg(reason, w_ev)
    w_assoc_v = V.where(V.and_(V.not_(can_index), can_assoc),
                        const(_C_CONSIST), zero)
    work = _chg(work, w_assoc_v); epoch_acc = _chg(epoch_acc, w_assoc_v)
    verif = _chg(verif, w_assoc_v)
    # end_epoch 1: caps = ma1_s + 1 (sim recall always solved)
    epoch_work_raw.append(V.to_list(epoch_acc))
    epoch_caps_raw.append(V.to_intlist(V.add(V.floor_int(ma1_s), V.floor_int(one))))
    epoch_pb_raw.append(None)  # filled after state snapshot below
    # reset epoch acc; maintenance charges (consolidate + topology) go to E2
    epoch_acc = const(0.0)
    w_cons1 = V.mul(col("l_consolidation"), const(_C_CONSOLIDATE))
    work = _chg(work, w_cons1); maint = _chg(maint, w_cons1)
    epoch_acc = _chg(epoch_acc, w_cons1)
    w_tm1 = tm_maint
    work = _chg(work, w_tm1); maint = _chg(maint, w_tm1)
    epoch_acc = _chg(epoch_acc, w_tm1)

    # ================= EPOCH 2: reuse, composition, probing ============
    # method-acq reuse task
    work = _chg(work, disp_w); epoch_acc = _chg(epoch_acc, disp_w)
    reason = _chg(reason, disp_w)
    pers_epi = V.or_(V.ge(methods, V.floor_int(one)), col("has_episodic_memory"))
    ma2_plan_ok = V.and_(V.and_(V.not_(pers_epi), can_plan),
                         V.le(need1, budget))
    w_ma2 = V.where(pers_epi, const(_C_REUSE),
                    V.where(ma2_plan_ok, V.mul(need1, const(_C_EXPANSION)),
                            V.where(can_rule, const(_C_RULE), zero)))
    work = _chg(work, w_ma2); epoch_acc = _chg(epoch_acc, w_ma2)
    reason = _chg(reason, w_ma2)
    ma2_s = V.or_(pers_epi, V.or_(ma2_plan_ok, can_rule))
    # reused counter (methods>0 or episodic) -> method_reuse_fraction
    reused = pers_epi
    # composition task (w2=14, composition=True)
    work = _chg(work, disp_w); epoch_acc = _chg(epoch_acc, disp_w)
    reason = _chg(reason, disp_w)
    need2 = V.mul(V.mul(const(_W2), em_exp), fm_compose)
    comp_plan = V.and_(V.not_(can_rule), can_plan)
    w_cross_in = V.mul(V.mul(need2, const(_C_EXPANSION)), const(0.1))
    w_cross = V.mul(V.mul(w_cross_in, tm_cross),
                    V.add(const(1.0),
                          V.div(V.mul(const(0.1),
                                      V.sub(n_mod, const(1.0))),
                                const(2.0))))
    w_cross = V.where(comp_plan, w_cross, zero)
    work = _chg(work, w_cross); epoch_acc = _chg(epoch_acc, w_cross)
    reason = _chg(reason, w_cross)
    comp_within = V.le(need2, budget)
    comp_plan_w = V.where(comp_within,
                          V.mul(need2, const(_C_EXPANSION)),
                          V.mul(V.as_float(budget), const(_C_EXPANSION)))
    w_comp = V.where(can_rule,
                     V.mul(V.mul(const(_C_RULE), const(2.0)), fm_compose),
                     V.where(can_plan, comp_plan_w,
                             V.where(can_fsm,
                                     V.mul(V.mul(const(2.0), const(_C_RULE)),
                                           fm_compose), zero)))
    work = _chg(work, w_comp); epoch_acc = _chg(epoch_acc, w_comp)
    reason = _chg(reason, w_comp)
    exp_add2 = V.where(can_rule, zero_i,
                       V.where(can_plan,
                               V.where(comp_within, V.floor_int(need2), budget),
                               zero_i))
    expansions = V.add(expansions, exp_add2)
    comp_s = V.or_(can_rule, V.or_(V.and_(can_plan, comp_within), can_fsm))
    compose_used = comp_s
    # probe world 1
    work = _chg(work, disp_w); epoch_acc = _chg(epoch_acc, disp_w)
    reason = _chg(reason, disp_w)
    probe1_obs_ok = V.and_(V.not_(can_probe), V.ge(budget, const(_W6_N)))
    w_probe1_p = V.where(can_probe,
                         V.mul(V.mul(const(_PROBE_N), const(_C_PROBE)),
                               em_probe), zero)
    w_probe1_o = V.where(probe1_obs_ok,
                         V.mul(V.mul(const(_W6_N), const(_C_OBSERVE)),
                               fm_admit), zero)
    work = _chg(work, w_probe1_p); epoch_acc = _chg(epoch_acc, w_probe1_p)
    reason = _chg(reason, w_probe1_p)
    work = _chg(work, w_probe1_o); epoch_acc = _chg(epoch_acc, w_probe1_o)
    acq = _chg(acq, w_probe1_o)
    probes = V.add(probes, V.where(can_probe,
                                   V.floor_int(const(_PROBE_N)), zero_i))
    probe1_s = V.or_(can_probe, V.ge(budget, const(_W6_N)))
    # end_epoch 2: caps = ma2_s + comp_s + probe1_s
    epoch_work_raw.append(V.to_list(epoch_acc))
    epoch_caps_raw.append(None)  # filled at assembly
    epoch_pb_raw.append(None)
    epoch_acc = const(0.0)
    w_cons2 = V.mul(col("l_consolidation"), const(_C_CONSOLIDATE))
    work = _chg(work, w_cons2); maint = _chg(maint, w_cons2)
    epoch_acc = _chg(epoch_acc, w_cons2)
    work = _chg(work, w_tm1); maint = _chg(maint, w_tm1)
    epoch_acc = _chg(epoch_acc, w_tm1)

    # ================= EPOCH 3: revocation + scoped failure ============
    w_acq3 = V.mul(V.mul(const(3.0), const(_C_OBSERVE)), fm_admit)
    work = _chg(work, w_acq3); acq = _chg(acq, w_acq3)
    epoch_acc = _chg(epoch_acc, w_acq3)
    facts = V.add(facts, V.floor_int(const(3.0)))
    # closure task: dispatch + closure*retrieve (always solved)
    work = _chg(work, disp_w); epoch_acc = _chg(epoch_acc, disp_w)
    reason = _chg(reason, disp_w)
    w_clos = V.mul(const(_C_CLOSURE), fm_retrieve)
    work = _chg(work, w_clos); epoch_acc = _chg(epoch_acc, w_clos)
    reason = _chg(reason, w_clos)
    # revocation event: full_rescan | cone reopen | stale (no charge)
    w_rev = V.where(r_full,
                    V.mul(const(_C_RESCAN), const(_C_REVOK_FACTS)),
                    V.where(r_none, zero,
                            V.mul(V.mul(const(_C_CONE), fm_reopen),
                                  const(2.0))))
    work = _chg(work, w_rev); epoch_acc = _chg(epoch_acc, w_rev)
    revis = _chg(revis, w_rev)
    # re-solve after reopen
    work = _chg(work, disp_w); epoch_acc = _chg(epoch_acc, disp_w)
    reason = _chg(reason, disp_w)
    res_ok = V.and_(V.not_(r_none), V.or_(can_plan, can_rule))
    need3 = V.mul(const(4.0), em_exp)
    w_res = V.where(res_ok,
                    V.where(can_rule, const(_C_RULE),
                            V.mul(need3, const(_C_EXPANSION))), zero)
    work = _chg(work, w_res); epoch_acc = _chg(epoch_acc, w_res)
    reason = _chg(reason, w_res)
    # scoped failure x2: dispatch + (check | blind-reuse | rule)
    check_ok = V.or_(can_check, fibred)
    w_sc = V.where(check_ok,
                   V.mul(const(_C_CONSIST),
                         V.where(fibred, const(0.4), const(1.0))),
                   V.where(pers_epi, const(_C_REUSE), const(_C_RULE)))
    for _t in range(2):
        work = _chg(work, disp_w); epoch_acc = _chg(epoch_acc, disp_w)
        reason = _chg(reason, disp_w)
        work = _chg(work, w_sc); epoch_acc = _chg(epoch_acc, w_sc)
        verif = _chg(verif, V.where(check_ok, w_sc, zero))
        reason = _chg(reason, V.where(check_ok, zero, w_sc))
    # end_epoch 3: caps = 1 (closure) + res_ok
    epoch_work_raw.append(V.to_list(epoch_acc))
    epoch_caps_raw.append(None)
    epoch_pb_raw.append(None)
    epoch_acc = const(0.0)
    w_cons3 = V.mul(col("l_consolidation"), const(_C_CONSOLIDATE))
    work = _chg(work, w_cons3); maint = _chg(maint, w_cons3)
    epoch_acc = _chg(epoch_acc, w_cons3)
    work = _chg(work, w_tm1); maint = _chg(maint, w_tm1)
    epoch_acc = _chg(epoch_acc, w_tm1)

    # ============ EPOCH 4: repr twins, family variants, probe 2 =========
    need4 = V.mul(const(_W4), em_exp)
    twin_within = V.le(need4, budget)
    twin_path = V.and_(can_rewrite,
                       V.or_(can_rule, V.and_(can_plan, twin_within)))
    w_rewrite = V.where(can_rewrite, const(_C_REWRITE), zero)
    w_twin_sub = V.where(can_rewrite,
                         V.where(can_rule, const(_C_RULE),
                                 V.where(V.and_(can_plan, twin_within),
                                         V.mul(need4, const(_C_EXPANSION)),
                                         zero)), zero)
    exp_add4 = V.where(V.and_(can_rewrite,
                              V.and_(V.not_(can_rule),
                                     V.and_(can_plan, twin_within))),
                       V.floor_int(need4), zero_i)
    repr_s_sum = V.where(twin_path, const(2.0), const(0.0))
    for _t in range(2):
        work = _chg(work, disp_w); epoch_acc = _chg(epoch_acc, disp_w)
        reason = _chg(reason, disp_w)
        work = _chg(work, w_rewrite); epoch_acc = _chg(epoch_acc, w_rewrite)
        reason = _chg(reason, w_rewrite)
        work = _chg(work, w_twin_sub); epoch_acc = _chg(epoch_acc, w_twin_sub)
        reason = _chg(reason, w_twin_sub)
        expansions = V.add(expansions, exp_add4)
    # family variants x3 (i = 0, 1, 2)
    fv_plan_ok = V.and_(V.and_(V.not_(can_schema), V.not_(can_rule)),
                        V.and_(can_plan, V.ge(budget, const(_W4))))
    w_fv = V.where(can_schema, const(_C_SCHEMAAPPLY),
                   V.where(can_rule, const(_C_RULE),
                           V.where(fv_plan_ok,
                                   V.mul(const(_W4), const(_C_EXPANSION)),
                                   zero)))
    w_abstr = V.where(can_schema, const(_C_ABSTR), zero)
    for i in range(3):
        work = _chg(work, disp_w); epoch_acc = _chg(epoch_acc, disp_w)
        reason = _chg(reason, disp_w)
        if i == 0:
            work = _chg(work, w_abstr); acq = _chg(acq, w_abstr)
            epoch_acc = _chg(epoch_acc, w_abstr)
            schemas = V.add(schemas, V.floor_int(can_schema))
        work = _chg(work, w_fv); epoch_acc = _chg(epoch_acc, w_fv)
        reason = _chg(reason, w_fv)
    fv_s_sum = V.where(V.or_(can_schema, V.or_(can_rule, fv_plan_ok)),
                       const(3.0), const(0.0))
    # probe world 2
    work = _chg(work, disp_w); epoch_acc = _chg(epoch_acc, disp_w)
    reason = _chg(reason, disp_w)
    w_probe2 = V.where(can_probe,
                       V.mul(V.mul(const(_PROBE_N), const(_C_PROBE)),
                             em_probe), zero)
    work = _chg(work, w_probe2); epoch_acc = _chg(epoch_acc, w_probe2)
    reason = _chg(reason, w_probe2)
    probes = V.add(probes, V.where(can_probe,
                                   V.floor_int(const(_PROBE_N)), zero_i))
    probe2_s = can_probe
    # end_epoch 4 (records; trailing maintenance still charged to work)
    epoch_work_raw.append(V.to_list(epoch_acc))
    epoch_caps_raw.append(None)
    epoch_pb_raw.append(None)
    w_cons4 = V.mul(col("l_consolidation"), const(_C_CONSOLIDATE))
    work = _chg(work, w_cons4); maint = _chg(maint, w_cons4)
    w_tm4 = tm_maint
    work = _chg(work, w_tm4); maint = _chg(maint, w_tm4)

    # ---------------- persistent_bytes snapshots per epoch ---------------
    def _stored(methods_i, schemas_i, facts_i):
        m8 = V.mul(V.as_float(methods_i), const(8.0))
        e12 = const(0.0)  # episodes never incremented in T0
        s6 = V.mul(V.as_float(schemas_i), const(6.0))
        f1 = V.as_float(facts_i)
        acc = V.add(m8, e12)
        acc = V.add(acc, s6)
        acc = V.add(acc, f1)
        return acc

    def _pb(methods_i, schemas_i, facts_i, built):
        stored = _stored(methods_i, schemas_i, facts_i)
        base = V.add(unit_prior, V.mul(stored, fm_bytes))
        return V.add(base, V.where(built, const(24.0), const(0.0)))

    built = index_built
    methods_f = methods
    schemas_0 = zero_i
    facts_4 = V.add(zero_i, V.floor_int(const(4.0)))
    facts_7 = V.add(facts_4, V.floor_int(const(3.0)))
    pb_e1 = _pb(methods_f, schemas_0, facts_4, built)
    pb_e2 = pb_e1
    pb_e3 = _pb(methods_f, schemas_0, facts_7, built)
    pb_e4 = _pb(methods_f, schemas, facts_7, built)
    pb_final = pb_e4

    # ---------------- per-epoch capability snapshots --------------------
    def _bool_to_int(b):
        return V.where(b, V.floor_int(one), zero_i)

    caps_e1 = V.add(_bool_to_int(ma1_s), V.floor_int(one))
    caps_e2 = V.add(V.add(_bool_to_int(ma2_s), _bool_to_int(comp_s)),
                    _bool_to_int(probe1_s))
    caps_e3 = V.add(V.floor_int(one), _bool_to_int(res_ok))
    caps_e4 = V.add(V.add(V.floor_int(repr_s_sum), V.floor_int(fv_s_sum)),
                    _bool_to_int(probe2_s))
    for k, caps in ((1, caps_e1), (2, caps_e2), (3, caps_e3)):
        epoch_caps_raw[k - 1] = V.to_intlist(caps)
    epoch_caps_raw[3] = V.to_intlist(caps_e4)
    epoch_pb_raw[0] = V.to_list(pb_e1)
    epoch_pb_raw[1] = V.to_list(pb_e2)
    epoch_pb_raw[2] = V.to_list(pb_e3)
    epoch_pb_raw[3] = V.to_list(pb_e4)

    # ---------------- scalar summary columns ----------------------------
    solved = V.add(_bool_to_int(ma1_s), V.floor_int(one))
    solved = V.add(solved, _bool_to_int(ma2_s))
    solved = V.add(solved, _bool_to_int(comp_s))
    solved = V.add(solved, _bool_to_int(probe1_s))
    solved = V.add(solved, V.floor_int(one))        # closure task
    solved = V.add(solved, _bool_to_int(res_ok))
    solved = V.add(solved, V.floor_int(repr_s_sum))
    solved = V.add(solved, V.floor_int(fv_s_sum))
    solved = V.add(solved, _bool_to_int(probe2_s))
    solved_l = V.to_intlist(solved)
    total_tasks = 16
    work_l = V.to_list(work)
    acq_l = V.to_list(acq)
    reason_l = V.to_list(reason)
    verif_l = V.to_list(verif)
    maint_l = V.to_list(maint)
    revis_l = V.to_list(revis)
    pb_l = V.to_list(pb_final)
    expansions_l = V.to_intlist(expansions)
    probes_l = V.to_intlist(probes)
    harmful_l = [2 * (1 - int(bool(x))) for x in V.to_list(check_ok)]
    stale_l = [2 * int(bool(x)) for x in V.to_list(r_none)]
    refusals_l = [2 * int(bool(x)) for x in V.to_list(check_ok)]
    reused_l = [int(bool(x)) for x in V.to_list(pers_epi)]
    compose_l = [int(bool(x)) for x in V.to_list(comp_s)]
    ma1_l = [int(bool(x)) for x in V.to_list(ma1_s)]
    ma2_l = [int(bool(x)) for x in V.to_list(ma2_s)]
    comp_l = [int(bool(x)) for x in V.to_list(comp_s)]
    probe1_l = [int(bool(x)) for x in V.to_list(probe1_s)]
    probe2_l = [int(bool(x)) for x in V.to_list(probe2_s)]
    res_l = [int(bool(x)) for x in V.to_list(res_ok)]
    repr_l = [int(x) for x in V.to_list(repr_s_sum)]
    fv_l = [int(x) for x in V.to_list(fv_s_sum)]
    rnone_l = [int(bool(x)) for x in V.to_list(r_none)]
    methods_l = V.to_intlist(methods)
    schemas_l = V.to_intlist(schemas)
    n_act = C["n_active_units"]
    n_units = C["n_units"]

    # ---------------- assembly (exact CPU roundings, python round) ------
    out: List[Dict[str, Any]] = []
    for i in range(n):
        solved_i = solved_l[i]
        sf = round(solved_i / max(1, total_tasks), 6)
        ev = {
            "solved": solved_i, "total_tasks": total_tasks,
            "solved_fraction": sf,
            "work_total": round(work_l[i], 6),
            "acquisition_work": round(acq_l[i], 6),
            "reasoning_work": round(reason_l[i], 6),
            "verification_work": round(verif_l[i], 6),
            "maintenance_work": round(maint_l[i], 6),
            "revision_work": round(revis_l[i], 6),
            "self_change_work": 0.0,
            "persistent_bytes": round(pb_l[i], 6),
            "probes": probes_l[i], "expansions": expansions_l[i],
            "correct_refusals": refusals_l[i],
            "harmful_transfers": harmful_l[i],
            "stale_answers": stale_l[i],
            "method_reuse_fraction": round(reused_l[i] / 2.0, 6),
            "composition_used": compose_l[i],
            "per_family": {
                "composition": {"solved": comp_l[i], "total": 1},
                "family_variant": {"solved": fv_l[i], "total": 3},
                "method_acq": {"solved": ma1_l[i] + ma2_l[i], "total": 2},
                "probe": {"solved": probe1_l[i] + probe2_l[i], "total": 2},
                "repr_twin": {"solved": repr_l[i], "total": 2},
                "revocation": {"solved": 1 + (0 if rnone_l[i] else 1),
                               "total": 2},
                "scoped_failure": {"solved": 0, "total": 2},
                "similarity_recall": {"solved": 1, "total": 1},
            },
            "epoch_work": [round(epoch_work_raw[e][i], 6) for e in range(4)],
            "epoch_capabilities": [epoch_caps_raw[e][i] for e in range(4)],
            "epoch_persistent_bytes": [round(epoch_pb_raw[e][i], 6)
                                       for e in range(4)],
            "methods": methods_l[i], "episodes": 0, "schemas": schemas_l[i],
            "active_bytes_proxy": round(float(
                (4 + 3) * 1.0 + 6.0), 6),
            "dead_units": list(batch["meta"][i]["_dead_units"]),
            "active_kN": round(n_act[i] / max(1, int(n_units[i])), 6),
        }
        gates = {
            "GATE_CORRECTNESS": harmful_l[i] == 0 and stale_l[i] == 0,
            "GATE_INVARIANTS": True,
            "GATE_PROTECTED_ISOLATION": True,  # no external_io in the batch tape
            "GATE_REVOCATION_FIDELITY": rnone_l[i] == 0,
            "GATE_CAPABILITY_FLOOR": sf >= CAPABILITY_FLOOR_V1,
        }
        gates["feasible"] = all(gates.values())
        out.append({"evaluation": ev, "gates": gates,
                    "feasible": gates["feasible"], "tier": "T0",
                    "genotype_digest": batch["meta"][i]["_genotype_digest"],
                    "phenotype_digest": batch["meta"][i]["_phenotype_digest"],
                    "active_unit_types": list(
                        batch["meta"][i]["_active_unit_types"]),
                    "active_operators": list(
                        batch["meta"][i]["_active_operators"]),
                    "dead_units": list(batch["meta"][i]["_dead_units"]),
                    "n_units": int(n_units[i])})

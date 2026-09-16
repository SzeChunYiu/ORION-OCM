"""Neutral battery generator v1 — GMI #833 blind-recovery protocol v2.

Generation rules (all coverage-complete within a declared class; NO per-family
selection anywhere in this file). The output NEUTRAL_BATTERY_FREEZE_V1.json is
the frozen task battery; its git blob hash is the freeze anchor for every v2
recovery tranche. This generator reads no benchmark, family, or fingerprint
data: battery_generate_v1.py + its declared rules are the ENTIRE task source.

Battery classes:
  B_BOOL2      all 16 two-input boolean functions (per-task) + one
               class-universal task (all 16 functions selected by rank bits).
  B_BOOL3      all 256 three-input boolean functions (per-task).
  B_DELAY      all delayed-copy lags L = 0..L_MAX on a de Bruijn stream of
               order L_MAX+1; L_MAX is DERIVED from the machine state domain
               by the counting bound L <= floor(log2(|D|)).
  B_LOCAL      all 256 elementary local rules (3-site neighborhood) on a ring
               of width W (per-rule over all 2^W ring states) + one
               class-universal task (rule bits + ring bits).

Every numeric parameter below is derived or ablation-scoped in
PRIOR_DISCLOSURE_V1.md (section DERIVATIONS); none is tuned against any family
outcome.
"""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --- declared parameters (derivations in PRIOR_DISCLOSURE_V1.md) -------------
D_GUARD_PRIMARY = 3      # value-domain guard [-3,3]; ablations [-2,2], [-4,4]
RING_W_PRIMARY = 4       # = neighborhood span (3) + 1; ablation 8
L_MAX_DERIVATION = "floor(log2(|D|)) with D = [-3,3] => floor(log2(7)) = 2"
L_MAX_PRIMARY = int(math.floor(math.log2(2 * D_GUARD_PRIMARY + 1)))


def _bool_battery(n_inputs: int, universal: bool) -> dict:
    """Complete boolean-function battery of the given arity.

    Canonical order: truth-table vectors over lexicographic input rows.
    The class-universal task (when enabled) selects the function by the
    big-endian binary digits of its lexicographic rank.
    """
    rows = list(itertools.product((0, 1), repeat=n_inputs))
    per_task = []
    for r, table in enumerate(itertools.product((0, 1), repeat=len(rows))):
        per_task.append({
            "task_id": f"BOOL{n_inputs}_{r:0{len(rows)}d}",
            "rank": r,
            "inputs": [list(x) for x in rows],
            "required_outputs": list(table),
        })
    battery = {
        "battery_class": f"B_BOOL{n_inputs}",
        "generation_rule": "complete enumeration of all boolean functions of "
                           f"{n_inputs} inputs in lexicographic truth-table order",
        "per_task_tasks": per_task,
    }
    if universal:
        u_rows, u_req = [], []
        for r, table in enumerate(itertools.product((0, 1), repeat=len(rows))):
            select_bits = [(r >> b) & 1 for b in range(len(rows) - 1, -1, -1)]
            for row, out in zip(rows, table):
                u_rows.append(select_bits + list(row))
                u_req.append(int(out))
        battery["class_universal_task"] = {
            "task_id": f"BOOL{n_inputs}_UNIVERSAL",
            "inputs": u_rows,
            "required_outputs": u_req,
            "select_encoding": "select bits = big-endian binary digits of the "
                               "lexicographic rank of the truth-table vector",
        }
    return battery


def de_bruijn(k: int, n: int) -> list:
    """de Bruijn sequence B(k, n) via the standard Lyndon-word algorithm."""
    a = [0] * k * n
    sequence: list = []

    def db(t: int, p: int) -> None:
        if t > n:
            if n % p == 0:
                sequence.extend(a[1:p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)

    db(1, 1)
    return sequence


def delay_battery(l_max: int) -> dict:
    """All delayed-copy lags 0..l_max on a de Bruijn stream of order l_max+1."""
    order = l_max + 1
    stream = de_bruijn(2, order)
    tasks = []
    for lag in range(0, l_max + 1):
        # The machine reads the RAW stream from canonical initial state 0,
        # which encodes the zero input history x(-1..-lag) = 0; outputs are
        # therefore the stream delayed by lag with a zero prefix:
        # y[t] = 0 for t < lag, y[t] = x[t - lag] for t >= lag.
        required = [0] * lag + stream[:len(stream) - lag]
        tasks.append({
            "task_id": f"DELAY_{lag:02d}",
            "lag": lag,
            "stream": list(stream),
            "machine_inputs": list(stream),
            "required_outputs": required,
        })
    return {
        "battery_class": "B_DELAY",
        "l_max": l_max,
        "l_max_derivation": L_MAX_DERIVATION,
        "de_bruijn_order": order,
        "de_bruijn_length": len(stream),
        "generation_rule": "complete lag range 0..l_max with l_max derived by "
                           "the state-domain counting bound; stream = de Bruijn "
                           "sequence B(2, l_max+1) so every binary (l_max+1)-gram "
                           "occurs exactly once (full input-history coverage)",
        "tasks": tasks,
    }


def local_battery(w: int, universal: bool = True) -> dict:
    """All 256 elementary local rules on a ring of width w.

    Per-rule task: inputs = all 2^w ring states (lexicographic over site bits
    left-to-right); required output = the rule applied at every site with ring
    wraparound. Class-universal task: Wolfram-canonical rule bits + ring bits.
    """
    ring_states = list(itertools.product((0, 1), repeat=w))
    neighborhoods = list(itertools.product((0, 1), repeat=3))
    per_task = []
    tables = {}
    for r in range(256):
        out_bits = []
        for state in ring_states:
            nxt = [int((r >> neighborhoods.index(
                (state[(i - 1) % w], state[i], state[(i + 1) % w]))) & 1)
                for i in range(w)]
            out_bits.append(nxt)
        tables[r] = out_bits
        per_task.append({
            "task_id": f"LOCAL_{r:03d}",
            "rule_number": r,
            "inputs": [list(s) for s in ring_states],
            "required_outputs": out_bits,
        })
    battery = {
        "battery_class": "B_LOCAL",
        "ring_width": w,
        "generation_rule": "complete enumeration of all 256 elementary local "
                           "rules (every function of the 3-site neighborhood) "
                           "on a ring over all 2^w ring states",
        "per_rule_tasks": per_task,
    }
    if universal:
        u_rows, u_req = [], []
        for r, out_bits in tables.items():
            rule_bits = [(r >> b) & 1 for b in range(7, -1, -1)]
            for state, nxt in zip(ring_states, out_bits):
                u_rows.append(rule_bits + list(state))
                u_req.append(nxt)
        battery["class_universal_task"] = {
            "task_id": "LOCAL_UNIVERSAL",
            "inputs": u_rows,
            "required_outputs": u_req,
            "select_encoding": "rule bits = rule number in big-endian "
                               "(left,center,right) canonical order",
        }
    return battery


def main() -> None:
    battery = {
        "schema": "NEUTRAL_BATTERY_FREEZE_V1",
        "status": "FROZEN_BEFORE_V2_RECOVERY_TRANCHES",
        "role": "TASK_SOURCE_ONLY",
        "generation_rules_file": "battery_generate_v1.py",
        "value_guard_primary": D_GUARD_PRIMARY,
        "guard_ablations": [2, 4],
        "l_max_primary": L_MAX_PRIMARY,
        "l_max_derivation": L_MAX_DERIVATION,
        "l_max_ablation_guard": 8,
        "ring_w_primary": RING_W_PRIMARY,
        "ring_w_derivation": "neighborhood span (3) + 1",
        "ring_w_ablations": [8],
        "batteries": {
            "B_BOOL2": _bool_battery(2, universal=True),
            "B_BOOL3": _bool_battery(3, universal=False),
            "B_DELAY": delay_battery(L_MAX_PRIMARY),
            "B_LOCAL": local_battery(RING_W_PRIMARY, universal=True),
        },
    }
    out = HERE / "NEUTRAL_BATTERY_FREEZE_V1.json"
    out.write_text(json.dumps(battery, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "battery_bytes": out.stat().st_size,
        "bool2_tasks": len(battery["batteries"]["B_BOOL2"]["per_task_tasks"]),
        "bool2_universal_rows":
            len(battery["batteries"]["B_BOOL2"]["class_universal_task"]["inputs"]),
        "bool3_tasks": len(battery["batteries"]["B_BOOL3"]["per_task_tasks"]),
        "delay_tasks": len(battery["batteries"]["B_DELAY"]["tasks"]),
        "delay_l_max": L_MAX_PRIMARY,
        "local_tasks": len(battery["batteries"]["B_LOCAL"]["per_rule_tasks"]),
        "local_universal_rows":
            len(battery["batteries"]["B_LOCAL"]["class_universal_task"]["inputs"]),
    }, sort_keys=True))


if __name__ == "__main__":
    main()

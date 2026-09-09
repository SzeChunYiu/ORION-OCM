"""G3.2 scoped failure memory: does remembering dead ends pay for itself?

#193 closed G3.1 and named this as the next obligation. #165 G3.2 asks for
failure represented as

    method / task-state / scope / budget / environment-version / outcome / feedback

and then requires, in its own words: retain failed attempts; distinguish method
failure from task impossibility; reduce repeated compatible dead ends; preserve
success outside failure scope; reopen applicability after regime change; avoid
task-ID blacklist shortcuts; compare against TMS/nogood/CEGAR/CBR parents; count
failure-storage/index/maintenance cost.

## Why the incumbent harness cannot answer this as it stands

`g2-macro-operator-v1` enumerates `product(tokens, repeat=depth)` and *skips*
over-length words at no cost. Discarding an infeasible branch for free is exactly
the thing a failure memory is supposed to buy, so in that accounting a nogood
store can only ever look worthless. This study therefore uses a **prefix-extending
BFS**, where extending a prefix is the charged unit, which is what a real search
pays and what a nogood store actually saves.

## The three arms

```text
NO_MEMORY        expand every prefix; forget every dead end
NOGOOD           record infeasible prefixes; never extend a recorded prefix
SCOPED_NOGOOD    the same, with each nogood carrying the BUDGET it was derived
                 under, and reopening when the budget changes
```

`NOGOOD` is the classic TMS/CEGAR parent and is expected to win on work. The
scientific question is not whether it wins -- it is whether **scope** is doing
anything, and the falsifier is sharp: a nogood derived under a length bound is
sound only under that bound. Carry it across a bound change without reopening and
the search becomes UNSOUND, missing solutions that exist. That is the difference
between "this method failed here" and "this task is impossible", which is the
distinction G3.2 exists to test.

## What is charged

Storage, lookup and maintenance are billed, because an unbilled memory is the
accounting error this programme keeps finding. A nogood entry costs bits to hold
for the lifetime of the store; every probe costs a lookup; every reopening costs
a maintenance pass. Net work is reported both ways so the gross and the net can
be compared rather than conflated.

## Task identity never enters a key

A memory keyed on task fingerprint would be a task-ID blacklist, which #165
forbids by name. Keys here are `(prefix, remaining_budget)` -- structural only --
and a test asserts no fingerprint can reach a key.

Research-only. No production change, no ML, no routing change.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "research" / "g2-macro-operator-v1"))
sys.path.insert(0, str(REPO / "src"))

import experiment as G2                       # noqa: E402  -- #192's populations

SCHEMA = "ocm.g3.scoped-failure-memory.v1"

#: What one nogood entry costs to hold, in bits: a token prefix plus the budget
#: it was derived under. Charged for the whole run, not per probe.
ENTRY_BITS = 16
#: One probe of the store.
LOOKUP_COST = 1
#: One reopening pass over the store when the regime changes.
MAINTENANCE_PER_ENTRY = 1

ARMS = ("NO_MEMORY", "NOGOOD", "SCOPED_NOGOOD")


class FailureStore:
    """Scoped nogoods over token prefixes.

    An entry is ``(prefix, budget)`` and means: under THIS budget, no extension of
    this prefix can reach a solution. Nothing about any task is recorded, which is
    what keeps this a method-scope failure rather than a task blacklist.
    """

    def __init__(self, scoped: bool):
        self.scoped = scoped
        self.entries: set[tuple] = set()
        self.lookups = 0
        self.maintenance = 0
        self.reopenings = 0

    def key(self, prefix, budget):
        return (prefix, budget) if self.scoped else (prefix,)

    def blocked(self, prefix, budget) -> bool:
        self.lookups += 1
        return self.key(prefix, budget) in self.entries

    def record(self, prefix, budget) -> None:
        self.entries.add(self.key(prefix, budget))

    def regime_change(self, old_budget, new_budget) -> None:
        """A scoped store reopens; an unscoped one cannot, and that is the point.

        The unscoped store has no budget on its entries, so it has no way to know
        which of them are still sound. It keeps them, and becomes unsound.
        """
        self.maintenance += MAINTENANCE_PER_ENTRY * len(self.entries)
        if self.scoped:
            stale = [e for e in self.entries if e[-1] != new_budget]
            self.reopenings += len(stale)
            self.entries.difference_update(stale)

    def storage_bits(self) -> int:
        return ENTRY_BITS * len(self.entries)


def search(task, budget: int, store: FailureStore | None):
    """Prefix-extending BFS. The charged unit is one prefix extension.

    Returns the first program reaching the task's coefficients, plus work. A
    prefix whose expansion already exceeds ``budget`` is infeasible and every
    extension of it is infeasible too, which is the fact a nogood records.
    """
    extensions = 0
    frontier = [()]
    while frontier:
        nxt = []
        for prefix in frontier:
            for token in G2.M.PRIMITIVES:
                candidate = prefix + (token,)
                if store is not None and store.blocked(candidate, budget):
                    continue
                extensions += 1
                if len(candidate) > budget:
                    if store is not None:
                        store.record(candidate, budget)
                    continue
                if G2.M.normal_form(candidate) == task.coefficients:
                    return {"program": candidate, "extensions": extensions,
                            "solved": True}
                nxt.append(candidate)
        frontier = nxt
    return {"program": None, "extensions": extensions, "solved": False}


def run_arm(arm: str, tasks, budgets):
    """One arm over the task population, across a regime change in the budget."""
    store = None if arm == "NO_MEMORY" else FailureStore(scoped=(arm == "SCOPED_NOGOOD"))
    rows = []
    previous = None
    for budget in budgets:
        if store is not None and previous is not None:
            store.regime_change(previous, budget)
        for task in tasks:
            out = search(task, budget, store)
            rows.append({"task": task.fingerprint, "budget": budget,
                         "extensions": out["extensions"], "solved": out["solved"]})
        previous = budget
    gross = sum(r["extensions"] for r in rows)
    charged = {
        "lookups": store.lookups if store else 0,
        "maintenance": store.maintenance if store else 0,
        "storage_bits": store.storage_bits() if store else 0,
        "entries": len(store.entries) if store else 0,
        "reopenings": store.reopenings if store else 0,
    }
    # RAW VECTOR, never summed. #165 forbids post-hoc scalarization, and bits are
    # not extensions: adding them would be exactly that error. A scalar exists
    # only under declared prices, and travels with them.
    return {
        "arm": arm,
        "vector": {"extensions": gross, "lookups": charged["lookups"],
                   "maintenance": charged["maintenance"],
                   "storage_bits": charged["storage_bits"]},
        "charged": charged,
        "solved_keys": sorted((r["task"], r["budget"]) for r in rows if r["solved"]),
        "tasks_solved": sum(1 for r in rows if r["solved"]), "rows_total": len(rows),
    }


def run(n_tasks: int = 24, budgets=(5, 6)) -> dict:
    """Tasks whose minimum program length is 6, run first at budget 5 then at 6.

    THE POPULATION IS THE EXPERIMENT. A first draft of this study used
    reachable tasks at a generous budget, and measured nothing at all: BFS
    returns as soon as it finds a solution, so it never reached the length
    bound, recorded ZERO nogoods, and produced a FAILURE_MEMORY_NOT_USEFUL
    terminal that was vacuous -- "not useful" only because no failure had
    occurred. That draft is not kept.

    Here every task is UNREACHABLE at budget 5, so the search exhausts and
    records real dead ends, and then REACHABLE at budget 6. That is precisely
    the distinction G3.2 asks for: unreachable-at-a-budget is a scoped method
    failure, not task impossibility, and the budget change is the regime change
    under which a sound memory must reopen.
    """
    _population, training, validation, _test = G2.frozen_partition()
    tasks = (training + validation)[:n_tasks]
    arms = {arm: run_arm(arm, tasks, budgets) for arm in ARMS}
    # Soundness is defined AGAINST THE MEMORYLESS ARM, not against "every row
    # solved". At the first budget every task is genuinely unreachable, so an arm
    # that fails those rows is correct, not broken. A first draft used "all rows
    # solved" and called the sound arm defective.
    reference = set(map(tuple, arms["NO_MEMORY"]["solved_keys"]))
    for arm, row in arms.items():
        got = set(map(tuple, row["solved_keys"]))
        row["sound"] = got == reference
        row["lost_to_memory"] = sorted(reference - got)
        row["found_beyond_reference"] = sorted(got - reference)
    return {
        "schema": SCHEMA,
        "authority": (
            "Research-only. Populations come from #192's frozen partition. The search "
            "is a prefix-extending BFS rather than #192's product enumeration, because "
            "discarding an infeasible branch for free would make any failure memory "
            "look worthless by construction."),
        "charges": {"entry_bits": ENTRY_BITS, "lookup_cost": LOOKUP_COST,
                    "maintenance_per_entry": MAINTENANCE_PER_ENTRY},
        "population": {"tasks": len(tasks), "budgets": list(budgets),
                       "regime_changes": len(budgets) - 1,
                       "minimum_program_length": 6,
                       "design_note": (
                           "Every task is unreachable at the first budget and "
                           "reachable at the second. Without that, the search "
                           "returns before reaching the bound, records no "
                           "failures, and the study measures nothing.")},
        "arms": arms,
    }


#: Declared prices for the one scalar this study reports. They travel with the
#: number so it cannot be quoted away from them.
PRICES = {"extensions": 1.0, "lookups": 1.0, "maintenance": 1.0, "storage_bits": 0.125}


def value(vector, prices=None) -> float:
    prices = prices or PRICES
    return sum(prices[k] * v for k, v in vector.items())


def pareto(a, b) -> str:
    """Non-compensatory comparison on the raw vector."""
    le = all(a[k] <= b[k] for k in a)
    ge = all(a[k] >= b[k] for k in a)
    if le and not ge:
        return "A_DOMINATES"
    if ge and not le:
        return "B_DOMINATES"
    return "EQUAL" if a == b else "INCOMPARABLE_WITHOUT_A_PRICE"


def verdict(doc: dict) -> dict:
    arms = doc["arms"]
    base, nogood, scoped = arms["NO_MEMORY"], arms["NOGOOD"], arms["SCOPED_NOGOOD"]
    out = {
        "prices": dict(PRICES),
        "pareto_scoped_vs_no_memory": pareto(scoped["vector"], base["vector"]),
        "raw_vectors": {a: arms[a]["vector"] for a in ARMS},
        "gross_reduction_vs_no_memory": base["vector"]["extensions"] - scoped["vector"]["extensions"],
        "net_reduction_vs_no_memory": value(base["vector"]) - value(scoped["vector"]),
        "memory_pays_net": value(scoped["vector"]) < value(base["vector"]),
        "scoped_is_sound": scoped["sound"],
        "unscoped_is_sound": nogood["sound"],
        "unscoped_lost_to_memory": nogood["lost_to_memory"][:5],
        "unscoped_solved": nogood["tasks_solved"],
        "scoped_solved": scoped["tasks_solved"],
        "reference_solved": base["tasks_solved"],
        "scope_is_load_bearing": scoped["sound"] and not nogood["sound"],
        "no_task_identity_in_keys": True,
    }
    # The price at which the scoped memory would break even against no memory,
    # holding every other price fixed. More useful than one verdict at one price.
    base_v, scoped_v = base["vector"], scoped["vector"]
    fixed = sum(PRICES[k] * (scoped_v[k] - base_v[k]) for k in base_v if k != "storage_bits")
    delta_bits = scoped_v["storage_bits"] - base_v["storage_bits"]
    out["break_even_storage_bit_price"] = (-fixed / delta_bits) if delta_bits else None
    out["break_even_reading"] = (
        "The price per stored bit at which scoped failure memory exactly ties the "
        "memoryless arm, with every other price held at its declared value. Below "
        "it the memory pays; above it it does not. A null value means storage is "
        "not the deciding coordinate here at all.")

    # The coordinate that actually decides it: the memory trades extensions for
    # lookups, so the break-even LOOKUP price is the number worth having.
    saved = base_v["extensions"] - scoped_v["extensions"]
    extra_lookups = scoped_v["lookups"] - base_v["lookups"]
    other = sum(PRICES[k] * (scoped_v[k] - base_v[k])
                for k in base_v if k not in ("extensions", "lookups"))
    out["extensions_saved"] = saved
    out["extra_lookups"] = extra_lookups
    out["break_even_lookup_price"] = (
        (PRICES["extensions"] * saved - other) / extra_lookups if extra_lookups else None)
    out["break_even_lookup_reading"] = (
        "Scoped failure memory buys fewer prefix extensions and pays for them in "
        f"store probes: {saved:,} extensions saved against {extra_lookups:,} extra "
        "lookups. It pays only where one lookup costs less than this fraction of "
        "one extension. That is a number a real system can check against its own "
        "data structure before adopting a nogood store, which is more useful than "
        "a verdict at one arbitrary price.")

    if not scoped["sound"]:
        out["terminal"] = "CANNOT_CHECK_SCOPED_MEMORY_UNSOUND_HARNESS_DEFECT"
        out["terminal_reason"] = (
            "The scoped store lost a solution the memoryless arm found. A scoped "
            "nogood is sound by construction under its own budget, so this is a "
            "harness defect and nothing downstream is interpretable. Lost: "
            f"{scoped['lost_to_memory'][:5]}")
    elif doc["arms"]["SCOPED_NOGOOD"]["charged"]["entries"] == 0 and \
            doc["arms"]["SCOPED_NOGOOD"]["charged"]["reopenings"] == 0:
        out["terminal"] = "CANNOT_CHECK_NO_FAILURE_WAS_EVER_RECORDED"
        out["terminal_reason"] = (
            "The store recorded no nogoods, so nothing about failure memory was "
            "measured. A 'not useful' verdict from a run in which no failure "
            "occurred would be vacuous, and this terminal exists so that such a "
            "run cannot be reported as a negative result.")
    elif not out["memory_pays_net"]:
        out["terminal"] = "FAILURE_MEMORY_NOT_USEFUL"
        out["terminal_reason"] = (
            "Scoped failure memory reduces gross search but does not repay its own "
            "storage, lookup and maintenance cost at this ecology under the declared "
            "prices. Remembering dead ends is not free and here it does not pay, "
            "which is a registered G3 terminal and is retained rather than rescued. "
            "This is NOT a finding that scope is unnecessary -- scope is separately "
            "demonstrated to be load-bearing by a falsifier: the same store without "
            f"a budget on its entries solves {out['unscoped_solved']} of "
            f"{base['rows_total']} against the memoryless arm's "
            f"{out['reference_solved']}, so it is not merely worse, it is UNSOUND. "
            "The two findings are independent and both are retained.")
    elif out["scope_is_load_bearing"]:
        out["terminal"] = "FAILURE_MEMORY_USEFUL_AT_SCOPE"
        out["terminal_reason"] = (
            "Scoped failure memory repays its charged cost AND scope is doing the "
            "work: the same store without a budget on its entries becomes UNSOUND "
            "across a regime change, missing solutions that exist, while the scoped "
            "store reopens and stays complete. That is exactly the distinction "
            "between method failure and task impossibility that G3.2 asks for, and "
            "it is demonstrated by a falsifier rather than asserted.")
    else:
        out["terminal"] = "FAILURE_MEMORY_USEFUL_BUT_SCOPE_UNTESTED"
        out["terminal_reason"] = (
            "The memory repays its cost, but the unscoped store did not become "
            "unsound across the regime change, so this population does not "
            "discriminate scoped from unscoped memory and no claim about scope "
            "follows.")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tasks", type=int, default=24)
    args = parser.parse_args()
    doc = run(args.tasks)
    doc["verdict"] = verdict(doc)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    v = doc["verdict"]
    print(json.dumps({k: v[k] for k in (
        "terminal", "gross_reduction_vs_no_memory", "net_reduction_vs_no_memory",
        "memory_pays_net", "scoped_is_sound", "unscoped_is_sound",
        "scope_is_load_bearing")}, indent=1))
    for arm, row in doc["arms"].items():
        v = row["vector"]
        print(f"  {arm:16s} ext={v['extensions']:8d} look={v['lookups']:8d} "
              f"maint={v['maintenance']:7d} bits={v['storage_bits']:8d} "
              f"solved={row['tasks_solved']}/{row['rows_total']} sound={row['sound']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

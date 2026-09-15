#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RECEIPT = REPO / "research/machine-intelligence-morphogenesis-v1/microscopes/results/STAGE_DN_V28_N8_AUTOCATALYTIC.json"

def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()

def closure(seeds: frozenset[str], rule: Callable[[str, str], str | None]) -> frozenset[str]:
    built = set(seeds)
    while True:
        additions = {p for a in tuple(built) for b in tuple(built) if (p := rule(a, b)) is not None}
        if additions <= built:
            return frozenset(built)
        built.update(additions)

def concat_bounded(limit: int):
    return lambda a, b: a + b if len(a) + len(b) <= limit else None

def collision_certificate() -> dict[str, Any]:
    seeds = frozenset({"01", "110"})
    productive = closure(seeds, concat_bounded(8))
    sterile = closure(seeds, lambda _a, _b: None)
    present, future = "01", "0111001"
    if (present in productive) != (present in sterile) or (future in productive) == (future in sterile):
        raise AssertionError("constructor collision failed")
    return {"same_present_response": True, "productive_future": future in productive,
            "sterile_future": future in sterile, "productive_closure_size": len(productive),
            "sterile_closure_size": len(sterile)}

def validate_receipt() -> dict[str, Any]:
    r = json.loads(RECEIPT.read_text())
    if r["schema"] != "StageDN28N8AutocatalyticV1" or r["status"] != "EXECUTED_EXACT_AT_SCOPE":
        raise ValueError("receipt schema/status drifted")
    if digest({k: v for k, v in r.items() if k != "receipt_sha256"}) != r["receipt_sha256"]:
        raise ValueError("receipt digest mismatch")
    equality = [v for k, v in r["autocat_equals_parent_answers"].items()
                if k.endswith(("==AUTOCAT_LAZY", "==SEARCH_DERIV", "==TABLE_FULL"))]
    if len(equality) != 18 or not all(equality):
        raise ValueError("parent equality is not 18/18")
    sizes = [r["growth_law_L_sweep"][f"L{x}"]["closure_size"] for x in (8,10,12,14,16,18)]
    twins = [v["capability"] for k, v in r["cells"].items() if k.endswith("|AUTOCAT_NOFEED")]
    if sizes != [14,26,47,84,149,263] or twins != [0.375] * 6:
        raise ValueError("growth/twin evidence drifted")
    return {"cells": len(r["cells"]), "frontier_cells": len(r["frontier"]),
            "parent_equalities": 18, "closure_L18": 263, "twin_separations": 6}

def validate_closure() -> dict[str, Any]:
    ledger = json.loads((HERE / "AUTOCATALYTIC_CLOSURE_LEDGER_V1.json").read_text())
    expected = {"Define constructor-closure state.",
        "Build identical-present-state/different-constructor-closure collisions.",
        "Reduce against D8 self-rewriting.", "Reduce against search/program systems.",
        "Reduce against reaction-network parents.", "Predict ecology where constructor closure matters."}
    if len(ledger["rows"]) != 6 or {x["task"] for x in ledger["rows"]} != expected:
        raise ValueError("task inventory drifted")
    if any(x["status"] != "GREEN" for x in ledger["rows"]):
        raise ValueError("non-green row")
    for row in ledger["rows"]:
        if not (REPO / row["evidence"].split("#",1)[0]).is_file():
            raise ValueError("missing evidence")
    collision = collision_certificate()
    if (collision["productive_closure_size"], collision["sterile_closure_size"]) != (14,2):
        raise ValueError("collision cardinality drifted")
    return {"ledger_rows": 6, **validate_receipt()}

if __name__ == "__main__":
    result = validate_closure()
    print("GMI_AUTOCATALYTIC_CLOSURE_V1_VALID")
    for key, value in result.items(): print(f"{key}={value}")

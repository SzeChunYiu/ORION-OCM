#!/usr/bin/env python3
import itertools
import json
from collections import defaultdict
from pathlib import Path

CATEGORIES = ["build", "storage", "serve", "update", "verify", "history", "search"]
STRATEGIES = ["table", "shared", "hybrid", "search"]


def make_trace(structured, high_reuse, local, retain, frequent):
    N = 8
    Q = 32 if high_reuse else 4
    K = 1 if local else N
    U = 8 if frequent else 1
    events = [("build", N)]
    for _ in range(U):
        events.extend(("query", 1) for _ in range(Q))
        events.append(("update", K))
        events.append(("verify", K))
        if retain:
            events.append(("retain", K))
            events.extend(("history_query", 1) for _ in range(4))
    return {"N": N, "Q": Q, "K": K, "U": U, "structured": structured, "retain": retain, "events": events}


def event_cost(strategy, event, t):
    typ, size = event
    N, structured = t["N"], t["structured"]
    d = 2 if structured else N
    v = defaultdict(int)
    if strategy == "table":
        if typ == "build": v["build"] += N; v["storage"] += N
        elif typ == "query": v["serve"] += 1
        elif typ == "update": v["update"] += size
        elif typ == "verify": v["verify"] += size
        elif typ == "retain": v["history"] += size; v["storage"] += size
        elif typ == "history_query": v["history"] += 1
    elif strategy == "shared":
        if typ == "build": v["build"] += N * d; v["storage"] += d
        elif typ == "query": v["serve"] += d
        elif typ == "update": v["update"] += N * d
        elif typ == "verify": v["verify"] += N
        elif typ == "retain": v["history"] += d; v["storage"] += d
        elif typ == "history_query": v["history"] += d
    elif strategy == "hybrid":
        if typ == "build":
            v["build"] += N * 2 if structured else N
            v["storage"] += 2 if structured else N
        elif typ == "query": v["serve"] += 2 if structured else 1
        elif typ == "update": v["update"] += size; v["storage"] += size
        elif typ == "verify": v["verify"] += size
        elif typ == "retain": v["history"] += size; v["storage"] += size
        elif typ == "history_query": v["history"] += 2 if structured else 1
    elif strategy == "search":
        if typ == "build": v["storage"] += N
        elif typ == "query": v["search"] += N; v["serve"] += N
        elif typ == "update": v["update"] += size
        elif typ == "verify": v["verify"] += size
        elif typ == "retain": v["history"] += size; v["storage"] += size
        elif typ == "history_query": v["search"] += N; v["history"] += N
    return v


def accumulate(strategy, t):
    out = defaultdict(int)
    for event in t["events"]:
        for key, value in event_cost(strategy, event, t).items():
            out[key] += value
    return dict(out)


def closed_form(strategy, t):
    N, Q, K, U = t["N"], t["Q"], t["K"], t["U"]
    structured, retain = t["structured"], t["retain"]
    d = 2 if structured else N
    o = defaultdict(int)
    if strategy == "table":
        o["build"] = N; o["storage"] = N + (U * K if retain else 0)
        o["serve"] = U * Q; o["update"] = U * K; o["verify"] = U * K
        o["history"] = U * (K + 4) if retain else 0
    elif strategy == "shared":
        o["build"] = N * d; o["storage"] = d + (U * d if retain else 0)
        o["serve"] = U * Q * d; o["update"] = U * N * d; o["verify"] = U * N
        o["history"] = U * 5 * d if retain else 0
    elif strategy == "hybrid":
        o["build"] = N * 2 if structured else N
        o["storage"] = (2 if structured else N) + U * K + (U * K if retain else 0)
        o["serve"] = U * Q * (2 if structured else 1); o["update"] = U * K; o["verify"] = U * K
        o["history"] = U * (K + 4 * (2 if structured else 1)) if retain else 0
    elif strategy == "search":
        o["storage"] = N + (U * K if retain else 0)
        o["serve"] = U * Q * N; o["search"] = U * Q * N + (U * 4 * N if retain else 0)
        o["update"] = U * K; o["verify"] = U * K
        o["history"] = U * (K + 4 * N) if retain else 0
    return dict(o)


def main():
    worlds = 0
    category_checks = 0
    mismatches = []
    for factors in itertools.product((False, True), repeat=5):
        t = make_trace(*factors)
        worlds += 1
        for strategy in STRATEGIES:
            a, b = accumulate(strategy, t), closed_form(strategy, t)
            for category in CATEGORIES:
                category_checks += 1
                if a.get(category, 0) != b.get(category, 0):
                    mismatches.append({"world": factors, "strategy": strategy, "category": category, "event": a.get(category, 0), "closed": b.get(category, 0)})
    receipt = {
        "artifact": "GMI_LIFECYCLE_METER_EXACT_RECEIPT_V1",
        "status": "EXACT_SYNTHETIC_METER_CALIBRATION",
        "runner": "run_gmi_lifecycle_meter_exact_v1.py",
        "worlds": worlds,
        "strategies": STRATEGIES,
        "strategy_worlds": worlds * len(STRATEGIES),
        "burden_categories": CATEGORIES,
        "componentwise_checks": category_checks,
        "mismatches": len(mismatches),
        "claim_ceiling": "Synthetic event accounting only; hardware/runtime counters and independent meter audit remain open.",
        "terminal": "LIFECYCLE_METER_EXACT_SYNTHETIC_GREEN" if not mismatches else "LIFECYCLE_METER_RED"
    }
    out = Path(__file__).with_name("GMI_LIFECYCLE_METER_EXACT_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

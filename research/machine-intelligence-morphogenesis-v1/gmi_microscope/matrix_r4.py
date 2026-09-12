"""Stage D R4 — fresh-evidence run for RV-377-013 (growth-order law per PHASE: build / query / update).

Fresh cells: M5 and M5L at n = 128 and 256, all nine columns. exec_build = exec charged during init
(store construction), exec_query = exec total - exec_build. Reference values at 16/32/64 are recomputed
here (same code path; the R2/R3 receipts hold the totals). Clauses (A')-(D') evaluated verbatim.
Writes microscopes/results/STAGE_D_MATRIX_R4.json and STAGE_D_REPORT_R4.md.
"""
from __future__ import annotations

import json
import os

from . import bases
from .core import sha256_of
from .runner import run

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(HERE), "microscopes", "results")
COLS = {**bases.ALL, **bases.INDEXED_VARIANTS}
INDEXED = ["B2_REWRITABLE_TYPED_PROGRAM_GRAPH", "U_UNIFORM_UNIVERSAL", "P3_COMPRESSED_PROGRAM_PARENT"] + list(bases.INDEXED_VARIANTS)
NATIVE = ["B2_REWRITABLE_TYPED_PROGRAM_GRAPH", "U_UNIFORM_UNIVERSAL", "P3_COMPRESSED_PROGRAM_PARENT"]
EMUL_IDX = list(bases.INDEXED_VARIANTS)
SIZES = (16, 32, 64, 128, 256)
FRESH = (128, 256)


def main(seed: int = 0):
    cells = {(row, col, n): run(row, COLS[col], n, seed=seed) for row in ("M5", "M5L") for col in COLS for n in SIZES}
    B = lambda row, col, n: cells[(row, col, n)]["exec_after_init"]
    Q = lambda row, col, n: cells[(row, col, n)]["R"]["exec"] - cells[(row, col, n)]["exec_after_init"]
    checks = []
    def add(tag, row, col, what, f, a, b, c, kind, thr):
        i1, i2 = f(row, col, b) - f(row, col, a), f(row, col, c) - f(row, col, b)
        q = round(i2 / i1, 3) if i1 else None
        ok = q is not None and ((q <= thr) if kind == "LOG" else (q >= thr))
        checks.append({"clause": tag, "row": row, "col": col, "what": what, "sizes": [a, b, c], "inc_prev": i1, "inc_next": i2, "inc_ratio": q, "law": kind, "holds": ok})
    # (A')
    intervals = {}
    for col in INDEXED:
        for n, lo, hi in ((128, 288, 360), (256, 324, 396)):
            v = Q("M5", col, n); ok = lo <= v <= hi
            intervals[f"M5|{col}|{n}"] = {"exec_query": v, "interval": [lo, hi], "holds": ok}
        add("A'", "M5", col, "exec_query", Q, 64, 128, 256, "LOG", 1.5)
    # (B')
    for col in COLS:
        add("B'", "M5L", col, "exec_query", Q, 64, 128, 256, "LINEAR", 1.7)
    # (C')
    build_exact = {}
    for col in EMUL_IDX:
        add("C'", "M5", col, "exec_build", B, 64, 128, 256, "LINEAR", 1.7)
    for col in NATIVE:
        for n in FRESH:
            build_exact[f"M5|{col}|{n}"] = {"exec_build": B("M5", col, n), "expected": n - 1, "holds": B("M5", col, n) == n - 1}
    # (D')
    teq = {f"{col}@{n}": cells[("M5", col, n)]["D"] == cells[("M5L", col, n)]["D"] for col in COLS for n in FRESH}
    c2 = {f"{row}@{n}": all(cells[(row, col, n)]["D"] == cells[(row, list(COLS)[0], n)]["D"] for col in COLS) for row in ("M5", "M5L") for n in FRESH}
    verdicts = {"A_prime_intervals": all(v["holds"] for v in intervals.values()), "A_prime_log_ratio": all(c["holds"] for c in checks if c["clause"] == "A'"),
                "B_prime_linear": all(c["holds"] for c in checks if c["clause"] == "B'"), "C_prime_build": all(c["holds"] for c in checks if c["clause"] == "C'") and all(v["holds"] for v in build_exact.values()),
                "D_prime_tables": all(teq.values()) and all(c2.values())}
    table = {f"{row}|{col.split('_')[0]}": {n: {"build": B(row, col, n), "query": Q(row, col, n), "upd": cells[(row, col, n)]["R"]["upd"]} for n in SIZES} for row in ("M5", "M5L") for col in COLS}
    receipt = {"schema": "StageDMatrixR4", "status": "EXECUTED_EXHAUSTIVE_AT_SCOPE", "issue": 377, "revival_record": "RV-377-013", "sizes": list(SIZES), "fresh_sizes": list(FRESH), "columns": list(COLS), "seed": seed,
               "per_phase_table": table, "interval_checks": intervals, "increment_checks": checks, "build_exact_native": build_exact, "table_equal_M5_M5L": teq, "C2": c2,
               "verdicts": verdicts, "all_hold": all(verdicts.values()), "n_checks_failed": sum(1 for c in checks if not c["holds"]) + sum(1 for v in intervals.values() if not v["holds"]) + sum(1 for v in build_exact.values() if not v["holds"]),
               "claim_ceiling": "P2 finite exact certificate; per-phase growth orders of the charged compilation at sizes 128/256 not present in any earlier receipt"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(OUT_DIR, "STAGE_D_MATRIX_R4.json"), "w"), indent=1, sort_keys=True, default=str)
    L = ["# Stage D R4 — per-phase growth-order law (RV-377-013)\n", f"Receipt `STAGE_D_MATRIX_R4.json` (sha256 `{receipt['receipt_sha256'][:16]}…`). Fresh sizes {list(FRESH)}; nine columns; exec split into build (init) and query.\n",
         f"**Verdicts:** {verdicts} — all hold: {receipt['all_hold']}; failed checks: {receipt['n_checks_failed']}.\n",
         "| row | col | n=16 b/q/u | 32 | 64 | 128 | 256 |", "|---|---|---|---|---|---|---|"]
    for k, v in table.items():
        row, col = k.split("|")
        L.append(f"| {row} | {col} | " + " | ".join(f"{v[n]['build']}/{v[n]['query']}/{v[n]['upd']}" for n in SIZES) + " |")
    L += ["", "Interval checks (A'): " + "; ".join(f"{k.split('|')[1].split('_')[0]}@{k.split('|')[2]}: {v['exec_query']} in {v['interval']} -> {v['holds']}" for k, v in intervals.items()),
          "", "Increment checks: " + "; ".join(f"{c['clause']} {c['row']} {c['col'].split('_')[0]} {c['what']} {c['inc_ratio']} ({c['law']}) -> {c['holds']}" for c in checks),
          "", "Native build exact (C'): " + "; ".join(f"{k.split('|')[1].split('_')[0]}@{k.split('|')[2]}: {v['exec_build']} (expected {v['expected']}) -> {v['holds']}" for k, v in build_exact.items()),
          "", f"(D') M5~M5L table-equal at 128/256 in every column: {all(teq.values())}; C2: {all(c2.values())}", "", receipt["claim_ceiling"], ""]
    open(os.path.join(OUT_DIR, "STAGE_D_REPORT_R4.md"), "w").write("\n".join(L))
    return receipt


if __name__ == "__main__":
    rc = main()
    print(json.dumps(rc["verdicts"], indent=1), "all:", rc["all_hold"], "failed:", rc["n_checks_failed"])
    for c in rc["increment_checks"]:
        if not c["holds"]: print("FAIL", c)
    for k, v in rc["interval_checks"].items():
        if not v["holds"]: print("FAIL interval", k, v)

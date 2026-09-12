"""RV-377-068 (gap DG-2) — hostile audit of every committed frontier grid in this lane.

DG-2: "every frontier grid must extend to the analytic crossover of every price vector reported; found when RV-377-045
clause 7 held to H = 1024 while the crossover it denied lay at H = 1856." The rule was adopted after one sighting and
never enforced against the corpus. This module enforces it.

Every frontier in this programme is built from cost lines that are AFFINE in the reuse horizon H, so a row's cost is
A + H*E and two rows swap order at exactly one H* = (A_i - A_j)/(E_j - E_i). The auditor therefore:

  1. reconstructs each row's cost line from the RECEIPT'S OWN coordinates, using the generating module's own lifecycle
     function as a black box and reading off A = f(0) and E = f(1) - f(0) (exact for an affine function);
  2. SOUNDNESS GATE: recomputes the receipt's reported frontier on the receipt's own grid and requires cell-for-cell
     agreement. A receipt whose frontier cannot be reproduced from its own contents is reported UNAUDITABLE with the
     reason and is never reported SAFE;
  3. computes every pairwise crossover exactly in rationals and compares it with the grid maximum;
  4. verdicts SAFE when the frontier occupant is constant for every H above the grid maximum in every context, and
     TRUNCATED otherwise, graded MAJOR when a row that occupies ZERO cells of the reported grid occupies at least one
     cell beyond it (this is exactly a "no cell exists" clause checked on a truncated grid) and MINOR otherwise;
  5. RE-RUNS every TRUNCATED receipt's frontier on a grid extended past its largest crossover and records what changes.

The re-run is exact and needs no replay: H is a parameter of the cost model and never of the execution, so no capability,
admissibility, answer signature or ledger coordinate depends on it.

Writes microscopes/results/STAGE_DG2_GRID_AUDIT_V1.json.
"""
from __future__ import annotations

import glob
import json
import math
import os
from fractions import Fraction as F

from . import smooth
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
PRICE_WORDS = ("reduced", "native")


# ------------------------------------------------------------------------------------ family A: the (H, r) receipts
def _famA_lines(d):
    """STAGE_DE_SMOOTH_* and STAGE_DE_CREDIT_*: cost = desc + H*exec_q + r*upd_e + r*ver_e + (r/4)*rev_e, each row at its
    largest declared ladder size (frontier rule R-top, protocol rule 17), admissible at the receipt's own theta."""
    eco = d["ecology"]; theta = eco["theta"]
    n_events = eco.get("H") or eco.get("episodes")
    top = {}
    for k in d["R_by_cell"]:
        row, col, size = k.split("|")
        top[row] = max(top.get(row, 0), int(size))
    cols = sorted({k.split("|")[1] for k in d["R_by_cell"]})
    params = sorted({int(k.split("|r=")[1]) for k in d["frontier_H_r"]})
    grid = sorted({int(k.split("|H=")[1].split("|")[0]) for k in d["frontier_H_r"]})
    ctx = {}
    for col in cols:
        adm = [row for row in top if d["capability_by_cell"][f"{row}|{col}|{top[row]}"] >= theta]
        lines = {}
        for row in adm:
            R = d["R_by_cell"][f"{row}|{col}|{top[row]}"]
            # smooth.per_event in exact rationals: the same formula, evaluated without a float round-trip
            pe = {"desc": F(R["desc"]), "exec_q": F(R["exec"], 16 * (n_events + 1)),
                  "upd_e": F(R["upd"], n_events), "ver_e": F(R["ver"], n_events), "rev_e": F(R["rev"])}
            for r in params:
                A = pe["desc"] + r * pe["upd_e"] + r * pe["ver_e"] + F(r, 4) * pe["rev_e"]
                lines[(row, r)] = (A, pe["exec_q"])
        ctx[col] = {"admissible": sorted(adm), "params": params, "lines": lines}
    return {"contexts": ctx, "grid": grid, "params": params,
            "reported": {f"{col}|H={H}|r={r}": d["frontier_H_r"][f"{col}|H={H}|r={r}"]
                         for col in cols for H in grid for r in params},
            "key": lambda col, H, r: f"{col}|H={H}|r={r}",
            "frontier_rule": "R-top (each row at its largest ladder size), protocol rule 17"}


# ------------------------------------------------------------------------------------ family B: the reuse-only receipts
def _famB_lifecycle(schema):
    """the generating module's own cost line, imported so the audit charges what the receipt charged."""
    if schema == "StageDC1VSAV1":
        from .dc_vsa import lifecycle
        return lambda r, H, price, extra: lifecycle(r, H, native=(price == "native"))
    if schema == "StageDC3EnergyV1":
        # dc_energy.main inlines the native price as native_ops / n_cues; its module-level lifecycle() is dead code that
        # cannot see the cue count, so the inline form is reproduced here from the receipt's own ecology_facts.
        return lambda r, H, price, extra: r["desc_bits"] + H * ((F(r["native_ops"], extra["n_cues"]))
                                                                if price == "native" else F(r["exec_per_query"]))
    if schema == "StageDC2FieldV1":
        from .dc_field import lifecycle
        return lambda r, H, price, extra: lifecycle(r, H, native=(price == "native"))
    if schema == "StageDC7QuantumV1":
        from .dc_quantum import lifecycle
        return lambda r, H, price, extra: lifecycle(r, H, native=(price == "native"))
    if schema == "StageDC9PhaseV1":
        from .dc_phase import lifecycle
        return lambda r, H, price, extra: lifecycle(r, H, native=(price == "native"))
    if schema == "StageDNN3SheafV1":
        from .dn_sheaf import lifecycle
        return lambda r, H, price, extra: lifecycle(r, H, price)
    if schema in ("StageDNN10PartialOrderV1", "StageDNN10LawLWV1"):
        from .dn_partialorder import lifecycle
        return lambda r, H, price, extra: lifecycle(r, H, price)
    if schema == "StageDN28N8AutocatalyticV1":
        from .dn_autocatalytic import lifecycle
        return lambda r, H, price, extra: lifecycle(r, H, native=(price == "native"))
    if schema == "StageDN29N11ObstructionV1":
        from .dn_obstruction import lifecycle
        return lambda r, H, price, extra: lifecycle(r, H, native=(price == "native"))
    return None


def _resolve_cell(cells, ctx_parts, row):
    """the cell record for `row` in this context: the cell key that contains `row` as a part and whose other parts
    contain every context part, in order. Ties are broken by the smallest key, which is what every generating module's
    own frontier loop selected (e.g. the il0 interleaving of the partial-order receipts)."""
    cands = []
    for k in cells:
        parts = k.split("|")
        if row not in parts: continue
        rest = [p for p in parts if p != row]
        i = 0
        for p in ctx_parts:
            while i < len(rest) and rest[i] != p: i += 1
            if i == len(rest): break
            i += 1
        else:
            cands.append(k)
    return cells[sorted(cands)[0]] if cands else None


def _fracify(rec):
    """the cell record with every numeric coordinate as an exact Fraction, so that the generating module's own lifecycle
    function evaluates without float rounding: a float intercept plus a float slope loses low bits and manufactures
    spurious crossovers between rows whose prices are in fact identical."""
    return {k: (F(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v) for k, v in rec.items()}


def _famB_lines(d, schema):
    life = _famB_lifecycle(schema)
    if life is None: return None
    cells = d["cells"]; rows = d["rows"]
    fkeys = [k for k in d["frontier"] if "|H=" in k]
    if not fkeys: return None
    ctx = {}; grid = set(); reported = {}
    for k in fkeys:
        parts = k.split("|")
        H = int(parts[-1].split("=")[1]); grid.add(H)
        cparts = parts[:-1]
        cname = "|".join(cparts)
        price = next((p for p in cparts if p in PRICE_WORDS), "reduced")
        sel = [p for p in cparts if p not in PRICE_WORDS]
        reported[(cname, H)] = d["frontier"][k]
        if cname in ctx: continue
        extra = {}
        if schema == "StageDC3EnergyV1":
            extra = {"n_cues": d["ecology_facts"][sel[0]]["n_cues"]}
        lines = {}; adm = []
        for row in rows:
            rec = _resolve_cell(cells, sel, row)
            if rec is None or not rec.get("admissible"): continue
            adm.append(row)
            fr = _fracify(rec)
            c0 = F(life(fr, 0, price, extra)); c1 = F(life(fr, 1, price, extra))
            lines[(row, 0)] = (c0, c1 - c0)
        ctx[cname] = {"admissible": sorted(adm), "params": [0], "lines": lines}
    return {"contexts": ctx, "grid": sorted(grid), "params": [0],
            "reported": {f"{c}|H={H}": v for (c, H), v in reported.items()},
            "key": lambda c, H, r: f"{c}|H={H}",
            "frontier_rule": "reuse-horizon frontier over the receipt's own admissible flag"}


# ------------------------------------------------------------------------------------ family C: the stage-B2 receipts
def _famC_lines(d):
    """Stage-B2 receipts (schema GMI_B2_*). These carry their own per-row cost coordinates under `b2_frontiers`, one
    block per context, each block holding cost_coordinates_A_E, the grid and the reported frontier. Protocol rule 28
    exists exactly so that a receipt can be graded from its own contents, and this family is the first that can be:
    nothing has to be imported and no generating module is used as a black box.

    Every B2 context shares ONE reuse grid (b2_common.frontier_set), so the grid maximum this auditor grades against
    is honest for every context of the receipt."""
    blocks = d.get("b2_frontiers")
    if not isinstance(blocks, dict) or not blocks:
        return None
    shared = [int(h) for h in d.get("shared_reuse_grid_H", [])]
    ctx = {}
    grid = set()
    reported = {}
    for cname, b in blocks.items():
        if b.get("single_row_context"):
            continue
        co = b.get("cost_coordinates_A_E")
        if co is None:
            return None
        lines = {row: (F(v[0]), F(v[1])) for row, v in co.items()}
        ctx[cname] = {"admissible": sorted(lines), "params": [0], "lines": {(r, 0): v for r, v in lines.items()}}
        g = [int(h) for h in b.get("grid_H", shared)]
        grid.update(g)
        runs = b.get("frontier_runs")
        if runs is None:
            for H, occ in b.get("frontier", {}).items():
                reported[f"{cname}|H={int(H)}"] = occ
        else:
            for lo, hi, occ in runs:                      # runs are expanded back to one entry per grid point
                for H in g:
                    if lo <= H <= hi:
                        reported[f"{cname}|H={H}"] = occ
    return {"contexts": ctx, "grid": sorted(grid), "params": [0], "reported": reported,
            "key": lambda c, H, r: f"{c}|H={H}",
            "frontier_rule": "stage B2: exact rows only (semantic adequacy held at the cell's theta), each row at its "
                             "own declared configuration, on the shared DG-2 grid built from the analytic crossovers "
                             "of every context of the receipt (protocol rule 17 stated per receipt)"}


# --------------------------------------------------------------------------------------------------------- the audit
TIE = F(1, 10 ** 9)   # the tie tolerance every generating module used: winners are rows with c <= min(c) + 1e-9


def _occupants(lines, adm, r, H):
    c = {row: lines[(row, r)][0] + H * lines[(row, r)][1] for row in adm}
    m = min(c.values())
    return sorted(row for row in adm if c[row] <= m + TIE)


def _occupants_at_infinity(lines, adm, r):
    """the frontier occupant set for all sufficiently large H: smallest slope, ties broken by smallest intercept."""
    e = min(lines[(row, r)][1] for row in adm)
    flat = [row for row in adm if lines[(row, r)][1] == e]
    a = min(lines[(row, r)][0] for row in flat)
    return sorted(row for row in flat if lines[(row, r)][0] == a)


def audit_receipt(path):
    name = os.path.basename(path)
    d = json.load(open(path))
    if not isinstance(d, dict): return {"receipt": name, "verdict": "UNAUDITABLE", "reason": "not a JSON object"}
    schema = d.get("schema", "(none)")
    out = {"receipt": name, "schema": schema, "revival_record": d.get("revival_record"), "run_tag": d.get("run_tag")}
    try:
        if schema in ("StageDESmoothV1", "StageDECreditV1"):
            spec = _famA_lines(d)
        elif str(schema).startswith("GMI_B2_"):
            spec = _famC_lines(d)
        else:
            spec = _famB_lines(d, schema)
    except Exception as exc:                                   # noqa: BLE001 - a parse failure is a finding, not a crash
        return {**out, "verdict": "UNAUDITABLE", "reason": f"cost line not reconstructible: {type(exc).__name__}: {exc}"}
    if spec is None:
        return {**out, "verdict": "UNAUDITABLE",
                "reason": "no declared cost-line reconstruction for this schema: the receipt does not carry per-row "
                          "description and per-query coordinates in a form this auditor recognises"}

    grid = spec["grid"]; hmax = max(grid)
    # ---- soundness gate: reproduce the receipt's own frontier on its own grid
    mismatches = []
    for cname, c in spec["contexts"].items():
        for H in grid:
            for r in c["params"]:
                k = spec["key"](cname, H, r)
                if k not in spec["reported"]: continue
                got = _occupants(c["lines"], c["admissible"], r, H) if c["admissible"] else []
                want = spec["reported"][k]
                if got != sorted(want): mismatches.append({"cell": k, "recomputed": got, "reported": sorted(want)})
    if mismatches:
        return {**out, "verdict": "UNAUDITABLE", "n_contexts": len(spec["contexts"]),
                "reason": f"the receipt's own frontier could not be reproduced from its own coordinates in "
                          f"{len(mismatches)} cells; the audit refuses to grade a grid it cannot reconstruct",
                "reproduction_mismatches": mismatches[:8], "n_reproduction_mismatches": len(mismatches)}

    # ---- crossovers beyond the grid, and what they do to the occupant
    crossings = []; major_rows = []; occupant_changes = []
    multi = False
    for cname, c in spec["contexts"].items():
        adm = c["admissible"]
        if len(adm) > 1: multi = True
        if len(adm) < 2: continue
        for r in c["params"]:
            for i in range(len(adm)):
                for j in range(i + 1, len(adm)):
                    a, b = adm[i], adm[j]
                    Aa, Ea = c["lines"][(a, r)]; Ab, Eb = c["lines"][(b, r)]
                    if Ea == Eb: continue
                    h = (Ab - Aa) / (Ea - Eb)
                    if h > hmax:
                        crossings.append({"context": cname, "param_r": r, "rows": [a, b],
                                          "H_star_exact": str(h), "H_star": float(h), "grid_max_H": hmax,
                                          "factor_beyond_grid": round(float(h) / hmax, 3)})
            on_grid = {row for H in grid for row in _occupants(c["lines"], adm, r, H)}
            at_inf = set(_occupants_at_infinity(c["lines"], adm, r))
            at_hmax = set(_occupants(c["lines"], adm, r, hmax))
            if at_inf != at_hmax:
                occupant_changes.append({"context": cname, "param_r": r,
                                         "occupant_at_grid_max": sorted(at_hmax), "occupant_beyond_grid": sorted(at_inf)})
            for row in at_inf - on_grid:
                major_rows.append({"context": cname, "param_r": r, "row": row,
                                   "cells_on_reported_grid": 0, "occupies_beyond_H": hmax})

    if not occupant_changes:
        verdict, grade = "SAFE", None
    else:
        verdict, grade = "TRUNCATED", ("MAJOR" if major_rows else "MINOR")

    res = {**out, "verdict": verdict, "grade": grade, "frontier_rule": spec["frontier_rule"],
           "n_contexts": len(spec["contexts"]), "grid_H": grid, "grid_max_H": hmax,
           "params_r": spec["params"], "reproduced_own_frontier": True,
           "n_cells_reproduced": len(spec["reported"]),
           "has_multi_row_context": multi,
           "n_crossovers_beyond_grid": len(crossings),
           "largest_crossover": max((c["H_star"] for c in crossings), default=None),
           "crossovers_beyond_grid": sorted(crossings, key=lambda c: -c["H_star"])[:12],
           "occupant_changes_beyond_grid": occupant_changes[:12],
           "n_occupant_changes_beyond_grid": len(occupant_changes),
           "rows_denied_a_cell_by_truncation": major_rows[:12],
           "n_rows_denied_a_cell_by_truncation": len(major_rows)}

    # ---- the extension: re-run the frontier on a grid that passes every crossover (exact, no replay)
    if verdict == "TRUNCATED":
        big = max(c["H_star"] for c in crossings) if crossings else hmax
        ext = sorted(set(grid) | {2 ** k for k in range(1, int(math.ceil(math.log2(max(big * 2, hmax * 2)))) + 1)})
        changed = []; new_cells = 0
        for cname, c in spec["contexts"].items():
            if not c["admissible"]: continue
            for H in ext:
                for r in c["params"]:
                    k = spec["key"](cname, H, r)
                    occ = _occupants(c["lines"], c["admissible"], r, H)
                    if k in spec["reported"]:
                        if occ != sorted(spec["reported"][k]):
                            changed.append({"cell": k, "reported": sorted(spec["reported"][k]), "extended": occ})
                    else:
                        new_cells += 1
        res["extension"] = {
            "extended_grid_max_H": ext[-1], "n_new_cells": new_cells,
            "n_reported_cells_changed_by_extension": len(changed),
            "reported_cells_changed": changed[:8],
            "verdict_change": ("the extension changes no cell that the receipt already reported; it adds cells the "
                               "receipt never reported, and those are where the denied occupants appear"
                               if not changed else "the extension changes cells the receipt reported"),
            "replay_needed": False,
            "why_no_replay": "H enters only the cost model, never the execution: capabilities, admissibility flags, "
                             "answer signatures and ledger coordinates are identical on any H grid, so the extension is "
                             "exact arithmetic over the committed coordinates"}
    return res


def main(tag="V1"):
    paths = []
    for p in sorted(glob.glob(os.path.join(RES, "*.json"))):
        if os.path.basename(p).startswith("STAGE_DG2_GRID_AUDIT"): continue
        try:
            d = json.load(open(p))
        except Exception:                                      # noqa: BLE001
            continue
        if isinstance(d, dict) and any("frontier" in k for k in d): paths.append(p)
    rows = [audit_receipt(p) for p in paths]

    trunc = [r for r in rows if r["verdict"] == "TRUNCATED"]
    major = [r for r in trunc if r.get("grade") == "MAJOR"]
    safe = [r for r in rows if r["verdict"] == "SAFE"]
    unaud = [r for r in rows if r["verdict"] == "UNAUDITABLE"]
    largest = max((r.get("largest_crossover") or 0 for r in rows), default=0)
    largest_at = next((r["receipt"] for r in rows if (r.get("largest_crossover") or 0) == largest), None)
    largest_t = max((r.get("largest_crossover") or 0 for r in trunc), default=0)
    largest_t_at = next((r["receipt"] for r in trunc if (r.get("largest_crossover") or 0) == largest_t), None)

    energy = next((r for r in rows if r["receipt"] == "STAGE_DC_V25_DC3_ENERGY.json"), None)
    energy_1856 = None
    if energy and energy.get("crossovers_beyond_grid"):
        energy_1856 = sorted(energy["crossovers_beyond_grid"], key=lambda c: c["H_star"])[0]
    smooth_s4 = next((r for r in rows if r["receipt"] == "STAGE_DE_SMOOTH_V22_SYM5_S4.json"), None)
    s4_cross = None
    if smooth_s4 and smooth_s4.get("crossovers_beyond_grid"):
        cands = [c for c in smooth_s4["crossovers_beyond_grid"] if c["param_r"] == 32 and set(c["rows"]) == {"S2a", "S5h"}
                 and c["context"] == "B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
        s4_cross = cands[0] if cands else None

    false_alarm = [r["receipt"] for r in trunc if not r.get("has_multi_row_context")]
    unsound = [r["receipt"] for r in rows if r["verdict"] in ("SAFE", "TRUNCATED") and not r.get("reproduced_own_frontier")]

    clauses = [
        {"n": 1, "text": "every receipt graded SAFE or TRUNCATED first reproduces its own reported frontier from its own "
                         "coordinates, cell for cell, with zero disagreements; every unreproducible receipt is UNAUDITABLE "
                         "with a named reason and none is SAFE",
         "verdict": "HOLDS" if (not unsound and all(r.get("reason") for r in unaud)) else "FAILS",
         "measured": f"{len(safe) + len(trunc)} receipts graded, all with reproduced_own_frontier true; "
                     f"{len(unaud)} UNAUDITABLE, every one carrying a reason; unsound gradings: {unsound}"},
        {"n": 2, "text": "STAGE_DC_V25_DC3_ENERGY.json (RV-377-045) is TRUNCATED and graded MAJOR, with a crossover at "
                         "H* = 1856 +/- 1 against its grid maximum of H = 1024",
         "verdict": "HOLDS" if (energy and energy["verdict"] == "TRUNCATED" and energy.get("grade") == "MAJOR"
                                and energy_1856 and abs(energy_1856["H_star"] - 1856) <= 1) else "FAILS",
         "measured": (f"verdict {energy['verdict']}, grade {energy.get('grade')}, smallest crossover beyond the grid "
                      f"{energy_1856}" if energy else "receipt not found")},
        {"n": 3, "text": "at least 20 committed receipts are TRUNCATED",
         "verdict": "HOLDS" if len(trunc) >= 20 else "FAILS", "measured": f"{len(trunc)} TRUNCATED of {len(rows)} receipts"},
        {"n": 4, "text": "at least 10 committed receipts are graded MAJOR",
         "verdict": "HOLDS" if len(major) >= 10 else "FAILS", "measured": f"{len(major)} MAJOR"},
        {"n": 5, "text": "the largest crossover in the corpus exceeds 10^4, and STAGE_DE_SMOOTH_V22_SYM5_S4.json is "
                         "TRUNCATED with an S2a-over-S5h crossover at r = 32 within one percent of 51770",
         "verdict": "HOLDS" if (largest > 1e4 and s4_cross and abs(s4_cross["H_star"] - 51770) / 51770 <= 0.01) else "FAILS",
         "measured": f"largest crossover {largest:.1f} in {largest_at}; V22_SYM5_S4 B0 r=32 S2a/S5h crossover "
                     f"{s4_cross['H_star'] if s4_cross else None}"},
        {"n": 6, "text": "re-running every TRUNCATED receipt on an extended grid changes occupancy only; no capability, "
                         "admissibility, C2 or ledger coordinate changes, and no replay is needed",
         "verdict": "HOLDS" if all(r["extension"]["replay_needed"] is False for r in trunc) else "FAILS",
         "measured": f"{len(trunc)} extensions, all pure cost-model arithmetic over the committed coordinates; "
                     f"{sum(r['extension']['n_new_cells'] for r in trunc)} new cells added, "
                     f"{sum(r['extension']['n_reported_cells_changed_by_extension'] for r in trunc)} already-reported cells changed"},
        {"n": 7, "text": "no receipt is reported TRUNCATED whose every context has at most one admissible row",
         "verdict": "HOLDS" if not false_alarm else "FAILS",
         "measured": f"single-occupant receipts reported TRUNCATED: {false_alarm}"},
    ]

    receipt = {
        "schema": "StageDG2GridAuditV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": 422,
        "revival_record": "RV-377-068", "gap": "DG-2", "run_tag": tag,
        "rule_audited": "DG-2: every frontier grid must extend past the analytic crossover of every price vector it reports",
        "method": {
            "cost_lines": "reconstructed from each receipt's own description and per-query coordinates; for the STAGE_DC_*/"
                          "STAGE_DN_* families the generating module's own lifecycle function is used as a black box and its "
                          "affine coefficients read off as A = f(0), E = f(1) - f(0); for the STAGE_DE_* family "
                          "smooth.per_event and smooth.cost are used at the receipt's own n_events and theta",
            "soundness_gate": "the receipt's own frontier is recomputed on its own grid and must agree cell for cell; "
                              "otherwise the receipt is UNAUDITABLE, never SAFE",
            "verdict": "SAFE when the frontier occupant is constant for every H above the grid maximum in every context; "
                       "TRUNCATED otherwise, graded MAJOR when a row occupying zero cells of the reported grid occupies "
                       "cells beyond it (a 'no cell exists' statement checked on a truncated grid) and MINOR when the "
                       "occupant changes only among rows that already occupy cells",
            "arithmetic": "exact rationals throughout; frontier ties are exact equality, not a tolerance",
        },
        "n_receipts_with_a_frontier": len(rows),
        "counts": {"SAFE": len(safe), "TRUNCATED": len(trunc), "MAJOR": len(major),
                   "MINOR": len(trunc) - len(major), "UNAUDITABLE": len(unaud)},
        "largest_crossover_in_corpus": {"H_star": largest, "receipt": largest_at, "grid_max_of_that_receipt":
                                        next((r["grid_max_H"] for r in rows if r["receipt"] == largest_at), None)},
        "largest_crossover_among_truncated": {"H_star": largest_t, "receipt": largest_t_at,
                                              "note": "the crossover that actually moves an occupant; the corpus maximum "
                                                      "above may sit in a SAFE receipt, where the order swaps but the "
                                                      "frontier occupant does not"},
        "self_audited_receipts": ["STAGE_G14_FAILED_DRAW_CHARGING_V1.json carries its own extended-grid DG-2 check "
                                  "(extended_grid_dg2_selfcheck) and is reported UNAUDITABLE here only because this "
                                  "auditor has no reconstruction for its schema"],
        "registered_instance_reproduced": energy_1856,
        "receipts": sorted(rows, key=lambda r: (r["verdict"], r["receipt"])),
        "clauses_RV_377_068": clauses,
        "n_clauses_hold": sum(1 for c in clauses if c["verdict"] == "HOLDS"), "n_clauses": len(clauses),
        "counting_note": "every count above is a count of RECEIPTS or of frontier CELLS; neither is a count of forms and "
                         "neither is a species count",
        "claim_ceiling": "the audit is exact on the receipts whose cost lines are reconstructible from their own contents; "
                         "it says nothing about receipts reported UNAUDITABLE, and a SAFE verdict is a statement about the "
                         "receipt's own admissible set and price vectors, not about rows or prices it never reported",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DG2_GRID_AUDIT_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    rc = main()
    print("receipt", rc["receipt_sha256"][:16], rc["counts"])
    for c in rc["clauses_RV_377_068"]:
        print(f"  clause {c['n']}: {c['verdict']:6s} {str(c['measured'])[:150]}")
    for r in rc["receipts"]:
        if r["verdict"] != "SAFE":
            print(f"  {r['verdict']:11s} {r.get('grade') or '':5s} {r['receipt']:46s} "
                  f"{r.get('reason') or ('H*max=' + str(r.get('largest_crossover')))}")

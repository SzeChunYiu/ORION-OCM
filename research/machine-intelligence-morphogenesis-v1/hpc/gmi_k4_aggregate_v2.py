#!/usr/bin/env python3
"""Aggregate ONLY protected K4 V2 receipts.

V1/deterministic receipts are development-exposed and cannot enter this aggregate. The aggregator
validates prediction/generator/successor/beacon hashes, recomputes every task hash and public-beacon
seed, rejects missing/duplicate tasks, and never flips global closure terminals by itself.
"""
from __future__ import annotations
import argparse, collections, glob, hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE = os.path.join(ROOT, "GMI_K4_LOFO_FREEZE_V1.json")
GEN_FREEZE = os.path.join(ROOT, "GMI_K4_GENERATOR_FREEZE_V1.json")
SUCCESSOR = os.path.join(ROOT, "GMI_K4_PROTECTED_SUCCESSOR_FREEZE_V2.json")
BEACON = os.path.join(ROOT, "GMI_K4_PUBLIC_BEACON_V2.json")
RES = os.path.join(ROOT, "microscopes", "results", "k4_v2")


def jhash(path):
    raw = open(path).read(); return json.loads(raw), hashlib.sha256(raw.encode()).hexdigest()


def plan(fr):
    return [{"family": f, "grammar": g, "cell": c}
            for f in sorted(fr["families"]) for g in sorted(fr["grammars"])
            for c in ("w1", "w2", "w4", "w8")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", default=os.path.join(RES, "K4V2_*.json"))
    ap.add_argument("--reveal-names", action="store_true")
    ap.add_argument("--out-json", default=os.path.join(RES, "K4_V2_AGGREGATE.json"))
    ap.add_argument("--out-md", default=os.path.join(RES, "K4_V2_AGGREGATE.md"))
    a = ap.parse_args()

    full, fsha = jhash(FREEZE); fr = dict(full); fr.pop("name_key", None)
    gen, gsha = jhash(GEN_FREEZE); succ, ssha = jhash(SUCCESSOR); beacon, bsha = jhash(BEACON)
    if beacon.get("status") != "ACQUIRED_NO_REROLL" or not beacon.get("sha256_signature_consistency_verified"):
        raise SystemExit("invalid/missing protected public beacon")
    p = plan(fr); files = sorted(glob.glob(a.pattern)); by = collections.defaultdict(list); parse_fail = []
    for path in files:
        try:
            r = json.load(open(path)); r["_path"] = path
            if r.get("schema") != "GMIK4TaskReceiptV3":
                parse_fail.append({"path": path, "error": f"wrong schema {r.get('schema')}"}); continue
            by[r.get("task_index")].append(r)
        except Exception as e: parse_fail.append({"path": path, "error": repr(e)})

    errors = []
    if parse_fail: errors.append({"parse_or_schema_failures": parse_fail})
    missing = [i for i in range(len(p)) if len(by.get(i, [])) == 0]
    dup = {str(i): [r.get("_path") for r in rs] for i, rs in by.items() if len(rs) != 1}
    extra = sorted(i for i in by if not isinstance(i, int) or not 0 <= i < len(p))
    if missing: errors.append({"missing_task_indices": missing})
    if dup: errors.append({"duplicate_task_indices": dup})
    if extra: errors.append({"extra_task_indices": extra})

    rows = []
    for i, spec in enumerate(p):
        if len(by.get(i, [])) != 1: continue
        r = by[i][0]; er = []
        if any(r.get(k) != v for k, v in spec.items()): er.append("task_spec_mismatch")
        for key, expected in (("freeze_artifact_sha256", fsha), ("generator_freeze_sha256", gsha),
                              ("successor_freeze_sha256", ssha), ("public_beacon_sha256", bsha)):
            if r.get(key) != expected: er.append(key + "_mismatch")
        th = hashlib.sha256(json.dumps({**spec, "prediction_freeze": fsha, "generator_freeze": gsha, "successor_freeze": ssha}, sort_keys=True).encode()).hexdigest()
        seed_hex = hashlib.sha256(("GMI-K4-V2" + th + beacon["randomness"]).encode()).hexdigest()[:16]
        if r.get("task_hash") != th: er.append("task_hash_mismatch")
        if r.get("seed") != int(seed_hex, 16) % (2**32): er.append("seed_mismatch")
        if r.get("public_beacon_round") != beacon.get("target_round"): er.append("beacon_round_mismatch")
        if r.get("status") != "OK" or r.get("exit_code") != 0: er.append("task_failed")
        raw = r.get("raw_result")
        if not isinstance(raw, dict) or raw.get("schema") != "GMIK4CellResultV2": er.append("wrong_raw_result_schema")
        if er: errors.append({"task_index": i, "path": r.get("_path"), "errors": er})
        rows.append(r)

    counts = collections.Counter(r.get("verdict", "MISSING") for r in rows)
    fc = {f: collections.Counter() for f in sorted(fr["families"])}
    gc = {g: collections.Counter() for g in sorted(fr["grammars"])}
    cc = {c: collections.Counter() for c in ("w1", "w2", "w4", "w8")}
    for r in rows:
        fc[r["family"]][r["verdict"]] += 1; gc[r["grammar"]][r["verdict"]] += 1; cc[r["cell"]][r["verdict"]] += 1
    complete = not errors and len(rows) == len(p)
    all_green = complete and counts.get("K4_RECOVERY_GREEN", 0) == len(p)
    terminal = ("K4_V2_EXECUTION_INVALID" if errors else
                "K4_V2_ALL_REGISTERED_CELLS_GREEN__IG4_IG5_PENDING" if all_green else
                "K4_V2_CONTAINS_THEORY_RED" if counts.get("THEORY_RED", 0) else
                "K4_V2_CONTAINS_INCONCLUSIVE" if any(counts.get(x, 0) for x in ("INCONCLUSIVE_GRAMMAR", "INCONCLUSIVE_SEARCH", "TASK_FAILED")) else
                "K4_V2_MIXED")
    names = full.get("name_key", {}) if a.reveal_names else {}
    fam = {f: {**dict(fc[f]), **({"revealed_name": names.get(f)} if a.reveal_names else {})} for f in sorted(fc)}
    report = {
        "schema": "GMIK4ProtectedAggregateV2", "terminal": terminal,
        "prediction_freeze_sha256": fsha, "generator_freeze_sha256": gsha,
        "successor_freeze_sha256": ssha, "public_beacon_sha256": bsha,
        "public_beacon_round": beacon.get("target_round"), "expected_tasks": len(p),
        "receipts_found": len(files), "validated_rows": len(rows), "structural_errors": errors,
        "verdict_counts": dict(counts), "family_summary": fam,
        "grammar_summary": {k: dict(v) for k, v in gc.items()}, "cell_summary": {k: dict(v) for k, v in cc.items()},
        "all_complete": complete, "all_green_same_author_scope": all_green,
        "independence": {"IG-1": "CLOSED_REGISTERED_SCOPE", "IG-2": "FUTURE_PUBLIC_BEACON", "IG-3": "GITHUB_ORDERING_SCOPE", "IG-4": "PENDING_INDEPENDENT_BUCKETING", "IG-5": "PENDING_INDEPENDENT_PRIMITIVES"},
        "known_form_zero_prior_global_terminal": False,
        "no_gap_global_terminal": False,
        "claim_ceiling": "Protected V2 K4 evidence at the frozen same-author finite mechanism scope only; independent primitive/meter authorship and K5/real/hardware evidence remain separate gates."
    }
    os.makedirs(os.path.dirname(a.out_json), exist_ok=True); json.dump(report, open(a.out_json, "w"), indent=1, sort_keys=True)
    lines = ["# Protected K4 V2 aggregate", "", f"Terminal: `{terminal}`", "", f"Validated: **{len(rows)}/{len(p)}**; structural error groups: **{len(errors)}**.", "", "## Verdicts", ""]
    lines += [f"- `{k}`: {counts[k]}" for k in sorted(counts)]
    lines += ["", "## Family cells", ""]
    for f in sorted(fam):
        nm = f" — {fam[f].get('revealed_name')}" if a.reveal_names else ""
        vals = ", ".join(f"{k}={v}" for k, v in fam[f].items() if k != "revealed_name") or "none"
        lines.append(f"- `{f}`{nm}: {vals}")
    lines += ["", "IG-4 meter bucketing and IG-5 primitive selection remain pending independent evidence.", "Global K4/K5/no-gap terminals are not flipped by this aggregate alone.", ""]
    open(a.out_md, "w").write("\n".join(lines))
    print(json.dumps({"terminal": terminal, "counts": dict(counts), "validated": len(rows), "errors": len(errors)}, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__": raise SystemExit(main())

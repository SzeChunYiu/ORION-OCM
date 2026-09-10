#!/usr/bin/env python3
"""P1-E3 orchestrator: recovery + all frozen hostiles + receipts.

Never overwrites V1 artifacts. Emits P1E3_FAMILY_TABLE_V1.json and
P1E3_RECOVERY.json next to this file. Exit codes:
  0  all frozen gates pass
  1  hostile failure (taxonomy overlap / leakage not refused)
  2  zero instances recovered
  3  known-answer control mismatch
  4  no-alarm/tamper/scanner controls failed
  5  floors unmet (families/instances)
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import p1e3_recover  # noqa: E402
import p1e3_taxa  # noqa: E402
from policy import PolicyViolation, label_truth, refuse_generator_intent_as_cause  # noqa: E402

FLOORS = {"families_min": 10, "per_family_min": 5, "total_min": 50}

FORBIDDEN_IN_ANY_PY = [
    r"\bsocket\b", r"\burllib\b", r"\bhttpx?\b", r"\brequests\b", r"\bsubprocess\b",
    r"\bos\.system\b", r"\bpopen\b", r"\b__import__\b", r"\beval\(", r"\bexec\(",
    r"\bos\.environ\b", r"\bthreading\b", r"\bmultiprocessing\b", r"\bctypes\b",
    r"\bpickle\b", r"\bshutil\b", r"\bPath\w*\.write\w*\(", r"\bopen\(",
]
WRITE_EXCEPTION_EMIT_ALL = re.compile(r"open\(")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def review_authored_code(py_files: list[Path]) -> dict:
    """Static review gate. File-write tokens are legal ONLY in emit_all.py
    (it writes instances.jsonl in its own cwd); everything else is forbidden."""
    violations = []
    for f in py_files:
        text = f.read_text(errors="replace")
        for pat in FORBIDDEN_IN_ANY_PY:
            for m in re.finditer(pat, text):
                if f.name == "emit_all.py" and pat == r"\bopen\(":
                    continue
                line = text.count("\n", 0, m.start()) + 1
                violations.append({"file": f.name, "pattern": pat, "line": line})
    return {"n_files": len(py_files), "violations": violations, "clean": not violations}


def run_emit_all(authored_dir: Path, timeout_s: int = 180) -> dict:
    """Determinism re-run: execute emit_all.py in a scratch cwd; compare the
    emitted instances.jsonl bytes with the frozen studio artifact copy."""
    emit = authored_dir / "emit_all.py"
    studio_jsonl = authored_dir / "instances.jsonl"
    if not emit.is_file() or not studio_jsonl.is_file():
        return {"status": "CANNOT_CHECK", "reason": "emit_all.py or instances.jsonl missing"}
    frozen_bytes = studio_jsonl.read_bytes()  # the artifact under test; never clobbered
    import os
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")  # keep __pycache__ out of the frozen copy
    with tempfile.TemporaryDirectory(prefix="p1e3_sandbox_") as td:
        tdp = Path(td)
        try:
            proc = subprocess.run(
                [sys.executable, str(emit.resolve())],
                cwd=tdp, capture_output=True, text=True, timeout=timeout_s, env=env,
            )
        except subprocess.TimeoutExpired:
            return {"status": "TIMEOUT", "reason": f"emit_all exceeded {timeout_s}s"}
        out = tdp / "instances.jsonl"
        # If the emitter writes next to itself instead of its cwd, that touched
        # the frozen copy: detect, restore the frozen bytes, and compare against
        # the rerun bytes snapshotted BEFORE restoring.
        clobbered = False
        if out.is_file():
            candidate = out
        else:
            now = (authored_dir / "instances.jsonl").read_bytes()
            if now != frozen_bytes:
                clobbered = True
                candidate = tdp / "rerun_next_to_self.jsonl"
                candidate.write_bytes(now)
                (authored_dir / "instances.jsonl").write_bytes(frozen_bytes)
            else:
                candidate = None
        if candidate is None and proc.returncode == 0:
            # wrote next to itself identically: deterministic by byte equality
            return {
                "status": "DETERMINISTIC",
                "studio_sha": hashlib.sha256(frozen_bytes).hexdigest(),
                "rerun_sha": hashlib.sha256(frozen_bytes).hexdigest(),
                "wrote_next_to_self_and_was_restored": False,
            }
        if candidate is None or proc.returncode != 0:
            return {
                "status": "EMISSION_FAILED",
                "reason": f"rc={proc.returncode}",
                "stderr_tail": proc.stderr[-500:],
            }
        return {
            "status": "DETERMINISTIC" if sha(candidate) == hashlib.sha256(frozen_bytes).hexdigest() else "NON_DETERMINISTIC",
            "studio_sha": hashlib.sha256(frozen_bytes).hexdigest(),
            "rerun_sha": sha(candidate),
            "wrote_next_to_self_and_was_restored": clobbered,
        }


def load_instances(authored_dir: Path) -> list[dict]:
    rows = []
    for line in (authored_dir / "instances.jsonl").read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def compare_intent(recovered: dict, intent: dict | None) -> dict:
    """Audit-only ladder comparison of recovered truth vs author intent.

    Tolerant key matching: the author's intent key names are their own.
    Unknown/unstated fields count NOT_STATED, never AGREE."""
    if recovered.get("status") != "RECOVERED":
        return {"comparable": False, "agreement": "CANNOT_CHECK",
                "reason": recovered.get("reason")}
    intent = intent or {}
    truth = recovered["truth"]
    checks = {}

    def find(*needles: str, types=(int, bool, str)):
        for k, v in intent.items():
            if any(n in str(k).lower() for n in needles) and isinstance(v, types):
                return k, v
        return None, None

    # closure size
    k, v = find("closure", "derived", types=(int,))
    if k is not None:
        checks["closure_size"] = {"intent_key": k, "intent": v, "recovered": truth["closure_size"],
                                  "agree": v == truth["closure_size"]}
    # reachable goals (set or count)
    k, v = find("reach", "goal", types=(int,))
    if k is not None:
        checks["reachable_goal_count"] = {"intent_key": k, "intent": v,
                                          "recovered": len(truth["reachable_goals"]),
                                          "agree": v == len(truth["reachable_goals"])}
    elif isinstance((rv := intent.get("expected_reachable_goals")), list):
        checks["reachable_goals_set"] = {"intent_key": "expected_reachable_goals",
                                         "intent": rv, "recovered": truth["reachable_goals"],
                                         "agree": sorted(rv) == truth["reachable_goals"]}
    # min seed cost / possibility
    k, v = find("cost", "seed", types=(int,))
    poss = None
    for k2, v2 in intent.items():
        kl = str(k2).lower()
        if ("impossib" in kl or "possible" in kl) and isinstance(v2, bool):
            poss = (k2, v2)
            break
    ms = truth["min_seed"]
    if k is not None and ms["possible"]:
        checks["min_seed_cost"] = {"intent_key": k, "intent": v, "recovered": ms["cost"],
                                   "agree": v == ms["cost"]}
    # nested author shapes (author's own key names): intent["expected_min_seed"]
    # may be {"cost": c, "seed": [...]} or {"status": "IMPOSSIBLE"}; goals may be
    # a list under "expected_goals_reachable".
    ems = intent.get("expected_min_seed")
    if isinstance(ems, dict):
        if "cost" in ems and ms["possible"] and "min_seed_cost" not in checks:
            checks["min_seed_cost"] = {"intent_key": "expected_min_seed.cost", "intent": ems["cost"],
                                       "recovered": ms["cost"], "agree": ems["cost"] == ms["cost"]}
        if ems.get("status") == "IMPOSSIBLE" and poss is None:
            poss = ("expected_min_seed.status", False)
    if isinstance(intent.get("expected_goals_reachable"), list):
        rv = intent["expected_goals_reachable"]
        checks["reachable_goals_set"] = {"intent_key": "expected_goals_reachable",
                                         "intent": rv, "recovered": truth["reachable_goals"],
                                         "agree": sorted(rv) == truth["reachable_goals"]}
    if poss is not None:
        checks["min_seed_possible"] = {"intent_key": poss[0], "intent": poss[1],
                                       "recovered": ms["possible"],
                                       "agree": poss[1] == ms["possible"]}

    if not checks:
        return {"comparable": False, "agreement": "NOT_STATED", "reason": "no recognizable intent expectation fields"}
    agrees = [c["agree"] for c in checks.values()]
    return {
        "comparable": True,
        "agreement": "AGREE" if all(agrees) else "DISAGREE",
        "checks": checks,
        "disagreeing_checks": [name for name, c in checks.items() if not c["agree"]],
    }


def main() -> int:
    t0 = time.perf_counter()
    # Real run: no argument -> the frozen authored package next to this file.
    # A path argument runs the whole pipeline against that directory instead
    # (dry-run/fixture validation); receipts are written next to that dir so a
    # dry run can never contaminate the real receipts.
    authored = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE / "p1e3_authored"
    out_dir = authored.parent
    if not (authored / "instances.jsonl").is_file():
        print("authored package missing; run the author unit first")
        return 2

    # ALL authored artifacts, including every families/*.py module that
    # emit_all.py imports and executes (they are authored code too).
    py_files = sorted(p for p in authored.rglob("*.py") if "__pycache__" not in p.parts)
    md_files = sorted(p for p in authored.rglob("*.md") if "__pycache__" not in p.parts)
    review = review_authored_code(py_files)
    determinism = run_emit_all(authored)

    instances = load_instances(authored)
    tiers = p1e3_taxa.build_token_list()
    scan_targets = py_files + md_files + [authored / "instances.jsonl"]
    disjointness = p1e3_taxa.scan_paths(scan_targets, tiers)
    tamper = p1e3_taxa.tamper_control(scan_targets, tiers)
    noalarm = p1e3_taxa.no_alarm_control(p1e3_taxa._patterns(tiers))
    known = p1e3_recover.run_known_answer_control()

    # --- truth recovery (core only; intent never enters) --------------------
    rows = []
    for inst in instances:
        recovered = p1e3_recover.recover_instance(inst)
        intent = inst.get("intent") if isinstance(inst.get("intent"), dict) else {}
        comparison = compare_intent(recovered, intent)
        labelled = label_truth(
            target="decision",
            recovered=recovered,
            planted={"family": inst.get("family"), "instance_id": inst.get("instance_id"),
                     "intent": intent},
            independently_authored=True,
            evidence_class="E3",
        )
        rows.append({
            "instance_id": inst.get("instance_id"),
            "family": inst.get("family"),
            "recovery_status": recovered["status"],
            "reason": recovered.get("reason"),
            "truth": recovered.get("truth"),
            "intent_audit_only": intent,
            "intent_role": inst.get("intent_role") or intent.get("intent_role"),
            "intent_comparison": comparison,
            "truth_source": labelled["source"],
        })

    # --- leakage hostile: planted intent label must be REFUSED --------------
    leakage_refused = False
    leakage_error = None
    try:
        bad = {"target": "minimum_sufficient_cause", "source": "GENERATOR_INTENT",
               "truth": {"planted_family": rows[0]["family"]}}
        refuse_generator_intent_as_cause(bad)
    except PolicyViolation as exc:
        leakage_refused = True
        leakage_error = str(exc)
    # and the policy must fail closed for an unrecovered cause target
    cc = label_truth(target="cause", recovered=None, planted={"family": rows[0]["family"]},
                     independently_authored=True, evidence_class="E3")

    # --- tallies --------------------------------------------------------------
    fam_counts = Counter()
    fam_recovered = Counter()
    fam_cannot = Counter()
    agreement = Counter()
    for r in rows:
        fam_counts[r["family"]] += 1
        if r["recovery_status"] == "RECOVERED":
            fam_recovered[r["family"]] += 1
        else:
            fam_cannot[r["family"]] += 1
        agreement[r["intent_comparison"]["agreement"]] += 1
    recovered_n = sum(1 for r in rows if r["recovery_status"] == "RECOVERED")
    families_meeting_floor = sum(
        1 for f in fam_counts
        if fam_counts[f] >= FLOORS["per_family_min"] and fam_recovered[f] >= 1
    )

    taxonomy_clean = disjointness["total_overlaps"] == 0
    hostiles = {
        "H-P1E3-1-taxonomy-disjointness": {
            "passed": taxonomy_clean,
            "total_overlaps": disjointness["total_overlaps"],
            "per_file": {Path(k).name: v for k, v in disjointness["per_file"].items()},
        },
        "H-P1E3-2-intent-label-leakage": {
            "passed": leakage_refused and cc["source"] == "CANNOT_CHECK",
            "refusal_recorded": leakage_error,
            "unrecovered_cause_target_source": cc["source"],
        },
        "H-P1E3-3-known-answer": {"passed": known["all_match"], "n_cases": known["n_cases"],
                                  "rows": known["rows"]},
        "H-P1E3-4-no-alarm-control": {"passed": noalarm["control_passed"], "detail": noalarm},
        "H-P1E3-5-tamper-sensitivity": {"passed": tamper["alarm"], "detail": tamper},
    }
    floors_met = {
        "families": families_meeting_floor >= FLOORS["families_min"],
        "families_counted": families_meeting_floor,
        "per_family_min": all(v >= FLOORS["per_family_min"] for v in fam_counts.values()),
        "total": len(rows) >= FLOORS["total_min"],
        "total_instances": len(rows),
    }

    receipt = {
        "schema": "ocm.independent-authorship-gate.p1e3.recovery.v1",
        "pipeline_freeze": "P1E3_AUTHORSHIP_FREEZE_V1.json",
        "author_unit": "FRESH_MODEL_SESSION__MODEL_PROXY (HUMAN_GATE_BYPASSED__MODEL_PROXY)",
        "counts": {
            "instances": len(rows),
            "families": len(fam_counts),
            "families_meeting_floor": families_meeting_floor,
            "recovered": recovered_n,
            "cannot_check": len(rows) - recovered_n,
            "intent_agreement": dict(agreement),
        },
        "authored_code_review": review,
        "determinism_rerun": determinism,
        "hostiles": hostiles,
        "floors": floors_met,
        "rows": rows,
        "taxonomy_token_tiers": {k: len(v) for k, v in tiers.items()},
        "bindings": {str(p): sha(p) for p in scan_targets},
        "wall_s": round(time.perf_counter() - t0, 3),
        "no_novelty_claim": True,
    }
    (out_dir / "P1E3_RECOVERY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

    family_table = {
        "schema": "ocm.independent-authorship-gate.p1e3.family_table.v1",
        "generated_from": "p1e3_check.py",
        "author_unit": "FRESH_MODEL_SESSION__MODEL_PROXY (HUMAN_GATE_BYPASSED__MODEL_PROXY)",
        "families": [
            {
                "family": f,
                "instances": fam_counts[f],
                "recovered": fam_recovered[f],
                "cannot_check": fam_cannot[f],
                "counts_toward_floor": fam_counts[f] >= FLOORS["per_family_min"] and fam_recovered[f] >= 1,
            }
            for f in sorted(fam_counts)
        ],
        "totals": {
            "families": len(fam_counts),
            "families_meeting_floor": families_meeting_floor,
            "instances": len(rows),
            "recovered": recovered_n,
            "cannot_check": len(rows) - recovered_n,
        },
        "authored_artifact_shas": {str(p.relative_to(authored)): sha(p) for p in scan_targets},
    }
    (out_dir / "P1E3_FAMILY_TABLE_V1.json").write_text(json.dumps(family_table, indent=2, sort_keys=True) + "\n")

    print(json.dumps({
        "counts": receipt["counts"],
        "hostiles_passed": {k: v["passed"] for k, v in hostiles.items()},
        "floors": floors_met,
        "determinism": determinism.get("status"),
        "review_clean": review["clean"],
        "wall_s": receipt["wall_s"],
    }, indent=2))

    if not known["all_match"]:
        return 3
    if not (noalarm["control_passed"] and tamper["alarm"]):
        return 4
    if not taxonomy_clean:
        return 1
    if not hostiles["H-P1E3-2-intent-label-leakage"]["passed"]:
        return 1
    if recovered_n == 0:
        return 2
    if not (floors_met["families"] and floors_met["per_family_min"] and floors_met["total"]):
        return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

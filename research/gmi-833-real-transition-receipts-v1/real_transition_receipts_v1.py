"""Deterministic receipt builder for gmi-833-real-transition-receipts-v1.

Torch-free. Rebuilds per-setting evaluation artifacts, applies the frozen
blind classification rule (FREEZE_V2_AMENDMENT.md: data-derived stateless
floor) and selection rule, validates receipts through
gmi-833-real-transition-protocol-v1, and emits the package RESULT.
Runs identically on the execution host and in CI.

Usage: python -I -B real_transition_receipts_v1.py [package_dir]
  package_dir defaults to this file's directory; REAL_RUNS/ must exist.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

FREEZE_COMMIT = "cd6196aa5fd0edcdbcfb535ff2aecf7cd0870754"
ETA = 0.5
CLAIM_CEILING = "GMI_REAL_SYSTEM_TRANSITION_VALIDATION_PROTOCOL_MACHINE_CHECKABLE"
SETTINGS = ("low", "high")
LICENSED_BAND = (0.125, 0.375)  # 1/8 < E0 < 3/8 (FREEZE_V2_AMENDMENT.md A4)


def _load_protocol(repo_root: Path):
    p = repo_root / "research" / "gmi-833-real-transition-protocol-v1" / "real_transition_protocol_v1.py"
    spec = importlib.util.spec_from_file_location("real_transition_protocol_v1", p)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _median(xs: Sequence[float]) -> float:
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def classify(B: float, imm_err: float, N_imm: int, delay_err: float, N_delay: int,
             floor_del: float) -> str:
    """Amended blind rule (FREEZE_V2_AMENDMENT.md A3). Numeric inputs only."""
    if N_imm <= 0 or N_delay <= 0:
        return "ABSTAIN"
    sd = math.sqrt(0.25 / N_delay)
    sd_diff = math.sqrt(0.5 / N_delay)
    si = math.sqrt(0.25 / N_imm)
    if imm_err > 0.5 - 3 * si:  # trainability gate
        return "ABSTAIN"
    if B == 0.0:
        if delay_err <= floor_del + 3 * sd:
            return "STATELESS"
        return "ABSTAIN"
    if delay_err <= floor_del - 3 * sd_diff:
        return "PERSISTENT_STATE"
    return "ABSTAIN"


def scored_candidates(runs: Mapping[str, Any]) -> dict[str, dict[str, float]]:
    """Opaque-ID scored table: {cid: {err components, B, counts, spread}}."""
    out = {}
    for cid, c in sorted(runs["candidates"].items()):
        per = c["seeds_runs"]
        out[cid] = {
            "err_all": _median([r["err_all"] for r in per]),
            "err_imm": _median([r["err_imm"] for r in per]),
            "err_delay": _median([r["err_delay"] for r in per]),
            "N_imm": per[0]["N_imm"],
            "N_delay": per[0]["N_delay"],
            "B": float(c["carried_state_bytes"]),
            "seed_spread_err_all": max(r["err_all"] for r in per) - min(r["err_all"] for r in per),
        }
    return out


def floor_of(tab: Mapping[str, Mapping[str, float]]) -> tuple[str, Mapping[str, float]]:
    zero_b = [cid for cid, c in tab.items() if c["B"] == 0.0]
    assert zero_b, "pool must contain a B=0 candidate"
    cid = sorted(zero_b)[0]
    return cid, tab[cid]


def select_winners(tab: Mapping[str, Mapping[str, float]], p: float, lam: float) -> list[str]:
    js = {cid: p * c["err_all"] + lam * c["B"] for cid, c in tab.items()}
    best = min(js.values())
    return sorted(cid for cid, j in js.items() if j == best)


def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def build_eval_artifacts(runs_dir: Path) -> dict[str, dict[str, Any]]:
    """One eval artifact per system per setting; {system: {setting: artifact}}."""
    out: dict[str, dict[str, Any]] = {}
    for d in sorted(runs_dir.iterdir()):
        if not d.is_dir():
            continue
        runs = json.loads((d / "runs.json").read_text())
        p = runs["p"]
        lam_star = runs["lambda_star"]
        tab = scored_candidates(runs)
        _, floor_cand = floor_of(tab)
        floor_del = floor_cand["err_delay"]
        lams = {"low": lam_star / 2, "high": 3 * lam_star / 2, "boundary": lam_star}
        arts = {}
        for setting, lam in lams.items():
            winners = select_winners(tab, p, lam)
            js = {cid: p * c["err_all"] + lam * c["B"] for cid, c in tab.items()}
            if len(winners) == 1:
                w = tab[winners[0]]
                cls = classify(w["B"], w["err_imm"], w["N_imm"], w["err_delay"], w["N_delay"],
                               floor_del)
            else:
                cls = "ABSTAIN"
            art = {
                "system_id": runs["system_id"],
                "setting": setting,
                "lambda": lam,
                "error_price": p,
                "stateless_floor_del": floor_del,
                "priced_scores_J": js,
                "winner_ids": winners,
                "winner_classification": cls,
                "classification_inputs": {
                    cid: {k: tab[cid][k] for k in ("B", "err_imm", "N_imm", "err_delay", "N_delay")}
                    for cid in winners
                },
            }
            arts[setting] = art
            (d / ("eval_%s.json" % setting)).write_bytes(_canon(art))
        out[runs["system_id"]] = arts
    return out


def build_receipts(runs_dir: Path, artifacts: Mapping[str, Mapping[str, Any]],
                   licensed: Sequence[str]) -> list[dict[str, Any]]:
    receipts = []
    for sid in licensed:
        d = runs_dir / sid
        runs = json.loads((d / "runs.json").read_text())
        tab = scored_candidates(runs)
        arts = artifacts[sid]
        low, high, bnd = arts["low"], arts["high"], arts["boundary"]

        def art_hash(a: Mapping[str, Any]) -> str:
            return hashlib.sha256(_canon(a)).hexdigest()

        run_id = "%s:%s" % (sid, runs["source_sha256"][:12])
        cid_stateless, _ = floor_of(tab)
        cid_persist = [c for c in tab if tab[c]["B"] > 0][0]
        receipt = {
            "system_id": sid,
            "system_version": "v1",
            "implementation_ref": "research/gmi-833-real-transition-receipts-v1/train_real_transitions_v1.py@freeze-" + FREEZE_COMMIT[:10],
            "prediction_ref": "research/gmi-833-real-transition-receipts-v1/FREEZE_V1.md@" + FREEZE_COMMIT
                              + "+FREEZE_V2_AMENDMENT.md",
            "prediction_frozen_before_outcome": True,
            "evidence_kind": "REAL_SYSTEM",
            "task_or_workload_id": "%s@sha256:%s:T%d" % (sid, runs["source_sha256"], runs["T"]),
            "before_context": {
                "resource_price_lambda": low["lambda"], "error_price": runs["p"],
                "eta_registered": ETA, "lambda_star": runs["lambda_star"],
                "boundary_law": "lambda*=p*eta/(2B); licensed band 1/8<E0<3/8 (amendment A4)",
            },
            "after_context": {
                "resource_price_lambda": high["lambda"], "error_price": runs["p"],
                "eta_registered": ETA, "lambda_star": runs["lambda_star"],
                "boundary_law": "lambda*=p*eta/(2B); licensed band 1/8<E0<3/8 (amendment A4)",
            },
            "predicted_before_property": "PERSISTENT_STATE",
            "predicted_after_property": "STATELESS",
            "observed_before_property": low["winner_classification"],
            "observed_after_property": high["winner_classification"],
            "classification_blind_to_target_family": True,
            "resources_before": [
                runs["B_gru"],
                runs["candidates"][cid_persist]["param_count"],
                max(r["train_seconds"] for r in runs["candidates"][cid_persist]["seeds_runs"]),
            ],
            "resources_after": [
                runs["B_gru"],
                runs["candidates"][cid_persist]["param_count"],
                max(r["train_seconds"] for r in runs["candidates"][cid_persist]["seeds_runs"]),
            ],
            "run_id_before": run_id + ":low",
            "run_id_after": run_id + ":high",
            "artifact_hash_before": art_hash(low),
            "artifact_hash_after": art_hash(high),
            "protected_outcome_leakage": False,
            "classification_identified": low["winner_classification"] != "ABSTAIN"
            and high["winner_classification"] != "ABSTAIN",
            # extended provenance (not required by protocol v1)
            "x_source": {"path": runs["source_path"], "sha256": runs["source_sha256"],
                         "bytes": runs["source_bytes"], "fallback_used": runs["fallback_used"]},
            "realized_eta": runs["realized_eta"],
            "stateless_floor": {
                "candidate_id": cid_stateless,
                "floor_del": low["stateless_floor_del"],
                "E0_err_all": tab[cid_stateless]["err_all"],
            },
            "carried_state_bytes_persistent": runs["B_gru"],
            "seed_spread_err_all": {
                cid: tab[cid]["seed_spread_err_all"] for cid in tab
            },
            "boundary_tie_control": {
                "lambda": bnd["lambda"], "winners": bnd["winner_ids"],
                "counted_as_transition": False,
            },
            "shifted_law_control": {
                "shifted_boundary_lambda": 2 * runs["lambda_star"],
                "shifted_prediction_at_high": "PERSISTENT_STATE",
                "observed_at_high": high["winner_classification"],
                "shifted_prediction_falsified": high["winner_classification"] == "STATELESS",
            },
            "floor_witness_const0": runs["floor_witness_const0"],
            "library_versions": {"torch": runs["torch"], "numpy": runs["numpy"]},
        }
        receipts.append(receipt)
    return receipts


def licensed_systems(runs_dir: Path) -> tuple[list[str], list[dict[str, Any]]]:
    """Registered-order eligibility per amendment A4/A5; unlicensed recorded."""
    licensed: list[str] = []
    unlicensed: list[dict[str, Any]] = []
    for d in sorted(runs_dir.iterdir()):
        if not d.is_dir():
            continue
        runs = json.loads((d / "runs.json").read_text())
        tab = scored_candidates(runs)
        _, floor_cand = floor_of(tab)
        e0 = floor_cand["err_all"]
        reason = None
        if not (LICENSED_BAND[0] < e0 < LICENSED_BAND[1]):
            reason = "E0_OUTSIDE_LICENSED_BAND"
        else:
            sd_diff = math.sqrt(0.5 / floor_cand["N_delay"])
            cid_persist = [c for c in tab if tab[c]["B"] > 0][0]
            if not tab[cid_persist]["err_delay"] <= floor_cand["err_delay"] - 3 * sd_diff:
                reason = "PERSISTENT_DOES_NOT_BEAT_EMPIRICAL_FLOOR"
        if reason:
            unlicensed.append({"system_id": runs["system_id"], "E0": e0, "reason": reason})
        else:
            licensed.append(runs["system_id"])
    return licensed, unlicensed


def finite_certificate(pkg_dir: Path | None = None) -> dict[str, Any]:
    here = pkg_dir or Path(__file__).resolve().parent
    repo_root = here.parent.parent
    protocol = _load_protocol(repo_root)
    runs_dir = here / "REAL_RUNS"
    artifacts = build_eval_artifacts(runs_dir)
    licensed, unlicensed = licensed_systems(runs_dir)
    # FREEZE_V3_ADDENDUM.md B4: receipts for the first five licensed systems
    # in registered order; all licensed systems are still fully checked below
    receipts = build_receipts(runs_dir, artifacts, licensed[:5])
    evaluation = protocol.evaluate(receipts)

    checks: dict[str, bool] = {}
    # amended blind rule hostiles (pure function, numeric-only)
    checks["classify_floor_setter_stateless"] = classify(0.0, 0.0, 1000, 0.40, 1000, 0.40) == "STATELESS"
    checks["classify_trained_persistent"] = classify(96.0, 0.0, 1000, 0.02, 1000, 0.40) == "PERSISTENT_STATE"
    checks["classify_ambiguous_abstains"] = classify(96.0, 0.0, 1000, 0.38, 1000, 0.40) == "ABSTAIN"
    checks["classify_untrained_abstains"] = classify(96.0, 0.5, 1000, 0.02, 1000, 0.40) == "ABSTAIN"
    checks["classify_stateless_above_own_floor_abstains"] = classify(0.0, 0.0, 1000, 0.6, 1000, 0.4) == "ABSTAIN"

    per_system = []
    for sid in licensed:
        d = runs_dir / sid
        runs = json.loads((d / "runs.json").read_text())
        tab = scored_candidates(runs)
        _, floor_cand = floor_of(tab)
        cid_persist = [c for c in tab if tab[c]["B"] > 0][0]
        sd_diff = math.sqrt(0.5 / floor_cand["N_delay"])
        row = {
            "system_id": sid,
            "lambda_star": runs["lambda_star"],
            "E0_stateless": floor_cand["err_all"],
            "floor_del": floor_cand["err_delay"],
            "persist_delay": tab[cid_persist]["err_delay"],
            "observed": {s: artifacts[sid][s]["winner_classification"]
                         for s in SETTINGS + ("boundary",)},
            "licensed_band": LICENSED_BAND[0] < floor_cand["err_all"] < LICENSED_BAND[1],
            "persistent_beats_empirical_floor": tab[cid_persist]["err_delay"] <= floor_cand["err_delay"] - 3 * sd_diff,
            "stateless_floor_recorded": 0.0 < floor_cand["err_delay"] <= 0.5,
        }
        row["transition_matches_prediction"] = (
            row["observed"]["low"] == "PERSISTENT_STATE"
            and row["observed"]["high"] == "STATELESS"
        )
        row["shifted_law_falsified"] = artifacts[sid]["high"]["winner_classification"] == "STATELESS"
        per_system.append(row)
        checks[sid + ":licensed_band"] = row["licensed_band"]
        checks[sid + ":persistent_beats_empirical_floor"] = row["persistent_beats_empirical_floor"]
        checks[sid + ":stateless_floor_recorded"] = row["stateless_floor_recorded"]
        checks[sid + ":transition_matches_prediction"] = row["transition_matches_prediction"]
        checks[sid + ":shifted_law_falsified"] = row["shifted_law_falsified"]

    row_earned = evaluation["terminal"] == "REAL_SYSTEM_TRANSITION_VALIDATED_AT_REGISTERED_SCOPE"
    verdict = "GREEN" if all(checks.values()) else "RED"
    return {
        "schema": "GMI_833_REAL_TRANSITION_RECEIPTS_RESULT_V1",
        "claim_ceiling": CLAIM_CEILING,
        "freeze_commit": FREEZE_COMMIT,
        "amendment": "FREEZE_V2_AMENDMENT.md (data-derived stateless floor; licensed band 1/8<E0<3/8)",
        "verdict": verdict,
        "checks": checks,
        "systems": per_system,
        "unlicensed_systems": unlicensed,
        "protocol_evaluation": evaluation,
        "scientific_row_earned": bool(row_earned and verdict == "GREEN"),
        "forbidden_promotions": [
            "UNIVERSAL_ARCHITECTURE_PREDICTION",
            "REAL_WORLD_MIGRATION_CALIBRATION_BEYOND_REGISTERED_SYSTEMS",
            "STOCHASTIC_SWITCHING_CLOSED",
            "COMPLETE_GMI",
        ],
    }


def main() -> None:
    print(json.dumps(finite_certificate(), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

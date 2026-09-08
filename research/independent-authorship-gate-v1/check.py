#!/usr/bin/env python3
"""Run the ME-X1 recovered-vs-planted check and enforce the fail-closed policy."""
from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

from policy import (
    PolicyViolation,
    artifact_explained_positive_is_negative,
    label_truth,
    refuse_generator_intent_as_cause,
)
from recover_mex1 import bindings, compare_to_planted, load_mex1, recover_world

HERE = Path(__file__).resolve().parent
SPLIT = "dev"
SPLIT_SEED = "ME-X1-DEV-20260902"
PER_FAMILY = 5


def _row(inst, recovered, planted_cmp, labelled) -> dict:
    truth = (recovered.get("truth") or {})
    return {
        "instance_id": inst.instance_id,
        "planted_family_audit": inst.family,
        "variant": inst.variant,
        "recovery_status": recovered["status"],
        "action": truth.get("action"),
        "decisive_atom": truth.get("decisive_atom"),
        "decisive_module": truth.get("decisive_module"),
        "invalid_atoms": truth.get("invalid_atoms"),
        "min_sufficient_repair": truth.get("min_sufficient_repair"),
        "comparison": planted_cmp,
        "cause_truth_source": labelled["source"],
        "cause_truth": labelled["truth"],
    }


def run() -> dict:
    t0 = time.perf_counter()
    gen, model, oracle = load_mex1()
    pairs = gen.generate_split(SPLIT, SPLIT_SEED, {f: PER_FAMILY for f in model.FAMILIES})
    rows = []
    policy_ok = 0
    for inst, _exp in pairs:
        recovered = recover_world(model, oracle, inst.world_v0, inst.events, inst.request)
        labelled = label_truth(
            target="minimum_sufficient_cause",
            recovered=recovered,
            planted={"family": inst.family, "variant": inst.variant, "instance_id": inst.instance_id},
            independently_authored=False,
            evidence_class="E2",
        )
        refuse_generator_intent_as_cause(labelled)
        if labelled["source"] == "GENERATOR_INTENT":
            raise PolicyViolation("cause labelled from generator intent")
        if "planted_family" in (labelled.get("truth") or {}):
            raise PolicyViolation("planted family leaked into cause truth")
        policy_ok += 1
        rows.append(_row(inst, recovered, compare_to_planted(inst.family, inst.variant, recovered), labelled))

    fixtures = []
    for fx in gen.known_answer_fixtures():
        recovered = recover_world(model, oracle, fx["world"], fx["events"], fx["request"])
        labelled = label_truth(
            target="minimum_sufficient_cause",
            recovered=recovered,
            planted={"family": fx["family"], "case_id": fx["case_id"]},
            independently_authored=False,
            evidence_class="E1",
        )
        refuse_generator_intent_as_cause(labelled)
        fixtures.append({
            "case_id": fx["case_id"],
            "planted_family_audit": fx["family"],
            "recovery_status": recovered["status"],
            "recovered_action": (recovered.get("truth") or {}).get("action"),
            "fixture_expected_action": fx["expected"],
            "action_agrees_with_fixture": (recovered.get("truth") or {}).get("action") == fx["expected"],
            "comparison": compare_to_planted(fx["family"], "FIXTURE", recovered),
            "cause_truth_source": labelled["source"],
        })

    # Hostile: attempting to use planted family as cause truth must fail closed.
    hostile_ok = False
    try:
        bad = {
            "target": "cause",
            "source": "GENERATOR_INTENT",
            "truth": {"planted_family": pairs[0][0].family},
        }
        refuse_generator_intent_as_cause(bad)
    except PolicyViolation:
        hostile_ok = True

    e3_closed = label_truth(
        target="decision",
        recovered=None,
        planted={"family": "X1-A_CLAIM_PROBLEM_IDENTITY"},
        independently_authored=False,
        evidence_class="E3",
    )

    reasons = Counter(r["comparison"]["reason"] for r in rows)
    agreements = Counter(r["comparison"]["agreement"] for r in rows)
    artifact = sum(1 for r in rows if r["comparison"].get("artifact_explained_if_used_as_truth"))
    recovered_n = sum(1 for r in rows if r["recovery_status"] == "RECOVERED")
    body = {
        "schema": "ocm.independent-authorship-gate.recovery.v1",
        "world_family": "ME-X1",
        "split": {"name": SPLIT, "seed": SPLIT_SEED, "per_family": PER_FAMILY, "n": len(rows)},
        "oracle": "research/experiments/me-x1/mex1_oracle.py",
        "policy": "fail-closed: cause truth is independent recovery or CANNOT_CHECK; generator intent is audit-only",
        "counts": {
            "instances": len(rows),
            "recovered": recovered_n,
            "cannot_check": len(rows) - recovered_n,
            "policy_enforced": policy_ok,
            "hostile_generator_intent_refused": hostile_ok,
            "agreement": dict(agreements),
            "reasons": dict(reasons),
            "artifact_explained_if_family_used_as_truth": artifact,
            "fixtures": len(fixtures),
            "fixture_actions_match": sum(1 for f in fixtures if f["action_agrees_with_fixture"]),
        },
        "e3_without_independent_authorship": e3_closed["source"],
        "interpretation": (
            "ME-X1 decisions are independently recoverable by the exact oracle. "
            "Planted family names are generator intent. Agreement on POSITIVE rows is "
            "expected because the planter rejection-samples until the oracle invariant "
            "matches the planted family; that agreement is artifact-explained, not "
            "independent authorship. NEGATIVE / empty-cause rows show planted family "
            "!= recovered min-sufficient cause. Diagnosis truth is the recovered atom "
            "set, never Instance.family."
        ),
        "rows": rows,
        "fixtures": fixtures,
        "bindings": bindings(),
        "wall_s": time.perf_counter() - t0,
        "no_novelty_claim": True,
    }
    if artifact and artifact_explained_positive_is_negative("GENERATOR_FILTERED_BY_ORACLE_INVARIANT"):
        body["artifact_explained_positives_retained_as_negative_findings"] = True
    return body


def main() -> int:
    receipt = run()
    out = HERE / "RECOVERY.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: receipt[k] for k in ("schema", "world_family", "counts", "e3_without_independent_authorship", "interpretation", "wall_s")}, indent=2))
    if receipt["counts"]["recovered"] == 0:
        return 2
    if not receipt["counts"]["hostile_generator_intent_refused"]:
        return 1
    if receipt["e3_without_independent_authorship"] != "CANNOT_CHECK":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

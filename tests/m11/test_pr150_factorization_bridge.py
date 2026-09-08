"""PR #150 adversarial bridge: hidden-cause diagnosis into the real M11 governed lifecycle.

This is deliberately not an OCM-win test.  It checks that (a) no oracle cause label is needed when
interventions identify the minimum sufficient layer, (b) aliased symptom-only cases remain UNKNOWN,
and (c) both a factor-local arm and the strongest adaptive symbolic parent can traverse the same
prediction-receipt -> shadow -> external-adoption -> restart -> fresh-reuse path.  Equality is a
PARENT_SUFFICIENT receipt, not a scientific promotion.
"""
from __future__ import annotations

import json

from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.selfmodel import diagnose as DG
from ocm.selfmodel import govern as GV
from ocm.selfmodel import model as SM
from ocm.selfmodel import proposal as PR


def _failure(ablations):
    return SM.FailureRecord(
        "e150-f1", "anonymous-episode", "factorization", "wrong action", "restore future reuse",
        ("ev:trace-e150",), (SM.Layer.D1_ROUTING, SM.Layer.D2_OPERATOR, SM.Layer.D3_REPRESENTATION),
        tuple(ablations), {}, "LIVE", "high", 1, "research",
    )


def test_hidden_cause_uses_interventions_and_alias_without_interventions_is_cannot_check():
    # No cause/layer oracle is an input.  The only identifying information is the intervention result.
    f = _failure([
        SM.AblationEvidence("reroute only", SM.Layer.D1_ROUTING, False, "ev:a1"),
        SM.AblationEvidence("replace factor learner", SM.Layer.D2_OPERATOR, True, "ev:a2"),
        SM.AblationEvidence("rewrite representation", SM.Layer.D3_REPRESENTATION, True, "ev:a3"),
    ])
    d = DG.diagnose(f)
    assert d.minimum_sufficient == "D2" and not d.architecture_alarm

    # Symptom-equivalent causes with no diagnostic intervention are not guessed.
    alias = DG.diagnose(_failure([]))
    assert alias.minimum_sufficient is None and set(alias.unknown) == {"D1", "D2", "D3"}
    allowed, why = DG.escalation_allowed(alias, None)
    assert not allowed and "UNKNOWN" in why


def _runner(artifact, tasks):
    success = 0
    for task in tasks:
        if task["family"] == "preservation":
            success += 1
        elif artifact["strategy"] in {"factor_local", "symbolic_incremental_parent"}:
            success += 1
    return {"success": success, "n": len(tasks), "resources": {"steps": len(tasks)}}


def _run_governed_bridge(root, strategy: str):
    rt = OCMRuntime(root)
    diagnosis = DG.diagnose(_failure([
        SM.AblationEvidence("reroute only", SM.Layer.D1_ROUTING, False, "ev:b1"),
        SM.AblationEvidence("install learned factor learner", SM.Layer.D2_OPERATOR, True, "ev:b2"),
    ]))
    assert diagnosis.minimum_sufficient == "D2"

    incumbent = {"strategy": "global", "supports": []}
    learned = {"strategy": strategy, "supports": [[0, 1], [2, 3]]}
    if strategy == "factor_local":
        learned["relevance_cache"] = [0, 1, 2, 3]  # duplicate cache is intentionally charged elsewhere.
    pred = PR.Prediction(("target",), (), {"steps": 4}, ("preservation",), (), ("no_fresh_reuse",), 0.0)
    proposal = PR.SelfChangeProposal(
        f"e150-{strategy}", "1", ("ev:b2",), "cognition.factorizer", "D2", "fp-inc",
        PR.ChangeClass.C2_OPERATOR, {"replace": "learned_sparse_factorization", "source": strategy},
        lambda _inc: dict(learned), pred, ("preservation",), (), "target",
        "restore fp-inc", "research", "window-e150", PR.Origin.LEARNED,
        dev_tasks=("dev-episode-1",),
    )
    assert PR.is_minimum_sufficient(proposal, diagnosis.minimum_sufficient)
    broader = PR.SelfChangeProposal(
        "e150-broad", "1", ("ev:b2",), "cognition.factorizer", "D2", "fp-inc",
        PR.ChangeClass.C3_REPRESENTATION, {"replace": "whole_representation"}, lambda x: x,
        pred, ("preservation",), (), "target", "restore fp-inc", "research", "window-e150",
        PR.Origin.LEARNED,
    )
    assert not PR.is_minimum_sufficient(broader, diagnosis.minimum_sufficient)

    ledger = GV.AdoptionLedger(rt)
    ledger.propose(proposal)
    receipt = GV.register_prediction(rt, proposal)  # must precede protected shadow access.
    target = [{"id": f"held-target-{i}", "family": "target"} for i in range(4)]
    preservation = [{"id": f"held-pres-{i}", "family": "preservation"} for i in range(4)]
    suites = {"target": target, "preservation": preservation}
    shadow = GV.shadow_evaluate(rt, incumbent, proposal, _runner, suites)
    assurance = GV.assure(
        proposal, shadow, protocol_hash="e150-v1", frozen_protocol_hash="e150-v1",
        budget={"steps": 4}, rollback_exists=True, prediction_receipt=receipt, runtime=rt,
        held_out_task_ids=[t["id"] for rows in suites.values() for t in rows],
    )
    assert assurance.passed, assurance.reasons
    decision = GV.ExternalAdopter("e150-external-token").decide(proposal, assurance)
    assert decision.approved
    components = {
        "cognition.factorizer": {"artifact": "fp-inc"},
        "skill.future_reuse": {"artifact": "skill-v1", "depends_on": "cognition.factorizer"},
    }
    challenger, info = ledger.adopt(proposal, decision, incumbent, components)
    assert info["migration"]["revalidate"] == ["skill.future_reuse"]

    # M11 adoption is externally installed.  Persist that host installation as data, then restart
    # the OCM runtime and require the adoption ledger and the installed factorization to survive.
    install = root / f"host-installed-{strategy}.json"
    install.write_text(json.dumps(challenger, sort_keys=True))
    ledger.persist()
    rt2 = OCMRuntime(root)
    ledger2 = GV.AdoptionLedger.load(rt2)
    assert proposal.fingerprint() in ledger2.adoption_history
    assert ledger2.adoption_history[proposal.fingerprint()]["liveness"] == "LIVE"
    reloaded = json.loads(install.read_text())
    fresh = [{"id": f"fresh-{strategy}-{i}", "family": "target"} for i in range(8)]
    fresh_result = _runner(reloaded, fresh)
    assert fresh_result["success"] == fresh_result["n"]
    return fresh_result, len(install.read_bytes()), len(rt2.events)


def test_real_m11_restart_reuse_is_parent_sufficient(tmp_path):
    factor = _run_governed_bridge(tmp_path / "factor", "factor_local")
    parent = _run_governed_bridge(tmp_path / "parent", "symbolic_incremental_parent")
    assert factor[0] == parent[0]  # same fresh capability through the same governed lifecycle
    assert parent[1] <= factor[1]  # parent avoids the duplicate learned relevance cache
    assert factor[2] == parent[2]  # equal governance/event cost
    # Scientific terminal for this bridge is therefore PARENT_SUFFICIENT.

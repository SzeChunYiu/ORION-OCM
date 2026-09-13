"""Deterministic synthetic counterfactual assay for recursive evolvability."""
from __future__ import annotations

import json
from pathlib import Path
import importlib.util
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("gmi_rsi_model", HERE / "model.py")
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def rec(g, tq, sq, *, persistent=False, self_change=False, d_changed=False,
        d_digest="D0", machine_digest=None, parent=None, evaluator_changed=False,
        d_executed=True, machine_originated=True, externally_admitted=True):
    if machine_digest is None:
        machine_digest = "ROOT" if g == 0 else f"G{g}"
    return M.GenerationRecord(
        generation=g,
        task_quality=tq,
        shadow_quality=sq,
        persistent_change=persistent,
        self_change=self_change,
        development_operator_changed=d_changed,
        development_operator_digest=d_digest,
        machine_digest=machine_digest,
        parent_digest=parent,
        development_operator_executed=d_executed,
        machine_originated=machine_originated,
        externally_admitted=externally_admitted,
        evaluator_proxy_changed=evaluator_changed,
    )


def arms():
    matched = M.ResourceVector(compute=4.0, data=2.0, evaluator=1.0, human=0.0)
    frozen = M.AssayArm(
        name="FROZEN_D",
        root_machine_digest="ROOT",
        development_ecology="DEVELOPMENT_ECOLOGY_V1",
        held_out_ecology="HELD_OUT_DEVELOPMENTAL_ECOLOGY_V1",
        resources=matched,
        frozen_development_operator=True,
        shadow_evaluator_frozen=True,
        records=(
            rec(0, .50, .50),
            rec(1, .58, .58, persistent=True, self_change=True, parent="ROOT"),
            rec(2, .61, .61, persistent=True, self_change=True, parent="G1"),
            rec(3, .63, .63, persistent=True, self_change=True, parent="G2"),
        ),
    )
    mutable = M.AssayArm(
        name="MUTABLE_D",
        root_machine_digest="ROOT",
        development_ecology="DEVELOPMENT_ECOLOGY_V1",
        held_out_ecology="HELD_OUT_DEVELOPMENTAL_ECOLOGY_V1",
        resources=matched,
        frozen_development_operator=False,
        shadow_evaluator_frozen=True,
        records=(
            rec(0, .50, .50),
            # deliberate stepping stone: immediate quality falls while D changes
            rec(1, .47, .47, persistent=True, self_change=True, d_changed=True, d_digest="D1", parent="ROOT"),
            rec(2, .69, .69, persistent=True, self_change=True, d_digest="D1", parent="G1", d_executed=True),
            rec(3, .82, .82, persistent=True, self_change=True, d_digest="D1", parent="G2", d_executed=True),
        ),
    )
    fixed_d_self_edit = M.AssayArm(
        name="FIXED_D_SELF_EDIT",
        root_machine_digest="ROOT",
        development_ecology="DEVELOPMENT_ECOLOGY_V1",
        held_out_ecology="HELD_OUT_DEVELOPMENTAL_ECOLOGY_V1",
        resources=matched,
        frozen_development_operator=True,
        shadow_evaluator_frozen=True,
        records=(
            rec(0, .50, .50),
            rec(1, .66, .66, persistent=True, self_change=True, parent="ROOT"),
            rec(2, .73, .73, persistent=True, self_change=True, parent="G1"),
            rec(3, .77, .77, persistent=True, self_change=True, parent="G2"),
        ),
    )
    evaluator_gaming = M.AssayArm(
        name="EVALUATOR_GAMING",
        root_machine_digest="ROOT",
        development_ecology="DEVELOPMENT_ECOLOGY_V1",
        held_out_ecology="HELD_OUT_DEVELOPMENTAL_ECOLOGY_V1",
        resources=matched,
        frozen_development_operator=False,
        shadow_evaluator_frozen=False,
        records=(
            rec(0, .50, .50),
            rec(1, .90, .51, persistent=True, self_change=True, d_changed=True,
                d_digest="D_GAME", evaluator_changed=True, parent="ROOT"),
            rec(2, .97, .50, persistent=True, self_change=True, d_digest="D_GAME",
                evaluator_changed=True, parent="G1"),
        ),
    )
    extra_compute = M.AssayArm(
        name="EXTRA_COMPUTE",
        root_machine_digest="ROOT",
        development_ecology="DEVELOPMENT_ECOLOGY_V1",
        held_out_ecology="HELD_OUT_DEVELOPMENTAL_ECOLOGY_V1",
        resources=M.ResourceVector(compute=8.0, data=2.0, evaluator=1.0, human=0.0),
        frozen_development_operator=False,
        shadow_evaluator_frozen=True,
        records=(
            rec(0, .50, .50),
            rec(1, .65, .65, persistent=True, self_change=True, d_changed=True, d_digest="D_X", parent="ROOT"),
            rec(2, .79, .79, persistent=True, self_change=True, d_digest="D_X", parent="G1"),
        ),
    )
    return frozen, mutable, fixed_d_self_edit, evaluator_gaming, extra_compute


def run(out: Path | None = None):
    frozen, mutable, fixed_d, gaming, extra_compute = arms()
    result = {}
    for arm, comparator in (
        (frozen, None),
        (mutable, frozen),
        (fixed_d, frozen),
        (gaming, frozen),
        (extra_compute, frozen),
    ):
        assessment = M.classify(arm, frozen_comparator=comparator)
        result[arm.name] = {
            "level": assessment.level.name,
            "reasons": list(assessment.reasons),
            "metaproductivity": M.metaproductivity(arm),
            "best_descendant_shadow_quality": M.descendant_utility(arm),
            "meta_gain": None if assessment.meta_gain is None else assessment.meta_gain.__dict__,
            "strictly_accelerating": M.is_strictly_accelerating([r.shadow_quality for r in arm.records]),
        }
    result["terminal"] = "SYNTHETIC_PROTOCOL_BEHAVES_AS_REGISTERED_NO_EMPIRICAL_RSI_CLAIM"
    if out is not None:
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    run(HERE / "RESULT.json")

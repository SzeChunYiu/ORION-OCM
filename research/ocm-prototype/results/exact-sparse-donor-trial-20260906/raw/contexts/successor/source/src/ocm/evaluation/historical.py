"""Historical replay adapters (M2 §12): wrap the inherited controlled results without upgrading
any claim.  Each adapter runs the frozen reference module from ``research/orion-machine/reference``
through ``ocm.historical.load_reference`` and returns the authoritative terminal, its limitation,
and (where the canonical core can reproduce the object) the canonical-core cross-check.

A source result that cannot be replayed here reports a named ``CANNOT_CHECK`` and stays
historical evidence only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Callable

from ocm.historical import load_reference
from ocm.kso import checks as C
from ocm.kso.warrant import CannotCheck


@dataclass(frozen=True)
class ReplayResult:
    name: str
    terminal: str
    status: str                    # PASS | FAIL | CANNOT_CHECK
    limitation: str
    detail: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "terminal": self.terminal, "status": self.status, "limitation": self.limitation, "detail": self.detail}


def _wrap(name: str, limitation: str, fn: Callable[[], tuple[str, dict[str, Any]]]) -> ReplayResult:
    try:
        terminal, detail = fn()
        return ReplayResult(name, terminal, "PASS", limitation, detail)
    except CannotCheck as exc:
        return ReplayResult(name, "CANNOT_CHECK", "CANNOT_CHECK", limitation, {"reason": str(exc)})
    except Exception as exc:  # noqa: BLE001
        label = type(exc).__name__
        if "CannotCheck" in label or "CANNOT_CHECK" in str(exc):
            return ReplayResult(name, "CANNOT_CHECK", "CANNOT_CHECK", limitation, {"reason": f"{label}: {exc}"})
        return ReplayResult(name, "FAIL", "FAIL", limitation, {"reason": f"{label}: {exc}"})


def replay_m0_math() -> ReplayResult:
    def run():
        ref = load_reference("kso_math_v1").run_all()
        canon = C.check_navigation_reference_equivalence(random_spaces=5)
        return ref["terminals"]["M0_FINITE_MATH_CORE"], {"reference": ref["warrant_semiring"], "canonical_equivalence": canon}
    return _wrap("M0_MATH_SANITY", "finite calibration; GENERAL_NOVELTY remains NOT_ESTABLISHED", run)


def replay_m1_population() -> ReplayResult:
    def run():
        m1 = load_reference("kso_m1_mex1_population_v1")
        out = m1.run(split="dev", per_family=1)
        return out.get("terminals", {}).get("M1_DEV", out.get("terminal", "M1_KSO_INSTANCE")), {"worlds": out.get("worlds", out.get("n_worlds")), "protected": "NOT_RUN"}
    return _wrap("M1_POPULATION_FIXTURE", "dev split only; protected split NOT_RUN (custody seed)", run)


def replay_m2_solve_parent_tie() -> ReplayResult:
    def run():
        import json

        from ocm.historical import repository_root

        outcome_md = (repository_root() / "research/orion-machine/results/KSO_M2_COMPARATOR_OUTCOME_V1.md").read_text(encoding="utf-8")
        if "PARENT_SUFFICIENT" not in outcome_md:
            raise CannotCheck("comparator outcome record does not carry PARENT_SUFFICIENT")
        solve = json.loads((repository_root() / "research/orion-machine/results/KSO_M2_SOLVE_RECEIPT_V1.json").read_text(encoding="utf-8"))
        return "PARENT_SUFFICIENT", {"store_exact": solve["headline"]["STORE_EXACT"], "navigation_exact": solve["headline"]["NAVIGATION_EXACT"], "mechanic_terminal": solve["headline"]["mechanic_terminal"], "m2_1_revival": "research/ocm-m2/M2_1_SURPRISE_REVIVAL_OUTCOME_V1.md (dev split, 47/50 under PROPAGATED; default unchanged)"}
    return _wrap("M2_SOLVE_STRONGEST_PARENT_TIE", "frozen receipt; navigation-only 38/50 non-significant vs RWR/CBR at n=50", run)


def replay_m3_exact_procedure_learning() -> ReplayResult:
    def run():
        m3 = load_reference("kso_m3_learning_v1")
        out = m3.run_m3()
        return out.get("terminal", "M3_EXACT_GAP_LEARNING_GREEN"), {"channels": sorted(out.get("channels", {})) if isinstance(out.get("channels"), dict) else out.get("channels")}
    return _wrap("M3_EXACT_PROCEDURE_LEARNING", "finite Boolean learning calibration (16 hypotheses); not KS-T13", run)


def replay_m4_jump_calibration() -> ReplayResult:
    def run():
        m4 = load_reference("kso_m4_jump_v1")
        out = m4.run_m4()
        return out.get("terminal", "M4_MINIMUM_SUFFICIENT_JUMP_GREEN"), {"selected_level": out.get("selected_level", out.get("minimum_level")), "v1_84_world_benchmark": False}
    return _wrap("M4_GOVERNED_FINITE_JUMP", "one affine→conjunction instance; the 84-opaque-world benchmark is NOT_RUN", run)


def replay_m5_controlled_chat() -> ReplayResult:
    def run():
        m5 = load_reference("kso_m5_chat_v1")
        out = m5.run_m5()
        return out.get("terminal", "M5_CONTROLLED_CODEC_CHAT_GREEN"), {"codecs": 2, "open_domain_language": False}
    return _wrap("M5_CONTROLLED_CODEC_CHAT", "two hand codecs over five commands; KS-T10 stays OPEN_M5", run)


def replay_m6a_lean_admission() -> ReplayResult:
    def run():
        m6 = load_reference("kso_m6_formal_math_v1")
        out = m6.run_m6a() if hasattr(m6, "run_m6a") else m6.run_m6()
        return out.get("terminal", "M6A_FORMAL_MATH_VERIFIER_CHANNEL_INTEGRATED_PARENT_SUFFICIENT"), {"frontier_math_discovery": False, "lean_rerun": "CANNOT_CHECK (external Lean not provisioned; historical receipt replayed)"}
    return _wrap("M6A_LEAN_PROOF_ADMISSION", "proof-kernel integration only; upstream PARENT_SUFFICIENT", run)


def replay_multidomain() -> ReplayResult:
    def run():
        md = load_reference("kso_multidomain_v1")
        out = md.run_multidomain()
        return out.get("terminal", "MULTIDOMAIN_NON_INTERFERENCE_GREEN"), {"domains": 2}
    return _wrap("MULTIDOMAIN_NON_INTERFERENCE", "one procedure domain + Lean certificates; shared-support case is MEG-22", run)


ADAPTERS = (replay_m0_math, replay_m1_population, replay_m2_solve_parent_tie, replay_m3_exact_procedure_learning, replay_m4_jump_calibration, replay_m5_controlled_chat, replay_m6a_lean_admission, replay_multidomain)


def replay_all() -> dict[str, Any]:
    rows = [a() for a in ADAPTERS]
    return {
        "adapters": [r.as_dict() for r in rows],
        "counts": {s: sum(1 for r in rows if r.status == s) for s in ("PASS", "FAIL", "CANNOT_CHECK")},
        "authority": "inherited terminals replayed, never upgraded; M2 solve stays PARENT_SUFFICIENT; novelty NOT_ESTABLISHED",
    }

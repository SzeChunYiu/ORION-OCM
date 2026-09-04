"""Wisdom + Method KSO V0 — contextual principles bias method selection, never mint answers.

Finite calibration of four distinct layers:

    cultural artifact -> interpretation -> defeasible principle -> executable method

The same governed KnowledgeSpace/warrant machinery used by other KSO prototypes stores these
objects. A famous quotation remains present even if an interpretation is revoked; only the
dependent principle loses liveness. Competing principles may coexist. Task context determines
which live principles apply, and they can bias method selection without supplying the task answer.

No moral/cultural universality or novelty claim. Exit: 0 controlled pass, 1 defect.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

HERE = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


m0 = _load("kso_m0_freeze_checks_v1", HERE / "kso_m0_freeze_checks_v1.py")
kso = m0.kso
ONE = m0.ONE


@dataclass(frozen=True)
class CulturalArtifact:
    artifact_id: str
    text: str
    culture: str
    source: str
    language: str
    evidence_id: int


@dataclass(frozen=True)
class Interpretation:
    interpretation_id: str
    artifact_id: str
    principle_id: str
    reading: str
    applicability_tags: frozenset[str]
    evidence_id: int


@dataclass(frozen=True)
class PrincipleCapsule:
    principle_id: str
    name: str
    interpretation_id: str
    applicability_tags: frozenset[str]
    supports_method_tags: frozenset[str] = frozenset()
    opposes_method_tags: frozenset[str] = frozenset()


@dataclass(frozen=True)
class MethodCapsule:
    method_id: str
    name: str
    applicability_tags: frozenset[str]
    method_tags: frozenset[str]
    steps: tuple[str, ...]
    evidence_id: int
    base_score: int = 0


@dataclass(frozen=True)
class TaskContext:
    task_id: str
    tags: frozenset[str]
    uncertainty: float
    marginal_information_value: float
    action_risk: float
    valid_information_actions: int


@dataclass(frozen=True)
class MethodSelection:
    task_id: str
    selected_method: str
    active_principles: tuple[str, ...]
    scores: tuple[tuple[str, int], ...]
    thought_trace: tuple[str, ...]


@dataclass
class WisdomMethodKSO:
    space: object = field(init=False)
    revoked: set[int] = field(default_factory=set)
    artifacts: dict[str, CulturalArtifact] = field(default_factory=dict)
    interpretations: dict[str, Interpretation] = field(default_factory=dict)
    principles: dict[str, PrincipleCapsule] = field(default_factory=dict)
    methods: dict[str, MethodCapsule] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.space = kso.KnowledgeSpace(
            (
                kso.Atom("wisdom:root", "wisdom_root", ONE),
                kso.Atom("methods:root", "method_root", ONE),
            ),
            (
                kso.Hyperedge("wisdom-to-methods", ("wisdom:root",), ("methods:root",), "SUPPORT", profile=ONE),
            ),
        )
        self.space.validate()

    def _admit(self, atom, edge, certificate=m0.CertificateKind.INSTRUCTION) -> None:
        self.space, rec = m0.admit(self.space, atom, (edge,), certificate, revoked=self.revoked)
        if not rec.reachable_by_navigation:
            raise RuntimeError(f"unreachable admitted atom: {atom.atom_id}")

    def add_artifact(self, a: CulturalArtifact) -> None:
        if a.artifact_id in self.artifacts:
            raise ValueError("duplicate artifact")
        atom_id = f"artifact:{a.artifact_id}"
        self._admit(
            kso.Atom(atom_id, "cultural_artifact", (frozenset({a.evidence_id}),)),
            kso.Hyperedge(f"edge:{atom_id}", ("wisdom:root",), (atom_id,), "SUPPORT", profile=ONE),
        )
        self.artifacts[a.artifact_id] = a

    def add_interpretation(self, i: Interpretation) -> None:
        if i.interpretation_id in self.interpretations:
            raise ValueError("duplicate interpretation")
        a = self.artifacts[i.artifact_id]
        atom_id = f"interpretation:{i.interpretation_id}"
        profile = (frozenset({a.evidence_id, i.evidence_id}),)
        self._admit(
            kso.Atom(atom_id, "interpretation", profile),
            kso.Hyperedge(
                f"edge:{atom_id}",
                (f"artifact:{a.artifact_id}",),
                (atom_id,),
                "SUPPORT",
                profile=ONE,
            ),
        )
        self.interpretations[i.interpretation_id] = i

    def add_principle(self, p: PrincipleCapsule) -> None:
        if p.principle_id in self.principles:
            raise ValueError("duplicate principle")
        i = self.interpretations[p.interpretation_id]
        source = self.space.atom_map()[f"interpretation:{i.interpretation_id}"]
        atom_id = f"principle:{p.principle_id}"
        self._admit(
            kso.Atom(atom_id, "principle", source.profile),
            kso.Hyperedge(
                f"edge:{atom_id}",
                (f"interpretation:{i.interpretation_id}",),
                (atom_id,),
                "SUPPORT",
                profile=ONE,
            ),
        )
        self.principles[p.principle_id] = p

    def add_method(self, m: MethodCapsule) -> None:
        if m.method_id in self.methods:
            raise ValueError("duplicate method")
        atom_id = f"method:{m.method_id}"
        self._admit(
            kso.Atom(atom_id, "method", (frozenset({m.evidence_id}),)),
            kso.Hyperedge(f"edge:{atom_id}", ("methods:root",), (atom_id,), "COMPOSITION", profile=ONE),
        )
        self.methods[m.method_id] = m

    def artifact_live(self, artifact_id: str) -> bool:
        return kso.profile_live(self.space.atom_map()[f"artifact:{artifact_id}"].profile, self.revoked)

    def interpretation_live(self, interpretation_id: str) -> bool:
        return kso.profile_live(self.space.atom_map()[f"interpretation:{interpretation_id}"].profile, self.revoked)

    def principle_live(self, principle_id: str) -> bool:
        return kso.profile_live(self.space.atom_map()[f"principle:{principle_id}"].profile, self.revoked)

    def method_live(self, method_id: str) -> bool:
        return kso.profile_live(self.space.atom_map()[f"method:{method_id}"].profile, self.revoked)

    def revoke(self, evidence_id: int) -> None:
        self.revoked.add(evidence_id)

    def reinstate(self, evidence_id: int) -> None:
        self.revoked.discard(evidence_id)

    def applicable_principles(self, task: TaskContext) -> tuple[PrincipleCapsule, ...]:
        rows = []
        for p in self.principles.values():
            if not self.principle_live(p.principle_id):
                continue
            if p.applicability_tags <= task.tags:
                rows.append(p)
        return tuple(sorted(rows, key=lambda x: x.principle_id))

    def select_method(self, task: TaskContext) -> MethodSelection:
        active = self.applicable_principles(task)
        scores: list[tuple[int, str, MethodCapsule]] = []
        trace = [
            f"task={task.task_id}",
            f"uncertainty={task.uncertainty:.2f}",
            f"marginal_information_value={task.marginal_information_value:.2f}",
            f"action_risk={task.action_risk:.2f}",
            "active_principles=" + ",".join(p.principle_id for p in active),
        ]
        for m in self.methods.values():
            if not self.method_live(m.method_id) or not (m.applicability_tags <= task.tags):
                continue
            score = m.base_score
            reasons = []
            for p in active:
                plus = len(p.supports_method_tags & m.method_tags)
                minus = len(p.opposes_method_tags & m.method_tags)
                score += 3 * plus - 4 * minus
                if plus or minus:
                    reasons.append(f"{p.principle_id}:{+3*plus-4*minus}")
            # Task-state signals are explicit rather than hidden in proverb text.
            if "gather-evidence" in m.method_tags:
                if task.valid_information_actions > 0:
                    score += round(5 * task.marginal_information_value)
                else:
                    score -= 8
                score -= round(3 * task.action_risk)
            if "stop-unknown" in m.method_tags:
                score += round(4 * (1.0 - task.marginal_information_value))
                score += round(2 * task.action_risk)
            if "unsupported-guess" in m.method_tags:
                score -= round(6 * task.uncertainty)
            trace.append(f"method={m.method_id};score={score};principle_terms={','.join(reasons) or 'none'}")
            scores.append((-score, m.method_id, m))
        if not scores:
            raise RuntimeError("no applicable live method")
        scores.sort(key=lambda x: (x[0], x[1]))
        selected = scores[0][2]
        score_rows = tuple((m.method_id, -neg) for neg, _, m in sorted(scores, key=lambda x: x[1]))
        trace.append(f"selected={selected.method_id}")
        return MethodSelection(
            task.task_id,
            selected.method_id,
            tuple(p.principle_id for p in active),
            score_rows,
            tuple(trace),
        )


def build_demo_space() -> WisdomMethodKSO:
    w = WisdomMethodKSO()

    # Public-domain classical / traditional sayings are stored as artifacts, not as universal rules.
    w.add_artifact(
        CulturalArtifact(
            "analects-known-unknown",
            "知之為知之，不知為不知，是知也",
            "Chinese",
            "Analects, Weizheng",
            "zh",
            1001,
        )
    )
    w.add_interpretation(
        Interpretation(
            "analects-epistemic-humility",
            "analects-known-unknown",
            "epistemic-humility",
            "Treat known, unknown, and unverified states distinctly; do not manufacture certainty.",
            frozenset({"uncertain"}),
            1101,
        )
    )
    w.add_principle(
        PrincipleCapsule(
            "epistemic-humility",
            "Epistemic humility",
            "analects-epistemic-humility",
            frozenset({"uncertain"}),
            supports_method_tags=frozenset({"gather-evidence", "stop-unknown"}),
            opposes_method_tags=frozenset({"unsupported-guess"}),
        )
    )

    w.add_artifact(
        CulturalArtifact(
            "keep-advancing",
            "百尺竿頭，更進一步",
            "Chinese",
            "traditional maxim; later Song/Yuan attestations",
            "zh",
            1002,
        )
    )
    w.add_interpretation(
        Interpretation(
            "keep-advancing-perseverance",
            "keep-advancing",
            "perseverance",
            "Do not stop solely because substantial progress has already been achieved when worthwhile progress remains possible.",
            frozenset({"search-open", "valuable-next-step"}),
            1102,
        )
    )
    w.add_principle(
        PrincipleCapsule(
            "perseverance",
            "Continue when a worthwhile next step exists",
            "keep-advancing-perseverance",
            frozenset({"search-open", "valuable-next-step"}),
            supports_method_tags=frozenset({"gather-evidence"}),
        )
    )

    w.add_artifact(
        CulturalArtifact(
            "look-before-leap",
            "Look before you leap",
            "English",
            "traditional English proverb",
            "en",
            1003,
        )
    )
    w.add_interpretation(
        Interpretation(
            "look-before-leap-restraint",
            "look-before-leap",
            "restraint",
            "Avoid costly or risky commitment when the expected value of acting is low or uncertainty is unresolved.",
            frozenset({"high-risk"}),
            1103,
        )
    )
    w.add_principle(
        PrincipleCapsule(
            "restraint",
            "Restraint under risk",
            "look-before-leap-restraint",
            frozenset({"high-risk"}),
            supports_method_tags=frozenset({"stop-unknown"}),
            opposes_method_tags=frozenset({"aggressive-action"}),
        )
    )

    w.add_method(
        MethodCapsule(
            "safe-probe",
            "Acquire one discriminating piece of evidence",
            frozenset({"uncertain"}),
            frozenset({"gather-evidence"}),
            ("identify discriminating observation", "acquire it within budget", "recompute hypotheses"),
            2001,
            base_score=1,
        )
    )
    w.add_method(
        MethodCapsule(
            "report-unknown",
            "Stop and report the unresolved state",
            frozenset({"uncertain"}),
            frozenset({"stop-unknown"}),
            ("state what is known", "state what is unknown", "name the missing evidence"),
            2002,
            base_score=1,
        )
    )
    w.add_method(
        MethodCapsule(
            "guess",
            "Commit to an unsupported guess",
            frozenset({"uncertain"}),
            frozenset({"unsupported-guess", "aggressive-action"}),
            ("choose a candidate without additional evidence",),
            2003,
            base_score=2,
        )
    )
    return w


def run_wisdom_methods_v0() -> dict[str, object]:
    w = build_demo_space()

    productive = TaskContext(
        "open-search",
        frozenset({"uncertain", "search-open", "valuable-next-step"}),
        uncertainty=0.9,
        marginal_information_value=0.9,
        action_risk=0.1,
        valid_information_actions=2,
    )
    p = w.select_method(productive)
    assert p.selected_method == "safe-probe"
    assert set(p.active_principles) == {"epistemic-humility", "perseverance"}

    risky = TaskContext(
        "unsafe-search",
        frozenset({"uncertain", "high-risk"}),
        uncertainty=0.9,
        marginal_information_value=0.05,
        action_risk=0.95,
        valid_information_actions=0,
    )
    r = w.select_method(risky)
    assert r.selected_method == "report-unknown"
    assert set(r.active_principles) == {"epistemic-humility", "restraint"}

    # Revoking an interpretation disables its derived principle, not the historical artifact.
    assert w.artifact_live("analects-known-unknown")
    assert w.principle_live("epistemic-humility")
    w.revoke(1101)
    assert w.artifact_live("analects-known-unknown")
    assert not w.interpretation_live("analects-epistemic-humility")
    assert not w.principle_live("epistemic-humility")
    after_revoke = w.select_method(productive)
    assert "epistemic-humility" not in after_revoke.active_principles
    assert after_revoke.selected_method == "safe-probe"  # perseverance still supports the method.
    w.reinstate(1101)
    assert w.principle_live("epistemic-humility")

    # The quotation text is never read by the selector: mutate the stored prose in a copy and the
    # selection contract is unchanged because method choice runs on explicit principle semantics.
    original = w.artifacts["keep-advancing"]
    w.artifacts["keep-advancing"] = CulturalArtifact(
        original.artifact_id,
        "[surface wording intentionally replaced for hostile control]",
        original.culture,
        original.source,
        original.language,
        original.evidence_id,
    )
    p2 = w.select_method(productive)
    assert p2.selected_method == p.selected_method and p2.active_principles == p.active_principles

    return {
        "terminal": "WISDOM_METHOD_KSO_V0_CONTROLLED_GREEN",
        "productive_search": {
            "active_principles": list(p.active_principles),
            "selected_method": p.selected_method,
            "scores": dict(p.scores),
            "thought_trace": list(p.thought_trace),
        },
        "high_risk_low_value": {
            "active_principles": list(r.active_principles),
            "selected_method": r.selected_method,
            "scores": dict(r.scores),
        },
        "revocation": {
            "artifact_survives_interpretation_revocation": True,
            "dependent_principle_dies": True,
            "unrelated_perseverance_still_selects_safe_probe": after_revoke.selected_method == "safe-probe",
            "reinstatement_restores_principle": w.principle_live("epistemic-humility"),
        },
        "hostile": {
            "quotation_surface_text_not_used_as_method_selector": True,
            "unsupported_guess_not_selected": p.selected_method != "guess" and r.selected_method != "guess",
        },
        "counts": {
            "artifacts": len(w.artifacts),
            "interpretations": len(w.interpretations),
            "principles": len(w.principles),
            "methods": len(w.methods),
        },
        "authority": {
            "universal_wisdom_claim": False,
            "moral_truth_claim": False,
            "cross_cultural_equivalence_claim": False,
            "general_method_intelligence": False,
            "novelty": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path)
    a = p.parse_args(argv)
    try:
        result = run_wisdom_methods_v0()
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"terminal": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1
    text = json.dumps(result, indent=2, sort_keys=True)
    if a.out:
        a.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

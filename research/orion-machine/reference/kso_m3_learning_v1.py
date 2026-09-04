"""KSO M3 — exact procedure acquisition, compositional reuse, and lifecycle correction.

This is a finite executable calibration of the operator directive: the machine learns a reusable
procedure from instruction, demonstration, interaction, experimentation, or feedback; the first
four can earn warrant under an exact registered finite contract, while feedback alone cannot.

The learning target is a Boolean binary operator on D={00,01,10,11}. The learner starts from the
full 16-function version space. It receives only the channel interface exposed by the selected
method. Learned primitive semantics are then used in held-out compositions that were never part
of the lesson. Revoking the lesson's evidence disables the learned procedure and its composites.

This is a mechanism calibration, not evidence of open-domain learning or language competence.
Exit: 0 pass, 1 fail, 2 CANNOT_CHECK.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence

DOMAIN: tuple[tuple[int, int], ...] = ((0, 0), (0, 1), (1, 0), (1, 1))
ALL_TABLES: tuple[tuple[int, ...], ...] = tuple(itertools.product((0, 1), repeat=4))
TARGET_AND: tuple[int, ...] = (0, 0, 0, 1)


class CannotCheck(RuntimeError):
    pass


class Channel(str, Enum):
    INSTRUCTION = "INSTRUCTION"
    DEMONSTRATION = "DEMONSTRATION"
    INTERACTION = "INTERACTION"
    EXPERIMENTATION = "EXPERIMENTATION"
    FEEDBACK = "FEEDBACK"


WARRANTING = frozenset({Channel.INSTRUCTION, Channel.DEMONSTRATION, Channel.INTERACTION, Channel.EXPERIMENTATION})


@dataclass(frozen=True)
class Example:
    x: tuple[int, int]
    y: int


@dataclass(frozen=True)
class Lesson:
    name: str
    channel: Channel
    evidence_id: int
    examples: tuple[Example, ...] = ()
    declared_table: tuple[int, ...] = ()
    endpoint_feedback: tuple[tuple[str, int], ...] = ()


@dataclass(frozen=True)
class LearnedProcedure:
    name: str
    table: tuple[int, ...]
    evidence_id: int
    channel: Channel
    complete: bool = True

    def live(self, revoked: Iterable[int] = ()) -> bool:
        return self.evidence_id not in frozenset(revoked)

    def apply(self, x: tuple[int, int], revoked: Iterable[int] = ()) -> int:
        if not self.live(revoked):
            raise CannotCheck(f"procedure {self.name} is not live")
        return self.table[DOMAIN.index(x)]


@dataclass(frozen=True)
class LearningReceipt:
    channel: Channel
    initial_hypotheses: int
    final_hypotheses: int
    observations: int
    learned: LearnedProcedure | None
    warranted: bool
    status: str
    information_trace: tuple[Example, ...] = ()


class BlindTeacher:
    """Query-only interface. The learner never receives the target table object."""

    def __init__(self, answer_fn: Callable[[tuple[int, int]], int]):
        self._answer = answer_fn
        self.calls: list[tuple[int, int]] = []

    def answer(self, x: tuple[int, int]) -> int:
        self.calls.append(x)
        return int(self._answer(x))


def table_apply(table: Sequence[int], x: tuple[int, int]) -> int:
    if len(table) != 4 or any(v not in (0, 1) for v in table):
        raise ValueError("a Boolean binary table needs four 0/1 outputs")
    return int(table[DOMAIN.index(x)])


def version_space(examples: Iterable[Example], candidates: Sequence[tuple[int, ...]] = ALL_TABLES) -> tuple[tuple[int, ...], ...]:
    ex = tuple(examples)
    return tuple(t for t in candidates if all(table_apply(t, e.x) == e.y for e in ex))


def _learn_if_unique(name: str, channel: Channel, evidence_id: int, examples: Sequence[Example]) -> LearningReceipt:
    vs = version_space(examples)
    if len(vs) != 1:
        return LearningReceipt(channel, len(ALL_TABLES), len(vs), len(examples), None, False, "GAP_AMBIGUOUS", tuple(examples))
    proc = LearnedProcedure(name, vs[0], evidence_id, channel, True)
    return LearningReceipt(channel, len(ALL_TABLES), 1, len(examples), proc, True, "LEARNED_WARRANTED", tuple(examples))


def learn_instruction(lesson: Lesson) -> LearningReceipt:
    if lesson.channel is not Channel.INSTRUCTION:
        raise ValueError("wrong channel")
    if len(lesson.declared_table) != 4:
        return LearningReceipt(Channel.INSTRUCTION, 16, 16, 0, None, False, "CANNOT_CHECK_INCOMPLETE_RULE")
    examples = tuple(Example(x, table_apply(lesson.declared_table, x)) for x in DOMAIN)
    return _learn_if_unique(lesson.name, Channel.INSTRUCTION, lesson.evidence_id, examples)


def learn_demonstration(lesson: Lesson) -> LearningReceipt:
    if lesson.channel is not Channel.DEMONSTRATION:
        raise ValueError("wrong channel")
    return _learn_if_unique(lesson.name, Channel.DEMONSTRATION, lesson.evidence_id, lesson.examples)


def _best_query(vs: Sequence[tuple[int, ...]], asked: frozenset[tuple[int, int]]) -> tuple[int, int]:
    options = []
    for x in DOMAIN:
        if x in asked:
            continue
        n0 = sum(table_apply(t, x) == 0 for t in vs)
        n1 = len(vs) - n0
        options.append((max(n0, n1), abs(n0 - n1), DOMAIN.index(x), x))
    if not options:
        raise CannotCheck("no unasked query can refine a non-singleton version space")
    return min(options)[-1]


def learn_interaction(name: str, evidence_id: int, teacher: BlindTeacher) -> LearningReceipt:
    vs: tuple[tuple[int, ...], ...] = ALL_TABLES
    trace: list[Example] = []
    asked: set[tuple[int, int]] = set()
    while len(vs) > 1:
        x = _best_query(vs, frozenset(asked))
        asked.add(x)
        e = Example(x, teacher.answer(x))
        trace.append(e)
        vs = version_space(trace)
        if not vs:
            raise CannotCheck("teacher answers are inconsistent with the registered hypothesis class")
    proc = LearnedProcedure(name, vs[0], evidence_id, Channel.INTERACTION, True)
    return LearningReceipt(Channel.INTERACTION, 16, 1, len(trace), proc, True, "LEARNED_WARRANTED", tuple(trace))


def learn_experimentation(name: str, evidence_id: int, sandbox: BlindTeacher) -> LearningReceipt:
    trace = tuple(Example(x, sandbox.answer(x)) for x in DOMAIN)
    rec = _learn_if_unique(name, Channel.EXPERIMENTATION, evidence_id, trace)
    if rec.learned is None:
        raise CannotCheck("complete experimental trace failed to identify a finite function")
    return rec


def learn_feedback(lesson: Lesson) -> LearningReceipt:
    if lesson.channel is not Channel.FEEDBACK:
        raise ValueError("wrong channel")
    return LearningReceipt(Channel.FEEDBACK, 16, 16, len(lesson.endpoint_feedback), None, False, "FEEDBACK_RECORDED_UNWARRANTED", ())


KNOWN_UNARY: Mapping[str, Callable[[int, tuple[int, int]], int]] = {
    "IDENTITY": lambda z, x: z,
    "NOT": lambda z, x: 1 - z,
    "XOR_A": lambda z, x: z ^ x[0],
}
PROGRAMS: tuple[str, ...] = ("IDENTITY", "NOT", "XOR_A")


def execute_composite(proc: LearnedProcedure | None, program: str, x: tuple[int, int], revoked: Iterable[int] = ()) -> tuple[str, int | None]:
    if proc is None:
        return ("GAP_UNKNOWN_PROCEDURE", None)
    if program not in KNOWN_UNARY:
        return ("GAP_UNKNOWN_COMBINATOR", None)
    if not proc.live(revoked):
        return ("GAP_REVOKED_PROCEDURE", None)
    z = proc.apply(x, revoked)
    return ("PASS", int(KNOWN_UNARY[program](z, x)))


def heldout_composition_score(proc: LearnedProcedure | None, target_table: Sequence[int], revoked: Iterable[int] = ()) -> tuple[int, int]:
    correct = total = 0
    for p in PROGRAMS:
        for x in DOMAIN:
            total += 1
            status, got = execute_composite(proc, p, x, revoked)
            expected = int(KNOWN_UNARY[p](table_apply(target_table, x), x))
            correct += int(status == "PASS" and got == expected)
    return correct, total


@dataclass
class ProcedureStore:
    procedures: dict[str, LearnedProcedure] = field(default_factory=dict)
    utility_feedback: dict[str, int] = field(default_factory=dict)
    revoked: set[int] = field(default_factory=set)

    def admit(self, receipt: LearningReceipt) -> bool:
        if receipt.learned is None or not receipt.warranted:
            return False
        self.procedures[receipt.learned.name] = receipt.learned
        return True

    def revoke(self, evidence_id: int) -> None:
        self.revoked.add(evidence_id)

    def reinstate(self, evidence_id: int) -> None:
        self.revoked.discard(evidence_id)

    def run(self, name: str, program: str, x: tuple[int, int]) -> tuple[str, int | None]:
        return execute_composite(self.procedures.get(name), program, x, self.revoked)


def integrate_into_kso(receipt: LearningReceipt):
    """Bind an M3 receipt to the frozen M0 acquisition transaction."""
    here = Path(__file__).resolve().parent

    def load(name, path):
        if name in sys.modules:
            return sys.modules[name]
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise CannotCheck(f"cannot import {path}")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod

    kso = load("kso_math_v1", here / "kso_math_v1.py")
    m0 = load("kso_m0_freeze_checks_v1", here / "kso_m0_freeze_checks_v1.py")
    one = (frozenset(),)
    base = kso.KnowledgeSpace(
        (kso.Atom("proc:library", "procedure", one), kso.Atom("goal:learn", "goal", one)),
        (kso.Hyperedge("library-goal", ("goal:learn",), ("proc:library",), "DEPENDENCE", profile=one),),
    )
    channel_map = {
        Channel.INSTRUCTION: m0.CertificateKind.INSTRUCTION,
        Channel.DEMONSTRATION: m0.CertificateKind.DEMONSTRATION,
        Channel.INTERACTION: m0.CertificateKind.INTERACTION,
        Channel.EXPERIMENTATION: m0.CertificateKind.EXPERIMENTATION,
        Channel.FEEDBACK: m0.CertificateKind.FEEDBACK,
    }
    name = receipt.learned.name if receipt.learned else "feedback:observation"
    profile = (frozenset({receipt.learned.evidence_id}),) if receipt.learned else one
    atom = kso.Atom(f"proc:{name}", "procedure", profile)
    edge = kso.Hyperedge(f"edge:{name}", ("proc:library",), (f"proc:{name}",), "COMPOSITION", profile=one)
    ks, adm = m0.admit(base, atom, (edge,), channel_map[receipt.channel])
    return ks, adm


def _teacher_for(table: tuple[int, ...]) -> BlindTeacher:
    return BlindTeacher(lambda x: table_apply(table, x))


def run_m3() -> dict[str, object]:
    evidence = {c: 100 + i for i, c in enumerate(Channel)}
    lessons = {
        Channel.INSTRUCTION: Lesson("AND", Channel.INSTRUCTION, evidence[Channel.INSTRUCTION], declared_table=TARGET_AND),
        Channel.DEMONSTRATION: Lesson("AND", Channel.DEMONSTRATION, evidence[Channel.DEMONSTRATION], examples=tuple(Example(x, table_apply(TARGET_AND, x)) for x in DOMAIN)),
        Channel.FEEDBACK: Lesson("AND", Channel.FEEDBACK, evidence[Channel.FEEDBACK], endpoint_feedback=(("episode-1", 1), ("episode-2", 0))),
    }
    recs: dict[Channel, LearningReceipt] = {}
    recs[Channel.INSTRUCTION] = learn_instruction(lessons[Channel.INSTRUCTION])
    recs[Channel.DEMONSTRATION] = learn_demonstration(lessons[Channel.DEMONSTRATION])
    ti = _teacher_for(TARGET_AND)
    recs[Channel.INTERACTION] = learn_interaction("AND", evidence[Channel.INTERACTION], ti)
    te = _teacher_for(TARGET_AND)
    recs[Channel.EXPERIMENTATION] = learn_experimentation("AND", evidence[Channel.EXPERIMENTATION], te)
    recs[Channel.FEEDBACK] = learn_feedback(lessons[Channel.FEEDBACK])

    rows = {}
    for c, r in recs.items():
        score, total = heldout_composition_score(r.learned, TARGET_AND)
        rows[c.value] = {
            "status": r.status,
            "warranted": r.warranted,
            "observations": r.observations,
            "final_hypotheses": r.final_hypotheses,
            "heldout_composition_exact": score,
            "heldout_composition_total": total,
        }

    incomplete = Lesson("AND", Channel.DEMONSTRATION, 999, examples=tuple(Example(x, table_apply(TARGET_AND, x)) for x in DOMAIN[:3]))
    bad_demo = learn_demonstration(incomplete)
    assert bad_demo.learned is None and bad_demo.final_hypotheses == 2
    assert all(recs[c].learned is not None and recs[c].warranted for c in WARRANTING)
    assert recs[Channel.FEEDBACK].learned is None and not recs[Channel.FEEDBACK].warranted
    assert rows[Channel.FEEDBACK.value]["heldout_composition_exact"] == 0
    assert all(rows[c.value]["heldout_composition_exact"] == 12 for c in WARRANTING)

    lifecycle = {}
    for c in sorted(WARRANTING, key=lambda x: x.value):
        p = recs[c].learned
        assert p is not None
        pre = heldout_composition_score(p, TARGET_AND)
        dead = heldout_composition_score(p, TARGET_AND, {p.evidence_id})
        post = heldout_composition_score(p, TARGET_AND)
        assert pre == (12, 12) and dead == (0, 12) and post == (12, 12)
        lifecycle[c.value] = {"pre": pre[0], "after_revoke": dead[0], "after_reinstate": post[0]}

    integration = {}
    for c, r in recs.items():
        ks, adm = integrate_into_kso(r)
        integration[c.value] = {
            "warranted": bool(adm.warranted),
            "edges_added": adm.edges_added,
            "profile_live": bool(ks.atom_map()[adm.atom_id].profile),
        }
    assert all(integration[c.value]["warranted"] and integration[c.value]["profile_live"] for c in WARRANTING)
    assert not integration[Channel.FEEDBACK.value]["warranted"] and not integration[Channel.FEEDBACK.value]["profile_live"]

    return {
        "terminal": "M3_EXACT_GAP_LEARNING_GREEN",
        "target": "AND",
        "hypothesis_space": 16,
        "channels": rows,
        "interaction_queries": len(ti.calls),
        "experiments": len(te.calls),
        "hostiles": {"incomplete_demo_final_hypotheses": bad_demo.final_hypotheses, "feedback_false_warrant": 0},
        "lifecycle": lifecycle,
        "m0_integration": integration,
        "authority": {"open_domain_learning": False, "novelty": False, "M4": False, "M5": False, "M6": False},
    }


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out")
    args = p.parse_args(argv)
    try:
        result = run_m3()
        if args.out:
            Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True))
        return 0
    except CannotCheck as exc:
        print(json.dumps({"terminal": "CANNOT_CHECK", "reason": str(exc)}))
        return 2
    except Exception as exc:
        print(json.dumps({"terminal": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

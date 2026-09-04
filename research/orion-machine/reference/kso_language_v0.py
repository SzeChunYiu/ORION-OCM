"""Language KSO L0 — exact grammar/construction acquisition and coarse-to-fine realization.

This is a controlled language-mechanism calibration, not an open-domain language model.
It makes the user's sketch->detail idea executable:

    semantic frame -> sentence construction -> phrase slots -> lexicalization
    -> morphology -> linearization -> checked surface form

The learner can acquire clause and noun-phrase order from aligned demonstrations or receive
an explicit grammar lesson. Morphology is induced from exact finite hypothesis sets; irregular
lexical forms override productive rules. Every learned object has evidence identity and can be
revoked/reinstated. A construction is language-scoped and will not silently transfer to another
language.

No LLM is called by this module. Exit: 0 pass, 1 defect, 2 CANNOT_CHECK.
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


class CannotCheck(RuntimeError):
    pass


class Pos(str, Enum):
    DETERMINER = "DETERMINER"
    NOUN = "NOUN"
    ADJECTIVE = "ADJECTIVE"
    VERB = "VERB"
    PROPER_NOUN = "PROPER_NOUN"


class Tense(str, Enum):
    PRESENT = "PRESENT"
    PAST = "PAST"


class Number(str, Enum):
    SINGULAR = "SINGULAR"
    PLURAL = "PLURAL"


CLAUSE_ROLES = ("S", "V", "O")
NP_ROLES = ("D", "A", "N")
CLAUSE_ORDERS = tuple(itertools.permutations(CLAUSE_ROLES))
NP_ORDERS = tuple(itertools.permutations(NP_ROLES))


@dataclass(frozen=True)
class Lexeme:
    language: str
    concept_id: str
    lemma: str
    pos: Pos
    evidence_id: int
    irregular_forms: tuple[tuple[str, str], ...] = ()

    def live(self, revoked: Iterable[int] = ()) -> bool:
        return self.evidence_id not in frozenset(revoked)

    def irregular(self, feature: str) -> str | None:
        return dict(self.irregular_forms).get(feature)


@dataclass(frozen=True)
class Construction:
    construction_id: str
    language: str
    construction_type: str
    order: tuple[str, ...]
    evidence_id: int
    channel: str

    def live(self, revoked: Iterable[int] = ()) -> bool:
        return self.evidence_id not in frozenset(revoked)


@dataclass(frozen=True)
class MorphRule:
    rule_id: str
    language: str
    feature: str
    transform: str
    evidence_id: int
    channel: str

    def live(self, revoked: Iterable[int] = ()) -> bool:
        return self.evidence_id not in frozenset(revoked)


@dataclass(frozen=True)
class NPConcept:
    noun_concept: str
    determiner_concept: str | None = None
    adjective_concepts: tuple[str, ...] = ()
    number: Number = Number.SINGULAR


@dataclass(frozen=True)
class SemanticFrame:
    language: str
    agent: NPConcept
    predicate_concept: str
    patient: NPConcept | None = None
    tense: Tense = Tense.PRESENT
    polarity: str = "POSITIVE"
    speech_act: str = "ASSERT"


@dataclass(frozen=True)
class SentencePlan:
    language: str
    semantic_frame: SemanticFrame
    construction_id: str
    sketch: tuple[str, ...]
    slot_realizations: tuple[tuple[str, tuple[str, ...]], ...]
    morphology: tuple[tuple[str, str], ...]
    unresolved_slots: tuple[str, ...] = ()

    def slots(self) -> dict[str, tuple[str, ...]]:
        return dict(self.slot_realizations)


@dataclass(frozen=True)
class GenerationResult:
    status: str
    surface: str | None
    plan: SentencePlan | None
    reason: str = ""


@dataclass(frozen=True)
class ClauseDemo:
    agent: str
    verb: str
    patient: str
    surface: tuple[str, ...]


@dataclass(frozen=True)
class NPDemo:
    determiner: str
    adjective: str
    noun: str
    surface: tuple[str, ...]


@dataclass(frozen=True)
class MorphDemo:
    lemma: str
    form: str


@dataclass(frozen=True)
class InductionReceipt:
    object_type: str
    evidence_id: int
    initial_hypotheses: int
    final_hypotheses: int
    observations: int
    status: str
    order: tuple[str, ...] = ()
    transform: str = ""


MORPH_TRANSFORMS = ("IDENTITY", "ADD_S", "ADD_ES", "ADD_ED", "ADD_D")


def apply_transform(transform: str, lemma: str) -> str:
    if transform == "IDENTITY":
        return lemma
    if transform == "ADD_S":
        return lemma + "s"
    if transform == "ADD_ES":
        return lemma + "es"
    if transform == "ADD_ED":
        return lemma + "ed"
    if transform == "ADD_D":
        return lemma + "d"
    raise ValueError(f"unknown morphology transform {transform}")


def _order_matches(order: Sequence[str], role_tokens: dict[str, str], surface: Sequence[str]) -> bool:
    return tuple(role_tokens[r] for r in order) == tuple(surface)


def induce_clause_order(language: str, demos: Sequence[ClauseDemo], evidence_id: int) -> InductionReceipt:
    candidates = tuple(
        order
        for order in CLAUSE_ORDERS
        if all(_order_matches(order, {"S": d.agent, "V": d.verb, "O": d.patient}, d.surface) for d in demos)
    )
    if len(candidates) != 1:
        return InductionReceipt("CLAUSE_TRANSITIVE", evidence_id, len(CLAUSE_ORDERS), len(candidates), len(demos), "GAP_AMBIGUOUS")
    return InductionReceipt("CLAUSE_TRANSITIVE", evidence_id, len(CLAUSE_ORDERS), 1, len(demos), "LEARNED_WARRANTED", order=candidates[0])


def induce_np_order(language: str, demos: Sequence[NPDemo], evidence_id: int) -> InductionReceipt:
    candidates = tuple(
        order
        for order in NP_ORDERS
        if all(_order_matches(order, {"D": d.determiner, "A": d.adjective, "N": d.noun}, d.surface) for d in demos)
    )
    if len(candidates) != 1:
        return InductionReceipt("NP", evidence_id, len(NP_ORDERS), len(candidates), len(demos), "GAP_AMBIGUOUS")
    return InductionReceipt("NP", evidence_id, len(NP_ORDERS), 1, len(demos), "LEARNED_WARRANTED", order=candidates[0])


def induce_morph_rule(language: str, feature: str, demos: Sequence[MorphDemo], evidence_id: int) -> InductionReceipt:
    candidates = tuple(
        t for t in MORPH_TRANSFORMS if all(apply_transform(t, d.lemma) == d.form for d in demos)
    )
    if len(candidates) != 1:
        return InductionReceipt("MORPH", evidence_id, len(MORPH_TRANSFORMS), len(candidates), len(demos), "GAP_AMBIGUOUS")
    return InductionReceipt("MORPH", evidence_id, len(MORPH_TRANSFORMS), 1, len(demos), "LEARNED_WARRANTED", transform=candidates[0])


@dataclass
class LanguageKSO:
    constructions: dict[tuple[str, str], Construction] = field(default_factory=dict)
    morph_rules: dict[tuple[str, str], MorphRule] = field(default_factory=dict)
    lexemes: list[Lexeme] = field(default_factory=list)
    revoked: set[int] = field(default_factory=set)
    space: object = field(init=False)

    def __post_init__(self) -> None:
        self.space = kso.KnowledgeSpace(
            (
                kso.Atom("lang:root", "language_kso", ONE),
                kso.Atom("lang:syntax", "language_region", ONE),
                kso.Atom("lang:morphology", "language_region", ONE),
                kso.Atom("lang:lexicon", "language_region", ONE),
                kso.Atom("lang:semantics", "language_region", ONE),
            ),
            (
                kso.Hyperedge("lang-root-syntax", ("lang:root",), ("lang:syntax",), "SUPPORT", profile=ONE),
                kso.Hyperedge("lang-root-morph", ("lang:root",), ("lang:morphology",), "SUPPORT", profile=ONE),
                kso.Hyperedge("lang-root-lex", ("lang:root",), ("lang:lexicon",), "SUPPORT", profile=ONE),
                kso.Hyperedge("lang-root-semantics", ("lang:root",), ("lang:semantics",), "SUPPORT", profile=ONE),
            ),
        )
        self.space.validate()

    def _admit(self, atom_id: str, atom_type: str, evidence_id: int, parent: str, certificate) -> None:
        atom = kso.Atom(atom_id, atom_type, (frozenset({evidence_id}),))
        edge_id = "lang-edge:" + hashlib.sha256(f"{parent}|{atom_id}".encode()).hexdigest()[:16]
        edge = kso.Hyperedge(edge_id, (parent,), (atom_id,), "SUPPORT", profile=ONE)
        self.space, rec = m0.admit(self.space, atom, (edge,), certificate, revoked=self.revoked)
        if not (rec.warranted and rec.reachable_by_navigation):
            raise CannotCheck(f"failed to admit {atom_id}")

    def teach_lexeme(
        self,
        language: str,
        concept_id: str,
        lemma: str,
        pos: Pos,
        evidence_id: int,
        *,
        irregular_forms: Sequence[tuple[str, str]] = (),
    ) -> Lexeme:
        if any(x.language == language and x.concept_id == concept_id and x.pos is pos for x in self.lexemes):
            raise ValueError(f"duplicate lexical mapping: {language}:{concept_id}:{pos.value}")
        lex = Lexeme(language, concept_id, lemma, pos, evidence_id, tuple(irregular_forms))
        atom_id = f"lang:{language}:lex:{pos.value}:{concept_id}"
        self._admit(atom_id, "lexeme", evidence_id, "lang:lexicon", m0.CertificateKind.INSTRUCTION)
        self.lexemes.append(lex)
        return lex

    def teach_construction(
        self,
        language: str,
        construction_type: str,
        order: Sequence[str],
        evidence_id: int,
    ) -> Construction:
        allowed = set(CLAUSE_ROLES if construction_type == "CLAUSE_TRANSITIVE" else NP_ROLES if construction_type == "NP" else ())
        if not allowed or set(order) != allowed or len(order) != len(allowed):
            raise ValueError("invalid construction order")
        c = Construction(
            f"{language}:{construction_type}:{''.join(order)}",
            language,
            construction_type,
            tuple(order),
            evidence_id,
            "INSTRUCTION",
        )
        self._store_construction(c, m0.CertificateKind.INSTRUCTION)
        return c

    def admit_induced_construction(self, language: str, rec: InductionReceipt) -> Construction:
        if rec.status != "LEARNED_WARRANTED" or not rec.order:
            raise CannotCheck("construction induction did not identify one warranted construction")
        c = Construction(
            f"{language}:{rec.object_type}:{''.join(rec.order)}",
            language,
            rec.object_type,
            rec.order,
            rec.evidence_id,
            "DEMONSTRATION",
        )
        self._store_construction(c, m0.CertificateKind.DEMONSTRATION)
        return c

    def _store_construction(self, c: Construction, certificate) -> None:
        key = (c.language, c.construction_type)
        if key in self.constructions:
            raise ValueError(f"construction already registered: {key}")
        atom_id = f"lang:{c.language}:construction:{c.construction_type}"
        self._admit(atom_id, "construction", c.evidence_id, "lang:syntax", certificate)
        self.constructions[key] = c

    def admit_morph_rule(self, language: str, feature: str, rec: InductionReceipt) -> MorphRule:
        if rec.status != "LEARNED_WARRANTED" or not rec.transform:
            raise CannotCheck("morphology induction did not identify one warranted rule")
        key = (language, feature)
        if key in self.morph_rules:
            raise ValueError(f"morphology rule already registered: {key}")
        rule = MorphRule(f"{language}:{feature}:{rec.transform}", language, feature, rec.transform, rec.evidence_id, "DEMONSTRATION")
        atom_id = f"lang:{language}:morph:{feature}"
        self._admit(atom_id, "morphology_rule", rec.evidence_id, "lang:morphology", m0.CertificateKind.DEMONSTRATION)
        self.morph_rules[key] = rule
        return rule

    def revoke(self, evidence_id: int) -> None:
        self.revoked.add(evidence_id)

    def reinstate(self, evidence_id: int) -> None:
        self.revoked.discard(evidence_id)

    def _lexeme(self, language: str, concept_id: str, pos: Pos) -> Lexeme:
        rows = [x for x in self.lexemes if x.language == language and x.concept_id == concept_id and x.pos is pos and x.live(self.revoked)]
        if not rows:
            raise CannotCheck(f"GAP_UNKNOWN_LEXEME:{language}:{concept_id}:{pos.value}")
        if len(rows) != 1:
            raise CannotCheck(f"GAP_AMBIGUOUS_LEXEME:{language}:{concept_id}:{pos.value}")
        return rows[0]

    def _construction(self, language: str, construction_type: str) -> Construction:
        c = self.constructions.get((language, construction_type))
        if c is None:
            raise CannotCheck(f"GAP_NO_{construction_type}_CONSTRUCTION")
        if not c.live(self.revoked):
            raise CannotCheck(f"GAP_REVOKED_{construction_type}_CONSTRUCTION")
        return c

    def _rule(self, language: str, feature: str) -> MorphRule:
        r = self.morph_rules.get((language, feature))
        if r is None:
            raise CannotCheck(f"GAP_MORPHOLOGY:{language}:{feature}")
        if not r.live(self.revoked):
            raise CannotCheck(f"GAP_REVOKED_MORPHOLOGY:{language}:{feature}")
        return r

    def realize_np(self, language: str, np: NPConcept) -> tuple[str, ...]:
        c = self._construction(language, "NP")
        det: tuple[str, ...] = ()
        if np.determiner_concept:
            det = (self._lexeme(language, np.determiner_concept, Pos.DETERMINER).lemma,)
        adjs = tuple(self._lexeme(language, x, Pos.ADJECTIVE).lemma for x in np.adjective_concepts)
        noun = (self._lexeme(language, np.noun_concept, Pos.NOUN).lemma,)
        role_tokens = {"D": det, "A": adjs, "N": noun}
        return tuple(token for role in c.order for token in role_tokens[role])

    def verb_form(self, language: str, predicate_concept: str, tense: Tense, subject_number: Number) -> tuple[str, str]:
        lex = self._lexeme(language, predicate_concept, Pos.VERB)
        if tense is Tense.PAST:
            irregular = lex.irregular("PAST")
            if irregular is not None:
                return irregular, "IRREGULAR:PAST"
            r = self._rule(language, "PAST")
            return apply_transform(r.transform, lex.lemma), r.rule_id
        if tense is Tense.PRESENT and subject_number is Number.SINGULAR:
            irregular = lex.irregular("PRES_3SG")
            if irregular is not None:
                return irregular, "IRREGULAR:PRES_3SG"
            r = self._rule(language, "PRES_3SG")
            return apply_transform(r.transform, lex.lemma), r.rule_id
        return lex.lemma, "IDENTITY:PRESENT_NON_3SG"

    def plan(self, frame: SemanticFrame) -> SentencePlan:
        if frame.polarity != "POSITIVE" or frame.speech_act != "ASSERT":
            raise CannotCheck("GAP_NO_APPLICABLE_CONSTRUCTION")
        if frame.patient is None:
            raise CannotCheck("GAP_NO_INTRANSITIVE_CONSTRUCTION")
        clause = self._construction(frame.language, "CLAUSE_TRANSITIVE")
        subject = self.realize_np(frame.language, frame.agent)
        obj = self.realize_np(frame.language, frame.patient)
        verb, morph_source = self.verb_form(frame.language, frame.predicate_concept, frame.tense, frame.agent.number)
        slots = (("S", subject), ("V", (verb,)), ("O", obj))
        return SentencePlan(
            frame.language,
            frame,
            clause.construction_id,
            clause.order,
            slots,
            (("V", morph_source),),
            (),
        )

    def realize(self, plan: SentencePlan) -> str:
        if plan.unresolved_slots:
            raise CannotCheck("REFINE_REQUIRED")
        clause = self._construction(plan.language, "CLAUSE_TRANSITIVE")
        if plan.construction_id != clause.construction_id or plan.sketch != clause.order:
            raise CannotCheck("SEMANTIC_CHECK_FAILED:construction_drift")
        slots = plan.slots()
        if set(slots) != set(CLAUSE_ROLES):
            raise CannotCheck("SEMANTIC_CHECK_FAILED:slot_set")
        tokens = [token for role in plan.sketch for token in slots[role]]
        if not tokens:
            raise CannotCheck("SEMANTIC_CHECK_FAILED:empty_surface")
        text = " ".join(tokens)
        text = text[0].upper() + text[1:] + "."
        return text

    def speak(self, frame: SemanticFrame) -> GenerationResult:
        try:
            p = self.plan(frame)
            return GenerationResult("PASS", self.realize(p), p)
        except CannotCheck as exc:
            reason = str(exc)
            status = reason.split(":", 1)[0] if reason else "CANNOT_CHECK"
            return GenerationResult(status, None, None, reason)


def _teach_demo_lexicon(machine: LanguageKSO, start_evidence: int = 2000) -> None:
    rows = (
        ("DEF", "the", Pos.DETERMINER, ()),
        ("CURIOUS", "curious", Pos.ADJECTIVE, ()),
        ("RED", "red", Pos.ADJECTIVE, ()),
        ("ROBOT", "robot", Pos.NOUN, ()),
        ("DOOR", "door", Pos.NOUN, ()),
        ("PAINTING", "painting", Pos.NOUN, ()),
        ("OPEN", "open", Pos.VERB, ()),
        ("ADMIRE", "admire", Pos.VERB, ()),
        ("WALK", "walk", Pos.VERB, ()),
        ("JUMP", "jump", Pos.VERB, ()),
        ("GO", "go", Pos.VERB, (("PAST", "went"),)),
    )
    for i, (concept, lemma, pos, irregular) in enumerate(rows):
        machine.teach_lexeme("en", concept, lemma, pos, start_evidence + i, irregular_forms=irregular)


def _target_frame(predicate: str = "OPEN", *, tense: Tense = Tense.PRESENT) -> SemanticFrame:
    return SemanticFrame(
        language="en",
        agent=NPConcept("ROBOT", "DEF", ("CURIOUS",), Number.SINGULAR),
        predicate_concept=predicate,
        patient=NPConcept("DOOR" if predicate == "OPEN" else "PAINTING", "DEF", ("RED",), Number.SINGULAR),
        tense=tense,
    )


def run_language_l0() -> dict[str, object]:
    machine = LanguageKSO()
    _teach_demo_lexicon(machine)

    pre = machine.speak(_target_frame())
    assert pre.status == "GAP_NO_CLAUSE_TRANSITIVE_CONSTRUCTION"

    ambiguous = induce_clause_order("en", (), 3000)
    assert ambiguous.status == "GAP_AMBIGUOUS" and ambiguous.final_hypotheses == 6

    clause_rec = induce_clause_order(
        "en",
        (
            ClauseDemo("alice", "likes", "bob", ("alice", "likes", "bob")),
            ClauseDemo("robots", "help", "people", ("robots", "help", "people")),
        ),
        3001,
    )
    np_rec = induce_np_order(
        "en",
        (
            NPDemo("the", "red", "door", ("the", "red", "door")),
            NPDemo("a", "small", "robot", ("a", "small", "robot")),
        ),
        3002,
    )
    m3_rec = induce_morph_rule("en", "PRES_3SG", (MorphDemo("walk", "walks"), MorphDemo("jump", "jumps")), 3003)
    past_rec = induce_morph_rule("en", "PAST", (MorphDemo("walk", "walked"), MorphDemo("jump", "jumped")), 3004)
    assert clause_rec.order == ("S", "V", "O")
    assert np_rec.order == ("D", "A", "N")
    assert m3_rec.transform == "ADD_S"
    assert past_rec.transform == "ADD_ED"

    clause = machine.admit_induced_construction("en", clause_rec)
    machine.admit_induced_construction("en", np_rec)
    machine.admit_morph_rule("en", "PRES_3SG", m3_rec)
    machine.admit_morph_rule("en", "PAST", past_rec)

    result = machine.speak(_target_frame())
    assert result.status == "PASS" and result.surface == "The curious robot opens the red door."
    assert result.plan is not None and result.plan.sketch == ("S", "V", "O")
    assert result.plan.slots()["S"] == ("the", "curious", "robot")
    assert result.plan.slots()["V"] == ("opens",)
    assert result.plan.slots()["O"] == ("the", "red", "door")

    # Systematic lexical composition: ADMIRE never appeared in the grammar or morphology demos.
    heldout = machine.speak(_target_frame("ADMIRE"))
    assert heldout.status == "PASS" and heldout.surface == "The curious robot admires the red painting."

    regular_past, regular_src = machine.verb_form("en", "WALK", Tense.PAST, Number.SINGULAR)
    irregular_past, irregular_src = machine.verb_form("en", "GO", Tense.PAST, Number.SINGULAR)
    assert regular_past == "walked" and "ADD_ED" in regular_src
    assert irregular_past == "went" and irregular_src == "IRREGULAR:PAST"

    machine.revoke(clause.evidence_id)
    revoked = machine.speak(_target_frame())
    assert revoked.status == "GAP_REVOKED_CLAUSE_TRANSITIVE_CONSTRUCTION"
    machine.reinstate(clause.evidence_id)
    reinstated = machine.speak(_target_frame())
    assert reinstated.surface == result.surface

    wrong_language = SemanticFrame(
        language="toy-sov",
        agent=_target_frame().agent,
        predicate_concept="OPEN",
        patient=_target_frame().patient,
    )
    blocked_transfer = machine.speak(wrong_language)
    assert blocked_transfer.status == "GAP_NO_CLAUSE_TRANSITIVE_CONSTRUCTION"

    # Explicit grammar-book instruction and demonstration induction must agree on the sketch.
    instructed = LanguageKSO()
    _teach_demo_lexicon(instructed, 4000)
    ci = instructed.teach_construction("en", "CLAUSE_TRANSITIVE", ("S", "V", "O"), 4100)
    instructed.teach_construction("en", "NP", ("D", "A", "N"), 4101)
    instructed.admit_morph_rule("en", "PRES_3SG", InductionReceipt("MORPH", 4102, 5, 1, 2, "LEARNED_WARRANTED", transform="ADD_S"))
    instructed.admit_morph_rule("en", "PAST", InductionReceipt("MORPH", 4103, 5, 1, 2, "LEARNED_WARRANTED", transform="ADD_ED"))
    instruction_result = instructed.speak(_target_frame())
    assert ci.order == clause.order and instruction_result.surface == result.surface

    return {
        "terminal": "LANGUAGE_KSO_L0_CONTROLLED_GREEN",
        "learning": {
            "clause_order_initial_hypotheses": clause_rec.initial_hypotheses,
            "clause_order_final_hypotheses": clause_rec.final_hypotheses,
            "clause_order": list(clause_rec.order),
            "np_order": list(np_rec.order),
            "present_3sg_rule": m3_rec.transform,
            "regular_past_rule": past_rec.transform,
        },
        "generation": {
            "prelesson": pre.status,
            "surface": result.surface,
            "sentence_sketch": list(result.plan.sketch if result.plan else ()),
            "heldout_surface": heldout.surface,
            "regular_past": regular_past,
            "irregular_past": irregular_past,
            "after_revocation": revoked.status,
            "after_reinstatement": reinstated.surface,
            "wrong_language_transfer": blocked_transfer.status,
            "instruction_demo_surface_equal": instruction_result.surface == result.surface,
        },
        "space": {
            "atoms": len(machine.space.atoms),
            "hyperedges": len(machine.space.hyperedges),
            "learned_constructions": len(machine.constructions),
            "learned_morph_rules": len(machine.morph_rules),
            "lexemes": len(machine.lexemes),
        },
        "authority": {
            "open_domain_language": False,
            "human_level_language": False,
            "raw_books_sufficient_for_grounded_meaning": False,
            "post_llm_language_paradigm": False,
            "novelty": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path)
    a = p.parse_args(argv)
    try:
        result = run_language_l0()
    except CannotCheck as exc:
        print(json.dumps({"terminal": "CANNOT_CHECK", "reason": str(exc)}))
        return 2
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

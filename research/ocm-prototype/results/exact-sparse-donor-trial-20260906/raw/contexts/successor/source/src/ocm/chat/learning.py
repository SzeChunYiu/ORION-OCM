"""Chat access to attributed knowledge and independently checked total methods."""
from __future__ import annotations

from fractions import Fraction
import re

from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.language import lexicon as L
from ocm.knowledge.world import SourceDocument, triple
from ocm.learning import methods as M
from ocm.store.evidence import Channel

NAME = r"[a-z][a-z0-9_-]{0,31}"


def _skills(session):
    scope = Scope.of(session.conversation_id)
    return [a for a in session.runtime.state.ks.atoms
            if a.atom_type == "procedure" and dict(a.meta).get("kind") == "chat-method.v1"
            and a.scope == scope]


def _admit(session, name, task, result):
    runtime = session.runtime
    admitted = M.admit_solution(runtime, task, result)
    proof = runtime.state.ks.atom_map()[admitted["method_id"]]
    _, lesson = runtime.admit_evidence({"method_name": name, "program": result.program,
        "turn": len(session.dialogue.workspace.turns)}, Channel.INSTRUCTION, "chat-user",
        scope=Scope.of(session.conversation_id))
    payload = {"kind": "chat-method.v1", "name": name, "program": result.program,
               "coefficients": tuple(map(str, task.coefficients)), "checker": M.CHECKER,
               "proof": admitted["method_id"], "lesson": lesson}
    fingerprint = content_hash(payload)
    warrant = proof.warrant.meet(WarrantProfile.of({lesson}))
    atom_id = "chat-method:" + fingerprint
    edge = Hyperedge("support:" + atom_id, (proof.atom_id,), (atom_id,), "SUPPORT", warrant=warrant)
    runtime.admit_object(Atom(atom_id, "procedure", warrant, scope=Scope.of(session.conversation_id),
        content_ref=fingerprint, meta=tuple(payload.items())), (edge,), "EXACT_CHECKER")
    return lesson, admitted["evidence_id"]


def handle(session, text):
    """Return reply and evidence, or None. No Python/string evaluation or external IO."""
    low = text.strip().lower().rstrip("?")
    runtime = session.runtime
    if low in ("list skills", "what skills have you learned", "what methods do you know"):
        rows = _skills(session)
        live = [a for a in rows if a.liveness(runtime.state.revoked) is Liveness.LIVE]
        names = sorted({dict(a.meta)["name"] for a in live})
        return ("My live arithmetic methods: " + ", ".join(names) + "." if names else
                "I have no live named arithmetic methods yet. Try: learn method next-square: inc square", ())
    if low.startswith("learn method ") or low.startswith("find method:"):
        try:
            if low.startswith("learn method "):
                match = re.fullmatch(r"learn method (" + NAME + r"): ([a-z ,]+)", low)
                if not match:
                    raise ValueError("Use: learn method name: inc square")
                name, body = match.groups()
                program = M.checked_program(body.replace(",", " ").split())
                task = M.PolynomialTask(name, M.normal_form(program))
                result = M.SearchResult(task.fingerprint, "user-instruction", "VERIFIED_POLYNOMIAL_IDENTITY",
                                        program, 0, 1, (), len(program))
            else:
                body = low[len("find method:"):].strip()
                if len(body) > 512 or len(body.split(",")) > 17:
                    raise ValueError("coefficient budget exceeded")
                task = M.PolynomialTask("chat-target", tuple(Fraction(c.strip()) for c in body.split(",")))
                result = M.solve(task, M.SearchBudget(slots=1000, max_length=4))
                name = "found-" + task.fingerprint[:12]
                if not M.verify_solution(task, result):
                    return ("I did not find a verified method within 1,000 search slots and four instructions. "
                            "That does not show the problem has no solution.", ())
            if any(dict(a.meta)["name"] == name and a.liveness(runtime.state.revoked) is Liveness.LIVE
                   for a in _skills(session)):
                return (f"A live method named '{name}' already exists; use a new name or revoke its lesson first.", ())
            evidence = _admit(session, name, task, result)
            return (f"Learned method '{name}': {' then '.join(result.program) or 'identity'}. "
                    f"Checked its polynomial meaning for every rational input. Try: run {name} on 3. "
                    f"Lesson: {evidence[0]}; proof: {evidence[1]}.", evidence)
        except (ValueError, ZeroDivisionError, OverflowError) as exc:
            return (f"I cannot learn that method: {exc}", ())
    if low.startswith("run "):
        match = re.fullmatch(r"run (" + NAME + r") on ([+-]?[0-9]{1,12}(?:/[0-9]{1,12})?)", low)
        if not match:
            return ("Use: run method-name on 3 (or an exact fraction such as 3/2).", ())
        name, value = match.groups()
        live = [a for a in _skills(session) if dict(a.meta)["name"] == name
                and a.liveness(runtime.state.revoked) is Liveness.LIVE]
        if len(live) != 1:
            return (f"I have no unique live method named '{name}'. Its lesson or proof may be missing or revoked.", ())
        atom = live[0]
        payload = dict(atom.meta)
        try:
            program = M.checked_program(payload["program"])
            if (content_hash(payload) != atom.content_ref or payload["checker"] != M.CHECKER
                    or M.normal_form(program) != tuple(Fraction(c) for c in payload["coefficients"])):
                raise ValueError("method identity or proof changed")
            answer = M.execute(program, Fraction(value))
        except (ValueError, ZeroDivisionError, OverflowError) as exc:
            return (f"I cannot run that method: {exc}", ())
        return (f"{name}({value}) = {answer}. Checked arithmetic; this uses your learned method.",
                tuple(sorted(atom.warrant.evidence)))
    if low.startswith("remember:"):
        body = low[len("remember:"):].strip().rstrip(".")
        if set(body.split()) & {"not", "no", "never", "all", "every", "some"}:
            return ("This memory form supports positive statements about named subjects. Please give an unambiguous positive statement.", ())
        match = re.fullmatch(r"([a-z][a-z -]{0,63}) is (in |a |an )?([a-z][a-z -]{0,63})", body)
        if not match:
            return ("Use: remember: mira is a botanist, or remember: mira is in oslo. I retain it as your report.", ())
        subject, relation, obj = match.groups()
        meaning = triple(subject.strip(), "LOCATED_IN" if relation == "in " else "IS_A", obj.strip())
        source = "chat-user:" + content_hash({"text": text, "conversation": session.conversation_id,
                                               "turn": len(session.dialogue.workspace.turns)})
        session.world.add_document(SourceDocument(source, "User report", "user-provided", content_hash(text), kind="user_report"))
        existing, _ = session.world.lookup(meaning)
        fact = session.world.assert_fact(existing.fact_id if existing else source, meaning,
                                        session.conversation_id, source, gloss=body.capitalize() + ".")
        eid = fact.assertion_evidence[-1]
        for label in (subject.strip(), obj.strip()):
            if " " not in label and not session.dialogue.lexicon.by_lemma(label):
                session.dialogue.lexicon.add(L.Lexeme(label, L.Category.NOUN,
                    (L.Sense(source + ":" + label, label, "entity", WarrantProfile.of({eid})),)))
        session._save_world_index()
        session._save_learned()
        return (f"I will remember that you reported: {body}. It is not independently verified. Evidence: {eid}.", (eid,))
    return None

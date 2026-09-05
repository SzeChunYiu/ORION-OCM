"""Pilot field custody: acquired language and generator DATA in one KSO ledger."""
import json
from fractions import Fraction

from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import WarrantProfile, meet_all_profiles
from ocm.language.constructions import Construction, Slot
from ocm.language.lexicon import Category, Lexeme, Lexicon, Sense
from ocm.learning import methods as M
from ocm.store.evidence import Channel
import minimal_language_learning as L

SCOPE = Scope.of("vessel-pilot")
LANG, GEN, PRIM = "pilot:language", "pilot:generator", "pilot:primitives"


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def payload(ks, atom_id):
    atom = ks.atom_map()[atom_id]
    data = json.loads(dict(atom.meta)["data"])
    if content_hash(data) != atom.content_ref:
        raise ValueError("field payload identity changed")
    return data


def put(runtime, atom_id, data, warrant, parents=("pilot:root",), certificate="INSTRUCTION"):
    if atom_id in runtime.state.ks.ids:
        if encode(payload(runtime.state.ks, atom_id)) != encode(data):
            raise ValueError("pilot object identity collision")
        return atom_id
    edges = tuple(Hyperedge("support:" + atom_id + ":" + parent, (parent,), (atom_id,),
                            "SUPPORT", warrant=warrant) for parent in parents)
    runtime.admit_object(Atom(atom_id, "procedure", warrant, scope=SCOPE,
        quarantined=not parents, content_ref=content_hash(data), meta=(("data", encode(data)),)),
        edges, certificate)
    return atom_id


def setup(runtime):
    if "pilot:fixture" in runtime.state.ks.ids:
        return payload(runtime.state.ks, "pilot:fixture")
    _, prior = runtime.admit_evidence({"prior": "total arithmetic DSL and registered transitive-role template"},
        Channel.INSTRUCTION, "host-prior", scope=SCOPE)
    put(runtime, "pilot:root", {"prior": prior}, WarrantProfile.of({prior}), ())
    words, word_evidence = [], []
    language = L.empty_language("pilot-language")
    for word, category, node_type in (("robot", "N", "entity"), ("girl", "N", "entity"),
            ("door", "N", "entity"), ("ball", "N", "entity"),
            ("open", "V", "event"), ("push", "V", "event")):
        _, eid = runtime.admit_evidence({"word": word, "category": category, "concept": word},
            Channel.INSTRUCTION, "word-teacher", scope=SCOPE)
        words.append([word, category, word, node_type, eid]); word_evidence.append(eid)
        L.teach_word(language, word, Category(category), word, node_type, eid)
    lessons, acquired = [], []
    for teacher in ("teacher:a", "teacher:b"):
        _, eid = runtime.admit_evidence({"utterance": "robot door open",
            "meaning": L.transitive_meaning("robot", "open", "door").as_dict()},
            Channel.INSTRUCTION, teacher, scope=SCOPE)
        c = L.learn_transitive(language, "robot door open", L.transitive_meaning("robot", "open", "door"),
            held_out_queries=(), evidence_id=eid)
        lessons.append(eid); acquired.append(c)
    if acquired[0].pattern != acquired[1].pattern:
        raise ValueError("independent aligned lessons disagree")
    grammar = WarrantProfile.of(*({e} for e in lessons))
    language_data = {"kind": "acquired-language.v1", "words": words,
        "pattern": [[s.name, s.category.value] for s in acquired[0].pattern],
        "grammar_evidence": lessons, "language": language.language}
    put(runtime, LANG, language_data, grammar.meet(WarrantProfile.of(set(word_evidence))))
    training, training_evidence = [], []
    for program in (("inc", "square", "inc"), ("inc", "square", "double")):
        task = M.PolynomialTask("training", M.normal_form(program))
        result = M.SearchResult(task.fingerprint, "explicit-demonstration", "VERIFIED_POLYNOMIAL_IDENTITY",
                                program, 0, 1, (), len(program))
        if not M.verify_solution(task, result):
            raise ValueError("unchecked arithmetic lesson")
        _, eid = runtime.admit_evidence({"task": [str(c) for c in task.coefficients], "program": program},
            Channel.INSTRUCTION, "method-teacher", scope=SCOPE)
        training.append((task, result)); training_evidence.append(eid)
    generator = M.learn_generator(training)
    if not generator.fragments:
        raise ValueError("no recurring fragment acquired")
    put(runtime, GEN, {"kind": "generator.v1", "fragments": generator.fragments,
        "training_tasks": generator.training_tasks}, WarrantProfile.of(set(training_evidence)))
    put(runtime, PRIM, {"kind": "primitive.v1", "instructions": M.PRIMITIVES}, WarrantProfile.of({prior}))
    fixture = {"language_lessons": lessons, "generator_lessons": training_evidence,
        "word_lessons": word_evidence, "prior": prior,
        "scope": "explicit supervision; generator compression acquired, no utility promotion asserted"}
    put(runtime, "pilot:fixture", fixture, WarrantProfile.of({prior}))
    runtime.persist()
    return fixture


def restore_language(ks):
    data = payload(ks, LANG)
    if set(data) != {"kind", "words", "pattern", "grammar_evidence", "language"}:
        raise ValueError("unexpected learned language fields")
    lexicon = Lexicon()
    for word, category, concept, node_type, eid in data["words"]:
        w = WarrantProfile.of({eid})
        lexicon.add(Lexeme(word, Category(category),
            (Sense(word, concept, node_type, w),), warrant=w))
    slots = tuple(Slot(name, Category(category)) for name, category in data["pattern"])
    if sorted((s.name, s.category.value) for s in slots) != [("obj", "N"), ("subj", "N"), ("verb", "V")]:
        raise ValueError("pattern outside registered role grammar")
    construction = Construction("pilot:acquired", "bare_transitive", slots, L.transitive_template,
        WarrantProfile.of(*({e} for e in data["grammar_evidence"])), language=data["language"])
    return lexicon, (construction,)


def truth_warrant(runtime, atom_ids):
    return meet_all_profiles(runtime.state.ks.atom_map()[x].warrant for x in atom_ids)
